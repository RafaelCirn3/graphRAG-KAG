import json
from pathlib import Path

import pytest

from src.evaluation.eval_set import build_questions, load_titles
from src.evaluation.metrics import Catalog, abstained, aggregate, score_answer, unsupported_entities

TITLES = load_titles(Path(__file__).resolve().parents[1] / "data" / "raw" / "titles.json")
CATALOG = Catalog.from_titles(TITLES)
QUESTIONS = {q["id"]: q for q in build_questions(TITLES)}


def test_gold_derivado_do_catalogo():
    q1 = QUESTIONS["q1"]
    assert set(q1["gold_documents"]) == {"movie:the-matrix", "movie:john-wick"}
    assert {"Lana Wachowski", "Chad Stahelski", "The Matrix", "John Wick"} <= set(q1["gold_entities"])
    assert QUESTIONS["q4"]["gold_documents"] == ["series:dark"]
    assert QUESTIONS["q11"]["gold_entities"] == ["AMC"]
    assert set(QUESTIONS["q13"]["gold_entities"]) == {"Keanu Reeves", "Jonathan Banks"}


def test_perguntas_sem_resposta_nao_tem_gabarito():
    for qid in ("q14", "q15", "q16", "q17"):
        assert QUESTIONS[qid]["answerable"] is False
        assert QUESTIONS[qid]["gold_entities"] == []


def test_pergunta_adversarial_falha_se_catalogo_passar_a_ter_a_resposta():
    extended = TITLES + [{**TITLES[0], "id": "movie:pf", "title": "Pulp Fiction"}]
    with pytest.raises(ValueError):
        build_questions(extended)


def test_resposta_correta_sem_alucinacao():
    answer = "Keanu Reeves atuou em The Matrix, dirigido por Lana Wachowski e Lilly Wachowski, e em John Wick, dirigido por Chad Stahelski."
    result = score_answer(QUESTIONS["q1"], answer, CATALOG)
    assert result["correct"] and not result["hallucinated"] and result["recall"] == 1.0


def test_alucinacao_detectada_em_filme_fora_do_catalogo():
    answer = "Keanu Reeves atuou em The Matrix e em Speed, dirigido por Jan de Bont."
    result = score_answer(QUESTIONS["q1"], answer, CATALOG)
    assert result["hallucinated"] and not result["correct"]
    assert "Speed" in result["unsupported_entities"]


def test_inicio_de_frase_nao_gera_falso_positivo():
    answer = "Segundo as evidências, Christopher Nolan dirigiu Inception. Além disso, Interstellar também."
    assert unsupported_entities(answer, QUESTIONS["q2"]["question"], CATALOG) == []


def test_abstencao_correta_em_pergunta_sem_resposta():
    answer = "As evidências recuperadas não bastam: não há informação sobre Pulp Fiction no catálogo."
    assert abstained(answer)
    result = score_answer(QUESTIONS["q14"], answer, CATALOG)
    assert result["correct"] and not result["hallucinated"]


def test_resposta_confiante_em_pergunta_sem_resposta_e_alucinacao():
    result = score_answer(QUESTIONS["q14"], "Pulp Fiction foi dirigido por Quentin Tarantino.", CATALOG)
    assert result["hallucinated"] and not result["correct"]


def test_aggregate_separa_variantes_e_categorias():
    rows = [
        {"variant": "a", "category": "1_salto", "answerable": True, "correct": True, "hallucinated": False, "recall": 1.0},
        {"variant": "a", "category": "sem_resposta", "answerable": False, "correct": False, "hallucinated": True, "recall": None},
        {"variant": "b", "category": "1_salto", "answerable": True, "correct": False, "hallucinated": False, "recall": 0.5},
    ]
    summary = aggregate(rows)
    assert summary["a"]["geral"]["alucinacao"] == 0.5
    assert summary["a"]["sem_resposta"]["abstencao_correta"] == 0.0
    assert summary["b"]["1_salto"]["recall_medio"] == 0.5
