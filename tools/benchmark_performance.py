import time
import tracemalloc
import statistics
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from agents.dataset_analyzer import analyze_dataset
from agents.embedding_agent import EarthquakeEmbeddingAgent
from agents.metadata_recommender import suggest
from agents.content_improver import improve
from agents.reviewer import review
from agents.qa_agent import EarthquakeQAAgent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "data", "small_earthquakes")

# ===========================================================
#               UTILITY DI BENCHMARK
# ===========================================================

def benchmark(func, *args, runs=5, **kwargs):
    """Misura mean, std, p95 su N esecuzioni reali."""
    times = []

    for _ in range(runs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)

    mean = statistics.mean(times)
    std = statistics.pstdev(times)
    p95 = sorted(times)[max(0, int(0.95 * runs) - 1)]

    return {
        "mean": round(mean, 6),
        "std_dev": round(std, 6),
        "p95": round(p95, 6),
        "runs": runs
    }


def measure_memory(func, *args, **kwargs):
    """Misura memoria usata da una chiamata."""
    tracemalloc.start()
    func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "current_kb": round(current / 1024, 2),
        "peak_kb": round(peak / 1024, 2)
    }


# ===========================================================
#               BENCHMARK PIPELINE INGV
# ===========================================================

def run_full_benchmark(dataset_path: str):

    results = {}

    print(f"📂 Caricamento dataset da: {dataset_path}")

    # ---------------------------------------------------
    # 1) Dataset Analyzer
    # ---------------------------------------------------
    analyzer_times = benchmark(analyze_dataset, dataset_path)
    dataset = analyze_dataset(dataset_path)

    results["dataset_analysis"] = analyzer_times
    results["dataset_memory"] = measure_memory(analyze_dataset, dataset_path)

    events = dataset.get("events", [])
    print(f"✅ EVENTI TOTALI TROVATI: {len(events)}")

    # Filtra eventi davvero utilizzabili
    valid_events = [
        e for e in events
        if e.get("Magnitude") not in (None, "", " ")
           and e.get("Depth_Km") not in (None, "", " ")
    ]

    print(f"✅ EVENTI VALIDATI PER EMBEDDING: {len(valid_events)}")

    # Limite per stabilizzare il benchmark
    valid_events = valid_events[:300]

    # ---------------------------------------------------
    # 2) Embedding Agent
    # ---------------------------------------------------
    emb = EarthquakeEmbeddingAgent()

    if valid_events:
        print("🔧 Generazione embeddings reali...")
        embedding_times = benchmark(emb.add_earthquake_events, valid_events)
    else:
        print("⚠️ Nessun evento valido → embedding saltato.")
        embedding_times = {"mean": 0, "std_dev": 0, "p95": 0, "runs": 5}

    results["embedding_generation"] = embedding_times

    # ---------------------------------------------------
    # 3) Metadata
    # ---------------------------------------------------
    print("🧪 Metadata Recommender...")
    metadata_times = benchmark(suggest, dataset)
    metadata = suggest(dataset)
    results["metadata"] = metadata_times

    # ---------------------------------------------------
    # 4) Content Improver
    # ---------------------------------------------------
    print("✍️ Content Improver...")
    improver_times = benchmark(improve, dataset, metadata)
    improved = improve(dataset, metadata)
    results["content_improver"] = improver_times

    # ---------------------------------------------------
    # 5) Reviewer
    # ---------------------------------------------------
    print("🔍 Reviewer...")
    review_times = benchmark(review, dataset, improved)
    results["reviewer"] = review_times

    # ---------------------------------------------------
    # 6) Vector Search
    # ---------------------------------------------------
    print("🔎 Vector Search con Qdrant...")
    qa = EarthquakeQAAgent()

    def test_vector_search():
        qa.emb.semantic_search("earthquake magnitude analysis", top_k=5)

    vector_times = benchmark(test_vector_search)
    results["vector_search"] = vector_times

    # ---------------------------------------------------
    # 7) Memory usage embeddings
    # ---------------------------------------------------
    print("💾 Misura memoria embeddings...")
    results["embedding_memory"] = measure_memory(
        emb.semantic_search, "earthquake", top_k=3
    )



    return results


# ===========================================================
#                   MAIN
# ===========================================================

if __name__ == "__main__":

    dataset = DATASET_DIR

    print("\n🔬 Running INGV Multi-Agent Benchmark...\n")
    results = run_full_benchmark(dataset)

    print(json.dumps(results, indent=2, ensure_ascii=False))

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n✅ Benchmark completato e salvato in benchmark_results.json.\n")