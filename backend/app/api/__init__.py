from fastapi import APIRouter
from app.api.analysis import router as analysis_router
from app.api.journal import router as journal_router
from app.api.mood import router as mood_router
from app.api.screener import router as screener_router

router = APIRouter()
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
router.include_router(journal_router, prefix="/journal", tags=["Journal"])
router.include_router(mood_router, prefix="/mood", tags=["Mood"])
router.include_router(screener_router, prefix="/screener", tags=["Screener"])
