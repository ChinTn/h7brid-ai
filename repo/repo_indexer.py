import os
import json
import hashlib
import ollama

from pathlib import Path

from tracing.debug import trace

from repo.repo_state import REPO_INDEX

from repo.graph_builder import (
    build_graph
)

# =====================================
# CONFIG
# =====================================

EMBEDDING_MODEL = "nomic-embed-text"

INDEX_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "repo_index.json"
)

REPO_ROOT = Path.cwd()

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".html",
    ".css",
    ".md",
    ".txt"
}

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    "dist",
    "build"
}


# =====================================
# HASHING
# =====================================

def hash_content(content):

    return hashlib.md5(
        content.encode("utf-8")
    ).hexdigest()


# =====================================
# EMBEDDING
# =====================================

def get_embedding(text):

    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text[:3000]
    )

    return response["embedding"]


# =====================================
# SCAN REPO
# =====================================

def scan_repo():

    files = []

    for root, dirs, filenames in os.walk(REPO_ROOT):

        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]

        for filename in filenames:

            ext = Path(filename).suffix

            if ext not in \
               SUPPORTED_EXTENSIONS:

                continue

            path = Path(root) / filename

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    content = f.read()

                files.append({
                    "path": str(
                        path.relative_to(
                            REPO_ROOT
                        )
                    ),
                    "content": content
                })

            except:
                pass

    return files


# =====================================
# INDEX SINGLE FILE
# =====================================

def index_file(file_data):

    content = file_data["content"]

    content_hash = hash_content(
        content
    )

    embedding_text = f"""
FILE NAME:
{Path(file_data['path']).name}

FILE PATH:
{file_data['path']}

CONTENT:
{content[:4000]}
"""

    embedding = get_embedding(
        embedding_text
    )

    return {
        "path": file_data["path"],
        "content": content,
        "hash": content_hash,
        "embedding": embedding
    }


# =====================================
# LOAD INDEX
# =====================================

def load_index():

    global REPO_INDEX

    if not INDEX_PATH.exists():
        return

    try:

        with open(
            INDEX_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

            if not content:
                return

            REPO_INDEX.update(
                json.loads(content)
            )

    except Exception as e:

        trace(
            f"Failed to load repo index: {e}"
        )


# =====================================
# SAVE INDEX
# =====================================

def save_index():

    INDEX_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        INDEX_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            REPO_INDEX,
            f
        )


# =====================================
# BUILD REPO GRAPH
# =====================================

def build_repo_graph():

    trace("Generating graph")

    graph = build_graph(
        REPO_INDEX
    )

    for path in REPO_INDEX:

        REPO_INDEX[path]["graph"] = \
            graph.get(path, [])

    trace("Graph synced")


# =====================================
# BUILD / UPDATE INDEX
# =====================================

def build_repo_index():

    trace(
        "Building repository index"
    )

    load_index()

    files = scan_repo()

    updated = 0

    existing_paths = set(
        REPO_INDEX.keys()
    )

    current_paths = set()

    # =====================================
    # INDEX FILES
    # =====================================

    for file_data in files:

        path = file_data["path"]

        current_paths.add(path)

        content_hash = hash_content(
            file_data["content"]
        )

        existing = REPO_INDEX.get(path)

        # =====================================
        # SKIP UNCHANGED
        # =====================================

        if existing and \
           existing["hash"] == \
           content_hash:

            continue

        trace(f"Indexing: {path}")

        REPO_INDEX[path] = index_file(
            file_data
        )

        updated += 1

    # =====================================
    # REMOVE DELETED FILES
    # =====================================

    deleted = existing_paths - current_paths

    for path in deleted:

        trace(
            f"Removing deleted file: "
            f"{path}"
        )

        del REPO_INDEX[path]

    # =====================================
    # REBUILD GRAPH
    # =====================================

    build_repo_graph()

    # =====================================
    # SAVE
    # =====================================

    save_index()

    trace(
        f"Repository index updated "
        f"({updated} files changed)"
    )