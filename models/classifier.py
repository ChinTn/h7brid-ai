from models.local_model import local_chat

from repo.retrieval import retrieve_relevant_files

from tracing.debug import trace


def classify_prompt(prompt):

    trace("Running hybrid workload classifier")

    # =====================================
    # RETRIEVAL ANALYSIS
    # =====================================

    relevant_files = retrieve_relevant_files(
        prompt
    )

    retrieved_count = len(relevant_files)

    total_context_size = 0

    for file in relevant_files:

        total_context_size += len(
            file["content"]
        )

    # =====================================
    # HEURISTIC WORKLOAD SCORING
    # =====================================

    workload_score = 0

    # prompt length
    workload_score += len(prompt.split()) * 0.5

    # retrieved files
    workload_score += retrieved_count * 4

    # context size
    workload_score += total_context_size / 4000

    trace(
        f"Workload score: {workload_score}"
    )

    # =====================================
    # AUTO CLOUD ESCALATION
    # =====================================

    if workload_score > 60:

        trace(
            "Escalating to cloud due to workload"
        )

        return "COMPLEX"

    # =====================================
    # AI CLASSIFIER
    # =====================================

    system_prompt = """
You are a workload-aware AI classifier.

Classify prompts into:

SIMPLE:
- quick responses
- small explanations
- lightweight coding help

COMPLEX:
- deep reasoning
- architecture
- debugging
- repository analysis
- scalability
- multi-file understanding

Reply ONLY:
SIMPLE

or

COMPLEX
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

    trace(f"AI classifier result: {result}")

    if "COMPLEX" in result:
        return "COMPLEX"

    return "SIMPLE"