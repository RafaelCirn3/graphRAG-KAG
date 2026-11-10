"""Busca híbrida: vetor, full-text e expansão estruturada no grafo."""

from __future__ import annotations

from typing import Any

from neo4j import Driver

from src.retrieval.embeddings import embed_text


def hybrid_search(driver: Driver, question: str, limit: int = 5) -> list[dict[str, Any]]:
    embedding = embed_text(question)
    query = """
    CALL db.index.vector.queryNodes('chunk_embedding_vector', $limit, $embedding)
    YIELD node AS chunk, score AS vector_score
    OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(chunk)
    OPTIONAL MATCH (d)-[:HAS_CHUNK]->(related:Chunk)
    RETURN d.id AS document_id, d.title AS title, chunk.text AS text,
           vector_score, collect(DISTINCT related.id)[0..5] AS related_chunks
    ORDER BY vector_score DESC
    """
    with driver.session() as session:
        vector_results = [dict(row) for row in session.run(query, embedding=embedding, limit=limit)]
    text_results = fulltext_search(driver, question, limit)
    text_scores = {item["document_id"]: float(item.get("score") or 0.0) for item in text_results}
    max_text = max(text_scores.values(), default=1.0)
    merged = []
    with driver.session() as session:
        for item in vector_results:
            document_id = item["document_id"]
            path_row = session.run(
                """
                MATCH (p:Paper {id: $document_id})
                OPTIONAL MATCH path = (p)-[*1..3]-(neighbor)
                RETURN count(path) AS paths
                """,
                document_id=document_id,
            ).single()
            path_score = min(1.0, (path_row["paths"] if path_row else 0) / 10.0)
            vector_score = float(item.get("vector_score") or 0.0)
            fulltext_score = text_scores.get(document_id, 0.0) / max_text
            item["fulltext_score"] = round(fulltext_score, 4)
            item["path_score"] = round(path_score, 4)
            item["hybrid_score"] = round(0.6 * vector_score + 0.2 * fulltext_score + 0.2 * path_score, 4)
            merged.append(item)
    return sorted(merged, key=lambda item: item["hybrid_score"], reverse=True)


def fulltext_search(driver: Driver, question: str, limit: int = 5) -> list[dict[str, Any]]:
    query = """
    CALL db.index.fulltext.queryNodes('chunk_text_fulltext', $question)
    YIELD node AS chunk, score
    OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(chunk)
    RETURN d.id AS document_id, d.title AS title, chunk.text AS text, score
    ORDER BY score DESC LIMIT $limit
    """
    with driver.session() as session:
        return [dict(row) for row in session.run(query, question=question, limit=limit)]
