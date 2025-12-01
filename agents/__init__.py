"""
Agent factory helpers and shared settings.
"""
import os
from google.genai import types

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
DEFAULT_RETRY = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def get_api_key() -> str:
    """
    Fetch API key from env for local runs. Caller should raise if missing.
    """
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY env var is required to run agents with Gemini.")
    return key
