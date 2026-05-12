import os

LOCAL_MODEL = "qwen2.5-coder:1.5b"

CLOUD_MODEL = "inclusionai/ring-2.6-1t:free"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

PROJECT_ROOT = os.getcwd()

MAX_RECENT_MESSAGES = 6

DEBUG_MODE = False

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