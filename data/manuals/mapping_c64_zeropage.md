# Mapping della Zero Page del Commodore 64 ($0000-$00FF)

## Introduzione
La Zero Page (indirizzi da `$0000` a `$00FF`) è l'area più preziosa della memoria del 6502: consente istruzioni di un byte più corte e veloci di un ciclo di clock. Nel Commodore 64, tuttavia, gran parte della Zero Page è condivisa tra la CPU 6510, l'interprete BASIC e il sistema operativo Kernal.

## Locazioni Hardware Critiche
- **$0000 (D6510 - Data Direction Register):** Imposta la direzione dei 6 pin di I/O della CPU 6510. Valore standard di default: `$2F` (%00101111).
- **$0001 (R6510 - Port Register):** Controlla il banking della memoria di sistema:
  - Bit 0 (`LORAM`): 1 = BASIC ROM visibile a $A000, 0 = RAM.
  - Bit 1 (`HIRAM`): 1 = Kernal ROM visibile a $E000, 0 = RAM.
  - Bit 2 (`CHAREN`): 1 = I/O visibile a $D000, 0 = Character ROM.
  - Bit 3 (`CASSETTE WRITE`): Linea di scrittura registratore Datassette.
  - Bit 4 (`CASSETTE SENSE`): Rileva se un tasto del registratore è premuto.
  - Bit 5 (`MOTOR`): 0 = Motore registratore attivo, 1 = Spento.

## Locazioni Libere e Sicure per il Programmatore Assembly
- **$0002:** Totalmente inutilizzato da Kernal e BASIC. Byte sicuro per flag o contatore.
- **$00FB-$00FE (4 byte liberi):**
  - Definiti ufficialmente da Commodore come puntatori liberi per l'utente.
  - Ideali per due puntatori a 16 bit: `$FB/$FC` e `$FD/$FE`.
  - Usati tipicamente per l'indirizzamento indiretto indicizzato: `lda ($fb),y`.

## Aree Riservate del Sistema Operativo
- **$002D-$002E (VARTAB):** Puntatore all'inizio della tabella variabili del BASIC.
- **$0073-$008A (CHRGET / CHRGOT):**
  - Piccolo frammento di programma in linguaggio macchina copiato in Zero Page all'avvio.
  - Eseguito dal BASIC per leggere il carattere/token successivo da programma.
  - Se il BASIC non è utilizzato, l'intera area ($73-$8A = 24 byte) può essere riutilizzata per codice o variabili utente.
- **$0090 (ST):** Byte di stato I/O del Kernal per operazioni su disco, nastro o seriale.
- **$0091 (STOP):** Flag per il controllo della pressione del tasto RUN/STOP (valore diverso da $7F indica tasto premuto).
- **$00A0-$00A2 (TIME):** Software Jiffy Clock a 24 bit, incrementato 60 volte al secondo dall'interrupt della CIA 1.

## Linee Guida di Sicurezza
1. **Se gli Interrupt di sistema (IRQ) sono attivi:** Non toccare `$0000-$0001`, `$0090-$00A2` e le locazioni usate dai timer.
2. **Se il BASIC è spento (`SEI` eseguito o banking `$36/$35`):** Diventano utilizzabili liberamente tutte le locazioni del BASIC (`$0003-$008F`), inclusa l'area di memoria floating point.
