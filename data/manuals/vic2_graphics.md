# Controllore Video VIC-II (MOS 6569 PAL / 6567 NTSC)

## Registri Base e Funzioni ($D000-$D02E)
Il chip VIC-II controlla l'uscita video, la gestione dei colori, il testo, i bitmap e gli 8 sprite hardware:
- **$D000-$D00F:** Coordinate X (byte basso) e Y per gli 8 sprite (da Sprite 0 a Sprite 7).
- **$D010:** Bit 8 per la coordinata X di ciascuno sprite (consente coordinate orizzontali fino a 511 pixel).
- **$D011:** Registro di Controllo 1:
  - Bit 7: Bit 8 del contatore raster (`$D012`).
  - Bit 6: Extended Color Mode (ECM).
  - Bit 5: Bitmap Mode (BMM) (1 = Bitmap, 0 = Testo).
  - Bit 4: Screen Enable (DEN) (1 = Schermo attivo, 0 = Bordo copre lo schermo).
  - Bit 3: Dimensione Schermo (RSEL) (1 = 25 righe, 0 = 24 righe per scroll verticale).
  - Bit 0-2: Scroll verticale fluido (0-7 pixel).
- **$D012:** Registro del contatore della riga raster corrente (0-255). Se scritto, imposta la linea di trigger per il raster interrupt.
- **$D015:** Abilitazione sprite (1 bit per sprite: 1=attivo, 0=spento).
- **$D016:** Registro di Controllo 2:
  - Bit 4: Multicolor Mode (MCM) per testo o bitmap (1=attivo).
  - Bit 3: Dimensione Schermo (CSEL) (1 = 40 colonne, 0 = 38 colonne per scroll orizzontale).
  - Bit 0-2: Scroll orizzontale fluido (0-7 pixel).
- **$D018:** Memory Setup (Bit 4-7: indirizzo Screen RAM a blocchi di 1 KB; Bit 1-3: indirizzo Character ROM / Bitmap a blocchi di 2 KB/8 KB).
- **$D019:** Interrupt Flag Register (Bit 0: Raster IRQ avvenuto. Scrivere '1' su questo bit per confermare e azzerare l'interrupt).
- **$D01A:** Interrupt Mask Register (Bit 0: Abilita la generazione di Raster Interrupts).
- **$D020:** Colore del bordo dello schermo (valori da 0 a 15).
- **$D021:** Colore dello sfondo standard (Background 0).
- **$D022-$D024:** Colori sfondo ausiliari 1-3 in modalità Multicolor ed ECM.
- **$D025-$D026:** Colori condivisi per sprite multicolor.
- **$D027-$D02E:** Colore individuale per ciascuno degli sprite 0-7.

## Timing Rasterline PAL vs NTSC e Bad Lines
- **PAL (C64 Standard Europeo):** Frequenza clock ≈ 0.985 MHz. Esattamente 63 cicli di clock della CPU per linea raster; 312 linee totali per frame (50 Hz).
- **NTSC (C64 Standard USA):** Frequenza clock ≈ 1.023 MHz. Esattamente 65 cicli di clock della CPU per linea raster; 263 linee totali per frame (60 Hz).
- **Bad Lines (Linee Cattive):** Nelle modalità testo, ogni 8 righe raster all'interno dell'area visibile (quando `$D011` bit 0-2 corrisponde agli ultimi 3 bit del contatore raster), il VIC-II "ruba" il bus dati alla CPU per caricare i codici carattere per le successive 8 righe. Questo sottrae circa 40-43 cicli alla CPU, lasciando solo 20-23 cicli disponibili su quella specifica linea.

## Gestione dei Raster Interrupt e Stabilizzazione
Per eseguire codice perfettamente agganciato al pennello elettronico (es. barre colore a riga fissa o cambi di modalità grafica al pixel):
1. Disattivare le interruzioni CIA 1 (`lda #$7f / sta $dc0d`).
2. Configurare `$D01A` con bit 0 = 1 per abilitare il raster IRQ del VIC-II.
3. Impostare la riga desiderata scrivendo in `$D012` e configurando il bit 7 di `$D011`.
4. Puntare il vettore IRQ di sistema (`$0314-$0315` se Kernal attivo, oppure `$FFFE-$FFFF` in full RAM).
5. All'interno della routine di interrupt, confermare l'evento con `asl $d019` o `dec $d019` (scrivendo '1' sul bit 0).

## Selezione del Banco VIC-II da 16 KB (CIA 2 $DD00)
Il VIC-II può indirizzare direttamente solo 16 KB di memoria alla volta. La scelta del blocco di 16 KB avviene tramite i bit 0 e 1 della porta A del CIA 2 (`$DD00`):
- **%11 (Valore 3):** Banco 0 ($0000-$3FFF) - Default all'avvio.
- **%10 (Valore 2):** Banco 1 ($4000-$7FFF).
- **%01 (Valore 1):** Banco 2 ($8000-$BFFF).
- **%00 (Valore 0):** Banco 3 ($C000-$FFFF).
*Nota:* I bit sono invertiti (0 seleziona l'area alta, 1 l'area bassa). Modificare sempre preservando gli altri bit con `ora` e `and`.
