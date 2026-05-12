import os

from dotenv import load_dotenv

# =====================================
# LOAD ENV VARIABLES
# =====================================

load_dotenv()

# =====================================
# MODELS
# =====================================

LOCAL_MODEL = "qwen2.5-coder:1.5b"

CLOUD_MODEL = "inclusionai/ring-2.6-1t:free"

# =====================================
# API KEYS
# =====================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
)

# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = os.getcwd()

MAX_RECENT_MESSAGES = 6

DEBUG_MODE = False

# =====================================
# FILE SUPPORT
# =====================================

ALLOWED_EXTENSIONS = [
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".html",
    ".css",
    ".md"
]

# =====================================
# VALIDATION
# =====================================

if not OPENROUTER_API_KEY:

    print(
        "\n[WARNING] OPENROUTER_API_KEY missing.\n"
    )