"""
Citizen Data Ingestion Router:
Ingests and queries geo-tagged citizen crack and slope-movement photos via MongoDB.
Provides a crowd-sourced secondary validation surface to confirm slope instability on the ground.
"""

import os
import base64
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas import CitizenReportCreate, CitizenReportResponse
from backend.database import db_manager
from backend.config import settings

router = APIRouter(prefix="/citizen-reports", tags=["Citizen Science & Crowd-Sourced Observations"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Geo-Tagged Citizen Crack / Slope Photo",
    description="Stores citizen ground observations and photos with a 2dsphere GeoJSON spatial coordinate in MongoDB."
)
async def submit_citizen_report(report: CitizenReportCreate):
    report_id = str(uuid.uuid4())
    timestamp_str = datetime.utcnow().isoformat() + "Z"

    # Save photo if base64 provided
    photo_url = None
    if report.photo_base64:
        try:
            # Strip base64 header if present (e.g. data:image/jpeg;base64,...)
            raw_b64 = report.photo_base64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]

            img_bytes = base64.b64decode(raw_b64)
            filename = f"crack_{report_id[:8]}.jpg"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            photo_url = f"/uploads/citizen_photos/{filename}"
        except Exception as e:
            print("[Photo Save Warning]", e)

    # Document formatted with standard GeoJSON 2dsphere specification
    doc = {
        "_id": report_id,
        "reporter_name": report.reporter_name,
        "phone_number": report.phone_number,
        "location": {
            "type": "Point",
            "coordinates": [report.longitude, report.latitude], # GeoJSON uses [Lon, Lat]
        },
        "latitude": report.latitude,
        "longitude": report.longitude,
        "elevation_m": report.elevation_m,
        "district": report.district or "Unspecified",
        "state": report.state or "India",
        "observation_type": report.observation_type,
        "crack_width_cm": report.crack_width_cm,
        "crack_length_m": report.crack_length_m,
        "movement_speed": report.movement_speed,
        "hazard_level": report.hazard_level,
        "notes": report.notes,
        "photo_url": photo_url,
        "timestamp": timestamp_str,
    }

    inserted_id = await db_manager.insert_citizen_report(doc)

    return {
        "status": "INGESTED",
        "report_id": inserted_id,
        "message": "Citizen geotechnical observation stored successfully in MongoDB cluster.",
        "location": {
            "latitude": report.latitude,
            "longitude": report.longitude,
            "coordinates_geojson": [report.longitude, report.latitude],
        },
        "observation_type": report.observation_type,
        "hazard_level": report.hazard_level,
        "photo_url": photo_url,
    }


@router.get(
    "/nearby",
    summary="Query Nearby Geo-Tagged Citizen Reports (2dsphere Index)",
    description="Uses MongoDB $near geospatial query to find ground cracks and slope movement within a radius of target coordinates."
)
async def get_nearby_citizen_reports(
    lat: float = Query(..., ge=6.5, le=38.5, description="Search center latitude"),
    lon: float = Query(..., ge=66.5, le=100.0, description="Search center longitude"),
    radius_km: float = Query(15.0, ge=0.5, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(25, ge=1, le=100, description="Maximum reports to return"),
):
    reports = await db_manager.query_nearby_reports(
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        limit=limit,
    )
    return {
        "search_center": {"latitude": lat, "longitude": lon},
        "radius_km": radius_km,
        "count": len(reports),
        "reports": reports,
    }


@router.get(
    "/stats",
    summary="Citizen Report Statistical Summary",
    description="Aggregates reported hazard types and severity distribution across the database."
)
async def get_report_stats():
    # Gather from database
    all_reports = await db_manager.query_nearby_reports(lat=20.0, lon=78.0, radius_km=3000.0, limit=1000)
    
    types_count = {}
    severity_count = {}
    for r in all_reports:
        t = r.get("observation_type", "other")
        types_count[t] = types_count.get(t, 0) + 1
        s = r.get("hazard_level", "UNKNOWN")
        severity_count[s] = severity_count.get(s, 0) + 1

    return {
        "total_verified_citizen_reports": len(all_reports),
        "breakdown_by_observation_type": types_count,
        "breakdown_by_hazard_level": severity_count,
    }
