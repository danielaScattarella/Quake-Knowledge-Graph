# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Earthquake Multi‑Agent Assistant
# Dockerfile per Podman
# ---------------------------------------------------------

FROM python:3.10-slim

# Evita errori interattivi in Podman
ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------
# Installazione dipendenze di sistema
# ---------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Directory applicazione
# ---------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------
# Installazione dipendenze Python
# ---------------------------------------------------------
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# Copia codice
# ---------------------------------------------------------
COPY . /app

# ---------------------------------------------------------
# Variabili di ambiente
# ---------------------------------------------------------
ENV QDRANT_URL="http://qdrant:6333"
ENV QDRANT_API_KEY="admin-key"
ENV QDRANT_COLLECTION="earthquake_events"
ENV EMBEDDING_DIM=384
ENV COHERE_API_KEY=""

COPY . /app
COPY data/ /app/data/



# ---------------------------------------------------------
# Comando default:
# esegue la pipeline dei terremoti sul dataset di esempio
# ---------------------------------------------------------
CMD ["python", "main.py", "data"]