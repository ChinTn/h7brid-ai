from repo.scanner import scan_repo

from tracing.debug import trace

repo_files_cache = scan_repo()

def retrieve_relevant_files(prompt):

    trace("Running repository retrieval")

    relevant = []

    prompt_words = prompt.lower().split()

    for file in repo_files_cache:

        try:

            with open(
                file["full_path"],
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read()

            lowered = content.lower()

            score = 0

            # filename relevance
            for word in prompt_words:

                if word in file["path"].lower():
                    score += 3

                if word in lowered:
                    score += 1

            # always include important files
            important_files = [
                "package.json",
                "requirements.txt",
                "README.md",
                "main.py",
                "app.py",
                "server.js"
            ]

            if any(
                imp in file["path"]
                for imp in important_files
            ):
                score += 2

            if score > 0:

                relevant.append({
                    "path": file["path"],
                    "content": content[:4000],
                    "score": score
                })

        except:
            pass

    relevant.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return relevant[:5]