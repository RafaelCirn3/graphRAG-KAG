"""Interface visual demonstrativa do projeto acadêmico GraphRAG/KAG."""

import json
from pathlib import Path

import streamlit as st

from src.config import settings


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


st.title("🕸️ GraphRAG & KAG")
st.warning("Demonstração visual acadêmica — não representa um produto de produção.")
st.caption("Atividade final de Tendências em Ciência da Computação | Busca híbrida e rastreabilidade")

status, counts = neo4j_status()
records = load_sample_data()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Neo4j", status)
col2.metric("Publicações de exemplo", len(records))
col3.metric("Chunks", counts.get("Chunk", "—"))
col4.metric("Entidades", counts.get("Entity", "—"))

question = st.text_area("Pergunta multi-hop", "Quais instituições possuem autores que publicaram sobre GraphRAG e quais tecnologias aparecem nesses artigos?")

if st.button("Executar demonstração", type="primary"):
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

with st.expander("Sobre o demonstrativo"):
    st.write("A tela demonstra pergunta, resposta, caminho do grafo, Cypher, confiança e evidências. Embeddings, NER/RE e LLM serão conectados nas próximas fases.")
