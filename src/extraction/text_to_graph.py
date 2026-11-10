"""Transformação determinística de publicações acadêmicas em um grafo tipado."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_LABELS = {"Paper", "Author", "Venue", "Technology", "Institution", "ResearchArea"}
ALLOWED_RELATIONSHIPS = {
    "WROTE",
    "PUBLISHED_AT",
    "USES_TECHNOLOGY",
    "AFFILIATED_WITH",
    "BELONGS_TO",
    "CITES",
}


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


def extract_publication(publication: dict[str, Any]) -> ExtractedGraph:
    paper_id = str(publication["id"])
    nodes = [_node(paper_id, "Paper", title=publication["title"], year=publication.get("year"))]
    relationships: list[GraphRelationship] = []

    for author in publication.get("authors", []):
        author_id = str(author["id"])
        nodes.append(_node(author_id, "Author", name=author["name"]))
        relationships.append(GraphRelationship(author_id, "Author", "WROTE", paper_id, "Paper", {}))

    venue = publication.get("venue")
    if venue:
        venue_id = f"venue:{str(venue).strip().lower().replace(' ', '-') }"
        nodes.append(_node(venue_id, "Venue", name=venue))
        relationships.append(GraphRelationship(paper_id, "Paper", "PUBLISHED_AT", venue_id, "Venue", {}))

    for topic in publication.get("topics", []):
        topic_name = topic.get("display_name", topic) if isinstance(topic, dict) else topic
        topic_id = f"technology:{str(topic_name).strip().lower().replace(' ', '-') }"
        nodes.append(_node(topic_id, "Technology", name=str(topic_name)))
        relationships.append(GraphRelationship(paper_id, "Paper", "USES_TECHNOLOGY", topic_id, "Technology", {}))

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
