"""Avaliação comparativa acadêmica: baseline textual, vetorial e híbrido."""

import json
from pathlib import Path

from neo4j import GraphDatabase

from src.config import settings
from src.retrieval.embeddings import embed_text
from src.retrieval.hybrid import hybrid_search


def main() -> None:
    questions = [json.loads(line) for line in Path("data/evaluation/questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    results = []
    try:
        with driver.session() as session:
            for item in questions:
                question = item["question"]
                vector = session.run(
                    """
                    CALL db.index.vector.queryNodes('chunk_embedding_vector', 5, $embedding)
                    YIELD node, score
                    OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(node)
                    RETURN collect(DISTINCT d.id) AS documents
                    """,
                    embedding=embed_text(question),
                ).single()["documents"]
                hybrid = hybrid_search(driver, question, 5)
                results.append({
                    "id": item["id"],
                    "min_hops": item["min_hops"],
                    "vector_documents": vector,
                    "hybrid_documents": [row["document_id"] for row in hybrid],
                    "hybrid_scores": [row["hybrid_score"] for row in hybrid],
                    "vector_hit": bool(vector),
                    "hybrid_hit": bool(hybrid),
                })
    finally:
        driver.close()
    output = Path("data/evaluation/results.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    vector_rate = sum(row["vector_hit"] for row in results) / len(results)
    hybrid_rate = sum(row["hybrid_hit"] for row in results) / len(results)
    print(f"Avaliação concluída: {len(results)} perguntas")
    print(f"Recall operacional — vetorial: {vector_rate:.2%}; híbrido: {hybrid_rate:.2%}")
    print(f"Resultados: {output}")


if __name__ == "__main__":
    main()
