"""Extrai e persiste entidades e relações da amostra acadêmica."""

from neo4j import GraphDatabase

from src.config import settings
from src.extraction.text_to_graph import extract_publication, validate_graph
from src.graph.text_to_graph_loader import persist_graph
from src.ingestion.loaders import load_jsonl, normalize_publication


def main() -> None:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    try:
        total_nodes = total_relationships = 0
        for record in load_jsonl("data/raw/publications.sample.jsonl"):
            graph = extract_publication(normalize_publication(record, source="sample"))
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
