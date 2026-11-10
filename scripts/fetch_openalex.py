"""Baixa uma amostra pequena de publicações reais do OpenAlex."""

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main() -> None:
    params = urlencode({
        "search": "GraphRAG knowledge graph retrieval augmented generation",
        "filter": "type:article,from_publication_date:2020-01-01",
        "per-page": 20,
        "mailto": "academic-demo@example.com",
    })
    request = Request(f"https://api.openalex.org/works?{params}", headers={"User-Agent": "GraphRAG-KAG-Academic-Demo/0.1"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    output = Path("data/raw/openalex_publications.jsonl")
    records = payload.get("results", [])
    output.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")
    print(f"OpenAlex: {len(records)} publicações salvas em {output}")


if __name__ == "__main__":
    main()
