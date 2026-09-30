import React, { useState } from 'react';
import { TelemetryNode } from '../types/telemetry';
import { TELEMETRY_NODES } from '../data/mockTelemetry';
import { soundFx } from '../utils/audioAlert';

export const SensorArrayModule: React.FC = () => {
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [nodes, setNodes] = useState<TelemetryNode[]>(TELEMETRY_NODES);
  const [selectedNode, setSelectedNode] = useState<TelemetryNode | null>(TELEMETRY_NODES[0]);
  const [simulatedPoreSpike, setSimulatedPoreSpike] = useState(false);

  const filteredNodes = nodes.filter((n) => {
    if (filterType !== 'all' && n.type !== filterType) return false;
    if (filterStatus !== 'all' && n.status !== filterStatus) return false;
    return true;
  });

  const handleSimulateThreshold = () => {
    soundFx.playRadarPing();
    setSimulatedPoreSpike(!simulatedPoreSpike);
    setNodes((prev) =>
      prev.map((node) => {
        if (node.id === 'NODE-PZ-42A') {
          return {
            ...node,
            value: simulatedPoreSpike ? 82.0 : 124.6,
            status: simulatedPoreSpike ? 'warning' : 'alert',
            readingsHistory: [...node.readingsHistory.slice(1), simulatedPoreSpike ? 82.0 : 124.6],
          };
        }
        return node;
      })
    );
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Module Header Bar */}
      <div className="bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-wrap items-center justify-between gap-3 shadow-lg">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
              // TELEMETRY SENSOR MATRIX
            </span>
            <span className="px-2 py-0.5 rounded bg-[#10b981]/20 text-[#10b981] font-mono text-[10px] font-bold">
              142/144 OPERATIONAL
            </span>
          </div>
          <span className="font-headline text-xl text-[#dae2fc] font-bold">
            Real-Time Geotechnical & Hydrometeorological Sensors
          </span>
        </div>

        {/* Action button to test sensor alert */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleSimulateThreshold}
            className={`px-3 py-1.5 rounded font-mono text-xs font-bold uppercase transition-all flex items-center gap-1.5 cursor-pointer ${
              simulatedPoreSpike
                ? 'bg-[#ef4444] text-white shadow-[0_0_12px_rgba(239,68,68,0.5)]'
                : 'bg-[#222a3d] hover:bg-[#31394d] text-[#ffb3ad] border border-[#ef4444]/30'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">sensors_off</span>
            <span>{simulatedPoreSpike ? 'Reset Sensor Test' : 'Inject Pore Water Spike'}</span>
          </button>
        </div>
      </div>

      {/* Top Filter & Summary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-3">
        {/* Filters */}
        <div className="lg:col-span-3 bg-[#131b2e] p-3 rounded-xl border border-[#222a3d] flex flex-wrap items-center gap-2">
          <span className="font-mono text-xs text-[#869397] mr-2">Filter Type:</span>
          {['all', 'Piezometer', 'InSAR Reflector', 'Doppler Rain Gauge', 'Tiltmeter', 'SMAP Soil Probe'].map(
            (t) => (
              <button
                key={t}
                type="button"
                onClick={() => setFilterType(t)}
                className={`px-2.5 py-1 rounded font-mono text-xs transition-colors cursor-pointer ${
                  filterType === t
                    ? 'bg-[#4cd7f6] text-[#003640] font-bold'
                    : 'bg-[#171f32] text-[#bcc9cd] hover:bg-[#222a3d]'
                }`}
              >
                {t === 'all' ? 'All Types' : t}
              </button>
            )
          )}

          <div className="h-5 w-px bg-[#222a3d] mx-2 hidden sm:block" />

          <span className="font-mono text-xs text-[#869397] mr-1">Status:</span>
          {['all', 'alert', 'warning', 'active'].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setFilterStatus(s)}
              className={`px-2 py-1 rounded font-mono text-xs transition-colors uppercase cursor-pointer ${
                filterStatus === s
                  ? s === 'alert'
                    ? 'bg-[#ef4444] text-white font-bold'
                    : s === 'warning'
                    ? 'bg-[#ffb95f] text-black font-bold'
                    : 'bg-[#10b981] text-black font-bold'
                  : 'bg-[#171f32] text-[#bcc9cd] hover:bg-[#222a3d]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Node stats */}
        <div className="bg-[#131b2e] p-3 rounded-xl border border-[#222a3d] flex items-center justify-between">
          <div className="flex flex-col">
            <span className="font-mono text-[10px] text-[#869397] uppercase">Battery Health Avg</span>
            <span className="font-mono text-base font-bold text-[#10b981]">91.4% Solar-Fed</span>
          </div>
          <div className="flex flex-col text-right">
            <span className="font-mono text-[10px] text-[#869397] uppercase">Data Frequency</span>
            <span className="font-mono text-base font-bold text-[#4cd7f6]">Every 10 sec</span>
          </div>
        </div>
      </div>

      {/* Main Split: Node Table & Detail View */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        {/* Node List Table (col-span-8) */}
        <div className="xl:col-span-8 bg-[#131b2e] rounded-xl border border-[#222a3d] overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#171f32] text-[#869397] uppercase border-b border-[#222a3d]">
                <tr>
                  <th className="py-3 px-4">Node ID & Type</th>
                  <th className="py-3 px-4">Location / Sector</th>
                  <th className="py-3 px-4">Current Value</th>
                  <th className="py-3 px-4">Threshold</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Battery</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#222a3d]">
                {filteredNodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  const isAlert = node.status === 'alert';
                  const isWarning = node.status === 'warning';

                  return (
                    <tr
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className={`hover:bg-[#171f32]/80 transition-colors cursor-pointer ${
                        isSelected ? 'bg-[#222a3d]/80' : ''
                      }`}
                    >
                      <td className="py-3 px-4">
                        <div className="flex flex-col">
                          <span className="font-bold text-[#dae2fc]">{node.id}</span>
                          <span className="text-[10px] text-[#4cd7f6]">{node.type}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-col">
                          <span className="text-[#dae2fc]">{node.location}</span>
                          <span className="text-[10px] text-[#869397]">{node.sector}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-baseline gap-1">
                          <span
                            className={`font-bold text-sm ${
                              isAlert ? 'text-[#ffb3ad]' : isWarning ? 'text-[#ffb95f]' : 'text-[#10b981]'
                            }`}
                          >
                            {node.value}
                          </span>
                          <span className="text-[10px] text-[#869397]">{node.unit}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-[#869397]">
                        {node.threshold} {node.unit}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded uppercase text-[10px] font-bold ${
                            isAlert
                              ? 'bg-[#a40217]/50 text-[#ffb3ad] border border-[#ef4444]/40 animate-pulse'
                              : isWarning
                              ? 'bg-[#e79400]/30 text-[#ffb95f] border border-[#ffb95f]/40'
                              : 'bg-[#10b981]/20 text-[#10b981]'
                          }`}
                        >
                          {node.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-[14px] text-[#10b981]">
                            battery_charging_full
                          </span>
                          <span className="text-[#bcc9cd]">{node.batteryPct}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          type="button"
                          className="px-2 py-1 bg-[#222a3d] hover:bg-[#31394d] text-[#4cd7f6] rounded text-[10px] transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Node Real-time Telemetry Card (col-span-4) */}
        {selectedNode && (
          <div className="xl:col-span-4 bg-[#131b2e] p-4 rounded-xl border border-[#222a3d] flex flex-col gap-4 shadow-xl">
            <div className="flex items-start justify-between">
              <div className="flex flex-col">
                <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                  // TELEMETRY OSCILLOSCOPE
                </span>
                <span className="font-headline text-lg text-[#dae2fc] font-bold">
                  {selectedNode.id}
                </span>
                <span className="font-body text-xs text-[#bcc9cd]">{selectedNode.location}</span>
              </div>
              <span
                className={`px-2 py-0.5 rounded uppercase text-xs font-mono font-bold ${
                  selectedNode.status === 'alert'
                    ? 'bg-[#ef4444] text-white animate-pulse'
                    : selectedNode.status === 'warning'
                    ? 'bg-[#ffb95f] text-black'
                    : 'bg-[#10b981] text-black'
                }`}
              >
                {selectedNode.status}
              </span>
            </div>

            {/* Metric Big Display */}
            <div className="p-3 bg-[#171f32] rounded border border-[#222a3d] flex items-center justify-between">
              <div className="flex flex-col">
                <span className="font-mono text-[10px] text-[#869397] uppercase">Current Level</span>
                <span className="font-headline text-2xl font-bold text-[#dae2fc]">
                  {selectedNode.value}{' '}
                  <span className="font-mono text-xs text-[#869397] font-normal">
                    {selectedNode.unit}
                  </span>
                </span>
              </div>
              <div className="flex flex-col text-right">
                <span className="font-mono text-[10px] text-[#869397] uppercase">Threshold Cutoff</span>
                <span className="font-mono text-sm font-bold text-[#ffb3ad]">
                  {selectedNode.threshold} {selectedNode.unit}
                </span>
              </div>
            </div>

            {/* Sparkline Visualizer */}
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between font-mono text-[11px] text-[#869397]">
                <span>Historical Sampling Trend (Last 1 Hour)</span>
                <span className="text-[#4cd7f6] uppercase font-bold">{selectedNode.trend}</span>
              </div>
              <div className="h-28 w-full bg-[#060e20] p-2 rounded border border-[#222a3d] flex items-end gap-2">
                {selectedNode.readingsHistory.map((val, idx) => {
                  const maxVal = Math.max(...selectedNode.readingsHistory, selectedNode.threshold);
                  const heightPct = Math.min(100, Math.round((val / (maxVal * 1.15)) * 100));
                  const isOver = val >= selectedNode.threshold;

                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                      <span className="font-mono text-[9px] text-[#869397]">{val}</span>
                      <div
                        className={`w-full rounded-t transition-all duration-300 ${
                          isOver ? 'bg-[#ef4444]' : 'bg-[#4cd7f6]'
                        }`}
                        style={{ height: `${heightPct}%` }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Calibration & Sensor Specifications */}
            <div className="flex flex-col gap-2 p-3 bg-[#171f32] rounded border border-[#222a3d] text-xs font-mono">
              <span className="text-[#4cd7f6] font-bold">// HARDWARE SPECIFICATIONS</span>
              <div className="flex justify-between text-[#bcc9cd]">
                <span>Telemetry Uplink:</span>
                <span className="text-white">LoRaWAN + ISRO GSAT-7A</span>
              </div>
              <div className="flex justify-between text-[#bcc9cd]">
                <span>Sampling Resolution:</span>
                <span className="text-white">0.05 kPa / 16-bit ADC</span>
              </div>
              <div className="flex justify-between text-[#bcc9cd]">
                <span>Sensor Depth:</span>
                <span className="text-white">18.5 meters in-borehole</span>
              </div>
              <div className="flex justify-between text-[#bcc9cd]">
                <span>Last Calibration:</span>
                <span className="text-[#10b981]">Yesterday 06:00 IST</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
