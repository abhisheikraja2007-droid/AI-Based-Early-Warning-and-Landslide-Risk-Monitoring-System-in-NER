import React, { useState, useEffect } from 'react';
import { SAR_UNITS, INITIAL_INCIDENT_REPORTS } from '../data/mockTelemetry';
import { IncidentReport } from '../types/telemetry';
import { soundFx } from '../utils/audioAlert';
import { api } from '../services/api';

interface DispatchModuleProps {
  onBroadcastSMS: () => void;
  onOpenReportModal: () => void;
}

export const DispatchModule: React.FC<DispatchModuleProps> = ({
  onBroadcastSMS,
  onOpenReportModal,
}) => {
  const [incidents, setIncidents] = useState<IncidentReport[]>(INITIAL_INCIDENT_REPORTS);
  const [sarUnits] = useState(SAR_UNITS);
  const [selectedIncident, setSelectedIncident] = useState<IncidentReport>(INITIAL_INCIDENT_REPORTS[0]);

  useEffect(() => {
    const loadRealReports = async () => {
      try {
        const realReports = await api.getCitizenReports();
        if (realReports && realReports.length > 0) {
          const mapped: IncidentReport[] = realReports.map((r: any, idx: number) => ({
            id: r.device_report_id || `RPT-LIVE-${idx + 1}`,
            timestamp: r.device_timestamp || new Date().toISOString(),
            type: r.report_type || 'Tension Crack Detected',
            sector: 'Sector 4: Tupul (NH-37)',
            kmMarker: 42.4,
            status: 'VERIFIED_ACTIVE',
            reportedBy: r.device_id || 'Citizen Mobile Edge App',
            notes: r.notes || `Slope tension fissure observed. Severity: ${r.severity || 'HIGH'}`,
            coords: `${r.latitude ? r.latitude.toFixed(3) : '24.855'}°N, ${r.longitude ? r.longitude.toFixed(3) : '93.697'}°E`,
            offlineSynced: true,
          }));
          setIncidents([...mapped, ...INITIAL_INCIDENT_REPORTS]);
          setSelectedIncident(mapped[0]);
        }
      } catch (err) {
        console.warn('Using baseline reports:', err);
      }
    };
    loadRealReports();
  }, []);


  // Action checklist toggles
  const [actionItems, setActionItems] = useState([
    { id: 'act-1', text: 'Enforce NH-37 Km 38 Police Barricade at Sinam', completed: true },
    { id: 'act-2', text: 'Activate ISRO Bhuvan Bypass Signage towards Noney', completed: true },
    { id: 'act-3', text: 'Deploy BRO CAT 330D Earthmovers to clear Ije River bed', completed: true },
    { id: 'act-4', text: 'Issue Stage-4 Evacuation Order for 144 Tupul households', completed: true },
    { id: 'act-5', text: 'Stage IAF MI-17 Helipad at Leikop for medical airlift', completed: false },
    { id: 'act-6', text: 'Maintain Emergency Satellite Mesh Relay at Tupul Post', completed: true },
  ]);

  const toggleAction = (id: string) => {
    soundFx.playRadarPing();
    setActionItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, completed: !item.completed } : item))
    );
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Module Header Bar */}
      <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-wrap items-center justify-between gap-3 shadow-lg">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
              // DISPATCH & INCIDENT COMMAND
            </span>
            <span className="px-2 py-0.5 rounded bg-[#ef4444]/20 text-[#ffb3ad] font-mono text-[10px] font-bold">
              STAGE-4 DISASTER ACTIVATED
            </span>
          </div>
          <span className="font-headline text-xl text-[#dae2fc] font-bold">
            Search & Rescue (SAR), BRO Heavy Machinery & Emergency Broadcast
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onBroadcastSMS}
            className="px-3.5 py-2 rounded bg-[#06b6d4] hover:bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold uppercase flex items-center gap-2 shadow-lg transition-all cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">campaign</span>
            <span>Trigger Mass SMS Broadcast</span>
          </button>
          <button
            type="button"
            onClick={onOpenReportModal}
            className="px-3 py-2 rounded bg-[#222a3d] hover:bg-[#31394d] text-[#dae2fc] font-mono text-xs font-bold uppercase flex items-center gap-1.5 border border-[#2d3449] transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">add_location_alt</span>
            <span>New Incident Log</span>
          </button>
        </div>
      </div>

      {/* Grid: Active Incidents & Deployed SAR Units */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* Left Column: Active Reported Incidents (col-span-6) */}
        <div className="xl:col-span-6 flex flex-col gap-4">
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-3 shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // ACTIVE HAZARD DISPATCH LOG
              </span>
              <span className="font-mono text-xs text-[#869397]">
                {incidents.length} Reported Events
              </span>
            </div>

            <div className="flex flex-col gap-2">
              {incidents.map((inc) => {
                const isSelected = selectedIncident.id === inc.id;
                const isCritical = inc.status === 'VERIFIED_ACTIVE';

                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#171f32] border-[#4cd7f6] shadow-md'
                        : 'bg-[#131b2e] border-[#222a3d] hover:bg-[#171f32]'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-[#dae2fc]">
                            {inc.id}
                          </span>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                              isCritical
                                ? 'bg-[#a40217]/50 text-[#ffb3ad] animate-pulse'
                                : 'bg-[#e79400]/30 text-[#ffb95f]'
                            }`}
                          >
                            {inc.status}
                          </span>
                        </div>
                        <span className="font-headline text-sm font-semibold text-[#dae2fc] mt-1">
                          {inc.type}
                        </span>
                      </div>
                      <span className="font-mono text-[10px] text-[#869397]">{inc.timestamp}</span>
                    </div>

                    <p className="font-body text-xs text-[#bcc9cd] mt-2 line-clamp-2">{inc.notes}</p>

                    <div className="mt-2 pt-2 border-t border-[#222a3d] flex items-center justify-between text-[11px] font-mono text-[#869397]">
                      <span>{inc.sector} (Km {inc.kmMarker})</span>
                      <span className="text-[#4cd7f6]">{inc.coords}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Incident Action Plan Checklist */}
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-3 shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // INCIDENT ACTION PLAN (IAP) ENFORCEMENT
              </span>
              <span className="font-mono text-xs text-[#10b981] font-bold">
                {actionItems.filter((a) => a.completed).length}/{actionItems.length} Enforced
              </span>
            </div>

            <div className="flex flex-col gap-2">
              {actionItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggleAction(item.id)}
                  className="flex items-center gap-3 p-2.5 rounded bg-[#171f32] hover:bg-[#222a3d] border border-[#222a3d] text-left transition-colors cursor-pointer"
                >
                  <span
                    className={`material-symbols-outlined text-[20px] ${
                      item.completed ? 'text-[#10b981]' : 'text-[#869397]'
                    }`}
                  >
                    {item.completed ? 'check_box' : 'check_box_outline_blank'}
                  </span>
                  <span
                    className={`font-body text-xs flex-1 ${
                      item.completed ? 'text-[#dae2fc]' : 'text-[#869397]'
                    }`}
                  >
                    {item.text}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Deployed SAR Teams & Field Equipment (col-span-6) */}
        <div className="xl:col-span-6 flex flex-col gap-4">
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-3 shadow-xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                // DEPLOYED FIRST RESPONDERS & SAR ASSETS
              </span>
              <span className="font-mono text-xs text-[#10b981] font-bold">5 Units On-Grid</span>
            </div>

            <div className="grid grid-cols-1 gap-2.5">
              {sarUnits.map((unit) => (
                <div
                  key={unit.id}
                  className="p-3 bg-[#171f32] rounded-lg border border-[#222a3d] flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex flex-col">
                      <span className="font-headline text-sm font-bold text-[#dae2fc]">
                        {unit.name}
                      </span>
                      <span className="font-mono text-[11px] text-[#4cd7f6]">{unit.type}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-[#10b981]/20 text-[#10b981] font-mono text-[10px] font-bold">
                      {unit.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-[11px] font-mono text-[#bcc9cd] pt-1">
                    <div>
                      <span className="text-[#869397] block text-[9px] uppercase">Location</span>
                      <span>{unit.currentLocation}</span>
                    </div>
                    <div>
                      <span className="text-[#869397] block text-[9px] uppercase">Strength</span>
                      <span className="text-white font-bold">{unit.personnelCount} Personnel</span>
                    </div>
                    <div>
                      <span className="text-[#869397] block text-[9px] uppercase">Comms Channel</span>
                      <span className="text-[#4cd7f6]">{unit.contactFrequency}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Emergency Communications Relay Card */}
          <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-3 shadow-xl">
            <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
              // TACTICAL TELECOM & AIRLIFT STATUS
            </span>
            <div className="grid grid-cols-2 gap-3 font-mono text-xs">
              <div className="p-3 bg-[#171f32] rounded border border-[#222a3d] flex flex-col gap-1">
                <span className="text-[#869397] text-[10px] uppercase">Cell Tower Backup</span>
                <span className="text-[#10b981] font-bold">Airtel & Jio COW Operational</span>
                <span className="text-[#869397] text-[10px]">Tupul VSAT Solar-Powered</span>
              </div>
              <div className="p-3 bg-[#171f32] rounded border border-[#222a3d] flex flex-col gap-1">
                <span className="text-[#869397] text-[10px] uppercase">Medical Helivac</span>
                <span className="text-[#ffb95f] font-bold">Standby at Leikop</span>
                <span className="text-[#869397] text-[10px]">Ceiling: 8,000 ft (Rain Squalls)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
