# c64-6502-assistant

### Motore di assistenza ibrido per lo sviluppo Assembly MOS 6502 su Commodore 64

*Scrivi codice Assembly per il C64 con la potenza dell'Intelligenza Artificiale e la precisione deterministica del validatore hardware.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture: Hybrid](https://img.shields.io/badge/Architecture-Hybrid%20AI%20%2B%20Rules-7c3aed.svg)](#-architettura-ibrida)
[![Target: MOS 6502](https://img.shields.io/badge/Target-MOS%206502%20NMOS-red.svg)](#-propositi-del-progetto)
[![Platform: C64](https://img.shields.io/badge/Platform-Commodore%2064-0078D6.svg)](#-propositi-del-progetto)

---

## 🎯 Propositi del Progetto

Lo sviluppo in linguaggio **Assembly per Commodore 64 (MOS 6502)** richiede un controllo millimetrico delle risorse hardware: conteggio esatto dei cicli di clock per il timing video (VIC-II), allocazione attenta della Zero Page e rispetto rigoroso dell'Instruction Set Architecture (ISA) originale NMOS del 1982.

I moderni Large Language Model (come ChatGPT o Claude) offrono un'eccellente capacità generativa, ma nel retrocomputing soffrono di **gravi allucinazioni**: introducono istruzioni inesistenti (es. appartenenti al 65C02 come `BRA` o `STZ`), inventano i conteggi dei cicli di clock e sovrascrivono locazioni di memoria critiche per il sistema operativo Kernal/BASIC.

**`c64-6502-assistant` nasce con i seguenti propositi fondamentali:**

1. **Eliminare le allucinazioni dell'IA nel retrocomputing**: Agire da filtro e supervisore hardware, garantendo che ogni riga di codice generata sia strettamente conforme al microprocessore MOS 6502 NMOS del C64.
2. **Fornire un *Ground Truth* deterministico**: Integrare un validatore hardware locale basato su regole matematiche e fisiche certe (cicli macchina, indirizzamenti legali, limiti fisici dei registri).
3. **Calcolare con precisione cicli di clock e linee raster**: Fornire all'istante il budget temporale delle routine per schermi PAL (63 cicli per linea raster) e NTSC (65 cicli per linea raster), fondamentale per raster split, aperture dei bordi e sincronizzazioni con il VIC-II.
4. **Prevenire conflitti di memoria e banking**: Riconoscere le locazioni riservate della Zero Page (`$00-$FF`), i registri di I/O (`$D000-$DFFF`) e le aree di memoria sensibili per evitare crash imprevisti o corruzioni dello stack.
5. **Supportare lo sviluppatore con documentazione storica (RAG)**: Consentire l'interrogazione semantica contestuale di testi di riferimento storici (es. *Mapping the Commodore 64*, manuali VIC-II, SID 6581/8580 e Jump Table del Kernal).
6. **Approccio *Local-First* e accessibile**: Funzionare interamente in locale su CPU standard, senza obbligo di chiavi API cloud, garantendo velocità, indipendenza e riproducibilità.

---

## 🏛️ Architettura Ibrida

Il progetto adotta un'architettura ibrida a due stadi: l'**AI** fornisce flessibilità, spiegazioni e bozze di codice, mentre il **Core Deterministico** ne certifica la correttezza prima che raggiunga lo sviluppatore.

```
                  [ Richiesta Sviluppatore ]
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │        Modulo RAG & Generazione AI        │ ◄── [ Manuali Tecnici C64 ]
        │  (Comprensione, sintesi e spiegazioni)    │     (Mapping C64, VIC-II, SID)
        └───────────────────────────────────────────┘
                              │ (Bozza Assembly 6502)
                              ▼
        ┌───────────────────────────────────────────┐
        │      Validatore Hardware Deterministico   │ ──► [ Rifiuto opcodes 65C02/invalidi ]
        │         (Ground Truth 6502 NMOS)          │ ──► [ Calcolo cicli esatti PAL/NTSC ]
        └───────────────────────────────────────────┘ ──► [ Controllo Zero Page & Registri ]
                              │
                              ▼ (Codice verificato al 100%)
                 [ Output Pronto per l'Uso ]
```

### Confronto con gli approcci tradizionali

| Caratteristica | LLM Generico (ChatGPT/Claude) | Assemblatore (ACME/KickAssembler) | **c64-6502-assistant** |
|---|---|---|---|
| **Spiegazione & Scrittura guidata** | ✅ Sì | ❌ No | **✅ Sì (Guidata da RAG)** |
| **Rifiuto opcodes 65C02 su C64** | ❌ Spesso allucina opcodes errati | ⚠️ Rilevato solo a compilazione | **✅ Validato in tempo reale** |
| **Calcolo cicli & budget raster** | ❌ Inaffidabile / Inventato | ❌ Manuale (a cura dell'utente) | **✅ Deterministico (PAL/NTSC)** |
| **Controllo sicurezza Zero Page** | ❌ Non consapevole del Kernal | ❌ Nessun controllo semantico | **✅ Avvisi su aree riservate** |
| **Esecuzione Offline / Locale** | ❌ Connessione Cloud richiesta | ✅ Locale | **✅ Local-first (CPU-friendly)** |

---

## 📁 Struttura del Progetto

Il repository segue il moderno standard `src`-layout con packaging compatibile con PEP 621:

```text
c64-6502-assistant/
├── .github/
│   └── workflows/          # Pipeline CI (test automatici e linting)
├── data/
│   └── manuals/            # Manuali e testi storici di riferimento (Markdown/TXT)
├── docs/                   # Specifiche di architettura e documentazione
├── src/
│   └── c64_assistant/
│       ├── core/           # Motore deterministico 6502 (ISA, cicli, memoria, validatore)
│       ├── rag/            # Parsing e recupero semantico della documentazione
│       ├── ai/             # Prompt engineering, guardrail e orchestrazione AI
│       └── ui/             # Interfaccia CLI (Rich/Typer) e Web (Streamlit)
├── tests/                  # Suite di test unitari (pytest)
├── pyproject.toml          # Configurazione e dipendenze del pacchetto
└── README.md               # Documentazione principale del progetto
```

---

## 🚀 Quickstart

### 1. Requisiti e Installazione

Requisito: **Python 3.10 o superiore**.

```bash
# 1. Clona il repository
git clone https://github.com/tuo-username/c64-6502-assistant.git
cd c64-6502-assistant

# 2. Crea e attiva l'ambiente virtuale
python -m venv .venv
# Su Windows:
.venv\Scripts\activate
# Su Linux/macOS:
source .venv/bin/activate

# 3. Installa il pacchetto in modalità editabile con dipendenze di sviluppo
pip install -e .[dev]
```

### 2. Utilizzo della CLI

Il pacchetto mette a disposizione il comando `c64-assistant`:

#### Calcolo dei cicli di clock e linee raster
Calcola i cicli di clock spesi e le linee raster impegnate per schermi PAL e NTSC:
```bash
c64-assistant cycles "lda #$00 \n sta $d020 \n nop"
```

#### Validazione di un file sorgente Assembly
Controlla che un file sorgente `.asm` non contenga istruzioni non valide per il MOS 6502 del C64:
```bash
c64-assistant validate mio_codice.asm
```

#### Ispezione della mappa di memoria del C64
Verifica permessi, registri hardware associati e sicurezza della Zero Page:
```bash
# Registro colore del bordo (VIC-II)
c64-assistant memory '$D020'

# Locazione Zero Page (verifica se sicura o usata dal Kernal/BASIC)
c64-assistant memory '$FB'
```

### 3. Interfaccia Web Locale (Streamlit)

Per avviare la dashboard grafica interattiva:

```bash
pip install -e .[ui]
streamlit run src/c64_assistant/ui/web.py
```

### 4. Esecuzione dei Test

Tutti i moduli del core deterministico e RAG sono coperti da test automatici:

```bash
pytest
```

---

## 🗺️ Roadmap

- [x] **Fase 1: Setup di progetto, packaging PEP 621 e CI/CD**
- [x] **Fase 2: Motore deterministico base (ISA 6502, Cycle Counter, Memory Map C64)**
- [x] **Fase 3: CLI interattiva (Rich/Typer) e Dashboard Web (Streamlit)**
- [ ] **Fase 4: RAG vettoriale avanzato con database locale (ChromaDB) e manuali indicizzati**
- [ ] **Fase 5: Integrazione multi-provider LLM (Ollama locale + API esterne facoltative)**
- [ ] **Fase 6: Analizzatore e simulatore avanzato di interrupt raster del VIC-II**

---

## 📄 Licenza

Distribuito sotto licenza **MIT**. Consulta il file [`LICENSE`](LICENSE) per ulteriori dettagli.
