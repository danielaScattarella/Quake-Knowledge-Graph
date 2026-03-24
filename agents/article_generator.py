from config.config import co


class EarthquakeArticleGeneratorAgent:
    """
    Genera articoli, report e pubblicazioni basati sui dati dei terremoti INGV.
    Produce contenuti in stile scientifico/divulgativo seguendo le istruzioni dell’utente.
    """

    def __init__(self):
        self.model = "command-a-03-2025"

    def generate(self, dataset_context: str, user_instructions: str, dataset_description: str = "") -> str:
        """
        dataset_context: testo generato dal dataset_analyzer e dagli agenti
        user_instructions: cosa deve produrre l’articolo (es. “report settimanale”, “analisi evento", ecc.)
        dataset_description: contesto opzionale dell’utente
        """

        prompt = f"""
You are an expert seismology writer specialized in creating publication-ready articles about earthquakes,
with a focus on INGV datasets and Italian seismic activity.

Your task is to generate a clear, accurate, well‑structured scientific article based on the provided INGV data
and the user's instructions.

Guidelines:
1. Write as a seismology expert, using correct terminology (magnitude, hypocenter, epicenter, depth, sequence, swarm, etc.)
2. Structure the article with clear sections and subsections (e.g., Overview, Seismic Parameters, Event Distribution, Interpretation…)
3. Insert [TODO: ...] for any section requiring manual refinement or missing data
4. Use Markdown formatting
5. Maintain a balance between technical precision and readability
6. Use only the information provided in the dataset context—do not hallucinate
7. Embed numerical values (magnitude range, depth range, event count, etc.) when present

INGV DATA CONTEXT:
{dataset_context}

DATASET DESCRIPTION (if provided):
{dataset_description if dataset_description else "No additional description provided"}

USER INSTRUCTIONS FOR ARTICLE:
{user_instructions}

Please generate a complete, structured scientific article following the user's instructions.
Include [TODO: ...] tags where necessary.
"""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=4096
            )
            return response.text.strip()

        except Exception as e:
            raise Exception(f"Failed to generate earthquake article: {str(e)}")

    # ----------------------------------------------------------------------

    def generate_outline(self, dataset_context: str, user_instructions: str) -> str:
        """
        Produce un outline dettagliato dell’articolo, utile prima della generazione completa.
        """

        prompt = f"""
You are an expert in seismology and scientific communication.
Generate a detailed outline (in Markdown) for an article based on the INGV earthquake dataset and the user's instructions.

Use hierarchical structure:
- Main sections
    - Subsections
        - Optional bullet points

INGV DATA CONTEXT:
{dataset_context}

USER INSTRUCTIONS:
{user_instructions}

Produce a comprehensive outline suitable for seismological reporting or publication.
"""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=2048
            )
            return response.text.strip()

        except Exception as e:
            raise Exception(f"Failed to generate outline: {str(e)}")

    # ----------------------------------------------------------------------

    def extract_summary(self, event_text: str) -> str:
        """
        Estrae un riassunto breve (2-3 frasi) da un singolo evento o da un blocco di eventi.
        """

        prompt = f"""
Summarize the following seismic event information in 2–3 scientific sentences:

{event_text}

Summary:
"""

        try:
            response = co.chat(
                message=prompt,
                model=self.model,
                max_tokens=200
            )
            return response.text.strip()

        except Exception:
            return "[TODO: Add manual summary]"