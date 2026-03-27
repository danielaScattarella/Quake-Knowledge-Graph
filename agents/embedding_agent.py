# agents/embedding_agent.py

import os
import uuid
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client import models
from config.config import qdrant, QDRANT_COLLECTION, EMBEDDING_DIM


class EarthquakeEmbeddingAgent:

    def __init__(self):
        self.collection = QDRANT_COLLECTION
        self.dim = EMBEDDING_DIM
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = [c.name for c in qdrant.get_collections().collections]
        except Exception:
            collections = []
        if self.collection not in collections:
            qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.dim,
                    distance=Distance.COSINE
                )
            )

    # ------------------------------------------------------
    # Embedding MiniLM
    # ------------------------------------------------------
    def _embed_with_miniLM(self, texts):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts, normalize_embeddings=False)
        return [list(e) for e in embeddings]

    # ------------------------------------------------------
    # Format event as short text
    # ------------------------------------------------------
    def _format_event_as_text(self, event: dict) -> str:
        return (
            f"Earthquake event. EventID {event.get('EventID')}. "
            f"Time {event.get('Time')}. "
            f"Latitude {event.get('Latitude')}, Longitude {event.get('Longitude')}. "
            f"Depth {event.get('Depth_Km')} km. "
            f"Magnitude {event.get('Magnitude')} {event.get('MagType')}. "
            f"Location {event.get('EventLocationName')}."
        )

    # ------------------------------------------------------
    # Add events with batching
    # ------------------------------------------------------
    def add_earthquake_events(self, events: list):
        texts, metadata = [], []
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

        BATCH_EMB = 200
        BATCH_UPSERT = 200

        for i in range(0, len(events), BATCH_EMB):
            batch_texts = texts[i:i+BATCH_EMB]
            batch_meta = metadata[i:i+BATCH_EMB]
            vectors = self._embed_with_miniLM(batch_texts)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=list(vec),
                    payload={"text": txt, **meta}
                )
                for vec, txt, meta in zip(vectors, batch_texts, batch_meta)
            ]

            for j in range(0, len(points), BATCH_UPSERT):
                qdrant.upsert(
                    collection_name=self.collection,
                    points=points[j:j+BATCH_UPSERT]
                )

    # ------------------------------------------------------
    # UNIVERSAL PARSER (ALWAYS RETURNS {"score":..., "event": dict})
    # ------------------------------------------------------
    def _parse_hits(self, hits):

        parsed = []

        for h in hits:

            # ✅ Case 1: ScoredPoint
            if hasattr(h, "payload"):
                parsed.append({
                    "score": getattr(h, "score", None),
                    "event": h.payload
                })
                continue

            # ✅ Case 2: Some versions return nested lists
            if isinstance(h, list):
                # Take the first element recursively
                return self._parse_hits(h)

            # ✅ Case 3: Tuple formats (old Qdrant)
            if isinstance(h, tuple):
                if len(h) == 3:
                    _id, score, payload = h
                elif len(h) == 2:
                    score, payload = h
                else:
                    continue

                # Ensure payload is dict (required by QA agent)
                if isinstance(payload, list):
                    # Some bizarre cases return payload wrapped in list
                    if len(payload) > 0 and isinstance(payload[0], dict):
                        payload = payload[0]

                parsed.append({
                    "score": score,
                    "event": payload
                })

        return parsed

    # ------------------------------------------------------
    # Search similar events
    # ------------------------------------------------------
    def search_similar_events(self, query_event: dict, top_k=5):
        query_text = self._format_event_as_text(query_event)
        vec = self._embed_with_miniLM([query_text])[0]

        hits = qdrant.query_points(
            collection_name=self.collection,
            query=vec,
            limit=top_k,
            with_payload=True
        )

        return self._parse_hits(hits.points if hasattr(hits, "points") else hits)


    # ------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------
    def semantic_search(self, text_query: str, top_k=5):
        vec = self._embed_with_miniLM([text_query])[0]

        hits = qdrant.query_points(
            collection_name=self.collection,
            query=vec,
            limit=top_k,
            with_payload=True
        )

                
            
        return self._parse_hits(hits.points if hasattr(hits, "points") else hits)
