# Fontes, bibliotecas e licenças

## Dados

- OpenAlex API — metadados acadêmicos usados na amostra real. Consultado pelo script `scripts/fetch_openalex.py`. Verifique os termos atuais de uso e atribuição em <https://docs.openalex.org/>
- DBLP — fonte planejada para expansão, ainda não usada na execução atual: <https://dblp.org/>
- arXiv — fonte planejada para expansão de textos públicos, ainda não usada na execução atual: <https://arxiv.org/>

## Software e documentação

- Neo4j Community — banco de dados orientado a grafos: <https://neo4j.com/docs/>
- Neo4j Python Driver — acesso ao Neo4j: <https://neo4j.com/docs/python-manual/current/>
- Streamlit — interface visual: <https://docs.streamlit.io/>
- vis-network — visualização interativa carregada via CDN na UI: <https://visjs.github.io/vis-network/docs/network/>

## Implementação própria

- Embeddings locais por hashing determinístico em `src/retrieval/embeddings.py`.
- Canonicalização em `src/extraction/entity_resolution.py`.
- NER/RE baseado em padrões em `src/extraction/ner_re.py`.
- Text-to-Graph, recuperação híbrida, Shortest Path e geração grounded desenvolvidos para esta atividade.

Modelos externos e chamadas pagas de LLM não foram utilizados na execução atual. Qualquer adoção futura deve registrar modelo, versão, fornecedor, licença e configuração.
