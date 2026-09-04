"""Orchestratore principale dell'assistente: unione di AI e Validatore Deterministico."""

import os
from pydantic import BaseModel, Field

from c64_assistant.core.validator import HardwareValidator, ValidationReport
from c64_assistant.rag.retriever import C64KnowledgeRetriever
from .prompts import SYSTEM_PROMPT_C64_EXPERT


class AssistantResponse(BaseModel):
    query: str
    explanation: str
    suggested_code: str = ""
    hardware_context: list[str] = Field(default_factory=list)
    validation_report: ValidationReport | None = None


class AssistantEngine:
    """Motore ibrido di assistenza per lo sviluppo 6502/C64."""

    def __init__(
        self,
        retriever: C64KnowledgeRetriever | None = None,
        model_name: str = "gemini-2.5-flash",
    ):
        self.retriever = retriever or C64KnowledgeRetriever()
        self.model_name = model_name

    def analyze_and_validate(self, code: str) -> ValidationReport:
        """Analizza il codice assembly direttamente tramite il validatore hardware deterministico."""
        return HardwareValidator.validate_code(code)

    def ask(self, query: str, code_snippet: str = "") -> AssistantResponse:
        """Elabora una richiesta utente con grounding sui manuali C64 e validazione automatica del codice."""
        # 1. Recupero contesto hardware (RAG)
        context_results = self.retriever.query(query, max_results=2)
        context_texts = [f"[{r.chunk.source_title} - {r.chunk.section}]\n{r.chunk.content}" for r in context_results]

        # 2. Validazione preliminare se viene fornito codice
        report = None
        if code_snippet.strip():
            report = self.analyze_and_validate(code_snippet)

        # 3. Spiegazione tecnica (in modalità locale/offline fornisce analisi deterministica)
        explanation = (
            f"Analisi per C64 (6502 NMOS) con contesto di riferimento su {len(context_results)} sezioni tecniche."
        )

        return AssistantResponse(
            query=query,
            explanation=explanation,
            suggested_code=code_snippet,
            hardware_context=context_texts,
            validation_report=report,
        )
