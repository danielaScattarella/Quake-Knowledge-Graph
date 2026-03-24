# agents/reviewer.py

def review(dataset_summary, improved_data=None):
    """
    Valuta la qualità del dataset INGV (completezza campi, valori anomali, consistenza statistica,
    mancanza di informazioni essenziali).
    """

    issues = []
    recommendations = []
    completeness_checks = {}

    events = dataset_summary.get("events", [])
    summary = dataset_summary.get("summary", {})

    # -----------------------------
    #   CHECK 1 — Presenza eventi
    # -----------------------------
    if not events:
        issues.append("❌ Il dataset non contiene eventi sismici (lista vuota).")
        return _empty_result(issues)

    total_events = len(events)

    # -----------------------------
    #   CHECK 2 — Completezza campi critici
    # -----------------------------
    completeness_checks["EventID"] = all(e.get("EventID") for e in events)
    completeness_checks["Time"] = all(e.get("Time") for e in events)
    completeness_checks["Latitude"] = all(e.get("Latitude") for e in events)
    completeness_checks["Longitude"] = all(e.get("Longitude") for e in events)
    completeness_checks["Magnitude"] = all(e.get("Magnitude") for e in events)
    completeness_checks["Depth_Km"] = all(e.get("Depth_Km") for e in events)
    completeness_checks["Location"] = all(e.get("EventLocationName") for e in events)

    for field, ok in completeness_checks.items():
        if not ok:
            issues.append(f"⚠️ Il campo '{field}' non è presente per tutti gli eventi.")

    # -----------------------------
    #   CHECK 3 — Valori anomali
    # -----------------------------
    anomalies = []

    for e in events:
        try:
            depth = float(e.get("Depth_Km"))
            if depth < 0 or depth > 700:
                anomalies.append(
                    f"Profondità anomala {depth} km per EventID {e.get('EventID')}"
                )
        except:
            anomalies.append(
                f"Profondità non numerica per EventID {e.get('EventID')}"
            )

        try:
            mag = float(e.get("Magnitude"))
            if mag < -1 or mag > 10:
                anomalies.append(
                    f"Magnitudo anomala {mag} per EventID {e.get('EventID')}"
                )
        except:
            anomalies.append(
                f"Magnitudo non numerica per EventID {e.get('EventID')}"
            )

    if anomalies:
        issues.append("⚠️ Rilevate anomalie nei parametri numerici (profondità o magnitudo).")
        recommendations.append("💡 Verificare i valori anomali riportati nella sezione dedicata.")
    
    # -----------------------------
    #   CHECK 4 — Variabilità magnitudo
    # -----------------------------
    if summary.get("max_magnitude", 0) < 1:
        recommendations.append(
            "ℹ️ Il dataset contiene solo eventi molto piccoli (micro-sismicità)."
        )

    # -----------------------------
    #   CHECK 5 — Distribuzione geografica
    # -----------------------------
    if _is_single_area(events):
        recommendations.append(
            "ℹ️ La distribuzione geografica è molto concentrata: potrebbe trattarsi di una sequenza locale."
        )

    # -----------------------------
    #   CHECK 6 — Miglioramenti automatizzati (se presenti)
    # -----------------------------
    if improved_data and isinstance(improved_data, dict):
        improvements_list = improved_data.get("improvements", [])
        for imp in improvements_list[:3]:
            recommendations.append(f"💡 {imp}")

    # -----------------------------
    #   Risultati finali
    # -----------------------------
    validation_results = {
        "critical_issues": len([i for i in issues if "❌" in i]),
        "warnings": len([i for i in issues if "⚠️" in i]),
        "recommendations_count": len(recommendations),
        "completeness": completeness_checks,
        "overall_health": calculate_health_score_earthquakes(issues, recommendations, completeness_checks),
        "numerical_anomalies": anomalies,
        "total_events": total_events
    }

    return {
        "issues": issues,
        "recommendations": recommendations,
        "validation_results": validation_results,
        "action_items": generate_action_items_earthquakes(issues, recommendations),
        "priority_fixes": get_priority_fixes_earthquakes(issues),
    }


# ============================================================
#               FUNZIONI DI SUPPORTO
# ============================================================

def _empty_result(issues):
    return {
        "issues": issues,
        "recommendations": [],
        "validation_results": {"overall_health": 0},
        "action_items": [],
        "priority_fixes": ["Aggiungere eventi o verificare il formato dei dati."]
    }


def _is_single_area(events):
    """Rileva se la maggior parte degli eventi ha la stessa area geografica."""
    locations = [e.get("EventLocationName", "").split()[0] for e in events if e.get("EventLocationName")]
    if not locations:
        return False
    most_common = max(set(locations), key=locations.count)
    proportion = locations.count(most_common) / len(locations)
    return proportion > 0.70  # soglia: 70% negli stessi dintorni


# ============================================================
#               SCORING
# ============================================================

def calculate_health_score_earthquakes(issues, recommendations, completeness):
    score = 100

    # Penalità
    score -= len([i for i in issues if "❌" in i]) * 25
    score -= len([i for i in issues if "⚠️" in i]) * 10
    score -= len(recommendations) * 5

    # Campi essenziali mancanti
    for field in ["Time", "Latitude", "Longitude", "Magnitude"]:
        if not completeness.get(field):
            score -= 15

    return max(0, min(100, score))


# ============================================================
#               ACTION ITEMS
# ============================================================

def generate_action_items_earthquakes(issues, recommendations):
    actions = []

    if any("dataset non contiene eventi" in i.lower() for i in issues):
        actions.append({
            "priority": "P0 - CRITICAL",
            "task": "Verificare il file e la formattazione",
            "details": "Assicurarsi che gli eventi siano separati da delimitatori validi."
        })

    if any("Profondità" in i or "Magnitudo" in i for i in issues):
        actions.append({
            "priority": "P1 - HIGH",
            "task": "Correggere valori numerici anomali",
            "details": "Verificare la correttezza delle coordinate ipocentrali e del calcolo della magnitudo."
        })

    for rec in recommendations[:3]:
        actions.append({
            "priority": "P2 - MEDIUM",
            "task": rec.replace("💡 ", ""),
            "details": "Applicare miglioramenti suggeriti dall’agente di revisione."
        })

    return actions[:5]


# ============================================================
#               PRIORITY FIXES
# ============================================================

def get_priority_fixes_earthquakes(issues):
    if any("⚠️" in i and "Profondità" in i for i in issues):
        return ["Verificare profondità anomale", "Controllare magnitudo"]
    if any("❌" in i for i in issues):
        return ["Verificare struttura del file", "Controllare integrità dei dati"]
    return ["Migliorare descrizioni località", "Aggiungere metadati mancanti"]