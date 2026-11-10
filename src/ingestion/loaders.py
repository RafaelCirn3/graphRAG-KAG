"""Loaders locais para fontes acadêmicas normalizadas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


def load_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    """Lê registros JSONL sem alterar o conteúdo original."""
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"Linha {number} precisa conter um objeto JSON")
        yield value


def normalize_publication(record: dict[str, Any], source: str = "unknown") -> dict[str, Any]:
    """Converte campos comuns de OpenAlex/DBLP/arXiv para o formato do projeto."""
    title = record.get("title") or record.get("display_name") or record.get("name")
    if not title:
        raise ValueError("Publicação sem título")
    authors = record.get("authors") or record.get("authorships") or []
    normalized_authors = []
    for author in authors:
        if isinstance(author, str):
            normalized_authors.append({"id": author, "name": author})
        else:
            nested = author.get("author", {}) if isinstance(author, dict) else {}
            normalized_authors.append({
                "id": author.get("id") or nested.get("id") or author.get("name"),
                "name": author.get("name") or nested.get("display_name") or nested.get("name"),
            })
    abstract = record.get("abstract") or record.get("summary") or record.get("description") or ""
    if not abstract and isinstance(record.get("abstract_inverted_index"), dict):
        positions = [(position, word) for word, indexes in record["abstract_inverted_index"].items() for position in indexes]
        abstract = " ".join(word for _, word in sorted(positions))
    return {
        "id": str(record.get("id") or record.get("doi") or record.get("url") or title),
        "title": str(title).strip(),
        "abstract": str(abstract).strip(),
        "year": record.get("year") or record.get("publication_year"),
        "source": source,
        "uri": record.get("uri") or record.get("url") or record.get("doi"),
        "authors": [a for a in normalized_authors if a.get("id") and a.get("name")],
        "venue": record.get("venue") or record.get("container_name") or record.get("journal"),
        "topics": record.get("topics") or record.get("concepts") or [],
    }
