"""
Edge Sync API Router:
Handles batch upload of offline queued mobile citizen reports when reconnecting to high connectivity.
Uses MongoDB bulk upsert operations indexed by device_report_id and original device timestamps
to prevent duplicate records and chronologically order the ground truth.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Query

from backend.schemas import BatchSyncRequest, BatchSyncResponse
from backend.database import db_manager

router = APIRouter(prefix="/sync", tags=["Edge Sync & Offline Ingestion"])


@router.post(
    "",
    response_model=BatchSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk Upsert Queued Reports from Reconnected Mobile App",
    description=(
        "When mobile devices in rural valleys regain high connectivity, they blast batches of "
        "queued geotechnical crack/slope-movement reports. This endpoint executes atomic MongoDB "
        "bulk upserts indexed by device_report_id and original client_timestamp, preventing "
        "duplicate entries and maintaining strict chronological ground-truth integrity."
    )
)
async def bulk_sync_queued_reports(payload: BatchSyncRequest):
    if not payload.reports:
        return BatchSyncResponse(
            status="SUCCESS",
            storage_backend="None",
            total_received=0,
            upserted_count=0,
            modified_count=0,
            matched_count=0,
            message="No reports provided in sync batch."
        )

    # Convert Pydantic models to dicts
    report_dicts = []
    for r in payload.reports:
        d = r.dict()
        d["uploaded_by_device"] = payload.device_id
        d["sync_server_received_at"] = payload.sync_initiated_at
        report_dicts.append(d)

    # Execute MongoDB bulk write upsert
    result = await db_manager.bulk_upsert_citizen_reports(report_dicts)

    return BatchSyncResponse(
        status="SUCCESS",
        storage_backend=result["storage_backend"],
        total_received=result["total_received"],
        upserted_count=result["upserted_count"],
        modified_count=result["modified_count"],
        matched_count=result["matched_count"],
        message=(
            f"Successfully processed {result['total_received']} queued reports: "
            f"{result['upserted_count']} new upserted, {result['modified_count']} updated duplicates."
        )
    )


@router.get(
    "/reports",
    summary="Retrieve Chronologically Ordered Ground-Truth Reports",
    description="Returns citizen reports ordered chronologically by original device recording timestamp."
)
async def get_chronological_reports(limit: int = Query(default=50, ge=1, le=500)):
    reports = await db_manager.get_chronological_reports(limit=limit)
    return {
        "count": len(reports),
        "reports": reports,
        "ordering": "client_timestamp ASC",
    }
