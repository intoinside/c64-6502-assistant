"""Caricatore e parser semantico per manuali e testi tecnici del Commodore 64."""

import re
from pathlib import Path
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    source_title: str
    section: str
    content: str
    memory_addresses: list[str] = Field(default_factory=list, description="Indirizzi esadecimali $xxxx citati")
    chips: list[str] = Field(default_factory=list, description="Chip hardware di riferimento (VIC-II, SID, CIA, ecc.)")
    tags: list[str] = Field(default_factory=list, description="Tag e argomenti tecnici")
    code_snippets: list[str] = Field(default_factory=list, description="Snippet di codice assembly inclusi")


class C64ManualLoader:
    """Caricatore intelligente e chunker semantico con estrazione automatica di metadati hardware."""

    def __init__(self, data_dir: Path | str = "data/manuals"):
        self.data_dir = Path(data_dir)

    @classmethod
    def extract_addresses(cls, text: str) -> list[str]:
        """Estrae tutti gli indirizzi esadecimali nel formato $nn o $nnnn."""
        raw_matches = re.findall(r"\$([0-9a-fA-F]{2,4})\b", text)
        normalized = []
        for m in raw_matches:
            # Normalizza in maiuscolo con prefisso $
            normalized.append(f"${m.upper()}")
        return list(dict.fromkeys(normalized))  # rimozione duplicati preservando l'ordine

    @classmethod
    def detect_chips_and_tags(cls, text: str, section: str) -> tuple[list[str], list[str]]:
        """Identifica i chip e i tag tematici associati al frammento di testo."""
        combined = f"{section} {text}".lower()
        chips = []
        tags = []

        # Rilevamento Chip
        if any(k in combined for k in ["vic-ii", "vic2", "6569", "6567", "$d0", "raster", "sprite", "bordo"]):
            chips.append("VIC-II")
        if any(k in combined for k in ["sid", "6581", "8580", "$d4", "voce", "adsr", "filtro", "waveform"]):
            chips.append("SID")
        if any(k in combined for k in ["cia 1", "cia 2", "cia1", "cia2", "6526", "$dc", "$dd"]):
            chips.append("CIA")
        if any(k in combined for k in ["kernal", "$ff", "chrout", "getin", "bsout", "jump table"]):
            chips.append("KERNAL")
        if any(k in combined for k in ["zero page", "$0000", "$0001", "banking", "puntator"]):
            chips.append("ZERO_PAGE")
        if any(k in combined for k in ["6502", "6510", "cpu", "stack", "flag", "accumulatore"]):
            chips.append("CPU_6502")

        # Rilevamento Tag
        if "raster" in combined:
            tags.append("raster_timing")
        if "sprite" in combined:
            tags.append("sprites")
        if "interrupt" in combined or "irq" in combined:
            tags.append("interrupts")
        if "banking" in combined or "$0001" in combined:
            tags.append("memory_banking")
        if "bad line" in combined:
            tags.append("bad_lines")

        return chips, tags

    @classmethod
    def extract_code_snippets(cls, text: str) -> list[str]:
        """Estrae blocchi di codice assembly markdown racchiusi tra triple backtick."""
        snippets = re.findall(r"```(?:assembly|asm)?\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        return [s.strip() for s in snippets if s.strip()]

    def load_markdown_file(self, file_path: Path | str) -> list[DocumentChunk]:
        """Esegue il chunking semantico di un manuale basandosi sulle intestazioni markdown."""
        path = Path(file_path)
        if not path.exists():
            return []

        chunks: list[DocumentChunk] = []
        current_title = path.stem.replace("_", " ").title()
        current_section = "Panoramica Generale"
        current_buffer: list[str] = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("## ") or line.startswith("### "):
                    if current_buffer:
                        content_text = "\n".join(current_buffer).strip()
                        addresses = self.extract_addresses(f"{current_section} {content_text}")
                        chips, tags = self.detect_chips_and_tags(content_text, current_section)
                        snippets = self.extract_code_snippets(content_text)

                        chunks.append(
                            DocumentChunk(
                                source_title=current_title,
                                section=current_section,
                                content=content_text,
                                memory_addresses=addresses,
                                chips=chips,
                                tags=tags,
                                code_snippets=snippets,
                            )
                        )
                        current_buffer = []
                    current_section = line.strip("# \n")
                elif line.startswith("# "):
                    current_title = line.strip("# \n")
                else:
                    current_buffer.append(line)

        if current_buffer:
            content_text = "\n".join(current_buffer).strip()
            addresses = self.extract_addresses(f"{current_section} {content_text}")
            chips, tags = self.detect_chips_and_tags(content_text, current_section)
            snippets = self.extract_code_snippets(content_text)

            chunks.append(
                DocumentChunk(
                    source_title=current_title,
                    section=current_section,
                    content=content_text,
                    memory_addresses=addresses,
                    chips=chips,
                    tags=tags,
                    code_snippets=snippets,
                )
            )

        return chunks

    def load_all(self) -> list[DocumentChunk]:
        """Carica e indicizza tutti i manuali .md presenti nella cartella dei manuali."""
        if not self.data_dir.exists():
            return []

        all_chunks: list[DocumentChunk] = []
        for file in sorted(self.data_dir.glob("*.md")):
            if file.name.lower() == "readme.md":
                continue
            all_chunks.extend(self.load_markdown_file(file))
        return all_chunks
