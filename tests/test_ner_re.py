from src.extraction.ner_re import extract_entities_and_relations


def test_ner_re_extracts_known_entities():
    result = extract_entities_and_relations("Uma história de vingança no crime organizado")
    assert {mention.name for mention in result.mentions} >= {"vingança", "crime organizado"}
    assert result.relations
