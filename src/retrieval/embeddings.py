"""Embeddings determinísticos locais para a demonstração acadêmica.

Não substituem um modelo semântico de produção; permitem validar o índice vector
sem exigir credenciais externas ou downloads pesados.
"""

from __future__ import annotations

import hashlib
import math
import re


EMBEDDING_DIMENSION = 384


def embed_text(text: str, dimension: int = EMBEDDING_DIMENSION) -> list[float]:
    tokens = re.findall(r"[\wÀ-ÿ]+", text.lower())
    vector = [0.0] * dimension
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector
