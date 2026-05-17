import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.api.v1 import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("urbanflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from app.database import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        if db.query(User).count() == 0:
            logger.info("Empty database — run: python scripts/seed_data.py")
        db.close()
    except Exception as e:
        logger.warning("DB check skipped: %s", e)
    logger.info("UrbanFlow AI API started")
    yield
    logger.info("UrbanFlow AI API shutdown")


settings = get_settings()
app = FastAPI(
    title="UrbanFlow AI",
    description="AI-Powered Smart City Resource Optimization Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "urbanflow-api"}
