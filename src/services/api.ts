/**
 * Live API Client for Drishti-NER AI Landslide Early Warning Backend
 * Connects directly to FastAPI backend on http://localhost:8000 (via Vite proxy /api/v1)
 * Eliminates all mock data with real-time PyTorch & XGBoost model inference.
 */

const API_BASE = '/api/v1';

export interface BackendCorridorSegment {
  segment_id: string;
  corridor_name: string;
  chainage_km: string;
  location_name: string;
  latitude: number;
  longitude: number;
  base_slope_deg: number;
  current_hazard_level: 'NORMAL' | 'WATCH' | 'WARNING' | 'EMERGENCY_EVACUATION';
  landslide_probability: number;
  spatial_susceptibility: number;
  rainfall_24h_mm: number;
  rainfall_7d_antecedent_mm: number;
  soil_saturation_pct: number;
  action_required: string;
  start_coord: [number, number];
  end_coord: [number, number];
}

export interface BackendCorridorResponse {
  corridor_id: string;
  corridor_name: string;
  timestamp: string;
  high_hazard_segments_count: number;
  evacuation_recommended: boolean;
  segments: BackendCorridorSegment[];
}

export interface ReplayStep {
  step_index: number;
  relative_time: string;
  simulated_timestamp: string;
  display_time: string;
  rainfall_24h_mm: number;
  rainfall_7d_antecedent_mm: number;
  smap_soil_saturation_pct: number;
  operational_advisory: string;
}

export interface ReplayTimelineResponse {
  event: string;
  total_steps: number;
  steps: ReplayStep[];
}

export interface EvacuationRouteResponse {
  status: string;
  provider: string;
  bhuvan_token_active: boolean;
  token_masked?: string;
  route_summary: {
    origin: { lat: number; lon: number };
    destination: { lat: number; lon: number };
    total_distance_km: number;
    estimated_time_minutes: number;
    average_speed_kmh: number;
    avoided_hazard_zones: number;
    evacuation_status: string;
  };
  geojson: {
    type: 'Feature';
    geometry: {
      type: 'LineString';
      coordinates: [number, number][];
    };
    properties: {
      name: string;
      terrain: string;
      hazard_clearance: boolean;
    };
  };
  turn_by_turn_instructions: string[];
}

export interface PredictionResult {
  status: string;
  lead_time_window: string;
  risk_probability: number;
  alert_status: 'NORMAL' | 'WATCH' | 'WARNING' | 'EMERGENCY_EVACUATION';
  top_shap_factors: {
    feature: string;
    value: number;
    shap_attribution: number;
    effect: 'INCREASED RISK' | 'DECREASED RISK';
  }[];
  latency_ms: number;
}

export interface SystemHealth {
  status: string;
  timestamp: number;
  model_cache: {
    spatial_pytorch_loaded: boolean;
    temporal_xgboost_loaded: boolean;
    shap_explainer_ready: boolean;
    cache_duration_seconds: number;
  };
  database: {
    mongodb_connected: boolean;
    geospatial_2dsphere_ready: boolean;
  };
  task_queue: {
    broker: string;
    celery_enabled: boolean;
    async_off_thread: boolean;
  };
}

class ApiService {
  /**
   * Fetches real-time status of all 10 NH-37 highway segments.
   */
  async getCorridors(): Promise<BackendCorridorResponse> {
    const res = await fetch(`${API_BASE}/corridors`);
    if (!res.ok) throw new Error(`Failed to fetch corridors: ${res.statusText}`);
    return res.json();
  }

  /**
   * Fetches lightweight Delta-Only GeoJSON for high-risk highway segments.
   */
  async getCorridorDelta(): Promise<any> {
    const res = await fetch(`${API_BASE}/corridors/delta`);
    if (!res.ok) throw new Error(`Failed to fetch delta GeoJSON: ${res.statusText}`);
    return res.json();
  }

  /**
   * Fetches 2022 historic Tupul disaster replay timeline steps.
   */
  async getReplayTimeline(): Promise<ReplayTimelineResponse> {
    const res = await fetch(`${API_BASE}/replay/timeline`);
    if (!res.ok) throw new Error(`Failed to fetch replay timeline: ${res.statusText}`);
    return res.json();
  }

  /**
   * Executes a step in the 2022 historic replay demo, updating live corridor risks.
   */
  async applyReplayStep(stepIndex: number): Promise<any> {
    const res = await fetch(`${API_BASE}/replay/step?step_index=${stepIndex}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Failed to execute replay step ${stepIndex}: ${res.statusText}`);
    return res.json();
  }

  /**
   * Requests real ISRO Bhuvan emergency routing avoiding high-risk landslide zones.
   */
  async getEvacuationRoute(
    originLat: number = 24.77,
    originLon: number = 93.68,
    destLat: number = 24.81,
    destLon: number = 93.94,
    avoidLandslides: boolean = true
  ): Promise<EvacuationRouteResponse> {
    const res = await fetch(`${API_BASE}/routing/evacuation-route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        origin_lat: originLat,
        origin_lon: originLon,
        dest_lat: destLat,
        dest_lon: destLon,
        avoid_landslide_corridors: avoidLandslides,
      }),
    });
    if (!res.ok) throw new Error(`Failed to compute evacuation route: ${res.statusText}`);
    return res.json();
  }

  /**
   * Submits a citizen photo crack / slope movement report to MongoDB.
   */
  async submitCitizenReport(formData: FormData): Promise<any> {
    const res = await fetch(`${API_BASE}/citizen-reports/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Failed to submit citizen report: ${res.statusText}`);
    return res.json();
  }

  /**
   * Ingests a batch of offline reports with timestamp ordering.
   */
  async syncOfflineBatch(reports: any[]): Promise<any> {
    const res = await fetch(`${API_BASE}/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reports }),
    });
    if (!res.ok) throw new Error(`Failed to sync offline batch: ${res.statusText}`);
    return res.json();
  }

  /**
   * Fetches ingested citizen crack reports from MongoDB.
   */
  async getCitizenReports(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/sync/reports`);
    if (!res.ok) throw new Error(`Failed to fetch citizen reports: ${res.statusText}`);
    const data = await res.json();
    return data.reports || [];
  }

  /**
   * Runs live multi-sensor XGBoost inference with PyTorch baseline and SHAP attributions.
   */
  async predictRisk(params: {
    spatial_susceptibility: number;
    rainfall_24h_mm: number;
    rainfall_7d_antecedent_mm: number;
    smap_surface_sm: number;
    smap_rootzone_sm: number;
  }): Promise<PredictionResult> {
    const res = await fetch(`${API_BASE}/inference/predict-sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`Failed to run AI inference: ${res.statusText}`);
    return res.json();
  }

  /**
   * Fetches live system health and model cache status.
   */
  async getHealth(): Promise<SystemHealth> {
    const res = await fetch('/health');
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  }
}

export const api = new ApiService();
