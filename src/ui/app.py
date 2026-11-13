"""Interface visual demonstrativa do projeto acadêmico GraphRAG/KAG."""

import json
import streamlit as st
import streamlit.components.v1 as components

from src.config import settings
from src.generation.grounded import grounded_answer
from src.ingestion.loaders import load_json, normalize_title
from src.retrieval.hybrid import hybrid_search


st.set_page_config(page_title="GraphRAG & KAG — Demonstração", page_icon="🕸️", layout="wide")


def load_sample_data() -> list[dict]:
    return [normalize_title(record) for record in load_json("data/raw/titles.json")]


def neo4j_status() -> tuple[str, dict[str, int]]:
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
        driver.verify_connectivity()
        with driver.session() as session:
            rows = session.run("""
                MATCH (n)
                WITH labels(n) AS labels, count(n) AS total
                UNWIND labels AS label
                RETURN label, sum(total) AS total ORDER BY label
            """)
            result = {row["label"]: row["total"] for row in rows}
        driver.close()
        return "Conectado", result
    except Exception:
        return "Modo demonstrativo", {}


def build_demo_result(question: str, records: list[dict]) -> dict:
    people = sorted({name for r in records for name in r["creators"] + r["cast"]})
    studios = sorted({r["studio"] for r in records if r.get("studio")})
    genres = sorted({g for r in records for g in r["genres"]})
    cypher = """MATCH (actor:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(t:Movie)
MATCH (director:Person)-[:DIRECTED]->(t), (t)-[:PRODUCED_BY]->(s:Studio)
RETURN actor, t, director, s LIMIT 25"""
    return {
        "answer": f"Demonstração para: {question}\n\nO catálogo contém {len(records)} títulos, {len(people)} pessoas, {len(studios)} estúdios/canais e {len(genres)} gêneros.",
        "cypher": cypher,
        "people": people,
        "studios": studios,
        "genres": genres,
    }


def graph_for_documents(driver, document_ids: list[str]) -> str:
    if not document_ids:
        return "digraph G { empty [label=\"Nenhum subgrafo recuperado\"]; }"
    query = """
    MATCH (p)-[r]-(neighbor)
    WHERE (p:Movie OR p:Series) AND p.id IN $document_ids
    RETURN p.id AS source_id, labels(p)[0] AS source_type,
           coalesce(p.title, p.name, p.id) AS source_name,
           type(r) AS relationship,
           neighbor.id AS target_id, labels(neighbor)[0] AS target_type,
           coalesce(neighbor.title, neighbor.name, neighbor.id) AS target_name
    LIMIT 40
    """
    rows = driver.execute_query(query, document_ids=document_ids).records
    lines = ["digraph G {", "rankdir=LR;"]
    rendered_nodes: set[str] = set()
    colors = {
        "Movie": "#DCEBFF",
        "Series": "#E0F7FA",
        "Person": "#E6F4EA",
        "Genre": "#FFF4CC",
        "Studio": "#F3E8FF",
    }
    for row in rows:
        source = str(row["source_id"]).replace('"', "'")
        target = str(row["target_id"]).replace('"', "'")
        source_name = str(row["source_name"]).replace('"', "'").replace("\n", " ")
        target_name = str(row["target_name"]).replace('"', "'").replace("\n", " ")
        source_type = str(row["source_type"])
        target_type = str(row["target_type"])
        relationship = str(row["relationship"]).replace('"', "'")
        if source not in rendered_nodes:
            lines.append(f'"{source}" [label="{source_type}: {source_name}", fillcolor="{colors.get(source_type, "#EEEEEE")}"];')
            rendered_nodes.add(source)
        if target not in rendered_nodes:
            lines.append(f'"{target}" [label="{target_type}: {target_name}", fillcolor="{colors.get(target_type, "#EEEEEE")}"];')
            rendered_nodes.add(target)
        lines.append(f'"{source}" -> "{target}" [label="{relationship}"];')
    lines.insert(1, "node [shape=box, style=filled, fontname=Arial];")
    lines.append("}")
    return "\n".join(lines)


def interactive_graph(driver, document_ids: list[str]) -> None:
    query = """
    MATCH (p)-[r]-(neighbor)
    WHERE (p:Movie OR p:Series) AND p.id IN $document_ids
    RETURN p.id AS source_id, coalesce(p.title, p.name, p.id) AS source_name,
           labels(p)[0] AS source_type, type(r) AS relationship,
           neighbor.id AS target_id, coalesce(neighbor.title, neighbor.name, neighbor.id) AS target_name,
           labels(neighbor)[0] AS target_type LIMIT 40
    """
    rows = driver.execute_query(query, document_ids=document_ids).records
    nodes = {}
    edges = []
    type_colors = {
        "Movie": "#5B9BF3",
        "Series": "#2EC4D6",
        "Person": "#6EDB45",
        "Genre": "#FFD43B",
        "Studio": "#B889F4",
        "Entity": "#A7B0BE",
    }
    for row in rows:
        for node_id, name, node_type in [
            (row["source_id"], row["source_name"], row["source_type"]),
            (row["target_id"], row["target_name"], row["target_type"]),
        ]:
            short_name = str(name)
            if len(short_name) > 22:
                short_name = short_name[:19] + "..."
            nodes[node_id] = {
                "id": node_id,
                "label": short_name,
                "title": f"{node_type}: {name}",
                "group": node_type,
                "shape": "dot",
                "size": 24 if node_type in {"Movie", "Series"} else 18,
                "color": type_colors.get(node_type, "#A7B0BE"),
                "font": {"color": "#FFFFFF", "size": 14, "face": "Arial"},
            }
        edges.append({"from": row["source_id"], "to": row["target_id"], "label": row["relationship"], "arrows": "to"})
    payload = json.dumps({"nodes": list(nodes.values()), "edges": edges}, ensure_ascii=False)
    return f"""
    <div id="graph" style="height:560px;border:1px solid #ddd;border-radius:8px;"></div>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script>
      const data = {payload};
      const container = document.getElementById('graph');
      const options = {{
        interaction: {{hover: true, navigationButtons: true, tooltipDelay: 120}},
        physics: {{stabilization: {{iterations: 180}}, barnesHut: {{gravitationalConstant: -4200, springLength: 170}}}},
        nodes: {{shape: 'dot', borderWidth: 2, shadow: true}},
        edges: {{smooth: {{type: 'dynamic'}}, color: '#AAB4C3', font: {{color: '#E7ECF2', size: 11, strokeWidth: 3, strokeColor: '#111827'}}}}
      }};
      new vis.Network(container, {{nodes: new vis.DataSet(data.nodes), edges: new vis.DataSet(data.edges)}}, options);
    </script>
    """


st.title("🕸️ GraphRAG & KAG")
st.caption("Atividade final de Tendências em Ciência da Computação | Busca híbrida e rastreabilidade")

if "data_mode" not in st.session_state:
    st.session_state.data_mode = "demonstrativo"
mode_demo, mode_real = st.columns(2)
if mode_demo.button("Dados demonstrativos", use_container_width=True):
    st.session_state.data_mode = "demonstrativo"
if mode_real.button("Dados reais", use_container_width=True):
    st.session_state.data_mode = "real"
st.info(f"Modo ativo: **{'Dados reais (catálogo + Neo4j)' if st.session_state.data_mode == 'real' else 'Dados demonstrativos (amostra local)'}**")

status, counts = neo4j_status()
records = load_sample_data()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Neo4j", status)
col2.metric("Títulos no catálogo", len(records))
col3.metric("Chunks", counts.get("Chunk", "—"))
col4.metric("Entidades", counts.get("Entity", "—"))

question = st.text_area("Pergunta multi-hop", "Em quais filmes Keanu Reeves atuou e quem dirigiu esses filmes?")

if st.button("Executar consulta", type="primary"):
    if st.session_state.data_mode == "real":
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
        try:
            with st.spinner("Recuperando evidências e gerando a resposta com o LLM (pode levar ~40 s na CPU)..."):
                results = hybrid_search(driver, question, limit=5)
                executed_cypher = results[0].get("executed_cypher", {}) if results else {}
                result = grounded_answer(question, results, cypher=json.dumps(executed_cypher, ensure_ascii=False, indent=2))
            graph_dot = graph_for_documents(driver, result["sources"])
            graph_html = interactive_graph(driver, result["sources"])
        finally:
            driver.close()
        st.subheader("Resposta grounded — dados reais")
        st.write(result["answer"])
        st.metric("Confiança", result["confidence"])
        st.caption(f"Gerado por {settings.llm_model}" if result["llm"] else "Resposta por template (LLM não configurado)")
        st.write(f"**Documentos recuperados:** {len(result['sources'])}")
        st.write("**Pontuação híbrida:** combinação de vetor, full-text e caminho do grafo")
        st.subheader("Subgrafo real recuperado")
        components.html(graph_html, height=590, scrolling=True)
        st.caption("Nós circulares: azul = filme, ciano = série, verde = pessoa, amarelo = gênero, roxo = estúdio/canal. Passe o mouse sobre um nó para ver o nome completo.")
        with st.expander("Resultados e scores"):
            st.json(results)
        with st.expander("Cypher e evidências"):
            trace = executed_cypher.get("generated", {})
            if trace.get("error"):
                st.warning(trace["error"])
            st.code(trace.get("query", ""), language="cypher")
            st.json(trace.get("parameters", {}))
            st.subheader("Títulos recuperados")
            for index, title in enumerate(result["evidence_titles"], 1):
                st.markdown(f"{index}. **{title}**")
            st.caption("As fontes são mantidas pelos IDs do catálogo (data/raw/titles.json), cada um com URI de referência.")
    else:
        result = build_demo_result(question, records)
        st.subheader("Resposta demonstrativa")
        st.write(result["answer"])
        left, right = st.columns(2)
        with left:
            st.subheader("Rastreabilidade")
            st.metric("Confiança demonstrativa", "0,82")
            st.write("**Nós:** Person → Movie/Series → Genre/Studio")
            st.write("**Saltos:** 2")
            st.write("**Fontes:** data/raw/titles.json (URIs da Wikipedia)")
        with right:
            st.subheader("Subgrafo recuperado")
            st.graphviz_chart("""digraph G {
              rankdir=LR;
              graph [bgcolor="transparent"];
              node [shape=circle, fixedsize=true, width=1.25, height=1.25, style=filled, fontname="Arial", fontsize=10];
              Person [label="Person", fillcolor="#6EDB45"];
              Movie [label="Movie", fillcolor="#5B9BF3"];
              Series [label="Series", fillcolor="#2EC4D6"];
              Genre [label="Genre", fillcolor="#FFD43B"];
              Studio [label="Studio", fillcolor="#B889F4"];
              Person -> Movie [label="DIRECTED / ACTED_IN"];
              Person -> Series [label="CREATED / ACTED_IN"];
              Movie -> Genre [label="HAS_GENRE"];
              Series -> Studio [label="PRODUCED_BY"];
            }""", use_container_width=True)
            st.caption("Modo demonstrativo: círculos representam os tipos de nó do schema.")
        with st.expander("Cypher gerado"):
            st.code(result["cypher"], language="cypher")
        with st.expander("Evidências e nós encontrados"):
            st.json({"people": result["people"], "studios": result["studios"], "genres": result["genres"]})
