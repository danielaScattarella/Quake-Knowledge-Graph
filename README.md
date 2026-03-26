

<img width="1024" height="1024" alt="Quake Knowledge Graph mi fai un immagine che descr (1)" src="https://github.com/user-attachments/assets/f97b5034-c0f4-42a5-a03d-f25af60626ea" />

The system is designed to allow the intelligent, automated analysis of INGV seismic data. The goal is to enable agents to collaborate tra loro by analysing the datasets dei terremoti, processing, and enriching them to generate explanations, reports, and answers to questions about seismic phenomena. Built with LangGraph, integrated with **Cohere LLM**, **MiniLM**, and **Qdrant vector** database.

# Project Objectives
This system is based on advanced multi-agent architectures:

- **Agent Orchestration**: Directed graph execution using LangGraph with persistent state management
- **Multi-Agent Architecture**: Distributed agent design with task-level specialisation and coordination
- **Tool Integration**: Custom toolchain augmenting LLM capabilities with deterministic operations
- **Semantic Search**: Embedding-based similarity matching for contextual data access
- **LLM Integration**: Cohere APIs for generative tasks, structured analysis, and recommendation pipelines

# Quick Start
## Prerequisites

- Python 3.10+
- API Keys for: Cohere - LLM API
- Podman

**Installation**
1. Clone and setup environment:

```bash
cd quake-knowledge-graph
python -m venv venv
venv\Scripts\activate
```
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (.env file):

```bash
Qdrant Cloud
QDRANT_URL = http://localhost:6333

QDRANT_API_KEY = admin-key
QDRANT_COLLECTION = earthquake_events
EMBEDDING_DIM = 384

Cohere
COHERE_API_KEY=your_api_key
```

# Architecture Overview

## System Architecture Diagram


<img width="832" height="454" alt="architettura multi agente" src="https://github.com/user-attachments/assets/03c310b3-5fad-40fe-8c0f-0ed89780ae04" />

## Multi-Agent System
1. **Repository Analyzer Agent** - Extracts repository structure, files, metadata, and detects project type
2. **Embedding Agent** - Manages semantic embeddings via Jina and stores in Qdrant for intelligent retrieval
3. **Metadata Recommender Agent** - Suggests project metadata, titles, and relevant tags
4. **Content Improver Agent** - Enhances README and documentation using LLM-powered suggestions
5. **Reviewer Agent** - Validates completeness and identifies gaps in documentation
6. **QA Agent** - Answers questions about repositories using vector similarity search
7. **Article Generator Agent** - Creates publication-ready content with structured narratives

## Tools
1. **File Loader Tool** – Upload INGV seismic datasets in TXT, CSV, XML, JSON, or ZIP formats and perform structural parsing.
2. **Text Splitter Tool** – Splits technical texts into optimised chunks (800 tokens / 100 overlaps) for embedding or analysis.
3. **Data Analyzer Tool** – Analyse the structure of seismic datasets and detect fields, formats, anomalies, and patterns.
4. **Web Search Tool** – Local search tool for INGV earthquake datasets. Performs structured queries on magnitude, depth, geographical area, time ranges, and types of events.

# Agent Roles & Responsibilities
## Agent Interaction Pipeline

<img width="2597" height="733" alt="Pipline" src="https://github.com/user-attachments/assets/d60a28a9-1a4f-4636-9c77-65dde31536a2" />

### Dataset Analyser Agent
The Dataset Analyser Agent is the entry point of the entire seismological pipeline. It is responsible for examining an INGV dataset, managing both directories and ZIP archives, and automatically identifying the files in TXT format of the official seismic catalogues. Once the files have been extracted, the agent reads the contents line by line, recognises the standard INGV columns, and filters out invalid or incomplete rows. Transform each event into a structured record with geophysical fields, including magnitude, depth, coordinates, event type, and authorial metadata. During processing, it verifies data consistency and identifies anomalies. When finished, it produces a complete statistical summary, including the minimum, maximum, and average magnitude; min/max/avg depth; and the total number of valid events. It also returns the entire list of extracted events, the number of files processed, and the path of the normalised dataset. Its output becomes the solid foundation on which the other agents in the multi-agent pipeline are grafted.

### Embedding Agent
The Embedding Agent is responsible for transforming each INGV seismic event into a semantic vector representation for intelligent search. Upon launch, the agent verifies that the Qdrant collection dedicated to events exists; if it does not, it automatically creates it with the correct carrier size. Each event is converted into short, informative text that summarises magnitude, location, depth, event type, and essential metadata. These texts are then processed locally through the MiniLM model of SentenceTransformers, a fast and effective solution even in an offline environment. The generated embeddings are grouped into small batches to avoid exceeding payload limits and optimise memory usage. Next, the agent constructs vector points complete with descriptive payloads and inserts them into Qdrant in controlled micro-batches. Once the collection is populated, the agent allows you to perform semantic searches of similar events, either based on another event or on a free-text query. This enables exploratory analysis, clustering, and intelligent queries on earthquake characteristics.

### Metadata Recommender Agent
The Metadata Recommender Agent analyses the already processed seismic dataset and generates intelligent metadata that enriches the geophysical content provided by INGV. Starting from the list of events and the statistical values extracted from the Dataset Analyser, the agent builds a series of synthetic titles that best represent the extent and intensity of the seismic sequence. It then produces a one-sentence summary, useful for compact descriptions in reports or information systems. In parallel, it generates thematic tags based on magnitude, average depth, and characteristic locations such as Campi Flegrei, Etna, or the Apennines, allowing rapid classification of the dataset. The agent also elaborates reasoning, i.e., a textual explanation of the choices made and the seismological classification of the data. The goal is to provide a set of metadata that is clear, consistent, and immediately usable by Content Improver, Reviewer, and Article Generator in the multi-agent pipeline. In this way, the agent contributes to the scientific and narrative contextualization of seismic information.

### Content Improver Agent
The Content Improver Agent intervenes after the seismic dataset has been analysed and enriched with metadata, aiming to transform raw numbers and values into clear, readable, and technically accurate text. Starting from the statistical summary (min/max/average magnitude, min/max/average depth, number of events) and the metadata suggested by the Metadata Recommender, the agent builds a concise description that presents the entire dataset in a fluid, understandable way. It integrates the main information into a coherent paragraph, explaining the variability in magnitude, the distribution of hypocentral depths, and the geographical spread of the INGV-recorded events. The result is improved text that is ready to be used in reports, UI panels, or as the basis for the introductory section of the final seismological article. The agent also returns a summary of metadata usage and the number of events processed, enabling subsequent steps in the pipeline to track context.

### Reviewer Agent
The Reviewer Agent serves as the scientific validator for the entire INGV seismic dataset, assessing its quality, reliability, and completeness. After receiving the events processed by the Dataset Analyzer and any enhanced text from the Content Improver, it performs a series of structured checks to identify critical errors, missing fields, and inconsistencies in geophysical values. In particular, it analyses the presence of fundamental fields such as time of origin, coordinates, magnitude, and depth, verifying that they are always available and correctly formatted. It also identifies numerical anomalies such as out-of-range depth or unrealistic magnitude, and produces targeted alerts to be submitted to the user or to the next steps in the pipeline. In addition to checks, it calculates a dataset health score by penalising serious problems, warnings, and missing fields. The Reviewer also produces recommendations and potential improvement actions, ranks them by priority, and facilitates the dataset review. This assessment is the foundation for the QA Agent and for generating the final report.

### QA Agent
The QA Agent is the agent dedicated to answering questions about INGV seismic data, integrating semantic search and LLM generation. When the agent receives a question from the user, it first performs a vector search in Qdrant using the Embedding Agent to identify the most relevant events based on the query's semantic content. Starting from the results, it builds a synthetic scientific context, reporting key information such as magnitude, depth, coordinates, location, and type of event for each event. This context is then transformed into a specialised geophysical prompt, designed to guide the LLM model towards precise answers consistent with real data. The agent then uses the Cohere model to generate a concise, scientific, evidence-based response from the dataset. The QA Agent thus allows you to query the entire seismic archive in natural language, obtaining explanations, summaries, and targeted information on the most significant events. It is a fundamental component to make the dataset searchable intelligently and immediately.

### Article Generator
The Article Generator Agent is the component of the pipeline responsible for producing complete seismological articles, scientific reports, and other informative content based on INGV data. Use an advanced LLM model to transform the results generated by other agents — dataset analysis, metadata, reviews, and summaries — into structured, clear, publish-ready text. The agent receives context consisting of seismic statistics, magnitude ranges, spatial distributions, and any user inputs, such as requests for weekly reports or analysis of specific areas. Based on these elements, it builds a detailed prompt that guides the LLM model towards a formal and scientific style, dividing the content into coherent sections and subsections.

## Performance Metrics
### 🕒 Processing Speed

| Operation               | Mean Time   | Std Dev     | P95        |
|-------------------------|-------------|-------------|------------|
| Dataset Analysis        | 0.0227 s    | 0.0114 s    | 0.0189 s   |
| Embedding Generation    | 37.52 s     | 40.55 s     | 18.34 s    |
| Metadata Recommendation | 0.00028 s   | 0.00015 s   | 0.00024 s  |
| Content Improver        | 0.00002 s   | 0.00001 s   | 0.000015 s |
| Reviewer                | 0.00615 s   | 0.00138 s   | 0.00616 s  |
| Vector Search (Qdrant)  | 3.30 s      | 0.27 s      | 3.57 s     |

### 💾 Resource Usage

| Metric                    | Value      | Comment                                             |
|---------------------------|------------|-----------------------------------------------------|
| Dataset Memory (peak)     | ~1.47 MB   | Lightweight INGV TXT parsing                        |
| Embedding Memory (peak)   | ~10.33 MB  | Expected footprint for MiniLM (sentence-transformers) |
| Embedding Memory (current)| ~4.25 MB   | Model in RAM without GPU overhead                   |


The INGV multi‑agent seismic analysis pipeline demonstrates robust performance and stable execution across all stages. Dataset parsing is extremely fast (22 ms on average), confirming that the INGV TXT loader is well-optimised for structured seismic catalogues. The most computationally expensive operation is embedding generation, which takes approximately 37 seconds due to the combination of MiniLM inference and Qdrant insertions running inside a Podman virtualised environment. Metadata generation, content improvement, and dataset review modules are highly efficient, with execution times close to zero, as they rely on lightweight transformations and statistical summarisation. Vector search operations in Qdrant average around 3.3 seconds, which is normal considering the overhead of MiniLM inference and the network path between the host and the Podman VM. Memory usage is stable and predictable, with MiniLM consuming roughly 10 MB peak RAM — consistent with CPU‑only sentence-transformers models.

## Performance Testing

Run benchmark performance:

```bash
python tools/benchmark_performance.py
```

# 📁 Project Structure
```bash
├── agents/ # 7 specialized agents (INGV)
│ ├── dataset_analyzer.py # Analysis of seismic datasets (INGV formats)
│ ├── embedding_agent.py # Embedding on geophysical & retrieval data
│ ├── metadata_recommender.py # Metadata suggestion (event, magnitude...)
│ ├── content_improver.py # Improved event descriptions
│ ├── reviewer.py # Scientific validation & scoring
│ ├── qa_agent.py # Q&A on INGV earthquakes
│ └── article_generator.py # Generation of seismological reports/studies
│
├── tools/ # 5 support tools
│ ├── file_loader.py # Dataset upload
│ ├── text_splitter.py # Chunking technical texts (800 tokens / 100 overlap)
│ ├── data_analyzer.py # Structural analysis of seismological datasets
│ ├── web_search.py # Integration with public data (INGV, EMSC, USGS)
│ ├── test_ingv_embeddings.py # Test embedding (INGV vector service)
│ ├── test_qdrant.py # Vector database test
│ └── benchmark_performance.py # Benchmark pipeline/LLM
│
├── orchestrator/ # Flow orchestration
│ ├── langgraph_flow.py # Pipeline LangGraph
│ └── simple_pipeline.py # Simplified alternative pipeline
│
├── config/
│ └── config.py # Service Configurations (INGV API, Cohere, Qdrant)
│
├── data/
| ├── small_earthquakes # Small dataset INGV used for gui and test
│ └── sample_earthquakes/ # Dataset INGV
│
├── main.py # Entry point CLI
├── app.py # GUI
├── requirements.txt # Requirements
├── .env # Environment variable templates
├── earthquakes.kube.yaml # Podman Services (Qdrant, API, LLM)
├── Dockerfile # Docker app
├── LICENSE # License
└── README.md # Project documentation
```

## 🔧 Technology Stack

### Core Framework
1. **Python 3.10+** - Programming language
2. **LangGraph (0.0.x)** - Multi-agent orchestration and workflow
3. **LangChain (0.1.x)** - Text processing, utilities, and tool integration

### AI/ML Services
1. **Cohere API (5.20.0)** - Large Language Models for generation and analysis
2. **MiniLM** - Text embeddings
3. **Qdrant Cloud (1.6.0)** - Vector database for semantic search

### Key Libraries
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for API calls
- **streamlit** - Web interface (optional)
- **sentence-transformers** - Local embedding fallback
- **cohere** - LLM SDK
- **qdrant-client** - Vector database client

## Testing & Quality Assurance
```bash
Test LLM and embeddings
python tools/test_llm_embeddings.py

Test Qdrant integration
python tools/test_qdrant.py
```
### Test Coverage
1. Unit Tests: Agent-specific functionality
2. Integration Tests: End-to-end pipeline
3. Performance Tests: Benchmarking and profiling

## Example Outputs

Suggested metadata
```bash
{
  "title_alternatives":[
          0:"Seismic Activity Summary from INGV Records"
          1:"INGV Earthquake Dataset Analysis"
          2:"Seismic Events Report (M 0.3–1.7)"
  ]
 "one_line_summary":"Dataset containing 6 INGV-recorded earthquakes, with magnitudes ranging from 0.3 to              1.7 (average 1.05)."
 "tags":[
         0:"microseismicity"
         1:"intermediate-depth"
         2:"geophysics"
         3:"campi-flegrei"
         4:"INGV"
         5:"earthquake"
         6:"seismic"
   ]
   "reasoning":{
          "magnitude_range":"Magnitude ranges from 0.3 to 1.7, avg 1.05."
          "depth_range":"Depth ranges from 1.9 km to 24.5 km."
          "classification_basis":"Tags and metadata are derived from earthquake intensity, depth category, and   notable locations contained in the dataset."
    }      
  }
```

Enhanced content
```bash
{
    "improved_text":"The dataset contains 6 analyzed seismic events. Earthquake magnitudes range from 0.3 to 1.7, with an average value of 1.02. Hypocentral depths span from 1.9 to 24.5 km (average: 11.35 km). The recorded events are distributed across multiple areas, showing spatial patterns and parameter variability consistent with typical regional micro‑seismic activity."
    "metadata_used":{
    "title_alternatives":[
              0:"Seismic Activity Summary from INGV Records"
              1:"INGV Earthquake Dataset Analysis"
              2:"Seismic Events Report (M 0.3–1.7)"
     ]
     "one_line_summary":"Dataset containing 6 INGV-recorded earthquakes, with magnitudes ranging from 0.3 to 1.7 (average 1.05)."
     "tags":[
             0:"microseismicity"
             1:"intermediate-depth"
             2:"geophysics"
             3:"campi-flegrei"
             4:"INGV"
             5:"earthquake"
             6:"seismic"
        ]
       "reasoning":{
            "magnitude_range":"Magnitude ranges from 0.3 to 1.7, avg 1.05."
            "depth_range":"Depth ranges from 1.9 km to 24.5 km."
            "classification_basis":"Tags and metadata are derived from earthquake intensity, depth category, and notable locations contained in the dataset."
       }
  }
```

  Scientific review
```bash
  {
 "issues":[]
 "recommendations":[]
 "validation_results":{
      "critical_issues":0
      "warnings":0
     "recommendations_count":0
     "completeness":{
           "EventID":true
           "Time":true
           "Latitude":true
           "Longitude":true
           "Magnitude":true
           "Depth_Km":true
           "Location":true
      }
     "overall_health":100
     "numerical_anomalies":[]
     "total_events":6
 }
"action_items":[]
"priority_fixes":[
       0:"Migliorare descrizioni località"
       1:"Aggiungere metadati mancanti"
  ]
 }
```
## 🔐 Security & Best Practices
- API Keys: Store in .env, never commit to repository
- Environment Variables: Use python-dotenv for configuration
- Error Handling: Graceful fallbacks for service failures
- Rate Limiting: Respects API rate limits to avoid throttling
- Logging: Detailed error messages for debugging
- Data Privacy: Repositories stored locally, not sent to external services (except embeddings)

## 🚀 Deployment
### Podman Deployment
```bash
podman machine init --now --user-mode-networking
podman machine start
podman build -t earthquake-agent .
podman play kube earthquakes.kube.yaml
```

## Acknowledgments
Built with:

- LangChain ecosystem for agent framework
- Qdrant for vector database infrastructure
- Cohere for LLM capabilities



