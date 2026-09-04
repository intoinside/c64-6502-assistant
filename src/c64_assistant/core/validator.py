"""Validatore deterministico per codice Assembly 6502 su Commodore 64.

Verifica conformità all'ISA NMOS, compatibilità delle modalità di indirizzamento,
collisioni con la memoria di sistema (Zero Page, Stack, ROM Kernal/BASIC) e
fornisce suggerimenti precisi di correzione.
"""

import re
from pydantic import BaseModel, Field

from .cycle_counter import CycleCounter, CycleCounterReport
from .memory import C64MemoryMap, MemoryRegionType
from .opcodes import (
    AddressingMode,
    CMOS_ONLY_MNEMONICS,
    OFFICIAL_MNEMONICS_NMOS,
    UNOFFICIAL_ILLEGAL_MNEMONICS,
    get_all_modes_for_mnemonic,
    get_opcode_info,
    is_cmos_mnemonic,
    is_official_mnemonic,
    is_unofficial_mnemonic,
)


class ValidationIssue(BaseModel):
    line_number: int
    severity: str = Field(description="ERROR, WARNING o INFO")
    code: str = Field(description="Identificativo univoco del problema")
    message: str
    suggestion: str = ""


class ValidationReport(BaseModel):
    is_valid: bool = True
    errors_count: int = 0
    warnings_count: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)
    timing_report: CycleCounterReport = Field(default_factory=CycleCounterReport)


class HardwareValidator:
    """Validatore deterministico basato sulle specifiche fisiche del MOS 6502 e C64."""

    @classmethod
    def validate_code(cls, code: str) -> ValidationReport:
        report = ValidationReport()
        report.timing_report = CycleCounter.analyze_block(code)

        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            clean = CycleCounter.clean_comment(line)
            if not clean:
                continue

            # Riconoscimento ed esclusione direttive assembler diffuse
            if any(clean.lower().startswith(d) for d in CycleCounter.KNOWN_DIRECTIVES) or "*=" in clean.replace(" ", ""):
                continue

            parts = clean.split()
            # Salta etichetta standalone (es. "loop:")
            if parts[0].endswith(":") and len(parts) == 1:
                continue
            if parts[0].endswith(":"):
                parts = parts[1:]
            elif len(parts) > 1 and parts[0].upper() not in OFFICIAL_MNEMONICS_NMOS and not is_cmos_mnemonic(parts[0]) and not is_unofficial_mnemonic(parts[0]):
                # Prima parola etichetta senza due punti
                parts = parts[1:]

            if not parts:
                continue

            mnemonic = parts[0].upper()
            operand = " ".join(parts[1:]) if len(parts) > 1 else ""

            # Salta macro o direttive locali (es. .byte, !word)
            if mnemonic.startswith(".") or mnemonic.startswith("!"):
                continue

            # 1. Verifica istruzioni 65C02 (incompatibili con il C64 standard)
            if is_cmos_mnemonic(mnemonic):
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="ERROR",
                        code="CMOS_INSTRUCTION_NOT_SUPPORTED",
                        message=f"L'istruzione '{mnemonic}' è un'estensione 65C02/CMOS assente nel 6502 NMOS del C64.",
                        suggestion=cls._suggest_cmos_replacement(mnemonic),
                    )
                )
                continue

            # 2. Verifica opcode illegali / non documentati (tipici della demoscene)
            if is_unofficial_mnemonic(mnemonic):
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="WARNING",
                        code="UNOFFICIAL_OPCODE",
                        message=f"'{mnemonic}' è un opcode non documentato (illegale) del 6502.",
                        suggestion="Funziona su C64 fisico, ma potrebbe creare instabilità con versioni alternative della CPU o emulatori non accurati.",
                    )
                )

            # 3. Verifica mnemonico sconosciuto
            elif not is_official_mnemonic(mnemonic):
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="ERROR",
                        code="UNKNOWN_MNEMONIC",
                        message=f"Istruzione '{mnemonic}' sconosciuta.",
                        suggestion="Usa solo istruzioni del set ufficiale MOS 6502 NMOS.",
                    )
                )
                continue

            # 4. Verifica compatibilità modalità di indirizzamento per questo mnemonico
            mode = CycleCounter.resolve_addressing_mode(mnemonic, operand)
            op_info = get_opcode_info(mnemonic, mode)

            if not op_info:
                allowed_modes = [m.value for m in get_all_modes_for_mnemonic(mnemonic)]
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="ERROR",
                        code="INVALID_ADDRESSING_MODE",
                        message=f"L'istruzione '{mnemonic}' non supporta la modalità di indirizzamento '{mode.value}' con operando '{operand}'.",
                        suggestion=f"Modalità supportate per {mnemonic}: {', '.join(allowed_modes)}.",
                    )
                )

            # 5. Ispezione indirizzi per controlli di collisione memoria
            cls._check_memory_hazards(idx, mnemonic, operand, report)

        report.errors_count = sum(1 for i in report.issues if i.severity == "ERROR")
        report.warnings_count = sum(1 for i in report.issues if i.severity == "WARNING")
        report.is_valid = report.errors_count == 0

        return report

    @classmethod
    def _suggest_cmos_replacement(cls, mnemonic: str) -> str:
        """Fornisce il suggerimento idiomatico per sostituire istruzioni 65C02 con codice 6502 standard."""
        replacements = {
            "BRA": "Sostituisci BRA con un salto incondizionato JMP o con una condizione sempre vera (es. SEC / BCS oppure CLV / BVC).",
            "STZ": "Il 6502 non ha STZ; carica zero nell'accumulatore o in un registro indice (LDA #$00) e usa STA.",
            "PHX": "Il 6502 non ha PHX; trasferisci X in A (TXA) e fai PHA.",
            "PHY": "Il 6502 non ha PHY; trasferisci Y in A (TYA) e fai PHA.",
            "PLX": "Il 6502 non ha PLX; estrai lo stack in A (PLA) e trasferisci in X (TAX).",
            "PLY": "Il 6502 non ha PLY; estrai lo stack in A (PLA) e trasferisci in Y (TAY).",
        }
        return replacements.get(mnemonic, "Usa le istruzioni standard del 6502 NMOS.")

    @classmethod
    def _check_memory_hazards(cls, line_no: int, mnemonic: str, operand: str, report: ValidationReport) -> None:
        """Verifica se l'operando indirizza locazioni pericolose o sensibili della memoria C64."""
        # Estrazione indirizzo esadecimale ($nn o $nnnn)
        hex_match = re.search(r"\$([0-9a-fA-F]{1,4})\b", operand)
        if not hex_match or operand.startswith("#"):
            return

        addr = int(hex_match.group(1), 16)
        is_write = mnemonic in {"STA", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR"}

        # A. Controllo Zero Page ($0000-$00FF)
        if addr <= 0xFF:
            zp_info = C64MemoryMap.check_zero_page_safety(addr)
            if not zp_info["is_safe"]:
                report.issues.append(
                    ValidationIssue(
                        line_number=line_no,
                        severity="WARNING",
                        code="ZERO_PAGE_CONFLICT",
                        message=f"Accesso a Zero Page ${addr:02X}: {zp_info['details']}",
                        suggestion="Se usi routine Kernal o interrupt, preferisci i puntatori utente liberi ($FB-$FE) o la locazione $02.",
                    )
                )

        # B. Controllo scrittura nell'area Stack CPU ($0100-$01FF)
        elif 0x0100 <= addr <= 0x01FF and is_write:
            report.issues.append(
                ValidationIssue(
                    line_number=line_no,
                    severity="WARNING",
                    code="STACK_HAZARD",
                    message=f"Scrittura diretta nello Stack hardware (${addr:04X}). Rischio di corrompere indirizzi di ritorno e registri.",
                    suggestion="Usa le istruzioni di stack native (PHA, PLA, PHP, PLP, JSR, RTS) oppure verifica con cura lo Stack Pointer.",
                )
            )

        # C. Controllo scrittura in aree ROM di default ($A000-$BFFF e $E000-$FFFF)
        elif (0xA000 <= addr <= 0xBFFF or 0xE000 <= addr <= 0xFFFF) and is_write:
            region = C64MemoryMap.get_region_for_address(addr)
            reg_name = region.name if region else "ROM Area"
            report.issues.append(
                ValidationIssue(
                    line_number=line_no,
                    severity="WARNING",
                    code="ROM_WRITE_HAZARD",
                    message=f"Scrittura nell'area {reg_name} (${addr:04X}). In configurazione standard la ROM è attiva e la scrittura non ha effetto a schermo o RAM.",
                    suggestion="Se intendi scrivere nella RAM sottostante, devi prima disattivare la ROM configurando il registro di banking $0001 (es. $36 o $35).",
                )
            )
