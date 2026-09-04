"""Definizione formale del set di istruzioni (ISA) 6502 NMOS per Commodore 64.

Contiene tutte le 56 istruzioni ufficiali con tutti i 151 opcode, modalità di
indirizzamento, conteggio byte, cicli base, penalità di pagina e flag.
"""

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
    description: str = Field(
        default="",
        description="Breve descrizione dell'istruzione",
    )


# Insieme completo delle 56 Istruzioni Ufficiali 6502 NMOS (Commodore 64 standard)
OFFICIAL_MNEMONICS_NMOS = {
    "ADC", "AND", "ASL", "BCC", "BCS", "BEQ", "BIT", "BMI",
    "BNE", "BPL", "BRK", "BVC", "BVS", "CLC", "CLD", "CLI",
    "CLV", "CMP", "CPX", "CPY", "DEC", "DEX", "DEY", "EOR",
    "INC", "INX", "INY", "JMP", "JSR", "LDA", "LDX", "LDY",
    "LSR", "NOP", "ORA", "PHA", "PHP", "PLA", "PLP", "ROL",
    "ROR", "RTI", "RTS", "SBC", "SEC", "SED", "SEI", "STA",
    "STX", "STY", "TAX", "TAY", "TSX", "TXA", "TXS", "TYA",
}

# Istruzioni 65C02 (CMOS) assenti nel MOS 6502 NMOS standard del C64
CMOS_ONLY_MNEMONICS = {
    "BRA", "PHX", "PHY", "PLX", "PLY", "STZ", "TRB", "TSB",
    "BBR", "BBS", "BBR0", "BBR1", "BBR2", "BBR3", "BBR4", "BBR5", "BBR6", "BBR7",
    "BBS0", "BBS1", "BBS2", "BBS3", "BBS4", "BBS5", "BBS6", "BBS7",
    "RMB0", "RMB1", "RMB2", "RMB3", "RMB4", "RMB5", "RMB6", "RMB7",
    "SMB0", "SMB1", "SMB2", "SMB3", "SMB4", "SMB5", "SMB6", "SMB7",
    "WAI", "STP",
}

# Opcode non documentati ("illegali") diffusi nella demoscene C64
UNOFFICIAL_ILLEGAL_MNEMONICS = {
    "LAX", "SAX", "DCP", "ISC", "ISB", "SLO", "RLA", "SRE", "RRA",
    "ALR", "ANC", "ARR", "AXS", "LAS", "KIL", "JAM", "SHX", "SHY",
}

# Matrice completa di tutte le 56 istruzioni e 151 combinazioni ufficiali NMOS 6502
ISA_6502_NMOS: dict[str, list[OpcodeInfo]] = {
    "ADC": [
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.IMMEDIATE, opcode_hex="69", bytes_count=2, cycles=2, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.ZERO_PAGE, opcode_hex="65", bytes_count=2, cycles=3, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="75", bytes_count=2, cycles=4, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.ABSOLUTE, opcode_hex="6D", bytes_count=3, cycles=4, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.ABSOLUTE_X, opcode_hex="7D", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="79", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="61", bytes_count=2, cycles=6, flags_affected="N,V,Z,C", description="Add with Carry"),
        OpcodeInfo(mnemonic="ADC", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="71", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Add with Carry"),
    ],
    "AND": [
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.IMMEDIATE, opcode_hex="29", bytes_count=2, cycles=2, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.ZERO_PAGE, opcode_hex="25", bytes_count=2, cycles=3, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="35", bytes_count=2, cycles=4, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.ABSOLUTE, opcode_hex="2D", bytes_count=3, cycles=4, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.ABSOLUTE_X, opcode_hex="3D", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="39", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="21", bytes_count=2, cycles=6, flags_affected="N,Z", description="Logical AND with Accumulator"),
        OpcodeInfo(mnemonic="AND", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="31", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,Z", description="Logical AND with Accumulator"),
    ],
    "ASL": [
        OpcodeInfo(mnemonic="ASL", mode=AddressingMode.ACCUMULATOR, opcode_hex="0A", bytes_count=1, cycles=2, flags_affected="N,Z,C", description="Arithmetic Shift Left"),
        OpcodeInfo(mnemonic="ASL", mode=AddressingMode.ZERO_PAGE, opcode_hex="06", bytes_count=2, cycles=5, flags_affected="N,Z,C", description="Arithmetic Shift Left"),
        OpcodeInfo(mnemonic="ASL", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="16", bytes_count=2, cycles=6, flags_affected="N,Z,C", description="Arithmetic Shift Left"),
        OpcodeInfo(mnemonic="ASL", mode=AddressingMode.ABSOLUTE, opcode_hex="0E", bytes_count=3, cycles=6, flags_affected="N,Z,C", description="Arithmetic Shift Left"),
        OpcodeInfo(mnemonic="ASL", mode=AddressingMode.ABSOLUTE_X, opcode_hex="1E", bytes_count=3, cycles=7, flags_affected="N,Z,C", description="Arithmetic Shift Left"),
    ],
    "BCC": [
        OpcodeInfo(mnemonic="BCC", mode=AddressingMode.RELATIVE, opcode_hex="90", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Carry Clear (C=0)"),
    ],
    "BCS": [
        OpcodeInfo(mnemonic="BCS", mode=AddressingMode.RELATIVE, opcode_hex="B0", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Carry Set (C=1)"),
    ],
    "BEQ": [
        OpcodeInfo(mnemonic="BEQ", mode=AddressingMode.RELATIVE, opcode_hex="F0", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Equal / Zero Set (Z=1)"),
    ],
    "BIT": [
        OpcodeInfo(mnemonic="BIT", mode=AddressingMode.ZERO_PAGE, opcode_hex="24", bytes_count=2, cycles=3, flags_affected="N,V,Z", description="Bit Test with Accumulator"),
        OpcodeInfo(mnemonic="BIT", mode=AddressingMode.ABSOLUTE, opcode_hex="2C", bytes_count=3, cycles=4, flags_affected="N,V,Z", description="Bit Test with Accumulator"),
    ],
    "BMI": [
        OpcodeInfo(mnemonic="BMI", mode=AddressingMode.RELATIVE, opcode_hex="30", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Minus / Negative (N=1)"),
    ],
    "BNE": [
        OpcodeInfo(mnemonic="BNE", mode=AddressingMode.RELATIVE, opcode_hex="D0", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Not Equal / Zero Clear (Z=0)"),
    ],
    "BPL": [
        OpcodeInfo(mnemonic="BPL", mode=AddressingMode.RELATIVE, opcode_hex="10", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Plus / Positive (N=0)"),
    ],
    "BRK": [
        OpcodeInfo(mnemonic="BRK", mode=AddressingMode.IMPLIED, opcode_hex="00", bytes_count=1, cycles=7, flags_affected="B,I", description="Force Interrupt / Break"),
    ],
    "BVC": [
        OpcodeInfo(mnemonic="BVC", mode=AddressingMode.RELATIVE, opcode_hex="50", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Overflow Clear (V=0)"),
    ],
    "BVS": [
        OpcodeInfo(mnemonic="BVS", mode=AddressingMode.RELATIVE, opcode_hex="70", bytes_count=2, cycles=2, branch_taken_cycle=True, page_boundary_cycle=True, flags_affected="-", description="Branch if Overflow Set (V=1)"),
    ],
    "CLC": [
        OpcodeInfo(mnemonic="CLC", mode=AddressingMode.IMPLIED, opcode_hex="18", bytes_count=1, cycles=2, flags_affected="C", description="Clear Carry Flag"),
    ],
    "CLD": [
        OpcodeInfo(mnemonic="CLD", mode=AddressingMode.IMPLIED, opcode_hex="D8", bytes_count=1, cycles=2, flags_affected="D", description="Clear Decimal Mode"),
    ],
    "CLI": [
        OpcodeInfo(mnemonic="CLI", mode=AddressingMode.IMPLIED, opcode_hex="58", bytes_count=1, cycles=2, flags_affected="I", description="Clear Interrupt Disable (Enable Interrupts)"),
    ],
    "CLV": [
        OpcodeInfo(mnemonic="CLV", mode=AddressingMode.IMPLIED, opcode_hex="B8", bytes_count=1, cycles=2, flags_affected="V", description="Clear Overflow Flag"),
    ],
    "CMP": [
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.IMMEDIATE, opcode_hex="C9", bytes_count=2, cycles=2, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.ZERO_PAGE, opcode_hex="C5", bytes_count=2, cycles=3, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="D5", bytes_count=2, cycles=4, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.ABSOLUTE, opcode_hex="CD", bytes_count=3, cycles=4, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.ABSOLUTE_X, opcode_hex="DD", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="D9", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="C1", bytes_count=2, cycles=6, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
        OpcodeInfo(mnemonic="CMP", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="D1", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,Z,C", description="Compare Memory with Accumulator"),
    ],
    "CPX": [
        OpcodeInfo(mnemonic="CPX", mode=AddressingMode.IMMEDIATE, opcode_hex="E0", bytes_count=2, cycles=2, flags_affected="N,Z,C", description="Compare Memory and Index X"),
        OpcodeInfo(mnemonic="CPX", mode=AddressingMode.ZERO_PAGE, opcode_hex="E4", bytes_count=2, cycles=3, flags_affected="N,Z,C", description="Compare Memory and Index X"),
        OpcodeInfo(mnemonic="CPX", mode=AddressingMode.ABSOLUTE, opcode_hex="EC", bytes_count=3, cycles=4, flags_affected="N,Z,C", description="Compare Memory and Index X"),
    ],
    "CPY": [
        OpcodeInfo(mnemonic="CPY", mode=AddressingMode.IMMEDIATE, opcode_hex="C0", bytes_count=2, cycles=2, flags_affected="N,Z,C", description="Compare Memory and Index Y"),
        OpcodeInfo(mnemonic="CPY", mode=AddressingMode.ZERO_PAGE, opcode_hex="C4", bytes_count=2, cycles=3, flags_affected="N,Z,C", description="Compare Memory and Index Y"),
        OpcodeInfo(mnemonic="CPY", mode=AddressingMode.ABSOLUTE, opcode_hex="CC", bytes_count=3, cycles=4, flags_affected="N,Z,C", description="Compare Memory and Index Y"),
    ],
    "DEC": [
        OpcodeInfo(mnemonic="DEC", mode=AddressingMode.ZERO_PAGE, opcode_hex="C6", bytes_count=2, cycles=5, flags_affected="N,Z", description="Decrement Memory"),
        OpcodeInfo(mnemonic="DEC", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="D6", bytes_count=2, cycles=6, flags_affected="N,Z", description="Decrement Memory"),
        OpcodeInfo(mnemonic="DEC", mode=AddressingMode.ABSOLUTE, opcode_hex="CE", bytes_count=3, cycles=6, flags_affected="N,Z", description="Decrement Memory"),
        OpcodeInfo(mnemonic="DEC", mode=AddressingMode.ABSOLUTE_X, opcode_hex="DE", bytes_count=3, cycles=7, flags_affected="N,Z", description="Decrement Memory"),
    ],
    "DEX": [
        OpcodeInfo(mnemonic="DEX", mode=AddressingMode.IMPLIED, opcode_hex="CA", bytes_count=1, cycles=2, flags_affected="N,Z", description="Decrement Index X"),
    ],
    "DEY": [
        OpcodeInfo(mnemonic="DEY", mode=AddressingMode.IMPLIED, opcode_hex="88", bytes_count=1, cycles=2, flags_affected="N,Z", description="Decrement Index Y"),
    ],
    "EOR": [
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.IMMEDIATE, opcode_hex="49", bytes_count=2, cycles=2, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.ZERO_PAGE, opcode_hex="45", bytes_count=2, cycles=3, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="55", bytes_count=2, cycles=4, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.ABSOLUTE, opcode_hex="4D", bytes_count=3, cycles=4, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.ABSOLUTE_X, opcode_hex="5D", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="59", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="41", bytes_count=2, cycles=6, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="EOR", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="51", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,Z", description="Exclusive OR with Accumulator"),
    ],
    "INC": [
        OpcodeInfo(mnemonic="INC", mode=AddressingMode.ZERO_PAGE, opcode_hex="E6", bytes_count=2, cycles=5, flags_affected="N,Z", description="Increment Memory"),
        OpcodeInfo(mnemonic="INC", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="F6", bytes_count=2, cycles=6, flags_affected="N,Z", description="Increment Memory"),
        OpcodeInfo(mnemonic="INC", mode=AddressingMode.ABSOLUTE, opcode_hex="EE", bytes_count=3, cycles=6, flags_affected="N,Z", description="Increment Memory"),
        OpcodeInfo(mnemonic="INC", mode=AddressingMode.ABSOLUTE_X, opcode_hex="FE", bytes_count=3, cycles=7, flags_affected="N,Z", description="Increment Memory"),
    ],
    "INX": [
        OpcodeInfo(mnemonic="INX", mode=AddressingMode.IMPLIED, opcode_hex="E8", bytes_count=1, cycles=2, flags_affected="N,Z", description="Increment Index X"),
    ],
    "INY": [
        OpcodeInfo(mnemonic="INY", mode=AddressingMode.IMPLIED, opcode_hex="C8", bytes_count=1, cycles=2, flags_affected="N,Z", description="Increment Index Y"),
    ],
    "JMP": [
        OpcodeInfo(mnemonic="JMP", mode=AddressingMode.ABSOLUTE, opcode_hex="4C", bytes_count=3, cycles=3, flags_affected="-", description="Jump to New Location"),
        OpcodeInfo(mnemonic="JMP", mode=AddressingMode.INDIRECT, opcode_hex="6C", bytes_count=3, cycles=5, flags_affected="-", description="Jump Indirect (Nota: bug hardware $xxFF su NMOS)"),
    ],
    "JSR": [
        OpcodeInfo(mnemonic="JSR", mode=AddressingMode.ABSOLUTE, opcode_hex="20", bytes_count=3, cycles=6, flags_affected="-", description="Jump to New Location Saving Return Address"),
    ],
    "LDA": [
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.IMMEDIATE, opcode_hex="A9", bytes_count=2, cycles=2, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.ZERO_PAGE, opcode_hex="A5", bytes_count=2, cycles=3, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="B5", bytes_count=2, cycles=4, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.ABSOLUTE, opcode_hex="AD", bytes_count=3, cycles=4, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.ABSOLUTE_X, opcode_hex="BD", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="B9", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="A1", bytes_count=2, cycles=6, flags_affected="N,Z", description="Load Accumulator with Memory"),
        OpcodeInfo(mnemonic="LDA", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="B1", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,Z", description="Load Accumulator with Memory"),
    ],
    "LDX": [
        OpcodeInfo(mnemonic="LDX", mode=AddressingMode.IMMEDIATE, opcode_hex="A2", bytes_count=2, cycles=2, flags_affected="N,Z", description="Load Index X with Memory"),
        OpcodeInfo(mnemonic="LDX", mode=AddressingMode.ZERO_PAGE, opcode_hex="A6", bytes_count=2, cycles=3, flags_affected="N,Z", description="Load Index X with Memory"),
        OpcodeInfo(mnemonic="LDX", mode=AddressingMode.ZERO_PAGE_Y, opcode_hex="B6", bytes_count=2, cycles=4, flags_affected="N,Z", description="Load Index X with Memory"),
        OpcodeInfo(mnemonic="LDX", mode=AddressingMode.ABSOLUTE, opcode_hex="AE", bytes_count=3, cycles=4, flags_affected="N,Z", description="Load Index X with Memory"),
        OpcodeInfo(mnemonic="LDX", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="BE", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Load Index X with Memory"),
    ],
    "LDY": [
        OpcodeInfo(mnemonic="LDY", mode=AddressingMode.IMMEDIATE, opcode_hex="A0", bytes_count=2, cycles=2, flags_affected="N,Z", description="Load Index Y with Memory"),
        OpcodeInfo(mnemonic="LDY", mode=AddressingMode.ZERO_PAGE, opcode_hex="A4", bytes_count=2, cycles=3, flags_affected="N,Z", description="Load Index Y with Memory"),
        OpcodeInfo(mnemonic="LDY", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="B4", bytes_count=2, cycles=4, flags_affected="N,Z", description="Load Index Y with Memory"),
        OpcodeInfo(mnemonic="LDY", mode=AddressingMode.ABSOLUTE, opcode_hex="AC", bytes_count=3, cycles=4, flags_affected="N,Z", description="Load Index Y with Memory"),
        OpcodeInfo(mnemonic="LDY", mode=AddressingMode.ABSOLUTE_X, opcode_hex="BC", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Load Index Y with Memory"),
    ],
    "LSR": [
        OpcodeInfo(mnemonic="LSR", mode=AddressingMode.ACCUMULATOR, opcode_hex="4A", bytes_count=1, cycles=2, flags_affected="N,Z,C", description="Logical Shift Right"),
        OpcodeInfo(mnemonic="LSR", mode=AddressingMode.ZERO_PAGE, opcode_hex="46", bytes_count=2, cycles=5, flags_affected="N,Z,C", description="Logical Shift Right"),
        OpcodeInfo(mnemonic="LSR", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="56", bytes_count=2, cycles=6, flags_affected="N,Z,C", description="Logical Shift Right"),
        OpcodeInfo(mnemonic="LSR", mode=AddressingMode.ABSOLUTE, opcode_hex="4E", bytes_count=3, cycles=6, flags_affected="N,Z,C", description="Logical Shift Right"),
        OpcodeInfo(mnemonic="LSR", mode=AddressingMode.ABSOLUTE_X, opcode_hex="5E", bytes_count=3, cycles=7, flags_affected="N,Z,C", description="Logical Shift Right"),
    ],
    "NOP": [
        OpcodeInfo(mnemonic="NOP", mode=AddressingMode.IMPLIED, opcode_hex="EA", bytes_count=1, cycles=2, flags_affected="-", description="No Operation"),
    ],
    "ORA": [
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.IMMEDIATE, opcode_hex="09", bytes_count=2, cycles=2, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.ZERO_PAGE, opcode_hex="05", bytes_count=2, cycles=3, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="15", bytes_count=2, cycles=4, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.ABSOLUTE, opcode_hex="0D", bytes_count=3, cycles=4, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.ABSOLUTE_X, opcode_hex="1D", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="19", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="01", bytes_count=2, cycles=6, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
        OpcodeInfo(mnemonic="ORA", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="11", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,Z", description="Logical Inclusive OR with Accumulator"),
    ],
    "PHA": [
        OpcodeInfo(mnemonic="PHA", mode=AddressingMode.IMPLIED, opcode_hex="48", bytes_count=1, cycles=3, flags_affected="-", description="Push Accumulator on Stack"),
    ],
    "PHP": [
        OpcodeInfo(mnemonic="PHP", mode=AddressingMode.IMPLIED, opcode_hex="08", bytes_count=1, cycles=3, flags_affected="-", description="Push Processor Status on Stack"),
    ],
    "PLA": [
        OpcodeInfo(mnemonic="PLA", mode=AddressingMode.IMPLIED, opcode_hex="68", bytes_count=1, cycles=4, flags_affected="N,Z", description="Pull Accumulator from Stack"),
    ],
    "PLP": [
        OpcodeInfo(mnemonic="PLP", mode=AddressingMode.IMPLIED, opcode_hex="28", bytes_count=1, cycles=4, flags_affected="N,V,B,D,I,Z,C", description="Pull Processor Status from Stack"),
    ],
    "ROL": [
        OpcodeInfo(mnemonic="ROL", mode=AddressingMode.ACCUMULATOR, opcode_hex="2A", bytes_count=1, cycles=2, flags_affected="N,Z,C", description="Rotate One Bit Left"),
        OpcodeInfo(mnemonic="ROL", mode=AddressingMode.ZERO_PAGE, opcode_hex="26", bytes_count=2, cycles=5, flags_affected="N,Z,C", description="Rotate One Bit Left"),
        OpcodeInfo(mnemonic="ROL", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="36", bytes_count=2, cycles=6, flags_affected="N,Z,C", description="Rotate One Bit Left"),
        OpcodeInfo(mnemonic="ROL", mode=AddressingMode.ABSOLUTE, opcode_hex="2E", bytes_count=3, cycles=6, flags_affected="N,Z,C", description="Rotate One Bit Left"),
        OpcodeInfo(mnemonic="ROL", mode=AddressingMode.ABSOLUTE_X, opcode_hex="3E", bytes_count=3, cycles=7, flags_affected="N,Z,C", description="Rotate One Bit Left"),
    ],
    "ROR": [
        OpcodeInfo(mnemonic="ROR", mode=AddressingMode.ACCUMULATOR, opcode_hex="6A", bytes_count=1, cycles=2, flags_affected="N,Z,C", description="Rotate One Bit Right"),
        OpcodeInfo(mnemonic="ROR", mode=AddressingMode.ZERO_PAGE, opcode_hex="66", bytes_count=2, cycles=5, flags_affected="N,Z,C", description="Rotate One Bit Right"),
        OpcodeInfo(mnemonic="ROR", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="76", bytes_count=2, cycles=6, flags_affected="N,Z,C", description="Rotate One Bit Right"),
        OpcodeInfo(mnemonic="ROR", mode=AddressingMode.ABSOLUTE, opcode_hex="6E", bytes_count=3, cycles=6, flags_affected="N,Z,C", description="Rotate One Bit Right"),
        OpcodeInfo(mnemonic="ROR", mode=AddressingMode.ABSOLUTE_X, opcode_hex="7E", bytes_count=3, cycles=7, flags_affected="N,Z,C", description="Rotate One Bit Right"),
    ],
    "RTI": [
        OpcodeInfo(mnemonic="RTI", mode=AddressingMode.IMPLIED, opcode_hex="40", bytes_count=1, cycles=6, flags_affected="All", description="Return from Interrupt"),
    ],
    "RTS": [
        OpcodeInfo(mnemonic="RTS", mode=AddressingMode.IMPLIED, opcode_hex="60", bytes_count=1, cycles=6, flags_affected="-", description="Return from Subroutine"),
    ],
    "SBC": [
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.IMMEDIATE, opcode_hex="E9", bytes_count=2, cycles=2, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.ZERO_PAGE, opcode_hex="E5", bytes_count=2, cycles=3, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="F5", bytes_count=2, cycles=4, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.ABSOLUTE, opcode_hex="ED", bytes_count=3, cycles=4, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.ABSOLUTE_X, opcode_hex="FD", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="F9", bytes_count=3, cycles=4, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="E1", bytes_count=2, cycles=6, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
        OpcodeInfo(mnemonic="SBC", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="F1", bytes_count=2, cycles=5, page_boundary_cycle=True, flags_affected="N,V,Z,C", description="Subtract with Borrow"),
    ],
    "SEC": [
        OpcodeInfo(mnemonic="SEC", mode=AddressingMode.IMPLIED, opcode_hex="38", bytes_count=1, cycles=2, flags_affected="C", description="Set Carry Flag"),
    ],
    "SED": [
        OpcodeInfo(mnemonic="SED", mode=AddressingMode.IMPLIED, opcode_hex="F8", bytes_count=1, cycles=2, flags_affected="D", description="Set Decimal Mode"),
    ],
    "SEI": [
        OpcodeInfo(mnemonic="SEI", mode=AddressingMode.IMPLIED, opcode_hex="78", bytes_count=1, cycles=2, flags_affected="I", description="Set Interrupt Disable Status"),
    ],
    "STA": [
        # Nota: Le istruzioni Store su indirizzi indicizzati non beneficiano mai del risparmio di cicli (5 o 6 cicli fissi)
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.ZERO_PAGE, opcode_hex="85", bytes_count=2, cycles=3, flags_affected="-", description="Store Accumulator in Memory"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="95", bytes_count=2, cycles=4, flags_affected="-", description="Store Accumulator in Memory"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.ABSOLUTE, opcode_hex="8D", bytes_count=3, cycles=4, flags_affected="-", description="Store Accumulator in Memory"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.ABSOLUTE_X, opcode_hex="9D", bytes_count=3, cycles=5, page_boundary_cycle=False, flags_affected="-", description="Store Accumulator in Memory (5 cicli fissi)"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.ABSOLUTE_Y, opcode_hex="99", bytes_count=3, cycles=5, page_boundary_cycle=False, flags_affected="-", description="Store Accumulator in Memory (5 cicli fissi)"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.INDEXED_INDIRECT_X, opcode_hex="81", bytes_count=2, cycles=6, flags_affected="-", description="Store Accumulator in Memory"),
        OpcodeInfo(mnemonic="STA", mode=AddressingMode.INDIRECT_INDEXED_Y, opcode_hex="91", bytes_count=2, cycles=6, page_boundary_cycle=False, flags_affected="-", description="Store Accumulator in Memory (6 cicli fissi)"),
    ],
    "STX": [
        OpcodeInfo(mnemonic="STX", mode=AddressingMode.ZERO_PAGE, opcode_hex="86", bytes_count=2, cycles=3, flags_affected="-", description="Store Index X in Memory"),
        OpcodeInfo(mnemonic="STX", mode=AddressingMode.ZERO_PAGE_Y, opcode_hex="96", bytes_count=2, cycles=4, flags_affected="-", description="Store Index X in Memory"),
        OpcodeInfo(mnemonic="STX", mode=AddressingMode.ABSOLUTE, opcode_hex="8E", bytes_count=3, cycles=4, flags_affected="-", description="Store Index X in Memory"),
    ],
    "STY": [
        OpcodeInfo(mnemonic="STY", mode=AddressingMode.ZERO_PAGE, opcode_hex="84", bytes_count=2, cycles=3, flags_affected="-", description="Store Index Y in Memory"),
        OpcodeInfo(mnemonic="STY", mode=AddressingMode.ZERO_PAGE_X, opcode_hex="94", bytes_count=2, cycles=4, flags_affected="-", description="Store Index Y in Memory"),
        OpcodeInfo(mnemonic="STY", mode=AddressingMode.ABSOLUTE, opcode_hex="8C", bytes_count=3, cycles=4, flags_affected="-", description="Store Index Y in Memory"),
    ],
    "TAX": [
        OpcodeInfo(mnemonic="TAX", mode=AddressingMode.IMPLIED, opcode_hex="AA", bytes_count=1, cycles=2, flags_affected="N,Z", description="Transfer Accumulator to Index X"),
    ],
    "TAY": [
        OpcodeInfo(mnemonic="TAY", mode=AddressingMode.IMPLIED, opcode_hex="A8", bytes_count=1, cycles=2, flags_affected="N,Z", description="Transfer Accumulator to Index Y"),
    ],
    "TSX": [
        OpcodeInfo(mnemonic="TSX", mode=AddressingMode.IMPLIED, opcode_hex="BA", bytes_count=1, cycles=2, flags_affected="N,Z", description="Transfer Stack Pointer to Index X"),
    ],
    "TXA": [
        OpcodeInfo(mnemonic="TXA", mode=AddressingMode.IMPLIED, opcode_hex="8A", bytes_count=1, cycles=2, flags_affected="N,Z", description="Transfer Index X to Accumulator"),
    ],
    "TXS": [
        OpcodeInfo(mnemonic="TXS", mode=AddressingMode.IMPLIED, opcode_hex="9A", bytes_count=1, cycles=2, flags_affected="-", description="Transfer Index X to Stack Pointer"),
    ],
    "TYA": [
        OpcodeInfo(mnemonic="TYA", mode=AddressingMode.IMPLIED, opcode_hex="98", bytes_count=1, cycles=2, flags_affected="N,Z", description="Transfer Index Y to Accumulator"),
    ],
}

# Costruzione indice veloce per lookup esadecimale (Opcode Hex -> OpcodeInfo)
OPCODE_BY_HEX: dict[str, OpcodeInfo] = {}
for mnem, ops in ISA_6502_NMOS.items():
    for op in ops:
        OPCODE_BY_HEX[op.opcode_hex.upper()] = op


def get_opcode_info(mnemonic: str, mode: AddressingMode) -> OpcodeInfo | None:
    """Restituisce le specifiche OpcodeInfo per una data combinazione di mnemonico e modo."""
    ops = ISA_6502_NMOS.get(mnemonic.upper(), [])
    for op in ops:
        if op.mode == mode:
            return op
    return None


def get_all_modes_for_mnemonic(mnemonic: str) -> list[AddressingMode]:
    """Restituisce tutte le modalità di indirizzamento supportate da un mnemonico."""
    ops = ISA_6502_NMOS.get(mnemonic.upper(), [])
    return [op.mode for op in ops]


def is_official_mnemonic(mnemonic: str) -> bool:
    """Verifica se il mnemonico fa parte delle 56 istruzioni ufficiali 6502 NMOS."""
    return mnemonic.upper() in OFFICIAL_MNEMONICS_NMOS


def is_cmos_mnemonic(mnemonic: str) -> bool:
    """Verifica se l'istruzione appartiene al set 65C02 (incompatibile con C64 standard)."""
    return mnemonic.upper() in CMOS_ONLY_MNEMONICS


def is_unofficial_mnemonic(mnemonic: str) -> bool:
    """Verifica se il mnemonico fa parte degli opcode illegali / non documentati."""
    return mnemonic.upper() in UNOFFICIAL_ILLEGAL_MNEMONICS
