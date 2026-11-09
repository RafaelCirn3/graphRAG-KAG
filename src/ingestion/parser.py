"""Parser de publicações para documentos textuais rastreáveis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedDocument:
    document_id: str
    title: str
    text: str
    metadata: dict


def parse_publication(publication: dict) -> ParsedDocument:
    text_parts = [publication["title"]]
    if publication.get("abstract"):
        text_parts.append(publication["abstract"])
    if publication.get("topics"):
        topics = [t.get("display_name", t) if isinstance(t, dict) else t for t in publication["topics"]]
        text_parts.append("Tópicos: " + ", ".join(map(str, topics)))
    return ParsedDocument(
        document_id=str(publication["id"]),
        title=publication["title"],
        text="\n\n".join(text_parts),
        metadata={k: v for k, v in publication.items() if k not in {"title", "abstract", "topics"}},
    )
