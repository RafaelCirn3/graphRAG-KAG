# Guia de desenvolvimento e reprodução

## Fluxo executado

1. Subir o Neo4j: `docker compose up -d`.
2. Aplicar migrações: `python -m scripts.migrate`.
3. Carregar documentos e chunks: `python -m scripts.load_sample --input data/raw/titles.json`.
4. Executar Text-to-Graph: `python -m scripts.run_text_to_graph --input data/raw/titles.json`.
5. Gerar embeddings: `python -m scripts.build_embeddings`.
6. Avaliar: `python -m scripts.evaluate`.
7. Iniciar UI: `streamlit run src/ui/app.py --server.port 8501`.

## Fluxo automatizado via Docker

`docker compose up --build` executa o Neo4j, espera o healthcheck, aplica migrações, carrega `data/raw/titles.json`, executa Text-to-Graph, gera embeddings, roda a avaliação e inicia o Streamlit na porta 8501.

## Validações atuais

- Catálogo com 9 títulos (5 filmes, 4 séries) validado pelo Text-to-Graph.
- 4 perguntas de avaliação.
- 8 testes automatizados aprovados.

## Convenções

- Não versionar `.env`, segredos ou dados privados.
- Atualizar `docs/schema.md` quando labels ou relações mudarem.
- Manter `uri` de referência em cada título.
- Usar os botões `Dados demonstrativos` e `Dados reais` na UI para separar o resumo local da consulta no Neo4j.
