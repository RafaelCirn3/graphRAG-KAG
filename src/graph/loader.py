"""Carga idempotente de documentos e chunks no Neo4j."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from neo4j import Driver

from src.ingestion.chunker import chunk_document
from src.ingestion.loaders import normalize_title
from src.ingestion.parser import parse_title


def document_checksum(item: dict[str, Any]) -> str:
    payload = json.dumps(item, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_title(driver: Driver, raw_record: dict[str, Any], source: str = "local") -> int:
    item = normalize_title(raw_record, source=source)
    document = parse_title(item)
    chunks = chunk_document(document)
    metadata = {key: item.get(key) for key in ("source", "type", "year", "creators", "cast", "genres", "studio")}
    document_props = {
        "id": document.document_id,
        "title": document.title,
        "uri": item.get("uri"),
        "checksum": document_checksum(item),
        "source": source,
        "year": item.get("year"),
        "metadata_json": json.dumps(metadata, ensure_ascii=False),
    }
    chunk_props = [
        {"id": c.id, "text": c.text, "position": c.position, "document_id": c.document_id}
        for c in chunks
    ]
    query = """
    MERGE (d:Document {id: $document.id})
    SET d.title = $document.title,
        d.uri = $document.uri,
        d.checksum = $document.checksum,
        d.source = $document.source,
        d.year = $document.year,
        d.metadata_json = $document.metadata_json,
        d.updated_at = datetime()
    WITH d
    UNWIND $chunks AS chunk
    MERGE (c:Chunk {id: chunk.id})
    SET c.text = chunk.text,
        c.position = chunk.position,
        c.document_id = chunk.document_id
    MERGE (d)-[:HAS_CHUNK]->(c)
    RETURN count(c) AS chunks
    """
    with driver.session() as session:
        result = session.run(query, document=document_props, chunks=chunk_props).single()
    return int(result["chunks"]) if result else 0


def load_titles(driver: Driver, records: Iterable[dict[str, Any]], source: str = "local") -> int:
    return sum(load_title(driver, record, source=source) for record in records)
