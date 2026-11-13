"""Métricas automáticas de correção e alucinação para o experimento GraphRAG vs. LLM puro.

Definição operacional usada no artigo:
- *Alucinação* = a resposta afirma algo que a base de conhecimento (o catálogo) não sustenta:
  (a) cita uma entidade (nome próprio) que não existe no catálogo nem na pergunta; ou
  (b) responde com confiança uma pergunta cuja resposta não está no catálogo.
- Isso mede fidelidade à base, não verdade no mundo real. Uma resposta pode ser verdadeira fora
  do catálogo e ainda assim contar como alucinação aqui. A avaliação humana complementa a métrica.

Limitação conhecida: a detecção de entidades é heurística (nomes próprios com inicial maiúscula).
Palavra única no início de frase é ignorada para evitar falsos positivos ("Segundo...", "Nenhuma...").
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from statistics import mean
from typing import Any, Iterable

_LINK = {"de", "da", "do", "dos", "das", "bo", "of", "the", "and", "von", "van", "e"}
_CAP = r"[A-ZÀ-Ý][A-Za-zÀ-ÿ0-9'’\-]*"
_SPAN = re.compile(rf"{_CAP}(?:\s+(?:(?:de|da|do|dos|das|bo|of|the|and|von|van)\s+)?{_CAP})*")

_ABSTAIN = (
    "nao ha evidencia", "nao ha evidencias", "evidencias nao bastam", "evidencias insuficientes",
    "evidencia insuficiente", "informacao insuficiente", "nao encontrei", "nao consta",
    "nao ha informac", "nao ha registro", "nao tenho informac", "nao possuo informac",
    "nao esta no catalogo", "nao estao no catalogo", "nao existe no catalogo",
    "nao foi possivel", "nao e possivel responder", "nao foram encontrad", "nao foi encontrad",
    "nenhuma evidencia", "nao ha filmes", "nao ha series", "nao ha nenhum", "nao ha titulos",
)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


@dataclass(frozen=True)
class Catalog:
    """Vocabulário (tokens normalizados) de tudo que o catálogo sustenta."""

    tokens: frozenset[str]

    @classmethod
    def from_titles(cls, titles: list[dict[str, Any]]) -> "Catalog":
        tokens: set[str] = set()
        for t in titles:
            fields = [t["title"], t.get("studio", ""), t.get("synopsis", ""),
                      *t.get("creators", []), *t.get("cast", []), *t.get("genres", [])]
            for value in fields:
                tokens.update(normalize(value).split())
        return cls(frozenset(tokens))


def abstained(answer: str) -> bool:
    text = normalize(answer)
    return any(pattern in text for pattern in _ABSTAIN)


def unsupported_entities(answer: str, question: str, catalog: Catalog) -> list[str]:
    """Nomes próprios da resposta que não aparecem no catálogo nem na pergunta."""
    text = re.sub(r"\[[^\]]*\]", " ", answer).replace("*", "").replace("_", " ")
    allowed = catalog.tokens | set(normalize(question).split()) | _LINK
    found: list[str] = []
    for match in _SPAN.finditer(text):
        tokens = match.group(0).split()
        prefix = text[: match.start()].rstrip(" \t\"'“”«(")
        if not prefix or prefix[-1] in ".!?:;\n•-–—":
            tokens = tokens[1:]  # primeira palavra de frase é maiúscula por gramática
        while tokens and normalize(tokens[0]) in _LINK:
            tokens = tokens[1:]
        if not tokens:
            continue
        if any(word not in allowed for token in tokens for word in normalize(token).split()):
            found.append(" ".join(tokens))
    return list(dict.fromkeys(found))


def _contains(answer_norm: str, gold: str) -> bool:
    return f" {normalize(gold)} " in f" {answer_norm} "


def score_answer(item: dict[str, Any], answer: str, catalog: Catalog) -> dict[str, Any]:
    answer_norm = normalize(answer)
    is_abstention = abstained(answer)
    unsupported = unsupported_entities(answer, item["question"], catalog)
    gold = item.get("gold_entities", [])
    found = [g for g in gold if _contains(answer_norm, g)]
    recall = len(found) / len(gold) if gold else None
    if item["answerable"]:
        correct = recall == 1.0 and not is_abstention
        hallucinated = bool(unsupported)
    else:
        correct = is_abstention and not unsupported
        hallucinated = (not is_abstention) or bool(unsupported)
    return {
        "correct": correct,
        "hallucinated": hallucinated,
        "abstained": is_abstention,
        "recall": recall,
        "missing_entities": [g for g in gold if g not in found],
        "unsupported_entities": unsupported,
    }


def _rate(values: Iterable[bool]) -> float | None:
    values = list(values)
    return round(sum(values) / len(values), 4) if values else None


def aggregate(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """rows: dicts com variant, category, answerable, correct, hallucinated, recall."""
    summary: dict[str, dict[str, dict[str, Any]]] = {}
    for variant in sorted({r["variant"] for r in rows}):
        mine = [r for r in rows if r["variant"] == variant]
        groups = {"geral": mine}
        for category in sorted({r["category"] for r in mine}):
            groups[category] = [r for r in mine if r["category"] == category]
        summary[variant] = {}
        for name, rs in groups.items():
            answerable = [r for r in rs if r["answerable"]]
            blocked = [r for r in rs if not r["answerable"]]
            recalls = [r["recall"] for r in answerable if r["recall"] is not None]
            summary[variant][name] = {
                "n": len(rs),
                "acerto": _rate(r["correct"] for r in rs),
                "recall_medio": round(mean(recalls), 4) if recalls else None,
                "alucinacao": _rate(r["hallucinated"] for r in rs),
                "abstencao_correta": _rate(r["correct"] for r in blocked),
            }
    return summary


def format_table(summary: dict[str, dict[str, dict[str, Any]]], group: str = "geral") -> str:
    def cell(value: float | None) -> str:
        return "—" if value is None else f"{value:.0%}"

    lines = ["| Variante | n | Acerto | Recall médio | Alucinação | Abstenção correta |",
             "|---|---|---|---|---|---|"]
    for variant, groups in summary.items():
        g = groups.get(group)
        if g:
            lines.append(f"| {variant} | {g['n']} | {cell(g['acerto'])} | {cell(g['recall_medio'])} | "
                         f"{cell(g['alucinacao'])} | {cell(g['abstencao_correta'])} |")
    return "\n".join(lines)
