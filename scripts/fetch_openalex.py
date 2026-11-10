"""Baixa uma amostra pequena de publicações reais do OpenAlex."""

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main() -> None:
    output = Path("data/raw/openalex_publications.jsonl")
    force = os.getenv("FORCE_OPENALEX_REFRESH", "0") == "1"
    if output.exists() and output.stat().st_size > 100 and not force:
        count = sum(1 for line in output.read_text(encoding="utf-8").splitlines() if line.strip())
        print(f"OpenAlex: usando cache local com {count} publicações em {output}")
        return
    params = urlencode({
        "search": "GraphRAG knowledge graph retrieval augmented generation",
        "filter": "type:article,from_publication_date:2020-01-01",
        "per-page": 20,
        "mailto": os.getenv("OPENALEX_MAILTO", "academic-demo@example.com"),
    })
    request = Request(f"https://api.openalex.org/works?{params}", headers={"User-Agent": "GraphRAG-KAG-Academic-Demo/0.1"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            records = payload.get("results", [])
            output.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")
            print(f"OpenAlex: {len(records)} publicações salvas em {output}")
            return
        except HTTPError as error:
            if error.code != 429 or attempt == 2:
                break
            wait_seconds = int(error.headers.get("Retry-After", str(2 ** (attempt + 1))))
            print(f"OpenAlex: limite de requisições; nova tentativa em {wait_seconds}s")
            time.sleep(wait_seconds)
        except URLError as error:
            if attempt == 2:
                print(f"OpenAlex: falha de rede ({error})")
                break
            time.sleep(2 ** (attempt + 1))

    sample = Path("data/raw/publications.sample.jsonl")
    if output.exists() and output.stat().st_size > 100:
        print(f"OpenAlex indisponível; mantendo cache existente em {output}")
        return
    output.write_text(sample.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OpenAlex indisponível; usando fallback acadêmico em {output}")


if __name__ == "__main__":
    main()
