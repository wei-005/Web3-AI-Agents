import os
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path(os.path.dirname(os.path.dirname(__file__))) / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def save_report(content: str, prefix: str = "report") -> str:
    """
    Save a markdown report and return its path.
    """
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = REPORT_DIR / f"{prefix}-{ts}.md"
    path.write_text(content)
    return str(path)
