import math

from tracing.debug import trace
from repo.repo_state import REPO_INDEX
from repo.repo_indexer import get_embedding


# =====================================
# COSINE SIMILARITY
# =====================================

def cosine_similarity(a, b):

    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(x * x for x in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# =====================================
# RETRIEVAL
# =====================================

def retrieve_relevant_files(
    prompt,
    top_k=5
):

    trace("Semantic retrieval started")

    prompt_embedding = get_embedding(
        prompt
    )

    scored = []

    for path, data in REPO_INDEX.items():

        similarity = cosine_similarity(
            prompt_embedding,
            data["embedding"]
        )

        scored.append({
            "path": path,
            "content": data["content"],
            "score": similarity
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top_files = scored[:top_k]

    trace(
        "Retrieved: "
        + ", ".join(
            f"{f['path']} ({f['score']:.2f})"
            for f in top_files
        )
    )

    return top_files