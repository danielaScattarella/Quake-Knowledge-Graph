import os
from dotenv import load_dotenv
import cohere

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


def test_llm():
    """
    Test LLM con domanda sismologica, non generica.
    """
    prompt = (
        "You are a seismology assistant. "
        "Explain in one paragraph what a magnitude 3 earthquake represents "
        "in terms of energy release and typical perceptibility by the population."
    )

    response = co.chat(
        message=prompt,
        model="command-a-03-2025",
        max_tokens=200
    )

    print("LLM Response:")
    print(response.text)


def test_embeddings():
    """
    Test embedding su un evento INGV realistico.
    """
    example_event = (
        "Earthquake event. EventID 41671662. "
        "Occurred at 2025-02-11T01:50:01.670000. "
        "Location latitude 40.829833, longitude 14.140167. "
        "Depth 1.9 km. Magnitude 1.7 Md. "
        'Epicenter near "Campi Flegrei".'
    )

    response = co.embed(
        model="embed-english-v3.0",
        input_type="search_document",
        texts=[example_event]
    )

    print("\nEmbedding (first 10 values):")
    print(response.embeddings[0][:10])


if __name__ == "__main__":
    test_llm()
    test_embeddings()