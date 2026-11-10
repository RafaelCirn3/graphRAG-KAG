"""Algoritmos de grafo usados para enriquecer evidências."""

from neo4j import Driver


def shortest_path(driver: Driver, source_id: str, target_id: str) -> list[dict]:
    query = """
    MATCH (source {id: $source_id}), (target {id: $target_id})
    MATCH path = shortestPath((source)-[*..6]-(target))
    RETURN [node IN nodes(path) | {id: node.id, labels: labels(node)}] AS nodes,
           [rel IN relationships(path) | type(rel)] AS relationships
    LIMIT 1
    """
    with driver.session() as session:
        record = session.run(query, source_id=source_id, target_id=target_id).single()
    return dict(record) if record else {"nodes": [], "relationships": []}
