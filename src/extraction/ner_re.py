"""NER/RE leve e reproduzível: detecta temas conhecidos nas sinopses."""

from __future__ import annotations

from dataclasses import dataclass

from src.extraction.entity_resolution import canonical_id


@dataclass(frozen=True)
class Mention:
    entity_id: str
    name: str
    entity_type: str
    start: int
    end: int


@dataclass(frozen=True)
class ExtractedRelations:
    mentions: list[Mention]
    relations: list[tuple[str, str, str, float]]


def extract_entities_and_relations(text: str) -> ExtractedRelations:
    from src.model import ask
    data = ask("Extract entities and explicit semantic relations from Portuguese prose. "
               "Return JSON with entities [{name,type}] and relations [{source,predicate,target,quote}]. "
               "Copy names and supporting quotes exactly from the input. No inferred facts.", text, True)
    mentions = []
    for entity in data["entities"]:
        name = entity["name"].strip()
        if name and name in text:
            start = text.index(name)
            mentions.append(Mention(canonical_id("entity", name), name, entity["type"], start, start+len(name)))
    ids = {m.name:m.entity_id for m in mentions}
    relations = []
    for r in data["relations"]:
        quote = r.get("quote", "")
        if quote and quote in text and all(r[k] in ids and r[k] in quote for k in ("source","target")):
            relations.append((ids[r["source"]],ids[r["target"]],r["predicate"],1.0))
    return ExtractedRelations(mentions, relations)
