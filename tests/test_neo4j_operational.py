import os
import pytest
from neo4j import GraphDatabase
from src.config import settings


@pytest.mark.skipif(os.getenv("RUN_NEO4J_TESTS") != "1", reason="requires loaded Neo4j")
def test_loaded_catalog():
    with GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password)) as driver:
        with driver.session() as session:
            indexes = {row["name"]: row["state"] for row in session.run("SHOW INDEXES")}
            assert all(indexes.get(i) == "ONLINE" for i in ("person_name","movie_title","chunk_embedding_vector"))
            assert session.run("MATCH (:Entity)-[:MENTIONED_IN]->(t)<-[:DESCRIBES]-(:Document) RETURN count(t) AS n").single()["n"]
            assert session.run("MATCH (:Person {name:'Keanu Reeves'})-[:ACTED_IN]->(:Movie)<-[:DIRECTED]-(:Person) RETURN count(*) AS n").single()["n"]

