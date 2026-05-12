import math
from pathlib import Path

from tracing.debug import trace

# =====================================
# CONFIG
# =====================================

SEMANTIC_EDGE_THRESHOLD = 0.72

IMPORT_EDGE_WEIGHT = 0.95
SEMANTIC_EDGE_MULTIPLIER = 0.85
DIRECTORY_EDGE_WEIGHT = 0.25

MAX_SEMANTIC_NEIGHBOURS = 8


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
# IMPORT EXTRACTION
# =====================================

def extract_imports(content):

    imports = []

    lines = content.splitlines()

    for line in lines:

        stripped = line.strip()

        # JS/TS imports
        if stripped.startswith("import "):

            try:

                if "from" in stripped:

                    module = (
                        stripped
                        .split("from")[1]
                        .strip()
                        .replace('"', "")
                        .replace("'", "")
                        .replace(";", "")
                    )

                    imports.append(module)

            except:
                pass

        # Python imports
        elif stripped.startswith("from "):

            try:

                module = (
                    stripped
                    .split("import")[0]
                    .replace("from", "")
                    .strip()
                )

                imports.append(module)

            except:
                pass

        elif stripped.startswith("import "):

            try:

                module = (
                    stripped
                    .replace("import", "")
                    .strip()
                )

                imports.append(module)

            except:
                pass

    return imports


# =====================================
# DIRECTORY SIMILARITY
# =====================================

def same_directory_bonus(path_a, path_b):

    dir_a = str(Path(path_a).parent)
    dir_b = str(Path(path_b).parent)

    if dir_a == dir_b:
        return DIRECTORY_EDGE_WEIGHT

    return 0.0


# =====================================
# IMPORT RELATIONSHIP
# =====================================

def import_relationship_score(
    path_a,
    imports_a,
    path_b
):

    file_name = Path(path_b).stem

    for imported in imports_a:

        if file_name in imported:
            return IMPORT_EDGE_WEIGHT

    return 0.0


# =====================================
# BUILD GRAPH
# =====================================

def build_graph(repo_index):

    trace("Building repository graph")

    graph = {}

    paths = list(repo_index.keys())

    # =====================================
    # PREPROCESS IMPORTS
    # =====================================

    imports_map = {}

    for path in paths:

        content = repo_index[path]["content"]

        imports_map[path] = extract_imports(
            content
        )

    # =====================================
    # BUILD EDGES
    # =====================================

    for path_a in paths:

        graph[path_a] = []

        embedding_a = \
            repo_index[path_a]["embedding"]

        imports_a = imports_map[path_a]

        candidates = []

        for path_b in paths:

            if path_a == path_b:
                continue

            embedding_b = \
                repo_index[path_b]["embedding"]

            semantic_score = cosine_similarity(
                embedding_a,
                embedding_b
            )

            if semantic_score < \
               SEMANTIC_EDGE_THRESHOLD:

                continue

            weight = 0.0

            # =====================================
            # SEMANTIC WEIGHT
            # =====================================

            weight += (
                semantic_score
                * SEMANTIC_EDGE_MULTIPLIER
            )

            # =====================================
            # IMPORT BONUS
            # =====================================

            weight += import_relationship_score(
                path_a,
                imports_a,
                path_b
            )

            # =====================================
            # DIRECTORY BONUS
            # =====================================

            weight += same_directory_bonus(
                path_a,
                path_b
            )

            candidates.append({
                "path": path_b,
                "weight": weight
            })

        # =====================================
        # KEEP BEST NEIGHBOURS
        # =====================================

        candidates.sort(
            key=lambda x: x["weight"],
            reverse=True
        )

        graph[path_a] = candidates[
            :MAX_SEMANTIC_NEIGHBOURS
        ]

    trace("Repository graph built")

    return graph