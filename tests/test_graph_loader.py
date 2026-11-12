from src.graph.loader import document_checksum


def test_document_checksum_is_stable():
    record = {"id": "movie:1", "title": "GraphRAG"}
    assert document_checksum(record) == document_checksum({"title": "GraphRAG", "id": "movie:1"})
