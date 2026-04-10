import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import Base, engine
from app.routes import chat
from app.routes import knowledge

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# Resolve the frontend directory relative to this file
_HERE = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(_HERE, "..", "..", "frontend"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="MCUBE LUNA AI",
    description="LUNA AI Support Chatbot API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes (must be registered BEFORE static file mount) ──────────────────
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "message": "MCUBE LUNA Backend Running"}


# ── Serve frontend as static files (catches everything not matched above) ──────
# Chat UI  →  http://server/
# Admin    →  http://server/admin.html
# Widget   →  http://server/ (same UI, loaded via iframe by embed.js)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    logger.info("Serving frontend from: %s", FRONTEND_DIR)
else:
    logger.warning("Frontend directory not found at %s — static serving disabled", FRONTEND_DIR)
