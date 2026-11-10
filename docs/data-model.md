# Modelo de dados

O modelo oficial está em [`schema.md`](schema.md).

A implementação atual cobre quatro grupos principais:

- Documentos e chunks: `Document`, `Chunk`, `HAS_CHUNK`;
- Publicações: `Paper`, `Author`, `Venue`, `Technology`;
- Afiliações: `Institution`, `AFFILIATED_WITH`;
- Extração Text-to-Graph: `Entity`, `MENTIONS`, `RELATED_TO`.

Os embeddings ficam em `Chunk.embedding`, com dimensão 384 e similaridade de cosseno. A descrição detalhada de propriedades, relações e limitações está em `docs/schema.md`.
