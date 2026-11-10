"""Interface visual demonstrativa do projeto acadêmico GraphRAG/KAG."""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.config import settings
from src.generation.grounded import grounded_answer
from src.retrieval.hybrid import hybrid_search


st.set_page_config(page_title="GraphRAG & KAG — Demonstração", page_icon="🕸️", layout="wide")


def load_sample_data() -> list[dict]:
    path = Path("data/raw/publications.sample.jsonl")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
    authors = sorted({a["name"] for r in records for a in r.get("authors", [])})
    venues = sorted({r.get("venue") for r in records if r.get("venue")})
    technologies = sorted({t for r in records for t in r.get("topics", [])})
    cypher = """MATCH (i:Institution)<-[:AFFILIATED_WITH]-(a:Author)-[:WROTE]->(p:Paper)
MATCH (p)-[:PUBLISHED_AT]->(v:Venue), (p)-[:USES_TECHNOLOGY]->(t:Technology)
WHERE toLower(p.title) CONTAINS 'graphrag' OR toLower(p.title) CONTAINS 'knowledge'
RETURN i, a, p, v, t LIMIT 25"""
    return {
        "answer": f"Demonstração para: {question}\n\nA amostra contém {len(records)} publicações, {len(authors)} autores, {len(venues)} venues e {len(technologies)} tópicos.",
        "cypher": cypher,
        "authors": authors,
        "venues": venues,
        "technologies": technologies,
    }


def graph_for_documents(driver, document_ids: list[str]) -> str:
    if not document_ids:
        return "digraph G { empty [label=\"Nenhum subgrafo recuperado\"]; }"
    query = """
    MATCH (p:Paper)-[r]-(neighbor)
    WHERE p.id IN $document_ids
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
        "Paper": "#DCEBFF",
        "Author": "#E6F4EA",
        "Technology": "#FFF4CC",
        "Venue": "#F3E8FF",
        "Institution": "#FFE4E6",
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
    MATCH (p:Paper)-[r]-(neighbor)
    WHERE p.id IN $document_ids
    RETURN p.id AS source_id, coalesce(p.title, p.name, p.id) AS source_name,
           labels(p)[0] AS source_type, type(r) AS relationship,
           neighbor.id AS target_id, coalesce(neighbor.title, neighbor.name, neighbor.id) AS target_name,
           labels(neighbor)[0] AS target_type LIMIT 40
    """
    rows = driver.execute_query(query, document_ids=document_ids).records
    nodes = {}
    edges = []
    type_colors = {
        "Paper": "#5B9BF3",
        "Author": "#6EDB45",
        "Technology": "#FFD43B",
        "Venue": "#B889F4",
        "Institution": "#FF8A8A",
        "Entity": "#A7B0BE",
    }
    for row in rows:
        for node_id, name, node_type in [
            (row["source_id"], row["source_name"], row["source_type"]),
            (row["target_id"], row["target_name"], row["target_type"]),
        ]:
            short_name = str(name)
            if node_type == "Paper":
                short_name = f"Paper {len([n for n in nodes.values() if n['group'] == 'Paper']) + 1}"
            elif len(short_name) > 22:
                short_name = short_name[:19] + "..."
            nodes[node_id] = {
                "id": node_id,
                "label": short_name,
                "title": f"{node_type}: {name}",
                "group": node_type,
                "shape": "dot",
                "size": 24 if node_type == "Paper" else 18,
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
st.info(f"Modo ativo: **{'Dados reais (OpenAlex + Neo4j)' if st.session_state.data_mode == 'real' else 'Dados demonstrativos (amostra local)'}**")

status, counts = neo4j_status()
records = load_sample_data()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Neo4j", status)
col2.metric("Publicações de exemplo", len(records))
col3.metric("Chunks", counts.get("Chunk", "—"))
col4.metric("Entidades", counts.get("Entity", "—"))

question = st.text_area("Pergunta multi-hop", "Quais instituições possuem autores que publicaram sobre GraphRAG e quais tecnologias aparecem nesses artigos?")

if st.button("Executar consulta", type="primary"):
    if st.session_state.data_mode == "real":
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
        try:
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
        st.write(f"**Documentos recuperados:** {len(result['sources'])}")
        st.write("**Pontuação híbrida:** combinação de vetor, full-text e caminho do grafo")
        st.subheader("Subgrafo real recuperado")
        components.html(graph_html, height=590, scrolling=True)
        st.caption("Nós circulares: azul = artigo, verde = autor, amarelo = tecnologia, roxo = venue. Passe o mouse sobre um nó para ver o título completo.")
        with st.expander("Resultados e scores"):
            st.json(results)
        with st.expander("Cypher e evidências"):
            st.code(result["cypher"], language="text")
            st.subheader("Artigos recuperados")
            for index, title in enumerate(result["evidence_titles"], 1):
                st.markdown(f"{index}. **{title}**")
            st.caption("As fontes são mantidas internamente pelos IDs OpenAlex; os títulos são exibidos para leitura humana.")
    else:
        result = build_demo_result(question, records)
        st.subheader("Resposta demonstrativa")
        st.write(result["answer"])
        left, right = st.columns(2)
        with left:
            st.subheader("Rastreabilidade")
            st.metric("Confiança demonstrativa", "0,82")
            st.write("**Nós:** Institution → Author → Paper → Venue/Technology")
            st.write("**Saltos:** 4")
            st.write("**Fontes:** DBLP/OpenAlex/arXiv + amostra local")
        with right:
            st.subheader("Subgrafo recuperado")
            st.graphviz_chart("""digraph G {
              rankdir=LR;
              graph [bgcolor="transparent"];
              node [shape=circle, fixedsize=true, width=1.25, height=1.25, style=filled, fontname="Arial", fontsize=10];
              Institution [label="Institution", fillcolor="#FF8A8A"];
              Author [label="Author", fillcolor="#6EDB45"];
              Paper [label="Paper", fillcolor="#5B9BF3"];
              Venue [label="Venue", fillcolor="#B889F4"];
              Technology [label="Technology", fillcolor="#FFD43B"];
              Institution -> Author [label="AFFILIATED_WITH"];
              Author -> Paper [label="WROTE"];
              Paper -> Venue [label="PUBLISHED_AT"];
              Paper -> Technology [label="USES_TECHNOLOGY"];
            }""", use_container_width=True)
            st.caption("Modo demonstrativo: círculos representam os tipos de nó do schema.")
        with st.expander("Cypher gerado"):
            st.code(result["cypher"], language="cypher")
        with st.expander("Evidências e nós encontrados"):
            st.json({"authors": result["authors"], "venues": result["venues"], "technologies": result["technologies"]})
