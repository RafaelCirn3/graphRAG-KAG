"""Conjunto de avaliação com gabarito derivado do próprio catálogo (titles.json).

O gabarito é calculado a partir dos dados, não digitado à mão: se o catálogo mudar,
basta regerar o arquivo com `python -m scripts.build_eval_set`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

Title = dict[str, Any]


def load_titles(path: str | Path) -> list[Title]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _uniq(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def _by_title(titles: list[Title], name: str) -> Title:
    return next(t for t in titles if t["title"] == name)


def _directed(titles: list[Title], person: str) -> list[Title]:
    return [t for t in titles if t["type"] == "movie" and person in t["creators"]]


def _created(titles: list[Title], people: list[str]) -> list[Title]:
    return [t for t in titles if t["type"] == "series" and set(t["creators"]) & set(people)]


def _acted(titles: list[Title], person: str, kind: str) -> list[Title]:
    return [t for t in titles if t["type"] == kind and person in t["cast"]]


def _flat(titles: list[Title], field: str) -> list[str]:
    return _uniq([value for t in titles for value in t[field]])


def _item(qid: str, category: str, hops: int, question: str, docs: list[Title],
          entities: list[str], terms: list[str], answerable: bool = True) -> dict[str, Any]:
    return {
        "id": qid,
        "category": category,
        "min_hops": hops,
        "question": question,
        "answerable": answerable,
        "gold_documents": [d["id"] for d in docs],
        "gold_entities": _uniq(entities),
        "evidence_terms": terms,
    }


def _require_absent(titles: list[Title], *, title: str | None = None, actor: str | None = None,
                    nolan_after: int | None = None) -> None:
    """Garante que a pergunta 'sem resposta' continua sem resposta no catálogo atual."""
    if title and any(t["title"].lower() == title.lower() for t in titles):
        raise ValueError(f"'{title}' agora existe no catálogo; troque a pergunta adversarial.")
    if actor and any(actor in t["cast"] for t in titles):
        raise ValueError(f"'{actor}' agora existe no catálogo; troque a pergunta adversarial.")
    if nolan_after and any(t["year"] > nolan_after for t in _directed(titles, "Christopher Nolan")):
        raise ValueError("Há filme de Nolan após o ano limite; troque a pergunta adversarial.")


def build_questions(titles: list[Title]) -> list[dict[str, Any]]:
    keanu = _acted(titles, "Keanu Reeves", "movie")
    nolan = _directed(titles, "Christopher Nolan")
    gilligan = _created(titles, ["Vince Gilligan"])
    time_travel = [t for t in titles if t["type"] == "series" and t["studio"] == "Netflix"
                   and "viagem no tempo" in t["synopsis"].lower()]
    matrix = _by_title(titles, "The Matrix")
    interstellar = _by_title(titles, "Interstellar")
    dark = _by_title(titles, "Dark")
    saul = _by_title(titles, "Better Call Saul")
    banks = _acted(titles, "Jonathan Banks", "series")
    saul_family = _created(titles, saul["creators"])
    cast_count = Counter(actor for t in titles for actor in t["cast"])
    repeated = [name for name, count in cast_count.items() if count > 1]
    repeated_docs = [t for t in titles if set(t["cast"]) & set(repeated)]

    _require_absent(titles, title="Pulp Fiction")
    _require_absent(titles, actor="Tom Hanks")
    _require_absent(titles, title="The Crown")
    _require_absent(titles, nolan_after=2015)

    return [
        # Perguntas originais do projeto (q1-q4), agora com gabarito.
        _item("q1", "2_saltos", 2, "Em quais filmes Keanu Reeves atuou e quem dirigiu esses filmes?",
              keanu, _flat(keanu, "creators") + [t["title"] for t in keanu], ["keanu reeves"]),
        _item("q2", "2_saltos", 2, "Quais filmes foram dirigidos por Christopher Nolan e quais estúdios os produziram?",
              nolan, [t["title"] for t in nolan] + [t["studio"] for t in nolan], ["christopher nolan"]),
        _item("q3", "2_saltos", 2, "Quais séries foram criadas por Vince Gilligan e quais atores aparecem nelas?",
              gilligan, [t["title"] for t in gilligan] + _flat(gilligan, "cast"), ["vince gilligan"]),
        _item("q4", "2_saltos", 2, "Quais séries da Netflix envolvem viagem no tempo e quem as criou?",
              time_travel, [t["title"] for t in time_travel] + _flat(time_travel, "creators"),
              ["netflix", "viagem no tempo"]),
        # 1 salto
        _item("q5", "1_salto", 1, "Quem dirigiu o filme The Matrix?",
              [matrix], matrix["creators"], ["the matrix"]),
        _item("q6", "1_salto", 1, "Qual estúdio produziu o filme Interstellar?",
              [interstellar], [interstellar["studio"]], ["interstellar"]),
        _item("q7", "1_salto", 1, "Quem criou a série Dark?",
              [dark], dark["creators"], ["dark"]),
        # 2 saltos
        _item("q8", "2_saltos", 2, "Quais atores atuaram em filmes dirigidos por Christopher Nolan?",
              nolan, _flat(nolan, "cast"), ["christopher nolan"]),
        _item("q9", "2_saltos", 2, "Em quais séries Jonathan Banks atuou e quem as criou?",
              banks, [t["title"] for t in banks] + _flat(banks, "creators"), ["jonathan banks"]),
        _item("q10", "2_saltos", 2, "Com quais atores Keanu Reeves contracenou nos filmes do catálogo?",
              keanu, [a for t in keanu for a in t["cast"] if a != "Keanu Reeves"], ["keanu reeves"]),
        # 3 saltos
        _item("q11", "3_saltos", 3, "Quais estúdios produziram séries criadas por quem criou Better Call Saul?",
              saul_family, [t["studio"] for t in saul_family], ["better call saul"]),
        _item("q12", "3_saltos", 3, "Quais atores atuaram em séries criadas por quem criou Better Call Saul?",
              saul_family, _flat(saul_family, "cast"), ["better call saul"]),
        # Agregação (exige olhar o grafo inteiro, não só vizinhança de um nó)
        _item("q13", "agregacao", 0, "Quais atores aparecem em mais de um título do catálogo?",
              repeated_docs, repeated, []),
        # Sem resposta no catálogo: o comportamento correto é dizer que não há evidência.
        _item("q14", "sem_resposta", 0, "Quem dirigiu o filme Pulp Fiction?", [], [], ["pulp fiction"], False),
        _item("q15", "sem_resposta", 0, "Em quais filmes Tom Hanks atuou?", [], [], ["tom hanks"], False),
        _item("q16", "sem_resposta", 0, "Qual estúdio produziu a série The Crown?", [], [], ["the crown"], False),
        _item("q17", "sem_resposta", 0, "Quais filmes Christopher Nolan dirigiu depois de 2015?",
              [], [], ["christopher nolan"], False),
    ]


def write_jsonl(questions: list[dict[str, Any]], path: str | Path) -> None:
    lines = [json.dumps(q, ensure_ascii=False) for q in questions]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
