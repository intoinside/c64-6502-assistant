# Architettura di C64-6502-Assistant

## Panoramica

`c64-6502-assistant` è un motore ibrido di assistenza allo sviluppo per Assembly 6502 su Commodore 64, progettato seguendo l'approccio ingegneristico di **Rizzo AI Academy**:
- **Local-first & Offline-capable**: Funzionamento su CPU senza dipendenze cloud obbligatorie.
- **Validatore Deterministico come Ground Truth**: La fisica e le regole hardware del 6502/C64 prevalgono sulle allucinazioni probabilistiche dei modelli LLM.
- **RAG di Dominio Verticale**: Indicizzazione locale di documentazione storica e reference guide tecniche.

```
       +-------------------------------------------------------------+
       |                  Interfaccia Utente                         |
       |                (CLI Rich / Web Streamlit)                   |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               Orchestratore Ibrido (AI Engine)              |
       +--------------------+-------------------+--------------------+
                            |                   |
            +---------------+                   +---------------+
            |                                                   |
            v                                                   v
+-----------------------+                           +-----------------------+
|  Base di Conoscenza   |                           |  Validatore Hardware  |
|  (RAG / Manuals C64)  |                           |     Deterministico    |
+-----------------------+                           +-----------------------+
| - Mapping the C64     |                           | - 6502 NMOS ISA Table |
| - Registri VIC-II/SID |                           | - Cycle Counter       |
| - Kernal jump tables  |                           | - PAL/NTSC Budgeting  |
| - Retrieval semantico |                           | - Zero Page & Banking |
+-----------------------+                           +-----------------------+
```

## Moduli del Progetto

### 1. `c64_assistant.core`
Contiene le regole immutabili dell'hardware:
- `opcodes.py`: Formalizzazione delle 56 istruzioni ufficiali NMOS, modalità di indirizzamento e flag. Filtra istruzioni non supportate (es. 65C02).
- `memory.py`: Modellazione della mappa di memoria C64 a 64 KB, inclusa Zero Page, registri I/O VIC-II/SID/CIA e controllo collisioni con il Kernal.
- `cycle_counter.py`: Calcolo deterministico dei cicli di clock spesi da ciascuna istruzione e calcolo delle linee raster impegnate (PAL 63 cicli, NTSC 65 cicli).
- `validator.py`: Ispezione sintattica e architetturale del codice prima dell'esecuzione.

### 2. `c64_assistant.rag`
Fornisce il grounding documentale:
- `loader.py`: Chunking semantico di manuali tecnici in formato Markdown e testo.
- `retriever.py`: Ricerca di sezioni rilevanti tramite indirizzo di memoria (es. `$D020`) o query testuale.

### 3. `c64_assistant.ai`
Gestisce l'interazione intelligente:
- `prompts.py`: System prompt specializzato che istruisce il modello sui vincoli ferrei dell'hardware vintage.
- `engine.py`: Pipeline ibrida che arricchisce il prompt con il contesto RAG e sottopone l'output al validatore deterministico.

### 4. `c64_assistant.ui`
Strumenti per lo sviluppatore:
- `cli.py`: Interfaccia CLI con comandi `cycles`, `validate`, `memory`.
- `web.py`: Interfaccia Web locale con visualizzazione grafica delle metriche hardware.
