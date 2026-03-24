# orchestrator/simple_pipeline.py

import asyncio

from agents.dataset_analyzer import analyze_dataset
from agents.embedding_agent import EarthquakeEmbeddingAgent
from agents.metadata_recommender import suggest as suggest_metadata_earthquakes
from agents.content_improver import improve as improve_earthquake_content
from agents.reviewer import review as review_earthquake_dataset


async def run_pipeline(dataset_path: str):
    """
    Pipeline semplice per dataset sismici INGV.
    Step:
    1. Analisi dataset
    2. Embedding eventi
    3. Metadata recommendation
    4. Content improvement
    5. Scientific review
    """

    # 1) ANALISI DATI
    summary = analyze_dataset(dataset_path)

    # 2) EMBEDDINGS ED INDICIZZAZIONE
    events = summary.get("events", [])
    if events:
        emb = EarthquakeEmbeddingAgent()
        print(f"Embedding di {len(events)} eventi INGV...")
        emb.add_earthquake_events(events)
    else:
        print("[WARNING] Nessun evento INGV trovato. Embedding saltato.")

    # 3) METADATI SISMICI
    metadata = suggest_metadata_earthquakes(summary)

    # 4) MIGLIORAMENTO TESTUALE DEI CONTENUTI
    improved = improve_earthquake_content(summary, metadata)

    # 5) REVISIONE SCIENTIFICA
    review = review_earthquake_dataset(summary, improved)

    return {
        "summary": summary,
        "metadata": metadata,
        "improved": improved,
        "review": review
    }


if __name__ == "__main__":
    import sys
    import json

    dataset = sys.argv[1] if len(sys.argv) > 1 else "data/sample_earthquakes"
    result = asyncio.run(run_pipeline(dataset))

    print(json.dumps({
        "metadata": result["metadata"],
        "review": result["review"]
    }, indent=2, ensure_ascii=False))