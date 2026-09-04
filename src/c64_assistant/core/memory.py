"""Mappa di memoria del Commodore 64, aree riservate e banking."""

from enum import Enum
from pydantic import BaseModel, Field


class MemoryRegionType(str, Enum):
    ZERO_PAGE = "zero_page"
    STACK = "stack"
    BASIC_RAM = "basic_ram"
    SCREEN_RAM = "screen_ram"
    VIC_II = "vic_ii"
    SID = "sid"
    COLOR_RAM = "color_ram"
    CIA_1 = "cia_1"
    CIA_2 = "cia_2"
    BASIC_ROM = "basic_rom"
    KERNAL_ROM = "kernal_rom"
    IO_AREA = "io_area"
    FREE_RAM = "free_ram"


class MemoryRegion(BaseModel):
    name: str
    start_addr: int
    end_addr: int
    region_type: MemoryRegionType
    description: str
    safe_for_user_code: bool = True
    notes: str = ""


class C64MemoryMap:
    """Modello delle aree di memoria del Commodore 64 e controlli di sicurezza."""

    # Mappe note standard C64
    REGIONS = [
        MemoryRegion(
            name="Zero Page (CPU & OS)",
            start_addr=0x0000,
            end_addr=0x00FF,
            region_type=MemoryRegionType.ZERO_PAGE,
            description="Locazioni veloci a 1 byte; $0000-$0001 per port banking CPU",
            safe_for_user_code=False,
            notes="Attenzione: $02-$FF sono condivisi con Kernal/BASIC a meno di disattivare gli interrupt.",
        ),
        MemoryRegion(
            name="CPU Hardware Stack",
            start_addr=0x0100,
            end_addr=0x01FF,
            region_type=MemoryRegionType.STACK,
            description="Stack hardware gestito dal registro SP",
            safe_for_user_code=False,
            notes="Non usare come buffer dati generale, rischio stack overflow.",
        ),
        MemoryRegion(
            name="Default Screen RAM",
            start_addr=0x0400,
            end_addr=0x07E7,
            region_type=MemoryRegionType.SCREEN_RAM,
            description="Memoria schermo predefinita testo (40x25)",
            safe_for_user_code=False,
            notes="Scrivere qui altera direttamente i caratteri visualizzati a video.",
        ),
        MemoryRegion(
            name="Default BASIC RAM",
            start_addr=0x0801,
            end_addr=0x9FFF,
            region_type=MemoryRegionType.BASIC_RAM,
            description="Area standard di caricamento programmi BASIC e codice utente",
            safe_for_user_code=True,
            notes="Indirizzo classico di avvio codice machine language: $0801 (SYS 2061).",
        ),
        MemoryRegion(
            name="VIC-II Video Controller",
            start_addr=0xD000,
            end_addr=0xD3FF,
            region_type=MemoryRegionType.VIC_II,
            description="Registri del chip video VIC-II (sprite, raster, colori bordo/sfondo)",
            safe_for_user_code=True,
            notes="Mappato in I/O se $0001 abilita l'I/O.",
        ),
        MemoryRegion(
            name="SID Sound Synthesizer",
            start_addr=0xD400,
            end_addr=0xD7FF,
            region_type=MemoryRegionType.SID,
            description="Registri del sintetizzatore sonoro SID 6581/8580",
            safe_for_user_code=True,
            notes="Mappato in I/O per voci 1-3, filtri e volume.",
        ),
        MemoryRegion(
            name="Color RAM (Nibbles)",
            start_addr=0xD800,
            end_addr=0xDBE7,
            region_type=MemoryRegionType.COLOR_RAM,
            description="Memoria colore dei caratteri (4 bit per cella)",
            safe_for_user_code=True,
            notes="Locazioni a 4 bit (0-15 per i 16 colori C64).",
        ),
        MemoryRegion(
            name="CIA 1 (Keyboard & Joysticks)",
            start_addr=0xDC00,
            end_addr=0xDCFF,
            region_type=MemoryRegionType.CIA_1,
            description="Complex Interface Adapter 1: timer, tastiera, joystick porta 2",
            safe_for_user_code=False,
            notes="Modifiche incaute possono bloccare la scansione della tastiera del Kernal.",
        ),
        MemoryRegion(
            name="CIA 2 (Serial Bus, RS232, VIC Bank)",
            start_addr=0xDD00,
            end_addr=0xDDFF,
            region_type=MemoryRegionType.CIA_2,
            description="Complex Interface Adapter 2: selezione banco VIC-II, IEC bus",
            safe_for_user_code=False,
            notes="Port A ($DD00) controlla i due bit per la selezione del banco 16KB del VIC-II.",
        ),
        MemoryRegion(
            name="Kernal ROM",
            start_addr=0xE000,
            end_addr=0xFFFF,
            region_type=MemoryRegionType.KERNAL_ROM,
            description="Sistema operativo Kernal del C64 e jump table ($FF81-$FFF3)",
            safe_for_user_code=False,
            notes="Solo lettura a meno di bank-switching via $0001 per esporre la RAM sottostante.",
        ),
    ]

    @classmethod
    def get_region_for_address(cls, addr: int) -> MemoryRegion | None:
        """Restituisce la regione di memoria corrispondente a un indirizzo a 16 bit."""
        for region in cls.REGIONS:
            if region.start_addr <= addr <= region.end_addr:
                return region
        return None

    @classmethod
    def check_zero_page_safety(cls, addr: int) -> dict[str, str | bool]:
        """Verifica se una locazione in Zero Page è libera o usata dal sistema."""
        if not (0x0000 <= addr <= 0x00FF):
            return {"is_zero_page": False, "is_safe": True, "details": "Indirizzo fuori da Zero Page"}

        # Locazioni critiche C64 Zero Page
        if addr in (0x00, 0x01):
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": "Registro direzionale o porta CPU 6510 (Banking memoria). Modificare con cautela estrema.",
            }
        # Locazioni libere note per programmi assembly utente (senza BASIC attivo)
        if 0xFB <= addr <= 0xFE:
            return {
                "is_zero_page": True,
                "is_safe": True,
                "details": "Puntatori liberi in Zero Page ($FB-$FE) per uso generico utente.",
            }

        return {
            "is_zero_page": True,
            "is_safe": False,
            "details": f"Locazione ${addr:02X} usata normalmente dal Kernal/BASIC. Richiede disattivazione interrupt o salvataggio.",
        }
