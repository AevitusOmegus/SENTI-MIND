"""
Journal API — CRUD for journal entries stored in Supabase.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from supabase import Client
from app.api.auth_middleware import get_current_user, get_supabase_client
from app.core.config import settings

router = APIRouter()


def _sb() -> Client:
    return get_supabase_client()


class JournalSaveRequest(BaseModel):
    raw_text: str
    analysis: dict
    category: Optional[str] = None
    risk_level: Optional[str] = None


class GratitudeSaveRequest(BaseModel):
    text: str
    source_entry_id: Optional[str] = None


@router.post("/", status_code=201)
async def save_entry(
    payload: JournalSaveRequest,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    result = (
        sb.table("journal_entries")
        .insert({
            "user_id": user_id,
            "raw_text": payload.raw_text,
            "analysis": payload.analysis,
            "category": payload.category,
            "risk_level": payload.risk_level,
        })
        .execute()
    )
    return result.data[0]


@router.get("/")
async def list_entries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    result = (
        sb.table("journal_entries")
        .select("id, raw_text, category, risk_level, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data


# --- Gratitude Snippets ---
# NOTE: These MUST be declared before /{entry_id} so FastAPI doesn't
# match "gratitude" as an entry_id.

@router.post("/gratitude/", status_code=201)
async def save_gratitude(
    payload: GratitudeSaveRequest,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    result = (
        sb.table("gratitude_snippets")
        .insert({
            "user_id": user_id,
            "text": payload.text,
            "source_entry_id": payload.source_entry_id,
        })
        .execute()
    )
    return result.data[0]


@router.get("/gratitude/")
async def list_gratitude(user_id: str = Depends(get_current_user)):
    sb = _sb()
    result = (
        sb.table("gratitude_snippets")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.delete("/gratitude/{snippet_id}", status_code=204)
async def delete_gratitude(
    snippet_id: str,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    sb.table("gratitude_snippets").delete().eq("id", snippet_id).eq("user_id", user_id).execute()


# --- Single entry operations (MUST come after static sub-paths) ---

@router.get("/{entry_id}")
async def get_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    result = (
        sb.table("journal_entries")
        .select("*")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return result.data


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    sb.table("journal_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()

