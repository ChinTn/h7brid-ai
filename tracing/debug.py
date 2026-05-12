import time

DEBUG_MODE = False

PIPELINE_STATE = {
    "current_mode": "CHAT",
    "debug_mode": False,
    "router_decision": None,
    "classifier_model": None,
    "draft_model": None,
    "refinement_model": None,
    "retrieved_files": [],
    "edited_file": None,
    "memory_active": False,
    "recent_message_count": 0,
    "summary_active": False,
    "stages": [],
    "timings": {}
}

# =========================================
# DEBUG TOGGLE
# =========================================

def set_debug(value):

    global DEBUG_MODE

    DEBUG_MODE = value

    PIPELINE_STATE["debug_mode"] = value

# =========================================
# TRACE
# =========================================

def trace(message):

    if DEBUG_MODE:
        print(f"\n[TRACE] {message}")

# =========================================
# STAGE TRACKING
# =========================================

def start_stage(stage_name):

    PIPELINE_STATE["stages"].append(
        {
            "name": stage_name,
            "status": "running"
        }
    )

    PIPELINE_STATE["timings"][stage_name] = time.time()

    if DEBUG_MODE:
        print(f"\n⚙️ STARTED: {stage_name}")

def end_stage(stage_name):

    start_time = PIPELINE_STATE["timings"].get(stage_name)

    duration = 0

    if start_time:
        duration = round(time.time() - start_time, 2)

    for stage in PIPELINE_STATE["stages"]:

        if stage["name"] == stage_name:
            stage["status"] = f"done ({duration}s)"

    if DEBUG_MODE:
        print(f"✅ COMPLETED: {stage_name} ({duration}s)")

# =========================================
# RESET PIPELINE
# =========================================

def reset_pipeline():

    PIPELINE_STATE["router_decision"] = None
    PIPELINE_STATE["classifier_model"] = None
    PIPELINE_STATE["draft_model"] = None
    PIPELINE_STATE["refinement_model"] = None
    PIPELINE_STATE["retrieved_files"] = []
    PIPELINE_STATE["edited_file"] = None
    PIPELINE_STATE["stages"] = []
    PIPELINE_STATE["timings"] = {}

# =========================================
# FINAL UI
# =========================================

def show_pipeline():

    if not DEBUG_MODE:
        return

    print("\n")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧠 HYBRID AGENT PIPELINE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print("\n[ROUTER]")

    print(
        f"Decision: {PIPELINE_STATE['router_decision']}"
    )

    print("\n[MODE]")
    
    print(
          f"Conversation Mode: "
          f"{PIPELINE_STATE['current_mode']}"
        )
    
    print("\n[MODELS]")

    print(
        f"Classifier: {PIPELINE_STATE['classifier_model']}"
    )

    print(
        f"Drafting: {PIPELINE_STATE['draft_model']}"
    )

    print(
        f"Refinement: {PIPELINE_STATE['refinement_model']}"
    )

    print("\n[RETRIEVAL]")

    if PIPELINE_STATE["retrieved_files"]:

        for file in PIPELINE_STATE["retrieved_files"]:

            print(f" • {file}")

    else:
        print("No files retrieved")

    print("\n[MEMORY]")

    print(
        f"Recent Messages: {PIPELINE_STATE['recent_message_count']}"
    )

    print(
        f"Compressed Summary Active: "
        f"{PIPELINE_STATE['summary_active']}"
    )

    print("\n[PIPELINE STAGES]")

    for stage in PIPELINE_STATE["stages"]:

        print(
            f" • {stage['name']} → {stage['status']}"
        )

    print("\n[PATCH]")

    if PIPELINE_STATE["edited_file"]:

        print(
            f"Edited File: "
            f"{PIPELINE_STATE['edited_file']}"
        )

    else:

        print("No file modified")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")