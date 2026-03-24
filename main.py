import argparse
import json
from pathlib import Path

from tools.earthquake_dataset_loader import EarthquakeDatasetLoader
from orchestrator.langgraph_flow import run_langgraph_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Earthquake Multi-Agent Pipeline (INGV Dataset Processor)"
    )

    parser.add_argument(
        "dataset",
        type=str,
        help="Percorso a file o directory INGV (.txt, .csv, .xml, .json, .zip)"
    )

    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Percorso file JSON per salvare l'output completo della pipeline"
    )

    args = parser.parse_args()
    dataset_path = Path(args.dataset)

    # ---------------------------------------------------
    # 1. Caricamento dataset
    # ---------------------------------------------------
    print("\n📁 Caricamento dataset...")
    loader = EarthquakeDatasetLoader()
    dataset_dir = loader.load_from_path(str(dataset_path))
    print(f"   → Dataset directory: {dataset_dir}")

    # ---------------------------------------------------
    # 2. Esecuzione pipeline LangGraph multi‑agente
    # ---------------------------------------------------
    print("\n⚙️ Avvio pipeline multi‑agente...")
    result = run_langgraph_pipeline(dataset_dir)
    print("   → Pipeline completata!\n")

    # ---------------------------------------------------
    # 3. Estrazione risultati
    # ---------------------------------------------------
    summary = result.get("dataset_summary", {})
    metadata = result.get("metadata", {})
    improved = result.get("improved", {})
    review = result.get("review", {})
    qa = result.get("qa", "")
    article = result.get("article", "")

    print("==============================================")
    print("🌋 RISULTATI ANALISI SISMICA COMPLETA")
    print("==============================================")

    # 📌 Dataset summary
    if "summary" in summary:
        s = summary["summary"]
        print(f"Totale eventi analizzati: {s.get('total_events')}")
        print(f"Magnitudo massima:        {s.get('max_magnitude')}")
        print(f"Profondità massima:       {s.get('max_depth')} km")

    # 📌 Metadati
    print("\n🔖 Metadati suggeriti:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))

    # 📌 Revisione scientifica
    print("\n🔍 Revisione scientifica:")
    print(json.dumps(review, indent=2, ensure_ascii=False))

    # 📌 Q&A intelligente
    print("\n❓ Risposte automatiche (QA Agent):")
    print(qa)

    # 📌 Report finale
    print("\n📝 Articolo / Report Sismologico:")
    print(article)

    # ---------------------------------------------------
    # 4. Salvataggio opzionale
    # ---------------------------------------------------
    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Risultati salvati in: {args.save}")

    print("\n✅ Elaborazione completata.\n")


if __name__ == "__main__":
    main()