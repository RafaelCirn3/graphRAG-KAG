"""Compara LLM sem recuperação, RAG vetorial e GraphRAG híbrido quanto a acerto e alucinação.

Uso:
  python -m scripts.evaluate_hallucination                      # gera respostas (Neo4j + Ollama) e pontua
  python -m scripts.evaluate_hallucination --answers ext.json   # adiciona respostas de um LLM externo
  python -m scripts.evaluate_hallucination --no-generate --answers ext.json   # só pontua o arquivo

Formato de --answers: {"q1": {"gpt": "texto da resposta", ...}, "q2": {...}}
(cada chave interna vira uma variante na tabela; serve para a comparação com LLM externo).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.evaluation.eval_set import load_titles
from src.evaluation.metrics import Catalog, aggregate, format_table, score_answer

VECTOR_QUERY = """
CALL db.index.vector.queryNodes('chunk_embedding_vector', $k, $embedding) YIELD node, score
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(node)
RETURN d.id AS document_id, d.title AS title, node.text AS text, score AS vector_score
ORDER BY score DESC
"""


def vector_evidence(driver: Any, question: str, k: int = 5) -> list[dict[str, Any]]:
    from src.retrieval.embeddings import embed_text

    with driver.session() as session:
        rows = [dict(r) for r in session.run(VECTOR_QUERY, k=k * 3, embedding=embed_text(question))]
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        seen.setdefault(row["document_id"], row)  # já ordenado por score: fica o melhor chunk
    return list(seen.values())[:k]


def generate_answers(questions: list[dict[str, Any]], variants: list[str], k: int) -> dict[str, dict[str, str | None]]:
    from neo4j import GraphDatabase

    from src.config import settings
    from src.generation.grounded import llm_answer
    from src.generation.no_retrieval import no_retrieval_answer
    from src.retrieval.hybrid import hybrid_search

    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    answers: dict[str, dict[str, str | None]] = {}
    try:
        for item in questions:
            question = item["question"]
            answers[item["id"]] = {}
            for variant in variants:
                if variant == "no_retrieval":
                    answer = no_retrieval_answer(question)
                elif variant == "vector":
                    answer = llm_answer(question, vector_evidence(driver, question, k))
                elif variant == "hybrid":
                    answer = llm_answer(question, hybrid_search(driver, question, k))
                else:
                    raise ValueError(f"variante desconhecida: {variant}")
                answers[item["id"]][variant] = answer
                print(f"{item['id']} {variant}: {'ok' if answer else 'SEM RESPOSTA (LLM indisponível?)'}")
    finally:
        driver.close()
    return answers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--questions", default="data/evaluation/questions_eval.jsonl")
    parser.add_argument("--titles", default="data/raw/titles.json")
    parser.add_argument("--output", default="data/evaluation/hallucination_results.json")
    parser.add_argument("--variants", nargs="+", default=["no_retrieval", "vector", "hybrid"])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--answers", help="JSON com respostas de outro LLM (variantes extras)")
    parser.add_argument("--no-generate", action="store_true", help="não chama Neo4j/Ollama; só pontua --answers")
    args = parser.parse_args()

    questions = [json.loads(line) for line in Path(args.questions).read_text(encoding="utf-8").splitlines() if line.strip()]
    catalog = Catalog.from_titles(load_titles(args.titles))

    answers: dict[str, dict[str, str | None]] = {q["id"]: {} for q in questions}
    if not args.no_generate:
        for qid, variants in generate_answers(questions, args.variants, args.k).items():
            answers[qid].update(variants)
    if args.answers:
        external = json.loads(Path(args.answers).read_text(encoding="utf-8"))
        for qid, variants in external.items():
            answers.setdefault(qid, {}).update(variants)

    rows, detail = [], []
    for item in questions:
        entry = {"id": item["id"], "category": item["category"], "question": item["question"],
                 "answerable": item["answerable"], "variants": {}}
        for variant, answer in answers.get(item["id"], {}).items():
            if not answer:
                entry["variants"][variant] = {"answer": None}
                continue
            scored = score_answer(item, answer, catalog)
            entry["variants"][variant] = {"answer": answer, **scored}
            rows.append({"variant": variant, "category": item["category"], "answerable": item["answerable"], **scored})
        detail.append(entry)

    summary = aggregate(rows)
    Path(args.output).write_text(json.dumps({"summary": summary, "questions": detail}, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
    print("\n" + format_table(summary))
    for category in sorted({r["category"] for r in rows}):
        print(f"\n[{category}]\n" + format_table(summary, category))
    print(f"\nResultados detalhados: {args.output}")


if __name__ == "__main__":
    main()
