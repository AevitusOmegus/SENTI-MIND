"""
Auth middleware — Supabase JWT verification and RLS-aware client factory.

Architecture:
- A single module-level Supabase client is used for JWT verification.
- For RLS-authenticated DB operations, a per-request client is created
  via get_authenticated_client(), injecting the caller's JWT.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client, ClientOptions

from app.core.config import settings

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)

# Single module-level client for auth verification (no per-user token needed)
_supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


class AuthenticatedUser:
    """Holds the verified user_id and their raw JWT for RLS client creation."""

    __slots__ = ("user_id", "token")

    def __init__(self, user_id: str, token: str):
        self.user_id = user_id
        self.token = token


async def _verify_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[AuthenticatedUser]:
    """Verify a Supabase JWT and return an AuthenticatedUser, or None if no creds."""
    if not creds:
        return None

    try:
        user_response = _supabase.auth.get_user(creds.credentials)
        if hasattr(user_response, "user") and user_response.user:
            return AuthenticatedUser(
                user_id=user_response.user.id,
                token=creds.credentials,
            )
        raise Exception("Invalid user response")
    except Exception as e:
        logger.warning("Token verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    auth: Optional[AuthenticatedUser] = Depends(_verify_token),
) -> str:
    """Require a valid Supabase JWT and return the user_id string."""
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth.user_id


async def get_optional_user(
    auth: Optional[AuthenticatedUser] = Depends(_verify_token),
) -> Optional[str]:
    """Return user_id if JWT is valid, else None (no error raised)."""
    return auth.user_id if auth else None


async def get_authenticated_client(
    auth: Optional[AuthenticatedUser] = Depends(_verify_token),
) -> Client:
    """
    Return a Supabase client scoped to the caller's JWT for RLS.
    Must be used behind an auth-required route.
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options=ClientOptions(headers={"Authorization": f"Bearer {auth.token}"}),
    )
