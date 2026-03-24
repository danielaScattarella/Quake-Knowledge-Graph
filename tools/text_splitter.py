# tools/text_splitter.py

"""
Text splitter ottimizzato per dataset INGV.
- NON spezza i record dei terremoti (una riga = un evento)
- Split solo per testi lunghi (> chunk_size) come descrizioni, note tecniche o articoli
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore


def split_text(text: str, chunk_size=800, chunk_overlap=100):
    """
    Split intelligente per testi sismologici:
    - Se è un dataset INGV (righe con delimitatore '|'), NON va splittato.
    - Se è un testo lungo narrativo, viene splittato normalmente.
    """

    # Caso 1: dataset con record a colonne → NON SPLITTARE
    if "|" in text and "\n" in text:
        # Identifica se almeno 3 colonne tipo INGV
        header = text.split("\n")[0]
        if header.count("|") >= 3:
            # Restituisce una sola chunk, senza spezzare i record
            return [text]

    # Caso 2: testo narrativo o molto lungo → uso splitter normale
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)