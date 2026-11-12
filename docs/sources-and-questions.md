# Fontes e perguntas de avaliação

## Fonte adotada

- `data/raw/titles.json`: catálogo local de filmes e séries mantido pela equipe.
- Cada título tem `uri` apontando para a página de referência na Wikipedia, usada como fonte rastreável.

### Formato de cada título

```json
{
  "id": "movie:the-matrix",
  "type": "movie",
  "title": "The Matrix",
  "year": 1999,
  "synopsis": "Texto curto usado nos chunks, embeddings e NER.",
  "creators": ["Lana Wachowski", "Lilly Wachowski"],
  "cast": ["Keanu Reeves"],
  "genres": ["Ficção científica"],
  "studio": "Warner Bros.",
  "uri": "https://en.wikipedia.org/wiki/The_Matrix"
}
```

`type` deve ser `movie` ou `series`. Em filmes, `creators` vira `DIRECTED`; em séries, vira `CREATED`.

## Perguntas com evidência disponível

1. Em quais filmes Keanu Reeves atuou e quem dirigiu esses filmes?
2. Quais filmes foram dirigidos por Christopher Nolan e quais estúdios os produziram?
3. Quais séries foram criadas por Vince Gilligan e quais atores aparecem nelas?
4. Quais séries da Netflix envolvem viagem no tempo e quem as criou?

Os caminhos esperados incluem:

```text
Person → ACTED_IN → Movie ← DIRECTED ← Person
Person → DIRECTED → Movie → PRODUCED_BY → Studio
Person → CREATED → Series ← ACTED_IN ← Person
Studio ← PRODUCED_BY ← Series ← CREATED ← Person
```
