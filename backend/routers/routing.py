"""
FastAPI Router for ISRO Bhuvan Emergency Routing and Evacuation Detours.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.bhuvan_service import bhuvan_routing_service
from backend.config import settings

router = APIRouter(prefix="/routing", tags=["ISRO Bhuvan Emergency Routing"])


class EvacuationRouteRequest(BaseModel):
    origin_lat: float = Field(..., example=24.77, description="Latitude of starting location (e.g. affected village / Tupul)")
    origin_lon: float = Field(..., example=93.68, description="Longitude of starting location")
    dest_lat: float = Field(..., example=24.81, description="Latitude of safe evacuation center / hospital")
    dest_lon: float = Field(..., example=93.94, description="Longitude of safe evacuation center / hospital")
    avoid_landslide_corridors: bool = Field(True, description="Whether to avoid sectors marked RED/ORANGE for landslides")


@router.get("/status")
async def get_routing_status():
    """
    Returns the current configuration and authentication status of the ISRO Bhuvan Routing API.
    """
    token_present = bool(settings.BHUVAN_ROUTING_API_KEY)
    masked_token = f"{settings.BHUVAN_ROUTING_API_KEY[:6]}...{settings.BHUVAN_ROUTING_API_KEY[-4:]}" if token_present else None
    
    return {
        "status": "OPERATIONAL",
        "service": "ISRO Bhuvan Routing API & Emergency Evacuation Engine",
        "is_authenticated": token_present,
        "active_token": masked_token,
        "capabilities": [
            "Shortest Path Calculation",
            "Landslide Corridor Hazard Avoidance",
            "Emergency Evacuation LineString GeoJSON",
            "Dynamic Turn-by-Turn Rerouting"
        ]
    }


@router.post("/evacuation-route")
async def calculate_evacuation_route(request: EvacuationRouteRequest):
    """
    Calculates the safest evacuation path connecting an origin to a safe hospital or relief camp,
    actively avoiding high-risk landslide sectors.
    """
    try:
        route = bhuvan_routing_service.compute_evacuation_route(
            origin=(request.origin_lat, request.origin_lon),
            destination=(request.dest_lat, request.dest_lon),
            avoid_zones=[{"hazard": "CRITICAL_LANDSLIDE"}] if request.avoid_landslide_corridors else []
        )
        return route
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evacuation routing failed: {str(e)}")
