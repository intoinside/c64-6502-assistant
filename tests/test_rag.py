"""Test completi per il modulo RAG (C64ManualLoader, DocumentChunk, C64KnowledgeRetriever)."""

from c64_assistant.rag.loader import C64ManualLoader
from c64_assistant.rag.retriever import C64KnowledgeRetriever


def test_manual_loader_chunking_and_metadata():
    loader = C64ManualLoader(data_dir="data/manuals")
    chunks = loader.load_all()

    # Devono esserci almeno 10 sezioni estratte dai manuali curati
    assert len(chunks) >= 10

    # Verifica presenza dei chip estratti
    all_chips = {chip for c in chunks for chip in c.chips}
    assert "VIC-II" in all_chips
    assert "SID" in all_chips
    assert "KERNAL" in all_chips
    assert "ZERO_PAGE" in all_chips

    # Verifica presenza di indirizzi esadecimali estratti
    all_addresses = {addr for c in chunks for addr in c.memory_addresses}
    assert "$D020" in all_addresses
    assert "$D012" in all_addresses
    assert "$D400" in all_addresses
    assert "$FFD2" in all_addresses

    # Verifica che almeno un chunk contenga snippet di codice
    chunks_with_code = [c for c in chunks if len(c.code_snippets) > 0]
    assert len(chunks_with_code) > 0


def test_retriever_exact_address_lookup():
    loader = C64ManualLoader(data_dir="data/manuals")
    retriever = C64KnowledgeRetriever(loader=loader)

    # 1. Lookup per registro bordo VIC-II $D020
    vic_results = retriever.find_by_address("$D020")
    assert len(vic_results) > 0
    assert any("$D020" in r.chunk.memory_addresses for r in vic_results)
    assert vic_results[0].score == 1.0

    # 2. Lookup per registro base SID $D400 (senza dollaro)
    sid_results = retriever.find_by_address("D400")
    assert len(sid_results) > 0
    assert any("SID" in r.chunk.chips for r in sid_results)

    # 3. Lookup per routine Kernal CHROUT $FFD2
    kernal_results = retriever.find_by_address("$FFD2")
    assert len(kernal_results) > 0
    assert any("FFD2" in r.chunk.section for r in kernal_results)

    # 4. Lookup per Zero Page $01 (test variante a 4 cifre $0001)
    zp_results = retriever.find_by_address("$01")
    assert len(zp_results) > 0


def test_retriever_chip_filtering():
    loader = C64ManualLoader(data_dir="data/manuals")
    retriever = C64KnowledgeRetriever(loader=loader)

    sid_chunks = retriever.find_by_chip("SID")
    assert len(sid_chunks) > 0
    for res in sid_chunks:
        assert "SID" in res.chunk.chips


def test_retriever_hybrid_query():
    loader = C64ManualLoader(data_dir="data/manuals")
    retriever = C64KnowledgeRetriever(loader=loader)

    # Query con termine raster e timing
    results_raster = retriever.query("come gestire il raster interrupt con $D012")
    assert len(results_raster) > 0
    top = results_raster[0]
    assert "VIC-II" in top.chunk.chips or "$D012" in top.chunk.memory_addresses

    # Query musicale
    results_music = retriever.query("impostare inviluppo adsr e volume su SID")
    assert len(results_music) > 0
    assert any("SID" in r.chunk.chips for r in results_music)
