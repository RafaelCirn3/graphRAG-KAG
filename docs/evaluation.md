# Avaliação experimental

## Conjunto de perguntas

Manter perguntas, resposta esperada, evidências esperadas e necessidade de hops em `data/evaluation/questions.jsonl`.

## Comparações mínimas

1. LLM sem recuperação.
2. RAG vetorial.
3. GraphRAG/KAG híbrido.

## Métricas

- qualidade: correção, relevância e completude;
- grounding: precisão das citações e suporte das afirmações;
- recuperação: Recall@k/MRR quando houver ground truth;
- operação: latência, custo e taxa de falha;
- explicabilidade: presença de Cypher, caminhos e subgrafo.

Registrar configuração, modelo, versão do dataset e resultados reproduzíveis.
