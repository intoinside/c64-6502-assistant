"""Client multi-provider per modelli di linguaggio (Ollama locale, Gemini, OpenAI e Offline)."""

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Interfaccia astratta per i client LLM."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Genera una risposta a partire da un prompt e un eventuale system prompt."""
        pass


class OllamaClient(BaseLLMClient):
    """Client per modelli eseguiti 100% in locale tramite Ollama (senza librerie esterne)."""

    def __init__(self, model: str = "qwen2.5-coder", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Impossibile connettersi a Ollama su {self.host}. Verifica che Ollama sia in esecuzione (ollama serve). Dettagli: {e}"
            ) from e


class GeminiClient(BaseLLMClient):
    """Client per modelli Google Gemini tramite google-genai o HTTP REST."""

    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non configurata. Imposta la variabile d'ambiente o usa il provider locale.")

        # Prova ad utilizzare la libreria ufficiale se disponibile
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            return response.text or ""
        except ImportError:
            # Fallback su endpoint REST diretto di Google
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}]
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            return ""


class OpenAIClient(BaseLLMClient):
    """Client compatibile OpenAI (funziona anche con server locali llama.cpp / vLLM / LocalAI)."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key-for-local")
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        url = f"{self.base_url}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return ""
        except urllib.error.URLError as e:
            raise ConnectionError(f"Errore nella chiamata all'endpoint {self.base_url}: {e}") from e


class OfflineClient(BaseLLMClient):
    """Generatore di template deterministico offline: funziona al 100% senza alcuna connessione né modello."""

    TEMPLATES = {
        "raster": """; Esempio sincronizzazione raster VIC-II standard C64
* = $0801
    sei                  ; Disabilita interrupt
    lda #$7f
    sta $dc0d            ; Spegne timer interrupt CIA 1
    lda $dc0d            ; Reset registri interrupt CIA 1

    lda #$01
    sta $d01a            ; Abilita raster interrupt VIC-II
    lda #$7f
    sta $d011            ; Pulisce bit 8 del raster line
    lda #$80
    sta $d012            ; Trigger su linea 128

wait_loop:
    lda $d012
    cmp #$80
    bne wait_loop
    inc $d020            ; Lampeggio bordo
    jmp wait_loop
""",
        "border": """; Lampeggio ciclico del colore del bordo
* = $0801
loop:
    inc $d020            ; Incrementa registro colore bordo
    ldx #$ff
delay:
    dex
    bne delay
    jmp loop
""",
        "sid": """; Inizializzazione e riproduzione nota musicale su SID
* = $0801
    lda #$0f
    sta $d418            ; Imposta volume master al massimo (15)

    lda #$00
    sta $d405            ; Attack immediato, Decay nullo
    lda #$f0
    sta $d406            ; Sustain massimo (15), Release rapido

    lda #$1d
    sta $d401            ; Frequenza alta (Nota LA ~440Hz)
    lda #$50
    sta $d400            ; Frequenza bassa

    lda #$21
    sta $d404            ; Forma d'onda Dente di Sega + Gate attivo
    rts
""",
        "default": """; Routine Assembly 6502 standard per Commodore 64
* = $0801
    lda #$00
    sta $d020            ; Bordo nero
    sta $d021            ; Sfondo nero
    rts
""",
    }

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        p_lower = prompt.lower()
        if "raster" in p_lower:
            code = self.TEMPLATES["raster"]
            desc = "Routine generata per la gestione e sincronizzazione della riga raster con il chip VIC-II."
        elif "sid" in p_lower or "suono" in p_lower or "musica" in p_lower:
            code = self.TEMPLATES["sid"]
            desc = "Configurazione del sintetizzatore SID MOS 6581/8580 per riprodurre una nota a 440 Hz."
        elif "bordo" in p_lower or "border" in p_lower or "colore" in p_lower:
            code = self.TEMPLATES["border"]
            desc = "Ciclo di cambio colore del registro VIC-II $D020 con delay loop su registro X."
        else:
            code = self.TEMPLATES["default"]
            desc = "Snippet generato conforme all'ISA 6502 NMOS per Commodore 64."

        return f"""Ecco la soluzione richiesta per Commodore 64 (6502 NMOS):

{desc}

```assembly
{code}
```

Il codice è conforme al set ufficiale NMOS ed è pronto per essere assemblato con ACME o KickAssembler.
"""


def get_llm_client(
    provider: str = "offline",
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> BaseLLMClient:
    """Factory per istanziare il client LLM appropriato."""
    p = provider.lower().strip()
    if p == "ollama":
        m = model or "qwen2.5-coder"
        host = base_url or "http://localhost:11434"
        return OllamaClient(model=m, host=host)
    elif p == "gemini":
        m = model or "gemini-2.5-flash"
        return GeminiClient(model=m, api_key=api_key)
    elif p in {"openai", "llamacpp", "vllm", "localai"}:
        m = model or "gpt-4o-mini"
        url = base_url or ("http://localhost:8080/v1" if p == "llamacpp" else "https://api.openai.com/v1")
        return OpenAIClient(model=m, api_key=api_key, base_url=url)
    else:
        return OfflineClient()
