from pathlib import Path

from tracing.debug import trace

# =====================================
# CONFIG
# =====================================

MAX_FINAL_FILES = 14

SEMANTIC_WEIGHT = 0.65
GRAPH_WEIGHT = 0.35

DIRECTORY_DIVERSITY_PENALTY = 0.08


# =====================================
# DIRECTORY
# =====================================

def get_directory(path):

    return str(
        Path(path).parent
    )


# =====================================
# RERANK
# =====================================

def rerank_results(
    semantic_results,
    graph_results,
    repo_index
):

    trace("Reranking retrieval results")

    combined = {}

    # =====================================
    # SEMANTIC SCORES
    # =====================================

    for item in semantic_results:

        path = item["path"]

        combined[path] = {
            "path": path,
            "semantic_score":
                item["score"],
            "graph_score": 0.0
        }

    # =====================================
    # GRAPH SCORES
    # =====================================

    for item in graph_results:

        path = item["path"]

        if path not in combined:

            combined[path] = {
                "path": path,
                "semantic_score": 0.0,
                "graph_score":
                    item["graph_score"]
            }

        else:

            combined[path][
                "graph_score"
            ] = item["graph_score"]

    # =====================================
    # FINAL SCORING
    # =====================================

    ranked = []

    for path, data in combined.items():

        final_score = (
            data["semantic_score"]
            * SEMANTIC_WEIGHT
        ) + (
            data["graph_score"]
            * GRAPH_WEIGHT
        )

        ranked.append({
            "path": path,
            "score": final_score,
            "semantic_score":
                data["semantic_score"],
            "graph_score":
                data["graph_score"],
            "content":
                repo_index[path]["content"]
        })

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # =====================================
    # DIVERSITY FILTER
    # =====================================

    selected = []

    directory_counts = {}

    for item in ranked:

        directory = get_directory(
            item["path"]
        )

        count = directory_counts.get(
            directory,
            0
        )

        adjusted_score = (
            item["score"]
            - (
                count
                * DIRECTORY_DIVERSITY_PENALTY
            )
        )

        item["adjusted_score"] = \
            adjusted_score

        selected.append(item)

        directory_counts[
            directory
        ] = count + 1

    # =====================================
    # FINAL SORT
    # =====================================

    selected.sort(
        key=lambda x: x["adjusted_score"],
        reverse=True
    )

    final = selected[
        :MAX_FINAL_FILES
    ]

    trace(
        "Final reranked files: "
        + ", ".join(
            f"{f['path']}"
            for f in final
        )
    )

    return final