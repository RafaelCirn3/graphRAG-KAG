# Avaliação experimental

## Conjunto de perguntas

As perguntas multi-hop estão em `data/evaluation/questions.jsonl` e os resultados executados em `data/evaluation/results.json`.

## Comparações executadas

1. Recuperação vetorial usando o índice de embeddings.
2. GraphRAG/KAG híbrido usando vetor, full-text e pontuação de caminho.

A comparação com LLM sem recuperação ainda não foi executada porque não há provedor ou modelo externo configurado. Foi criado um baseline sem recuperação e um formulário em `data/evaluation/human_evaluation_template.csv` para preenchimento pelos avaliadores.

## Métricas

- Recall operacional/hit: documentos retornados para cada pergunta;
- Grounding: existência de evidências e fontes;
- Recuperação: scores vetorial, full-text e caminho;
- Explicabilidade: Cypher, fontes e subgrafo retornados.

## Resultado atual

Foram avaliadas 4 perguntas com a amostra OpenAlex. O recall operacional foi de 100% para as estratégias vetorial e híbrida nesta amostra. Esse resultado não representa correção humana.

Embeddings: hashing determinístico local, dimensão 384. Geração: resposta grounded por template. Para a entrega final, recomenda-se avaliação humana de correção, relevância e completude.
