"""Parser de filmes/séries para documentos textuais rastreáveis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedDocument:
    document_id: str
    title: str
    text: str
    metadata: dict


def parse_title(item: dict) -> ParsedDocument:
    kind = "Filme" if item["type"] == "movie" else "Série"
    creator_label = "Direção" if item["type"] == "movie" else "Criação"
    text_parts = [f"{item['title']} ({kind}, {item.get('year') or 's/d'})"]
    if item.get("synopsis"):
        text_parts.append(item["synopsis"])
    for label, values in [(creator_label, item.get("creators")), ("Elenco", item.get("cast")), ("Gêneros", item.get("genres"))]:
        if values:
            text_parts.append(f"{label}: " + ", ".join(values))
    if item.get("studio"):
        text_parts.append(f"Estúdio/canal: {item['studio']}")
    return ParsedDocument(
        document_id=str(item["id"]),
        title=item["title"],
        text="\n\n".join(text_parts),
        metadata={k: v for k, v in item.items() if k not in {"title", "synopsis"}},
    )
