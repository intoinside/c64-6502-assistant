# Guida di Riferimento Hardware Commodore 64

## Registri Video VIC-II ($D000-$D02E)
Il controllore video VIC-II è mappato a partire dall'indirizzo esadecimale $D000.
I registri principali includono:
- **$D000-$D00F:** Coordinate X e Y degli 8 sprite hardware (Sprite 0-7).
- **$D010:** Bit 8 della coordinata X degli sprite (MSB).
- **$D011:** Registro di controllo 1 del VIC-II (abilitazione schermo a 24/25 righe, modalità testo/bitmap esteso, bit 8 del raster counter).
- **$D012:** Registro del contatore linea raster (lettura della linea corrente o scrittura per generare un raster interrupt).
- **$D015:** Registro abilitazione sprite (1 bit per ciascuno degli 8 sprite).
- **$D019:** Registro interrupt flag del VIC-II (scrivere '1' per confermare e resettare l'interrupt).
- **$D01A:** Registro abilitazione interrupt del VIC-II (bit 0 abilita il raster interrupt).
- **$D020:** Colore del bordo dello schermo (valori da 0 a 15).
- **$D021:** Colore dello sfondo 0 (valori da 0 a 15).

## Timing Rasterline PAL vs NTSC
- **PAL (C64 Europeo):** Frequenza clock ≈ 0.985 MHz. Esattamente 63 cicli di clock della CPU per ogni singola linea raster. Il display ha 312 linee raster totali.
- **NTSC (C64 Americano):** Frequenza clock ≈ 1.023 MHz. Esattamente 65 cicli di clock della CPU per ogni linea raster. Il display ha 263 linee raster totali.
- **Cicli Bad Line:** Durante le righe in cui il VIC-II legge i puntatori caratteri (ogni 8 righe raster nell'area testo), il bus CPU viene fermato ("stolen cycles") per circa 40-43 cicli.

## Registri Sonori SID ($D400-$D41C)
Il sintetizzatore sonoro SID 6581/8580 gestisce 3 voci indipendenti:
- **Voce 1:** Frequenza ($D400-$D401), Pulse Width ($D402-$D403), Controllo forma d'onda ($D404: Noise, Pulse, Saw, Triangle, Gate), Attacco/Decadimento ($D405), Sostegno/Rilascio ($D406).
- **Voce 2:** $D407-$D40D.
- **Voce 3:** $D40E-$D414.
- **Filtro e Volume Master:** $D415-$D418 ($D418 contiene il volume master nei 4 bit bassi 0-15).

## Zero Page ($0000-$00FF)
La Zero Page permette accessi in 3 cicli invece di 4.
- **$0000:** Data Direction Register della porta CPU 6510.
- **$0001:** Port Register della CPU 6510 (gestione banking RAM/ROM: Kernal, BASIC, I/O / Character ROM).
- **$00FB-$00FE:** Quattro locazioni libere inutilizzate dal Kernal/BASIC, comunemente impiegate come puntatori a 16 bit per indirizzamento indiretto indexed ($nn),Y.
