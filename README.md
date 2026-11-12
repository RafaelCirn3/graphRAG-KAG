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
5. Carregue documentos/chunks: `python -m scripts.load_sample --input data/raw/titles.json`.
6. Execute Text-to-Graph: `python -m scripts.run_text_to_graph --input data/raw/titles.json`.
7. Gere embeddings: `python -m scripts.build_embeddings`.
8. Rode a avaliação: `python -m scripts.evaluate`.
9. Inicie a UI: `streamlit run src/ui/app.py --server.port 8501`.

Os dados ficam em `data/raw/titles.json` (filmes e séries). O formato de cada título está em [`docs/sources-and-questions.md`](docs/sources-and-questions.md). Para adicionar títulos, edite esse arquivo e rode o pipeline de novo.

Na UI, use os botões **Dados demonstrativos** e **Dados reais** para alternar entre o resumo do catálogo local e a consulta no Neo4j.

## Execução completa via Docker

Esta é a forma recomendada para a apresentação. O Compose executa automaticamente:

1. Neo4j e healthcheck;
2. Migrações e índices;
3. Carga de documentos e chunks;
4. Text-to-Graph;
5. Embeddings;
6. Avaliação;
7. Streamlit.


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

O compose também sobe o Ollama (LLM local e gratuito). Na primeira execução o serviço `ollama-pull` baixa o modelo `qwen2.5:3b` (~2 GB), acompanhe com `docker compose logs -f ollama-pull`. O modelo fica no volume `ollama_data`; troque-o com `LLM_MODEL=<modelo> docker compose up`.

Os dados do Neo4j permanecem no volume Docker `neo4j_data`. Para apagar também os dados persistidos, use `docker compose down -v`.

## Estado atual

O fluxo implementado é: fonte → documento/chunk → Text-to-Graph → NER/RE → Neo4j → embeddings → recuperação híbrida → Shortest Path → resposta grounded → UI interativa → avaliação.

As limitações acadêmicas atuais estão registradas em [`docs/evaluation.md`](docs/evaluation.md).

## Integridade acadêmica

Bibliotecas, modelos, datasets e trechos de código externos devem ser registrados em `docs/references.md`, com atribuição e licença.
