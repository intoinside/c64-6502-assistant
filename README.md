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

## 🛠️ Installazione

### Prerequisiti

| Requisito | Versione minima | Note |
|---|---|---|
| **Python** | 3.10+ | [Download](https://www.python.org/downloads/) |
| **Git** | Qualsiasi | Per clonare il repository |
| **Ollama** *(opzionale)* | 0.1+ | Solo per il provider LLM locale. [Download](https://ollama.com/) |

### 1. Clona il repository

```bash
git clone https://github.com/tuo-username/c64-6502-assistant.git
cd c64-6502-assistant
```

### 2. Crea e attiva l'ambiente virtuale

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Installa le dipendenze

> **⚠️ Attenzione:** I comandi seguenti devono essere eseguiti dalla **root del repository** (la cartella `c64-6502-assistant/` che contiene il file `pyproject.toml`). Se ricevi l'errore *"does not appear to be a Python project"*, significa che sei nella directory sbagliata.
>
> ```powershell
> # Verifica di essere nella cartella corretta (deve contenere pyproject.toml)
> cd P:\c64-6502-assistant
> dir pyproject.toml
> ```

Prima di installare, aggiorna `pip` e il build backend `hatchling` alla versione più recente (obbligatorio per evitare errori di compatibilità):

```bash
pip install --upgrade pip hatchling
```

Poi scegli il profilo di installazione più adatto alle tue esigenze:

```bash
# ✅ Installazione base (CLI + validatore deterministico)
pip install -e .

# 🤖 Con supporto AI (provider Gemini e OpenAI)
pip install -e .[ai]

# 📚 Con supporto RAG (ChromaDB + Sentence Transformers)
pip install -e .[rag]

# 🌐 Con interfaccia Web (Streamlit)
pip install -e .[ui]

# 🚀 Tutto incluso (AI + RAG + UI + strumenti di sviluppo)
pip install -e .[all]
```

### 4. (Opzionale) Configura le variabili d'ambiente

Crea un file `.env` nella root del progetto per configurare i provider AI cloud:

```bash
# .env — copia e personalizza questo template
# Lascia vuoto o rimuovi le righe per i provider che non usi

# Google Gemini
GEMINI_API_KEY=la-tua-chiave-api-gemini

# OpenAI
OPENAI_API_KEY=la-tua-chiave-api-openai

# Ollama (locale, nessuna chiave richiesta)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Provider da usare di default: "ollama" | "gemini" | "openai" | "offline"
LLM_PROVIDER=offline
```

> **Nota:** In assenza del file `.env`, l'assistente funziona in modalità `offline`, che usa template deterministici predefiniti senza richiedere alcun modello AI.

---

## 🚀 Utilizzo

### CLI — Comando `c64-assistant`

Il pacchetto installa il comando `c64-assistant` direttamente nel PATH dell'ambiente virtuale.

---

#### `cycles` — Calcola i cicli di clock e le linee raster

Analizza una sequenza di istruzioni Assembly e restituisce il conteggio esatto dei cicli macchina, le linee raster impegnate e il budget disponibile per schermi PAL e NTSC.

```bash
c64-assistant cycles "lda #$00 \n sta $d020 \n nop"
```

**Output di esempio:**
```
┌─────────────────────────────────────────────────┐
│           Analisi Cicli — MOS 6502 NMOS         │
├──────────────┬──────────────────────────────────┤
│ Istruzione   │  Cicli │ Modalità                │
├──────────────┼──────────────────────────────────┤
│ LDA #$00     │      2 │ Immediato               │
│ STA $D020    │      4 │ Assoluto                │
│ NOP          │      2 │ Implicito               │
├──────────────┼──────────────────────────────────┤
│ TOTALE       │      8 │                         │
├──────────────┴──────────────────────────────────┤
│ PAL  (63 cicli/raster): 0.13 linee raster       │
│ NTSC (65 cicli/raster): 0.12 linee raster       │
└─────────────────────────────────────────────────┘
```

---

#### `validate` — Valida un file sorgente Assembly

Controlla che un file sorgente `.asm` non contenga istruzioni illegali per il MOS 6502 NMOS del C64 (es. opcode del 65C02, modalità di indirizzamento errate).

```bash
c64-assistant validate mio_codice.asm
```

**Output (codice valido):**
```
✅ Validazione superata — nessun errore trovato in mio_codice.asm
```

**Output (errori rilevati):**
```
❌ Errori trovati in mio_codice.asm:

  Riga 12: BRA $1234
    → Opcode 65C02: non supportato dal MOS 6502 NMOS del C64.
      Usa invece: BEQ/BNE/BCC/BCS/BMI/BPL/BVC/BVS

  Riga 18: STZ $D020
    → Opcode 65C02: non supportato dal MOS 6502 NMOS del C64.
      Usa invece: LDA #$00 / STA $D020
```

---

#### `memory` — Ispeziona la mappa di memoria del C64

Verifica informazioni dettagliate su qualsiasi indirizzo della mappa di memoria del C64: nome del registro hardware, chip associato, permessi di lettura/scrittura e avvisi di sicurezza per la Zero Page.

```bash
# Registro del colore del bordo (VIC-II)
c64-assistant memory '$D020'

# Locazione nella Zero Page (sicura o riservata al Kernal/BASIC?)
c64-assistant memory '$FB'

# Qualsiasi indirizzo in formato hex
c64-assistant memory '$DC00'
```

**Output di esempio (`$D020`):**
```
┌──────────────────────────────────────────────────┐
│   Mappa Memoria C64 — $D020                      │
├──────────────────────────────────────────────────┤
│  Nome:       VIC-II Border Color Register        │
│  Chip:       VIC-II (MOS 6569 PAL / 6567 NTSC)  │
│  Accesso:    Lettura / Scrittura                 │
│  Categoria:  I/O Hardware ($D000–$DFFF)          │
│  Avviso:     Nessuno — uso sicuro                │
└──────────────────────────────────────────────────┘
```

---

#### `ask` — Assistente AI con Guardrail (Modalità Interattiva)

Poni domande in linguaggio naturale sul C64, la programmazione Assembly 6502 e i registri hardware. La risposta dell'AI viene arricchita dal RAG (documentazione storica) e validata automaticamente dal motore deterministico prima di essere mostrata.

```bash
# Sessione interattiva (REPL)
c64-assistant ask

# Singola domanda diretta
c64-assistant ask "Come si legge il joystick dalla porta 2?"
c64-assistant ask "Scrivi una routine per cancellare lo schermo"
c64-assistant ask "Quanti cicli usa LDA ($FB,X)?"
```

**Scegliere il provider LLM:**
```bash
# Modalità offline (default, nessun modello richiesto)
c64-assistant ask --provider offline "Spiega il registro SID $D400"

# Ollama locale (es. llama3, mistral, codellama)
c64-assistant ask --provider ollama "Genera una routine di attesa"

# Google Gemini (richiede GEMINI_API_KEY in .env)
c64-assistant ask --provider gemini "Come funziona il raster interrupt?"

# OpenAI (richiede OPENAI_API_KEY in .env)
c64-assistant ask --provider openai "Spiega il memory banking del C64"
```

---

### 🌐 Interfaccia Web (Streamlit)

Per chi preferisce un'interfaccia grafica interattiva, avvia la dashboard web locale:

```bash
# Assicurati di aver installato le dipendenze UI
pip install -e .[ui]

# Avvia il server locale
streamlit run src/c64_assistant/ui/web.py
```

Il browser si aprirà automaticamente su `http://localhost:8501`. La dashboard include le seguenti schede:

| Scheda | Funzione |
|---|---|
| **🏠 Home** | Panoramica del progetto e stato del sistema |
| **⚙️ Cicli & Raster** | Calcolatore interattivo di cicli macchina e budget PAL/NTSC |
| **✅ Validatore** | Editor inline per validare codice Assembly in tempo reale |
| **🗺️ Mappa Memoria** | Explorer interattivo della mappa di memoria del C64 |
| **📚 Knowledge Base** | Ricerca semantica nella documentazione storica indicizzata |
| **🤖 Assistente AI** | Chat con il motore AI + guardrail deterministici |

---

### 🧪 Esecuzione dei Test

Tutti i moduli del core deterministico, RAG e AI sono coperti da test automatici con `pytest`:

```bash
# Esegui tutta la suite di test
pytest

# Con report di copertura del codice
pytest --cov=src/c64_assistant --cov-report=term-missing

# Filtra per modulo specifico
pytest tests/test_core.py
pytest tests/test_rag.py
pytest tests/test_ai.py
```

---

## 🔌 Provider LLM — Guida Rapida

| Provider | Connessione | Setup richiesto | Consigliato per |
|---|---|---|---|
| `offline` | Nessuna | Nulla | Test rapidi, uso senza AI |
| `ollama` | Locale | Installare [Ollama](https://ollama.com/) + un modello | Uso quotidiano privacy-first |
| `gemini` | Cloud | `GEMINI_API_KEY` in `.env` | Risposte di alta qualità |
| `openai` | Cloud | `OPENAI_API_KEY` in `.env` | Alternativa cloud |

### Installare un modello con Ollama

```bash
# Scarica e avvia Ollama (una tantum)
# → https://ollama.com/download

# Scarica un modello di codice (esempi)
ollama pull llama3          # Uso generale
ollama pull codellama       # Ottimizzato per il codice
ollama pull mistral         # Bilanciato velocità/qualità

# Verifica che Ollama sia attivo
ollama list
```

---

## 🗺️ Roadmap

- [x] **Fase 1: Setup di progetto, packaging PEP 621 e CI/CD**
- [x] **Fase 2: Motore deterministico base (ISA 6502, Cycle Counter, Memory Map C64)**
- [x] **Fase 3: CLI interattiva (Rich/Typer) e Dashboard Web (Streamlit)**
- [x] **Fase 4: RAG vettoriale con knowledge base locale e manuali indicizzati**
- [x] **Fase 5: Integrazione multi-provider LLM (Ollama + Gemini + OpenAI + Offline) con guardrail**
- [ ] **Fase 6: Analizzatore e simulatore avanzato di interrupt raster del VIC-II**
- [ ] **Fase 7: Supporto VICE debugger integration e export .prg**

---

## 📄 Licenza

Distribuito sotto licenza **MIT**. Consulta il file [`LICENSE`](LICENSE) per ulteriori dettagli.
