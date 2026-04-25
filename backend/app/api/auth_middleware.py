from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client, ClientOptions
from app.core.config import settings
from contextvars import ContextVar

_bearer = HTTPBearer(auto_error=False)

current_token: ContextVar[str] = ContextVar("current_token", default="")

# Shared client for JWT verification — no user context, created once at import time
_base_client: Client | None = None


def _get_base_client() -> Client:
    global _base_client
    if _base_client is None:
        _base_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _base_client


def get_supabase_client() -> Client:
    token = current_token.get()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options=ClientOptions(headers=headers)
    )


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase = _get_base_client()
    try:
        user_response = supabase.auth.get_user(creds.credentials)
        if hasattr(user_response, "user") and user_response.user:
            current_token.set(creds.credentials)
            return user_response.user.id
        raise Exception("Invalid user response")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    if not creds:
        return None

    supabase = _get_base_client()
    try:
        user_response = supabase.auth.get_user(creds.credentials)
        if hasattr(user_response, "user") and user_response.user:
            current_token.set(creds.credentials)
            return user_response.user.id
        return None
    except Exception:
        return None
