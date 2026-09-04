"""Calcolo deterministico dei cicli di clock per il 6502 e Commodore 64."""

from pydantic import BaseModel, Field


class InstructionTiming(BaseModel):
    line_number: int = Field(default=0)
    raw_line: str = Field(description="Riga sorgente assembly")
    mnemonic: str = Field(description="Mnemonic individuato")
    base_cycles: int = Field(description="Cicli di clock minimi")
    max_cycles: int = Field(description="Cicli massimi (in caso di branch o page boundary)")
    bytes_count: int = Field(default=1)
    notes: str = Field(default="")


class CycleCounterReport(BaseModel):
    total_min_cycles: int = 0
    total_max_cycles: int = 0
    total_bytes: int = 0
    pal_raster_lines: float = 0.0  # 63 cicli per linea raster su C64 PAL
    ntsc_raster_lines: float = 0.0  # 65 cicli per linea raster su C64 NTSC
    instructions: list[InstructionTiming] = Field(default_factory=list)


class CycleCounter:
    """Motore deterministico per il calcolo dei cicli di clock del 6502."""

    PAL_CYCLES_PER_LINE = 63
    NTSC_CYCLES_PER_LINE = 65

    # Cicli noti per mnemonici comuni in modalità base (implied/immediate/zeropage/absolute)
    DEFAULT_CYCLES = {
        "NOP": (2, 2, 1),
        "CLC": (2, 2, 1),
        "SEC": (2, 2, 1),
        "CLI": (2, 2, 1),
        "SEI": (2, 2, 1),
        "CLD": (2, 2, 1),
        "SED": (2, 2, 1),
        "CLV": (2, 2, 1),
        "TAX": (2, 2, 1),
        "TXA": (2, 2, 1),
        "TAY": (2, 2, 1),
        "TYA": (2, 2, 1),
        "TSX": (2, 2, 1),
        "TXS": (2, 2, 1),
        "INX": (2, 2, 1),
        "DEX": (2, 2, 1),
        "INY": (2, 2, 1),
        "DEY": (2, 2, 1),
        "PHA": (3, 3, 1),
        "PHP": (3, 3, 1),
        "PLA": (4, 4, 1),
        "PLP": (4, 4, 1),
        "RTS": (6, 6, 1),
        "RTI": (6, 6, 1),
        "JMP": (3, 3, 3),  # 3 cicli se absolute, 5 se indirect
        "JSR": (6, 6, 3),
        # Branching (2 cicli base, 3 se preso, 4 se page boundary)
        "BNE": (2, 4, 2),
        "BEQ": (2, 4, 2),
        "BCC": (2, 4, 2),
        "BCS": (2, 4, 2),
        "BPL": (2, 4, 2),
        "BMI": (2, 4, 2),
        "BVC": (2, 4, 2),
        "BVS": (2, 4, 2),
    }

    @classmethod
    def estimate_line(cls, line: str, line_no: int = 1) -> InstructionTiming | None:
        """Stima i cicli di una singola riga di codice assembly."""
        clean = line.split(";")[0].strip()
        if not clean or clean.endswith(":"):
            return None

        # Rimuove l'etichetta se presente (es. "loop: lda #$00")
        parts = clean.split()
        if parts[0].endswith(":"):
            parts = parts[1:]
        if not parts:
            return None

        mnemonic = parts[0].upper()
        operand = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Calcolo euristico iniziale per mnemonici con operandi (LDA, STA, ADC, etc.)
        if mnemonic in cls.DEFAULT_CYCLES:
            min_c, max_c, b_len = cls.DEFAULT_CYCLES[mnemonic]
            notes = "Branch condizionale (2=non preso, 3=preso, 4=page cross)" if mnemonic.startswith("B") else ""
            return InstructionTiming(
                line_number=line_no,
                raw_line=line.strip(),
                mnemonic=mnemonic,
                base_cycles=min_c,
                max_cycles=max_c,
                bytes_count=b_len,
                notes=notes,
            )

        # Regola generale per Load/Store/Aritmetica
        if mnemonic in {"LDA", "LDX", "LDY", "CMP", "CPX", "CPY", "ADC", "SBC", "AND", "ORA", "EOR"}:
            if operand.startswith("#"):
                return InstructionTiming(
                    line_number=line_no,
                    raw_line=line.strip(),
                    mnemonic=mnemonic,
                    base_cycles=2,
                    max_cycles=2,
                    bytes_count=2,
                    notes="Immediate mode",
                )
            if operand.startswith("$") and len(operand) <= 3:  # es. $02
                return InstructionTiming(
                    line_number=line_no,
                    raw_line=line.strip(),
                    mnemonic=mnemonic,
                    base_cycles=3,
                    max_cycles=3,
                    bytes_count=2,
                    notes="Zero Page",
                )
            return InstructionTiming(
                line_number=line_no,
                raw_line=line.strip(),
                mnemonic=mnemonic,
                base_cycles=4,
                max_cycles=5,
                bytes_count=3,
                notes="Absolute / Indexed mode (4 cicli + 1 se page cross)",
            )

        if mnemonic in {"STA", "STX", "STY"}:
            if operand.startswith("$") and len(operand) <= 3:
                return InstructionTiming(
                    line_number=line_no,
                    raw_line=line.strip(),
                    mnemonic=mnemonic,
                    base_cycles=3,
                    max_cycles=3,
                    bytes_count=2,
                    notes="Zero Page store",
                )
            return InstructionTiming(
                line_number=line_no,
                raw_line=line.strip(),
                mnemonic=mnemonic,
                base_cycles=4,
                max_cycles=5,
                bytes_count=3,
                notes="Absolute store",
            )

        # Default fallback
        return InstructionTiming(
            line_number=line_no,
            raw_line=line.strip(),
            mnemonic=mnemonic,
            base_cycles=2,
            max_cycles=4,
            bytes_count=2,
            notes="Stima generica 6502",
        )

    @classmethod
    def analyze_block(cls, code: str) -> CycleCounterReport:
        """Calcola la spesa totale di cicli di clock e l'equivalente in linee raster C64."""
        report = CycleCounterReport()
        lines = code.strip().splitlines()

        for idx, line in enumerate(lines, start=1):
            timing = cls.estimate_line(line, idx)
            if timing:
                report.instructions.append(timing)
                report.total_min_cycles += timing.base_cycles
                report.total_max_cycles += timing.max_cycles
                report.total_bytes += timing.bytes_count

        if report.total_min_cycles > 0:
            report.pal_raster_lines = round(report.total_min_cycles / cls.PAL_CYCLES_PER_LINE, 2)
            report.ntsc_raster_lines = round(report.total_min_cycles / cls.NTSC_CYCLES_PER_LINE, 2)

        return report
