# Requisitos e critérios de aceite

## Requisitos funcionais

1. Ingerir documentos não estruturados e produzir entidades e relações.
2. Canonicalizar entidades equivalentes e evitar nós duplicados.
3. Persistir um LPG no Neo4j com labels, propriedades e tipos de relação documentados.
4. Expor busca vetorial e consultas Cypher estruturadas em um fluxo híbrido.
5. Responder perguntas que exijam no mínimo dois saltos.
6. Enriquecer o contexto com PageRank, comunidades ou shortest path.
7. Exibir resposta, fontes/caminhos, nós consultados, Cypher e confiança.
8. Renderizar interativamente o subgrafo usado na resposta.

## Contexto de avaliação

Este repositório atende exclusivamente à atividade final da disciplina. O objetivo é demonstrar os requisitos técnicos definidos no documento Word, não construir um produto de produção. O schema e as decisões de modelagem podem ser mantidos em Markdown; não é necessário manter um registro separado de decisões.

## Requisitos não funcionais

- Reprodução local documentada e configuração por variáveis de ambiente.
- Testes unitários, integração com Neo4j e avaliação com perguntas de referência.
- Rastreabilidade: cada afirmação deve apontar para documentos e caminhos do grafo.
- Código e dependências com atribuição/licença registrada.

## Critérios de aceite

- Pipeline completo executa do documento à resposta sem intervenção manual.
- Constraints e índices são aplicados por migração idempotente.
- Há evidência de consulta multi-hop e comparação entre baseline vetorial e híbrido.
- UI permite inspecionar o contexto recuperado e a consulta executada.
- README permite reproduzir o ambiente.
