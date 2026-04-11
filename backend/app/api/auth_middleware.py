from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client, ClientOptions
from app.core.config import settings
from contextvars import ContextVar

_bearer = HTTPBearer(auto_error=False)

current_token: ContextVar[str] = ContextVar("current_token", default="")

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
    """Require a valid Supabase JWT and return the user_id."""
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Use context-free client for initial verification
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    try:
        user_response = supabase.auth.get_user(creds.credentials)
        if hasattr(user_response, 'user') and user_response.user:
            current_token.set(creds.credentials)
            return user_response.user.id
        raise Exception("Invalid user response")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token. {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """Return user_id if JWT is valid, else None."""
    if not creds:
        return None
        
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    try:
        user_response = supabase.auth.get_user(creds.credentials)
        if hasattr(user_response, 'user') and user_response.user:
            current_token.set(creds.credentials)
            return user_response.user.id
        return None
    except Exception:
        return None
