import re
from neo4j import Query
from neo4j.exceptions import ClientError
from src.model import ask

EDGES = "ACTED_IN|DIRECTED|CREATED|HAS_GENRE|PRODUCED_BY"
PROMPT = """Write a single read-only Neo4j Cypher query for the Portuguese question.
Schema: (Person)-[:ACTED_IN|DIRECTED|CREATED]->(Movie or Series);
(Movie or Series)-[:HAS_GENRE]->(Genre), -[:PRODUCED_BY]->(Studio).
Person, Studio and Genre have name. Titles have title, id, year.
Return a title node's id AS document_id, and the requested name or title AS fact.
Use MATCH, optional WHERE, WITH and RETURN only, simple bounded typed edges.
Use $name for the exact anchor value. LIMIT 40. No procedures, comments or semicolons.
Example: MATCH (a:Person)-[:ACTED_IN]->(t:Movie)<-[:DIRECTED]-(b:Person)
WHERE a.name = $name RETURN t.id AS document_id, b.name AS fact LIMIT 40.
Return JSON with cypher and name."""
SCHEMA = {"type":"object","required":["cypher","name"],"properties":{
    "cypher":{"type":"string"},"name":{"type":"string"}}}


# Constrain decoding itself so a small model produces executable Cypher.
EDGE_PATTERN = "(ACTED_IN|DIRECTED|CREATED|HAS_GENRE|PRODUCED_BY)"
NODE_LABEL = "(Person|Studio|Genre|Series|Movie)"
STEP = r"-\[:" + EDGE_PATTERN + r"\]-"
SCHEMA["properties"]["cypher"]["pattern"] = (
    r"^MATCH \(a:" + NODE_LABEL + r"\)" + STEP + r"\(t(:Movie|:Series)?\)"
    + "(" + STEP + r"\(b(:Person|:Studio|:Genre|:Movie|:Series)?\))?"
    + r" WHERE a\.(name|title) = \$name RETURN (a|t|b)\.id AS document_id, "
    + r"(a|t|b)\.(name|title) AS fact LIMIT 40$"
)
PROMPT += " Use undirected typed edges and variables a, t, b as required by the grammar."

def generated_paths(session, question):
    feedback = ""
    for attempt in range(3):
        reply = ask(PROMPT, question + feedback, SCHEMA)
        query = reply["cypher"].strip()
        params = {"name": reply["name"]}
        try:
            if (len(query) > 1600 or not re.fullmatch(r"MATCH [A-Za-z0-9_$:.,()<>=%\[\]\s-]+ LIMIT (?:[1-9]|[1-3][0-9]|40)", " ".join(query.split()), re.I)
                or re.search(r"\b(CALL|CREATE|DELETE|DETACH|SET|REMOVE|MERGE|LOAD|FOREACH|USE|DROP|ALTER|UNION|SHOW|FINISH)\b|//|-->",query,re.I)):
                raise ValueError("Use a bounded read-only MATCH query ending in LIMIT 40")
            plan = session.run(Query("EXPLAIN " + query, timeout=3), params)
            if plan.consume().query_type != "r":
                raise ValueError("Return title.id AS document_id and requested value AS fact")
            records = session.run(Query(query, timeout=5),params)
            if not {"document_id","fact"}.issubset(records.keys()):
                raise ValueError("Expected aliases document_id and fact")
            rows = [dict(row) for row in records]
            return {"query":query,"parameters":params}, rows
        except (ValueError, ClientError) as error:
            feedback = f" Previous query: {query}. Correct this error: {error}"
    return {"error":feedback}, []


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

