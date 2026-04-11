"""
Mood API — save mood logs and return heatmap data.
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase import Client
from app.api.auth_middleware import get_current_user, get_supabase_client
from app.core.config import settings

router = APIRouter()


def _sb() -> Client:
    return get_supabase_client()


class MoodLogRequest(BaseModel):
    category: str
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    entry_id: Optional[str] = None


@router.post("/", status_code=201)
async def log_mood(
    payload: MoodLogRequest,
    user_id: str = Depends(get_current_user),
):
    sb = _sb()
    result = (
        sb.table("mood_logs")
        .insert({
            "user_id": user_id,
            "category": payload.category,
            "confidence": payload.confidence,
            "risk_level": payload.risk_level,
            "risk_score": payload.risk_score,
            "entry_id": payload.entry_id,
            "logged_date": date.today().isoformat(),
        })
        .execute()
    )
    return result.data[0]


@router.get("/heatmap")
async def get_heatmap(user_id: str = Depends(get_current_user)):
    """Return the last 30 days of mood logs (one entry per day — latest wins)."""
    sb = _sb()
    since = (date.today() - timedelta(days=29)).isoformat()
    result = (
        sb.table("mood_logs")
        .select("logged_date, category, risk_level, confidence")
        .eq("user_id", user_id)
        .gte("logged_date", since)
        .order("logged_date", desc=False)
        .execute()
    )

    # Collapse to one entry per day (latest)
    by_date: dict = {}
    for row in result.data:
        by_date[row["logged_date"]] = row

    # Build trend feedback
    entries = list(by_date.values())
    feedback = _generate_feedback(entries)

    return {"days": list(by_date.values()), "feedback": feedback}


@router.get("/trends")
async def get_trends(
    days: int = 30,
    user_id: str = Depends(get_current_user),
):
    """Return mood trend data for line charts."""
    sb = _sb()
    since = (date.today() - timedelta(days=days - 1)).isoformat()
    result = (
        sb.table("mood_logs")
        .select("logged_date, category, confidence, risk_score")
        .eq("user_id", user_id)
        .gte("logged_date", since)
        .order("logged_date", desc=False)
        .execute()
    )
    return result.data


def _generate_feedback(entries: list) -> str:
    if not entries:
        return "No mood data yet. Start journaling to see your trends!"

    POSITIVE = {"Normal"}
    NEGATIVE = {"Depression", "Suicidal", "Anxiety", "Bipolar", "Stress", "Personality disorder"}

    recent = entries[-7:]  # last 7 days
    positive_count = sum(1 for e in recent if e["category"] in POSITIVE)
    negative_count = sum(1 for e in recent if e["category"] in NEGATIVE)

    if positive_count >= 5:
        return "🌟 Great week! You've had mostly positive days — keep it up."
    elif positive_count >= 3:
        return "💚 Things are looking up. You've had more good days than difficult ones recently."
    elif negative_count >= 5:
        return "💙 It's been a tough week. Remember to use the wellness tools and reach out for support."
    elif negative_count >= 3:
        return "🌤️ Some difficult days recently. Try the Box Breather or Grounding Tool when things feel heavy."
    else:
        return "📊 Your mood has been mixed this week. Keep checking in — consistency helps."
