from typing import Dict

from google.adk.tools.tool_context import ToolContext

# Threshold for triggering human approval (percentage of portfolio)
CONFIRM_THRESHOLD_PCT = 20


def propose_trade_execution(trade_plan: Dict, user_profile: Dict, tool_context: ToolContext) -> Dict:
    """
    Paper-trade execution gate with optional human approval.

    Args:
        trade_plan: Trade plan JSON (symbol, side, size_pct, entry, stop_loss, take_profit, time_horizon_days, notes)
        user_profile: Dict with at least a 'risk' field (conservative/balanced/aggressive)
        tool_context: ADK ToolContext for request_confirmation and state

    Returns:
        Dict with status: pending | approved | rejected | auto-approved, plus message and trade_plan echo.
    """
    size = float(trade_plan.get("size_pct", 0) or 0)
    risk = (user_profile.get("risk") or "balanced").lower()
    risky = (risk == "conservative" and size > 10) or size > CONFIRM_THRESHOLD_PCT

    # First call: request confirmation if risky
    if risky and not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"Potentially risky trade {trade_plan.get('symbol')} size {size}% for {risk} profile. Approve?",
            payload={"trade_plan": trade_plan, "user_profile": user_profile},
        )
        return {
            "status": "pending",
            "message": "Awaiting human approval for trade execution",
            "trade_plan": trade_plan,
        }

    # Resume after confirmation
    if risky:
        if tool_context.tool_confirmation.confirmed:
            return {
                "status": "approved",
                "message": "Human approved this trade plan",
                "trade_plan": trade_plan,
            }
        else:
            return {
                "status": "rejected",
                "message": "Human rejected this trade plan",
                "trade_plan": trade_plan,
            }

    # Safe path
    return {
        "status": "auto-approved",
        "message": "Trade within safe limits; auto-approved",
        "trade_plan": trade_plan,
    }
