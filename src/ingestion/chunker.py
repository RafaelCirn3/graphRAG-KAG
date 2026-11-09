"""Chunking determinístico para a etapa inicial de ingestão."""

from dataclasses import dataclass

from src.ingestion.parser import ParsedDocument


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    position: int


def chunk_document(document: ParsedDocument, max_chars: int = 800, overlap: int = 100) -> list[Chunk]:
    if max_chars <= 0 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Use max_chars > 0 e 0 <= overlap < max_chars")
    text = " ".join(document.text.split())
    chunks: list[Chunk] = []
    start = 0
    position = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(f"{document.document_id}:chunk:{position}", document.document_id, piece, position))
        if end >= len(text):
            break
        start = end - overlap
        position += 1
    return chunks
