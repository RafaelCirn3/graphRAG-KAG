"""Interface visual demonstrativa do projeto acadêmico GraphRAG/KAG."""

import json
from pathlib import Path

import streamlit as st

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
    RETURN p.id AS source, type(r) AS relationship, neighbor.id AS target
    LIMIT 40
    """
    rows = driver.execute_query(query, document_ids=document_ids).records
    lines = ["digraph G {", "rankdir=LR;"]
    for row in rows:
        source = str(row["source"]).replace('"', "'")
        target = str(row["target"]).replace('"', "'")
        relationship = str(row["relationship"]).replace('"', "'")
        lines.append(f'"{source}" -> "{target}" [label="{relationship}"];')
    lines.append("}")
    return "\n".join(lines)


st.title("🕸️ GraphRAG & KAG")
st.warning("Demonstração visual acadêmica — não representa um produto de produção.")
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
            result = grounded_answer(question, results, cypher="hybrid_search: vector + fulltext + path_score")
            graph_dot = graph_for_documents(driver, result["sources"])
        finally:
            driver.close()
        st.subheader("Resposta grounded — dados reais")
        st.write(result["answer"])
        st.metric("Confiança", result["confidence"])
        st.write(f"**Documentos recuperados:** {len(result['sources'])}")
        st.write("**Pontuação híbrida:** combinação de vetor, full-text e caminho do grafo")
        st.subheader("Subgrafo real recuperado")
        st.graphviz_chart(graph_dot, use_container_width=True)
        with st.expander("Resultados e scores"):
            st.json(results)
        with st.expander("Cypher e evidências"):
            st.code(result["cypher"], language="text")
            st.json({"sources": result["sources"], "titles": result["evidence_titles"]})
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
            st.graphviz_chart("""digraph G { rankdir=LR; Institution -> Author [label="AFFILIATED_WITH"]; Author -> Paper [label="WROTE"]; Paper -> Venue [label="PUBLISHED_AT"]; Paper -> Technology [label="USES_TECHNOLOGY"]; }""", use_container_width=True)
        with st.expander("Cypher gerado"):
            st.code(result["cypher"], language="cypher")
        with st.expander("Evidências e nós encontrados"):
            st.json({"authors": result["authors"], "venues": result["venues"], "technologies": result["technologies"]})
