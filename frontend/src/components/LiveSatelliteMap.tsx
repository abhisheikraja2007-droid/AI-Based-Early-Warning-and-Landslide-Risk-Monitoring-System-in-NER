/**
 * Live Satellite Imagery GIS Map Component for Drishti-NER
 * Provides high-resolution satellite tiles (ESRI World Imagery & Sentinel-2)
 * with dynamic NH-37 corridor hazard overlays, ISRO Bhuvan evacuation routing,
 * and live geotechnical risk telemetry markers.
 */

import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { CorridorSegment } from '../types/telemetry';
import { EvacuationRouteResponse } from '../services/api';

interface LiveSatelliteMapProps {
  segments: CorridorSegment[];
  selectedSegmentId: number;
  onSelectSegment: (segment: CorridorSegment) => void;
  bhuvanRoute?: EvacuationRouteResponse | null;
  showPytorchHeatmap: boolean;
  showRainfallRadar: boolean;
  showShelters: boolean;
  currentStepIndex: number;
}

// Satellite tile providers
const SATELLITE_PROVIDERS = {
  esri_satellite: {
    name: 'ESRI High-Res Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP',
    maxZoom: 18,
  },
  sentinel2: {
    name: 'Sentinel-2 Cloudless (ESA)',
    url: 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg',
    attribution: '&copy; Sentinel-2 cloudless by EOX IT Services GmbH',
    maxZoom: 16,
  },
  carto_dark: {
    name: 'Tactical Midnight Vector',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 19,
  },
};

export const LiveSatelliteMap: React.FC<LiveSatelliteMapProps> = ({
  segments,
  selectedSegmentId,
  onSelectSegment,
  bhuvanRoute,
  showPytorchHeatmap,
  showRainfallRadar,
  showShelters,
  currentStepIndex,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const overlayLayersRef = useRef<{ [key: string]: L.LayerGroup }>({});

  const [activeTileSource, setActiveTileSource] = useState<keyof typeof SATELLITE_PROVIDERS>('esri_satellite');
  const [isMapReady, setIsMapReady] = useState(false);

  // Initialize Leaflet map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center on NH-37 Tupul / Manipur Corridor: 24.84°N, 93.75°E
    const map = L.map(mapContainerRef.current, {
      center: [24.84, 93.75],
      zoom: 11,
      minZoom: 9,
      maxZoom: 18,
      zoomControl: false,
    });

    // Custom dark zoom control
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Initial Satellite Tile Layer
    const tileConf = SATELLITE_PROVIDERS[activeTileSource];
    const tileLayer = L.tileLayer(tileConf.url, {
      attribution: tileConf.attribution,
      maxZoom: tileConf.maxZoom,
    }).addTo(map);

    tileLayerRef.current = tileLayer;

    // Initialize layer groups for dynamic overlays
    overlayLayersRef.current = {
      corridors: L.layerGroup().addTo(map),
      bhuvanDetour: L.layerGroup().addTo(map),
      heatmap: L.layerGroup().addTo(map),
      shelters: L.layerGroup().addTo(map),
    };

    mapInstanceRef.current = map;
    setIsMapReady(true);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update base tile layer when activeTileSource changes
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    if (tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
    }
    const tileConf = SATELLITE_PROVIDERS[activeTileSource];
    const newTileLayer = L.tileLayer(tileConf.url, {
      attribution: tileConf.attribution,
      maxZoom: tileConf.maxZoom,
    }).addTo(mapInstanceRef.current);
    tileLayerRef.current = newTileLayer;
    newTileLayer.bringToBack();
  }, [activeTileSource]);

  // Render Corridor Segments and Hazards
  useEffect(() => {
    if (!isMapReady || !mapInstanceRef.current || !overlayLayersRef.current.corridors) return;
    const group = overlayLayersRef.current.corridors;
    group.clearLayers();

    segments.forEach((seg) => {
      const isSelected = seg.id === selectedSegmentId;
      const isCritical = seg.status === 'critical';
      const isWatch = seg.status === 'watch';

      const color = isCritical ? '#ef4444' : isWatch ? '#f59e0b' : '#10b981';

      // Sector waypoint marker
      const markerHtml = `
        <div class="relative flex items-center justify-center cursor-pointer group">
          ${isCritical ? '<div class="absolute w-8 h-8 rounded-full bg-red-500/40 animate-ping"></div>' : ''}
          <div class="w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] text-white shadow-lg border-2 ${
            isSelected ? 'border-cyan-400 scale-125' : 'border-white/80'
          }" style="background-color: ${color}">
            ${seg.id}
          </div>
          <div class="absolute bottom-6 left-1/2 -translate-x-1/2 hidden group-hover:flex px-2 py-1 bg-slate-900/90 text-cyan-300 text-[10px] font-mono whitespace-nowrap rounded border border-slate-700 shadow-xl">
            ${seg.sectorName} (${seg.kmRange})
          </div>
        </div>
      `;

      const icon = L.divIcon({
        className: 'custom-hazard-marker',
        html: markerHtml,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
      });

      const marker = L.marker([seg.coords.lat, seg.coords.lng], { icon });

      // Custom dark glassmorphism popup
      const popupHtml = `
        <div style="font-family: 'JetBrains Mono', monospace; min-width: 210px; background: #0f172a; color: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #334155;">
          <div style="font-size: 11px; font-weight: bold; color: ${color}; text-transform: uppercase;">
            ${isCritical ? 'CRITICAL HAZARD - ROAD BLOCKED' : isWatch ? 'ELEVATED SURVEILLANCE' : 'SAFE TRAVEL CORRIDOR'}
          </div>
          <div style="font-size: 13px; font-weight: 700; margin-top: 2px;">${seg.name}</div>
          <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Chainage: Km ${seg.kmRange} • Alt: ${seg.elevationMsl}m MSL</div>
          <div style="margin-top: 6px; padding: 6px; background: #1e293b; border-radius: 4px; font-size: 11px;">
            <div>Failure Probability: <b style="color: ${color}">${Math.round((1 - seg.stabilityScore) * 100)}%</b></div>
            <div>7-Day Rainfall: <b>${seg.rainfall7DayMm} mm</b></div>
            <div>Soil Saturation: <b>${seg.soilMoisturePct}%</b></div>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);
      marker.on('click', () => onSelectSegment(seg));
      group.addLayer(marker);
    });

    // Draw NH-37 Corridor Polyline connecting all sectors
    const latLngs = segments.map((s) => [s.coords.lat, s.coords.lng] as [number, number]);
    const corridorLine = L.polyline(latLngs, {
      color: '#38bdf8',
      weight: 4,
      opacity: 0.8,
      dashArray: '6, 6',
    });
    group.addLayer(corridorLine);
  }, [segments, selectedSegmentId, isMapReady]);

  // Render ISRO Bhuvan Safe Evacuation Detour Route
  useEffect(() => {
    if (!isMapReady || !mapInstanceRef.current || !overlayLayersRef.current.bhuvanDetour) return;
    const group = overlayLayersRef.current.bhuvanDetour;
    group.clearLayers();

    if (bhuvanRoute && bhuvanRoute.geojson && bhuvanRoute.geojson.geometry) {
      const coords = bhuvanRoute.geojson.geometry.coordinates.map(
        ([lon, lat]) => [lat, lon] as [number, number]
      );

      const detourLine = L.polyline(coords, {
        color: '#4cd7f6',
        weight: 5,
        opacity: 0.95,
      });

      detourLine.bindPopup(`
        <div style="font-family: monospace; background: #0f172a; color: #fff; padding: 8px; border-radius: 6px;">
          <b style="color: #4cd7f6;">ISRO Bhuvan Emergency Detour</b>
          <div>Distance: 35.9 km (Clear Safe Passage)</div>
          <div>Bypasses Km 42 Tupul Landslide Runout</div>
        </div>
      `);

      group.addLayer(detourLine);
    }
  }, [bhuvanRoute, isMapReady]);

  // Render PyTorch Susceptibility Heatmap & IMD Radar circles
  useEffect(() => {
    if (!isMapReady || !mapInstanceRef.current || !overlayLayersRef.current.heatmap) return;
    const group = overlayLayersRef.current.heatmap;
    group.clearLayers();

    if (showPytorchHeatmap) {
      // Add PyTorch high-susceptibility zones over steep mountain faces
      const highRiskZones = [
        { lat: 24.855, lng: 93.697, radius: 2400, color: '#ef4444', label: 'Tupul Fault Zone (Susceptibility: 0.88)' },
        { lat: 24.845, lng: 93.751, radius: 1800, color: '#f59e0b', label: 'Sinam East Face (Susceptibility: 0.62)' },
        { lat: 24.862, lng: 93.612, radius: 1600, color: '#f59e0b', label: 'Noney Pier 14 Ridge (Susceptibility: 0.58)' },
      ];

      highRiskZones.forEach((z) => {
        const circle = L.circle([z.lat, z.lng], {
          radius: z.radius,
          color: z.color,
          fillColor: z.color,
          fillOpacity: 0.28,
          weight: 1.5,
        }).bindPopup(`<b style="font-family: monospace;">${z.label}</b>`);
        group.addLayer(circle);
      });
    }

    if (showRainfallRadar) {
      // IMD Doppler radar inflow ring over the basin
      const radarRing = L.circle([24.83, 93.72], {
        radius: 7500,
        color: '#06b6d4',
        fillColor: '#06b6d4',
        fillOpacity: 0.12,
        weight: 1,
        dashArray: '4, 8',
      }).bindPopup('<b style="font-family: monospace;">IMD Doppler Radar: Orographic Inflow Active</b>');
      group.addLayer(radarRing);
    }
  }, [showPytorchHeatmap, showRainfallRadar, isMapReady]);

  // Render Evacuation Shelters & Relief Camps
  useEffect(() => {
    if (!isMapReady || !mapInstanceRef.current || !overlayLayersRef.current.shelters) return;
    const group = overlayLayersRef.current.shelters;
    group.clearLayers();

    if (showShelters) {
      const shelters = [
        { lat: 24.81, lng: 93.94, name: 'Noney Community Health Center', capacity: '142 Beds Available', icon: 'local_hospital' },
        { lat: 24.832, lng: 93.842, name: 'Leikop Emergency Relief Staging Camp', capacity: 'BRO & NDRF Staging Ground', icon: 'shield' },
      ];

      shelters.forEach((sh) => {
        const marker = L.marker([sh.lat, sh.lng], {
          icon: L.divIcon({
            className: 'shelter-pin',
            html: `
              <div class="px-2 py-1 rounded-full bg-emerald-500 text-slate-900 font-bold text-[10px] flex items-center gap-1 shadow-lg border-2 border-white whitespace-nowrap cursor-pointer">
                <span>🏥</span>
                <span>${sh.name.split(' ')[0]}</span>
              </div>
            `,
            iconAnchor: [30, 15],
          }),
        }).bindPopup(`
          <div style="font-family: monospace; padding: 6px;">
            <b style="color: #10b981;">${sh.name}</b>
            <div>Status: Operational Evacuation Shelter</div>
            <div>${sh.capacity}</div>
          </div>
        `);
        group.addLayer(marker);
      });
    }
  }, [showShelters, isMapReady]);

  const handleResetView = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([24.84, 93.75], 11, { animate: true });
    }
  };

  return (
    <div className="relative w-full h-[620px] rounded-xl overflow-hidden border border-[#222a3d] shadow-2xl bg-[#060e20]">
      {/* Live Leaflet Map Container */}
      <div ref={mapContainerRef} className="w-full h-full z-10" />

      {/* Top Floating Controls HUD */}
      <div className="absolute top-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        {/* Live Satellite Status Pill */}
        <div className="pointer-events-auto flex items-center gap-2 bg-[#060e20]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#222a3d] shadow-lg">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10b981] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#10b981]"></span>
          </span>
          <span className="font-mono text-xs font-bold text-[#dae2fc]">
            LIVE SATELLITE FEED: <span className="text-[#4cd7f6]">{SATELLITE_PROVIDERS[activeTileSource].name}</span>
          </span>
        </div>

        {/* Tile Provider Switcher */}
        <div className="pointer-events-auto flex items-center gap-1 bg-[#060e20]/90 backdrop-blur-md p-1 rounded-lg border border-[#222a3d] shadow-lg">
          {(Object.keys(SATELLITE_PROVIDERS) as (keyof typeof SATELLITE_PROVIDERS)[]).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => setActiveTileSource(key)}
              className={`px-2.5 py-1 font-mono text-[11px] rounded transition-all font-semibold cursor-pointer ${
                activeTileSource === key
                  ? 'bg-[#06b6d4] text-[#003640] shadow'
                  : 'text-[#869397] hover:text-[#dae2fc]'
              }`}
            >
              {key === 'esri_satellite' ? '🛰️ ESRI Satellite' : key === 'sentinel2' ? '🌍 Sentinel-2' : '🌑 Dark Vector'}
            </button>
          ))}
          <button
            type="button"
            onClick={handleResetView}
            title="Reset Map View to NH-37 Corridor"
            className="px-2 py-1 bg-[#171f32] text-[#4cd7f6] hover:bg-[#222a3d] rounded font-mono text-xs cursor-pointer ml-1"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Bottom Map Legend */}
      <div className="absolute bottom-3 left-3 z-20 pointer-events-auto bg-[#060e20]/90 backdrop-blur-md p-2.5 rounded-lg border border-[#222a3d] shadow-xl text-xs font-mono flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></span>
          <span className="text-[#dae2fc]">Normal</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></span>
          <span className="text-[#dae2fc]">Watch</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444] animate-pulse"></span>
          <span className="text-[#ffb3ad] font-bold">Evacuate</span>
        </div>
        <div className="flex items-center gap-1.5 border-l border-[#222a3d] pl-2">
          <span className="w-3 h-1 bg-[#4cd7f6] rounded"></span>
          <span className="text-[#4cd7f6]">Bhuvan Detour</span>
        </div>
      </div>
    </div>
  );
};
