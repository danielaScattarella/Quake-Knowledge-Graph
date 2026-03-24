from tools.file_loader import load_files_from_directory, extract_zip_to_dir
import os


INGV_FIELDS = [
    "EventID", "Time", "Latitude", "Longitude", "Depth_Km",
    "Author", "Catalog", "Contributor", "ContributorID",
    "MagType", "Magnitude", "MagAuthor", "EventLocationName", "EventType"
]

def analyze_dataset(path_or_zip: str, workdir="./temp_ingv"):
    # Gestione ZIP (se serve)
    if path_or_zip.endswith(".zip") or (os.path.isfile(path_or_zip) and path_or_zip.lower().endswith(".zip")):
        extract_zip_to_dir(path_or_zip, workdir)
        data_dir = workdir
    else:
        data_dir = path_or_zip

    files = load_files_from_directory(data_dir)

    # Cerca file TXT INGV
    txt_files = [f for f in files if f["path"].lower().endswith(".txt")]

    if not txt_files:
        return {"error": "Nessun file TXT INGV trovato", "files": files}

    parsed_records = []

    for f in txt_files:
        content = f["content"]
        lines = content.strip().split("\n")

        # Salta header
        header = lines[0].split("|")

        # Verifica compatibilità formato
        if len(header) < 5:  # minimo 5 colonne
            continue

        # Parsing righe successive
        for row in lines[1:]:
            parts = row.split("|")
            if len(parts) != len(INGV_FIELDS):
                # ignora o adatta riga non valida
                continue

            record = {INGV_FIELDS[i]: parts[i].strip() for i in range(len(INGV_FIELDS))}
            parsed_records.append(record)

    summary = summarize_earthquake_data(parsed_records)

    return {
        "dataset_directory": data_dir,
        "total_files": len(files),
        "txt_ingv_files": len(txt_files),
        "total_events": len(parsed_records),
        "events": parsed_records,
        "summary": summary
    }


def summarize_earthquake_data(events):
    if not events:
        return {}

    magnitudes = []
    depths = []

    for e in events:
        try:
            magnitudes.append(float(e["Magnitude"]))
        except:
            pass
        try:
            depths.append(float(e["Depth_Km"]))
        except:
            pass

    return {
        "min_magnitude": min(magnitudes) if magnitudes else None,
        "max_magnitude": max(magnitudes) if magnitudes else None,
        "avg_magnitude": sum(magnitudes) / len(magnitudes) if magnitudes else None,
        "min_depth": min(depths) if depths else None,
        "max_depth": max(depths) if depths else None,
        "avg_depth": sum(depths) / len(depths) if depths else None,
        "total_events": len(events),
    }
