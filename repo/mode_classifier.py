import json
import math
import ollama

from pathlib import Path
from tracing.debug import trace

# =====================================
# CONFIG
# =====================================

EMBEDDING_MODEL = "nomic-embed-text"

PROTOTYPES_PATH = (
    Path(__file__).parent.parent / "data" / "prototypes.json"
)

CACHE_PATH = (
    Path(__file__).parent.parent / "data" / "prototypes_cache.json"
)

TOP_K = 3

# =====================================
# CACHE (avoids re-embedding on every run)
# =====================================

_runtime_cache = None


# =====================================
# COSINE SIMILARITY
# =====================================

def cosine_similarity(a, b):

    dot    = sum(x * y for x, y in zip(a, b))
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
        prompt=text
    )

    return response["embedding"]


# =====================================
# PROTOTYPE LOADING
# (embeds once, caches to disk)
# =====================================

def load_prototypes():

    global _runtime_cache

    # Already loaded this session
    if _runtime_cache is not None:
        return _runtime_cache

    # Load from disk cache if it exists
    # and prototypes.json hasn't changed
    if CACHE_PATH.exists() and PROTOTYPES_PATH.exists():

        proto_mtime = PROTOTYPES_PATH.stat().st_mtime
        cache_mtime = CACHE_PATH.stat().st_mtime

        if cache_mtime >= proto_mtime:

            trace("Loading prototype embeddings from disk cache")

            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                _runtime_cache = json.load(f)

            return _runtime_cache

    # Re-embed all prototypes
    trace("Embedding prototypes (first run or prototypes changed)")

    with open(PROTOTYPES_PATH, "r", encoding="utf-8") as f:
        prototypes = json.load(f)

    embedded = []

    for item in prototypes:

        embedding = get_embedding(item["text"])

        embedded.append({
            "mode":      item["mode"],
            "text":      item["text"],
            "embedding": embedding
        })

    # Save to disk
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded, f)

    _runtime_cache = embedded

    trace(f"Cached {len(embedded)} prototype embeddings")

    return _runtime_cache


# =====================================
# CLASSIFY
# =====================================

def classify_mode(prompt):

    trace("Running embedding-based mode classifier")

    prompt_embedding = get_embedding(prompt)

    prototypes = load_prototypes()

    # Score every prototype
    scored = []

    for proto in prototypes:

        sim = cosine_similarity(
            prompt_embedding,
            proto["embedding"]
        )

        scored.append({
            "mode": proto["mode"],
            "text": proto["text"],
            "sim":  sim
        })

    scored.sort(key=lambda x: x["sim"], reverse=True)

    # Majority vote on top-K neighbours
    top_k  = scored[:TOP_K]
    chat_votes = sum(1 for s in top_k if s["mode"] == "CHAT")
    repo_votes = sum(1 for s in top_k if s["mode"] == "REPO")

    result = "REPO" if repo_votes > chat_votes else "CHAT"

    trace(
        f"Top match: '{top_k[0]['text']}' "
        f"(sim={top_k[0]['sim']:.3f}) → {result}"
    )

    return result