# Schema acadêmico do grafo

Este é o schema mínimo usado para a demonstração e avaliação da atividade. Ele pode ser ajustado ao domínio escolhido, desde que os quatro pilares do Word permaneçam atendidos.

## Nós

| Label | Propriedades principais | Finalidade |
|---|---|---|
| `Document` | `id`, `title`, `uri`, `checksum` | Fonte original |
| `Chunk` | `id`, `text`, `position`, `embedding` | Trecho indexável |
| `Entity` | `id`, `canonical_name`, `entity_type`, `aliases`, `embedding` | Entidade normalizada |

## Relações

- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Chunk)-[:MENTIONS]->(Entity)`
- `(Entity)-[:RELATED_TO {relation_type, confidence, source_chunk_id}]->(Entity)`

## Regras

- `id` é único em todos os labels.
- `Document.uri` e `Chunk.text` permitem localizar a origem da evidência.
- Toda relação extraída deve guardar confiança e o chunk de origem.
- Embeddings são gerados apenas quando a etapa de recuperação vetorial estiver habilitada.
