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

As 4 perguntas foram reescritas para o catálogo de filmes e séries; rode `python -m scripts.evaluate` para gerar `data/evaluation/results.json` atualizado. O recall operacional não representa correção humana.

Embeddings: hashing determinístico local, dimensão 384. Geração: LLM local via Ollama (`qwen2.5:3b`) quando disponível; caso contrário, template grounded. Para a entrega final, recomenda-se avaliação humana de correção, relevância e completude.

## Experimento de alucinação (LLM sem recuperação × RAG vetorial × GraphRAG híbrido)

- Conjunto: `data/evaluation/questions_eval.jsonl` (17 perguntas: 1, 2 e 3 saltos, agregação e 4 sem resposta no catálogo). O gabarito é calculado de `data/raw/titles.json`; regere com `python -m scripts.build_eval_set`.
- Execução: `python -m scripts.evaluate_hallucination` (precisa de Neo4j carregado e Ollama). Saída em `data/evaluation/hallucination_results.json`.
- LLM externo: `python -m scripts.evaluate_hallucination --no-generate --answers respostas.json`, com `{"q1": {"gpt": "resposta"}, ...}`.
- Métricas: acerto, recall de entidades, alucinação (entidade fora do catálogo ou resposta confiante sem evidência) e abstenção correta. A alucinação é medida em relação ao catálogo, não ao mundo real, e a detecção de entidades é heurística; a avaliação humana complementa.
- Testes: `pytest tests/test_evaluation.py` (não precisam de Neo4j).
