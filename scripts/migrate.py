"""Aplica as migrações Cypher locais de forma sequencial."""

from pathlib import Path

from neo4j import GraphDatabase

from src.config import settings


def main() -> None:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    try:
        for path in sorted(Path("src/graph/migrations").glob("*.cypher")):
            content = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not line.strip().startswith("//"))
            statements = [statement.strip() for statement in content.split(";") if statement.strip()]
            with driver.session() as session:
                for statement in statements:
                    session.run(statement).consume()
            print(f"Aplicada: {path.name} ({len(statements)} instruções)")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
