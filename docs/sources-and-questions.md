# Fontes e perguntas de avaliação

## Fonte adotada

- OpenAlex: publicações, autores, instituições, venues, tópicos e identificadores persistentes.
- A amostra atual contém 20 publicações reais e seus metadados disponíveis.

DBLP e arXiv permanecem fontes possíveis para expansão, mas não são necessários para a execução atual.

## Perguntas com evidência disponível

As perguntas abaixo foram ajustadas ao grafo atualmente carregado. Todas possuem o termo `GraphRAG`, presente nos títulos ou resumos da amostra, e exigem pelo menos dois relacionamentos:

1. Quais tecnologias aparecem em artigos relacionados a GraphRAG?
2. Quais autores escreveram artigos relacionados a GraphRAG e quais tecnologias aparecem nesses artigos?
3. Quais venues publicaram artigos relacionados a GraphRAG e quais tecnologias esses artigos utilizam?
4. Quais instituições estão associadas a autores de artigos relacionados a GraphRAG?

Os caminhos esperados incluem combinações como:

```text
Author → WROTE → Paper → USES_TECHNOLOGY → Technology
Author → WROTE → Paper → PUBLISHED_AT → Venue
Author → AFFILIATED_WITH → Institution
```

Quando a fonte não fornece instituições, a quarta pergunta deve retornar ausência de evidência em vez de inventar uma resposta.
