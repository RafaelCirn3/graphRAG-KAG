from src.generation.grounded import grounded_answer
from src.retrieval.embeddings import embed_text


def test_embedding_has_expected_dimension_and_norm():
    vector = embed_text("GraphRAG knowledge graph")
    assert len(vector) == 384
    assert any(value != 0 for value in vector)


def test_grounded_answer_requires_evidence():
    assert grounded_answer("question", [])["grounded"] is False
    assert grounded_answer("question", [{"document_id": "doc:1", "title": "Paper"}])["grounded"] is True
