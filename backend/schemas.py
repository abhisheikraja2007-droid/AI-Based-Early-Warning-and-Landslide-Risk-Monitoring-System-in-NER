"""
Pydantic Schemas for Request Validation and Response Serialization.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class InferenceRequest(BaseModel):
    latitude: float = Field(..., ge=6.5, le=38.5, description="Latitude in decimal degrees (India bounds)")
    longitude: float = Field(..., ge=66.5, le=100.0, description="Longitude in decimal degrees (India bounds)")
    event_date: str = Field(default="2025-07-16", description="Forecast target date (YYYY-MM-DD)")
    lead_time_hours: int = Field(default=12, ge=6, le=24, description="Early warning lead time window (6 to 24 hours)")
    custom_rainfall_24h: Optional[float] = Field(default=None, ge=0.0, description="Optional override for 24h event precipitation in mm")
    patch_filename: Optional[str] = Field(default=None, description="Optional Landslide4Sense .h5 patch filename")


class InferenceTaskResponse(BaseModel):
    task_id: str
    status: str
    poll_url: str
    message: str


class CitizenReportCreate(BaseModel):
    reporter_name: str = Field(..., min_length=2, description="Name of citizen or field volunteer")
    phone_number: Optional[str] = Field(default=None, description="Contact phone number")
    latitude: float = Field(..., ge=6.5, le=38.5, description="GPS Latitude")
    longitude: float = Field(..., ge=66.5, le=100.0, description="GPS Longitude")
    elevation_m: Optional[float] = Field(default=None, description="Barometric or GPS elevation in meters")
    district: Optional[str] = Field(default=None, description="Administrative district (e.g., Wayanad, Chamoli)")
    state: Optional[str] = Field(default=None, description="State (e.g., Kerala, Uttarakhand)")
    observation_type: str = Field(
        default="tension_crack",
        description="Physical observation: tension_crack, slope_subsidence, rockfall, mud_discharge, retaining_wall_tilt"
    )
    crack_width_cm: Optional[float] = Field(default=None, ge=0.0, description="Measured or estimated crack aperture in cm")
    crack_length_m: Optional[float] = Field(default=None, ge=0.0, description="Estimated longitudinal crack extent in meters")
    movement_speed: Optional[str] = Field(default="slow_creeping", description="Observed rate: slow_creeping, accelerating, sudden")
    hazard_level: str = Field(default="HIGH", description="Subjective urgency: LOW, MEDIUM, HIGH, EVACUATE")
    notes: Optional[str] = Field(default=None, description="Citizen notes or landmark description")
    photo_base64: Optional[str] = Field(default=None, description="Base64 encoded JPEG/PNG image")


class CitizenReportResponse(BaseModel):
    id: str
    reporter_name: str
    latitude: float
    longitude: float
    district: Optional[str]
    state: Optional[str]
    observation_type: str
    crack_width_cm: Optional[float]
    hazard_level: str
    timestamp: str
    photo_url: Optional[str]
    distance_km: Optional[float] = None


# ==============================================================================
# EDGE OFFLINE SYNC SCHEMAS (Timestamp-based Upserts)
# ==============================================================================

class SyncReportItem(BaseModel):
    device_report_id: Optional[str] = Field(default=None, description="Client-side UUID or unique string")
    device_id: str = Field(..., description="Unique mobile device hardware/app installation ID")
    client_timestamp: str = Field(..., description="ISO 8601 timestamp when observation was recorded locally offline")
    reporter_name: str = Field(..., description="Name of ground scout or panchayat field observer")
    phone_number: Optional[str] = None
    latitude: float = Field(..., ge=6.5, le=38.5)
    longitude: float = Field(..., ge=66.5, le=100.0)
    elevation_m: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None
    observation_type: str = Field(default="tension_crack")
    crack_width_cm: Optional[float] = None
    crack_length_m: Optional[float] = None
    movement_speed: Optional[str] = "slow_creeping"
    hazard_level: str = "HIGH"
    notes: Optional[str] = None
    photo_base64: Optional[str] = None


class BatchSyncRequest(BaseModel):
    device_id: str = Field(..., description="Identifier of the uploading device")
    sync_initiated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    reports: List[SyncReportItem] = Field(..., description="List of queued offline reports")


class BatchSyncResponse(BaseModel):
    status: str = "SUCCESS"
    storage_backend: str
    total_received: int
    upserted_count: int
    modified_count: int
    matched_count: int
    message: str


# ==============================================================================
# DELTA-ONLY GEOJSON SCHEMAS (Bandwidth-Optimized Edge Transmission)
# ==============================================================================

class DeltaGeoJSONProperties(BaseModel):
    segment_id: str
    corridor_name: str
    chainage_km: str
    location_name: str
    hazard_level: str  # NORMAL, MODERATE, HIGH_EARLY_WARNING, EMERGENCY_EVACUATION
    previous_hazard_level: str
    landslide_probability: float
    transition_timestamp: str
    delta_type: str  # HAZARD_ESCALATION, HAZARD_DEESCALATION, NEW_CRACK_DISCOVERY
    rainfall_24h_mm: float
    smap_soil_moisture: float
    recommended_action: str


class DeltaGeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]  # GeoJSON Point or LineString
    properties: DeltaGeoJSONProperties


class DeltaGeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    since_timestamp: Optional[str] = None
    generated_at: str
    total_corridor_segments: int
    delta_count: int
    bandwidth_saved_percent: float
    features: List[DeltaGeoJSONFeature]


class CorridorStatusResponse(BaseModel):
    corridor_id: str
    corridor_name: str
    total_length_km: float
    total_segments: int
    active_hazard_summary: Dict[str, int]
    last_updated: str
    segments: List[Dict[str, Any]]


# ==============================================================================
# HISTORIC REPLAY DEMO SCHEMAS (2022 Imphal-Jiribam Simulation)
# ==============================================================================

class ReplayStepDetail(BaseModel):
    step_index: int
    relative_time: str  # e.g., "T-72h", "T-24h", "T-12h", "T-6h", "T-0h"
    simulated_timestamp: str
    rainfall_24h_mm: float
    rainfall_7d_antecedent_mm: float
    smap_soil_saturation_pct: float
    critical_segment_id: str
    critical_location: str
    critical_risk_probability: float
    critical_hazard_level: str
    delta_escalations_count: int
    delta_geojson: DeltaGeoJSONFeatureCollection
    operational_advisory: str
