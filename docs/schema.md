# Schema acadêmico do grafo

Este é o schema mínimo usado para a demonstração e avaliação da atividade. Ele pode ser ajustado ao domínio escolhido, desde que os quatro pilares do Word permaneçam atendidos.

## Nós

| Label | Propriedades principais | Finalidade |
|---|---|---|
| `Document` | `id`, `title`, `uri`, `checksum` | Fonte original |
| `Chunk` | `id`, `text`, `position`, `embedding` | Trecho indexável |
| `Entity` | `id`, `canonical_name`, `entity_type`, `aliases`, `embedding` | Entidade normalizada |
| `Paper` | `id`, `title`, `year` | Publicação científica |
| `Author` | `id`, `name` | Autor |
| `Venue` | `id`, `name` | Conferência ou periódico |
| `Technology` | `id`, `name` | Tecnologia ou tópico |
| `Institution` | `id`, `name` | Instituição |
| `ResearchArea` | `id`, `name` | Área de pesquisa |

## Relações

- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Chunk)-[:MENTIONS]->(Entity)`
- `(Entity)-[:RELATED_TO {relation_type, confidence, source_chunk_id}]->(Entity)`
- `(Author)-[:WROTE]->(Paper)`
- `(Paper)-[:PUBLISHED_AT]->(Venue)`
- `(Paper)-[:USES_TECHNOLOGY]->(Technology)`
- `(Author)-[:AFFILIATED_WITH]->(Institution)`
- `(Paper)-[:BELONGS_TO]->(ResearchArea)`
- `(Paper)-[:CITES]->(Paper)`

## Regras

- `id` é único em todos os labels.
- `Document.uri` e `Chunk.text` permitem localizar a origem da evidência.
- Toda relação extraída deve guardar confiança e o chunk de origem.
- Embeddings são gerados apenas quando a etapa de recuperação vetorial estiver habilitada.
