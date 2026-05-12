# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Absolute path — works from ANY directory, always
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

LOCAL_MODEL = "qwen2.5-coder:1.5b"
CLOUD_MODEL = "inclusionai/ring-2.6-1t:free"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PROJECT_ROOT = Path(__file__).resolve().parent
MAX_RECENT_MESSAGES = 6
DEBUG_MODE = False
ALLOWED_EXTENSIONS = [
    ".py", ".js", ".ts", ".tsx",
    ".jsx", ".json", ".html", ".css", ".md"
]

# Fail loudly at startup, not deep in API call
if not OPENROUTER_API_KEY:
    raise ValueError(
        f"OPENROUTER_API_KEY not found.\n"
        f"Looking at: {_env_path}\n"
        f"File exists: {_env_path.exists()}"
    )