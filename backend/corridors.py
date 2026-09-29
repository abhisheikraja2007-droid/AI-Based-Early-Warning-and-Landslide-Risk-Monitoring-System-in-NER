"""
Corridor Management Engine for Critical Mountain Highways.
Specialized for the NH-37 Imphal-Jiribam Corridor (Manipur, India).
Monitors 135 km of highway chainage broken down into discrete geotechnical sectors.
Generates lightweight Delta-Only GeoJSON packets when road segments transition to high-risk.
"""

import time
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from backend.model_cache import model_cache
from backend.schemas import (
    DeltaGeoJSONFeature,
    DeltaGeoJSONProperties,
    DeltaGeoJSONFeatureCollection,
    CorridorStatusResponse,
)

# ==============================================================================
# NH-37 IMPHAL-JIRIBAM HIGHWAY CORRIDOR DEFINITION
# ==============================================================================
# The lifeline highway connecting Manipur to the rest of India via Assam.
# Traverses steep Disang flysch formations and river gorges prone to catastrophic failure.

NH37_CORRIDOR_METADATA = {
    "corridor_id": "NH37-IMPHAL-JIRIBAM",
    "corridor_name": "NH-37 Imphal-Jiribam National Highway",
    "state": "Manipur",
    "total_length_km": 135.0,
    "elevation_range_m": [150.0, 1100.0],
}

DEFAULT_CORRIDOR_SEGMENTS = [
    {
        "segment_id": "NH37-SEG-01",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 0.0 - Km 12.0",
        "location_name": "Imphal Valley West",
        "latitude": 24.805,
        "longitude": 93.910,
        "base_slope_deg": 4.5,
        "base_spatial_susceptibility": 0.08,
        "start_coord": [93.940, 24.810],
        "end_coord": [93.880, 24.800],
    },
    {
        "segment_id": "NH37-SEG-02",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 12.0 - Km 24.0",
        "location_name": "Kangchup Foot Hills",
        "latitude": 24.790,
        "longitude": 93.845,
        "base_slope_deg": 14.0,
        "base_spatial_susceptibility": 0.16,
        "start_coord": [93.880, 24.800],
        "end_coord": [93.810, 24.780],
    },
    {
        "segment_id": "NH37-SEG-03",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 24.0 - Km 38.0",
        "location_name": "Sinam / Awangkhul Sector",
        "latitude": 24.775,
        "longitude": 93.745,
        "base_slope_deg": 28.5,
        "base_spatial_susceptibility": 0.35,
        "start_coord": [93.810, 24.780],
        "end_coord": [93.680, 24.770],
    },
    {
        "segment_id": "NH37-SEG-04",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 38.0 - Km 50.0",
        "location_name": "Tupul Railway Yard / Ijei Confluence",
        "latitude": 24.712,
        "longitude": 93.642,
        "base_slope_deg": 38.2,
        "base_spatial_susceptibility": 0.48,  # Historic Epicenter: High Disang flysch susceptibility
        "start_coord": [93.680, 24.770],
        "end_coord": [93.640, 24.710],
    },
    {
        "segment_id": "NH37-SEG-05",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 50.0 - Km 62.0",
        "location_name": "Noney Bridge & River Gorge",
        "latitude": 24.730,
        "longitude": 93.590,
        "base_slope_deg": 34.0,
        "base_spatial_susceptibility": 0.43,
        "start_coord": [93.640, 24.710],
        "end_coord": [93.590, 24.730],
    },
    {
        "segment_id": "NH37-SEG-06",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 62.0 - Km 76.0",
        "location_name": "Khongsang Ridge Sector",
        "latitude": 24.760,
        "longitude": 93.530,
        "base_slope_deg": 24.0,
        "base_spatial_susceptibility": 0.28,
        "start_coord": [93.590, 24.730],
        "end_coord": [93.530, 24.760],
    },
    {
        "segment_id": "NH37-SEG-07",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 76.0 - Km 90.0",
        "location_name": "Rengpang / Irang River Approach",
        "latitude": 24.755,
        "longitude": 93.480,
        "base_slope_deg": 29.0,
        "base_spatial_susceptibility": 0.36,
        "start_coord": [93.530, 24.760],
        "end_coord": [93.430, 24.750],
    },
    {
        "segment_id": "NH37-SEG-08",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 90.0 - Km 104.0",
        "location_name": "Nungba Sub-Divisional Pass",
        "latitude": 24.750,
        "longitude": 93.390,
        "base_slope_deg": 22.0,
        "base_spatial_susceptibility": 0.24,
        "start_coord": [93.430, 24.750],
        "end_coord": [93.350, 24.760],
    },
    {
        "segment_id": "NH37-SEG-09",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 104.0 - Km 120.0",
        "location_name": "Barak River / Oinamlong",
        "latitude": 24.770,
        "longitude": 93.315,
        "base_slope_deg": 31.0,
        "base_spatial_susceptibility": 0.38,
        "start_coord": [93.350, 24.760],
        "end_coord": [93.280, 24.770],
    },
    {
        "segment_id": "NH37-SEG-10",
        "corridor_name": "NH-37 Imphal-Jiribam",
        "chainage_km": "Km 120.0 - Km 135.0",
        "location_name": "Jiribam Foothills & Assam Plain",
        "latitude": 24.800,
        "longitude": 93.200,
        "base_slope_deg": 9.0,
        "base_spatial_susceptibility": 0.10,
        "start_coord": [93.280, 24.770],
        "end_coord": [93.120, 24.800],
    },
]


class CorridorHazardManager:
    """
    Stateful Highway Corridor Hazard Tracker.
    Maintains real-time segment states and detects hazard escalations.
    Generates bandwidth-efficient Delta-Only GeoJSON updates.
    """

    def __init__(self):
        self.segments_state: Dict[str, Dict[str, Any]] = {}
        self.history_transitions: List[Dict[str, Any]] = []
        self._initialize_segments()

    def _initialize_segments(self):
        """Initializes all corridor segments to baseline NORMAL conditions."""
        now_iso = datetime.now(timezone.utc).isoformat()
        for seg in DEFAULT_CORRIDOR_SEGMENTS:
            s_id = seg["segment_id"]
            self.segments_state[s_id] = {
                **seg,
                "hazard_level": "NORMAL",
                "previous_hazard_level": "NORMAL",
                "landslide_probability": 0.05,
                "rainfall_24h_mm": 5.0,
                "smap_soil_moisture": 0.22,
                "transition_timestamp": now_iso,
                "last_evaluated": now_iso,
                "delta_type": "INITIAL_BASELINE",
                "recommended_action": "Normal highway transit permissible.",
            }

    def evaluate_corridor(
        self,
        rainfall_24h_map: Optional[Dict[str, float]] = None,
        rainfall_7d_map: Optional[Dict[str, float]] = None,
        smap_override: Optional[float] = None,
        timestamp_iso: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Evaluates machine learning landslide probability for all segments.
        Detects hazard level transitions and records delta events.
        """
        now_iso = timestamp_iso or datetime.now(timezone.utc).isoformat()
        transitioned_segments = []

        for seg_id, seg in self.segments_state.items():
            rf_24h = rainfall_24h_map.get(seg_id, 10.0) if rainfall_24h_map else 10.0
            rf_7d = rainfall_7d_map.get(seg_id, rf_24h * 3.5) if rainfall_7d_map else rf_24h * 3.5
            spatial_score = seg["base_spatial_susceptibility"]

            # Compute SMAP satellite proxy
            smap_feat = model_cache.smap_engine.compute_smap_proxy(
                rainfall_24h_mm=rf_24h,
                rainfall_7d_mm=rf_7d,
                api_7d=rf_7d * 0.75,
                slope_susceptibility=spatial_score,
            )
            if smap_override is not None:
                smap_feat["smap_surface_sm"] = smap_override

            # Formulate feature vector for XGBoost model
            feature_vector = [
                spatial_score,
                rf_24h,
                rf_24h * 1.8, # 3-day sum proxy
                rf_7d,
                rf_7d * 0.75, # 7-day API
                rf_24h / max(rf_7d / 7.0, 1.0), # Intensity ratio
                rf_24h - (rf_7d / 7.0), # Acceleration
                smap_feat["smap_surface_sm"],
                smap_feat["smap_rootzone_sm"],
                smap_feat["smap_soil_water_index"],
                smap_feat["smap_saturation_ratio"],
                smap_feat["smap_pore_pressure_proxy"],
            ]

            prob = 0.05
            if model_cache.temporal_model is not None:
                x_arr = np.array([feature_vector], dtype=np.float32)
                prob = float(model_cache.temporal_model.predict_proba(x_arr)[0, 1])
            else:
                # Analytical fallback rule
                prob = min(0.99, spatial_score * (rf_24h / 120.0))

            # Determine new hazard tier
            if prob >= 0.75:
                new_hazard = "EMERGENCY_EVACUATION"
                action = "RED ALERT: Complete highway closure. Order immediate vehicle stoppage & evacuation to safe shelters."
            elif prob >= 0.50:
                new_hazard = "HIGH_EARLY_WARNING"
                action = "ORANGE ALERT: Divert heavy freight. Deploy SDRF/BRO clearing bulldozers to high-risk chainage."
            elif prob >= 0.28:
                new_hazard = "MODERATE_ADVISORY"
                action = "YELLOW ADVISORY: Reduced speed limit 20 km/h. High vigilance for rolling boulders & mud discharge."
            else:
                new_hazard = "NORMAL"
                action = "GREEN: Normal mountain transit permissible."

            old_hazard = seg["hazard_level"]

            # Detect state transition
            if new_hazard != old_hazard or prob != seg["landslide_probability"]:
                is_escalation = (new_hazard in ["HIGH_EARLY_WARNING", "EMERGENCY_EVACUATION"] and old_hazard not in ["HIGH_EARLY_WARNING", "EMERGENCY_EVACUATION"])
                delta_type = "HAZARD_ESCALATION" if is_escalation else "HAZARD_UPDATE"

                updated_segment = {
                    **seg,
                    "previous_hazard_level": old_hazard,
                    "hazard_level": new_hazard,
                    "landslide_probability": round(prob, 4),
                    "rainfall_24h_mm": round(rf_24h, 2),
                    "smap_soil_moisture": round(smap_feat["smap_surface_sm"], 3),
                    "transition_timestamp": now_iso,
                    "last_evaluated": now_iso,
                    "delta_type": delta_type,
                    "recommended_action": action,
                }

                self.segments_state[seg_id] = updated_segment
                if new_hazard != old_hazard:
                    transitioned_segments.append(updated_segment)
                    self.history_transitions.append(copy.deepcopy(updated_segment))

        return transitioned_segments

    def get_corridor_status(self) -> CorridorStatusResponse:
        """Returns the full baseline status of the entire highway corridor."""
        now_iso = datetime.now(timezone.utc).isoformat()
        segments_list = list(self.segments_state.values())

        summary = {
            "NORMAL": 0,
            "MODERATE_ADVISORY": 0,
            "HIGH_EARLY_WARNING": 0,
            "EMERGENCY_EVACUATION": 0,
        }
        for s in segments_list:
            lvl = s.get("hazard_level", "NORMAL")
            summary[lvl] = summary.get(lvl, 0) + 1

        return CorridorStatusResponse(
            corridor_id=NH37_CORRIDOR_METADATA["corridor_id"],
            corridor_name=NH37_CORRIDOR_METADATA["corridor_name"],
            total_length_km=NH37_CORRIDOR_METADATA["total_length_km"],
            total_segments=len(segments_list),
            active_hazard_summary=summary,
            last_updated=now_iso,
            segments=segments_list,
        )

    def get_delta_geojson(
        self,
        since_timestamp: Optional[str] = None,
        only_escalations: bool = True,
    ) -> DeltaGeoJSONFeatureCollection:
        """
        CRITICAL LOW-BANDWIDTH EDGE METHOD:
        Never transmits full static maps/polygons across slow 2G/EDGE mountain networks.
        Extracts ONLY the discrete highway segments that have transitioned to high risk.
        Calculates payload bandwidth savings (>85%).
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        delta_features: List[DeltaGeoJSONFeature] = []

        all_segments = list(self.segments_state.values())
        total_segments = len(all_segments)

        for s in all_segments:
            # Check if this segment transitioned
            trans_ts = s.get("transition_timestamp", "")
            is_recent = True
            if since_timestamp:
                is_recent = trans_ts >= since_timestamp

            is_high_risk = s.get("hazard_level") in ["HIGH_EARLY_WARNING", "EMERGENCY_EVACUATION"]
            has_changed = s.get("hazard_level") != s.get("previous_hazard_level")

            include_segment = False
            if only_escalations:
                include_segment = is_high_risk and (has_changed or is_recent)
            else:
                include_segment = has_changed or is_recent

            if include_segment:
                # Build LineString geometry for the highway segment
                feature = DeltaGeoJSONFeature(
                    type="Feature",
                    geometry={
                        "type": "LineString",
                        "coordinates": [s["start_coord"], s["end_coord"]],
                    },
                    properties=DeltaGeoJSONProperties(
                        segment_id=s["segment_id"],
                        corridor_name=s["corridor_name"],
                        chainage_km=s["chainage_km"],
                        location_name=s["location_name"],
                        hazard_level=s["hazard_level"],
                        previous_hazard_level=s["previous_hazard_level"],
                        landslide_probability=s["landslide_probability"],
                        transition_timestamp=s["transition_timestamp"],
                        delta_type=s.get("delta_type", "HAZARD_ESCALATION"),
                        rainfall_24h_mm=s["rainfall_24h_mm"],
                        smap_soil_moisture=s["smap_soil_moisture"],
                        recommended_action=s["recommended_action"],
                    ),
                )
                delta_features.append(feature)

        # Compute bandwidth saving relative to full corridor transmission
        delta_count = len(delta_features)
        if total_segments > 0:
            saved_pct = round((1.0 - (delta_count / total_segments)) * 100.0, 1)
        else:
            saved_pct = 100.0

        return DeltaGeoJSONFeatureCollection(
            type="FeatureCollection",
            since_timestamp=since_timestamp,
            generated_at=now_iso,
            total_corridor_segments=total_segments,
            delta_count=delta_count,
            bandwidth_saved_percent=saved_pct,
            features=delta_features,
        )


corridor_manager = CorridorHazardManager()
