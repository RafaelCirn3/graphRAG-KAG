from src.extraction.entity_resolution import canonical_id, deduplicate_names, normalize_name


def test_entity_names_are_canonicalized():
    assert normalize_name("  Graph-RÁG  ") == "graph rag"
    assert canonical_id("technology", "Graph RAG") == "technology:graph-rag"
    assert deduplicate_names(["NLP", "nlp", "N.L.P."]) == ["NLP"]
