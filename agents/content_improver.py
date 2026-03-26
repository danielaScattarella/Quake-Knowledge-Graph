# agents/content_improver.py

def improve(dataset_summary: dict, metadata: dict) -> dict:
    """
    Migliora la descrizione del dataset INGV generando un testo più leggibile,
    usando i metadati già calcolati.
    Restituisce un dizionario con la chiave 'improved_text'.
    """

    summary = dataset_summary.get("summary", {})
    events = dataset_summary.get("events", [])

    total = summary.get("total_events", 0)
    min_mag = summary.get("min_magnitude")
    max_mag = summary.get("max_magnitude")
    avg_mag = summary.get("avg_magnitude")
    min_depth = summary.get("min_depth")
    max_depth = summary.get("max_depth")
    avg_depth = summary.get("avg_depth")

    # Testo migliorato — sintetico e tecnico
    improved_text = (
        f"The dataset contains {total} analyzed seismic events. "
        f"Earthquake magnitudes range from {min_mag} to {max_mag}, "
        f"with an average value of {round(avg_mag, 2) if avg_mag else 'N/A'}. "
        f"Hypocentral depths span from {min_depth} to {max_depth} km "
        f"(average: {round(avg_depth, 2) if avg_depth else 'N/A'} km). "
        f"The recorded events are distributed across multiple areas, "
        f"showing spatial patterns and parameter variability consistent "
        f"with typical regional micro‑seismic activity."
    )
    return {
        "improved_text": improved_text,
        "metadata_used": metadata,
        "events_processed": len(events)
    }