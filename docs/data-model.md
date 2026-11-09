# Modelo de dados Neo4j

O modelo oficial da atividade está em [`schema.md`](schema.md). Este arquivo existe como ponto de compatibilidade para referências anteriores.

## Nós iniciais

- `Document {id, title, uri, checksum, published_at}`
- `Chunk {id, text, embedding, position}`
- `Entity {id, canonical_name, entity_type, aliases, embedding}`

## Relações iniciais

- `(Document)-[:HAS_CHUNK]->(Chunk)`
- `(Chunk)-[:MENTIONS]->(Entity)`
- `(Entity)-[:RELATED_TO {relation_type, confidence, source_chunk_id}]->(Entity)`

O schema pode evoluir conforme o domínio escolhido, mas mudanças devem ser versionadas em `src/graph/migrations/` e refletidas neste documento.

## Índices e constraints obrigatórios

- unicidade para IDs de `Document`, `Chunk` e `Entity`;
- BTREE para propriedades de filtragem;
- full-text para nomes/textos;
- vector para `Chunk.embedding` e/ou `Entity.embedding`.

Validar nomes e sintaxe compatíveis com a versão do Neo4j antes de aplicar em produção.
