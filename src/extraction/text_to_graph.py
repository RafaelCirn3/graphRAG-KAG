"""Transformação determinística de filmes e séries em um grafo tipado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.extraction.entity_resolution import canonical_id, deduplicate_names, normalize_name


ALLOWED_LABELS = {"Movie", "Series", "Person", "Genre", "Studio"}
ALLOWED_RELATIONSHIPS = {"DIRECTED", "CREATED", "ACTED_IN", "HAS_GENRE", "PRODUCED_BY"}


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    properties: dict[str, Any]


@dataclass(frozen=True)
class GraphRelationship:
    source_id: str
    source_label: str
    relationship: str
    target_id: str
    target_label: str
    properties: dict[str, Any]


@dataclass(frozen=True)
class ExtractedGraph:
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]


def _node(identifier: str, label: str, **properties: Any) -> GraphNode:
    return GraphNode(identifier, label, {"id": identifier, **properties})


def extract_title(item: dict[str, Any]) -> ExtractedGraph:
    title_id = str(item["id"])
    title_label = "Movie" if item["type"] == "movie" else "Series"
    creator_relationship = "DIRECTED" if item["type"] == "movie" else "CREATED"
    nodes = [_node(title_id, title_label, title=item["title"], year=item.get("year"))]
    relationships: list[GraphRelationship] = []

    def person(name: str, relationship: str) -> None:
        person_id = canonical_id("person", name)
        nodes.append(_node(person_id, "Person", name=name, canonical_name=normalize_name(name)))
        relationships.append(GraphRelationship(person_id, "Person", relationship, title_id, title_label, {}))

    for name in deduplicate_names(item.get("creators", [])):
        person(name, creator_relationship)
    for name in deduplicate_names(item.get("cast", [])):
        person(name, "ACTED_IN")

    for genre in deduplicate_names(item.get("genres", [])):
        genre_id = canonical_id("genre", genre)
        nodes.append(_node(genre_id, "Genre", name=genre))
        relationships.append(GraphRelationship(title_id, title_label, "HAS_GENRE", genre_id, "Genre", {}))

    studio = item.get("studio")
    if studio:
        studio_id = canonical_id("studio", studio)
        nodes.append(_node(studio_id, "Studio", name=studio))
        relationships.append(GraphRelationship(title_id, title_label, "PRODUCED_BY", studio_id, "Studio", {}))

    return ExtractedGraph(nodes, relationships)


def validate_graph(graph: ExtractedGraph) -> list[str]:
    errors: list[str] = []
    node_keys = {(node.label, node.id) for node in graph.nodes}
    for node in graph.nodes:
        if node.label not in ALLOWED_LABELS:
            errors.append(f"Label não permitido: {node.label}")
        if not node.id or not node.properties.get("id"):
            errors.append(f"Nó sem id: {node.label}")
    for relationship in graph.relationships:
        if relationship.relationship not in ALLOWED_RELATIONSHIPS:
            errors.append(f"Relacionamento não permitido: {relationship.relationship}")
        if (relationship.source_label, relationship.source_id) not in node_keys:
            errors.append(f"Origem inexistente: {relationship.source_id}")
        if (relationship.target_label, relationship.target_id) not in node_keys:
            errors.append(f"Destino inexistente: {relationship.target_id}")
    return errors
