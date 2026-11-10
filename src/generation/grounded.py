"""Geração grounded estruturada para a demonstração acadêmica."""

from __future__ import annotations

from typing import Any


def grounded_answer(question: str, evidence: list[dict[str, Any]], cypher: str = "") -> dict[str, Any]:
    titles = [item.get("title") for item in evidence if item.get("title")]
    sources = [item.get("document_id") for item in evidence if item.get("document_id")]
    confidence = min(0.95, 0.45 + (0.1 * len(set(sources)))) if evidence else 0.0
    answer = (
        f"A consulta foi respondida com base em {len(set(sources))} documento(s) recuperado(s). "
        f"A pergunta analisada foi: {question}"
    )
    return {
        "answer": answer,
        "confidence": round(confidence, 2),
        "sources": sorted(set(sources)),
        "evidence_titles": sorted(set(titles)),
        "cypher": cypher,
        "grounded": bool(evidence),
    }
