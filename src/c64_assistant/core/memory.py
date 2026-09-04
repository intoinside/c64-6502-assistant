"""Mappa di memoria, banking del 6510 e registri hardware del Commodore 64."""

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
    CHAR_ROM = "char_rom"
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


class BankingConfig(BaseModel):
    value_hex: str
    loram: bool = Field(description="Bit 0: Abilita BASIC ROM a $A000-$BFFF se alto")
    hiram: bool = Field(description="Bit 1: Abilita KERNAL ROM a $E000-$FFFF se alto")
    charen: bool = Field(description="Bit 2: Se basso seleziona Char ROM a $D000, se alto I/O chips")
    basic_rom_visible: bool
    kernal_rom_visible: bool
    io_visible: bool
    char_rom_visible: bool
    description: str


class C64MemoryMap:
    """Modello dettagliato della memoria a 64 KB del Commodore 64."""

    # 1. Regioni di Memoria Principali
    REGIONS = [
        MemoryRegion(
            name="Zero Page (CPU & OS)",
            start_addr=0x0000,
            end_addr=0x00FF,
            region_type=MemoryRegionType.ZERO_PAGE,
            description="Indirizzamento a 1 byte (3 cicli); locazioni $00-$01 controllano il port banking CPU",
            safe_for_user_code=False,
            notes="Locazioni $FB-$FE e $02 libere per il programmatore assembly.",
        ),
        MemoryRegion(
            name="CPU Hardware Stack",
            start_addr=0x0100,
            end_addr=0x01FF,
            region_type=MemoryRegionType.STACK,
            description="Stack hardware gestito dal registro SP (decrescente da $01FF a $0100)",
            safe_for_user_code=False,
            notes="Utilizzato da JSR, RTS, PHA, PLA, PHP, PLP e dalle interruzioni IRQ/NMI.",
        ),
        MemoryRegion(
            name="OS & Kernal Work Vectors",
            start_addr=0x0200,
            end_addr=0x03FF,
            region_type=MemoryRegionType.BASIC_RAM,
            description="Vettori di sistema e buffer di input caratteri",
            safe_for_user_code=False,
            notes="Contiene il vettore IRQ ($0314/$0315), NMI ($0318/$0319) e buffer tastiera ($0277-$0280).",
        ),
        MemoryRegion(
            name="Default Screen RAM",
            start_addr=0x0400,
            end_addr=0x07E7,
            region_type=MemoryRegionType.SCREEN_RAM,
            description="Memoria schermo testo predefinita (40 colonne x 25 righe = 1000 byte)",
            safe_for_user_code=False,
            notes="Posizione modificabile tramite il registro VIC-II $D018.",
        ),
        MemoryRegion(
            name="Sprite Pointers (Default)",
            start_addr=0x07F8,
            end_addr=0x07FF,
            region_type=MemoryRegionType.SCREEN_RAM,
            description="8 puntatori ai blocchi di 64 byte per gli sprite hardware 0-7",
            safe_for_user_code=True,
            notes="Valore n punta all'indirizzo (VIC_BANK * 16384) + (n * 64).",
        ),
        MemoryRegion(
            name="Default BASIC RAM / User Code",
            start_addr=0x0801,
            end_addr=0x9FFF,
            region_type=MemoryRegionType.BASIC_RAM,
            description="Area standard di caricamento programmi BASIC e codice assembly (38 KB)",
            safe_for_user_code=True,
            notes="Indirizzo standard di avvio codice machine language: $0801 (SYS 2061).",
        ),
        MemoryRegion(
            name="BASIC ROM (o RAM sottostante)",
            start_addr=0xA000,
            end_addr=0xBFFF,
            region_type=MemoryRegionType.BASIC_ROM,
            description="Interprete Commodore BASIC V2 (8 KB)",
            safe_for_user_code=False,
            notes="Disattivabile via $0001 (bit 0 = 0) per ottenere altri 8 KB di RAM contigua.",
        ),
        MemoryRegion(
            name="Free User RAM (sotto I/O)",
            start_addr=0xC000,
            end_addr=0xCFFF,
            region_type=MemoryRegionType.FREE_RAM,
            description="Area RAM completamente libera da ROM e OS (4 KB da 49152 a 53247)",
            safe_for_user_code=True,
            notes="Area ideale per routine assembly indipendenti (SYS 49152).",
        ),
        MemoryRegion(
            name="VIC-II Video Controller",
            start_addr=0xD000,
            end_addr=0xD3FF,
            region_type=MemoryRegionType.VIC_II,
            description="Registri del controllore video VIC-II (6569 PAL / 6567 NTSC)",
            safe_for_user_code=True,
            notes="Registri replicati a blocchi di 64 byte fino a $D3FF.",
        ),
        MemoryRegion(
            name="SID Sound Synthesizer",
            start_addr=0xD400,
            end_addr=0xD7FF,
            region_type=MemoryRegionType.SID,
            description="Registri del generatore sonoro MOS 6581/8580 (29 registri per 3 voci e filtri)",
            safe_for_user_code=True,
            notes="Mappato in I/O se $0001 ha bit 2 = 1.",
        ),
        MemoryRegion(
            name="Color RAM (Nibbles)",
            start_addr=0xD800,
            end_addr=0xDBE7,
            region_type=MemoryRegionType.COLOR_RAM,
            description="Memoria colore dei caratteri dello schermo (1000 locazioni a 4 bit)",
            safe_for_user_code=True,
            notes="Valori 0-15 corrispondenti ai 16 colori C64. I 4 bit alti sono non collegati.",
        ),
        MemoryRegion(
            name="CIA 1 (Keyboard, Joysticks & Timers)",
            start_addr=0xDC00,
            end_addr=0xDCFF,
            region_type=MemoryRegionType.CIA_1,
            description="Complex Interface Adapter 1: scansione matrice tastiera, porta joystick 2, timer IRQ",
            safe_for_user_code=False,
            notes="Scrivere senza cautela può disabilitare la tastiera o bloccare il timer a 60 Hz.",
        ),
        MemoryRegion(
            name="CIA 2 (Serial Bus, NMI, VIC Bank)",
            start_addr=0xDD00,
            end_addr=0xDDFF,
            region_type=MemoryRegionType.CIA_2,
            description="Complex Interface Adapter 2: selezione banco VIC-II ($DD00), IEC serial bus disk/printer",
            safe_for_user_code=False,
            notes="Port A bit 0-1 controllano i banchi VIC da 16 KB (valore invertito).",
        ),
        MemoryRegion(
            name="Kernal ROM (o RAM sottostante)",
            start_addr=0xE000,
            end_addr=0xFFFF,
            region_type=MemoryRegionType.KERNAL_ROM,
            description="Sistema Operativo Kernal e Jump Table ($FF81-$FFF3)",
            safe_for_user_code=False,
            notes="Disattivabile via $0001 (bit 1 = 0) per esporre la RAM sottostante.",
        ),
    ]

    # 2. Registri Hardware Noti di Frequente Utilizzo
    REGISTERS_INFO = {
        0xD000: "VIC-II: Sprite 0 X coordinate",
        0xD001: "VIC-II: Sprite 0 Y coordinate",
        0xD010: "VIC-II: Sprite 0-7 X coordinate MSB (bit 8 per posizione > 255)",
        0xD011: "VIC-II: Control Register 1 (Bit 7: Raster line bit 8, Bit 6: ECM, Bit 5: BMM, Bit 4: DEN, Bit 3: RSEL 24/25 righe, Bit 0-2: Y scroll)",
        0xD012: "VIC-II: Raster Counter (Lettura: riga raster corrente 0-255; Scrittura: linea di trigger raster IRQ)",
        0xD015: "VIC-II: Sprite Enable Register (1 bit per sprite 0-7)",
        0xD016: "VIC-II: Control Register 2 (Bit 4: MCM Multicolor, Bit 3: CSEL 38/40 colonne, Bit 0-2: X scroll)",
        0xD018: "VIC-II: Memory Setup Register (Bit 4-7: Indirizzo Screen RAM, Bit 1-3: Indirizzo Character/Bitmap)",
        0xD019: "VIC-II: Interrupt Flag Register (Scrivere 1 per confermare/resettare interrupt raster o collisione)",
        0xD01A: "VIC-II: Interrupt Mask Register (Bit 0: Abilita Raster Interrupt)",
        0xD020: "VIC-II: Border Color (0-15)",
        0xD021: "VIC-II: Background Color 0 (0-15)",
        0xD022: "VIC-II: Background Color 1 (Extra color in MCM)",
        0xD023: "VIC-II: Background Color 2 (Extra color in MCM)",
        0xD024: "VIC-II: Background Color 3",
        0xD027: "VIC-II: Sprite 0 Color",
        0xD400: "SID: Voice 1 Frequency Low Byte",
        0xD401: "SID: Voice 1 Frequency High Byte",
        0xD402: "SID: Voice 1 Pulse Width Low Byte",
        0xD403: "SID: Voice 1 Pulse Width High (Bit 0-3)",
        0xD404: "SID: Voice 1 Control Register (Bit 0: Gate, Bit 1: Sync, Bit 2: RingMod, Bit 3: Test, Bit 4: Triangle, Bit 5: Saw, Bit 6: Pulse, Bit 7: Noise)",
        0xD405: "SID: Voice 1 Attack/Decay (Bit 4-7: Attack, Bit 0-3: Decay)",
        0xD406: "SID: Voice 1 Sustain/Release (Bit 4-7: Sustain, Bit 0-3: Release)",
        0xD418: "SID: Master Volume (Bit 0-3: Volume 0-15) & Filter Mode",
        0xDC00: "CIA 1: Data Port A (Scansione matrice tastiera righe / Joystick 2)",
        0xDC01: "CIA 1: Data Port B (Scansione matrice tastiera colonne / Joystick 1)",
        0xDC0D: "CIA 1: Interrupt Control Register (Scrittura $7F disabilita timer IRQ tastiera)",
        0xDD00: "CIA 2: Data Port A (Bit 0-1 selezionano banco VIC-II: %11=$0000-%3FFF, %10=$4000-%7FFF, %01=$8000-%BFFF, %00=$C000-%FFFF)",
        0xDD0D: "CIA 2: Interrupt Control Register (Scrittura $7F disabilita NMI)",
    }

    # 3. Configurazioni Standard di Banking Memoria tramite registro $0001
    BANKING_CONFIGS = {
        0x37: BankingConfig(
            value_hex="$37 (55)",
            loram=True,
            hiram=True,
            charen=True,
            basic_rom_visible=True,
            kernal_rom_visible=True,
            io_visible=True,
            char_rom_visible=False,
            description="Default all'accensione: BASIC ROM ($A000), Kernal ROM ($E000), I/O ($D000) visibili. 38 KB RAM libera.",
        ),
        0x36: BankingConfig(
            value_hex="$36 (54)",
            loram=False,
            hiram=True,
            charen=True,
            basic_rom_visible=False,
            kernal_rom_visible=True,
            io_visible=True,
            char_rom_visible=False,
            description="BASIC ROM disattivata (sostituita da RAM), Kernal ($E000) e I/O ($D000) visibili. 48 KB RAM contigua.",
        ),
        0x35: BankingConfig(
            value_hex="$35 (53)",
            loram=False,
            hiram=False,
            charen=True,
            basic_rom_visible=False,
            kernal_rom_visible=False,
            io_visible=True,
            char_rom_visible=False,
            description="Tutte le ROM disattivate (sostituite da RAM), I/O ($D000) visibile per VIC-II/SID/CIA. 60 KB RAM disponibile.",
        ),
        0x34: BankingConfig(
            value_hex="$34 (52)",
            loram=False,
            hiram=False,
            charen=False,
            basic_rom_visible=False,
            kernal_rom_visible=False,
            io_visible=False,
            char_rom_visible=True,
            description="Tutta RAM a 64 KB eccetto la Character ROM visibile a $D000-$DFFF (usata per copiare i font in RAM).",
        ),
        0x30: BankingConfig(
            value_hex="$30 (48)",
            loram=False,
            hiram=False,
            charen=False,
            basic_rom_visible=False,
            kernal_rom_visible=False,
            io_visible=False,
            char_rom_visible=False,
            description="Full 64 KB RAM pura: tutte le ROM e i registri di I/O sono disattivati. Accesso completo alla RAM.",
        ),
    }

    # 4. Routine Kernal Jump Table Ufficiali ($FF81-$FFF3)
    KERNAL_JUMP_TABLE = {
        0xFF81: ("CINT", "Inizializza chip video e schermo"),
        0xFF84: ("IOINIT", "Inizializza chip CIA e periferiche I/O"),
        0xFF8A: ("RESTOR", "Ripristina vettori di default I/O del Kernal"),
        0xFF8D: ("VECTOR", "Legge o imposta la tabella vettori Kernal"),
        0xFF90: ("SETMSG", "Imposta flag messaggi Kernal"),
        0xFF99: ("MEMTOP", "Legge o imposta il limite superiore della RAM"),
        0xFF9C: ("MEMBOT", "Legge o imposta il limite inferiore della RAM"),
        0xFFA5: ("ACPTR", "Legge un byte dal bus seriale IEC"),
        0xFFA8: ("CIOUT", "Invia un byte sul bus seriale IEC"),
        0xFFBA: ("SETLFS", "Imposta numero logico di file, device address e secondario"),
        0xFFBD: ("SETNAM", "Imposta lunghezza e puntatore al nome del file"),
        0xFFC0: ("OPEN", "Apre un file logico"),
        0xFFC3: ("CLOSE", "Chiude un file logico"),
        0xFFC6: ("CHKIN", "Definisce il canale di ingresso"),
        0xFFC9: ("CHKOUT", "Definisce il canale di uscita"),
        0xFFCC: ("CLRCHN", "Ripristina i canali standard di I/O (tastiera e schermo)"),
        0xFFCF: ("CHRIN", "Legge un carattere dal canale di input"),
        0xFFD2: ("CHROUT / BSOUT", "Scrive un carattere a video o sul canale attivo"),
        0xFFD5: ("LOAD", "Carica memoria da dispositivo (es. disco 8)"),
        0xFFD8: ("SAVE", "Salva memoria su dispositivo"),
        0xFFE4: ("GETIN", "Legge un carattere dal buffer tastiera senza attendere (restituisce 0 se vuoto)"),
        0xFFF0: ("PLOT", "Legge o imposta la posizione del cursore a video (X=riga, Y=colonna)"),
        0xFFF3: ("IOBASE", "Restituisce l'indirizzo base dei chip I/O ($DC00)"),
    }

    @classmethod
    def get_region_for_address(cls, addr: int) -> MemoryRegion | None:
        """Restituisce la regione di memoria corrispondente a un indirizzo a 16 bit."""
        for region in cls.REGIONS:
            if region.start_addr <= addr <= region.end_addr:
                return region
        return None

    @classmethod
    def get_register_description(cls, addr: int) -> str | None:
        """Restituisce la descrizione di un registro hardware o routine Kernal nota."""
        if addr in cls.REGISTERS_INFO:
            return cls.REGISTERS_INFO[addr]
        if addr in cls.KERNAL_JUMP_TABLE:
            name, desc = cls.KERNAL_JUMP_TABLE[addr]
            return f"Kernal Jump Table: {name} - {desc}"
        return None

    @classmethod
    def get_banking_config(cls, port_value: int) -> BankingConfig:
        """Restituisce la configurazione di banking corrispondente al valore nel registro $0001."""
        clean_val = port_value & 0x37  # I bit rilevanti sono i primi 3 più i bit superiori
        if clean_val in cls.BANKING_CONFIGS:
            return cls.BANKING_CONFIGS[clean_val]

        # Calcolo dinamico per combinazioni custom
        b0 = bool(port_value & 0x01)
        b1 = bool(port_value & 0x02)
        b2 = bool(port_value & 0x04)

        return BankingConfig(
            value_hex=f"${port_value:02X}",
            loram=b0,
            hiram=b1,
            charen=b2,
            basic_rom_visible=(b0 and b1),
            kernal_rom_visible=b1,
            io_visible=b2,
            char_rom_visible=(not b2 and (b0 or b1)),
            description=f"Configurazione custom $0001=%{port_value:08b} (LORAM={b0}, HIRAM={b1}, CHAREN={b2})",
        )

    @classmethod
    def check_zero_page_safety(cls, addr: int) -> dict[str, str | bool]:
        """Analizza dettagliatamente l'uso di un byte in Zero Page ($0000-$00FF)."""
        if not (0x0000 <= addr <= 0x00FF):
            return {"is_zero_page": False, "is_safe": True, "details": "Indirizzo fuori dalla Zero Page"}

        # Locazioni critiche hardware
        if addr == 0x00:
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": "DDR (Data Direction Register) CPU 6510. I bit impostano la direzione dei pin I/O su chip.",
            }
        if addr == 0x01:
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": "CPU Port 6510 (Banking Memoria). I bit 0-2 commutano tra RAM e ROM BASIC/Kernal/IO.",
            }

        # Locazioni garantite libere per l'utente in qualsiasi condizione
        if 0xFB <= addr <= 0xFE:
            return {
                "is_zero_page": True,
                "is_safe": True,
                "details": "Puntatore libero sicuro in Zero Page ($FB-$FE). Consigliato per indirizzamento ($nn),Y.",
            }
        if addr == 0x02:
            return {
                "is_zero_page": True,
                "is_safe": True,
                "details": "Locazione $02 libera: inutilizzata da Kernal e BASIC.",
            }

        # Aree riservate con dettagli sull'uso da parte dell'OS
        if 0x73 <= addr <= 0x8A:
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": "Area CHRGET/CHRGOT: codice eseguibile in Zero Page per la scansione dei token BASIC.",
            }
        if 0x90 <= addr <= 0x97:
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": f"Locazione Kernal I/O Status ($90=ST, $91=STOP key flag, $92=Tape timing).",
            }
        if 0xA0 <= addr <= 0xA2:
            return {
                "is_zero_page": True,
                "is_safe": False,
                "details": "Jiffy Clock di sistema a 60 Hz (incrementato a ogni interrupt hardware CIA 1).",
            }

        return {
            "is_zero_page": True,
            "is_safe": False,
            "details": f"Locazione ${addr:02X} riservata dal Kernal/BASIC. Modificare solo dopo aver disattivato gli interrupt (SEI).",
        }
