import streamlit as st
import os
import json
from pathlib import Path

from orchestrator.langgraph_flow import run_langgraph_pipeline
from tools.earthquake_dataset_loader import EarthquakeDatasetLoader
from agents.article_generator import EarthquakeArticleGeneratorAgent


# ---------------------------------------------------
#   CONFIGURAZIONE STREAMLIT
# ---------------------------------------------------
st.set_page_config(page_title="Earthquake Intelligence Studio", layout="wide")

st.markdown("""
# 🌋 Earthquake Intelligence Studio
Sistema di analisi avanzata per dataset sismici INGV  
**Pipeline multi‑agente • Embeddings • Analisi scientifica • Generazione articoli**
""")

st.divider()


# ---------------------------------------------------
#   SESSION STATE
# ---------------------------------------------------
if "dataset_dir" not in st.session_state:
    st.session_state.dataset_dir = None

if "pipeline_output" not in st.session_state:
    st.session_state.pipeline_output = None

if "generated_article" not in st.session_state:
    st.session_state.generated_article = None


# ---------------------------------------------------
#   UPLOAD DATASET
# ---------------------------------------------------
st.subheader("📁 Carica Dataset INGV")

uploaded_file = st.file_uploader(
    "Carica file INGV (.txt, .csv, .xml, .json, .zip)",
    type=["txt", "csv", "xml", "json", "zip"]
)

if uploaded_file:
    loader = EarthquakeDatasetLoader()

    # Salvataggio temporaneo
    temp_path = Path("uploaded_" + uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    dataset_dir = loader.load_from_path(str(temp_path))
    st.session_state.dataset_dir = dataset_dir

    st.success("Dataset caricato correttamente!")
    st.write(f"📂 Directory dataset: `{dataset_dir}`")

    os.remove(temp_path)


# ---------------------------------------------------
#   RUN PIPELINE
# ---------------------------------------------------
st.divider()
st.subheader("⚙️ Esegui Analisi Multi‑Agente")

if st.button("🚀 Avvia Pipeline LangGraph", disabled=not st.session_state.dataset_dir):
    with st.spinner("Analisi in corso..."):
        output = run_langgraph_pipeline(st.session_state.dataset_dir)
        st.session_state.pipeline_output = output

    st.success("Pipeline completata!")


# ---------------------------------------------------
#   MOSTRA RISULTATI ANALISI
# ---------------------------------------------------
if st.session_state.pipeline_output:
    out = st.session_state.pipeline_output

    st.subheader("📊 Risultati Analisi")

    col1, col2, col3 = st.columns(3)
    col1.metric("Totale eventi", out["dataset_summary"].get("summary", {}).get("total_events"))
    col2.metric("Magnitudo max", out["dataset_summary"].get("summary", {}).get("max_magnitude"))
    col3.metric("Profondità max (km)", out["dataset_summary"].get("summary", {}).get("max_depth"))

    st.markdown("### 🔖 Metadati suggeriti")
    st.json(out["metadata"])

    st.markdown("### 🧩 Contenuto migliorato")
    st.json(out["improved"])

    st.markdown("### 🔍 Revisione scientifica")
    st.json(out["review"])


# ---------------------------------------------------
#   GENERAZIONE ARTICOLO
# ---------------------------------------------------
st.divider()
st.subheader("📝 Genera Articolo Sismologico")

instructions = st.text_area(
    "Istruzioni articolo",
    placeholder="Es: Genera un report sismico settimanale con focus sui Campi Flegrei."
)

if st.button("✍️ Genera articolo", disabled=not st.session_state.pipeline_output):
    agent = EarthquakeArticleGeneratorAgent()

    dataset_context = json.dumps(st.session_state.pipeline_output["dataset_summary"], indent=2)
    article = agent.generate(
        dataset_context=dataset_context,
        user_instructions=instructions,
        dataset_description="Earthquake dataset processed with multi-agent pipeline."
    )

    st.session_state.generated_article = article
    st.success("Articolo generato!")


# ---------------------------------------------------
#   MOSTRA ARTICOLO
# ---------------------------------------------------
if st.session_state.generated_article:
    st.subheader("📄 Articolo Generato")
    st.markdown(st.session_state.generated_article)

    st.download_button(
        "📥 Scarica come Markdown",
        st.session_state.generated_article,
        "article.md",
        "text/markdown"
    )