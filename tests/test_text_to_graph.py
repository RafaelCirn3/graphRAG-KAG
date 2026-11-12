from src.extraction.text_to_graph import extract_title, validate_graph


def test_text_to_graph_matches_schema():
    graph = extract_title({
        "id": "movie:1",
        "type": "movie",
        "title": "Filme Teste",
        "creators": ["Diretora"],
        "cast": ["Ator"],
        "genres": ["Drama"],
        "studio": "Estúdio",
    })
    assert validate_graph(graph) == []
    assert len(graph.nodes) == 5
    assert {r.relationship for r in graph.relationships} == {"DIRECTED", "ACTED_IN", "HAS_GENRE", "PRODUCED_BY"}
