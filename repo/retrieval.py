import math

from tracing.debug import trace

from repo.repo_state import REPO_INDEX
from repo.repo_indexer import get_embedding

from repo.graph_builder import build_graph
from repo.graph_traversal import (
    weighted_graph_expansion
)

# =====================================
# CONFIG
# =====================================

SEMANTIC_TOP_K = 5

FINAL_TOP_K = 6

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

    return dot / (
        norm_a * norm_b
    )

# =====================================
# TOKENIZE
# =====================================

def tokenize(text):

    separators = [
        "/",
        "\\",
        ".",
        "_",
        "-",
        ":"
    ]

    text = text.lower()

    for sep in separators:

        text = text.replace(
            sep,
            " "
        )

    return set(
        text.split()
    )

# =====================================
# LEXICAL SCORE
# =====================================

def lexical_score(
    query,
    path
):

    query_tokens = tokenize(query)

    path_tokens = tokenize(path)

    overlap = len(
        query_tokens.intersection(
            path_tokens
        )
    )

    return overlap

# =====================================
# SEMANTIC RETRIEVAL
# =====================================

def semantic_retrieval(
    prompt_embedding
):

    scored = []

    for path, data in REPO_INDEX.items():

        similarity = cosine_similarity(
            prompt_embedding,
            data["embedding"]
        )

        scored.append({
            "path": path,
            "content": data["content"],
            "semantic_score": similarity
        })

    scored.sort(
        key=lambda x: x["semantic_score"],
        reverse=True
    )

    return scored[:SEMANTIC_TOP_K]

# =====================================
# FINAL RERANK
# =====================================

def rerank_results(
    query,
    results
):

    reranked = []

    for item in results:

        lexical = lexical_score(
            query,
            item["path"]
        )

        semantic = item.get(
            "semantic_score",
            0
        )

        graph_score = item.get(
            "graph_score",
            0
        )

        final_score = (
            semantic * 0.65
            + graph_score * 0.25
            + lexical * 0.10
        )

        item["final_score"] = final_score

        reranked.append(item)

    reranked.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return reranked[:FINAL_TOP_K]

# =====================================
# MAIN RETRIEVAL
# =====================================

def retrieve_relevant_files(
    prompt
):

    trace("Hybrid retrieval started")

    # =====================================
    # EMBEDDING
    # =====================================

    prompt_embedding = get_embedding(
        prompt
    )

    # =====================================
    # SEMANTIC RETRIEVAL
    # =====================================

    semantic_results = semantic_retrieval(
        prompt_embedding
    )

    semantic_paths = [
        item["path"]
        for item in semantic_results
    ]

    # =====================================
    # GRAPH BUILD
    # =====================================

    graph = build_graph(
        REPO_INDEX
    )

    # =====================================
    # GRAPH EXPANSION
    # =====================================

    graph_results = weighted_graph_expansion(
        graph,
        semantic_paths
    )

    # =====================================
    # UNION
    # =====================================

    combined = {}

    for item in semantic_results:

        combined[item["path"]] = {
            "path": item["path"],
            "content": item["content"],
            "semantic_score": item[
                "semantic_score"
            ],
            "graph_score": 0
        }

    for item in graph_results:

        path = item["path"]

        if path not in REPO_INDEX:
            continue

        if path not in combined:

            combined[path] = {
                "path": path,
                "content": REPO_INDEX[path][
                    "content"
                ],
                "semantic_score": 0,
                "graph_score": item[
                    "graph_score"
                ]
            }

        else:

            combined[path][
                "graph_score"
            ] = item["graph_score"]

    # =====================================
    # FINAL RERANK
    # =====================================

    final_results = rerank_results(
        prompt,
        list(combined.values())
    )

    trace(
        "Retrieved: "
        + ", ".join(
            f"{f['path']} "
            f"({f['final_score']:.2f})"
            for f in final_results
        )
    )

    return final_results