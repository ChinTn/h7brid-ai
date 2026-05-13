# Hybrid Repo AI Agent

A repository-aware AI assistant for code understanding, retrieval, and automated patch generation.

This project combines local and cloud AI models, semantic retrieval, repository indexing, and file-editing workflows to support natural language code requests and repository edits.

## 🚀 What it does

- Indexes repository files with embeddings using `ollama`
- Classifies user prompts into general chat or repo-aware editing mode
- Retrieves relevant files using semantic similarity
- Generates code patches using a cloud model
- Shows diffs and optionally applies changes to files
- Stores recent conversation state for improved context

## 📦 Key features

- Repo indexing with cached embeddings
- Semantic retrieval for relevant file selection
- Local and cloud model support
- Edit request detection and patch workflow
- Diff preview before file updates
- Debug tracing with `/debug on` and `/debug off`

## 📁 Repository structure

- main.py — entry point and command loop
- config.py — configuration, environment loading, and model settings
- requirements.txt — Python dependency list
- readme.md — project documentation

- data
  - `repo_index.json` — cached repository embeddings and indexed file metadata
  - `prototypes.json` — prototypes used for prompt mode classification
  - `prototypes_cache.json` — cached embedded prototypes

- editing
  - patch_generator.py — builds prompts and parses file patch responses
  - diff_viewer.py — prints unified diffs between original and updated content
  - file_writer.py — writes file changes and syncs the index

- memory
  - memory_manager.py — tracks recent chat messages and conversation state

- models
  - `classifier.py` — prompt classification logic
  - cloud_model.py — OpenRouter cloud chat integration
  - local_model.py — local Ollama chat wrapper

- repo
  - repo_indexer.py — repository scanning, indexing, loading, and saving
  - repo_state.py — in-memory repository index state
  - `repo_summary.py` — repository summary utilities
  - `graph_builder.py` — repo graph builder
  - `graph_traversal.py` — graph traversal helpers
  - retrieval.py — semantic file retrieval
  - mode_classifier.py — embedding-based mode classification
  - context_builder.py — builds prompt context for the AI models

- tracing
  - `debug.py` — tracing utilities for pipeline debugging

## ⚙️ Prerequisites

- Python 3.11+ recommended
- `ollama` installed and configured for the local model
- Internet access for OpenRouter cloud model usage
- A valid `OPENROUTER_API_KEY`

## 🛠 Installation

1. Clone the repository or download the project files.

2. Create and activate a Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root with:

```text
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> config.py requires this value on startup. The app will raise an error if `OPENROUTER_API_KEY` is not set.

## ▶️ Running the agent

Start the application from the project root:

```bash
python main.py
```

The interactive prompt supports:

- normal chat queries
- edit requests such as `fix bug`, `update file`, `modify file`, `rewrite file`, `patch`, etc.
- `/debug on` to enable pipeline tracing
- `/debug off` to disable tracing
- `exit` or `quit` to leave the app

## 🧠 How it works

1. main.py starts the app and builds the repository index.
2. User input is classified and stored in memory.
3. If an edit request is detected, the app:
   - retrieves relevant files using semantic search
   - generates patches via a cloud model
   - displays diffs
   - prompts the user to apply changes
4. If not an edit request, the app can still handle general chat and repository-aware prompts through the context builder.

## 🔧 Configuration details

- config.py sets:
  - `LOCAL_MODEL`: local Ollama model name
  - `CLOUD_MODEL`: cloud model used through OpenRouter
  - `OPENROUTER_API_KEY`: loaded from .env
  - `ALLOWED_EXTENSIONS`: supported file types for indexing and retrieval
  - `MAX_RECENT_MESSAGES`: controls chat history length

- repo_indexer.py scans the repo, builds embeddings, and stores the index in repo_index.json
- mode_classifier.py uses prototype prompts to decide whether a user request is repository-aware or general chat
- patch_generator.py builds edit prompts and parses multi-file patch responses
- file_writer.py applies updates and syncs the repository index

## 💡 Notes

- The local model (`ollama`) and cloud model (`openai` via OpenRouter) are both used; the edit workflow currently uses the cloud model for patch generation.
- Cached data files in data speed up startup and classification.
- The app is designed for code repositories and supports common code file formats plus markdown and text files.

## 🧪 Recommended workflow

1. Run `python main.py`
2. Enter a request such as `fix bug in file_writer.py` or `update the prompt parser`
3. Review the retrieved file list
4. Inspect the diff output
5. Confirm whether to apply the patch

## 📌 Troubleshooting

- If the app fails to start with an API key error, verify .env exists and contains `OPENROUTER_API_KEY`.
- If local Ollama calls fail, ensure `ollama` is installed and the `LOCAL_MODEL` name is valid.
- If repository indexing is slow, remove large or irrelevant directories from repo_indexer.py ignore rules.

## 📚 Further improvements

This project can be extended by:

- adding more robust parsing for multi-file patch outputs
- improving edit request detection with a learned classifier
- supporting additional model providers
- adding a web or GUI frontend
- making the repo graph traversal fully integrated into retrieval

---

Thank you for using the Hybrid Repo AI Agent.