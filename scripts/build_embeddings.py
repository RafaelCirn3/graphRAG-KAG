"""Gera e persiste embeddings locais para os chunks do Neo4j."""

from neo4j import GraphDatabase

from src.config import settings
from src.retrieval.embeddings import embed_text


def main() -> None:
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    try:
        with driver.session() as session:
            chunks = list(session.run("MATCH (c:Chunk) RETURN c.id AS id, c.text AS text"))
            for chunk in chunks:
                session.run(
                    "MATCH (c:Chunk {id: $id}) SET c.embedding = $embedding",
                    id=chunk["id"], embedding=embed_text(chunk["text"]),
                ).consume()
        print(f"Embeddings gerados: {len(chunks)} chunks, dimensão 384")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
