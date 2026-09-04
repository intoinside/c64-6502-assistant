"""Validatore deterministico per codice Assembly 6502 su Commodore 64."""

import re
from pydantic import BaseModel, Field

from .cycle_counter import CycleCounter, CycleCounterReport
from .memory import C64MemoryMap
from .opcodes import CMOS_ONLY_MNEMONICS, OFFICIAL_MNEMONICS_NMOS


class ValidationIssue(BaseModel):
    line_number: int
    severity: str = Field(description="ERROR, WARNING o INFO")
    code: str = Field(description="Identificativo dell'errore (es. INVALID_OPCODE)")
    message: str
    suggestion: str = ""


class ValidationReport(BaseModel):
    is_valid: bool = True
    errors_count: int = 0
    warnings_count: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)
    timing_report: CycleCounterReport = Field(default_factory=CycleCounterReport)


class HardwareValidator:
    """Validatore di regole fisiche e architetturali del Commodore 64."""

    @classmethod
    def validate_code(cls, code: str) -> ValidationReport:
        report = ValidationReport()
        report.timing_report = CycleCounter.analyze_block(code)

        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            clean = line.split(";")[0].strip()
            if not clean or clean.endswith(":"):
                continue

            parts = clean.split()
            if parts[0].endswith(":"):
                parts = parts[1:]
            if not parts:
                continue

            mnemonic = parts[0].upper()
            operand = " ".join(parts[1:]) if len(parts) > 1 else ""

            # 1. Verifica opcode CMOS non supportati dal 6502 NMOS standard del C64
            if mnemonic in CMOS_ONLY_MNEMONICS:
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="ERROR",
                        code="CMOS_INSTRUCTION_NOT_SUPPORTED",
                        message=f"L'istruzione '{mnemonic}' appartiene al 65C02 e non è supportata dal 6502 NMOS del C64.",
                        suggestion=f"Sostituisci '{mnemonic}' con sequenza standard 6502 NMOS (es. per BRA usa JMP o BNE/BEQ garantito).",
                    )
                )

            # 2. Verifica mnemonico non riconosciuto
            elif mnemonic not in OFFICIAL_MNEMONICS_NMOS and not mnemonic.startswith("."):
                report.issues.append(
                    ValidationIssue(
                        line_number=idx,
                        severity="ERROR",
                        code="UNKNOWN_MNEMONIC",
                        message=f"Istruzione '{mnemonic}' sconosciuta o illegale.",
                        suggestion="Usa solo istruzioni del set ufficiale 6502.",
                    )
                )

            # 3. Controllo sicurezza indirizzamento Zero Page ($00-$FF)
            hex_match = re.search(r"\$([0-9a-fA-F]{2})\b", operand)
            if hex_match and not operand.startswith("#"):
                addr = int(hex_match.group(1), 16)
                zp_check = C64MemoryMap.check_zero_page_safety(addr)
                if not zp_check["is_safe"]:
                    report.issues.append(
                        ValidationIssue(
                            line_number=idx,
                            severity="WARNING",
                            code="ZERO_PAGE_CONFLICT",
                            message=f"Accesso a Zero Page ${addr:02X}: {zp_check['details']}",
                            suggestion="Usa puntatori liberi in Zero Page ($FB-$FE) oppure salva/ripristina la locazione.",
                        )
                    )

        report.errors_count = sum(1 for i in report.issues if i.severity == "ERROR")
        report.warnings_count = sum(1 for i in report.issues if i.severity == "WARNING")
        report.is_valid = report.errors_count == 0

        return report
