"""Caricamento e chunking di manuali tecnici C64 (Mapping the C64, VIC-II, SID)."""

from pathlib import Path
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    source_title: str
    section: str
    content: str
    memory_addresses: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class C64ManualLoader:
    """Loader locale per testi tecnici e reference sheet di Commodore 64 e 6502."""

    def __init__(self, data_dir: Path | str = "data/manuals"):
        self.data_dir = Path(data_dir)

    def load_markdown_file(self, file_path: Path | str) -> list[DocumentChunk]:
        """Esegue il chunking semantico di un file markdown basandosi sui titoli # e ##."""
        path = Path(file_path)
        if not path.exists():
            return []

        chunks: list[DocumentChunk] = []
        current_title = path.stem
        current_section = "Introduzione"
        current_buffer: list[str] = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    if current_buffer:
                        chunks.append(
                            DocumentChunk(
                                source_title=current_title,
                                section=current_section,
                                content="\n".join(current_buffer).strip(),
                            )
                        )
                        current_buffer = []
                    current_section = line.strip("# \n")
                else:
                    current_buffer.append(line)

        if current_buffer:
            chunks.append(
                DocumentChunk(
                    source_title=current_title,
                    section=current_section,
                    content="\n".join(current_buffer).strip(),
                )
            )

        return chunks

    def load_all(self) -> list[DocumentChunk]:
        """Carica tutti i manuali .md e .txt presenti nella cartella data/manuals."""
        if not self.data_dir.exists():
            return []

        all_chunks: list[DocumentChunk] = []
        for file in self.data_dir.glob("*.md"):
            all_chunks.extend(self.load_markdown_file(file))
        return all_chunks
