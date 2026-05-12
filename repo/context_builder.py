from repo.retrieval import (
    retrieve_relevant_files
)

from repo.mode_classifier import (
    classify_mode
)

from memory.memory_manager import (
    get_recent_messages,
    conversation_summary,
    set_current_mode
)

from tracing.debug import trace


# =====================================
# MODE
# =====================================

def determine_next_mode(prompt):

    result = classify_mode(prompt)

    trace(f"Mode: {result}")

    return result


# =====================================
# CONTEXT BUILDER
# =====================================

def build_context(user_prompt):

    messages = []

    next_mode = determine_next_mode(
        user_prompt
    )

    set_current_mode(next_mode)

    use_repo_context = \
        next_mode == "REPO"

    # =====================================
    # SYSTEM PROMPT
    # =====================================

    if use_repo_context:

        messages.append({
            "role": "system",
            "content": """
You are a repository-aware AI coding assistant.

The repository has already been indexed.

You understand:
- repository structure
- repository files
- semantic relationships
- project architecture

Do NOT ask user to paste code.
"""
        })

    else:

        messages.append({
            "role": "system",
            "content": """
You are a helpful AI assistant.
"""
        })

    # =====================================
    # MEMORY
    # =====================================

    if conversation_summary:

        messages.append({
            "role": "system",
            "content":
            conversation_summary
        })

    messages.extend(
        get_recent_messages()
    )

    # =====================================
    # REPO CONTEXT
    # =====================================

    repo_context = ""

    if use_repo_context:

        relevant_files = \
            retrieve_relevant_files(
                user_prompt
            )

        for file in relevant_files:

            repo_context += f"""

FILE:
{file['path']}

CONTENT:
{file['content'][:4000]}

"""

    # =====================================
    # USER MESSAGE
    # =====================================

    if use_repo_context:

        user_content = f"""
USER REQUEST:
{user_prompt}

REPOSITORY CONTEXT:
{repo_context}
"""

    else:

        user_content = user_prompt

    messages.append({
        "role": "user",
        "content": user_content
    })

    return messages