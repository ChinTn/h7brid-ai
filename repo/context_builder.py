from repo.retrieval import (
    retrieve_relevant_files
)

from repo.repo_summary import (
    build_repo_summary
)

from memory.memory_manager import (
    get_recent_messages,
    conversation_summary,
    get_current_mode,
    set_current_mode
)

from tracing.debug import trace

from models.local_model import local_chat


# =====================================
# MODE TRANSITION CLASSIFIER
# =====================================

def determine_next_mode(prompt):

    current_mode = get_current_mode()

    trace(f"Current mode: {current_mode}")

    system_prompt = f"""
You are an AI orchestration mode controller.

Current mode:
{current_mode}

Available modes:
- CHAT
- REPO

CHAT mode means:
- casual conversation
- general questions
- greetings
- non-technical discussion

REPO mode means:
- repository analysis
- code understanding
- debugging
- architecture discussion
- backend/frontend discussion
- file explanation
- software engineering discussion

Your job:
Determine whether the assistant should:
- remain in current mode
- transition to another mode

Rules:
- preserve conversational continuity
- preserve repository workflows
- avoid unnecessary repo activation
- casual followups should remain CHAT
- technical followups should remain REPO

Reply ONLY:
CHAT
or
REPO
"""

    response = local_chat([
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    result = response["message"]["content"] \
        .strip() \
        .upper()

    if "REPO" in result:
        return "REPO"

    return "CHAT"


# =====================================
# CONTEXT BUILDER
# =====================================

def build_context(user_prompt):

    trace("Building AI context")

    messages = []

    # =====================================
    # MODE TRANSITION
    # =====================================

    next_mode = determine_next_mode(
        user_prompt
    )

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

    messages.extend(
        get_recent_messages()
    )

    # =====================================
    # REPO RETRIEVAL
    # =====================================

    repo_context = ""

    if use_repo_context:

        relevant_files = retrieve_relevant_files(
            user_prompt
        )

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