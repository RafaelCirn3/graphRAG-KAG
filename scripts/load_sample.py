"""Carrega o catálogo local de filmes e séries no Neo4j."""

import argparse
from pathlib import Path

from neo4j import GraphDatabase

from src.config import settings
from src.graph.loader import load_titles
from src.ingestion.loaders import load_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/titles.json")
    parser.add_argument("--source", default="local")
    args = parser.parse_args()
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    try:
        driver.verify_connectivity()
        records = load_json(Path(args.input))
        total = load_titles(driver, records, source=args.source)
        print(f"Carga concluída: {total} chunks processados")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
