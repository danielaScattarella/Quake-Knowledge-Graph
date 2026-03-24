# agents/qa_agent.py

from config.config import co
from agents.embedding_agent import EarthquakeEmbeddingAgent


class EarthquakeQAAgent:
    """
    Risponde a domande sui terremoti INGV
    combinando embeddings + generazione LLM.
    """

    def __init__(self):
        self.emb = EarthquakeEmbeddingAgent()

    def answer(self, query: str, top_k=5):
        """
        Esegue ricerca semantica sugli eventi sismici
        e genera una risposta in linguaggio naturale
        utilizzando i dati ottenuti come contesto.
        """

        # Ricerca semantica nei terremoti INGV
        hits = self.emb.semantic_search(query, top_k=top_k)

        # Costruzione del contesto scientifico
        context_blocks = []
        for h in hits:
            ev = h["event"]
            context_blocks.append(
                f"EventID: {ev.get('EventID')}, "
                f"Time: {ev.get('Time')}, "
                f"Magnitude: {ev.get('Magnitude')} ({ev.get('MagType')}), "
                f"Depth: {ev.get('Depth_Km')} km, "
                f"Location: {ev.get('Location')}, "
                f"Type: {ev.get('EventType')}"
            )

        context = "\n".join(context_blocks)

        # Prompt geofisico specializzato
        prompt = (
            "You are a seismic analysis assistant specialized in INGV earthquake data.\n"
            "Use ONLY the information provided in the context.\n"
            "Respond concisely, scientifically, and clearly.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )

        # LLM Cohere
        resp = co.chat(
            message=prompt,
            model="command-a-03-2025",
            max_tokens=350
        )

        return resp.text.strip()
    