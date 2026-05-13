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
# LOCAL FAILURE DETECTION
# =====================================

def local_failed(answer):

    if not answer:
        return True

    stripped = answer.strip()

    if len(stripped) < 30:
        return True

    suspicious_patterns = [
        "obj['response']",
        "undefined",
        "null",
        "none",
        "{}",
        "[]"
    ]

    lowered = stripped.lower()

    for pattern in suspicious_patterns:

        if pattern in lowered:
            return True

    return False


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

        except (
            EOFError,
            KeyboardInterrupt
        ):

            print("\nExiting.")

            break

        reset_pipeline()

        if not prompt:
            continue

        # =====================================
        # EXIT
        # =====================================

        if prompt.lower() in {
            "exit",
            "quit"
        }:

            print("\nGoodbye.\n")

            break

        # =====================================
        # DEBUG ON
        # =====================================

        if prompt.lower() == "/debug on":

            set_debug(True)

            print(
                "\nDebug tracing enabled.\n"
            )

            continue

        # =====================================
        # DEBUG OFF
        # =====================================

        if prompt.lower() == "/debug off":

            set_debug(False)

            print(
                "\nDebug tracing disabled.\n"
            )

            continue

        # =====================================
        # MEMORY
        # =====================================

        add_message(
            "user",
            prompt
        )

        PIPELINE_STATE[
            "recent_message_count"
        ] = len(recent_messages)

        PIPELINE_STATE[
            "summary_active"
        ] = bool(conversation_summary)

        # =====================================
        # FILE EDIT FLOW
        # =====================================

        if is_edit_request(prompt):

            trace(
                "Detected repository edit request"
            )

            start_stage(
                "Repo Retrieval"
            )

            relevant = retrieve_relevant_files(
                prompt
            )

            end_stage(
                "Repo Retrieval"
            )

            PIPELINE_STATE[
                "retrieved_files"
            ] = [
                file["path"]
                for file in relevant
            ]

            if not relevant:

                print(
                    "\nNo relevant files found.\n"
                )

                continue

            print(
                "\n📂 Retrieved Files:\n"
            )

            for file in relevant:

                print(
                    f"- {file['path']}"
                )

            print(
                "\n☁️ USING CLOUD MODEL\n"
            )

            updated_files = generate_patch(
                prompt,
                relevant,
                use_cloud=True
            )

            if not updated_files:

                print(
                    "\n❌ No valid patches generated.\n"
                )

                continue

            for updated_file in updated_files:

                path = updated_file[
                    "path"
                ]

                original = None

                for file in relevant:

                    if file["path"] == path:

                        original = file[
                            "content"
                        ]

                        break

                if original is None:
                    continue

                print(
                    f"\n📄 Target File:\n{path}\n"
                )

                show_diff(
                    original,
                    updated_file[
                        "content"
                    ],
                    path
                )

            show_pipeline()

            confirm = input(
                "\nApply ALL changes? (y/n): "
            ).strip().lower()

            if confirm != "y":

                print(
                    "\n❌ Changes cancelled.\n"
                )

                continue

            start_stage(
                "File Write"
            )

            for updated_file in updated_files:

                apply_changes(
                    updated_file["path"],
                    updated_file["content"]
                )

            end_stage(
                "File Write"
            )

            print(
                "\n✅ All changes applied.\n"
            )

            continue

        # =====================================
        # NORMAL CHAT FLOW
        # =====================================

        trace(
            "Starting normal chat flow"
        )

        start_stage(
            "AI Classification"
        )

        decision = classify_prompt(
            prompt
        )

        end_stage(
            "AI Classification"
        )

        PIPELINE_STATE[
            "router_decision"
        ] = decision

        print(
            f"\n🧠 ROUTER DECISION:"
        )

        print(decision)

        # =====================================
        # CONTEXT
        # =====================================

        start_stage(
            "Context Retrieval"
        )

        context = build_context(
            prompt
        )

        end_stage(
            "Context Retrieval"
        )

        # =====================================
        # LOCAL FIRST
        # =====================================

        print(
            "\n⚡ USING LOCAL MODEL\n"
        )

        start_stage(
            "Local Inference"
        )

        response = local_chat(
            context,
            stream=False
        )

        answer = response[
            "message"
        ][
            "content"
        ]

        end_stage(
            "Local Inference"
        )

        # =====================================
        # LOCAL FAILURE
        # =====================================

        if local_failed(answer):

            print(
                "\n⚠️ Local model failed."
            )

            print(
                "☁️ Escalating to cloud...\n"
            )

            PIPELINE_STATE[
                "cloud_fallback"
            ] = True

            start_stage(
                "Cloud Fallback"
            )

            answer = cloud_chat(
                context
            )

            end_stage(
                "Cloud Fallback"
            )

        # =====================================
        # FINAL RESPONSE
        # =====================================

        print(
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        print(
            "🤖 RESPONSE"
        )

        print(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        print(answer)

        add_message(
            "assistant",
            answer
        )

        show_pipeline()


# =====================================
# ENTRY
# =====================================

if __name__ == "__main__":

    main()