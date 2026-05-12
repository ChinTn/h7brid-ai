from tracing.debug import (
    trace,
    set_debug,
    reset_pipeline,
    show_pipeline,
    PIPELINE_STATE,
    start_stage,
    end_stage
)

from repo.repo_indexer import (
    build_repo_index
)

from memory.memory_manager import (
    get_current_mode,
    add_message,
    recent_messages,
    conversation_summary
)

from models.classifier import classify_prompt
from models.local_model import local_chat
from models.cloud_model import cloud_chat

from repo.context_builder import build_context
from repo.retrieval import retrieve_relevant_files

from editing.patch_generator import generate_patch
from editing.diff_viewer import show_diff
from editing.file_writer import apply_changes


# =====================================
# EDIT REQUEST DETECTION
# =====================================

EDIT_KEYWORDS = [
    "edit file",
    "fix bug",
    "update file",
    "modify file",
    "rewrite file",
    "patch",
    "refactor code",
    "change implementation"
]


def is_edit_request(prompt):

    lower_prompt = prompt.lower()

    return any(
        keyword in lower_prompt
        for keyword in EDIT_KEYWORDS
    )


# =====================================
# MAIN
# =====================================

def main():

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧠 HYBRID REPO AI AGENT")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print("\n📦 Loading repository memory...\n")

    build_repo_index()

    print("✅ Repository indexed.\n")

    print("\nCommands:")
    print("/debug on")
    print("/debug off")
    print("exit / quit\n")

    while True:

        try:

            prompt = input("\nYou > ").strip()

        except (EOFError, KeyboardInterrupt):

            print("\nExiting.")

            break

        # =====================================
        # RESET PIPELINE
        # =====================================

        reset_pipeline()

        if not prompt:
            continue

        # =====================================
        # EXIT
        # =====================================

        if prompt.lower() in {"exit", "quit"}:

            print("\nGoodbye.\n")

            break

        # =====================================
        # DEBUG ON
        # =====================================

        if prompt.lower() == "/debug on":

            set_debug(True)

            print("\nDebug tracing enabled.\n")

            continue

        # =====================================
        # DEBUG OFF
        # =====================================

        if prompt.lower() == "/debug off":

            set_debug(False)

            print("\nDebug tracing disabled.\n")

            continue

        # =====================================
        # MEMORY UPDATE
        # =====================================

        add_message("user", prompt)

        PIPELINE_STATE["recent_message_count"] = \
            len(recent_messages)

        PIPELINE_STATE["summary_active"] = \
            bool(conversation_summary)

        # =====================================
        # FILE EDIT FLOW
        # =====================================

        if is_edit_request(prompt):

            trace("Detected repository edit request")

            start_stage("Repo Retrieval")

            relevant = retrieve_relevant_files(
                prompt
            )

            end_stage("Repo Retrieval")

            PIPELINE_STATE["retrieved_files"] = [
                file["path"]
                for file in relevant
            ]

            if not relevant:

                print(
                    "\nNo relevant files found.\n"
                )

                continue

            print("\n📂 Retrieved Files:\n")

            for file in relevant:

                print(f"- {file['path']}")

            # =====================================
            # PATCH GENERATION
            # =====================================

            start_stage("Patch Generation")

            decision = classify_prompt(prompt)

            PIPELINE_STATE["router_decision"] = \
                decision

            PIPELINE_STATE["classifier_model"] = \
                "qwen2.5-coder:1.5b (local)"

            PIPELINE_STATE["refinement_model"] = \
                "inclusionai/ring-2.6-1t:free"

            print("\n☁️ USING CLOUD MODEL\n")

            updated_files = generate_patch(
                prompt,
                relevant,
                use_cloud=True
            )

            end_stage("Patch Generation")

            if not updated_files:

                print(
                    "\n❌ No valid patches generated.\n"
                )

                continue

            # =====================================
            # SHOW DIFFS
            # =====================================

            for updated_file in updated_files:

                path = updated_file["path"]

                original = None

                for file in relevant:

                    if file["path"] == path:

                        original = file["content"]

                        break

                if original is None:

                    continue

                print(
                    f"\n📄 Target File:\n{path}\n"
                )

                show_diff(
                    original,
                    updated_file["content"],
                    path
                )

            # =====================================
            # SHOW PIPELINE
            # =====================================

            show_pipeline()

            # =====================================
            # APPLY CONFIRMATION
            # =====================================

            confirm = input(
                "\nApply ALL changes? (y/n): "
            ).strip().lower()

            if confirm != "y":

                print(
                    "\n❌ Changes cancelled.\n"
                )

                continue

            # =====================================
            # APPLY FILES
            # =====================================

            start_stage("File Write")

            for updated_file in updated_files:

                apply_changes(
                    updated_file["path"],
                    updated_file["content"]
                )

            end_stage("File Write")

            print(
                "\n✅ All changes applied.\n"
            )

            continue

        # =====================================
        # NORMAL CHAT FLOW
        # =====================================

        trace("Starting normal chat flow")

        # =====================================
        # CLASSIFIER
        # =====================================

        start_stage("AI Classification")

        decision = classify_prompt(prompt)

        end_stage("AI Classification")

        PIPELINE_STATE["router_decision"] = \
            decision

        PIPELINE_STATE["classifier_model"] = \
            "qwen2.5-coder:1.5b (local)"

        # =====================================
        # CONTEXT BUILDING
        # =====================================

        start_stage("Context Retrieval")

        context = build_context(prompt)

        PIPELINE_STATE["current_mode"] = \
            get_current_mode()

        end_stage("Context Retrieval")

        # =====================================
        # ROUTER DISPLAY
        # =====================================

        print(f"\n🧠 ROUTER DECISION:")
        print(decision)

        # =====================================
        # SIMPLE → LOCAL
        # =====================================

        if decision == "SIMPLE":

            PIPELINE_STATE["draft_model"] = \
                "qwen2.5-coder:1.5b"

            start_stage("Local Inference")

            response = local_chat(
                context,
                stream=False
            )

            answer = response["message"]["content"]

            end_stage("Local Inference")

            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🤖 RESPONSE")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            print(answer)

            add_message("assistant", answer)

            show_pipeline()

            continue

        # =====================================
        # COMPLEX → HYBRID DRAFT + CLOUD
        # =====================================

        else:

            PIPELINE_STATE["draft_model"] = \
                "qwen2.5-coder:1.5b"

            PIPELINE_STATE["refinement_model"] = \
                "inclusionai/ring-2.6-1t:free"

            # =====================================
            # LOCAL DRAFT
            # =====================================

            start_stage("Local Draft")

            draft_response = local_chat(
                context,
                stream=False
            )

            draft_answer = \
                draft_response["message"]["content"]

            end_stage("Local Draft")

            if PIPELINE_STATE.get("debug_mode"):

                print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("⚡ QUICK DRAFT")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

                print(draft_answer)

            # =====================================
            # CLOUD REFINEMENT
            # =====================================

            if PIPELINE_STATE.get("debug_mode"):

                print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("☁️ CLOUD REFINEMENT")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            refinement_context = context + [
                {
                    "role": "assistant",
                    "content": draft_answer
                },
                {
                    "role": "user",
                    "content": """
Improve and refine the previous answer.

Requirements:
- improve depth
- improve correctness
- improve architecture quality
- improve reasoning
- keep useful parts
"""
                }
            ]

            start_stage("Cloud Refinement")

            answer = cloud_chat(
                refinement_context
            )

            end_stage("Cloud Refinement")

            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🤖 FINAL RESPONSE")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            print(answer)

            add_message("assistant", answer)

            show_pipeline()


# =====================================
# ENTRY
# =====================================

if __name__ == "__main__":

    main()