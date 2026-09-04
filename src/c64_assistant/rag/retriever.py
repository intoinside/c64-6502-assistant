"""Motore di ricerca semantico, indicizzazione hardware e retrieval contestuale C64."""

import math
import re
from typing import Any
from .loader import C64ManualLoader, DocumentChunk


class SearchResult:
    def __init__(self, chunk: DocumentChunk, score: float, match_reason: str):
        self.chunk = chunk
        self.score = score
        self.match_reason = match_reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_title": self.chunk.source_title,
            "section": self.chunk.section,
            "score": round(self.score, 3),
            "match_reason": self.match_reason,
            "chips": self.chunk.chips,
            "memory_addresses": self.chunk.memory_addresses,
            "content": self.chunk.content,
            "code_snippets": self.chunk.code_snippets,
        }


class C64KnowledgeRetriever:
    """Sistema di recupero per la conoscenza tecnica del Commodore 64.

    Combina lookup deterministico per indirizzi di memoria e chip con un
    algoritmo di ranking semantico/TF-IDF locale senza dipendenze cloud obbligatorie,
    con supporto pluggable per ChromaDB se presente.
    """

    def __init__(self, loader: C64ManualLoader | None = None, use_vector_db: bool = False):
        self.loader = loader or C64ManualLoader()
        self.chunks: list[DocumentChunk] = []
        self.address_index: dict[str, list[DocumentChunk]] = {}
        self.chip_index: dict[str, list[DocumentChunk]] = {}
        self.use_vector_db = use_vector_db
        self.chroma_collection = None

        self._build_index()
        if self.use_vector_db:
            self._init_chroma_db()

    def _build_index(self) -> None:
        """Costruisce gli indici veloci in memoria."""
        self.chunks = self.loader.load_all()
        self.address_index.clear()
        self.chip_index.clear()

        for chunk in self.chunks:
            # 1. Indice per indirizzo
            for addr in chunk.memory_addresses:
                clean_addr = addr.upper().replace("$", "")
                self.address_index.setdefault(clean_addr, []).append(chunk)

            # 2. Indice per Chip
            for chip in chunk.chips:
                self.chip_index.setdefault(chip.upper(), []).append(chunk)

    def _init_chroma_db(self) -> None:
        """Inizializza il database vettoriale locale ChromaDB se la libreria è installata."""
        try:
            import chromadb
            client = chromadb.Client()
            self.chroma_collection = client.get_or_create_collection(name="c64_manuals")

            # Popola la collection
            ids = [f"chunk_{i}" for i in range(len(self.chunks))]
            docs = [f"{c.source_title} - {c.section}\n{c.content}" for c in self.chunks]
            metadatas = [
                {
                    "source": c.source_title,
                    "section": c.section,
                    "chips": ",".join(c.chips),
                    "addresses": ",".join(c.memory_addresses),
                }
                for c in self.chunks
            ]
            self.chroma_collection.add(ids=ids, documents=docs, metadatas=metadatas)
        except Exception:
            # Fallback trasparente sul motore integrato
            self.chroma_collection = None

    def find_by_address(self, address_hex: str) -> list[SearchResult]:
        """Lookup deterministico immediato per registro o locazione di memoria (es. '$D020' o '01')."""
        clean = address_hex.strip().upper().replace("$", "").replace("0X", "")
        results: list[SearchResult] = []

        # Corrispondenza esatta
        direct_matches = self.address_index.get(clean, [])
        for chunk in direct_matches:
            results.append(SearchResult(chunk, score=1.0, match_reason=f"Indirizzo esatto ${clean}"))

        # Se indirizzo a 2 cifre (es. '01'), prova anche variante a 4 cifre ('0001') e viceversa
        if len(clean) == 2 and not direct_matches:
            padded = f"00{clean}"
            for chunk in self.address_index.get(padded, []):
                results.append(SearchResult(chunk, score=0.9, match_reason=f"Indirizzo ${clean} (${padded})"))
        elif len(clean) == 4 and clean.startswith("00") and not direct_matches:
            short = clean[2:]
            for chunk in self.address_index.get(short, []):
                results.append(SearchResult(chunk, score=0.9, match_reason=f"Indirizzo ${clean} (${short})"))

        return results

    def find_by_chip(self, chip_name: str) -> list[SearchResult]:
        """Recupera tutti i frammenti di manuale relativi a un sottosistema o chip."""
        c_clean = chip_name.strip().upper()
        chunks = self.chip_index.get(c_clean, [])
        return [SearchResult(c, score=0.8, match_reason=f"Filtro hardware: {chip_name}") for c in chunks]

    def query(self, query_text: str, max_results: int = 4) -> list[SearchResult]:
        """Ricerca ibrida: individua indirizzi esadecimali nella query e applica TF-IDF sui termini."""
        results: list[SearchResult] = []
        seen_sections: set[str] = set()

        # 1. Controlla se la query include indirizzi esadecimali espliciti (es. $D020 o $D404)
        hex_matches = re.findall(r"\$([0-9a-fA-F]{2,4})\b", query_text)
        for hex_addr in hex_matches:
            addr_results = self.find_by_address(hex_addr)
            for res in addr_results:
                key = f"{res.chunk.source_title}_{res.chunk.section}"
                if key not in seen_sections:
                    seen_sections.add(key)
                    results.append(res)

        # 2. Ranking semantico e per parole chiave
        tokens = re.findall(r"\b[a-zA-Z0-9_\$]{2,}\b", query_text.lower())
        if not tokens:
            return results[:max_results]

        scored: list[tuple[float, str, DocumentChunk]] = []

        for chunk in self.chunks:
            key = f"{chunk.source_title}_{chunk.section}"
            if key in seen_sections:
                continue

            section_lower = chunk.section.lower()
            title_lower = chunk.source_title.lower()
            content_lower = chunk.content.lower()

            score = 0.0
            reasons = []

            for token in tokens:
                # Corrispondenza esatta nel titolo della sezione (alto peso)
                if token in section_lower:
                    score += 3.0
                    reasons.append(f"Match sezione '{token}'")
                # Corrispondenza nei chip o tag
                elif any(token == c.lower() for c in chunk.chips) or any(token == t.lower() for t in chunk.tags):
                    score += 2.5
                    reasons.append(f"Match chip/tag '{token}'")
                # Corrispondenza nel titolo del manuale
                elif token in title_lower:
                    score += 1.5
                # Corrispondenza nel corpo del testo
                else:
                    count = content_lower.count(token)
                    if count > 0:
                        # Log-frequency weighting
                        score += 0.5 + (0.3 * math.log(count + 1))
                        reasons.append(f"Occorrenze '{token}' ({count})")

            if score > 0:
                reason_str = ", ".join(reasons[:2]) if reasons else "Corrispondenza semantica"
                scored.append((score, reason_str, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        for score, reason, chunk in scored:
            results.append(SearchResult(chunk, score=round(score, 2), match_reason=reason))
            if len(results) >= max_results:
                break

        return results[:max_results]
