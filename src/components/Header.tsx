import React, { useState, useEffect } from 'react';
import { soundFx } from '../utils/audioAlert';

interface HeaderProps {
  appMode: 'control_room' | 'citizen';
  setAppMode: (mode: 'control_room' | 'citizen') => void;
  hazardText?: string;
  threatStage?: string;
  onOpenReportModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  appMode,
  setAppMode,
  hazardText = 'CURRENT HAZARD: HIGH ALERT (NH-37 KM 42 BLOCKED)',
  threatStage = 'STAGE-4 EVAC',
  onOpenReportModal,
}) => {
  const [isAudioAlertActive, setIsAudioAlertActive] = useState(false);
  const [istTime, setIstTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Format as IST (UTC+5:30)
      const options: Intl.DateTimeFormatOptions = {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      };
      setIstTime(new Intl.DateTimeFormat('en-GB', options).format(now));
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleSound = () => {
    const playing = soundFx.toggleEmergencyAlarm();
    setIsAudioAlertActive(playing);
  };

  return (
    <header className="fixed top-0 left-0 lg:left-64 right-0 z-40 bg-[#060e20]/95 backdrop-blur-xl border-b border-[#222a3d] shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
      <div className="h-20 w-full px-4 lg:px-6 flex items-center justify-between gap-3">
        {/* Brand & Subtitle */}
        <div className="flex items-center gap-3">
          <img
            src="https://lh3.googleusercontent.com/aida/AEtjO1Wi4tEsPN-qUqpFFYspCFECFeVDHuIrG4EiYnwU2AONznkf9ux_Oz0eKfKRwN5GRvH2oyGQbdyLjt-WBvMAxfmM6jLxnnELVj2dyyc-5mgsdFA9I9Qx-kagBBbXBtzDkKEtWY9xS44Nkc4vCiQkls8QNNvC4sKq4VgSQe6F96nPKbwdfYo0BZzuspRsZlLFaeHfOE96h6ubrM5eYcvcTqYJYxoY2IisE2Jd8tomrcb7SM5O85CTZso0Ibg"
            alt="Drishti-NER Geospatial Radar Logo"
            className="h-9 w-auto object-contain drop-shadow-[0_0_8px_rgba(76,215,246,0.5)]"
          />
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-headline text-lg sm:text-xl text-[#dae2fc] tracking-tight font-bold">
                DRISHTI-NER
              </span>
              <span className="font-mono text-xs text-[#4cd7f6] uppercase tracking-wider font-semibold">
                | AI Early Warning
              </span>
            </div>
            <span className="font-body text-xs text-[#bcc9cd] tracking-wide">
              NH-37 Corridor Surveillance (Imphal–Jiribam)
            </span>
          </div>
        </div>

        {/* Hazard Alert Banner (Middle) */}
        <div className="hidden xl:flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-[#a40217]/25 border border-[#ef4444]/40 rounded shadow-[0_0_15px_rgba(239,68,68,0.25)]">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ef4444] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#ef4444]"></span>
            </span>
            <span className="font-mono text-xs text-[#ffb3ad] font-bold tracking-wider uppercase">
              {hazardText}
            </span>
            <button
              onClick={toggleSound}
              className={`ml-1 p-1 rounded transition-colors flex items-center ${
                isAudioAlertActive
                  ? 'bg-[#ef4444] text-white animate-pulse'
                  : 'text-[#ffb3ad] hover:text-white hover:bg-[#a40217]/50'
              }`}
              title={isAudioAlertActive ? 'Mute Klaxon Alert' : 'Trigger Audio Hazard Klaxon'}
              type="button"
            >
              <span className="material-symbols-outlined text-[17px]">
                {isAudioAlertActive ? 'volume_up' : 'volume_off'}
              </span>
            </button>
          </div>
        </div>

        {/* Right Section: IST Clock, Auto-Sync & Mode Switch */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex flex-col text-right">
            <div className="flex items-center justify-end gap-1.5">
              <span className="inline-block w-2 h-2 rounded-full bg-[#4cd7f6] animate-pulse"></span>
              <span className="font-mono text-xs text-[#4cd7f6] font-semibold">
                Connected | Auto-sync Active
              </span>
            </div>
            <span className="font-mono text-[11px] text-[#bcc9cd]">
              {istTime || '14:28:10'} IST | IMD Doppler Active
            </span>
          </div>

          {/* Mode Switcher Pill */}
          <div className="flex items-center p-1 bg-[#171f32] border border-[#222a3d] rounded">
            <button
              type="button"
              onClick={() => setAppMode('citizen')}
              className={`px-2.5 py-1 font-mono text-xs rounded transition-all font-semibold ${
                appMode === 'citizen'
                  ? 'bg-[#06b6d4] text-[#003640] shadow-sm'
                  : 'text-[#bcc9cd] hover:text-[#dae2fc]'
              }`}
            >
              Citizen
            </button>
            <button
              type="button"
              onClick={() => setAppMode('control_room')}
              className={`px-2.5 py-1 font-mono text-xs rounded transition-all font-semibold ${
                appMode === 'control_room'
                  ? 'bg-[#06b6d4] text-[#003640] shadow-sm'
                  : 'text-[#bcc9cd] hover:text-[#dae2fc]'
              }`}
            >
              Control Room
            </button>
          </div>

          {/* Quick Action Button: Field Report */}
          <button
            onClick={onOpenReportModal}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-[#a40217]/80 hover:bg-[#a40217] text-[#ffdad6] text-xs font-mono font-semibold rounded border border-[#ef4444]/40 transition-colors shadow-sm"
            title="Submit field landslip report"
            type="button"
          >
            <span className="material-symbols-outlined text-[16px]">crisis_alert</span>
            <span className="uppercase">Report Slide</span>
          </button>
        </div>
      </div>
    </header>
  );
};
