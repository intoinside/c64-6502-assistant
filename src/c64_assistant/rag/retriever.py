"""Ricerca semantica e lookup dei contesti hardware per C64 e 6502."""

import re
from .loader import C64ManualLoader, DocumentChunk


class C64KnowledgeRetriever:
    """Sistema di recupero documentazione tecnica (supporta fallback su memory address e keyword)."""

    def __init__(self, loader: C64ManualLoader | None = None):
        self.loader = loader or C64ManualLoader()
        self.chunks: list[DocumentChunk] = []
        self._load_initial_knowledge()

    def _load_initial_knowledge(self) -> None:
        self.chunks = self.loader.load_all()

    def find_by_address(self, address_hex: str) -> list[DocumentChunk]:
        """Cerca sezioni di manuali che descrivono un indirizzo esadecimale (es. 'D020')."""
        addr_clean = address_hex.strip("$").upper()
        results = []
        pattern = re.compile(rf"\b(?:\$)?{addr_clean}\b", re.IGNORECASE)

        for chunk in self.chunks:
            if pattern.search(chunk.content) or pattern.search(chunk.section):
                results.append(chunk)

        return results

    def query(self, text_query: str, max_results: int = 3) -> list[DocumentChunk]:
        """Ricerca contestuale sui frammenti di testo dei manuali."""
        keywords = set(re.findall(r"\w+", text_query.lower()))
        if not keywords:
            return []

        scored_chunks: list[tuple[int, DocumentChunk]] = []
        for chunk in self.chunks:
            chunk_text = f"{chunk.section} {chunk.content}".lower()
            score = sum(1 for kw in keywords if kw in chunk_text)
            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:max_results]]
