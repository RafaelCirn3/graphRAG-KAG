"""Geração grounded estruturada para a demonstração acadêmica."""

from __future__ import annotations

from typing import Any


def grounded_answer(question: str, evidence: list[dict[str, Any]], cypher: str = "") -> dict[str, Any]:
    titles = [item.get("title") for item in evidence if item.get("title")]
    sources = [item.get("document_id") for item in evidence if item.get("document_id")]
    if evidence:
        scores = [
            0.45 * float(item.get("vector_score") or 0.0)
            + 0.2 * float(item.get("fulltext_score") or 0.0)
            + 0.15 * float(item.get("keyword_score") or 0.0)
            + 0.2 * float(item.get("path_score") or 0.0)
            for item in evidence
        ]
        confidence = min(0.98, max(scores))
    else:
        confidence = 0.0
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
        "paths": [item.get("path", {}) for item in evidence if item.get("path")],
    }
