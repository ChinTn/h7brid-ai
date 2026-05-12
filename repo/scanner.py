import os

from config import (
    PROJECT_ROOT,
    ALLOWED_EXTENSIONS
)

IGNORED_FOLDERS = [
    "node_modules",
    ".git",
    "dist",
    "build",
    "__pycache__",
    ".next",
    "venv",
    ".venv"
]

def scan_repo():

    repo_files = []

    for root, dirs, files in os.walk(PROJECT_ROOT):

        dirs[:] = [
            d for d in dirs
            if d not in IGNORED_FOLDERS
        ]

        for file in files:

            if any(
                file.endswith(ext)
                for ext in ALLOWED_EXTENSIONS
            ):

                full_path = os.path.join(root, file)

                relative_path = os.path.relpath(
                    full_path,
                    PROJECT_ROOT
                )

                repo_files.append({
                    "path": relative_path,
                    "full_path": full_path
                })

    return repo_files