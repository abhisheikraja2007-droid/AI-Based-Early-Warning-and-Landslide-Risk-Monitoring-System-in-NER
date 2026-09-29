"""
Inference API Router:
Dispatches heavy raster math and multi-sensor model inference off the main FastAPI web thread.
Supports asynchronous task queuing (Celery/Redis) with status polling.
"""

import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse

from backend.schemas import InferenceRequest, InferenceTaskResponse
from backend.tasks import (
    execute_heavy_raster_inference,
    run_celery_inference_task,
    task_store,
)
from backend.model_cache import model_cache

router = APIRouter(prefix="/inference", tags=["Early Warning & Model Inference"])
executor = ThreadPoolExecutor(max_workers=4)


def is_redis_available() -> bool:
    """Fast non-blocking check to verify if Redis broker is online."""
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.1, socket_timeout=0.1)
        client.ping()
        return True
    except Exception:
        return False


@router.post(
    "/predict-async",
    response_model=InferenceTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Asynchronously Trigger Heavy Raster & XGBoost Inference",
    description="Dispatches the 14-band raster math, spatial U-Net forward pass, IMD rolling precipitation calculation, and SMAP simulation off the web thread."
)
async def predict_landslide_async(
    request: InferenceRequest,
    background_tasks: BackgroundTasks,
):
    task_id = str(uuid.uuid4())
    task_store[task_id] = {
        "task_id": task_id,
        "status": "QUEUED",
        "created_at": str(asyncio.get_event_loop().time()),
    }

    # Resolve optional patch file
    patch_path = None
    if request.patch_filename:
        # Check TrainData / ValidData / TestData
        for sub in ["ValidData/img", "TrainData/img", "TestData/img"]:
            candidate = os.path.join(sub, request.patch_filename)
            if os.path.exists(candidate):
                patch_path = candidate
                break

    # 1. Try dispatching via Celery + Redis broker if Redis is reachable
    dispatched_celery = False
    if is_redis_available():
        try:
            celery_task = run_celery_inference_task.apply_async(
                kwargs={
                    "patch_path": patch_path,
                    "lat": request.latitude,
                    "lon": request.longitude,
                    "event_date": request.event_date,
                    "lead_time_hours": request.lead_time_hours,
                    "custom_rainfall_24h": request.custom_rainfall_24h,
                },
                task_id=task_id,
            )
            dispatched_celery = True
        except Exception:
            pass

    if not dispatched_celery:
        # Asynchronously run off main thread without blocking event loop
        def run_in_thread():
            task_store[task_id]["status"] = "PROCESSING"
            res = execute_heavy_raster_inference(
                patch_path=patch_path,
                lat=request.latitude,
                lon=request.longitude,
                event_date=request.event_date,
                lead_time_hours=request.lead_time_hours,
                custom_rainfall_24h=request.custom_rainfall_24h,
            )
            res["task_id"] = task_id
            task_store[task_id] = res

        executor.submit(run_in_thread)

    return InferenceTaskResponse(
        task_id=task_id,
        status="QUEUED",
        poll_url=f"/api/v1/inference/tasks/{task_id}",
        message="Inference job dispatched asynchronously off the main web thread."
    )


@router.get(
    "/tasks/{task_id}",
    summary="Poll Asynchronous Inference Task Status",
    description="Retrieves the completed landslide hazard prediction, SHAP driving factors, and telemetry."
)
async def get_task_status(task_id: str):
    if task_id not in task_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID '{task_id}' not found."
        )

    task_data = task_store[task_id]
    if task_data.get("status") in ["QUEUED", "PROCESSING"]:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=task_data,
        )
    return task_data


@router.post(
    "/predict-sync",
    summary="Synchronous Direct Inference (Using Cached In-Memory Models)",
    description="Direct zero-latency inference utilizing the pre-cached PyTorch and XGBoost models."
)
async def predict_landslide_sync(request: InferenceRequest):
    # Resolve optional patch
    patch_path = None
    if request.patch_filename:
        for sub in ["ValidData/img", "TrainData/img", "TestData/img"]:
            candidate = os.path.join(sub, request.patch_filename)
            if os.path.exists(candidate):
                patch_path = candidate
                break

    # Execute using in-memory model cache
    result = execute_heavy_raster_inference(
        patch_path=patch_path,
        lat=request.latitude,
        lon=request.longitude,
        event_date=request.event_date,
        lead_time_hours=request.lead_time_hours,
        custom_rainfall_24h=request.custom_rainfall_24h,
    )
    return result
