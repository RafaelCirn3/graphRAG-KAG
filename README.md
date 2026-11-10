# GraphRAG & KAG em Ciência da Computação

Projeto acadêmico de avaliação da disciplina Tendências em Ciência da Computação. O sistema demonstra recuperação aumentada por grafos para responder perguntas com contexto verificável, combinando extração de conhecimento, Neo4j, busca vetorial, Cypher e visualização do subgrafo utilizado.

## Equipe

Ewellyn Maria, Gustavo Palmeira, Rafael Cirne, Julliane Di Paula, Felipe Souto Mario e Arthur Xavier.

A responsabilidade é compartilhada por todos os integrantes. A equipe informada possui seis membros, dentro da faixa de 4 a 6 alunos indicada no documento-base.

## Escopo

- Text-to-Graph: ingestão de documentos, NER, RE e resolução de entidades.
- Neo4j LPG: modelo versionado, constraints, índices BTREE/full-text/vector.
- Recuperação híbrida: similaridade vetorial + Cypher + travessia multi-hop (mínimo de 2 saltos).
- UI: resposta fundamentada, Cypher gerado, nós/relacionamentos recuperados, confiança e subgrafo interativo.

## Estrutura

Consulte [`docs/architecture.md`](docs/architecture.md), [`docs/schema.md`](docs/schema.md) e [`task.md`](task.md).

## Execução local

1. Copie `.env.example` para `.env` e ajuste as credenciais do Neo4j.
2. Suba o Neo4j com `docker compose up -d`.
3. Instale as dependências definidas em `pyproject.toml`.
4. Execute a migração: `python -m scripts.migrate`.
5. Baixe os dados reais: `python -m scripts.fetch_openalex`.
6. Carregue documentos/chunks: `python -m scripts.load_sample --input data/raw/openalex_publications.jsonl --source openalex`.
7. Execute Text-to-Graph: `python -m scripts.run_text_to_graph --input data/raw/openalex_publications.jsonl --source openalex`.
8. Gere embeddings: `python -m scripts.build_embeddings`.
9. Rode a avaliação: `python -m scripts.evaluate`.
10. Inicie a UI: `streamlit run src/ui/app.py --server.port 8501`.

Na UI, use os botões **Dados demonstrativos** e **Dados reais** para alternar entre a amostra local e o Neo4j com dados do OpenAlex.

## Execução completa via Docker

Esta é a forma recomendada para a apresentação. O Compose executa automaticamente:

1. Neo4j e healthcheck;
2. Migrações e índices;
3. Download de 20 publicações do OpenAlex;
4. Carga de documentos e chunks;
5. Text-to-Graph;
6. Embeddings;
7. Avaliação;
8. Streamlit.

O bootstrap usa o arquivo OpenAlex já existente como cache. Se a API estiver temporariamente limitada (`HTTP 429`), ele tenta novamente e usa a amostra acadêmica local como fallback para não bloquear a demonstração.

Pré-requisitos: Docker Desktop com Compose ativo.

```bash
docker compose up --build
```

Depois acesse:

<http://localhost:8501>

Para executar em segundo plano:

```bash
docker compose up --build -d
```

Para acompanhar a preparação:

```bash
docker compose logs -f bootstrap
```

Para encerrar os serviços:

```bash
docker compose down
```

Os dados do Neo4j permanecem no volume Docker `neo4j_data`. Para apagar também os dados persistidos, use `docker compose down -v`.

## Estado atual

O fluxo implementado é: fonte → documento/chunk → Text-to-Graph → NER/RE → Neo4j → embeddings → recuperação híbrida → Shortest Path → resposta grounded → UI interativa → avaliação.

As limitações acadêmicas atuais estão registradas em [`docs/evaluation.md`](docs/evaluation.md).

## Integridade acadêmica

Bibliotecas, modelos, datasets e trechos de código externos devem ser registrados em `docs/references.md`, com atribuição e licença.
