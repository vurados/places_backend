from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.monitoring import metrics_middleware, metrics_endpoint
from core.config import settings
from api import api_router
from core.logging import setup_logging
from sqlalchemy import text
from fastapi import HTTPException
from core.database import engine

from contextlib import asynccontextmanager

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    yield
    # Shutdown logic
    await engine.dispose()

app = FastAPI(
    title="Urban Places Social App",
    description="App for sharing places and routes",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
@app.middleware("http")
async def metrics_middleware_wrapper(request, call_next):
    return await metrics_middleware(request, call_next)
app.add_route("/metrics", metrics_endpoint)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Urban Places Social App API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/live")
async def health_live():
    return {"status": "alive"}

@app.get("/health/ready")
async def health_ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")