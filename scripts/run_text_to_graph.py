"""Extrai e persiste o grafo de filmes e séries."""

import argparse

from neo4j import GraphDatabase

from src.config import settings
from src.extraction.text_to_graph import extract_title, validate_graph
from src.graph.text_to_graph_loader import persist_graph
from src.ingestion.loaders import load_json, normalize_title


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
        total_nodes = total_relationships = 0
        for record in load_json(args.input):
            graph = extract_title(normalize_title(record, source=args.source))
            errors = validate_graph(graph)
            if errors:
                raise ValueError("; ".join(errors))
            nodes, relationships = persist_graph(driver, graph)
            total_nodes += nodes
            total_relationships += relationships
        print(f"Text-to-Graph concluído: {total_nodes} nós processados, {total_relationships} relações processadas")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
