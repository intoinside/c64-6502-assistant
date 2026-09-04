# Routine della Kernal Jump Table del Commodore 64 ($FF81-$FFF3)

## Introduzione
La Kernal Jump Table garantisce la retrocompatibilità del codice machine language attraverso tutte le revisioni di ROM del C64. Le chiamate alle routine del sistema operativo devono essere sempre effettuate tramite i vettori della tabella da `$FF81` a `$FFF3`, mai saltando direttamente all'interno della ROM.

## Routine di Input / Output Principali

### $FFD2 - BSOUT / CHROUT (Stampa Carattere)
- **Scopo:** Invia un byte/carattere ASCII-PETSCII al canale di uscita attivo (per default lo schermo).
- **Parametri di ingresso:** `A` = codice carattere PETSCII da stampare.
- **Registri modificati:** Nessuno (preserva A, X, Y).
- **Esempio:**
  ```assembly
  lda #$41       ; Carattere 'A' in PETSCII
  jsr $ffd2      ; Visualizza 'A' a video
  ```

### $FFE4 - GETIN (Lettura Carattere da Buffer Tastiera)
- **Scopo:** Legge un carattere dal buffer della tastiera senza attendere l'interazione dell'utente.
- **Parametri di ingresso:** Nessuno.
- **Parametri di uscita:** `A` = codice PETSCII del tasto premuto, oppure `0` se il buffer è vuoto.
- **Registri modificati:** `A`, `X`, `Y`.

### $FFCF - CHRIN (Input Carattere Bloccante)
- **Scopo:** Legge un carattere dal canale di ingresso attivo. Se lo schermo/tastiera è attivo, mostra il cursore lampeggiante e attende la pressione del tasto RETURN.
- **Parametri di uscita:** `A` = codice carattere letto.
- **Registri modificati:** `A`.

### $FFF0 - PLOT (Lettura o Posizionamento Cursore Schermo)
- **Scopo:** Sposta il cursore di testo a una specifica riga e colonna, oppure ne legge la coordinata attuale.
- **Parametri di ingresso:**
  - `C = 1` (Carry Set): Legge la posizione corrente (restituisce `X` = riga 0-24, `Y` = colonna 0-39).
  - `C = 0` (Carry Clear): Imposta la posizione (con `X` = riga 0-24, `Y` = colonna 0-39).
- **Esempio:**
  ```assembly
  clc            ; 0 = Imposta posizione
  ldx #$0c       ; Riga 12
  ldy #$13       ; Colonna 19
  jsr $fff0      ; Posiziona il cursore al centro dello schermo
  ```

## Routine di Gestione File e Periferiche (Disk Drive #8)

### $FFBA - SETLFS (Imposta Parametri Logici del File)
- **Scopo:** Configura il numero logico del file, il device number (es. 8 per drive a dischi) e l'indirizzo secondario.
- **Parametri di ingresso:**
  - `A` = Logical File Number (es. 1)
  - `X` = Device Number (8 = primo drive floppy 1541)
  - `Y` = Secondary Address (0 = carica all'indirizzo base standard $0801, 1 = carica all'indirizzo originale nel file header).

### $FFBD - SETNAM (Imposta Nome File)
- **Scopo:** Definisce la lunghezza e il puntatore in memoria al nome del file da caricare o salvare.
- **Parametri di ingresso:**
  - `A` = Lunghezza della stringa nome file (numero di caratteri).
  - `X` = Byte basso dell'indirizzo della stringa in memoria.
  - `Y` = Byte alto dell'indirizzo della stringa in memoria.

### $FFD5 - LOAD (Caricamento Dati in Memoria)
- **Scopo:** Carica un file dal dispositivo specificato in RAM.
- **Parametri di ingresso:**
  - `A` = 0 per LOAD ordinario, 1 per VERIFY.
  - `X / Y` = Indirizzo di destinazione alternativo se l'indirizzo secondario è 0.
- **Parametri di uscita:** `C = 0` se caricamento riuscito (`X/Y` indicano l'indirizzo finale in memoria + 1); `C = 1` se si è verificato un errore (codice errore in `A`).

### $FFCC - CLRCHN (Ripristino Canali Standard)
- **Scopo:** Chiude i canali aperti per periferiche e ripristina la tastiera come canale di ingresso e lo schermo come canale di uscita.
