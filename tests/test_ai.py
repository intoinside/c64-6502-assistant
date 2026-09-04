"""Test completi per l'orchestratore AI, i client LLM e i guardrail deterministici."""

from c64_assistant.ai.engine import AssistantEngine
from c64_assistant.ai.llm_client import BaseLLMClient, OfflineClient, get_llm_client
from c64_assistant.rag.retriever import C64KnowledgeRetriever


class FlawedMockClient(BaseLLMClient):
    """Mock che genera prima codice con istruzioni 65C02 (BRA) e poi lo corregge se riceve il feedback del validatore."""

    def __init__(self):
        self.call_count = 0

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        self.call_count += 1
        # Prima chiamata: allucinazione istruzione 65C02 'bra'
        if self.call_count == 1:
            return """Ecco il codice richiesto per Commodore 64:
```assembly
loop:
    inc $d020
    bra loop
```
"""
        # Seconda chiamata (dopo che il validatore ha segnalato BRA): codice corretto con JMP
        return """Ecco il codice corretto:
```assembly
loop:
    inc $d020
    jmp loop
```
"""


def test_extract_assembly_code():
    markdown = """Spiegazione:
```assembly
lda #$00
sta $d020
rts
```
Fine spiegazione.
"""
    code = AssistantEngine.extract_assembly_code(markdown)
    assert "lda #$00" in code
    assert "sta $d020" in code
    assert "Spiegazione" not in code


def test_offline_client_generates_valid_code():
    client = OfflineClient()
    response = client.generate("come fare un raster interrupt su C64")
    assert "```assembly" in response
    code = AssistantEngine.extract_assembly_code(response)
    assert len(code) > 0

    # Verifica con il motore
    engine = AssistantEngine(llm_client=client)
    res = engine.ask("sincronizzare raster line")
    assert res.validation_report is not None
    assert res.validation_report.is_valid


def test_self_healing_guardrail_loop():
    """Verifica che il ciclo di auto-correzione rilevi l'istruzione 65C02 e corregga autonomamente il codice."""
    mock_client = FlawedMockClient()
    engine = AssistantEngine(llm_client=mock_client)

    response = engine.ask("crea un loop infinito per il colore del bordo", auto_fix=True)

    # Il mock client deve essere stato invocato 2 volte (1 generazione iniziale + 1 auto-correzione)
    assert mock_client.call_count == 2
    assert response.auto_fix_applied
    assert response.fix_iterations == 1
    assert response.validation_report.is_valid
    assert "jmp loop" in response.suggested_code
    assert "bra loop" not in response.suggested_code


def test_get_llm_client_factory():
    offline_client = get_llm_client("offline")
    assert isinstance(offline_client, OfflineClient)

    ollama_client = get_llm_client("ollama", model="qwen2.5-coder")
    assert ollama_client.model == "qwen2.5-coder"
