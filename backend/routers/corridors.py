"""
Corridors & Delta-GeoJSON API Router:
Serves highway corridor hazard status and bandwidth-optimized Delta-Only GeoJSON updates.
Prevents full-map retransmissions across low-bandwidth 2G/EDGE networks in rural mountain valleys.
"""

from typing import Optional, Dict
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

from backend.corridors import corridor_manager
from backend.schemas import (
    CorridorStatusResponse,
    DeltaGeoJSONFeatureCollection,
)

router = APIRouter(prefix="/corridors", tags=["Corridors & Delta-GeoJSON Edge Updates"])


@router.get(
    "/nh37-imphal-jiribam",
    response_model=CorridorStatusResponse,
    summary="Get Full Baseline Corridor Geometry & Hazard Status",
    description="Retrieves the entire NH-37 Imphal-Jiribam highway corridor (135 km) with all discrete monitored sectors."
)
async def get_corridor_baseline():
    return corridor_manager.get_corridor_status()


@router.get(
    "/delta",
    response_model=DeltaGeoJSONFeatureCollection,
    summary="Retrieve Bandwidth-Efficient Delta-Only GeoJSON Updates",
    description=(
        "CRITICAL LOW-BANDWIDTH EDGE ENDPOINT:\n\n"
        "To accommodate slow 2G/EDGE connections in rural valleys, the backend never sends "
        "the full static map back to the client. This endpoint delivers only lightweight GeoJSON "
        "deltas containing the specific highway coordinates/chainages that have transitioned to high-risk."
    )
)
async def get_delta_geojson(
    since_timestamp: Optional[str] = Query(
        default=None,
        description="ISO 8601 timestamp of client's last sync. Only transitions after this timestamp will be included."
    ),
    only_escalations: bool = Query(
        default=True,
        description="If True, only returns segments escalating into HIGH_EARLY_WARNING or EMERGENCY_EVACUATION."
    ),
):
    return corridor_manager.get_delta_geojson(
        since_timestamp=since_timestamp,
        only_escalations=only_escalations,
    )


class EvaluateCorridorPayload(BaseModel):
    uniform_rainfall_24h_mm: Optional[float] = None
    custom_rainfall_map: Optional[Dict[str, float]] = None
    smap_soil_moisture_override: Optional[float] = None


@router.post(
    "/evaluate",
    summary="Evaluate Machine Learning Risk Across Corridor Segments",
    description="Runs spatial U-Net + temporal XGBoost + SMAP inference across all segments to detect new transitions."
)
async def evaluate_corridor_risk(payload: EvaluateCorridorPayload):
    rf_map = payload.custom_rainfall_map or {}
    if payload.uniform_rainfall_24h_mm is not None:
        for s in corridor_manager.segments_state.keys():
            rf_map[s] = payload.uniform_rainfall_24h_mm

    transitions = corridor_manager.evaluate_corridor(
        rainfall_24h_map=rf_map,
        smap_override=payload.smap_soil_moisture_override,
    )

    return {
        "status": "EVALUATED",
        "transitions_detected": len(transitions),
        "transitioned_segments": [
            {
                "segment_id": t["segment_id"],
                "location_name": t["location_name"],
                "previous_hazard": t["previous_hazard_level"],
                "new_hazard": t["hazard_level"],
                "probability": t["landslide_probability"],
            }
            for t in transitions
        ],
        "delta_geojson_url": "/api/v1/corridors/delta",
    }
