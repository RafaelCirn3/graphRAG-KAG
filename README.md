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

## Execução local (planejada)

1. Copie `.env.example` para `.env` e preencha as credenciais do LLM/Neo4j.
2. Suba o Neo4j com `docker compose up -d`.
3. Instale as dependências definidas em `pyproject.toml`.
4. Execute as migrações/seeds e depois a UI conforme instruções que serão adicionadas em `docs/development.md`.

Para iniciar a demonstração visual: `streamlit run src/ui/app.py`.

## Integridade acadêmica

Bibliotecas, modelos, datasets e trechos de código externos devem ser registrados em `docs/references.md`, com atribuição e licença.
