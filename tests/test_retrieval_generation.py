from src.generation.grounded import grounded_answer
from src.retrieval.embeddings import embed_text


def test_embedding_has_expected_dimension_and_norm():
    vector = embed_text("GraphRAG knowledge graph")
    assert len(vector) == 384
    assert any(value != 0 for value in vector)


def test_grounded_answer_requires_evidence():
    assert grounded_answer("question", [])["grounded"] is False
    assert grounded_answer("question", [{"document_id": "doc:1", "title": "Paper"}])["grounded"] is True


def test_grounded_answer_falls_back_to_template_when_llm_is_down(monkeypatch):
    from dataclasses import replace

    from src.generation import grounded

    monkeypatch.setattr(grounded, "settings", replace(grounded.settings, ollama_url="http://127.0.0.1:9"))
    result = grounded_answer("question", [{"document_id": "doc:1", "title": "Paper"}])
    assert result["llm"] is False
    assert "1 documento" in result["answer"]
