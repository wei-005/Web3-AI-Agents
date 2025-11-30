"""
Agent factory helpers and shared settings.
"""
import os

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


def get_api_key() -> str:
    """
    Fetch API key from env for local runs. Caller should raise if missing.
    """
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY env var is required to run agents with Gemini.")
    return key
