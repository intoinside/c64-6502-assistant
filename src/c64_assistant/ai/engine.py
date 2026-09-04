"""Orchestratore principale dell'assistente: pipeline ibrida AI + RAG + Guardrail Deterministici."""

import re
from pydantic import BaseModel, Field

from c64_assistant.core.validator import HardwareValidator, ValidationReport
from c64_assistant.rag.retriever import C64KnowledgeRetriever, SearchResult
from .llm_client import BaseLLMClient, get_llm_client
from .prompts import (
    AUTO_FIX_PROMPT_TEMPLATE,
    RAG_PROMPT_TEMPLATE,
    SYSTEM_PROMPT_C64_EXPERT,
)


class AssistantResponse(BaseModel):
    query: str
    explanation: str
    suggested_code: str = ""
    raw_llm_output: str = ""
    hardware_context: list[str] = Field(default_factory=list)
    validation_report: ValidationReport | None = None
    auto_fix_applied: bool = False
    fix_iterations: int = 0
    fix_history: list[str] = Field(default_factory=list)


class AssistantEngine:
    """Motore ibrido di assistenza per lo sviluppo 6502/C64.

    Combina la generazione guidata da LLM (locale o remoto) con la verifica
    deterministica immediata del codice e un ciclo di auto-correzione (self-healing)
    se vengono rilevati errori hardware.
    """

    def __init__(
        self,
        retriever: C64KnowledgeRetriever | None = None,
        llm_client: BaseLLMClient | None = None,
        provider: str = "offline",
        model: str | None = None,
    ):
        self.retriever = retriever or C64KnowledgeRetriever()
        self.llm_client = llm_client or get_llm_client(provider=provider, model=model)

    @classmethod
    def extract_assembly_code(cls, text: str) -> str:
        """Estrae blocchi di codice assembly da una risposta markdown."""
        # 1. Ricerca blocchi formali con tag assembly o asm
        blocks = re.findall(r"```(?:assembly|asm)\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if blocks:
            return blocks[0].strip()

        # 2. Ricerca qualsiasi blocco tra backtick
        any_blocks = re.findall(r"```\n(.*?)```", text, re.DOTALL)
        if any_blocks:
            return any_blocks[0].strip()

        # 3. Ricerca righe che somigliano ad assembly (LDA, STA, NOP, RTS, ecc.)
        lines = text.splitlines()
        code_lines = []
        asm_keywords = {"LDA", "STA", "LDX", "STX", "LDY", "STY", "JMP", "JSR", "RTS", "NOP", "BNE", "BEQ", "INC", "DEC", "SEI", "CLI"}
        for line in lines:
            words = line.strip().split()
            if words and any(w.upper() in asm_keywords for w in words):
                code_lines.append(line.strip())

        if code_lines:
            return "\n".join(code_lines)

        return text.strip()

    def analyze_and_validate(self, code: str) -> ValidationReport:
        """Analizza il codice direttamente tramite il validatore hardware deterministico."""
        return HardwareValidator.validate_code(code)

    def ask(
        self,
        query: str,
        code_snippet: str = "",
        auto_fix: bool = True,
        max_fix_attempts: int = 2,
    ) -> AssistantResponse:
        """Elabora una richiesta utente con grounding RAG, generazione LLM e validazione deterministica."""
        # 1. Retrieval RAG: Recupero del contesto tecnico da manuali
        context_results: list[SearchResult] = self.retriever.query(query, max_results=3)
        context_str = ""
        context_texts = []
        for r in context_results:
            text_repr = f"[{r.chunk.source_title} - {r.chunk.section}]\n{r.chunk.content}"
            context_texts.append(text_repr)
            context_str += f"{text_repr}\n\n"

        # 2. Composizione Prompt con Grounding
        prompt = RAG_PROMPT_TEMPLATE.format(
            context=context_str if context_str else "Nessun manuale specifico trovato.",
            query=query,
            code_snippet=code_snippet,
        )

        # 3. Generazione iniziale LLM
        raw_output = self.llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT_C64_EXPERT)
        generated_code = self.extract_assembly_code(raw_output)

        # 4. Validazione Deterministica Iniziale
        report = self.analyze_and_validate(generated_code)

        auto_fix_applied = False
        fix_iterations = 0
        fix_history: list[str] = []

        # 5. Ciclo di Auto-Correzione (Self-Healing Guardrails)
        while not report.is_valid and auto_fix and fix_iterations < max_fix_attempts:
            fix_iterations += 1
            auto_fix_applied = True

            # Formattazione degli errori riscontrati dal validatore
            error_descriptions = []
            for issue in report.issues:
                error_descriptions.append(
                    f"- Riga {issue.line_number} [{issue.severity} {issue.code}]: {issue.message}\n  Suggerimento: {issue.suggestion}"
                )
            error_list_str = "\n".join(error_descriptions)
            fix_history.append(f"Tentativo #{fix_iterations}: rilevati {report.errors_count} errori bloccanti.")

            fix_prompt = AUTO_FIX_PROMPT_TEMPLATE.format(
                faulty_code=generated_code,
                error_list=error_list_str,
            )

            # Re-interrogazione del modello con i guardrails deterministici
            corrected_output = self.llm_client.generate(fix_prompt, system_prompt=SYSTEM_PROMPT_C64_EXPERT)
            new_code = self.extract_assembly_code(corrected_output)

            # Re-validazione del nuovo codice
            new_report = self.analyze_and_validate(new_code)

            # Se il nuovo codice ha meno errori o è valido, lo adottiamo
            if new_report.errors_count <= report.errors_count:
                generated_code = new_code
                report = new_report
                raw_output = corrected_output

            if report.is_valid:
                fix_history.append(f"Auto-correzione completata con successo al tentativo #{fix_iterations}.")
                break

        # Separazione spiegazione dal codice se presente
        clean_explanation = re.sub(r"```(?:assembly|asm)?\n.*?```", "", raw_output, flags=re.DOTALL).strip()
        if not clean_explanation:
            clean_explanation = "Codice generato e validato rispetto all'hardware MOS 6502 NMOS del Commodore 64."

        return AssistantResponse(
            query=query,
            explanation=clean_explanation,
            suggested_code=generated_code,
            raw_llm_output=raw_output,
            hardware_context=context_texts,
            validation_report=report,
            auto_fix_applied=auto_fix_applied,
            fix_iterations=fix_iterations,
            fix_history=fix_history,
        )
