"""Loader do catálogo local de filmes e séries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TITLE_TYPES = {"movie", "series"}


def load_json(path: str | Path) -> list[dict[str, Any]]:
    """Lê um arquivo JSON cujo conteúdo é uma lista de títulos."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{path} precisa conter uma lista de objetos JSON")
    return value


def normalize_title(record: dict[str, Any], source: str = "local") -> dict[str, Any]:
    """Valida um filme/série e devolve o formato usado pelo pipeline."""
    title = str(record.get("title") or "").strip()
    if not title:
        raise ValueError("Título sem nome")
    kind = str(record.get("type") or "").lower()
    if kind not in TITLE_TYPES:
        raise ValueError(f"{title}: 'type' precisa ser 'movie' ou 'series'")
    return {
        "id": str(record.get("id") or f"{kind}:{title}"),
        "type": kind,
        "title": title,
        "year": record.get("year"),
        "synopsis": str(record.get("synopsis") or "").strip(),
        "creators": [str(name).strip() for name in record.get("creators", []) if str(name).strip()],
        "cast": [str(name).strip() for name in record.get("cast", []) if str(name).strip()],
        "genres": [str(name).strip() for name in record.get("genres", []) if str(name).strip()],
        "studio": str(record.get("studio") or "").strip() or None,
        "uri": record.get("uri"),
        "source": source,
    }
