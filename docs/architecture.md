# Arquitetura

```text
Documentos -> ingestão/parser -> NER/RE -> resolução -> nós/relações -> Neo4j
                                                        |              |
Pergunta -> embedding/vector search -------------------+-> Cypher ----+
                                                                         |
                                             rank/communities/paths -> contexto
                                                                         |
                                             LLM -> resposta + evidências
                                                                         |
                                             UI + renderização do subgrafo
```

## Camadas

- `src/ingestion`: loaders, parsing, chunking e metadados de origem.
- `src/extraction`: NER, RE, schema e canonicalização.
- `src/graph`: driver Neo4j, migrações, carga e algoritmos.
- `src/retrieval`: busca vetorial, Cypher, multi-hop e fusão/ranking.
- `src/generation`: montagem de contexto, prompt, resposta estruturada e citações.
- `src/api`: contratos HTTP/orquestração do caso de uso.
- `src/ui`: interface e visualização do subgrafo.
- `tests`: unitários, integração e avaliação end-to-end.

O LLM não deve receber contexto sem origem. O objeto de resposta deve carregar `answer`, `confidence`, `sources`, `cypher`, `nodes` e `relationships`.
