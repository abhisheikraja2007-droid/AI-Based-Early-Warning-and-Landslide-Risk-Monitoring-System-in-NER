import React, { useState, useEffect } from 'react';
import { CorridorSegment, ShapFactor } from '../types/telemetry';
import {
  INITIAL_SEGMENTS,
  INITIAL_SHAP_FACTORS,
  HISTORICAL_SCRUBBER_STEPS,
} from '../data/mockTelemetry';
import { soundFx } from '../utils/audioAlert';
import { api } from '../services/api';

interface CorridorMapModuleProps {
  onOpenReportModal: () => void;
  onNavigateToDetour: () => void;
  onBroadcastSMS: () => void;
  onSelectSegment: (segment: CorridorSegment) => void;
}

export const CorridorMapModule: React.FC<CorridorMapModuleProps> = ({
  onOpenReportModal,
  onNavigateToDetour,
  onBroadcastSMS,
  onSelectSegment,
}) => {
  // Scrubber State
  const [currentStepIndex, setCurrentStepIndex] = useState(3); // default T-12h Critical
  const [isPlayingScrubber, setIsPlayingScrubber] = useState(false);
  const [liveSegments, setLiveSegments] = useState<CorridorSegment[]>(INITIAL_SEGMENTS);

  // Map layer toggles
  const [showPytorchHeatmap, setShowPytorchHeatmap] = useState(true);
  const [showRainfallRadar, setShowRainfallRadar] = useState(true);
  const [showSmapMoisture, setShowSmapMoisture] = useState(true);
  const [showShelters, setShowShelters] = useState(true);
  const [mapViewMode, setMapViewMode] = useState<'satellite' | 'contour' | 'hybrid'>('hybrid');
  const [is3DTilted, setIs3DTilted] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Selected Segment
  const [selectedSegmentId, setSelectedSegmentId] = useState<number>(4); // default Tupul Km 39-46

  // Fetch initial real-time corridors from FastAPI backend
  useEffect(() => {
    const fetchInitialCorridors = async () => {
      try {
        const res = await api.getCorridors();
        if (res && res.segments && res.segments.length > 0) {
          const mapped = res.segments.map((bs, idx) => ({
            id: idx + 1,
            name: `${bs.segment_id}: ${bs.location_name}`,
            kmRange: bs.chainage_km.replace('Km ', '').replace(' - Km ', '–'),
            startKm: idx * 12,
            endKm: (idx + 1) * 12,
            stabilityScore: Math.round((1 - bs.landslide_probability) * 100) / 100,
            status: bs.current_hazard_level === 'EMERGENCY_EVACUATION' ? 'critical' : bs.current_hazard_level === 'WARNING' || bs.current_hazard_level === 'WATCH' ? 'watch' : 'safe',
            sectorName: bs.location_name,
            elevationMsl: 780 + idx * 25,
            coords: { lat: bs.latitude, lng: bs.longitude },
            porePressureKPa: Math.round(bs.soil_saturation_pct * 1.2 * 10) / 10,
            displacementMmDay: bs.landslide_probability > 0.7 ? 3.2 : bs.landslide_probability > 0.4 ? 1.2 : 0.2,
            rainfall7DayMm: bs.rainfall_7d_antecedent_mm,
            soilMoisturePct: bs.soil_saturation_pct,
            slopeAngleDeg: bs.base_slope_deg,
            vulnerabilityFactor: bs.spatial_susceptibility,
            detourAvailable: true,
            activeHazards: bs.action_required ? [bs.action_required] : undefined,
          }));
          setLiveSegments(mapped as CorridorSegment[]);
        }
      } catch (err) {
        console.warn('Backend corridors load failed, using local baseline:', err);
      }
    };
    fetchInitialCorridors();
  }, []);

  // Active step data
  const step = HISTORICAL_SCRUBBER_STEPS[currentStepIndex];

  // Auto-play scrubber effect
  useEffect(() => {
    let timer: number;
    if (isPlayingScrubber) {
      timer = window.setInterval(() => {
        handleSelectStep((currentStepIndex + 1) % HISTORICAL_SCRUBBER_STEPS.length);
        soundFx.playRadarPing();
      }, 3500);
    }
    return () => clearInterval(timer);
  }, [isPlayingScrubber, currentStepIndex]);

  // Handle scrubber step change with live backend replay execution
  const handleSelectStep = async (index: number) => {
    setCurrentStepIndex(index);
    soundFx.playRadarPing();
    try {
      const replayRes = await api.applyReplayStep(index);
      if (replayRes && replayRes.corridor_status && replayRes.corridor_status.segments) {
        const updated = replayRes.corridor_status.segments.map((bs: any, idx: number) => ({
          id: idx + 1,
          name: `${bs.segment_id}: ${bs.location_name}`,
          kmRange: bs.chainage_km.replace('Km ', '').replace(' - Km ', '–'),
          startKm: idx * 12,
          endKm: (idx + 1) * 12,
          stabilityScore: Math.round((1 - bs.landslide_probability) * 100) / 100,
          status: bs.current_hazard_level === 'EMERGENCY_EVACUATION' ? 'critical' : bs.current_hazard_level === 'WARNING' || bs.current_hazard_level === 'WATCH' ? 'watch' : 'safe',
          sectorName: bs.location_name,
          elevationMsl: 780 + idx * 25,
          coords: { lat: bs.latitude, lng: bs.longitude },
          porePressureKPa: Math.round(bs.soil_saturation_pct * 1.2 * 10) / 10,
          displacementMmDay: bs.landslide_probability > 0.7 ? 3.2 : bs.landslide_probability > 0.4 ? 1.2 : 0.2,
          rainfall7DayMm: bs.rainfall_7d_antecedent_mm,
          soilMoisturePct: bs.soil_saturation_pct,
          slopeAngleDeg: bs.base_slope_deg,
          vulnerabilityFactor: bs.spatial_susceptibility,
          detourAvailable: true,
          activeHazards: bs.action_required ? [bs.action_required] : undefined,
        }));
        setLiveSegments(updated as CorridorSegment[]);
      }
    } catch (err) {
      console.warn('Replay step execution error:', err);
    }
  };

  // Dynamic segments based on live backend data and historical step
  const segments: CorridorSegment[] = liveSegments.map((s) => {
    if (s.id === 4) {
      return {
        ...s,
        stabilityScore: step.sector4Score,
        status: step.sector4Score < 0.3 ? 'critical' : step.sector4Score < 0.7 ? 'watch' : 'safe',
      };
    }
    return s;
  });

  const selectedSegment = segments.find((s) => s.id === selectedSegmentId) || segments[3];


  // Dynamic SHAP values based on current historical step
  const shapFactors: ShapFactor[] = [
    {
      ...INITIAL_SHAP_FACTORS[0],
      value: `+${step.shapSevere.toFixed(2)}`,
      impact: `+${step.shapSevere.toFixed(2)} (${step.shapSevere > 2.0 ? 'Severe' : step.shapSevere > 1.0 ? 'High' : 'Elevated'})`,
      contribution: Math.min(100, Math.round(step.shapSevere * 33)),
    },
    {
      ...INITIAL_SHAP_FACTORS[1],
      value: `+${step.shapHigh.toFixed(2)}`,
      impact: `+${step.shapHigh.toFixed(2)} (${step.shapHigh > 1.5 ? 'High' : 'Elevated'})`,
      contribution: Math.min(100, Math.round(step.shapHigh * 42)),
    },
    {
      ...INITIAL_SHAP_FACTORS[2],
      value: `+${step.shapElevated.toFixed(2)}`,
      impact: `+${step.shapElevated.toFixed(2)} (Elevated)`,
      contribution: Math.min(100, Math.round(step.shapElevated * 75)),
    },
    {
      ...INITIAL_SHAP_FACTORS[3],
      value: `+${step.shapPositive.toFixed(2)}`,
      impact: `+${step.shapPositive.toFixed(2)} (Positive)`,
      contribution: Math.min(100, Math.round(step.shapPositive * 85)),
    },
  ];

  // Circle circumference for radial gauge: r=42 -> C = 2 * PI * 42 ≈ 263.89
  const circumference = 2 * Math.PI * 42;
  const strokeDashoffset = circumference - (step.failProb / 100) * circumference;

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* 1. TOP TELEMETRY STATUS RIBBON */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {/* Monitored Corridor */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // MONITORED_CORRIDOR
          </span>
          <div className="flex items-baseline gap-1.5 mt-0.5">
            <span className="font-headline text-lg text-[#dae2fc] font-bold">NH-37</span>
            <span className="font-mono text-xs text-[#4cd7f6]">Km 0–110.4</span>
          </div>
        </div>

        {/* Threat Level */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // THREAT_LEVEL
          </span>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span
              className={`inline-block w-2.5 h-2.5 rounded-full ${
                step.threatLevel === 'STAGE-4 EVAC'
                  ? 'bg-[#ef4444] animate-ping'
                  : step.threatLevel === 'STAGE-3 WARNING'
                  ? 'bg-[#ffb95f] animate-pulse'
                  : 'bg-[#10b981]'
              }`}
            />
            <span
              className={`font-headline text-sm lg:text-base font-bold tracking-tight ${
                step.threatLevel === 'STAGE-4 EVAC'
                  ? 'text-[#ffb3ad]'
                  : step.threatLevel === 'STAGE-3 WARNING'
                  ? 'text-[#ffb95f]'
                  : 'text-[#10b981]'
              }`}
            >
              {step.threatLevel}
            </span>
          </div>
        </div>

        {/* Telemetry Nodes */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // TELEMETRY_NODES
          </span>
          <div className="flex items-baseline justify-between mt-0.5">
            <span className="font-headline text-lg text-[#4cd7f6] font-bold">
              142<span className="text-[#bcc9cd] font-mono text-xs">/144</span>
            </span>
            <span className="font-mono text-[10px] text-[#4cd7f6] uppercase font-semibold">
              98.6% UP
            </span>
          </div>
        </div>

        {/* Radar Precip Peak */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // RADAR_PRECIP_PEAK
          </span>
          <div className="flex items-baseline justify-between mt-0.5">
            <span className="font-headline text-lg text-[#ffb95f] font-bold">
              {step.radarPrecip}{' '}
              <span className="font-mono text-[11px] font-normal text-[#bcc9cd]">mm/h</span>
            </span>
            <span className="font-mono text-[10px] text-[#ef4444] font-bold">SURGE</span>
          </div>
        </div>

        {/* Rootzone Saturation */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // ROOTZONE_SATURATION
          </span>
          <div className="flex items-baseline justify-between mt-0.5">
            <span className="font-headline text-lg text-[#ffb95f] font-bold">
              {step.rootzoneMoisture}%
            </span>
            <span className="font-mono text-[10px] text-[#869397]">SMAP L4</span>
          </div>
        </div>

        {/* System Mode */}
        <div className="bg-[#131b2e] px-4 py-2.5 rounded border border-[#222a3d] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
            // SYSTEM_MODE
          </span>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className="inline-block w-2 h-2 rounded-full bg-[#4cd7f6] animate-pulse" />
            <span className="font-mono text-xs text-[#dae2fc] font-bold tracking-tight">
              AUTONOMOUS DISPATCH
            </span>
          </div>
        </div>
      </div>

      {/* 2. MAIN OPERATIONS VIEWPORT (SPLIT 68% MAP / 32% INSIGHTS) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* LEFT: CARTOGRAPHIC TELEMETRY HUD (col-span-8) */}
        <div className="xl:col-span-8 flex flex-col gap-3">
          {/* MAP CANVAS CONTAINER */}
          <div
            className={`relative w-full h-[620px] bg-[#060e20] rounded-xl overflow-hidden border border-[#222a3d] shadow-2xl flex flex-col transition-all duration-300 ${
              is3DTilted ? 'perspective-[1000px]' : ''
            }`}
          >
            {/* SATELLITE TERRAIN BACKDROP (from the user image asset / mockup) */}
            <div
              className={`absolute inset-0 bg-cover bg-center transition-all duration-500 ${
                mapViewMode === 'satellite'
                  ? 'opacity-85 mix-blend-normal'
                  : mapViewMode === 'contour'
                  ? 'opacity-20 mix-blend-luminosity'
                  : 'opacity-45 mix-blend-luminosity'
              }`}
              style={{
                backgroundImage:
                  "url('https://lh3.googleusercontent.com/aida-public/AB6AXuCtuIWvQbkv-lvjk7N7aYaAznlj-Kb02p-R53_ucKh4IZZ6cJz_ZYVJIYDZz2ztOZ1PpnUuj0_-as2qXyJMOQ-33bc5IT8dZNt_z6EbRfcRUw-_tPotxpGq5yVMFRsZdYmF3HndEWzdTyZMBZESjRWgA5Rc_Z3OLh015gCWjni-BjURkuqDOkgxryJcvhR2N9XT-A2KKJlTWIK-oSGcGcvhyw86eJwBTMhjFjKz4Yx4GYo8ZO233hUj')",
                transform: `scale(${zoomLevel}) ${is3DTilted ? 'rotateX(22deg) scale(1.08)' : ''}`,
                transformOrigin: 'center center',
              }}
            />

            {/* TOP FLOATING HUD: TELEMETRY QUICKSTATS + LAYER TOGGLES */}
            <div className="relative z-20 p-3 sm:p-4 flex flex-wrap items-start justify-between gap-2 bg-gradient-to-b from-[#060e20]/95 via-[#060e20]/60 to-transparent">
              {/* TOP-LEFT STATUS BADGES */}
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2 bg-[#171f32]/90 backdrop-blur-md px-2.5 py-1 rounded border border-[#ef4444]/40 shadow-md">
                  <span className="material-symbols-outlined text-[16px] text-[#ef4444]">
                    warning
                  </span>
                  <span className="font-mono text-xs text-[#ffb3ad] font-bold tracking-wider uppercase">
                    {step.activeHazardText}
                  </span>
                  <span className="font-mono text-xs text-[#bcc9cd] hidden sm:inline">
                    | SECTOR 4-TUPUL
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-1.5 font-mono text-[11px] text-[#bcc9cd] px-1">
                  <span>COORD: 24°51'18"N, 93°41'52"E</span>
                  <span>•</span>
                  <span className="text-[#4cd7f6]">ALT 820m MSL</span>
                  <span>•</span>
                  <span className="text-[#ffb95f]">IMD Doppler: Impending Inflow</span>
                </div>
              </div>

              {/* TOP-RIGHT LAYER SWITCHER PILLS */}
              <div className="flex flex-wrap items-center gap-1.5 bg-[#060e20]/80 backdrop-blur-md p-1 rounded border border-[#222a3d]">
                <button
                  type="button"
                  onClick={() => setShowPytorchHeatmap(!showPytorchHeatmap)}
                  className={`px-2 py-1 font-mono text-xs rounded flex items-center gap-1 transition-colors ${
                    showPytorchHeatmap
                      ? 'bg-[#222a3d] text-[#4cd7f6] font-semibold border border-[#4cd7f6]/40'
                      : 'bg-transparent text-[#869397] hover:text-[#bcc9cd]'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {showPytorchHeatmap ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span>PyTorch Heatmap</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowRainfallRadar(!showRainfallRadar)}
                  className={`px-2 py-1 font-mono text-xs rounded flex items-center gap-1 transition-colors ${
                    showRainfallRadar
                      ? 'bg-[#222a3d] text-[#4cd7f6] font-semibold border border-[#4cd7f6]/40'
                      : 'bg-transparent text-[#869397] hover:text-[#bcc9cd]'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {showRainfallRadar ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span>24h Rainfall Radar</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowSmapMoisture(!showSmapMoisture)}
                  className={`px-2 py-1 font-mono text-xs rounded flex items-center gap-1 transition-colors ${
                    showSmapMoisture
                      ? 'bg-[#222a3d] text-[#dae2fc] font-semibold border border-[#869397]/40'
                      : 'bg-transparent text-[#869397] hover:text-[#bcc9cd]'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">water_drop</span>
                  <span>SMAP Moisture ({step.rootzoneMoisture}%)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowShelters(!showShelters)}
                  className={`px-2 py-1 font-mono text-xs rounded flex items-center gap-1 font-bold shadow-sm transition-colors ${
                    showShelters
                      ? 'bg-[#4cd7f6] text-[#003640]'
                      : 'bg-[#222a3d] text-[#869397]'
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">shield</span>
                  <span>Shelters (Active)</span>
                </button>
              </div>
            </div>

            {/* INTERACTIVE VECTOR MAP GRAPHICS (SVG Topo & Hazard Overlay) */}
            <div
              className={`relative z-10 flex-1 w-full h-full pointer-events-auto transition-transform duration-300 ${
                is3DTilted ? 'scale-105' : ''
              }`}
            >
              <svg
                className="w-full h-full cursor-crosshair select-none"
                preserveAspectRatio="none"
                viewBox="0 0 900 520"
              >
                <defs>
                  {/* Radar scanning grid pattern */}
                  <pattern id="tacGrid" patternUnits="userSpaceOnUse" width="40" height="40">
                    <path
                      d="M 40 0 L 0 0 0 40"
                      fill="none"
                      stroke="#3d494c"
                      strokeWidth="0.5"
                      strokeOpacity="0.4"
                    />
                  </pattern>

                  {/* Glow Filters */}
                  <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  <filter id="glowAmber" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                </defs>

                {/* Radar Mesh Grid Layer */}
                <rect width="100%" height="100%" fill="url(#tacGrid)" opacity="0.35" />

                {/* Elevation Contour Lines (Topographic HUD) */}
                <g fill="none" stroke="#4cd7f6" strokeWidth="0.8" strokeOpacity="0.22">
                  <path d="M 50 180 Q 200 130 350 190 T 700 140 T 900 190" />
                  <path d="M 30 220 Q 220 180 400 240 T 730 200 T 900 230" />
                  <path d="M 70 270 Q 240 230 450 300 T 780 250 T 900 290" />
                  <path d="M 40 330 Q 260 290 490 350 T 800 310 T 900 340" />
                  <path d="M 80 400 Q 290 360 520 420 T 840 380 T 900 410" />
                </g>

                {/* River / Drainage Course (Cyan Translucent) */}
                <path
                  d="M 60 480 Q 220 420 380 470 T 700 410 T 880 460"
                  fill="none"
                  stroke="#4cd7f6"
                  strokeOpacity="0.45"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                />
                <text
                  x="710"
                  y="405"
                  className="fill-[#4cd7f6]/70 font-mono text-[10px] tracking-wide"
                >
                  Ije River Basin (Saturated)
                </text>

                {/* PyTorch Heatmap Density Clouds */}
                {showPytorchHeatmap && step.sector4Score < 0.5 && (
                  <g opacity="0.4">
                    <ellipse cx="375" cy="272" rx="90" ry="50" fill="#ef4444" filter="url(#glowRed)" />
                    <ellipse cx="460" cy="210" rx="55" ry="35" fill="#f59e0b" filter="url(#glowAmber)" />
                  </g>
                )}

                {/* 24h Rainfall Radar Precipitation Overlay */}
                {showRainfallRadar && (
                  <g opacity="0.25">
                    <circle cx="370" cy="270" r="140" fill="#06b6d4" filter="url(#glowCyan)" />
                    <circle cx="500" cy="220" r="90" fill="#06b6d4" />
                  </g>
                )}

                {/* NH-37 CORRIDOR ROAD VECTOR WITH 10 SEGMENTED SPANS */}
                {/* Segment 1: Km 0-15 (Green) */}
                <path
                  d="M 80 440 L 140 400"
                  fill="none"
                  stroke="#10b981"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#34d399] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(1);
                    onSelectSegment(segments[0]);
                  }}
                />

                {/* Segment 2: Km 16-28 (Green) */}
                <path
                  d="M 140 400 L 220 360"
                  fill="none"
                  stroke="#10b981"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#34d399] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(2);
                    onSelectSegment(segments[1]);
                  }}
                />

                {/* Segment 3: Km 29-38 (Yellow Watch) */}
                <path
                  d="M 220 360 L 320 305"
                  fill="none"
                  stroke="#f59e0b"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#fbbf24] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(3);
                    onSelectSegment(segments[2]);
                  }}
                />

                {/* Segment 4: Km 39-46 (CRITICAL RED HAZARD FLASH ZONE) */}
                <path
                  d="M 320 305 L 430 240"
                  fill="none"
                  stroke={step.sector4Score < 0.3 ? '#ef4444' : step.sector4Score < 0.7 ? '#f59e0b' : '#10b981'}
                  strokeLinecap="round"
                  strokeWidth="9"
                  filter={step.sector4Score < 0.5 ? 'url(#glowRed)' : undefined}
                  className={`cursor-pointer transition-all ${
                    step.sector4Score < 0.3 ? 'animate-pulse hover:stroke-[#f87171]' : ''
                  }`}
                  onClick={() => {
                    setSelectedSegmentId(4);
                    onSelectSegment(segments[3]);
                  }}
                />

                {/* Segment 5: Km 47-58 (Yellow Restricted) */}
                <path
                  d="M 430 240 L 530 190"
                  fill="none"
                  stroke="#f59e0b"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#fbbf24] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(5);
                    onSelectSegment(segments[4]);
                  }}
                />

                {/* Segments 6-10: Km 59-110 (Green Clear Corridors) */}
                <path
                  d="M 530 190 L 630 145"
                  fill="none"
                  stroke="#10b981"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#34d399] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(6);
                    onSelectSegment(segments[5]);
                  }}
                />
                <path
                  d="M 630 145 L 720 110"
                  fill="none"
                  stroke="#10b981"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#34d399] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(7);
                    onSelectSegment(segments[6]);
                  }}
                />
                <path
                  d="M 720 110 L 820 70"
                  fill="none"
                  stroke="#10b981"
                  strokeLinecap="round"
                  strokeWidth="7"
                  className="hover:stroke-[#34d399] cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedSegmentId(8);
                    onSelectSegment(segments[7]);
                  }}
                />

                {/* RUNOUT DEBRIS CORRIDOR ENVELOPE (Shaded Threat Polygonal Zone) */}
                {step.sector4Score < 0.5 && (
                  <>
                    <polygon
                      points="310,290 410,210 470,250 350,330"
                      fill="#a40217"
                      fillOpacity="0.35"
                    />
                    <polygon
                      points="325,300 400,225 445,255 355,320"
                      fill="#ef4444"
                      fillOpacity="0.25"
                      className="animate-pulse"
                    />
                  </>
                )}

                {/* PULSATING RADAR BEACON AT KM 42 (TUPUL RAILWAY DISASTER SECTOR) */}
                {step.sector4Score < 0.5 ? (
                  <g className="cursor-pointer" onClick={() => setSelectedSegmentId(4)}>
                    <circle
                      cx="375"
                      cy="272"
                      r="32"
                      fill="none"
                      stroke="#ef4444"
                      strokeWidth="1.2"
                      className="animate-ping"
                      opacity="0.75"
                    />
                    <circle cx="375" cy="272" r="20" fill="none" stroke="#ef4444" strokeWidth="1.5" />
                    <circle cx="375" cy="272" r="8" fill="#ef4444" className="animate-pulse" />
                  </g>
                ) : (
                  <circle cx="375" cy="272" r="6" fill="#10b981" />
                )}

                {/* EVACUATION BYPASS ROUTE (ISRO Bhuvan Safe Passage Route - Dashed Glowing Cyan) */}
                <path
                  d="M 300 320 C 330 380, 420 360, 460 300 S 520 230, 540 180"
                  fill="none"
                  stroke="#4cd7f6"
                  strokeWidth="4"
                  strokeDasharray="8 6"
                  filter="url(#glowCyan)"
                  className="cursor-pointer hover:stroke-[#a5f3fc] transition-colors"
                  onClick={onNavigateToDetour}
                />

                {/* DESTINATION EVACUATION SHELTER MARKER */}
                {showShelters && (
                  <g
                    transform="translate(540, 180)"
                    className="cursor-pointer hover:scale-110 transition-transform"
                    onClick={onNavigateToDetour}
                  >
                    <circle cx="0" cy="0" r="14" fill="#06b6d4" />
                    <circle cx="0" cy="0" r="6" fill="#0b1326" />
                    {/* Tooltip Badge on Map */}
                    <rect
                      x="-85"
                      y="-38"
                      width="170"
                      height="26"
                      rx="4"
                      fill="#0b1326"
                      stroke="#4cd7f6"
                      strokeWidth="1.2"
                    />
                    <text
                      x="0"
                      y="-21"
                      textAnchor="middle"
                      className="font-mono text-[11px] font-bold fill-[#dae2fc]"
                    >
                      NONEY RELIEF CENTER
                    </text>
                  </g>
                )}

                {/* MILEPOST & LOCATION LABELS */}
                <g className="font-mono text-[10px] fill-[#dae2fc]">
                  {/* Km 0 Marker */}
                  <circle cx="80" cy="440" r="4.5" fill="#10b981" />
                  <text x="80" y="460" textAnchor="middle">
                    Km 0 (Imphal West)
                  </text>

                  {/* Km 42 Hazard Warning Label */}
                  {step.sector4Score < 0.5 && (
                    <g
                      className="cursor-pointer"
                      onClick={() => {
                        setSelectedSegmentId(4);
                        onSelectSegment(segments[3]);
                      }}
                    >
                      <rect
                        x="250"
                        y="210"
                        width="220"
                        height="44"
                        rx="4"
                        fill="#222a3d"
                        stroke="#a40217"
                        strokeWidth="1.5"
                      />
                      <text x="260" y="228" className="font-bold text-[11px] fill-[#ffb3ad]">
                        KM 42: TUPUL RAILWAY YARD
                      </text>
                      <text x="260" y="244" className="text-[10px] fill-[#ffdad6] font-semibold">
                        SLOPE FAILURE PROBABILITY: {step.failProb > 50 ? '98.4%' : `${step.failProb}%`}
                      </text>
                    </g>
                  )}

                  {/* Km 110 Jiribam End Point */}
                  <circle cx="820" cy="70" r="4.5" fill="#10b981" />
                  <text x="800" y="55" textAnchor="middle">
                    Km 110 (Jiribam)
                  </text>
                </g>

                {/* Safe Passage Label on Detour */}
                <g className="cursor-pointer" onClick={onNavigateToDetour}>
                  <rect
                    x="360"
                    y="365"
                    width="190"
                    height="22"
                    rx="3"
                    fill="#131b2e"
                    stroke="#4cd7f6"
                    strokeWidth="0.8"
                  />
                  <text
                    x="455"
                    y="380"
                    textAnchor="middle"
                    className="font-mono text-[10px] font-bold fill-[#4cd7f6]"
                  >
                    ISRO BHUVAN SAFE DETOUR (35.9 KM)
                  </text>
                </g>
              </svg>
            </div>

            {/* BOTTOM HUD OVERLAYS (LEGEND + CONTROLS) */}
            <div className="relative z-20 p-3 sm:p-4 flex items-end justify-between gap-3 pointer-events-none">
              {/* BOTTOM-LEFT GEOSPATIAL MAP LEGEND */}
              <div className="pointer-events-auto bg-[#131b2e]/95 backdrop-blur-md p-3 rounded border border-[#222a3d] shadow-lg flex flex-col gap-1.5 w-56 sm:w-64">
                <span className="font-mono text-[10px] text-[#869397] uppercase tracking-wider font-semibold">
                  HUD MAP CLASSIFICATION
                </span>
                <div className="flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#a40217]" />
                    <span className="text-[#dae2fc]">Critical Hazard</span>
                  </div>
                  <span className="text-[#ffb3ad] font-bold">&gt;85%</span>
                </div>
                <div className="flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#e79400]" />
                    <span className="text-[#dae2fc]">Watch / Elevated</span>
                  </div>
                  <span className="text-[#ffb95f] font-bold">50–85%</span>
                </div>
                <div className="flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-[#10b981]" />
                    <span className="text-[#dae2fc]">Normal Baseline</span>
                  </div>
                  <span className="text-[#4cd7f6] font-bold">&lt;50%</span>
                </div>
                <div className="flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-1 bg-[#4cd7f6]" />
                    <span className="text-[#4cd7f6]">Safe Evac Vector</span>
                  </div>
                  <span className="text-[#4cd7f6] font-bold">BHUVAN</span>
                </div>
              </div>

              {/* BOTTOM-RIGHT INTERACTIVE CONTROLS */}
              <div className="pointer-events-auto flex items-center gap-1.5 bg-[#131b2e]/90 backdrop-blur-md p-1.5 rounded border border-[#222a3d] shadow-lg">
                <button
                  type="button"
                  onClick={() => setZoomLevel((z) => Math.min(1.6, z + 0.15))}
                  className="w-8 h-8 rounded bg-[#222a3d] hover:bg-[#31394d] flex items-center justify-center text-[#dae2fc] transition-colors"
                  title="Zoom In"
                >
                  <span className="material-symbols-outlined text-[18px]">add</span>
                </button>
                <button
                  type="button"
                  onClick={() => setZoomLevel((z) => Math.max(0.85, z - 0.15))}
                  className="w-8 h-8 rounded bg-[#222a3d] hover:bg-[#31394d] flex items-center justify-center text-[#dae2fc] transition-colors"
                  title="Zoom Out"
                >
                  <span className="material-symbols-outlined text-[18px]">remove</span>
                </button>
                <button
                  type="button"
                  onClick={() => setIs3DTilted(!is3DTilted)}
                  className={`px-2.5 h-8 rounded flex items-center gap-1 font-mono text-xs transition-colors ${
                    is3DTilted
                      ? 'bg-[#4cd7f6] text-[#003640] font-bold'
                      : 'bg-[#222a3d] hover:bg-[#31394d] text-[#4cd7f6]'
                  }`}
                  title="3D Terrain Mesh Tilt"
                >
                  <span className="material-symbols-outlined text-[16px]">view_in_ar</span>
                  <span>3D TILT</span>
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setMapViewMode(
                      mapViewMode === 'hybrid'
                        ? 'satellite'
                        : mapViewMode === 'satellite'
                        ? 'contour'
                        : 'hybrid'
                    )
                  }
                  className="px-2 h-8 rounded bg-[#222a3d] hover:bg-[#31394d] flex items-center gap-1 font-mono text-[11px] text-[#bcc9cd]"
                  title="Toggle Satellite vs Topo View"
                >
                  <span className="material-symbols-outlined text-[16px]">layers</span>
                  <span className="uppercase">{mapViewMode}</span>
                </button>
                <div
                  className="w-8 h-8 rounded bg-[#060e20] flex items-center justify-center text-[#4cd7f6]"
                  title="Compass North (Manipur 24°55' N)"
                >
                  <span className="material-symbols-outlined text-[18px]">explore</span>
                </div>
              </div>
            </div>
          </div>

          {/* CORRIDOR SEGMENT STATUS TICKER BAR */}
          <div className="bg-[#131b2e] p-3 rounded border border-[#222a3d] flex flex-col gap-2 shadow-md">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#869397] uppercase tracking-wider font-semibold">
                // NH-37 SEGMENTED SPATIAL CONTINUUM (10 TACTICAL REACHES)
              </span>
              <span className="font-mono text-[11px] text-[#4cd7f6] hidden sm:inline">
                AUTOMATED TELEMETRY SAMPLING RATE: 10 SEC
              </span>
            </div>

            {/* 10 Segmentation Blocks */}
            <div className="grid grid-cols-5 md:grid-cols-10 gap-1.5">
              {segments.map((seg) => {
                const isSelected = seg.id === selectedSegmentId;
                const isCrit = seg.status === 'critical';
                const isWat = seg.status === 'watch';

                return (
                  <button
                    key={seg.id}
                    type="button"
                    onClick={() => {
                      setSelectedSegmentId(seg.id);
                      onSelectSegment(seg);
                    }}
                    className={`p-1.5 rounded flex flex-col items-center transition-all cursor-pointer ${
                      isCrit
                        ? 'bg-[#a40217]/40 border-b-2 border-[#ef4444] animate-pulse'
                        : isWat
                        ? 'bg-[#171f32] border-b-2 border-[#ffb95f]'
                        : 'bg-[#171f32] border-b-2 border-[#10b981]'
                    } ${isSelected ? 'ring-2 ring-[#4cd7f6]' : 'hover:bg-[#222a3d]'}`}
                  >
                    <span
                      className={`font-mono text-[10px] ${
                        isCrit ? 'text-[#ffb3ad] font-bold' : 'text-[#bcc9cd]'
                      }`}
                    >
                      {seg.kmRange}
                    </span>
                    <span
                      className={`font-mono text-xs font-bold ${
                        isCrit ? 'text-[#ffb3ad]' : isWat ? 'text-[#ffb95f]' : 'text-[#10b981]'
                      }`}
                    >
                      {seg.stabilityScore.toFixed(2)}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: ACTION & PREDICTIVE INSIGHTS DRAWER (col-span-4) */}
        <div className="xl:col-span-4 flex flex-col gap-3">
          {/* CARD 1: 6-TO-24H EARLY WARNING RISK GAUGE */}
          <div className="bg-[#131b2e] p-4 rounded-xl flex flex-col gap-3 border border-[#222a3d] shadow-xl relative overflow-hidden">
            <div className="flex items-start justify-between">
              <div className="flex flex-col">
                <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                  // AI RISK PROGNOSIS
                </span>
                <span className="font-headline text-lg sm:text-xl text-[#dae2fc] font-bold">
                  6-to-24h Early Warning
                </span>
              </div>
              <span className="px-2 py-0.5 rounded bg-[#06b6d4] text-[#00424f] font-mono text-[11px] font-bold tracking-wider uppercase">
                12H ADVANCE LEAD
              </span>
            </div>

            {/* RADIAL FAILURE PROBABILITY GAUGE HUD */}
            <div className="flex items-center justify-around py-1">
              <div className="relative w-36 h-36 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    fill="none"
                    stroke="#2d3449"
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    fill="none"
                    stroke={step.failProb > 70 ? '#ef4444' : step.failProb > 40 ? '#ffb95f' : '#10b981'}
                    strokeWidth="8"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    className="transition-all duration-700 ease-out"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span
                    className={`font-headline text-3xl font-extrabold tracking-tighter ${
                      step.failProb > 70
                        ? 'text-[#ffb3ad]'
                        : step.failProb > 40
                        ? 'text-[#ffb95f]'
                        : 'text-[#10b981]'
                    }`}
                  >
                    {step.failProb}%
                  </span>
                  <span className="font-mono text-[10px] text-[#bcc9cd] uppercase">FAIL PROB</span>
                </div>
              </div>

              <div className="flex flex-col gap-1.5 max-w-[155px]">
                <div className="p-2 rounded bg-[#171f32] border border-[#222a3d]">
                  <span className="font-mono text-[9px] text-[#869397] uppercase block font-semibold">
                    Model Architecture
                  </span>
                  <span className="font-mono text-xs text-[#4cd7f6] font-bold">
                    PyTorch GNN Ensemble
                  </span>
                </div>
                <div className="p-2 rounded bg-[#171f32] border border-[#222a3d]">
                  <span className="font-mono text-[9px] text-[#869397] uppercase block font-semibold">
                    Confidence Score
                  </span>
                  <span className="font-mono text-xs text-[#dae2fc] font-bold">
                    99.1% Verified
                  </span>
                </div>
                <div className="p-2 rounded bg-[#a40217]/25 border border-[#ef4444]/30">
                  <span className="font-mono text-[9px] text-[#ffb3ad] uppercase block font-semibold">
                    Strain Dynamic
                  </span>
                  <span className="font-mono text-xs text-[#ffb3ad] font-bold">
                    {step.failProb > 70 ? 'Imminent Rupture' : 'Elastic Creep'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-2.5 bg-[#171f32] rounded border border-[#222a3d] text-xs text-[#bcc9cd] font-body flex items-start gap-2">
              <span className="material-symbols-outlined text-[#ef4444] text-[18px] shrink-0 mt-0.5">
                crisis_alert
              </span>
              <span>
                Shear strain threshold breached along bedding plane fault. Slope liquefaction imminent under continuous rainfall.
              </span>
            </div>
          </div>

          {/* CARD 2: EXPLAINABLE AI / SHAP ATTRIBUTION BREAKDOWN */}
          <div className="bg-[#131b2e] p-4 rounded-xl flex flex-col gap-2.5 border border-[#222a3d] shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // EXPLAINABLE AI (XAI)
              </span>
              <span className="font-mono text-xs text-[#bcc9cd]">SHAP VALUES (φ)</span>
            </div>
            <span className="font-headline text-lg text-[#dae2fc] font-bold">
              Why This Alert Triggered
            </span>

            {/* SHAP Bars Container */}
            <div className="flex flex-col gap-2.5 mt-1">
              {shapFactors.map((factor) => (
                <div key={factor.id} className="flex flex-col gap-1">
                  <div className="flex items-baseline justify-between font-mono text-xs">
                    <span className="text-[#dae2fc] font-medium">{factor.name}</span>
                    <span
                      className={`font-bold ${
                        factor.color === 'secondary'
                          ? 'text-[#ffb3ad]'
                          : factor.color === 'tertiary'
                          ? 'text-[#ffb95f]'
                          : 'text-[#4cd7f6]'
                      }`}
                    >
                      {factor.impact}
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#222a3d] overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        factor.color === 'secondary'
                          ? 'bg-[#a40217]'
                          : factor.color === 'tertiary'
                          ? 'bg-[#e79400]'
                          : 'bg-[#06b6d4]'
                      }`}
                      style={{ width: `${factor.contribution}%` }}
                    />
                  </div>
                  <span className="text-[#869397] font-mono text-[10px]">
                    {factor.description}
                  </span>
                </div>
              ))}
            </div>

            {/* Causal Trigger Plain Language Summary */}
            <div className="p-2.5 bg-[#222a3d] rounded border border-[#2d3449] mt-1">
              <span className="font-mono text-[11px] text-[#4cd7f6] font-bold block mb-0.5">
                // CAUSAL TRIGGER REASON
              </span>
              <p className="font-body text-xs text-[#dae2fc] leading-relaxed">
                {step.causalReason}
              </p>
            </div>
          </div>

          {/* CARD 3: ISRO BHUVAN SAFE EVACUATION PASSAGE */}
          <div className="bg-[#131b2e] p-4 rounded-xl flex flex-col gap-2.5 border border-[#222a3d] shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // BHUVAN CORRIDOR DISPATCH
              </span>
              <span className="material-symbols-outlined text-[#4cd7f6] text-[20px]">
                alt_route
              </span>
            </div>
            <span className="font-headline text-lg text-[#dae2fc] font-bold">
              Safe Evacuation Route
            </span>

            {/* Origin & Destination Flow */}
            <div className="bg-[#171f32] p-2.5 rounded border border-[#222a3d] flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444] shrink-0" />
                <div className="flex flex-col">
                  <span className="font-mono text-[9px] text-[#869397] uppercase">
                    ORIGIN (RED HAZARD ZONE)
                  </span>
                  <span className="font-mono text-xs text-[#dae2fc] font-bold">
                    Tupul Railway Colony / Village
                  </span>
                </div>
              </div>
              <div className="ml-1 w-0.5 h-3 bg-[#4cd7f6]/40" />
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#4cd7f6] shrink-0" />
                <div className="flex flex-col">
                  <span className="font-mono text-[9px] text-[#869397] uppercase">
                    DESTINATION (SHELTER)
                  </span>
                  <span className="font-mono text-xs text-[#4cd7f6] font-bold">
                    Noney Community Health Center
                  </span>
                </div>
              </div>
            </div>

            {/* Route metrics pills */}
            <div className="grid grid-cols-3 gap-1.5 py-1">
              <div className="p-2 bg-[#171f32] text-center rounded border border-[#222a3d]">
                <span className="font-mono text-[10px] text-[#869397] block uppercase">Distance</span>
                <span className="font-mono text-xs text-[#dae2fc] font-bold">35.9 km</span>
              </div>
              <div className="p-2 bg-[#171f32] text-center rounded border border-[#222a3d]">
                <span className="font-mono text-[10px] text-[#869397] block uppercase">Transit</span>
                <span className="font-mono text-xs text-[#4cd7f6] font-bold">61 mins</span>
              </div>
              <div className="p-2 bg-[#171f32] text-center rounded border border-[#222a3d]">
                <span className="font-mono text-[10px] text-[#869397] block uppercase">Hazards Avoided</span>
                <span className="font-mono text-xs text-[#ffb3ad] font-bold">1 Major</span>
              </div>
            </div>

            {/* PRIMARY ACTION BUTTONS */}
            <div className="flex flex-col gap-1.5 mt-1">
              <button
                type="button"
                onClick={onNavigateToDetour}
                className="w-full py-2.5 px-3 rounded bg-[#06b6d4] hover:bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_12px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">navigation</span>
                <span>Start GPS Navigation via Safe Detour</span>
              </button>
              <button
                type="button"
                onClick={onBroadcastSMS}
                className="w-full py-2 px-3 rounded bg-[#222a3d] hover:bg-[#31394d] text-[#dae2fc] font-mono text-xs font-semibold flex items-center justify-center gap-2 border border-[#2d3449] transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[#ffb3ad] text-[16px]">
                  campaign
                </span>
                <span>Broadcast SMS Alert to 4,200 Registered Villagers</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 3. BOTTOM FLOATING ACTION & HISTORICAL SCRUBBER BAR */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* CITIZEN FIELD REPORT ACTION BUTTON (col-span-4) */}
        <div className="lg:col-span-4 bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex items-center justify-between shadow-xl">
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-2">
              <span className="font-headline text-lg text-[#dae2fc] font-bold">
                Field Incident Ingest
              </span>
              <span className="px-1.5 py-0.5 rounded bg-[#4cd7f6]/20 text-[#4cd7f6] font-mono text-[9px] font-bold">
                OFFLINE SYNC
              </span>
            </div>
            <span className="font-body text-xs text-[#bcc9cd]">
              Report geo-tagged tension fissures & rockfalls
            </span>
          </div>
          <button
            type="button"
            onClick={onOpenReportModal}
            className="px-3.5 py-2 bg-[#a40217] hover:bg-[#ef4444] text-[#dae2fc] font-mono text-xs font-bold uppercase rounded flex items-center gap-1.5 shadow-lg transition-transform active:scale-95 shrink-0 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">photo_camera</span>
            <span>Report Landslip</span>
          </button>
        </div>

        {/* HISTORICAL PLAYBACK & MODEL SCRUBBER (col-span-8) */}
        <div className="lg:col-span-8 bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col justify-between gap-2 shadow-xl">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setIsPlayingScrubber(!isPlayingScrubber)}
                className="w-8 h-8 rounded bg-[#06b6d4] text-[#003640] flex items-center justify-center hover:bg-[#4cd7f6] transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">
                  {isPlayingScrubber ? 'pause' : 'play_arrow'}
                </span>
              </button>
              <div className="flex flex-col">
                <span className="font-mono text-xs text-[#dae2fc] font-bold uppercase tracking-wider">
                  ⏱️ Replay 2022 Tupul Disaster Telemetry
                </span>
                <span className="font-mono text-[10px] text-[#4cd7f6]">
                  PyTorch GNN Validation: Predicted Tupul Disaster 12h In Advance
                </span>
              </div>
            </div>
            <span className="px-2.5 py-1 bg-[#171f32] text-[#ffb3ad] font-mono text-xs font-bold rounded border border-[#ef4444]/30">
              SCRUBBER: {step.label} {step.stepId === 'T-12h' ? '(MANDATORY EVAC)' : ''}
            </span>
          </div>

          {/* 4-STEP TIMELINE TRACK SCRUBBER */}
          <div className="relative py-1">
            {/* Baseline Rail */}
            <div className="w-full h-2 bg-[#2d3449] rounded-full overflow-hidden flex">
              <div
                className={`w-1/4 h-full transition-colors ${
                  currentStepIndex >= 0 ? 'bg-[#10b981]' : 'bg-[#222a3d]'
                }`}
              />
              <div
                className={`w-1/4 h-full transition-colors ${
                  currentStepIndex >= 1 ? 'bg-[#ffb95f]' : 'bg-[#222a3d]'
                }`}
              />
              <div
                className={`w-1/4 h-full transition-colors ${
                  currentStepIndex >= 2 ? 'bg-[#e79400]' : 'bg-[#222a3d]'
                }`}
              />
              <div
                className={`w-1/4 h-full transition-colors ${
                  currentStepIndex >= 3 ? 'bg-[#ef4444] animate-pulse' : 'bg-[#222a3d]'
                }`}
              />
            </div>

            {/* Step Indicators Clickable */}
            <div className="grid grid-cols-4 gap-2 mt-2">
              {HISTORICAL_SCRUBBER_STEPS.map((s, idx) => {
                const isActive = idx === currentStepIndex;
                return (
                  <button
                    key={s.stepId}
                    type="button"
                    onClick={() => handleSelectStep(idx)}
                    className={`flex flex-col text-left p-1.5 rounded transition-all cursor-pointer ${
                      isActive ? 'bg-[#222a3d] ring-1 ring-[#4cd7f6]' : 'hover:bg-[#171f32]'
                    }`}
                  >
                    <span
                      className={`font-mono text-[10px] ${
                        isActive ? 'text-[#4cd7f6] font-bold' : 'text-[#869397]'
                      }`}
                    >
                      {s.label}
                    </span>
                    <span
                      className={`font-mono text-xs font-bold ${
                        idx === 3
                          ? 'text-[#ffb3ad]'
                          : idx === 2
                          ? 'text-[#ffb95f]'
                          : idx === 1
                          ? 'text-[#ffb95f]'
                          : 'text-[#10b981]'
                      }`}
                    >
                      {s.sublabel}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
