"""Suite completa di test per il Motore Deterministico 6502 e Commodore 64."""

from c64_assistant.core.cycle_counter import CycleCounter
from c64_assistant.core.memory import C64MemoryMap
from c64_assistant.core.opcodes import (
    OFFICIAL_MNEMONICS_NMOS,
    AddressingMode,
    get_opcode_info,
    is_cmos_mnemonic,
    is_official_mnemonic,
    is_unofficial_mnemonic,
)
from c64_assistant.core.validator import HardwareValidator


def test_isa_56_official_mnemonics():
    """Verifica che tutte le 56 istruzioni ufficiali NMOS siano censite e conformi."""
    assert len(OFFICIAL_MNEMONICS_NMOS) == 56
    for mnemonic in OFFICIAL_MNEMONICS_NMOS:
        assert is_official_mnemonic(mnemonic)
        assert not is_cmos_mnemonic(mnemonic)


def test_cmos_and_illegal_detection():
    """Verifica il corretto riconoscimento di istruzioni 65C02 ed opcode non documentati."""
    assert is_cmos_mnemonic("BRA")
    assert is_cmos_mnemonic("STZ")
    assert is_cmos_mnemonic("PHX")
    assert not is_official_mnemonic("BRA")

    assert is_unofficial_mnemonic("LAX")
    assert is_unofficial_mnemonic("DCP")
    assert not is_official_mnemonic("LAX")


def test_addressing_mode_resolution():
    """Verifica la deduzione automatica della modalità di indirizzamento corretta."""
    assert CycleCounter.resolve_addressing_mode("NOP", "") == AddressingMode.IMPLIED
    assert CycleCounter.resolve_addressing_mode("ASL", "A") == AddressingMode.ACCUMULATOR
    assert CycleCounter.resolve_addressing_mode("ASL", "") == AddressingMode.ACCUMULATOR
    assert CycleCounter.resolve_addressing_mode("LDA", "#$05") == AddressingMode.IMMEDIATE
    assert CycleCounter.resolve_addressing_mode("LDA", "$02") == AddressingMode.ZERO_PAGE
    assert CycleCounter.resolve_addressing_mode("LDA", "$02,X") == AddressingMode.ZERO_PAGE_X
    assert CycleCounter.resolve_addressing_mode("LDX", "$02,Y") == AddressingMode.ZERO_PAGE_Y
    assert CycleCounter.resolve_addressing_mode("LDA", "$D020") == AddressingMode.ABSOLUTE
    assert CycleCounter.resolve_addressing_mode("LDA", "$D000,X") == AddressingMode.ABSOLUTE_X
    assert CycleCounter.resolve_addressing_mode("LDA", "$D000,Y") == AddressingMode.ABSOLUTE_Y
    assert CycleCounter.resolve_addressing_mode("JMP", "($0314)") == AddressingMode.INDIRECT
    assert CycleCounter.resolve_addressing_mode("LDA", "($FB,X)") == AddressingMode.INDEXED_INDIRECT_X
    assert CycleCounter.resolve_addressing_mode("LDA", "($FB),Y") == AddressingMode.INDIRECT_INDEXED_Y
    assert CycleCounter.resolve_addressing_mode("BNE", "loop") == AddressingMode.RELATIVE


def test_cycle_counting_exactness():
    """Verifica la precisione millimetrica dei cicli di clock calcolati."""
    # NOP = 2 cicli fissi
    timing_nop, _ = CycleCounter.parse_line("nop")
    assert timing_nop is not None
    assert timing_nop.base_cycles == 2 and timing_nop.max_cycles == 2

    # LDA abs,X = 4 cicli base, 5 se attraversa confine pagina
    timing_lda, _ = CycleCounter.parse_line("lda $c000,x")
    assert timing_lda is not None
    assert timing_lda.base_cycles == 4 and timing_lda.max_cycles == 5

    # STA abs,X = sempre 5 cicli (nessun risparmio nelle scritture su 6502)
    timing_sta, _ = CycleCounter.parse_line("sta $c000,x")
    assert timing_sta is not None
    assert timing_sta.base_cycles == 5 and timing_sta.max_cycles == 5

    # BNE = 2 cicli (non preso), 4 cicli max (preso + page boundary)
    timing_bne, _ = CycleCounter.parse_line("bne exit")
    assert timing_bne is not None
    assert timing_bne.base_cycles == 2 and timing_bne.max_cycles == 4

    # INC abs = 6 cicli (Read-Modify-Write)
    timing_inc, _ = CycleCounter.parse_line("inc $d020")
    assert timing_inc is not None
    assert timing_inc.base_cycles == 6 and timing_inc.max_cycles == 6


def test_raster_line_budget():
    """Verifica il calcolo delle linee raster impegnate per C64 PAL e NTSC."""
    # 63 NOP = 126 cicli = esattamente 2.0 linee raster PAL
    code = "\n".join(["nop"] * 63)
    report = CycleCounter.analyze_block(code)
    assert report.total_min_cycles == 126
    assert report.pal_raster_lines == 2.0
    assert report.ntsc_raster_lines == round(126 / 65, 2)


def test_assembler_directives_handling():
    """Verifica che le direttive comuni di ACME e KickAssembler non generino falsi positivi."""
    code = """
    * = $0801
    !to "demo.prg", cbm
    !byte $00, $01
    .pc = $1000
    loop:
        lda #$00
        sta $d020
        rts
    """
    report = HardwareValidator.validate_code(code)
    assert report.is_valid
    assert report.errors_count == 0
    assert len(report.timing_report.detected_directives) >= 3


def test_validator_rejects_invalid_addressing_modes():
    """Verifica che istruzioni usate con modi di indirizzamento inesistenti siano rigettate."""
    # STX supporta ZP, ZP_Y, ABS, ma NON ABS_X
    bad_stx = "stx $1000,x"
    report = HardwareValidator.validate_code(bad_stx)
    assert not report.is_valid
    error_codes = [i.code for i in report.issues]
    assert "INVALID_ADDRESSING_MODE" in error_codes


def test_validator_detects_hazards():
    """Verifica la rilevazione di conflitti con Zero Page, Stack e scrittura su ROM."""
    code = """
    sta $01       ; Conflitto con Banking CPU Port
    inc $0150     ; Scrittura diretta nello Stack hardware
    sta $e000     ; Scrittura nella Kernal ROM in configurazione standard
    """
    report = HardwareValidator.validate_code(code)
    # Codice sintatticamente valido ma con 3 WARNING di hazard
    assert report.is_valid
    assert report.warnings_count == 3
    codes = [i.code for i in report.issues]
    assert "ZERO_PAGE_CONFLICT" in codes
    assert "STACK_HAZARD" in codes
    assert "ROM_WRITE_HAZARD" in codes


def test_c64_banking_configurations():
    """Verifica le configurazioni standard di memoria tramite il registro $0001."""
    conf_37 = C64MemoryMap.get_banking_config(0x37)
    assert conf_37.basic_rom_visible
    assert conf_37.kernal_rom_visible
    assert conf_37.io_visible

    conf_36 = C64MemoryMap.get_banking_config(0x36)
    assert not conf_36.basic_rom_visible
    assert conf_36.kernal_rom_visible

    conf_35 = C64MemoryMap.get_banking_config(0x35)
    assert not conf_35.basic_rom_visible
    assert not conf_35.kernal_rom_visible
    assert conf_35.io_visible

    conf_30 = C64MemoryMap.get_banking_config(0x30)
    assert not conf_30.io_visible
    assert not conf_30.basic_rom_visible
