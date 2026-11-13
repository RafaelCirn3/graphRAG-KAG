"""Busca híbrida: vetor, full-text e expansão estruturada no grafo."""

from __future__ import annotations

import re
from typing import Any

from neo4j import Driver

from src.retrieval.graph_context import enrich, generated_paths
from src.retrieval.embeddings import embed_text


STOPWORDS = {"quais", "qual", "que", "com", "para", "sobre", "dos", "das", "uma", "um", "e", "ou", "em", "quem", "esses", "essas", "nelas", "neles", "aparecem", "filmes", "séries", "títulos", "atores", "atuou", "dirigiu", "dirigidos", "criadas", "criou", "foram"}


def _query_terms(question: str) -> set[str]:
    return {term for term in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", question.lower()) if term not in STOPWORDS and len(term) > 2}


def hybrid_search(driver: Driver, question: str, limit: int = 5) -> list[dict[str, Any]]:
    embedding = embed_text(question)
    query = """
    CALL db.index.vector.queryNodes('chunk_embedding_vector', $candidate_limit, $embedding)
    YIELD node AS chunk, score AS vector_score
    OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(chunk)
    OPTIONAL MATCH (d)-[:HAS_CHUNK]->(related:Chunk)
    RETURN d.id AS document_id, d.title AS title, chunk.text AS text,
           vector_score, collect(DISTINCT related.id)[0..5] AS related_chunks
    ORDER BY vector_score DESC
    """
    terms = _query_terms(question)
    with driver.session() as session:
        vector_results = [dict(row) for row in session.run(query, embedding=embedding, candidate_limit=max(limit * 3, 10))]
    text_results = fulltext_search(driver, question, limit)
    text_scores = {item["document_id"]: float(item.get("score") or 0.0) for item in text_results}
    max_text = max(text_scores.values(), default=1.0)
    merged_by_document: dict[str, dict[str, Any]] = {}
    with driver.session() as session:
        for item in vector_results:
            document_id = item["document_id"]
            current = merged_by_document.get(document_id)
            if current and current["vector_score"] >= item["vector_score"]:
                continue
            merged_by_document[document_id] = item
        generated, paths = generated_paths(session, question)
        metrics = enrich(session)
        for item in list(merged_by_document.values()):
            document_id = item["document_id"]
            matching = [row for row in paths if row["document_id"] == document_id]
            path = {"paths": matching, **metrics.get(document_id, {})}
            path_score = float(bool(matching))
            vector_score = float(item.get("vector_score") or 0.0)
            fulltext_score = text_scores.get(document_id, 0.0) / max_text
            searchable_text = f"{item.get('title', '')} {item.get('text', '')}".lower()
            keyword_score = sum(1 for term in terms if term in searchable_text) / max(len(terms), 1)
            item["keyword_score"] = round(keyword_score, 4)
            item["fulltext_score"] = round(fulltext_score, 4)
            item["path_score"] = round(path_score, 4)
            item["hybrid_score"] = round(0.5 * vector_score + 0.2 * fulltext_score + 0.1 * keyword_score + 0.2 * path_score, 4)
            item["path"] = path
            item["executed_cypher"] = {"generated": generated}
    return sorted(merged_by_document.values(), key=lambda item: item["hybrid_score"], reverse=True)[:limit]


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
