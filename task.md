# Plano de execução — GraphRAG & KAG

## Fase 0 — Alinhamento e escopo (iniciada)

- [x] Formar equipe: Ewellyn Maria, Gustavo Palmeira, Rafael Cirne, Julliane Di Paula, Felipe Souto Mario e Arthur Xavier.
- [x] Definir responsabilidade compartilhada entre todos os integrantes.
- [x] Escolher domínio, fontes permitidas e perguntas multi-hop em `docs/sources-and-questions.md`.
- [x] Definir schema inicial em `docs/schema.md`.
- [x] Adotar os critérios de avaliação definidos no documento Word.
- [x] Confirmar escopo acadêmico, sem exigência de registro separado de decisões.

## Fase 1 — Ambiente e fundação (iniciada)

- [x] Criar manifesto Python, lint, testes e configuração por `.env`.
- [x] Criar ambiente Neo4j em `docker-compose.yml`.
- [x] Implementar migração inicial idempotente com constraints e índices obrigatórios.
- [x] Criar módulo de configuração e cliente Neo4j.
- [x] Subir Neo4j e validar conexão local.
- [x] Definir fontes acadêmicas e perguntas multi-hop iniciais em `docs/sources-and-questions.md`.
- [x] Criar dados de exemplo em `data/raw/publications.sample.jsonl`.
- [x] Criar loaders, parser e chunking determinísticos em `src/ingestion/`.
- [ ] Implementar carga dos documentos processados e metadados no Neo4j.
- [x] Criar UI Streamlit demonstrativa em `src/ui/app.py` com métricas de rastreabilidade e visualização do subgrafo.

## Fase 2 — Text-to-Graph

- [ ] Implementar NER e RE com saída estruturada e validação de schema.
- [ ] Implementar canonicalização/entity resolution e testes de duplicidade.
- [ ] Carregar documentos, chunks, entidades e relações no Neo4j.
- [ ] Validar amostras no Browser/Cypher e registrar erros conhecidos.

## Fase 3 — Recuperação e geração

- [ ] Gerar embeddings e configurar busca vetorial.
- [ ] Implementar consultas Cypher por entidade, vizinhança e caminhos de 2+ hops.
- [ ] Implementar fusão/ranking da recuperação híbrida.
- [ ] Adicionar PageRank, comunidades ou shortest path ao contexto.
- [ ] Criar prompt de grounding e resposta estruturada com evidências, Cypher e confiança.

## Fase 4 — Interface e avaliação

- [ ] Criar UI funcional para pergunta, resposta e métricas de rastreabilidade.
- [ ] Renderizar o subgrafo retornado com nós e relacionamentos destacados.
- [ ] Executar testes unitários, integração e fluxo end-to-end.
- [ ] Comparar baseline, RAG vetorial e GraphRAG/KAG conforme `docs/evaluation.md`.
- [ ] Corrigir falhas de grounding, latência e duplicidade.

## Fase 5 — Entrega e defesa

- [ ] Finalizar README com instalação, execução, arquitetura e limitações.
- [ ] Atualizar diagramas, referências, evidências e instruções de deployment.
- [ ] Revisar licenças, atribuições, segredos e reprodutibilidade.
- [ ] Preparar demonstração: pergunta multi-hop, Cypher, caminho, subgrafo e confiança.
- [ ] Fazer revisão final do repositório e ensaio da defesa.
