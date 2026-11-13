"""Baseline de comparação: o mesmo LLM respondendo SEM nenhuma evidência recuperada."""

from __future__ import annotations

import json
import logging
import urllib.request

from src.config import settings

logger = logging.getLogger(__name__)

# Prompt deliberadamente neutro: não pede para citar fontes nem para abster-se. É o uso
# típico de um LLM puro, e é o que o GraphRAG precisa superar.
SYSTEM_PROMPT = "Você responde perguntas sobre filmes e séries em português, de forma direta. Se faltar informação sobre o catálogo, diga explicitamente."


def no_retrieval_answer(question: str, model: str | None = None) -> str | None:
    """Resposta do LLM local (Ollama) sem contexto; None se o serviço estiver indisponível."""
    payload = {
        "model": model or settings.llm_model,
        "stream": False, "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
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
        logger.warning("LLM indisponível em %s: %s", settings.ollama_url, error)
        return None
    return text or None
