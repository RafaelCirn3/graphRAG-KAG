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
    relations: list[tuple[str, str, str, str]]


def extract_entities_and_relations(text: str) -> ExtractedRelations:
    from src.model import ask
    fields = {"source": {"type":"string"}, "predicate":{"type":"string"}, "target":{"type":"string"}}
    schema = {"type":"object","required":["relations","entities"],"properties":{
        "relations":{"type":"array","items":{"type":"object","properties":fields,"required":list(fields)}},
        "entities":{"type":"array","items":{"type":"string"}}}}
    data = ask("Leia a sinopse. Extraia triplas sujeito, verbo, objeto, com os tres campos "
               "copiados literalmente na mesma frase e na ordem do texto. Inclua personagens, "
               "grupos, objetos e conceitos. Use o verbo literal em predicate. Em entities liste "
               "as expressoes nominais mencionadas.", text, schema)
    import re
    mentions = {}
    def mention(name):
        match = re.search(re.escape(name), text, re.I) if name.strip() else None
        if match:
            exact = match.group()
            key = canonical_id("entity", exact)
            mentions[key] = Mention(key, exact, "Entity", match.start(), match.end())
            return key
    for name in data["entities"]:
        mention(name)
    relations = []
    for triple in data["relations"]:
        a, verb, b = (triple[key].strip() for key in ("source","predicate","target"))
        if not all((a,verb,b)):
            continue
        pattern = r"[^.!?]*?".join(re.escape(part) for part in (a,verb,b))
        span = re.search(pattern, text, re.I)
        if span:
            relations.append((mention(a),mention(b),verb,span.group()))
    return ExtractedRelations(list(mentions.values()), relations)
