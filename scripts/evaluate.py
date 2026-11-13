"""Avaliação comparativa acadêmica: baseline textual, vetorial e híbrido."""

import json
from pathlib import Path

from neo4j import GraphDatabase

from src.config import settings
from src.model import ask
from src.retrieval.embeddings import embed_text
from src.retrieval.hybrid import hybrid_search


FACT_SCHEMA = {
    "type": "object",
    "required": ["facts"],
    "properties": {"facts": {"type": "array", "items": {
        "type": "object", "required": ["title", "person"],
        "properties": {"title": {"type": "string"}, "person": {"type": "string"}}
    }}}
}


def ask_facts(prompt, question):
    for attempt in range(2):
        answer = ask(prompt, question, FACT_SCHEMA)
        facts = answer.get("facts") if isinstance(answer, dict) else None
        if isinstance(facts, list) and all(
            isinstance(fact, dict) and all(isinstance(fact.get(key), str) and fact[key].strip()
                                           for key in ("title", "person"))
            for fact in facts
        ):
            return answer
        prompt += ' Each item must be an object with nonempty title and person fields.'
    raise ValueError("Ollama returned invalid facts twice; evaluation cannot be scored.")


def main() -> None:
    questions = [json.loads(line) for line in Path("data/evaluation/questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    results = []
    try:
        with driver.session() as session:
            for item in questions:
                question = item["question"]
                vector = session.run(
                    """
                    CALL db.index.vector.queryNodes('chunk_embedding_vector', 5, $embedding)
                    YIELD node, score
                    OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(node)
                    RETURN collect(DISTINCT d.id) AS documents
                    """,
                    embedding=embed_text(question),
                ).single()["documents"]
                hybrid = hybrid_search(driver, question, 5)
                prompt = ("Answer the question about this catalog in Portuguese. Return JSON "
                          "with facts, a list of {title,person} pairs. For studios use the "
                          "studio name as person. Include only pairs answering the question.")
                baseline = ask_facts(prompt, question)
                augmented = ask_facts(prompt, question + "\nEvidence: " + json.dumps(hybrid, ensure_ascii=False))
                catalog = json.loads(Path("data/raw/titles.json").read_text(encoding="utf8"))
                rules = {"q1": ("cast", "Keanu Reeves", "creators"),
                         "q2": ("creators", "Christopher Nolan", "studio"),
                         "q3": ("creators", "Vince Gilligan", "cast"),
                         "q4": ("studio", "Netflix", "creators")}
                field, anchor, target = rules[item["id"]]
                gold = set()
                for title in catalog:
                    if anchor not in title[field]:
                        continue
                    if item["id"] == "q4" and "viagem no tempo" not in title["synopsis"].lower():
                        continue
                    values = title[target]
                    for value in ([values] if isinstance(values,str) else values):
                        gold.add((title["title"].casefold(),value.casefold()))
                def score(answer):
                    facts = {(f["title"].casefold(),f["person"].casefold()) for f in answer["facts"]}
                    return {"answer":answer, "unsupported": sorted(facts-gold),
                            "missing":sorted(gold-facts), "supported":sorted(gold & facts)}
                results.append({
                    "id": item["id"],
                    "min_hops": item["min_hops"],
                    "vector_documents": vector,
                    "hybrid_documents": [row["document_id"] for row in hybrid],
                    "hybrid_scores": [row["hybrid_score"] for row in hybrid],
                    "vector_hit": bool(vector),
                    "hybrid_hit": bool(hybrid),
                    "no_retrieval_baseline": score(baseline),
                    "graph_rag": score(augmented),
                })
    finally:
        driver.close()
    output = Path("data/evaluation/results.json")
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    vector_rate = sum(row["vector_hit"] for row in results) / len(results)
    hybrid_rate = sum(row["hybrid_hit"] for row in results) / len(results)
    print(f"Avaliação concluída: {len(results)} perguntas")
    print(f"Recall operacional — vetorial: {vector_rate:.2%}; híbrido: {hybrid_rate:.2%}")
    print(f"Resultados: {output}")


if __name__ == "__main__":
    main()
