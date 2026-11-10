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

- [x] Normalizar maiúsculas, acentos, abreviações e aliases.
- [x] Gerar IDs estáveis para autores, artigos, venues e tecnologias.
- [x] Evitar duplicidade de nomes equivalentes dentro da mesma publicação.
- [x] Criar testes para entidades equivalentes.
- [ ] Unificar entidades entre múltiplas fontes após importar DBLP/arXiv.

**Saída:** um único nó por entidade equivalente.

### 4. Dados acadêmicos reais

- [x] Importar uma amostra controlada de 20 artigos do OpenAlex.
- [x] Priorizar IA, NLP, Knowledge Graphs, GraphRAG e KAG.
- [x] Registrar fonte, URI e metadados de cada publicação.
- [x] Reexecutar a carga e validar a qualidade do grafo.
- [ ] Ampliar para DBLP/arXiv se necessário para aumentar as relações de citação.

**Saída:** base suficiente para a demonstração e avaliação.

### 5. Embeddings e busca vetorial

- [x] Escolher embeddings locais determinísticos compatíveis com dimensão 384 para a avaliação acadêmica.
- [x] Gerar embeddings para chunks.
- [x] Persistir os vetores no Neo4j.
- [x] Testar a busca pelo índice vetorial.

**Saída:** recuperação semântica funcionando.

### 6. Recuperação híbrida e multi-hop

- [x] Implementar busca vetorial por pergunta.
- [x] Implementar busca full-text e filtros Cypher.
- [x] Implementar expansão estruturada dos chunks relacionados.
- [x] Combinar resultados vetoriais e full-text como recuperação híbrida inicial.
- [x] Garantir que os resultados carreguem documentos e evidências.

**Saída:** contexto composto por similaridade semântica e estrutura do grafo.

### 7. Algoritmo de grafo

- [x] Implementar Shortest Path para explicar caminhos recuperados.
- [x] Limitar o caminho demonstrativo a até 6 hops.
- [ ] Incorporar o caminho à pontuação final da recuperação.

**Saída:** requisito de enriquecimento por algoritmo de grafo atendido.

### 8. Geração grounded

- [x] Criar geração grounded estruturada usando apenas evidências recuperadas.
- [x] Gerar resposta com fontes e títulos dos documentos.
- [x] Calcular confiança demonstrativa com critério explícito.
- [x] Retornar resposta estruturada com `answer`, `confidence`, `sources`, `evidence_titles`, `grounded` e `cypher`.
- [ ] Conectar um LLM externo para geração linguística final, se desejado.

**Saída:** resposta rastreável e fundamentada.

### 9. Integração da UI real

- [x] Substituir a resposta simulada da UI por consulta ao pipeline real.
- [x] Exibir a pergunta, resposta, fontes, confiança e scores da recuperação.
- [x] Incorporar a pontuação do caminho ao ranking híbrido.
- [x] Criar botões `Dados demonstrativos` e `Dados reais`.
- [x] Renderizar os nós e relacionamentos reais recuperados pelo Neo4j.

**Saída:** demonstração visual completa dos quatro pilares.

### 10. Avaliação comparativa

- [x] Executar as perguntas de `data/evaluation/questions.jsonl`.
- [x] Comparar baseline vetorial e recuperação híbrida GraphRAG/KAG.
- [x] Medir hit operacional, grounding, scores e rastreabilidade.
- [x] Registrar resultados em `data/evaluation/results.json`.
- [ ] Comparar também com LLM sem recuperação e avaliação humana de correção/relevância.

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
