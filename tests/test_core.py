"""Test unitari per il modulo core (ISA 6502, Cycle Counter, Memory Map, Validator)."""

from c64_assistant.core.cycle_counter import CycleCounter
from c64_assistant.core.memory import C64MemoryMap
from c64_assistant.core.validator import HardwareValidator


def test_cycle_counter_basic():
    code = """
    lda #$00
    sta $d020
    nop
    """
    report = CycleCounter.analyze_block(code)
    # LDA immediate = 2, STA absolute = 4..5, NOP = 2 -> min 8 cicli
    assert report.total_min_cycles >= 8
    assert report.total_bytes >= 6
    assert report.pal_raster_lines > 0.0


def test_memory_map_regions():
    vic_region = C64MemoryMap.get_region_for_address(0xD020)
    assert vic_region is not None
    assert vic_region.name.startswith("VIC-II")

    sid_region = C64MemoryMap.get_region_for_address(0xD400)
    assert sid_region is not None
    assert "SID" in sid_region.name


def test_zero_page_safety():
    # $01 is reserved for 6510 CPU Port (Banking)
    check_01 = C64MemoryMap.check_zero_page_safety(0x01)
    assert not check_01["is_safe"]

    # $FB is a free safe user pointer location
    check_fb = C64MemoryMap.check_zero_page_safety(0xFB)
    assert check_fb["is_safe"]


def test_validator_detects_cmos_instructions():
    # BRA and STZ are 65C02 instructions, not valid on stock C64 (6502 NMOS)
    invalid_code = """
    stz $d020
    bra loop
    """
    report = HardwareValidator.validate_code(invalid_code)
    assert not report.is_valid
    assert report.errors_count == 2
    error_codes = [issue.code for issue in report.issues]
    assert "CMOS_INSTRUCTION_NOT_SUPPORTED" in error_codes


def test_validator_accepts_valid_c64_code():
    valid_code = """
    lda #$00
    sta $d020
    rts
    """
    report = HardwareValidator.validate_code(valid_code)
    assert report.is_valid
    assert report.errors_count == 0
