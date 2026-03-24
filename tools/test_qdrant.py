# tools/test_qdrant_earthquakes.py

from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from config.config import QDRANT_COLLECTION

load_dotenv()

def test_qdrant_connection():
    """
    Test semplice per verificare:
    - connessione Qdrant
    - presenza della collezione sismica
    - numero di punti indicizzati
    """

    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    print("🔗 Connessione a Qdrant riuscita.\n")

    # Lista collezioni
    collections = client.get_collections()
    print("📚 Collezioni esistenti:")
    for c in collections.collections:
        print(" -", c.name)

    # Check collezione terremoti
    if QDRANT_COLLECTION not in [c.name for c in collections.collections]:
        print(f"\n⚠️ La collezione '{QDRANT_COLLECTION}' non esiste ancora.")
        print("   Verrà creata automaticamente dall’EarthquakeEmbeddingAgent.")
        return

    # Statistiche della collezione
    info = client.get_collection(QDRANT_COLLECTION)
    points = client.count(collection_name=QDRANT_COLLECTION).count

    print(f"\n🌋 Collezione terremoti: {QDRANT_COLLECTION}")
    print(f" - Modello vettoriale: {info.vectors}")
    print(f" - Punti indicizzati: {points}")

    print("\n✅ Test completato.")


if __name__ == "__main__":
    test_qdrant_connection()
