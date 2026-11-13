from src.model import ask

EDGES = "ACTED_IN|DIRECTED|CREATED|HAS_GENRE|PRODUCED_BY"
LABELS = {"Person", "Movie", "Series", "Genre", "Studio"}


def generated_paths(session, question):
    schema = {"type": "object", "properties": {
        "anchor": {"type": "string", "enum": ["Person", "Studio", "Genre"]},
        "name": {"type": "string", "minLength": 1},
        "first_edge": {"type": "string", "enum": EDGES.split("|")},
        "second_edge": {"type": "string", "enum": EDGES.split("|")}},
        "required": ["anchor", "name", "first_edge", "second_edge"]}
    plan = ask("Choose the named anchor and both graph edges to answer the question. "
               "Person ACTED_IN, DIRECTED or CREATED a title; a title HAS_GENRE or "
               "was PRODUCED_BY a studio. Copy the anchor name exactly.", question, schema)
    if not isinstance(plan, dict) or any(
        plan.get(key) not in schema["properties"][key]["enum"]
        for key in ("anchor", "first_edge", "second_edge")
    ) or not isinstance(plan.get("name"), str) or not plan["name"].strip():
        raise ValueError("Invalid Ollama graph query plan")
    query = (f"MATCH p=(a:{plan['anchor']})-[:{plan['first_edge']}]-(t)"
             f"-[:{plan['second_edge']}]-(b) WHERE a.name = $name "
             "RETURN t.id AS document_id, [n IN nodes(p) | coalesce(n.name,n.title)] AS nodes, "
             "[r IN relationships(p) | type(r)] AS relationships LIMIT 40")
    return query, [dict(row) for row in session.run(query, name=plan["name"])]


def enrich(session):
    import networkx as nx
    graph = nx.Graph()
    for row in session.run(f"MATCH (a)-[:{EDGES}]->(b) RETURN a.id AS a,b.id AS b"):
        graph.add_edge(row["a"], row["b"])
    if not graph:
        return {}
    rank = nx.pagerank(graph)
    result = {}
    for community in nx.community.louvain_communities(graph, seed=42):
        titles = sorted((node for node in community if node.startswith(("movie:", "series:"))),
                        key=rank.get, reverse=True)
        for title in titles:
            result[title] = {"pagerank": rank[title], "related_titles": [t for t in titles if t != title][:3]}
    return result

