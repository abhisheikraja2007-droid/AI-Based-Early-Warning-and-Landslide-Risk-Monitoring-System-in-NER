/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar, ModuleType } from './components/Sidebar';
import { CorridorMapModule } from './components/CorridorMapModule';
import { SensorArrayModule } from './components/SensorArrayModule';
import { AIForecastModule } from './components/AIForecastModule';
import { DispatchModule } from './components/DispatchModule';
import { SafeCorridorsModule } from './components/SafeCorridorsModule';
import { CitizenViewModule } from './components/CitizenViewModule';
import { FieldReportDialog } from './components/FieldReportDialog';
import { SMSBroadcastModal } from './components/SMSBroadcastModal';
import { SegmentDetailModal } from './components/SegmentDetailModal';
import { CorridorSegment } from './types/telemetry';
import { soundFx } from './utils/audioAlert';

export default function App() {
  const [activeModule, setActiveModule] = useState<ModuleType>('corridor-surveillance');
  const [appMode, setAppMode] = useState<'control_room' | 'citizen'>('control_room');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Modals
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isSMSModalOpen, setIsSMSModalOpen] = useState(false);
  const [selectedSegmentForModal, setSelectedSegmentForModal] = useState<CorridorSegment | null>(null);

  const handleOpenReportModal = () => {
    soundFx.playRadarPing();
    setIsReportModalOpen(true);
  };

  const handleNavigateToDetour = () => {
    soundFx.playRadarPing();
    setActiveModule('evacuation-routes');
  };

  const handleBroadcastSMS = () => {
    soundFx.playRadarPing();
    setIsSMSModalOpen(true);
  };

  const handleSelectSegment = (segment: CorridorSegment) => {
    soundFx.playRadarPing();
    setSelectedSegmentForModal(segment);
  };

  const handleSubmitNewReport = (report: {
    type: string;
    sector: string;
    milepost: string;
    notes: string;
    imagePreview?: string;
  }) => {
    // In control room or citizen mode, we can show a confirmation or log
    console.log('Ingested field hazard report:', report);
  };

  return (
    <div className="min-h-screen bg-[#0b1326] text-[#dae2fc] font-body selection:bg-[#4cd7f6]/30 selection:text-[#4cd7f6] flex flex-col">
      {/* Top Header Bar */}
      <Header
        appMode={appMode}
        setAppMode={(mode) => {
          soundFx.playRadarPing();
          setAppMode(mode);
        }}
        onOpenReportModal={handleOpenReportModal}
      />

      {/* Main App Container */}
      <div className="flex flex-1 pt-20">
        {/* Left Sidebar (visible on desktop or toggled on mobile) */}
        {appMode === 'control_room' && (
          <Sidebar
            activeModule={activeModule}
            setActiveModule={setActiveModule}
            isOpenMobile={isMobileSidebarOpen}
            setIsOpenMobile={setIsMobileSidebarOpen}
            porePressureRisk="HIGH RISK"
          />
        )}

        {/* Content Viewport */}
        <main
          className={`flex-1 min-h-[calc(100vh-5rem)] p-3 sm:p-4 lg:p-6 transition-all duration-200 ${
            appMode === 'control_room' ? 'lg:pl-64' : 'max-w-6xl mx-auto w-full'
          }`}
        >
          {/* Mobile module navigation switcher (when in control room on small screens) */}
          {appMode === 'control_room' && (
            <div className="lg:hidden flex items-center justify-between mb-4 p-2.5 bg-[#131b2e] rounded-lg border border-[#222a3d]">
              <button
                type="button"
                onClick={() => setIsMobileSidebarOpen(true)}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#222a3d] text-[#4cd7f6] rounded font-mono text-xs font-bold"
              >
                <span className="material-symbols-outlined text-[18px]">menu</span>
                <span>Operational Modules</span>
              </button>
              <span className="font-mono text-xs text-[#dae2fc] font-semibold uppercase">
                {activeModule.replace('-', ' ')}
              </span>
            </div>
          )}

          {/* Citizen Mode View */}
          {appMode === 'citizen' ? (
            <CitizenViewModule
              onOpenReportModal={handleOpenReportModal}
              onNavigateDetour={handleNavigateToDetour}
            />
          ) : (
            /* Control Room Operational Modules */
            <>
              {activeModule === 'corridor-surveillance' && (
                <CorridorMapModule
                  onOpenReportModal={handleOpenReportModal}
                  onNavigateToDetour={handleNavigateToDetour}
                  onBroadcastSMS={handleBroadcastSMS}
                  onSelectSegment={handleSelectSegment}
                />
              )}

              {activeModule === 'sensor-matrix' && <SensorArrayModule />}

              {activeModule === 'predictive-ai-models' && <AIForecastModule />}

              {activeModule === 'incident-dispatch' && (
                <DispatchModule
                  onBroadcastSMS={handleBroadcastSMS}
                  onOpenReportModal={handleOpenReportModal}
                />
              )}

              {activeModule === 'evacuation-routes' && <SafeCorridorsModule />}
            </>
          )}
        </main>
      </div>

      {/* Field Citizen Report Modal */}
      <FieldReportDialog
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        onSubmitReport={handleSubmitNewReport}
      />

      {/* SMS Mass Broadcast Modal */}
      <SMSBroadcastModal
        isOpen={isSMSModalOpen}
        onClose={() => setIsSMSModalOpen(false)}
      />

      {/* Segment Telemetry Detail Modal */}
      <SegmentDetailModal
        segment={selectedSegmentForModal}
        onClose={() => setSelectedSegmentForModal(null)}
        onNavigateDetour={handleNavigateToDetour}
      />
    </div>
  );
}
