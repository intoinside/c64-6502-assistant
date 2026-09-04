"""Definizione formale del set di istruzioni (ISA) 6502 NMOS."""

from enum import Enum
from pydantic import BaseModel, Field


class AddressingMode(str, Enum):
    IMPLIED = "implied"
    ACCUMULATOR = "accumulator"
    IMMEDIATE = "immediate"
    ZERO_PAGE = "zero_page"
    ZERO_PAGE_X = "zero_page_x"
    ZERO_PAGE_Y = "zero_page_y"
    ABSOLUTE = "absolute"
    ABSOLUTE_X = "absolute_x"
    ABSOLUTE_Y = "absolute_y"
    INDIRECT = "indirect"
    INDEXED_INDIRECT_X = "indexed_indirect_x"  # ($nn,X)
    INDIRECT_INDEXED_Y = "indirect_indexed_y"  # ($nn),Y
    RELATIVE = "relative"


class OpcodeInfo(BaseModel):
    mnemonic: str = Field(description="Mnemonic assembly (es. LDA, STA, NOP)")
    mode: AddressingMode = Field(description="Modalità di indirizzamento")
    opcode_hex: str = Field(description="Codice esadecimale dell'opcode (es. 'A9')")
    bytes_count: int = Field(description="Dimensione in byte dell'istruzione")
    cycles: int = Field(description="Cicli base di clock")
    page_boundary_cycle: bool = Field(
        default=False,
        description="Aggiunge 1 ciclo se attraversa il confine di pagina (page boundary)",
    )
    branch_taken_cycle: bool = Field(
        default=False,
        description="Aggiunge 1 ciclo se il branch viene intrapreso",
    )
    flags_affected: str = Field(
        default="",
        description="Flag di stato influenzati (N, V, -, B, D, I, Z, C)",
    )


# 56 Istruzioni Ufficiali 6502 NMOS (Commodore 64 standard)
OFFICIAL_MNEMONICS_NMOS = {
    "ADC", "AND", "ASL", "BCC", "BCS", "BEQ", "BIT", "BMI",
    "BNE", "BPL", "BRK", "BVC", "BVS", "CLC", "CLD", "CLI",
    "CLV", "CMP", "CPX", "CPY", "DEC", "DEX", "DEY", "EOR",
    "INC", "INX", "INY", "JMP", "JSR", "LDA", "LDX", "LDY",
    "LSR", "NOP", "ORA", "PHA", "PHP", "PLA", "PLP", "ROL",
    "ROR", "RTI", "RTS", "SBC", "SEC", "SED", "SEI", "STA",
    "STX", "STY", "TAX", "TAY", "TSX", "TXA", "TXS", "TYA",
}

# Esempi di istruzioni 65C02 non supportate dal 6502 NMOS originale del C64
CMOS_ONLY_MNEMONICS = {
    "BRA", "PHX", "PHY", "PLX", "PLY", "STZ", "TRB", "TSB", "BBR", "BBS",
}

# Mappatura baseline ISA 6502 (estendibile nel Passo 2)
ISA_6502_NMOS: dict[str, list[OpcodeInfo]] = {
    "NOP": [
        OpcodeInfo(
            mnemonic="NOP",
            mode=AddressingMode.IMPLIED,
            opcode_hex="EA",
            bytes_count=1,
            cycles=2,
            flags_affected="-",
        )
    ],
    "LDA": [
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.IMMEDIATE,
            opcode_hex="A9",
            bytes_count=2,
            cycles=2,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.ZERO_PAGE,
            opcode_hex="A5",
            bytes_count=2,
            cycles=3,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.ZERO_PAGE_X,
            opcode_hex="B5",
            bytes_count=2,
            cycles=4,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.ABSOLUTE,
            opcode_hex="AD",
            bytes_count=3,
            cycles=4,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.ABSOLUTE_X,
            opcode_hex="BD",
            bytes_count=3,
            cycles=4,
            page_boundary_cycle=True,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.ABSOLUTE_Y,
            opcode_hex="B9",
            bytes_count=3,
            cycles=4,
            page_boundary_cycle=True,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.INDEXED_INDIRECT_X,
            opcode_hex="A1",
            bytes_count=2,
            cycles=6,
            flags_affected="N,Z",
        ),
        OpcodeInfo(
            mnemonic="LDA",
            mode=AddressingMode.INDIRECT_INDEXED_Y,
            opcode_hex="B1",
            bytes_count=2,
            cycles=5,
            page_boundary_cycle=True,
            flags_affected="N,Z",
        ),
    ],
    "STA": [
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.ZERO_PAGE,
            opcode_hex="85",
            bytes_count=2,
            cycles=3,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.ZERO_PAGE_X,
            opcode_hex="95",
            bytes_count=2,
            cycles=4,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.ABSOLUTE,
            opcode_hex="8D",
            bytes_count=3,
            cycles=4,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.ABSOLUTE_X,
            opcode_hex="9D",
            bytes_count=3,
            cycles=5,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.ABSOLUTE_Y,
            opcode_hex="99",
            bytes_count=3,
            cycles=5,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.INDEXED_INDIRECT_X,
            opcode_hex="81",
            bytes_count=2,
            cycles=6,
            flags_affected="-",
        ),
        OpcodeInfo(
            mnemonic="STA",
            mode=AddressingMode.INDIRECT_INDEXED_Y,
            opcode_hex="91",
            bytes_count=2,
            cycles=6,
            flags_affected="-",
        ),
    ],
}
