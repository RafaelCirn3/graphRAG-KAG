"""Canonicalização simples e reproduzível de entidades acadêmicas."""

from __future__ import annotations

import re
import unicodedata


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    tokens = value.split()
    return "".join(tokens) if len(tokens) > 1 and all(len(token) == 1 for token in tokens) else value


def canonical_id(kind: str, value: str) -> str:
    return f"{kind}:{normalize_name(value).replace(' ', '-')}"


def deduplicate_names(values: list[str]) -> list[str]:
    unique: dict[str, str] = {}
    for value in values:
        key = normalize_name(value)
        if key and key not in unique:
            unique[key] = value.strip()
    return list(unique.values())
