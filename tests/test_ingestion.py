from src.ingestion.chunker import chunk_document
from src.ingestion.loaders import load_json, normalize_title
from src.ingestion.parser import parse_title


def test_title_pipeline_from_json():
    record = load_json("data/raw/titles.json")[0]
    item = normalize_title(record, source="local")
    document = parse_title(item)
    chunks = chunk_document(document, max_chars=50, overlap=5)
    assert document.document_id == "movie:the-matrix"
    assert "Keanu Reeves" in document.text
    assert chunks and all(chunk.document_id == document.document_id for chunk in chunks)
