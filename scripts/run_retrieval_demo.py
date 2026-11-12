"""Executa recuperação híbrida e geração grounded sobre a base local."""

from neo4j import GraphDatabase

from src.config import settings
from src.generation.grounded import grounded_answer
from src.retrieval.hybrid import fulltext_search, hybrid_search


def main() -> None:
    question = "Em quais filmes Keanu Reeves atuou e quem dirigiu esses filmes?"
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    try:
        vector_results = hybrid_search(driver, question)
        text_results = fulltext_search(driver, "Keanu Reeves")
        evidence = vector_results or text_results
        result = grounded_answer(question, evidence, cypher="vector + fulltext + graph expansion")
        print(result)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
