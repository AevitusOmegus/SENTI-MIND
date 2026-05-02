"""
Journal API — CRUD for journal entries stored in Supabase.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from supabase import Client
from app.api.auth_middleware import get_current_user, get_authenticated_client

logger = logging.getLogger(__name__)

router = APIRouter()


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
    sb: Client = Depends(get_authenticated_client),
):
    try:
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
    except Exception as e:
        logger.exception("Failed to save journal entry for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to save journal entry.")


@router.get("/")
async def list_entries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
        result = (
            sb.table("journal_entries")
            .select("id, raw_text, category, risk_level, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.exception("Failed to list journal entries for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve journal entries.")


@router.post("/gratitude/", status_code=201)
async def save_gratitude(
    payload: GratitudeSaveRequest,
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
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
    except Exception as e:
        logger.exception("Failed to save gratitude snippet for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to save gratitude snippet.")


@router.get("/gratitude/")
async def list_gratitude(
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
        result = (
            sb.table("gratitude_snippets")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.exception("Failed to list gratitude snippets for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve gratitude snippets.")


@router.delete("/gratitude/{snippet_id}", status_code=204)
async def delete_gratitude(
    snippet_id: str,
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
        result = sb.table("gratitude_snippets").delete().eq("id", snippet_id).eq("user_id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Gratitude snippet not found.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete gratitude snippet %s for user %s", snippet_id, user_id)
        raise HTTPException(status_code=500, detail="Failed to delete gratitude snippet.")


@router.get("/{entry_id}")
async def get_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get journal entry %s for user %s", entry_id, user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve journal entry.")


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user),
    sb: Client = Depends(get_authenticated_client),
):
    try:
        result = sb.table("journal_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry not found.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete journal entry %s for user %s", entry_id, user_id)
        raise HTTPException(status_code=500, detail="Failed to delete journal entry.")
