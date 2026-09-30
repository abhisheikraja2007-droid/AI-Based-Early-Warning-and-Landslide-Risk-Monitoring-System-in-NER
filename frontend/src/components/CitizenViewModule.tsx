import React from 'react';
import { soundFx } from '../utils/audioAlert';

interface CitizenViewProps {
  onOpenReportModal: () => void;
  onNavigateDetour: () => void;
}

export const CitizenViewModule: React.FC<CitizenViewProps> = ({
  onOpenReportModal,
  onNavigateDetour,
}) => {
  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full py-4">
      {/* 1. BIG EMERGENCY STATUS BANNER */}
      <div className="bg-[#a40217] p-6 rounded-2xl border-2 border-[#ef4444] shadow-[0_0_30px_rgba(239,68,68,0.35)] flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-[36px] text-white animate-bounce">
              warning
            </span>
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-xs text-[#ffdad6] uppercase font-bold tracking-widest">
              OFFICIAL MANIPUR STATE HIGHWAY ADVISORY
            </span>
            <span className="font-headline text-2xl sm:text-3xl font-extrabold text-white leading-tight">
              NH-37 IS CLOSED AT KM 42 (TUPUL)
            </span>
            <span className="font-body text-sm text-[#ffdad6] mt-1">
              Active massive rockfall and slope liquefaction. Do not attempt to cross. Use the designated safe detour.
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={onNavigateDetour}
          className="px-5 py-3 rounded-xl bg-white text-[#68000a] font-headline text-sm font-bold uppercase tracking-wider shadow-lg hover:bg-[#ffdad6] transition-all shrink-0 cursor-pointer"
        >
          View Safe Detour (35.9 km)
        </button>
      </div>

      {/* 2. THREE QUICK CITIZEN ACTION CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Action 1: Nearest Shelter */}
        <div className="bg-[#131b2e] p-5 rounded-xl border border-[#222a3d] flex flex-col justify-between gap-3 shadow-lg">
          <div className="flex flex-col">
            <div className="w-10 h-10 rounded-lg bg-[#4cd7f6]/20 text-[#4cd7f6] flex items-center justify-center mb-2">
              <span className="material-symbols-outlined text-[24px]">night_shelter</span>
            </div>
            <span className="font-headline text-lg font-bold text-[#dae2fc]">
              Nearest Safe Shelter
            </span>
            <span className="font-body text-xs text-[#bcc9cd] mt-1">
              Noney Community Health Center (142 beds available, medical care & food).
            </span>
          </div>
          <button
            type="button"
            onClick={onNavigateDetour}
            className="w-full py-2 bg-[#222a3d] hover:bg-[#31394d] text-[#4cd7f6] font-mono text-xs font-bold rounded transition-colors text-center cursor-pointer"
          >
            Get Directions →
          </button>
        </div>

        {/* Action 2: Report Fissures or Falling Rocks */}
        <div className="bg-[#131b2e] p-5 rounded-xl border border-[#222a3d] flex flex-col justify-between gap-3 shadow-lg">
          <div className="flex flex-col">
            <div className="w-10 h-10 rounded-lg bg-[#ef4444]/20 text-[#ffb3ad] flex items-center justify-center mb-2">
              <span className="material-symbols-outlined text-[24px]">photo_camera</span>
            </div>
            <span className="font-headline text-lg font-bold text-[#dae2fc]">
              Report Landslip
            </span>
            <span className="font-body text-xs text-[#bcc9cd] mt-1">
              Saw ground cracks or boulders? Send GPS photo to alert engineers immediately. Works offline!
            </span>
          </div>
          <button
            type="button"
            onClick={onOpenReportModal}
            className="w-full py-2 bg-[#a40217] hover:bg-[#ef4444] text-white font-mono text-xs font-bold rounded transition-colors text-center cursor-pointer"
          >
            Submit Observation →
          </button>
        </div>

        {/* Action 3: 24x7 Emergency Helplines */}
        <div className="bg-[#131b2e] p-5 rounded-xl border border-[#222a3d] flex flex-col justify-between gap-3 shadow-lg">
          <div className="flex flex-col">
            <div className="w-10 h-10 rounded-lg bg-[#10b981]/20 text-[#10b981] flex items-center justify-center mb-2">
              <span className="material-symbols-outlined text-[24px]">call</span>
            </div>
            <span className="font-headline text-lg font-bold text-[#dae2fc]">
              Emergency Helplines
            </span>
            <div className="flex flex-col gap-1 text-xs font-mono mt-1 text-[#bcc9cd]">
              <div>National Disaster: <span className="text-white font-bold">112</span></div>
              <div>BRO Task Force: <span className="text-white font-bold">0385-2443441</span></div>
              <div>Noney Control Post: <span className="text-white font-bold">98620-11234</span></div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => soundFx.playRadarPing()}
            className="w-full py-2 bg-[#222a3d] hover:bg-[#31394d] text-[#10b981] font-mono text-xs font-bold rounded transition-colors text-center cursor-pointer"
          >
            Direct Emergency Dial
          </button>
        </div>
      </div>

      {/* 3. SAFETY GUIDANCE & ADVISORY */}
      <div className="bg-[#131b2e] p-6 rounded-2xl border border-[#222a3d] flex flex-col gap-4 shadow-xl">
        <span className="font-headline text-lg font-bold text-[#dae2fc]">
          Monsoon Safety Guidelines for NH-37 Travelers
        </span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-body text-[#bcc9cd]">
          <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex items-start gap-2.5">
            <span className="material-symbols-outlined text-[#4cd7f6] text-[20px] shrink-0">
              water
            </span>
            <div>
              <span className="text-white font-bold block mb-0.5">Sudden Stream Changes</span>
              If streams or culverts turn turbid brown with floating branches, evacuate upslope immediately.
            </div>
          </div>

          <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex items-start gap-2.5">
            <span className="material-symbols-outlined text-[#ffb95f] text-[20px] shrink-0">
              hearing
            </span>
            <div>
              <span className="text-white font-bold block mb-0.5">Rumbling Noises</span>
              Unusual sounds like cracking trees or boulder collisions mean an active debris flow is in motion.
            </div>
          </div>

          <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex items-start gap-2.5">
            <span className="material-symbols-outlined text-[#ef4444] text-[20px] shrink-0">
              directions_car
            </span>
            <div>
              <span className="text-white font-bold block mb-0.5">Do Not Stop Under Cut Slopes</span>
              Never park or idle beneath freshly excavated highway cuts during heavy rain.
            </div>
          </div>

          <div className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex items-start gap-2.5">
            <span className="material-symbols-outlined text-[#10b981] text-[20px] shrink-0">
              sms
            </span>
            <div>
              <span className="text-white font-bold block mb-0.5">Cellular Emergency Broadcasts</span>
              Emergency SMS alerts are broadcast via government cell broadcast towers with no internet required.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
