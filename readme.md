# README.md

# Hybrid Repo AI Agent

A prototype repository-aware AI orchestration system designed for codebase understanding, semantic retrieval, graph-based context expansion, repository-level reasoning, and multi-file code editing.

The project started from a simple issue:
local coding models became very slow and unreliable while handling repository-level tasks.

Instead of only scaling model size, the architecture evolved toward:
- hybrid local + cloud inference
- repository indexing
- semantic retrieval
- graph traversal
- reranking
- context orchestration
- multi-file patch generation
- repository memory systems

The goal of the project is to experiment with modern AI infrastructure concepts used in repository-level AI systems.

---

# Features

- Hybrid local + cloud orchestration
- Semantic repository retrieval
- Repository indexing with embeddings
- Weighted graph traversal
- DFS-based context expansion
- Retrieval reranking
- Multi-file patch generation
- Repository-aware prompting
- Incremental indexing concepts
- Persistent repository memory
- Debug tracing pipelines
- Context-building orchestration
- Local-first inference strategy

---

## Understanding the Project

For deeper architecture and workflow explanation, read [understanding.md](./understanding.md)

---
# Architecture

```text
User Prompt
    ↓
SIMPLE vs COMPLEX Classification
    ↓
Semantic Retrieval
    ↓
Graph Expansion
    ↓
Reranking
    ↓
Context Builder
    ↓
Local Model OR Cloud Model
    ↓
Response / Patch Generation
```

---

# Project Structure

```text
hybrid-agent/
│
├── data/
│   ├── file_embeddings_cache.json
│   ├── prototypes_cache.json
│   ├── prototypes.json
│   ├── repo_index.json
│
├── editing/
│   ├── __init__.py
│   ├── diff_viewer.py
│   ├── file_writer.py
│   ├── patch_generator.py
│
├── memory/
│   ├── __init__.py
│   ├── memory_manager.py
│
├── models/
│   ├── __init__.py
│   ├── classifier.py
│   ├── cloud_model.py
│   ├── local_model.py
│
├── repo/
│   ├── __init__.py
│   ├── context_builder.py
│   ├── graph_builder.py
│   ├── graph_traversal.py
│   ├── mode_classifier.py
│   ├── repo_indexer.py
│   ├── repo_state.py
│   ├── repo_summary.py
│   ├── reranker.py
│   ├── retrieval.py
│   ├── scanner.py
│
├── tracing/
│   ├── __init__.py
│   ├── debug.py
│
├── .env
├── .gitignore
├── config.py
├── debug_key.py
├── main.py
├── README.md
├── requirements.txt
```

---

# Dependencies

| Dependency | Purpose |
|---|---|
| ollama | Local LLM inference |
| openai | OpenRouter/OpenAI cloud inference |
| sentence-transformers | Semantic embeddings |
| python-dotenv | Environment variable loading |

---

# Local + Cloud Models

## Local Model
Used for:
- lightweight reasoning
- faster responses
- lower latency tasks
- smaller repository operations

## Cloud Model
Used for:
- deeper reasoning
- architecture-level understanding
- larger repository tasks
- complex multi-file operations

---

# Retrieval Pipeline

The retrieval system combines:
- semantic retrieval
- graph expansion
- weighted traversal
- reranking
- structured context building

This improves:
- repository awareness
- contextual relevance
- multi-file understanding
- architectural coherence

---

# Editing Pipeline

The editing system supports:
- repository-aware patch generation
- multi-file modification concepts
- diff visualization
- structured file updates

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/hybrid-agent.git
cd hybrid-agent
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Ollama

Download and install Ollama from:

https://ollama.com/download

After installation, pull the local model:

```bash
ollama pull qwen2.5-coder:1.5b
```

You can replace this model later inside `config.py`.

---

## 5. Create `.env` File

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

## 6. Run the Project

```bash
python main.py
```

---

# First Startup

On first startup the system will:
- scan the repository
- generate embeddings
- build repository memory
- create retrieval indexes

This may take some time depending on repository size.

---

# Notes

- Local inference uses Ollama
- Cloud inference uses OpenRouter
- Runtime cache files are generated automatically
- Repository indexes are stored locally and should not be committed to git

---

# Recommended

Recommended Python version:

```text
Python 3.10+
```

---

# Current Status

This project is still experimental and under active development.

The system is focused on learning and experimenting with:
- AI orchestration systems
- retrieval pipelines
- repository-level reasoning
- graph-based context expansion
- multi-file AI editing systems

Future improvements may include:
- adaptive retrieval
- AST-aware patching
- planner-agent systems
- vector databases
- async orchestration
- smarter graph traversal
- dynamic retrieval policies
- improved reranking systems