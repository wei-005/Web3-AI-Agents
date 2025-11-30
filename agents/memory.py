from typing import Any, Dict

from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


async def ensure_session(app_name: str, user_id: str, session_id: str) -> None:
    try:
        await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    except Exception:
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)


async def upsert_user_profile(app_name: str, user_id: str, session_id: str, profile: Dict[str, Any]) -> None:
    await ensure_session(app_name, user_id, session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    session.state["user_profile"] = profile
    await session_service.update_session(session)


async def get_user_profile(app_name: str, user_id: str, session_id: str) -> Dict[str, Any]:
    await ensure_session(app_name, user_id, session_id)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    return session.state.get("user_profile", {})
