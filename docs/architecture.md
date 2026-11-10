# Arquitetura implementada

```text
Fonte acadêmica -> loader/parser/chunker -> NER/RE e canonicalização -> Neo4j
                                                                    |
Pergunta -> embedding -> busca vetorial + full-text + caminho -> contexto grounded
                                                                    |
                                                          Streamlit: UI real/demo
```

## Camadas atuais

- `src/ingestion`: loaders, parsing, chunking e metadados de origem.
- `src/extraction`: extração estruturada e canonicalização.
- `src/graph`: cliente Neo4j, carga Text-to-Graph e Shortest Path.
- `src/retrieval`: embeddings locais, busca vetorial, full-text e ranking híbrido.
- `src/generation`: resposta grounded estruturada com fontes e confiança.
- `src/ui`: interface Streamlit com modos demonstrativo e real.
- `scripts`: migração, coleta OpenAlex, carga, embeddings e avaliação.
- `tests`: testes unitários do pipeline.

## Fluxo real

1. OpenAlex fornece publicações acadêmicas.
2. O loader normaliza registros e o parser/chunker cria documentos e chunks.
3. O Text-to-Graph cria `Paper`, `Author`, `Venue` e `Technology`.
4. O NER/RE cria `Entity`, `MENTIONS` e `RELATED_TO` a partir dos chunks.
5. A canonicalização reduz duplicidades de nomes.
6. Embeddings de 384 dimensões são persistidos em `Chunk`.
7. A busca híbrida combina vetor, full-text e `path_score` baseado em Shortest Path.
8. A resposta grounded expõe documentos, títulos, confiança, caminhos e Cypher real.
9. A UI mostra o subgrafo real interativo ou a amostra demonstrativa.

O projeto não usa LLM externo atualmente; a geração final é um template grounded adequado à demonstração acadêmica.
