# tools/data_analyzer.py

from typing import Dict, List


class EarthquakeDataAnalyzer:
    """
    Analizzatore di eventi sismici INGV.
    Lavora su un singolo file di testo/CSV/XML già caricato come stringa.
    Estrae:
        - validità formale
        - valori numerici
        - anomalie
        - statistiche di base
        - consistenza dataset
    """

    FIELD_ORDER = [
        "EventID", "Time", "Latitude", "Longitude", "Depth_Km",
        "Author", "Catalog", "Contributor", "ContributorID",
        "MagType", "Magnitude", "MagAuthor",
        "EventLocationName", "EventType"
    ]

    def analyze_file(self, file_path: str, content: str) -> Dict:
        """
        Analizza un singolo file INGV (TXT/CSV).
        Riconosce header a colonne separati da | o ,.
        """

        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if not lines:
            return {"file": file_path, "error": "Empty file", "events": []}

        header = self._detect_header(lines[0])
        if not header:
            return {"file": file_path, "error": "Unrecognized INGV header", "events": []}

        events = []
        anomalies = []

        for row in lines[1:]:
            parsed = self._parse_row(row, header)
            if not parsed:
                anomalies.append(f"Invalid row: {row}")
                continue

            row_anomalies = self._detect_anomalies(parsed)
            anomalies.extend(row_anomalies)

            events.append(parsed)

        statistics = self._compute_statistics(events)

        return {
            "file": file_path,
            "total_events": len(events),
            "events": events,
            "anomalies": anomalies,
            "statistics": statistics
        }

    # -------------------------------------------------------------

    def _detect_header(self, header_line: str) -> List[str]:
        """Riconosce header INGV delimitato da | o da virgole."""
        if "|" in header_line:
            parts = [p.strip() for p in header_line.split("|")]
        elif "," in header_line:
            parts = [p.strip() for p in header_line.split(",")]
        else:
            return None

        # Validazione minima: almeno 5 colonne
        return parts if len(parts) >= 5 else None

    # -------------------------------------------------------------

    def _parse_row(self, row: str, header: List[str]) -> Dict:
        """Parsing robusto riga evento INGV."""
        delimiter = "|" if "|" in row else ","
        parts = [p.strip() for p in row.split(delimiter)]

        if len(parts) != len(header):
            return None

        return {header[i]: parts[i] for i in range(len(header))}

    # -------------------------------------------------------------

    def _detect_anomalies(self, event: Dict) -> List[str]:
        """Controlla valori anomali (magnitudo, profondità, lat/lon)."""

        anomalies = []

        # Magnitudo
        try:
            mag = float(event.get("Magnitude", "NaN"))
            if mag < -1 or mag > 10:
                anomalies.append(f"Anomalous magnitude: {mag}")
        except:
            anomalies.append("Non-numeric magnitude")

        # Profondità
        try:
            depth = float(event.get("Depth_Km", "NaN"))
            if depth < 0 or depth > 700:
                anomalies.append(f"Anomalous depth: {depth} km")
        except:
            anomalies.append("Non-numeric depth")

        # Coordinate
        try:
            lat = float(event.get("Latitude", "NaN"))
            lon = float(event.get("Longitude", "NaN"))
            if not (-90 <= lat <= 90):
                anomalies.append(f"Invalid latitude {lat}")
            if not (-180 <= lon <= 180):
                anomalies.append(f"Invalid longitude {lon}")
        except:
            anomalies.append("Invalid geographic coordinates")

        return anomalies

    # -------------------------------------------------------------

    def _compute_statistics(self, events: List[Dict]) -> Dict:
        """Calcola statistiche sismiche di base."""
        if not events:
            return {}

        mags = []
        depths = []

        for e in events:
            try:
                mags.append(float(e.get("Magnitude")))
            except:
                pass
            try:
                depths.append(float(e.get("Depth_Km")))
            except:
                pass

        stats = {
            "min_magnitude": min(mags) if mags else None,
            "max_magnitude": max(mags) if mags else None,
            "avg_magnitude": sum(mags) / len(mags) if mags else None,
            "min_depth": min(depths) if depths else None,
            "max_depth": max(depths) if depths else None,
            "avg_depth": sum(depths) / len(depths) if depths else None,
        }

        return stats