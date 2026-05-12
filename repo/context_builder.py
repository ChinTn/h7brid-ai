from repo.retrieval import retrieve_relevant_files
from repo.repo_summary import build_repo_summary
from repo.mode_classifier import classify_mode

from memory.memory_manager import (
    get_recent_messages,
    conversation_summary,
    get_current_mode,
    set_current_mode
)

from tracing.debug import trace


# =====================================
# MODE TRANSITION
# =====================================

def determine_next_mode(prompt):

    trace(f"Current mode: {get_current_mode()}")

    result = classify_mode(prompt)

    trace(f"Embedding classifier decided: {result}")

    return result


# =====================================
# CONTEXT BUILDER
# =====================================

def build_context(user_prompt):

    trace("Building AI context")

    messages = []

    next_mode = determine_next_mode(user_prompt)

    set_current_mode(next_mode)

    trace(f"Transitioned to mode: {next_mode}")

    use_repo_context = next_mode == "REPO"

    # =====================================
    # REPO MODE
    # =====================================

    if use_repo_context:

        trace("Repo-aware mode enabled")

        repo_summary = build_repo_summary()

        messages.append({
            "role": "system",
            "content": f"""
You are a repository-aware AI coding assistant.

The user is INSIDE their repository.

You already have:
- repository structure
- architecture understanding
- repository context
- relevant source files

NEVER ask the user to paste code
if repository context already exists.

Your job:
- analyze repositories
- debug issues
- explain architecture
- modify code
- reason about project structure

REPOSITORY SUMMARY:

{repo_summary}
"""
        })

    # =====================================
    # CHAT MODE
    # =====================================

    else:

        trace("Normal assistant mode enabled")

        messages.append({
            "role": "system",
            "content": """
You are a helpful conversational AI assistant.

Respond naturally.
"""
        })

    # =====================================
    # MEMORY SUMMARY
    # =====================================

    if conversation_summary:

        messages.append({
            "role": "system",
            "content": f"""
CONVERSATION SUMMARY:

{conversation_summary}
"""
        })

    # =====================================
    # RECENT MEMORY
    # =====================================

    messages.extend(get_recent_messages())

    # =====================================
    # REPO RETRIEVAL
    # =====================================

    repo_context = ""

    if use_repo_context:

        relevant_files = retrieve_relevant_files(user_prompt)

        for file in relevant_files:

            repo_context += f"""

FILE:
{file['path']}

CONTENT:
{file['content']}

"""

    # =====================================
    # USER REQUEST
    # =====================================

    if use_repo_context:

        user_content = f"""
USER REQUEST:

{user_prompt}

RELEVANT REPOSITORY CONTEXT:

{repo_context}
"""

    else:

        user_content = user_prompt

    messages.append({
        "role": "user",
        "content": user_content
    })

    return messages