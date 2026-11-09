"""Acesso Neo4j isolado para facilitar testes e evolução do projeto."""

from neo4j import Driver, GraphDatabase

from src.config import settings


def create_driver() -> Driver:
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


def verify_connection(driver: Driver) -> bool:
    driver.verify_connectivity()
    return True
