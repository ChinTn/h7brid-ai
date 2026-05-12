from pathlib import Path

from tracing.debug import trace

from repo.repo_state import REPO_INDEX

from repo.repo_indexer import (
    hash_content,
    get_embedding,
    save_index
)


# =====================================
# APPLY CHANGES
# =====================================

def apply_changes(path, content):

    trace(f"Writing file: {path}")

    # =====================================
    # WRITE REAL FILE
    # =====================================

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

    # =====================================
    # UPDATE REPO INDEX
    # =====================================

    embedding_text = f"""
FILE NAME:
{Path(path).name}

FILE PATH:
{path}

CONTENT:
{content[:4000]}
"""

    REPO_INDEX[path] = {
        "path": path,
        "content": content,
        "hash": hash_content(content),
        "embedding": get_embedding(
            embedding_text
        )
    }

    save_index()

    trace(
        f"Repository index synced: {path}"
    )