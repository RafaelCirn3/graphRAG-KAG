# Schema acadêmico do grafo

## Nós implementados

| Label | Propriedades principais | Uso |
|---|---|---|
| `Document` | `id`, `title`, `uri`, `checksum`, `source`, `year`, `metadata_json` | Documento original |
| `Chunk` | `id`, `text`, `position`, `document_id`, `embedding` | Trecho indexável |
| `Paper` | `id`, `title`, `year` | Publicação científica |
| `Author` | `id`, `name`, `canonical_name` | Autor canonicalizado |
| `Venue` | `id`, `name` | Conferência ou periódico |
| `Technology` | `id`, `name` | Tecnologia ou tópico |

## Nós previstos para expansão

`Institution`, `ResearchArea` e relações de citação `CITES` ainda dependem de dados dessas propriedades nas fontes escolhidas.

## Relações implementadas

- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Author)-[:WROTE]->(Paper)`
- `(Paper)-[:PUBLISHED_AT]->(Venue)`
- `(Paper)-[:USES_TECHNOLOGY]->(Technology)`

## Regras

- IDs são estáveis e usados em operações `MERGE`.
- Documentos carregam fonte, URI, checksum e metadados.
- Chunks carregam texto, posição e embedding de dimensão 384.
- A extração valida labels, IDs, relações e referências antes da persistência.
- O índice vetorial usa similaridade de cosseno.
