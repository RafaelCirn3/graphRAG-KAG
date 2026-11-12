"""Gera data/evaluation/questions_eval.jsonl com gabarito derivado de data/raw/titles.json."""

import argparse

from src.evaluation.eval_set import build_questions, load_titles, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--titles", default="data/raw/titles.json")
    parser.add_argument("--output", default="data/evaluation/questions_eval.jsonl")
    args = parser.parse_args()
    questions = build_questions(load_titles(args.titles))
    write_jsonl(questions, args.output)
    print(f"{len(questions)} perguntas escritas em {args.output}")


if __name__ == "__main__":
    main()
