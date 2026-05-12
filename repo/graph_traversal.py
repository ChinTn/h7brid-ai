from tracing.debug import trace

# =====================================
# CONFIG
# =====================================

MAX_GRAPH_DEPTH = 2

MAX_TOTAL_GRAPH_FILES = 15

MAX_NEIGHBOURS_PER_NODE = 4

MIN_EDGE_WEIGHT = 0.90

DEPTH_DECAY = 0.12


# =====================================
# WEIGHTED DFS
# =====================================

def weighted_graph_expansion(
    graph,
    seed_paths
):

    trace("Starting graph traversal")

    visited = set()

    collected = []

    # =====================================
    # DFS
    # =====================================

    def dfs(
        current_path,
        depth,
        inherited_score
    ):

        # =====================================
        # LIMITS
        # =====================================

        if depth > MAX_GRAPH_DEPTH:
            return

        if len(collected) >= \
           MAX_TOTAL_GRAPH_FILES:

            return

        if current_path in visited:
            return

        visited.add(current_path)

        collected.append({
            "path": current_path,
            "graph_score": inherited_score
        })

        neighbours = graph.get(
            current_path,
            []
        )

        # =====================================
        # SORT STRONGEST FIRST
        # =====================================

        neighbours.sort(
            key=lambda x: x["weight"],
            reverse=True
        )

        neighbours = neighbours[
            :MAX_NEIGHBOURS_PER_NODE
        ]

        # =====================================
        # EXPAND
        # =====================================

        for neighbour in neighbours:

            weight = neighbour["weight"]

            if weight < MIN_EDGE_WEIGHT:
                continue

            next_score = (
                inherited_score
                * weight
                * (1 - depth * DEPTH_DECAY)
            )

            dfs(
                neighbour["path"],
                depth + 1,
                next_score
            )

    # =====================================
    # START DFS FROM SEEDS
    # =====================================

    for seed in seed_paths:

        dfs(
            seed,
            depth=0,
            inherited_score=1.0
        )

    trace(
        f"Graph expansion collected "
        f"{len(collected)} files"
    )

    return collected