import React from 'react';
import { CorridorSegment } from '../types/telemetry';

interface SegmentDetailModalProps {
  segment: CorridorSegment | null;
  onClose: () => void;
  onNavigateDetour: () => void;
}

export const SegmentDetailModal: React.FC<SegmentDetailModalProps> = ({
  segment,
  onClose,
  onNavigateDetour,
}) => {
  if (!segment) return null;

  const isCritical = segment.status === 'critical';
  const isWatch = segment.status === 'watch';

  return (
    <div className="fixed inset-0 z-50 bg-[#060e20]/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#171f32] w-full max-w-lg p-5 sm:p-6 rounded-2xl border border-[#222a3d] shadow-2xl flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-headline text-lg sm:text-xl text-[#dae2fc] font-bold">
                {segment.name}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                  isCritical
                    ? 'bg-[#a40217]/50 text-[#ffb3ad] animate-pulse'
                    : isWatch
                    ? 'bg-[#e79400]/30 text-[#ffb95f]'
                    : 'bg-[#10b981]/20 text-[#10b981]'
                }`}
              >
                {segment.status}
              </span>
            </div>
            <span className="font-mono text-xs text-[#4cd7f6]">{segment.sectorName}</span>
          </div>
          <button type="button" onClick={onClose} className="text-[#bcc9cd] hover:text-white p-1">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Primary Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
          <div className="p-2.5 bg-[#131b2e] rounded border border-[#222a3d] flex flex-col">
            <span className="text-[#869397] text-[10px]">Stability Score</span>
            <span
              className={`text-base font-bold ${
                isCritical ? 'text-[#ffb3ad]' : isWatch ? 'text-[#ffb95f]' : 'text-[#10b981]'
              }`}
            >
              {segment.stabilityScore.toFixed(2)}
            </span>
          </div>

          <div className="p-2.5 bg-[#131b2e] rounded border border-[#222a3d] flex flex-col">
            <span className="text-[#869397] text-[10px]">Pore Pressure</span>
            <span
              className={`text-base font-bold ${
                segment.porePressureKPa > 80 ? 'text-[#ffb3ad]' : 'text-[#dae2fc]'
              }`}
            >
              {segment.porePressureKPa} kPa
            </span>
          </div>

          <div className="p-2.5 bg-[#131b2e] rounded border border-[#222a3d] flex flex-col">
            <span className="text-[#869397] text-[10px]">InSAR Creep</span>
            <span
              className={`text-base font-bold ${
                segment.displacementMmDay > 1.5 ? 'text-[#ffb3ad]' : 'text-[#dae2fc]'
              }`}
            >
              {segment.displacementMmDay} mm/d
            </span>
          </div>

          <div className="p-2.5 bg-[#131b2e] rounded border border-[#222a3d] flex flex-col">
            <span className="text-[#869397] text-[10px]">Slope Angle</span>
            <span className="text-base font-bold text-[#dae2fc]">{segment.slopeAngleDeg}°</span>
          </div>
        </div>

        {/* Hazard List if any */}
        {segment.activeHazards && segment.activeHazards.length > 0 && (
          <div className="p-3 bg-[#a40217]/20 border border-[#ef4444]/30 rounded-lg flex flex-col gap-1.5">
            <span className="font-mono text-xs text-[#ffb3ad] font-bold uppercase">
              // Active Threat Classification
            </span>
            <ul className="flex flex-col gap-1 text-xs text-[#ffdad6] font-body">
              {segment.activeHazards.map((hz, i) => (
                <li key={i} className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[14px] text-[#ef4444]">
                    error
                  </span>
                  <span>{hz}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Geographic location */}
        <div className="p-3 bg-[#131b2e] rounded-lg border border-[#222a3d] flex items-center justify-between text-xs font-mono">
          <span className="text-[#869397]">GPS Coordinates:</span>
          <span className="text-[#4cd7f6]">
            {segment.coords.lat}°N, {segment.coords.lng}°E
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 mt-1">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 font-mono text-xs text-[#bcc9cd] hover:text-white"
          >
            Close
          </button>
          {segment.detourAvailable && (
            <button
              type="button"
              onClick={() => {
                onClose();
                onNavigateDetour();
              }}
              className="px-4 py-2 bg-[#06b6d4] hover:bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold uppercase rounded shadow-md transition-all cursor-pointer"
            >
              Reroute via Safe Detour
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
