from langgraph.graph import StateGraph
from typing import TypedDict, Optional

# ---- agents ----
from agents.dataset_analyzer import analyze_dataset
from agents.embedding_agent import EarthquakeEmbeddingAgent
from agents.metadata_recommender import suggest as suggest_metadata_earthquakes
from agents.content_improver import improve as improve_earthquake_content
from agents.reviewer import review as review_earthquake_dataset
from agents.qa_agent import EarthquakeQAAgent
from agents.article_generator import EarthquakeArticleGeneratorAgent


class PipelineState(TypedDict):
    dataset_path: str
    dataset_summary: Optional[dict]
    metadata: Optional[dict]
    improved: Optional[dict]
    review: Optional[dict]
    qa: Optional[str]
    article: Optional[str]


# ------------------------------------------------------
#                     NODI DELLA PIPELINE
# ------------------------------------------------------

def analyze_data(state: PipelineState) -> PipelineState:
    summary = analyze_dataset(state["dataset_path"])
    return {"dataset_summary": summary}


def embed_events(state: PipelineState) -> PipelineState:
    summary = state["dataset_summary"]
    events = summary.get("events", [])

    if not events:
        print("[WARNING] Nessun evento trovato — niente embedding.")
        return {}

    emb = EarthquakeEmbeddingAgent()
    emb.add_earthquake_events(events)

    return {}


def suggest_metadata(state: PipelineState) -> PipelineState:
    meta = suggest_metadata_earthquakes(state["dataset_summary"])
    return {"metadata": meta}


def improve_content(state: PipelineState) -> PipelineState:
    improved = improve_earthquake_content(
        state["dataset_summary"], 
        state["metadata"]
    )
    return {"improved": improved}


def review_content(state: PipelineState) -> PipelineState:
    rev = review_earthquake_dataset(
        state["dataset_summary"], 
        state["improved"]
    )
    return {"review": rev}


def qa_on_dataset(state: PipelineState) -> PipelineState:
    agent = EarthquakeQAAgent()
    answer_question = agent.answer("Provide a summary or FAQs about the dataset")
    return {"qa": answer_question}


def generate_final_article(state: PipelineState) -> PipelineState:
    """7) Generazione articolo/report sismologico finale."""
    
    generator = EarthquakeArticleGeneratorAgent()

    # Costruzione del contesto unico da passare al modello
    dataset_context = f"""
DATASET SUMMARY:
{state['dataset_summary']}

SUGGESTED METADATA:
{state['metadata']}

REVIEW RESULTS:
{state['review']}
"""

    # Istruzioni per l’agente
    user_instructions = "Generate a complete seismological article based on the INGV dataset."

    # Chiamata corretta al metodo generate()
    text = generator.generate(
        dataset_context=dataset_context,
        user_instructions=user_instructions,
        dataset_description="Automatically generated dataset report"
    )

    return {"article": text}


# ------------------------------------------------------
#                     COSTRUZIONE DEL GRAFO
# ------------------------------------------------------

graph = StateGraph(PipelineState)

graph.add_node("analyze", analyze_data)
graph.add_node("embed", embed_events)
graph.add_node("metadata", suggest_metadata)
graph.add_node("improve", improve_content)
graph.add_node("review", review_content)
graph.add_node("qa", qa_on_dataset)
graph.add_node("article", generate_final_article)

graph.set_entry_point("analyze")

graph.add_edge("analyze", "embed")
graph.add_edge("embed", "metadata")
graph.add_edge("metadata", "improve")
graph.add_edge("improve", "review")
graph.add_edge("review", "qa")
graph.add_edge("qa", "article")
graph.add_edge("article", "__end__")

app = graph.compile()

# ---------------------------------
# FUNZIONE DI AVVIO DELLA PIPELINE 
# ---------------------------------

def run_langgraph_pipeline(dataset_path: str):
    """
    Esegue tutta la pipeline LangGraph e ritorna lo stato finale.
    """
    initial_state = {"dataset_path": dataset_path}
    final_state = app.invoke(initial_state)
    return final_state