from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.monitoring import metrics_middleware, metrics_endpoint
from app.core.config import settings
from app.api import api_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Urban Places Social App",
    description="App for sharing places and routes",
    version="0.1.0",
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
    return {"status": "healthy"}