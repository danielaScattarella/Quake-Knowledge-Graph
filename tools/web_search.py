# tools/web_search.py

from typing import List, Dict, Any
from datetime import datetime


class EarthquakeSearchTool:
    """
    Strumento di ricerca locale per dataset di terremoti INGV.
    NON usa Internet.
    Esegue interrogazioni strutturate su:
      - magnitudo
      - profondità
      - area geografica
      - range temporali
      - tipi di eventi
    """

    def search_by_magnitude(self, events: List[Dict], min_mag: float = None, max_mag: float = None) -> List[Dict]:
        """Ritorna eventi compresi nel range di magnitudo."""
        results = []
        for e in events:
            try:
                m = float(e.get("Magnitude", "NaN"))
                if (min_mag is None or m >= min_mag) and (max_mag is None or m <= max_mag):
                    results.append(e)
            except:
                continue
        return results

    def search_by_depth(self, events: List[Dict], min_depth: float = None, max_depth: float = None) -> List[Dict]:
        """Ritorna eventi compresi nel range di profondità."""
        results = []
        for e in events:
            try:
                d = float(e.get("Depth_Km", "NaN"))
                if (min_depth is None or d >= min_depth) and (max_depth is None or d <= max_depth):
                    results.append(e)
            except:
                continue
        return results

    def search_by_location(self, events: List[Dict], keyword: str) -> List[Dict]:
        """Ritorna eventi con località che contengono la keyword."""
        kw = keyword.lower()
        return [e for e in events if kw in str(e.get("EventLocationName", "")).lower()]

    def search_by_event_type(self, events: List[Dict], event_type: str) -> List[Dict]:
        """Ritorna eventi filtrati per EventType (es: 'earthquake', 'quarry blast')."""
        et = event_type.lower()
        return [e for e in events if et in str(e.get("EventType", "")).lower()]

    def search_by_time_range(self, events: List[Dict], start: str = None, end: str = None) -> List[Dict]:
        """
        Cerca eventi in un intervallo temporale.
        start/end devono essere in formato ISO (es: '2025-02-11T00:00:00')
        """
        def parse(t):
            try:
                return datetime.fromisoformat(t.replace("Z", ""))
            except:
                return None

        results = []
        dt_start = parse(start) if start else None
        dt_end = parse(end) if end else None

        for e in events:
            dt = parse(e.get("Time", ""))
            if not dt:
                continue

            if (dt_start is None or dt >= dt_start) and (dt_end is None or dt <= dt_end):
                results.append(e)

        return results

    def stats_summary(self, events: List[Dict]) -> Dict[str, Any]:
        """Ritorna statistiche rapide di magnitudo e profondità."""
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

        return {
            "count": len(events),
            "min_magnitude": min(mags) if mags else None,
            "max_magnitude": max(mags) if mags else None,
            "average_magnitude": sum(mags) / len(mags) if mags else None,
            "min_depth": min(depths) if depths else None,
            "max_depth": max(depths) if depths else None,
            "average_depth": sum(depths) / len(depths) if depths else None
        }