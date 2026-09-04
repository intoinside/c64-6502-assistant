"""Test per il modulo RAG (Loader e Retriever)."""

from c64_assistant.rag.loader import C64ManualLoader
from c64_assistant.rag.retriever import C64KnowledgeRetriever


def test_manual_loader_and_retriever():
    loader = C64ManualLoader(data_dir="data/manuals")
    chunks = loader.load_all()
    assert len(chunks) > 0

    retriever = C64KnowledgeRetriever(loader=loader)

    # Verifica ricerca per registro VIC-II $D020
    vic_results = retriever.find_by_address("D020")
    assert len(vic_results) > 0
    assert any("D020" in c.content for c in vic_results)

    # Verifica ricerca semantica / per parole chiave
    query_results = retriever.query("raster timing pal cicli")
    assert len(query_results) > 0
