# Sintetizzatore Sonoro SID (MOS 6581 / MOS 8580)

## Architettura del Chip ($D400-$D41C)
Il Sound Interface Device (SID) è mappato nell'area I/O a partire da `$D400`. Dispone di 3 voci oscillatrici indipendenti a sintesi sottrattiva, filtri programmabili (passa-basso, passa-alto, passa-banda) e un generatore di rumore bianco.

## Mappa dei Registri per Singola Voce
Ogni voce occupa un blocco di 7 registri consecutivi:
- **Voce 1:** `$D400-$D406`
- **Voce 2:** `$D407-$D40D`
- **Voce 3:** `$D40E-$D414`

### Registri di ciascuna voce (Offset +0 .. +6):
1. **Freq Low Byte (+0):** Byte basso della frequenza dell'oscillatore (8 bit).
2. **Freq High Byte (+1):** Byte alto della frequenza dell'oscillatore (8 bit).
   - Formula frequenza reale su PAL: `F_out = (Valore * 0.05859) Hz`.
   - Ad esempio: il LA a 440 Hz corrisponde a un valore a 16 bit di circa `7504` (`$1D50`).
3. **Pulse Width Low (+2):** Byte basso del duty cycle per onda quadra (bit 0-7).
4. **Pulse Width High (+3):** Byte alto del duty cycle (solo bit 0-3). Valore $0800 equivale a un'onda quadra perfetta (50%).
5. **Control Register (+4):**
   - **Bit 7 (Noise):** Genera rumore bianco pseudo-casuale (per percussioni, spari, esplosioni).
   - **Bit 6 (Pulse):** Forma d'onda a impulso/quadra (variabile tramite Pulse Width).
   - **Bit 5 (Sawtooth):** Forma d'onda a dente di sega (ricca di armoniche, ottima per archi e ottoni).
   - **Bit 4 (Triangle):** Forma d'onda triangolare (suono dolce, simile a flauto o basso).
   - **Bit 3 (Test):** Resetta e blocca l'oscillatore.
   - **Bit 2 (RingMod):** Modulazione ad anello (combina la voce corrente con la precedente).
   - **Bit 1 (Sync):** Hard sync dell'oscillatore con la voce precedente.
   - **Bit 0 (Gate):** 1 = Avvia l'inviluppo (Attack/Decay/Sustain); 0 = Avvia la fase di rilascio (Release).
6. **Attack / Decay (+5):**
   - Bit 4-7: Durata Attack (tempo impiegato per raggiungere il volume massimo da 2ms a 8s).
   - Bit 0-3: Durata Decay (tempo per scendere al livello di sustain).
7. **Sustain / Release (+6):**
   - Bit 4-7: Livello di Sustain (volume costante mantenuto finché il bit Gate rimane a 1, da 0 a 15).
   - Bit 0-3: Durata Release (tempo di decadimento a zero dopo che il Gate viene azzerato).

## Registri Globali: Filtri e Volume Master ($D415-$D418)
- **$D415:** Filter Cutoff Frequency Low (bit 0-2).
- **$D416:** Filter Cutoff Frequency High (bit 0-7). Frequenza di taglio complessiva a 11 bit ($0000-$07FF).
- **$D417:** Controllo Risonanza e Instradamento Voci:
  - Bit 4-7: Risonanza del filtro (0 = nessuna risonanza, 15 = auto-oscillazione).
  - Bit 0-3: Abilita il passaggio nel filtro per Voce 1 (bit 0), Voce 2 (bit 1), Voce 3 (bit 2) o ingresso esterno (bit 3).
- **$D418:** Master Volume e Modalità Filtro:
  - Bit 7: Disabilita Voce 3 (Voice 3 Mute).
  - Bit 6: Abilita Filtro Passa-Alto (High-Pass).
  - Bit 5: Abilita Filtro Passa-Banda (Band-Pass).
  - Bit 4: Abilita Filtro Passa-Basso (Low-Pass).
  - Bit 0-3: Volume Master principale (da 0 per muto a 15 per massimo volume). Deve essere impostato (es. `$0F`) per sentire qualsiasi suono.

## Sequenza di Inizializzazione Tipica
1. Azzerare tutti i registri da `$D400` a `$D418`.
2. Impostare il volume master in `$D418` (es. `lda #$0f / sta $d418`).
3. Definire l'inviluppo ADSR desiderato (es. Attack immediato e Decay medio: `$D405 = $09`, Sustain pieno: `$D406 = $F0`).
4. Scrivere la frequenza in `$D400` e `$D401`.
5. Selezionare la forma d'onda e attivare il gate in `$D404` (es. dente di sega: `lda #$21 / sta $d404`).
