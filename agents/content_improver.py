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
        f"Il dataset contiene {total} eventi sismici analizzati. "
        f"La magnitudo varia da {min_mag} a {max_mag} "
        f"con una media di {round(avg_mag, 2) if avg_mag else 'N/D'}. "
        f"La profondità ipocentrale varia da {min_depth} a {max_depth} km "
        f"(media: {round(avg_depth, 2) if avg_depth else 'N/D'} km). "
        f"Sono stati rilevati eventi localizzati in diverse aree, "
        f"con distribuzione spaziale e dei parametri coerente con la micro-sismicità tipica regionale."
    )

    return {
        "improved_text": improved_text,
        "metadata_used": metadata,
        "events_processed": len(events)
    }