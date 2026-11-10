# Guia de desenvolvimento e reprodução

## Fluxo executado

1. Subir o Neo4j: `docker compose up -d`.
2. Aplicar migrações: `python -m scripts.migrate`.
3. Baixar dados reais: `python -m scripts.fetch_openalex`.
4. Carregar documentos e chunks: `python -m scripts.load_sample --input data/raw/openalex_publications.jsonl --source openalex`.
5. Executar Text-to-Graph: `python -m scripts.run_text_to_graph --input data/raw/openalex_publications.jsonl --source openalex`.
6. Gerar embeddings: `python -m scripts.build_embeddings`.
7. Avaliar: `python -m scripts.evaluate`.
8. Iniciar UI: `streamlit run src/ui/app.py --server.port 8501`.

## Fluxo automatizado via Docker

`docker compose up --build` executa o Neo4j, espera o healthcheck, aplica migrações, baixa OpenAlex, carrega os dados, executa Text-to-Graph, gera embeddings, roda a avaliação e inicia o Streamlit na porta 8501.

## Validações atuais

- Neo4j ativo com constraints, BTREE, full-text e vector online.
- 20 publicações reais do OpenAlex importadas.
- 60 chunks reais carregados.
- 158 nós Text-to-Graph processados na amostra OpenAlex.
- 4 perguntas avaliadas.
- 7 testes automatizados aprovados.

## Convenções

- Não versionar `.env`, segredos ou dados privados.
- Atualizar `docs/schema.md` quando labels ou relações mudarem.
- Manter fonte e URI nos dados acadêmicos.
- Usar os botões `Dados demonstrativos` e `Dados reais` na UI para separar a amostra local da base OpenAlex.
