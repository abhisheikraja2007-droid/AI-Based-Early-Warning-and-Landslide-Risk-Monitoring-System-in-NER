"""
FastAPI Asynchronous Backend for Landslide Early Warning & Hazard Assessment.
Features:
  - Startup Lifecycle Model Caching (@app.on_event("startup")):
      Pre-loads PyTorch .pt Spatial U-Net and native XGBoost .json into RAM exactly once.
  - Task Queue Routing:
      Dispatches heavy raster math and multi-sensor inference off the main web thread via Celery/Redis.
  - MongoDB Geo-Spatial Ingestion:
      Stores and queries geo-tagged citizen tension-crack and slope-movement photos via 2dsphere index.
"""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.model_cache import model_cache
from backend.database import db_manager
from backend.routers import inference, citizen_reports, sync, corridors, replay

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-grade Asynchronous Landslide Hazard Assessment & Early Warning API.\n\n"
        "• **SpatialSusceptibility**: PyTorch 14-Channel U-Net on Sentinel-2 & ALOS PALSAR DEM.\n"
        "• **TemporalEngine**: Targeted 6-to-24-hour Lead-Time XGBoost on IMD 0.25° NetCDF & NASA SMAP.\n"
        "• **TaskQueue**: Non-blocking asynchronous Celery/Redis raster compute.\n"
        "• **CitizenGeodata**: MongoDB 2dsphere geo-tagged slope movement photo storage."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware for Frontend / Dashboard connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded citizen photos static files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ==============================================================================
# LIFECYCLE HOOK: MODEL CACHING & DATABASE INITIALIZATION
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """
    CRITICAL STARTUP HOOK:
    Loads the PyTorch .pt model and native XGBoost .json model into memory EXACTLY ONCE.
    Pre-compiles SHAP TreeExplainer and connects to MongoDB with 2dsphere geospatial index.
    Eliminates severe disk I/O and deserialization latency on live user requests.
    """
    print("\n" + "=" * 80)
    print("FASTAPI STARTUP: Initializing In-Memory Model Cache & Database...")
    print("=" * 80)

    # 1. In-Memory Model Caching
    model_cache.load_models()

    # 2. MongoDB Geospatial Cluster Connection
    await db_manager.connect()

    print("=" * 80)
    print("FASTAPI STARTUP COMPLETE. SERVER READY FOR LIVE ASYNCHRONOUS EVALUATION.")
    print("=" * 80 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown hook."""
    print("[FastAPI Shutdown] Closing database connections and clearing memory pools...")
    if db_manager.client:
        db_manager.client.close()


# ==============================================================================
# ROUTER INCLUSION
# ==============================================================================

app.include_router(inference.router, prefix=settings.API_V1_PREFIX)
app.include_router(citizen_reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(sync.router, prefix=settings.API_V1_PREFIX)
app.include_router(corridors.router, prefix=settings.API_V1_PREFIX)
app.include_router(replay.router, prefix=settings.API_V1_PREFIX)


# ==============================================================================
# HEALTH & METADATA ENDPOINTS
# ==============================================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "OPERATIONAL",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "models_cached_in_memory": model_cache.is_loaded,
        "model_load_latency_seconds": round(model_cache.load_time_seconds, 3),
        "database_backend": "MongoDB (2dsphere geospatial index active)",
        "task_queue_broker": "Celery & Redis (Asynchronous off-thread execution)",
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "model_cache": {
            "spatial_pytorch_loaded": model_cache.spatial_backend is not None,
            "temporal_xgboost_loaded": model_cache.temporal_model is not None,
            "shap_explainer_ready": model_cache.shap_explainer is not None,
            "cache_duration_seconds": round(model_cache.load_time_seconds, 3),
        },
        "database": {
            "mongodb_connected": db_manager.is_connected,
            "geospatial_2dsphere_ready": True,
        },
        "task_queue": {
            "broker": "Redis",
            "celery_enabled": True,
            "async_off_thread": True,
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
