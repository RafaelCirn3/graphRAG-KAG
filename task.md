# Plano de conclusão — GraphRAG & KAG

Projeto acadêmico para avaliação da disciplina Tendências em Ciência da Computação.
Responsabilidade compartilhada entre Ewellyn Maria, Gustavo Palmeira, Rafael Cirne,
Julliane Di Paula, Felipe Souto Mario e Arthur Xavier.

## Estado atual

### Concluído

- [x] Escopo acadêmico definido conforme o documento Word.
- [x] Domínio definido: publicações de Ciência da Computação, IA, NLP, Knowledge Graphs, GraphRAG e KAG.
- [x] Fontes e perguntas multi-hop definidas em `docs/sources-and-questions.md`.
- [x] Schema inicial documentado em `docs/schema.md`.
- [x] Estrutura simplificada do repositório criada.
- [x] Ambiente Python configurado em `pyproject.toml`.
- [x] Neo4j configurado em `docker-compose.yml` e validado localmente.
- [x] Constraints e índices BTREE, full-text e vector criados no Neo4j.
- [x] Loader JSONL, parser e chunker determinístico implementados em `src/ingestion/`.
- [x] Dataset de exemplo criado em `data/raw/publications.sample.jsonl`.
- [x] Perguntas de avaliação criadas em `data/evaluation/questions.jsonl`.
- [x] UI Streamlit demonstrativa criada em `src/ui/app.py`.
- [x] Testes básicos de configuração e ingestão aprovados.

### Demonstrado, mas ainda não integrado

- [ ] A UI consulta o Neo4j para gerar respostas reais.
- [ ] O subgrafo exibido na UI é derivado dos resultados reais.
- [ ] A confiança exibida é calculada por métricas reais.
- [ ] A resposta final é gerada por LLM usando contexto recuperado.

## Ordem obrigatória de implementação restante

### 1. Carga dos documentos no Neo4j

- [x] Criar o carregador de `Document` e `Chunk` usando o pipeline existente.
- [x] Persistir `(Document)-[:HAS_CHUNK]->(Chunk)`.
- [x] Persistir título, resumo, ano, URI, fonte e checksum.
- [x] Validar a carga com consultas Cypher.

**Saída:** documentos e chunks disponíveis no Neo4j.

### 2. Text-to-Graph

- [x] Extrair artigos, autores, venues e tecnologias a partir dos metadados normalizados.
- [x] Criar relações `WROTE`, `PUBLISHED_AT` e `USES_TECHNOLOGY`.
- [x] Validar a saída com o schema de `docs/schema.md`.
- [x] Criar testes para entidades e relações extraídas.
- [x] Persistir o resultado Text-to-Graph no Neo4j.
- [ ] Adicionar instituições, áreas de pesquisa e citações quando essas informações existirem na fonte real.

**Saída:** grafo de conhecimento navegável a partir dos documentos.

### 3. Resolução e canonicalização de entidades

- [ ] Normalizar maiúsculas, acentos, abreviações e aliases.
- [ ] Gerar IDs estáveis para autores, artigos, instituições e tecnologias.
- [ ] Evitar duplicidade entre registros de DBLP, OpenAlex e arXiv.
- [ ] Criar testes para entidades equivalentes.

**Saída:** um único nó por entidade equivalente.

### 4. Dados acadêmicos reais

- [ ] Importar uma amostra controlada de aproximadamente 50–100 artigos.
- [ ] Priorizar IA, NLP, Knowledge Graphs, GraphRAG e KAG.
- [ ] Registrar fonte, URI e atribuição de cada conjunto de dados.
- [ ] Reexecutar a carga e validar a qualidade do grafo.

**Saída:** base suficiente para a demonstração e avaliação.

### 5. Embeddings e busca vetorial

- [ ] Escolher um modelo de embeddings compatível com dimensão 384.
- [ ] Gerar embeddings para chunks e, se necessário, entidades.
- [ ] Persistir os vetores no Neo4j.
- [ ] Testar o índice vetorial com consultas de similaridade.

**Saída:** recuperação semântica funcionando.

### 6. Recuperação híbrida e multi-hop

- [ ] Implementar busca vetorial por pergunta.
- [ ] Implementar busca full-text e filtros Cypher.
- [ ] Implementar travessias com pelo menos 2 hops.
- [ ] Combinar os resultados em um ranking híbrido.
- [ ] Garantir que cada resultado carregue fontes e evidências.

**Saída:** contexto composto por similaridade semântica e estrutura do grafo.

### 7. Algoritmo de grafo

- [ ] Implementar pelo menos um algoritmo: Shortest Path, PageRank ou Community Detection.
- [ ] Preferencialmente começar por Shortest Path para explicar os caminhos recuperados.
- [ ] Incorporar o resultado ao contexto ou à pontuação dos resultados.

**Saída:** requisito de enriquecimento por algoritmo de grafo atendido.

### 8. Geração grounded

- [ ] Criar prompt que aceite apenas contexto recuperado.
- [ ] Gerar resposta com citações, fontes e caminho do grafo.
- [ ] Calcular ou estimar confiança com critérios explícitos.
- [ ] Retornar resposta estruturada com `answer`, `confidence`, `sources`, `nodes`, `relationships` e `cypher`.

**Saída:** resposta rastreável e fundamentada.

### 9. Integração da UI real

- [ ] Substituir a resposta simulada da UI por consulta ao pipeline real.
- [ ] Exibir a pergunta, resposta, Cypher, fontes, confiança e caminho real.
- [ ] Renderizar os nós e relacionamentos retornados pelo Neo4j.
- [ ] Informar quando o sistema estiver usando dados de exemplo ou dados reais.

**Saída:** demonstração visual completa dos quatro pilares.

### 10. Avaliação comparativa

- [ ] Executar as perguntas de `data/evaluation/questions.jsonl`.
- [ ] Comparar LLM sem recuperação, RAG vetorial e GraphRAG/KAG.
- [ ] Medir correção, relevância, grounding, multi-hop, latência e rastreabilidade.
- [ ] Registrar resultados em `docs/evaluation.md`.

**Saída:** evidência objetiva do funcionamento e dos benefícios do grafo.

### 11. Entrega e defesa

- [ ] Atualizar README com instalação, execução, arquitetura e limitações.
- [ ] Revisar schema, referências, licenças e atribuições.
- [ ] Testar reprodução do ambiente a partir de um clone limpo.
- [ ] Preparar demonstração com uma pergunta multi-hop real.
- [ ] Mostrar durante a defesa: pergunta, Cypher, caminho, subgrafo, fontes e confiança.
- [ ] Executar revisão final do repositório e ensaio da apresentação.

**Critério de conclusão:** todas as etapas obrigatórias acima marcadas como concluídas,
com o fluxo funcionando de ponta a ponta:

```text
Fonte → documento → chunk → entidades/relações → Neo4j
→ recuperação híbrida → multi-hop → contexto grounded → UI → avaliação
```
