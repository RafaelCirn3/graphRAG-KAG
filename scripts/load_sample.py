"""Carrega a amostra acadêmica local no Neo4j."""

import argparse
from pathlib import Path

from neo4j import GraphDatabase

from src.config import settings
from src.graph.loader import load_publications
from src.ingestion.loaders import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/publications.sample.jsonl")
    args = parser.parse_args()
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    try:
        driver.verify_connectivity()
        records = load_jsonl(Path(args.input))
        total = load_publications(driver, records, source="sample")
        print(f"Carga concluída: {total} chunks processados")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
