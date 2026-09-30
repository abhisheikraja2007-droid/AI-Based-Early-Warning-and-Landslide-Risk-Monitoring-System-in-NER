import React from 'react';
import { soundFx } from '../utils/audioAlert';

export type ModuleType =
  | 'corridor-surveillance'
  | 'sensor-matrix'
  | 'predictive-ai-models'
  | 'incident-dispatch'
  | 'evacuation-routes';

interface SidebarProps {
  activeModule: ModuleType;
  setActiveModule: (module: ModuleType) => void;
  isOpenMobile: boolean;
  setIsOpenMobile: (open: boolean) => void;
  porePressureRisk?: 'HIGH RISK' | 'ELEVATED' | 'NORMAL';
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeModule,
  setActiveModule,
  isOpenMobile,
  setIsOpenMobile,
  porePressureRisk = 'HIGH RISK',
}) => {
  const modules = [
    {
      id: 'corridor-surveillance' as ModuleType,
      label: 'Corridor Map',
      icon: 'radar',
      desc: 'Topographic Surveillance',
    },
    {
      id: 'sensor-matrix' as ModuleType,
      label: 'Sensor Array',
      icon: 'sensors',
      desc: '144 Telemetry Nodes',
    },
    {
      id: 'predictive-ai-models' as ModuleType,
      label: 'AI Forecast',
      icon: 'insights',
      desc: 'PyTorch GNN Ensemble',
    },
    {
      id: 'incident-dispatch' as ModuleType,
      label: 'Dispatch & SAR',
      icon: 'emergency_share',
      desc: 'NDRF & BRO Response',
    },
    {
      id: 'evacuation-routes' as ModuleType,
      label: 'Safe Corridors',
      icon: 'alt_route',
      desc: 'ISRO Bhuvan Bypass',
    },
  ];

  const handleSelectModule = (id: ModuleType) => {
    soundFx.playRadarPing();
    setActiveModule(id);
    setIsOpenMobile(false);
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpenMobile(false)}
        />
      )}

      <aside
        className={`fixed left-0 top-0 h-full w-64 bg-[#060e20] border-r border-[#222a3d] z-50 flex flex-col justify-between shadow-[4px_0_24px_rgba(0,0,0,0.6)] transition-transform duration-200 ease-in-out ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex flex-col">
          {/* Station Identification Header */}
          <div className="h-20 px-4 flex items-center justify-between bg-[#131b2e] border-b border-[#222a3d]">
            <div className="flex flex-col">
              <span className="font-mono text-xs text-[#4cd7f6] tracking-wider uppercase font-bold">
                TACTICAL TELEMETRY
              </span>
              <span className="font-mono text-[11px] text-[#bcc9cd]">
                STATION ID: NH37-IMP
              </span>
            </div>
            {/* Close button on mobile */}
            <button
              onClick={() => setIsOpenMobile(false)}
              className="lg:hidden text-[#bcc9cd] hover:text-white p-1"
              type="button"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          {/* Section Subtitle */}
          <div className="px-4 py-3 border-b border-[#171f32]">
            <span className="font-mono text-[10px] text-[#869397] uppercase tracking-widest font-semibold">
              Operational Modules
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1.5 p-3">
            {modules.map((m) => {
              const isActive = activeModule === m.id;
              return (
                <button
                  key={m.id}
                  onClick={() => handleSelectModule(m.id)}
                  type="button"
                  className={`flex items-center gap-3 px-3 py-2.5 rounded transition-all text-left group ${
                    isActive
                      ? 'bg-[#222a3d] text-[#4cd7f6] font-bold shadow-md border-l-2 border-[#4cd7f6]'
                      : 'text-[#bcc9cd] hover:bg-[#171f32] hover:text-[#dae2fc]'
                  }`}
                >
                  <span
                    className={`material-symbols-outlined text-[20px] transition-transform ${
                      isActive ? 'text-[#4cd7f6] scale-110' : 'text-[#869397] group-hover:text-[#4cd7f6]'
                    }`}
                  >
                    {m.icon}
                  </span>
                  <div className="flex flex-col leading-tight">
                    <span className="font-headline text-sm font-semibold tracking-wide">
                      {m.label}
                    </span>
                    <span className="font-mono text-[10px] text-[#869397] group-hover:text-[#bcc9cd]">
                      {m.desc}
                    </span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer Metrics Panel */}
        <div className="p-4 bg-[#131b2e] border-t border-[#222a3d] flex flex-col gap-2">
          <div className="flex items-center justify-between font-mono text-[11px] text-[#bcc9cd]">
            <span>RADAR LATENCY</span>
            <span className="text-[#4cd7f6] font-bold">42ms</span>
          </div>
          <div className="flex items-center justify-between font-mono text-[11px] text-[#bcc9cd]">
            <span>PORE PRESSURE</span>
            <span
              className={`font-bold ${
                porePressureRisk === 'HIGH RISK'
                  ? 'text-[#ffb3ad] animate-pulse'
                  : porePressureRisk === 'ELEVATED'
                  ? 'text-[#ffb95f]'
                  : 'text-[#10b981]'
              }`}
            >
              {porePressureRisk}
            </span>
          </div>

          {/* Threat Meter Bar */}
          <div className="w-full h-1.5 bg-[#222a3d] rounded-full overflow-hidden mt-1">
            <div
              className={`h-full transition-all duration-500 ${
                porePressureRisk === 'HIGH RISK'
                  ? 'bg-[#ef4444] w-4/5'
                  : porePressureRisk === 'ELEVATED'
                  ? 'bg-[#e79400] w-3/5'
                  : 'bg-[#10b981] w-1/4'
              }`}
            />
          </div>

          <div className="pt-2 mt-1 border-t border-[#171f32] flex items-center justify-between text-[10px] text-[#869397] font-mono">
            <span>ISRO-Doppler L4</span>
            <span className="text-[#4cd7f6]">P-Y-GNN v3.4</span>
          </div>
        </div>
      </aside>
    </>
  );
};
