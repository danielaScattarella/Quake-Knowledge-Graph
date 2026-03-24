# agents/metadata_recommender.py


def suggest(dataset_summary):
    """
    dataset_summary è il risultato prodotto dal dataset_analyzer:
    {
        "total_events": ...,
        "events": [...],
        "summary": {...}
    }
    """

    events = dataset_summary.get("events", [])
    summary = dataset_summary.get("summary", {})

    title_alternatives = generate_titles(events, summary)
    one_line_summary = generate_one_line_summary(summary)
    tags = generate_tags(events, summary)
    reasoning = generate_reasoning(summary)

    return {
        "title_alternatives": title_alternatives,
        "one_line_summary": one_line_summary,
        "tags": tags,
        "reasoning": reasoning
    }


# ------------------------------------------------------------
#               TITOLI PER DATI INGV
# ------------------------------------------------------------

def generate_titles(events, summary):
    titles = set()

    # caso dataset piccolo
    if len(events) < 5:
        titles.add("Small Seismic Event Collection (INGV)")

    # dataset standard
    titles.add("INGV Earthquake Dataset Analysis")
    titles.add("Seismic Activity Summary from INGV Records")

    # titolo basato sul range di magnitudo
    min_m = summary.get("min_magnitude")
    max_m = summary.get("max_magnitude")

    if min_m is not None and max_m is not None:
        titles.add(f"Seismic Events Report (M {min_m}–{max_m})")

    return list(titles)[:4]


# ------------------------------------------------------------
#               RIASSUNTO IN UNA FRASE
# ------------------------------------------------------------

def generate_one_line_summary(summary):
    if not summary:
        return "Dataset of seismic events recorded by INGV."

    min_m = summary.get("min_magnitude")
    max_m = summary.get("max_magnitude")
    avg_m = summary.get("avg_magnitude")
    total = summary.get("total_events")

    return (
        f"Dataset containing {total} INGV-recorded earthquakes, "
        f"with magnitudes ranging from {min_m} to {max_m} "
        f"(average {round(avg_m, 2)})."
    )


# ------------------------------------------------------------
#               TAG SISMICI
# ------------------------------------------------------------

def generate_tags(events, summary):
    tags = set()

    # base
    tags.update(["earthquake", "seismic", "INGV", "geophysics"])

    # magnitudo
    if summary.get("max_magnitude", 0) >= 5:
        tags.add("strong-earthquake")
    elif summary.get("max_magnitude", 0) >= 3:
        tags.add("moderate-earthquake")
    else:
        tags.add("microseismicity")

    # profondità
    avg_depth = summary.get("avg_depth")
    if avg_depth is not None:
        if avg_depth < 10:
            tags.add("shallow-earthquakes")
        elif avg_depth < 30:
            tags.add("intermediate-depth")
        else:
            tags.add("deep-earthquakes")

    # regioni (es. Campi Flegrei, Etna…)
    for e in events[:200]:  # limite per performance
        loc = e.get("EventLocationName", "")
        if "Flegrei" in loc:
            tags.add("campi-flegrei")
        if "Etna" in loc:
            tags.add("etna")
        if "Eolie" in loc:
            tags.add("eolie")
        if "Appennino" in loc or "Apennines" in loc:
            tags.add("appennino")

    return list(tags)[:10]


# ------------------------------------------------------------
#               MOTIVAZIONE / REASONING
# ------------------------------------------------------------

def generate_reasoning(summary):
    reasoning = {}

    mmin = summary.get("min_magnitude")
    mmax = summary.get("max_magnitude")
    mavg = summary.get("avg_magnitude")
    dmin = summary.get("min_depth")
    dmax = summary.get("max_depth")

    reasoning["magnitude_range"] = f"Magnitude ranges from {mmin} to {mmax}, avg {round(mavg, 2)}."
    reasoning["depth_range"] = f"Depth ranges from {dmin} km to {dmax} km."
    reasoning["classification_basis"] = (
        "Tags and metadata are derived from earthquake intensity, depth category, "
        "and notable locations contained in the dataset."
    )

    return reasoning