"""Executa NER/RE nos chunks e persiste menções e relações no Neo4j."""

from neo4j import GraphDatabase

from src.config import settings
from src.extraction.ner_re import extract_entities_and_relations


def main() -> None:
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    mentions_count = relations_count = 0
    try:
        with driver.session() as session:
            chunks = list(session.run("MATCH (c:Chunk) RETURN c.id AS id, c.text AS text"))
            for chunk in chunks:
                extracted = extract_entities_and_relations(chunk["text"])
                for mention in extracted.mentions:
                    session.run(
                        """
                        MERGE (e:Entity {id: $id})
                        SET e.canonical_name = $name, e.entity_type = $entity_type, e.name = $name
                        WITH e
                        MATCH (c:Chunk {id: $chunk_id})
                        MERGE (c)-[:MENTIONS]->(e)
                        """,
                        id=mention.entity_id, name=mention.name, entity_type=mention.entity_type, chunk_id=chunk["id"],
                    ).consume()
                    mentions_count += 1
                for source_id, target_id, relation, confidence in extracted.relations:
                    session.run(
                        """
                        MATCH (source:Entity {id: $source_id}), (target:Entity {id: $target_id})
                        MERGE (source)-[r:RELATED_TO]->(target)
                        SET r.relation_type = $relation, r.confidence = $confidence
                        """,
                        source_id=source_id, target_id=target_id, relation=relation, confidence=confidence,
                    ).consume()
                    relations_count += 1
        print(f"NER/RE concluído: {mentions_count} menções, {relations_count} relações")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
