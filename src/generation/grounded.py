"""Geração grounded estruturada para a demonstração acadêmica."""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

from src.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Você responde perguntas sobre um catálogo de filmes e séries usando SOMENTE as evidências "
    "fornecidas, recuperadas de um grafo de conhecimento. Responda em português, de forma direta. "
    "Cite os IDs dos documentos usados entre colchetes, ex.: [movie:matrix]. Se as evidências não "
    "bastarem para responder, diga isso explicitamente em vez de inventar."
)


def llm_answer(question: str, evidence: list[dict[str, Any]]) -> str | None:
    """Gera a resposta com um LLM local (Ollama); retorna None se ele não estiver disponível."""
    if not evidence:
        return None
    context = "\n\n".join(
        f"[{item.get('document_id')}] {item.get('title', '')}\n{item.get('text', '')}\n"
        f"Caminho no grafo: {item.get('path') or '—'}"
        for item in evidence
    )
    payload = {
        "model": settings.llm_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"<evidencias>\n{context}\n</evidencias>\n\nPergunta: {question}",
            },
        ],
    }
    request = urllib.request.Request(
        f"{settings.ollama_url}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            text = json.load(response)["message"]["content"].strip()
    except (OSError, KeyError, ValueError) as error:
        logger.warning("LLM indisponível em %s, usando template: %s", settings.ollama_url, error)
        return None
    return text or None


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
    generated = llm_answer(question, evidence)
    answer = generated or (
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
        "llm": generated is not None,
        "paths": [item.get("path", {}) for item in evidence if item.get("path")],
    }
