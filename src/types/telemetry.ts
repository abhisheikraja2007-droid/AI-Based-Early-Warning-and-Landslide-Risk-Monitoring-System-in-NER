export type ThreatLevel = 'STAGE-1 NORMAL' | 'STAGE-2 WATCH' | 'STAGE-3 WARNING' | 'STAGE-4 EVAC';

export interface CorridorSegment {
  id: number;
  name: string;
  kmRange: string;
  startKm: number;
  endKm: number;
  stabilityScore: number; // 0 to 1 (0.02 = critical hazard, 0.98 = safe)
  status: 'safe' | 'watch' | 'critical';
  sectorName: string;
  elevationMsl: number;
  coords: { lat: number; lng: number };
  porePressureKPa: number;
  displacementMmDay: number;
  rainfall7DayMm: number;
  soilMoisturePct: number;
  slopeAngleDeg: number;
  vulnerabilityFactor: number;
  activeHazards?: string[];
  detourAvailable: boolean;
}

export interface TelemetryNode {
  id: string;
  type: 'Piezometer' | 'InSAR Reflector' | 'Doppler Rain Gauge' | 'Tiltmeter' | 'SMAP Soil Probe' | 'Seismic Geophone';
  location: string;
  kmMarker: number;
  sector: string;
  status: 'active' | 'warning' | 'alert' | 'offline';
  batteryPct: number;
  lastReading: string;
  value: number;
  unit: string;
  threshold: number;
  trend: 'rising' | 'steady' | 'dropping';
  readingsHistory: number[];
}

export interface ShapFactor {
  id: string;
  name: string;
  value: string;
  contribution: number; // 0 to 100 for bar display
  impact: '+2.91 (Severe)' | '+1.84 (High)' | '+0.62 (Elevated)' | '+0.38 (Positive)' | string;
  color: 'secondary' | 'tertiary' | 'primary';
  description: string;
}

export interface EvacuationRoute {
  id: string;
  name: string;
  type: 'blocked' | 'safe_detour' | 'high_ridge_alt';
  distanceKm: number;
  transitMins: number;
  hazardsAvoided: number;
  status: 'CLEAR' | 'IMPASSABLE' | 'RESTRICTED';
  origin: string;
  destination: string;
  elevationGainM: number;
  shelterCapacity: number;
  shelterOccupied: number;
  routeHighlights: string[];
}

export interface IncidentReport {
  id: string;
  timestamp: string;
  type: string;
  sector: string;
  kmMarker: number;
  status: 'VERIFIED_ACTIVE' | 'DISPATCHED' | 'MONITORING' | 'RESOLVED';
  reportedBy: string;
  notes: string;
  coords: string;
  imageUrl?: string;
  offlineSynced?: boolean;
}

export interface SarUnit {
  id: string;
  name: string;
  type: 'NDRF Battalion' | 'SDRF Quick Response' | 'BRO Task Force' | 'Heavy Excavator Crew' | 'Drone Recon Unit';
  currentLocation: string;
  assignedSector: string;
  personnelCount: number;
  status: 'On-Site Operational' | 'En Route' | 'Staged / Ready' | 'Assisting Evacuation';
  contactFrequency: string;
}
