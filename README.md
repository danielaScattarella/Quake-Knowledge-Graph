The system is designed to allow the intelligent, automated analysis of INGV seismic data. The goal is to enable agents to collaborate tra loro by analysing the datasets dei terremoti, processing, and enriching them to generate explanations, reports, and answers to questions about seismic phenomena. Built with LangGraph, integrated with **Cohere LLM**, **MiniLM**, and **Qdrant vector** database.

# Project Objectives
This system is based on advanced multi-agent architectures:

**Agent Orchestration**: Directed graph execution using LangGraph with persistent state management
**Multi-Agent Architecture**: Distributed agent design with task-level specialisation and coordination
**Tool Integration**: Custom toolchain augmenting LLM capabilities with deterministic operations
**Semantic Search**: Embedding-based similarity matching for contextual data access
**LLM Integration**: Cohere APIs for generative tasks, structured analysis, and recommendation pipelines

# Quick Start
## Prerequisites
Python 3.10+
API Keys for: Cohere - LLM API
Podman

**Installation**
Clone and setup environment:

```bash
cd quake-knowledge-graph
python -m venv venv
venv\Scripts\activate
```

