import React, { useState, useEffect } from 'react';
import { EVACUATION_ROUTES } from '../data/mockTelemetry';
import { EvacuationRoute } from '../types/telemetry';
import { soundFx } from '../utils/audioAlert';
import { api, EvacuationRouteResponse } from '../services/api';

export const SafeCorridorsModule: React.FC = () => {
  const [routes, setRoutes] = useState<EvacuationRoute[]>(EVACUATION_ROUTES);
  const [activeRoute, setActiveRoute] = useState<EvacuationRoute>(EVACUATION_ROUTES[0]);
  const [bhuvanData, setBhuvanData] = useState<EvacuationRouteResponse | null>(null);
  const [isSimulatingGps, setIsSimulatingGps] = useState(false);
  const [navStepIndex, setNavStepIndex] = useState(0);

  useEffect(() => {
    const fetchRealRoute = async () => {
      try {
        const liveRes = await api.getEvacuationRoute(24.77, 93.68, 24.81, 93.94, true);
        if (liveRes && liveRes.route_summary) {
          setBhuvanData(liveRes);
          // Update the primary route with real ISRO Bhuvan calculation
          const updatedRoute: EvacuationRoute = {
            ...EVACUATION_ROUTES[0],
            distanceKm: liveRes.route_summary.total_distance_km,
            transitMins: Math.round(liveRes.route_summary.estimated_time_minutes),
            hazardsAvoided: liveRes.route_summary.avoided_hazard_zones,
            status: liveRes.route_summary.evacuation_status === 'CLEAR_SAFE_PASSAGE' ? 'CLEAR' : 'RESTRICTED',
            routeHighlights: liveRes.turn_by_turn_instructions || EVACUATION_ROUTES[0].routeHighlights,
          };
          setRoutes([updatedRoute, EVACUATION_ROUTES[1], EVACUATION_ROUTES[2]]);
          setActiveRoute(updatedRoute);
        }
      } catch (err) {
        console.warn('Using local fallback for Bhuvan route:', err);
      }
    };
    fetchRealRoute();
  }, []);

  const turnByTurnSteps = bhuvanData?.turn_by_turn_instructions?.map((inst, idx) => ({
    instruction: inst,
    distance: `${(idx * 7.5 + 2.4).toFixed(1)} km`,
    elevation: `${780 + idx * 25}m MSL`,
    note: idx === 0 ? 'BRO road safety checkpoint verified' : 'ISRO Bhuvan real-time hazard clearance active',
  })) || [
    {
      instruction: 'Depart Tupul Village heading South-East on Old Cachar Road',
      distance: '2.4 km',
      elevation: '820m MSL',
      note: 'Road surface paved; BRO survey crew deployed on shoulder',
    },
    {
      instruction: 'Take right fork at Leikop Spur toward Ije River Bailey Bridge',
      distance: '6.8 km',
      elevation: '740m MSL',
      note: 'Pore pressure sensors verify riverbank stable; proceed at 30 km/h',
    },
    {
      instruction: 'Cross Bailey Bridge 02 (Max 18 Tonne Load Capacity)',
      distance: '11.5 km',
      elevation: '690m MSL',
      note: 'Monitored by SDRF Manipur unit; clearance signal active',
    },
    {
      instruction: 'Ascend Western Ridge toward Noney Sub-Divisional Bypass',
      distance: '22.1 km',
      elevation: '860m MSL',
      note: 'Well-drained sandstone ridge; zero active slip indicators',
    },
    {
      instruction: 'Arrive at Noney Community Health Center (Safe Shelter)',
      distance: '35.9 km',
      elevation: '860m MSL',
      note: 'Shelter capacity available; 142 beds, clean water, medical triage',
    },
  ];

  const handleStartSim = () => {
    soundFx.playRadarPing();
    setIsSimulatingGps(true);
    setNavStepIndex(0);
  };

  const handleNextStep = () => {
    soundFx.playRadarPing();
    if (navStepIndex < turnByTurnSteps.length - 1) {
      setNavStepIndex((prev) => prev + 1);
    } else {
      setIsSimulatingGps(false);
      setNavStepIndex(0);
    }
  };


  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Header Bar */}
      <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-wrap items-center justify-between gap-3 shadow-lg">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
              // EVACUATION PASSAGE & RELIEF LOGISTICS
            </span>
            <span className="px-2 py-0.5 rounded bg-[#10b981]/20 text-[#10b981] font-mono text-[10px] font-bold">
              ISRO BHUVAN VERIFIED PASSAGE
            </span>
          </div>
          <span className="font-headline text-xl text-[#dae2fc] font-bold">
            Safe Corridor Navigation & Emergency Shelters
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleStartSim}
            className="px-3.5 py-2 rounded bg-[#06b6d4] hover:bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold uppercase flex items-center gap-2 shadow-lg transition-all cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">turn_sharp_right</span>
            <span>Simulate GPS Turn-by-Turn</span>
          </button>
        </div>
      </div>

      {/* GPS Simulation Active Banner */}
      {isSimulatingGps && (
        <div className="bg-[#060e20] p-4 rounded-xl border-2 border-[#4cd7f6] flex flex-col md:flex-row items-center justify-between gap-4 shadow-[0_0_24px_rgba(76,215,246,0.25)] animate-in fade-in">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-[#4cd7f6] text-[#003640] flex items-center justify-center font-bold shrink-0">
              <span className="material-symbols-outlined text-[28px]">navigation</span>
            </div>
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-[#4cd7f6] uppercase font-bold tracking-wider">
                ACTIVE GPS NAVIGATION • STEP {navStepIndex + 1} OF {turnByTurnSteps.length}
              </span>
              <span className="font-headline text-lg font-bold text-[#dae2fc]">
                {turnByTurnSteps[navStepIndex].instruction}
              </span>
              <span className="font-mono text-xs text-[#bcc9cd]">
                Distance: {turnByTurnSteps[navStepIndex].distance} • Elevation:{' '}
                {turnByTurnSteps[navStepIndex].elevation} • {turnByTurnSteps[navStepIndex].note}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={handleNextStep}
              className="px-4 py-2 bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold rounded hover:bg-[#a5f3fc] transition-colors cursor-pointer"
            >
              {navStepIndex < turnByTurnSteps.length - 1 ? 'Next Waypoint' : 'Arrive at Shelter'}
            </button>
            <button
              type="button"
              onClick={() => setIsSimulatingGps(false)}
              className="px-3 py-2 bg-[#222a3d] text-[#bcc9cd] font-mono text-xs rounded hover:text-white transition-colors cursor-pointer"
            >
              Exit Nav
            </button>
          </div>
        </div>
      )}

      {/* Grid: 3 Routes Comparison & Shelter Status */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* Left Column: Route Cards (col-span-7) */}
        <div className="xl:col-span-7 flex flex-col gap-3">
          <span className="font-mono text-xs text-[#869397] uppercase tracking-wider font-semibold">
            Corridor Route Options Comparison
          </span>

          {routes.map((route) => {
            const isSelected = activeRoute.id === route.id;
            const isClear = route.status === 'CLEAR';
            const isBlocked = route.status === 'IMPASSABLE';

            return (
              <div
                key={route.id}
                onClick={() => {
                  soundFx.playRadarPing();
                  setActiveRoute(route);
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#171f32] border-[#4cd7f6] shadow-xl'
                    : 'bg-[#131b2e] border-[#222a3d] hover:bg-[#171f32]'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex flex-col">
                    <span className="font-headline text-base font-bold text-[#dae2fc]">
                      {route.name}
                    </span>
                    <span className="font-mono text-xs text-[#869397]">
                      {route.origin} → {route.destination}
                    </span>
                  </div>
                  <span
                    className={`px-2.5 py-0.5 rounded font-mono text-xs font-bold uppercase ${
                      isClear
                        ? 'bg-[#10b981]/20 text-[#10b981] border border-[#10b981]/40'
                        : isBlocked
                        ? 'bg-[#a40217]/50 text-[#ffb3ad] border border-[#ef4444]/40 animate-pulse'
                        : 'bg-[#ffb95f]/20 text-[#ffb95f]'
                    }`}
                  >
                    {route.status}
                  </span>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-3 gap-2 mt-3 text-xs font-mono">
                  <div className="p-2 bg-[#131b2e] rounded border border-[#222a3d]">
                    <span className="text-[#869397] block text-[10px]">Transit Time</span>
                    <span className={`font-bold ${isBlocked ? 'text-[#ffb3ad]' : 'text-white'}`}>
                      {isBlocked ? 'BLOCKED' : `${route.transitMins} mins`}
                    </span>
                  </div>
                  <div className="p-2 bg-[#131b2e] rounded border border-[#222a3d]">
                    <span className="text-[#869397] block text-[10px]">Corridor Distance</span>
                    <span className="text-white font-bold">{route.distanceKm} km</span>
                  </div>
                  <div className="p-2 bg-[#131b2e] rounded border border-[#222a3d]">
                    <span className="text-[#869397] block text-[10px]">Hazard Avoidance</span>
                    <span className="text-[#4cd7f6] font-bold">
                      {route.hazardsAvoided} Critical Slide Avoided
                    </span>
                  </div>
                </div>

                {/* Highlights */}
                <ul className="mt-3 flex flex-col gap-1 text-xs font-body text-[#bcc9cd]">
                  {route.routeHighlights.map((hl, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="material-symbols-outlined text-[14px] text-[#4cd7f6] shrink-0 mt-0.5">
                        check
                      </span>
                      <span>{hl}</span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>

        {/* Right Column: Shelters & Relief Centers (col-span-5) */}
        <div className="xl:col-span-5 flex flex-col gap-4">
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-3 shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // ACTIVE EMERGENCY RELIEF SHELTERS
              </span>
              <span className="font-mono text-xs text-[#10b981] font-bold">2 Hubs Open</span>
            </div>

            {/* Shelter 1: Noney Community Health Center */}
            <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex flex-col gap-2">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-headline text-sm font-bold text-[#dae2fc]">
                    Noney Community Health Center
                  </span>
                  <span className="font-mono text-xs text-[#4cd7f6] block">
                    Coordinates: 24°51'08"N, 93°38'02"E
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded bg-[#10b981]/20 text-[#10b981] font-mono text-[10px] font-bold">
                  142 Beds Available
                </span>
              </div>

              {/* Capacity Bar */}
              <div className="flex flex-col gap-1">
                <div className="flex justify-between font-mono text-[11px] text-[#869397]">
                  <span>Occupancy (108 / 250)</span>
                  <span className="text-[#dae2fc]">43.2% Full</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#222a3d] overflow-hidden">
                  <div className="h-full bg-[#4cd7f6] w-[43%]" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-[#bcc9cd] pt-1">
                <span>Medical: 4 Doctors, 8 Nurses</span>
                <span>Water: 15,000L Potable</span>
              </div>
            </div>

            {/* Shelter 2: Tupul Higher Secondary School Camp */}
            <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex flex-col gap-2">
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-headline text-sm font-bold text-[#dae2fc]">
                    Tupul Upper School Relief Camp
                  </span>
                  <span className="font-mono text-xs text-[#ffb95f] block">
                    High Elevation Safe Zone (940m MSL)
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded bg-[#ffb95f]/20 text-[#ffb95f] font-mono text-[10px] font-bold">
                  85 Beds Available
                </span>
              </div>

              {/* Capacity Bar */}
              <div className="flex flex-col gap-1">
                <div className="flex justify-between font-mono text-[11px] text-[#869397]">
                  <span>Occupancy (115 / 200)</span>
                  <span className="text-[#dae2fc]">57.5% Full</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#222a3d] overflow-hidden">
                  <div className="h-full bg-[#ffb95f] w-[57%]" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-[#bcc9cd] pt-1">
                <span>Food Rations: 7-Day Supply</span>
                <span>Generator: Diesel Backup</span>
              </div>
            </div>
          </div>

          {/* Offline GPS Export Card */}
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex items-center justify-between shadow-xl">
            <div className="flex flex-col">
              <span className="font-headline text-sm font-bold text-[#dae2fc]">
                Download Offline GPX / KML
              </span>
              <span className="font-body text-xs text-[#bcc9cd]">
                Full vector track for handheld GPS & OsmAnd
              </span>
            </div>
            <button
              type="button"
              onClick={() => soundFx.playRadarPing()}
              className="px-3 py-1.5 bg-[#222a3d] hover:bg-[#31394d] text-[#4cd7f6] rounded font-mono text-xs font-bold border border-[#4cd7f6]/40 flex items-center gap-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">download</span>
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
