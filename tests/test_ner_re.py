from src.extraction.ner_re import extract_entities_and_relations


def test_ner_re_extracts_known_entities():
    result = extract_entities_and_relations("GraphRAG usa Neo4j e Python para NLP")
    assert {mention.name for mention in result.mentions} >= {"GraphRAG", "Neo4j", "Python", "NLP"}
    assert result.relations
