from src.extraction.text_to_graph import extract_publication, validate_graph


def test_text_to_graph_matches_schema():
    graph = extract_publication({
        "id": "paper:1",
        "title": "GraphRAG",
        "authors": [{"id": "author:1", "name": "Ana"}],
        "venue": "DemoNLP",
        "topics": ["NLP", "GraphRAG"],
    })
    assert validate_graph(graph) == []
    assert len(graph.nodes) == 5
    assert len(graph.relationships) == 4
