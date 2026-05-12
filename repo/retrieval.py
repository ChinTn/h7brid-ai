import os
import json
import math
import ollama

from pathlib import Path
from tracing.debug import trace

# =====================================
# CONFIG
# =====================================

EMBEDDING_MODEL = "nomic-embed-text"

REPO_ROOT = Path.cwd()

CACHE_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "file_embeddings_cache.json"
)

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".md",
    ".txt"
}

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "__pycache__"
}

TOP_K = 5

_runtime_cache = None


# =====================================
# COSINE SIMILARITY
# =====================================

def cosine_similarity(a, b):

    dot = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# =====================================
# EMBEDDING
# =====================================

def get_embedding(text):

    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text[:6000]
    )

    return response["embedding"]


# =====================================
# FILE SCANNING
# =====================================

def scan_repo_files():

    files = []

    for root, dirs, filenames in os.walk(REPO_ROOT):

        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]

        for filename in filenames:

            ext = Path(filename).suffix

            if ext not in SUPPORTED_EXTENSIONS:
                continue

            path = Path(root) / filename

            try:

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                files.append({
                    "path": str(path.relative_to(REPO_ROOT)),
                    "content": content
                })

            except Exception:
                pass

    return files


# =====================================
# BUILD CACHE
# =====================================

def build_embeddings_cache():

    trace("Building semantic retrieval cache")

    files = scan_repo_files()

    embedded_files = []

    for file in files:

        trace(f"Embedding: {file['path']}")

        summary_text = f"""
FILE NAME:
{Path(file['path']).name}

FILE PATH:
{file['path']}

CONTENT:
{file['content'][:2000]}
"""

        embedding = get_embedding(summary_text)

        embedded_files.append({
            "path": file["path"],
            "content": file["content"],
            "embedding": embedding
        })

    CACHE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_files, f)

    trace(
        f"Cached embeddings for "
        f"{len(embedded_files)} files"
    )

    return embedded_files


# =====================================
# LOAD CACHE
# =====================================

def load_embeddings_cache():

    global _runtime_cache

    if _runtime_cache is not None:
        return _runtime_cache

    if CACHE_PATH.exists():

        trace("Loading semantic retrieval cache")

        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            _runtime_cache = json.load(f)

        return _runtime_cache

    _runtime_cache = build_embeddings_cache()

    return _runtime_cache


# =====================================
# RETRIEVAL
# =====================================

def retrieve_relevant_files(prompt):

    trace("Running semantic file retrieval")

    prompt_embedding = get_embedding(prompt)

    indexed_files = load_embeddings_cache()

    scored = []

    for file in indexed_files:

        similarity = cosine_similarity(
            prompt_embedding,
            file["embedding"]
        )

        scored.append({
            "path": file["path"],
            "content": file["content"],
            "score": similarity
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top_files = scored[:TOP_K]

    trace(
        "Top retrieved files: "
        + ", ".join(
            f"{f['path']} ({f['score']:.2f})"
            for f in top_files
        )
    )

    return top_files