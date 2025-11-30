from typing import List


def compact_messages(messages: List[dict], keep_last: int = 6) -> List[dict]:
    """
    Lightweight context compaction: keep a short summary + last few messages.
    Expects messages as dicts with 'role' and 'content'.
    """
    if len(messages) <= keep_last:
        return messages
    summary = {
        "role": "system",
        "content": f"Conversation truncated. Previously exchanged {len(messages) - keep_last} messages summarized as: "
        + "; ".join(m.get("content", "")[:120] for m in messages[:-keep_last]),
    }
    return [summary] + messages[-keep_last:]
