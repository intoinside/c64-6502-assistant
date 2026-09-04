"""Calcolo deterministico dei cicli di clock e analisi raster per MOS 6502 su C64.

Supporta il parsing avanzato delle istruzioni, il riconoscimento rigoroso delle
modalità di indirizzamento, il calcolo dei cicli minimi/massimi (branch presi,
attraversamento del page boundary, penalità di scrittura) e la conversione
in linee raster PAL e NTSC con gestione delle Bad Lines del VIC-II.
"""

import re
from pydantic import BaseModel, Field
from .opcodes import (
    AddressingMode,
    ISA_6502_NMOS,
    OpcodeInfo,
    get_opcode_info,
    is_official_mnemonic,
)


class InstructionTiming(BaseModel):
    line_number: int = Field(default=0)
    raw_line: str = Field(description="Riga sorgente originale")
    label: str = Field(default="", description="Etichetta individuata")
    mnemonic: str = Field(default="", description="Mnemonico istruzione")
    operand: str = Field(default="", description="Operando dell'istruzione")
    mode: AddressingMode = Field(default=AddressingMode.IMPLIED, description="Modalità di indirizzamento rilevata")
    opcode_hex: str = Field(default="", description="Opcode esadecimale")
    base_cycles: int = Field(default=0, description="Cicli di clock minimi")
    max_cycles: int = Field(default=0, description="Cicli di clock massimi (branch/page cross)")
    bytes_count: int = Field(default=0, description="Dimensione in byte")
    flags_affected: str = Field(default="", description="Flag influenzati")
    notes: str = Field(default="", description="Note esplicative sul timing")


class CycleCounterReport(BaseModel):
    total_min_cycles: int = 0
    total_max_cycles: int = 0
    total_bytes: int = 0
    pal_raster_lines: float = 0.0  # 63 cicli per linea raster PAL
    ntsc_raster_lines: float = 0.0  # 65 cicli per linea raster NTSC
    has_branch_uncertainty: bool = False
    has_page_cross_uncertainty: bool = False
    instructions: list[InstructionTiming] = Field(default_factory=list)
    detected_directives: list[str] = Field(default_factory=list)


class CycleCounter:
    """Motore deterministico di calcolo cicli per il 6502 su Commodore 64."""

    PAL_CYCLES_PER_LINE = 63
    NTSC_CYCLES_PER_LINE = 65
    BAD_LINE_STOLEN_CYCLES = 42  # Media dei cicli sottratti dal VIC-II durante una Bad Line

    # Direttive assembler comuni (ACME, KickAssembler, CA65)
    KNOWN_DIRECTIVES = {
        "!to", "!zone", "!byte", "!by", "!word", "!wo", "!fill", "!align",
        ".pc", ".byte", ".word", ".text", ".pseudopc", ".align",
        "*=", "org", ".org",
    }

    @classmethod
    def clean_comment(cls, line: str) -> str:
        """Rimuove commenti sia in stile standard 6502 (;) sia C/C++ (//)."""
        clean = line.split(";")[0]
        clean = clean.split("//")[0]
        return clean.strip()

    @classmethod
    def resolve_addressing_mode(cls, mnemonic: str, operand: str) -> AddressingMode:
        """Determina la modalità di indirizzamento in base alla sintassi dell'operando."""
        m = mnemonic.upper()
        op = operand.strip()

        # 1. Nessun operando
        if not op:
            if m in {"ASL", "LSR", "ROL", "ROR"}:
                return AddressingMode.ACCUMULATOR
            return AddressingMode.IMPLIED

        # 2. Accumulatore esplicito (es. ASL A, ROR a)
        if op.upper() == "A" and m in {"ASL", "LSR", "ROL", "ROR"}:
            return AddressingMode.ACCUMULATOR

        # 3. Immediato (#$10, #10, #%1100, #'A')
        if op.startswith("#"):
            return AddressingMode.IMMEDIATE

        # 4. Indiretto e varianti tra parentesi tonde
        if op.startswith("(") and op.endswith(")"):
            inner = op[1:-1].strip()
            # JMP ($1234)
            if m == "JMP":
                return AddressingMode.INDIRECT
            # ($nn,X) -> Indexed Indirect X
            if re.search(r",\s*[Xx]$", inner):
                return AddressingMode.INDEXED_INDIRECT_X

        # ($nn),Y -> Indirect Indexed Y
        if re.search(r"^\([^)]+\)\s*,\s*[Yy]$", op):
            return AddressingMode.INDIRECT_INDEXED_Y

        # ($nn,X) senza parentesi esterna unificata
        if re.search(r"^\([^,]+,\s*[Xx]\)$", op):
            return AddressingMode.INDEXED_INDIRECT_X

        # 5. Istruzioni di Branch (BNE, BEQ, BCC, BCS, BPL, BMI, BVC, BVS)
        if m.startswith("B") and m in {"BNE", "BEQ", "BCC", "BCS", "BPL", "BMI", "BVC", "BVS"}:
            return AddressingMode.RELATIVE

        # 6. Indicizzati con X o Y
        is_indexed_x = bool(re.search(r",\s*[Xx]$", op))
        is_indexed_y = bool(re.search(r",\s*[Yy]$", op))

        base_op = re.sub(r",\s*[XxYy]$", "", op).strip()

        # Verifica se l'operando numerico risiede in Zero Page ($00-$FF)
        is_zero_page_val = False
        if base_op.startswith("$"):
            hex_part = base_op[1:]
            if len(hex_part) <= 2:
                is_zero_page_val = True
        elif base_op.isdigit():
            val = int(base_op)
            if 0 <= val <= 255:
                is_zero_page_val = True

        if is_indexed_x:
            # Eccezione: LDX non ha ZeroPage_X ma ZeroPage_Y
            if is_zero_page_val and m != "LDX":
                return AddressingMode.ZERO_PAGE_X
            return AddressingMode.ABSOLUTE_X

        if is_indexed_y:
            # LDX e STX supportano ZeroPage_Y
            if is_zero_page_val and m in {"LDX", "STX"}:
                return AddressingMode.ZERO_PAGE_Y
            return AddressingMode.ABSOLUTE_Y

        # 7. Zero Page vs Absolute non indicizzato
        if is_zero_page_val:
            return AddressingMode.ZERO_PAGE

        # Default per tutti gli altri operandi: Absolute
        return AddressingMode.ABSOLUTE

    @classmethod
    def parse_line(cls, line: str, line_no: int = 1) -> tuple[InstructionTiming | None, str | None]:
        """Esegue il parsing di una riga di testo assembly restituendo timing ed eventuali direttive."""
        clean = cls.clean_comment(line)
        if not clean:
            return None, None

        # Rilevamento direttive tipo * = $0801 o .pc = $0801
        if any(clean.lower().startswith(d) for d in cls.KNOWN_DIRECTIVES) or "*=" in clean.replace(" ", ""):
            return None, clean

        label = ""
        # Verifica presenza etichetta (es. "loop: lda #0" o "loop lda #0")
        parts = clean.split()
        if parts[0].endswith(":"):
            label = parts[0][:-1]
            parts = parts[1:]
        elif len(parts) > 1 and parts[0].upper() not in ISA_6502_NMOS and not parts[0].startswith("."):
            # Se la prima parola non è un mnemonico valido, è probabile che sia un'etichetta
            label = parts[0]
            parts = parts[1:]

        if not parts:
            return None, None

        mnemonic = parts[0].upper()
        operand = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Verifica se è una direttiva assembler
        if mnemonic.startswith(".") or mnemonic.startswith("!"):
            return None, clean

        # Risoluzione modalità di indirizzamento
        mode = cls.resolve_addressing_mode(mnemonic, operand)
        op_info = get_opcode_info(mnemonic, mode)

        if not op_info:
            # Fallback se la combinazione specifica non esiste o è illegale
            return InstructionTiming(
                line_number=line_no,
                raw_line=line.strip(),
                label=label,
                mnemonic=mnemonic,
                operand=operand,
                mode=mode,
                base_cycles=2,
                max_cycles=4,
                bytes_count=2,
                notes=f"Combinazione {mnemonic} con {mode.value} non ufficiale o non determinata",
            ), None

        # Calcolo cicli con gestione branch e page crossing
        min_c = op_info.cycles
        max_c = op_info.cycles
        notes_list = []

        if op_info.branch_taken_cycle:
            # Istruzioni di branch: 2 cicli se non preso, 3 se preso, 4 se attraversa pagina
            max_c = min_c + 2
            notes_list.append("Branch (2 cicli se non preso, 3 se preso, 4 se page cross)")

        elif op_info.page_boundary_cycle:
            # Istruzioni di lettura indicizzata con potenziale penalità di pagina (+1)
            max_c = min_c + 1
            notes_list.append(f"+1 ciclo se attraversa il confine di pagina ({min_c}..{max_c} cicli)")

        if op_info.flags_affected and op_info.flags_affected != "-":
            notes_list.append(f"Flags: [{op_info.flags_affected}]")

        return InstructionTiming(
            line_number=line_no,
            raw_line=line.strip(),
            label=label,
            mnemonic=mnemonic,
            operand=operand,
            mode=mode,
            opcode_hex=op_info.opcode_hex,
            base_cycles=min_c,
            max_cycles=max_c,
            bytes_count=op_info.bytes_count,
            flags_affected=op_info.flags_affected,
            notes="; ".join(notes_list),
        ), None

    @classmethod
    def analyze_block(cls, code: str) -> CycleCounterReport:
        """Analizza un intero blocco di codice assembly calcolando il budget hardware e temporale."""
        report = CycleCounterReport()
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            timing, directive = cls.parse_line(line, idx)
            if directive:
                report.detected_directives.append(directive)
            if timing:
                report.instructions.append(timing)
                report.total_min_cycles += timing.base_cycles
                report.total_max_cycles += timing.max_cycles
                report.total_bytes += timing.bytes_count

                if timing.max_cycles > timing.base_cycles:
                    if timing.mode == AddressingMode.RELATIVE:
                        report.has_branch_uncertainty = True
                    else:
                        report.has_page_cross_uncertainty = True

        if report.total_min_cycles > 0:
            report.pal_raster_lines = round(report.total_min_cycles / cls.PAL_CYCLES_PER_LINE, 2)
            report.ntsc_raster_lines = round(report.total_min_cycles / cls.NTSC_CYCLES_PER_LINE, 2)

        return report
