"""NER/RE leve e reproduzível para os chunks da demonstração acadêmica."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.extraction.entity_resolution import canonical_id


ENTITY_PATTERNS = {
    "Technology": ["GraphRAG", "KAG", "Neo4j", "Python", "OpenAlex", "LLM", "LlamaIndex", "LangChain"],
    "ResearchArea": ["NLP", "Knowledge Graph", "Information Retrieval", "Machine Learning"],
}


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
    mentions: list[Mention] = []
    for entity_type, names in ENTITY_PATTERNS.items():
        for name in names:
            for match in re.finditer(re.escape(name), text, flags=re.IGNORECASE):
                mentions.append(Mention(canonical_id("entity", name), name, entity_type, match.start(), match.end()))
    unique = {(mention.entity_id, mention.start): mention for mention in mentions}
    ordered = sorted(unique.values(), key=lambda item: item.start)
    relations = []
    for left, right in zip(ordered, ordered[1:]):
        if right.start - left.end <= 120:
            relations.append((left.entity_id, right.entity_id, "RELATED_TO", 0.6))
    return ExtractedRelations(ordered, relations)
