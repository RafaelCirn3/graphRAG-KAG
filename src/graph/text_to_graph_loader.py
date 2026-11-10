"""Persistência do resultado Text-to-Graph no Neo4j."""

from neo4j import Driver

from src.extraction.text_to_graph import ExtractedGraph, validate_graph


def persist_graph(driver: Driver, graph: ExtractedGraph) -> tuple[int, int]:
    errors = validate_graph(graph)
    if errors:
        raise ValueError("Saída Text-to-Graph inválida: " + "; ".join(errors))
    with driver.session() as session:
        for node in graph.nodes:
            session.run(
                f"MERGE (n:{node.label} {{id: $id}}) SET n += $properties",
                id=node.id,
                properties=node.properties,
            ).consume()
        for relationship in graph.relationships:
            session.run(
                f"MATCH (a:{relationship.source_label} {{id: $source_id}}), "
                f"(b:{relationship.target_label} {{id: $target_id}}) "
                f"MERGE (a)-[r:{relationship.relationship}]->(b) SET r += $properties",
                source_id=relationship.source_id,
                target_id=relationship.target_id,
                properties=relationship.properties,
            ).consume()
    return len(graph.nodes), len(graph.relationships)
