# agents/embedding_agent.py

import os
import uuid
from qdrant_client.models import VectorParams, Distance, PointStruct
from config.config import qdrant, QDRANT_COLLECTION, EMBEDDING_DIM


class EarthquakeEmbeddingAgent:
    """
    Embedding agent specifico INGV.
    - Converte eventi sismici in embeddings semantici
    - Indicizza in Qdrant con batching sicuro
    """

    def __init__(self):
        self.collection = QDRANT_COLLECTION
        self.dim = EMBEDDING_DIM
        self._ensure_collection()

    def _ensure_collection(self):
        """Crea la collezione Qdrant se non esiste."""
        try:
            collections = [c.name for c in qdrant.get_collections().collections]
        except Exception:
            collections = []

        if self.collection not in collections:
            qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
            )

    # ------------------------------------------------------
    #     EMBEDDING LOCALE (MiniLM)
    # ------------------------------------------------------
    def _embed_with_miniLM(self, texts):
        """
        Usa MiniLM locale per embedding,
        perché affidabile e veloce in ambiente offline.
        """
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, normalize_embeddings=False)
        return [list(e) for e in embeddings]

    # ------------------------------------------------------
    #     FORMATTAZIONE EVENTO IN TESTO BREVE (IMPORTANTE)
    # ------------------------------------------------------
    def _format_event_as_text(self, event: dict) -> str:
        """
        Trasforma un singolo evento INGV in un testo semantico breve.
        (NON inserire dataset interi → previene payload giganteschi)
        """
        return (
            f"Earthquake event. EventID {event.get('EventID')}. "
            f"Time {event.get('Time')}. "
            f"Latitude {event.get('Latitude')}, Longitude {event.get('Longitude')}. "
            f"Depth {event.get('Depth_Km')} km. "
            f"Magnitude {event.get('Magnitude')} {event.get('MagType')}. "
            f"Location {event.get('EventLocationName')}."
        )

    # ------------------------------------------------------
    #     ADD EVENTS — CON FIX BATCHING QDRANT
    # ------------------------------------------------------
    def add_earthquake_events(self, events: list):
        """
        Inserisce gli eventi INGV in Qdrant evitando payload troppo grandi.
        Qdrant ha limite payload JSON: 32MB → usiamo batch piccoli.
        """

        # 1️⃣ Format text & metadata (tutto conciso)
        texts = []
        metadata = []

        for e in events:
            texts.append(self._format_event_as_text(e))
            metadata.append({
                "EventID": e.get("EventID"),
                "Time": e.get("Time"),
                "Latitude": e.get("Latitude"),
                "Longitude": e.get("Longitude"),
                "Depth_Km": e.get("Depth_Km"),
                "Magnitude": e.get("Magnitude"),
                "MagType": e.get("MagType"),
                "Location": e.get("EventLocationName"),
                "EventType": e.get("EventType"),
            })

        # 2️⃣ Embedding in batch per evitare uso RAM eccessivo
        BATCH_EMB = 200
        BATCH_UPSERT = 200

        for i in range(0, len(events), BATCH_EMB):
            batch_texts = texts[i:i + BATCH_EMB]
            batch_meta = metadata[i:i + BATCH_EMB]

            vectors = self._embed_with_miniLM(batch_texts)

            # Crea i punti
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=list(vec),
                    payload={"text": txt, **meta}
                )
                for vec, txt, meta in zip(vectors, batch_texts, batch_meta)
            ]

            # 3️⃣ UPLOAD QDRANT IN SOTTO-BATCH: FIX 32MB PAYLOAD
            for j in range(0, len(points), BATCH_UPSERT):
                sub_points = points[j:j + BATCH_UPSERT]
                qdrant.upsert(
                    collection_name=self.collection,
                    points=sub_points
                )

    # ------------------------------------------------------
    #               SEARCH PER TERREMOTI
    # ------------------------------------------------------
    def search_similar_events(self, query_event: dict, top_k=5):
        query_text = self._format_event_as_text(query_event)
        vec = self._embed_with_miniLM([query_text])[0]

        hits = qdrant.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=top_k,
            append_payload=True
        )

        return [{"score": getattr(h, "score", None), "event": h.payload} for h in hits]

    # ------------------------------------------------------
    #               SEARCH PER TESTO
    # ------------------------------------------------------
    def semantic_search(self, text_query: str, top_k=5):
        vec = self._embed_with_miniLM([text_query])[0]

        hits = qdrant.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=top_k,
            append_payload=True
        )

        return [{"score": getattr(h, "score", None), "event": h.payload} for h in hits]