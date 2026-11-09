from src.ingestion.chunker import chunk_document
from src.ingestion.loaders import load_jsonl, normalize_publication
from src.ingestion.parser import parse_publication


def test_publication_pipeline_from_jsonl():
    record = next(load_jsonl("data/raw/publications.sample.jsonl"))
    publication = normalize_publication(record, source="sample")
    document = parse_publication(publication)
    chunks = chunk_document(document, max_chars=50, overlap=5)
    assert document.document_id == "demo:graphrag"
    assert chunks and all(chunk.document_id == document.document_id for chunk in chunks)
