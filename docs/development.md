# Guia de desenvolvimento

## Convenções

- Python tipado, lint/format automático e funções pequenas por camada.
- Commits focados e branches por tarefa.
- Nenhum segredo ou documento privado no Git.
- Toda alteração de schema acompanha migração, teste e atualização da documentação.

## Fluxo recomendado

1. Definir domínio, fontes e schema mínimo.
2. Implementar e testar ingestão/extracão isoladamente.
3. Validar carga e consultas diretamente no Neo4j.
4. Integrar recuperação híbrida antes de conectar a UI.
5. Medir baseline e GraphRAG/KAG com o mesmo conjunto de perguntas.
