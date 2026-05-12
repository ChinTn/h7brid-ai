from repo.scanner import scan_repo

from models.local_model import local_chat

from tracing.debug import trace

repo_summary_cache = None

def build_repo_summary():

    global repo_summary_cache

    if repo_summary_cache:
        return repo_summary_cache

    trace("Building repository summary")

    repo_files = scan_repo()

    structure = ""

    for file in repo_files[:200]:

        structure += f"{file['path']}\n"

    important_content = ""

    important_files = [
        "README.md",
        "package.json",
        "requirements.txt",
        "main.py",
        "app.py",
        "server.js"
    ]

    for file in repo_files:

        if any(
            imp in file["path"]
            for imp in important_files
        ):

            try:

                with open(
                    file["full_path"],
                    "r",
                    encoding="utf-8"
                ) as f:

                    content = f.read()

                important_content += f"""

FILE:
{file['path']}

CONTENT:
{content[:3000]}

"""

            except:
                pass

    summary_prompt = f"""
You are a repository analysis AI.

Analyze this repository structure and important files.

Your job:
- understand architecture
- identify frameworks
- identify backend/frontend stack
- identify important systems
- summarize project purpose
- summarize code organization

REPOSITORY STRUCTURE:

{structure}

IMPORTANT FILE CONTENT:

{important_content}

Return a detailed repository summary.
"""

    response = local_chat([
        {
            "role": "user",
            "content": summary_prompt
        }
    ])

    repo_summary_cache = \
        response["message"]["content"]

    return repo_summary_cache