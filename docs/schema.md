# Schema do grafo (filmes e séries)

## Nós implementados

| Label | Propriedades principais | Uso |
|---|---|---|
| `Document` | `id`, `title`, `uri`, `checksum`, `source`, `year`, `metadata_json` | Documento original (um por título) |
| `Chunk` | `id`, `text`, `position`, `document_id`, `embedding` | Trecho indexável |
| `Entity` | `id`, `name`, `canonical_name`, `entity_type` | Tema extraído da sinopse (NER) |
| `Movie` | `id`, `title`, `year` | Filme |
| `Series` | `id`, `title`, `year` | Série |
| `Person` | `id`, `name`, `canonical_name` | Diretor, criador ou ator canonicalizado |
| `Genre` | `id`, `name` | Gênero |
| `Studio` | `id`, `name` | Estúdio ou canal |

## Relações implementadas

- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Person)-[:DIRECTED]->(Movie)`
- `(Person)-[:CREATED]->(Series)`
- `(Person)-[:ACTED_IN]->(Movie|Series)`
- `(Movie|Series)-[:HAS_GENRE]->(Genre)`
- `(Movie|Series)-[:PRODUCED_BY]->(Studio)`
- `(Chunk)-[:MENTIONS]->(Entity)`
- `(Entity)-[:RELATED_TO {relation_type, confidence}]->(Entity)`

## Regras

- IDs são estáveis e usados em operações `MERGE`; pessoas, gêneros e estúdios usam IDs canônicos (`person:keanu-reeves`).
- Documentos carregam fonte, URI, checksum e metadados.
- Chunks carregam texto, posição e embedding de dimensão 384.
- A extração valida labels, IDs, relações e referências antes da persistência.
- O NER/RE determinístico identifica temas conhecidos nas sinopses e registra menções e relações com confiança.
- O índice vetorial usa similaridade de cosseno.
