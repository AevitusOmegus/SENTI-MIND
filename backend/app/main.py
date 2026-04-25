import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api import router
from app.models.classifier import classifier

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        classifier.load()
        logger.info("ClinicalClassifier loaded successfully.")
    except FileNotFoundError as exc:
        logger.critical(
            "Model artifact missing — run scripts/train_model_improved.py first.\n%s", exc
        )
        raise SystemExit(1) from exc
    except Exception as exc:
        logger.critical("Failed to load classifier: %s", exc)
        raise SystemExit(1) from exc
    yield


app = FastAPI(
    title="SentiMind API",
    description="Multi-layer sentiment & emotion analysis engine",
    version="1.0.0",
    lifespan=lifespan,
)

VERCEL_ORIGIN = "https://senti-mind-mocha.vercel.app"

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
if VERCEL_ORIGIN not in allowed_origins:
    allowed_origins.append(VERCEL_ORIGIN)


# --- Failsafe CORS middleware (runs BEFORE FastAPI error handlers) ---
# Guarantees Access-Control-Allow-Origin is present even on 500 crashes,
# so the browser reports the real error instead of a misleading CORS block.
class ForceCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception("Unhandled error in CORS middleware: %s", exc)
            response = JSONResponse({"detail": "Internal server error."}, status_code=500)
        if origin in allowed_origins or not origin:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response


app.add_middleware(ForceCORSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "allowed_origins": allowed_origins}
