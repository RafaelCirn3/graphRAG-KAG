# Fontes, bibliotecas e licenças

## Dados

- `data/raw/titles.json` — catálogo de filmes e séries montado pela equipe. Sinopses escritas pela equipe; diretores, elenco, gêneros e estúdios conferidos nas páginas da Wikipedia indicadas no campo `uri` de cada título (conteúdo CC BY-SA 4.0): <https://en.wikipedia.org/>

## Software e documentação

- Neo4j Community — banco de dados orientado a grafos: <https://neo4j.com/docs/>
- Neo4j Python Driver — acesso ao Neo4j: <https://neo4j.com/docs/python-manual/current/>
- Streamlit — interface visual: <https://docs.streamlit.io/>
- Ollama — execução local de LLMs (MIT): <https://github.com/ollama/ollama>
- vis-network — visualização interativa carregada via CDN na UI: <https://visjs.github.io/vis-network/docs/network/>

## Implementação própria

- Embeddings locais por hashing determinístico em `src/retrieval/embeddings.py`.
- Canonicalização em `src/extraction/entity_resolution.py`.
- NER/RE baseado em padrões em `src/extraction/ner_re.py`.
- Text-to-Graph, recuperação híbrida, Shortest Path e geração grounded desenvolvidos para esta atividade.

## Modelos externos

- Qwen2.5 3B (Alibaba, licença Qwen Research) executado localmente via Ollama — geração da resposta final; configurável em `LLM_MODEL`: <https://ollama.com/library/qwen2.5>
