"""Modulo Core: Regole hardware deterministiche 6502 e Commodore 64."""

from .cycle_counter import CycleCounter, CycleCounterReport, InstructionTiming
from .memory import BankingConfig, C64MemoryMap, MemoryRegion, MemoryRegionType
from .opcodes import (
    CMOS_ONLY_MNEMONICS,
    ISA_6502_NMOS,
    OFFICIAL_MNEMONICS_NMOS,
    UNOFFICIAL_ILLEGAL_MNEMONICS,
    AddressingMode,
    OpcodeInfo,
    get_all_modes_for_mnemonic,
    get_opcode_info,
    is_cmos_mnemonic,
    is_official_mnemonic,
    is_unofficial_mnemonic,
)
from .validator import HardwareValidator, ValidationIssue, ValidationReport

__all__ = [
    "ISA_6502_NMOS",
    "OFFICIAL_MNEMONICS_NMOS",
    "CMOS_ONLY_MNEMONICS",
    "UNOFFICIAL_ILLEGAL_MNEMONICS",
    "OpcodeInfo",
    "AddressingMode",
    "get_opcode_info",
    "get_all_modes_for_mnemonic",
    "is_official_mnemonic",
    "is_cmos_mnemonic",
    "is_unofficial_mnemonic",
    "C64MemoryMap",
    "MemoryRegion",
    "MemoryRegionType",
    "BankingConfig",
    "CycleCounter",
    "CycleCounterReport",
    "InstructionTiming",
    "HardwareValidator",
    "ValidationIssue",
    "ValidationReport",
]
