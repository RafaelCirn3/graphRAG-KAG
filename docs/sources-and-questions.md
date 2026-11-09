# Fontes e perguntas de avaliação

## Fontes adotadas

- DBLP/OpenAlex: metadados de artigos, autores, venues, instituições e áreas.
- arXiv: resumos ou textos públicos de Computação, quando disponíveis.
- Documentação oficial do Neo4j e das bibliotecas usadas: apoio técnico da demonstração.

O recorte inicial é Inteligência Artificial, NLP, Knowledge Graphs, GraphRAG e KAG. A amostra deve permanecer pequena (aproximadamente 50–100 artigos) para manter a avaliação reproduzível.

## Perguntas multi-hop iniciais

1. Quais tecnologias aparecem em artigos escritos por autores que publicaram em uma conferência de NLP?
2. Quais áreas de pesquisa estão associadas a artigos escritos por autores afiliados a uma instituição?
3. Quais artigos sobre GraphRAG são citados por trabalhos que também discutem recuperação vetorial?
4. Quais instituições possuem autores que publicaram sobre GraphRAG em conferências de NLP e quais tecnologias aparecem nesses artigos?

As perguntas devem exigir pelo menos dois relacionamentos e retornar as evidências do caminho percorrido.
