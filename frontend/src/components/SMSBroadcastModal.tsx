import React, { useState } from 'react';
import { soundFx } from '../utils/audioAlert';

interface SMSBroadcastModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SMSBroadcastModal: React.FC<SMSBroadcastModalProps> = ({ isOpen, onClose }) => {
  const [broadcastTarget, setBroadcastTarget] = useState('Sector 4 & 5 (Tupul, Noney & Awangkhul)');
  const [priorityLevel, setPriorityLevel] = useState('PRESIDENTIAL / HIGH ALERT FLASH');
  const [messageBody, setMessageBody] = useState(
    'URGENT EVACUATION ADVISORY: NH-37 Km 42 is blocked due to catastrophic slope rupture. Stage-4 Evacuation in effect for Tupul Valley. Divert immediately to Noney Relief Center via Old Cachar Bypass. Do not cross Ije River bed. - Manipur DMA'
  );
  const [isBroadcasting, setIsBroadcasting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  if (!isOpen) return null;

  const handleSend = () => {
    soundFx.playRadarPing();
    setIsBroadcasting(true);

    setTimeout(() => {
      setIsBroadcasting(false);
      setIsCompleted(true);

      setTimeout(() => {
        setIsCompleted(false);
        onClose();
      }, 1800);
    }, 900);
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#060e20]/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#171f32] w-full max-w-lg p-5 sm:p-6 rounded-2xl border border-[#222a3d] shadow-2xl flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#ffb3ad] text-[24px]">campaign</span>
            <span className="font-headline text-lg sm:text-xl text-[#dae2fc] font-bold">
              Emergency Cell Broadcast Dispatcher
            </span>
          </div>
          <button type="button" onClick={onClose} className="text-[#bcc9cd] hover:text-white p-1">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {isCompleted ? (
          <div className="p-8 flex flex-col items-center justify-center text-center gap-3">
            <div className="w-16 h-16 rounded-full bg-[#10b981]/20 text-[#10b981] flex items-center justify-center">
              <span className="material-symbols-outlined text-[36px]">cell_tower</span>
            </div>
            <span className="font-headline text-xl font-bold text-[#dae2fc]">
              SMS Transmitted Successfully!
            </span>
            <span className="font-body text-xs text-[#bcc9cd]">
              Dispatched to 4,200 registered subscribers via Cell Broadcast Channel 4370.
            </span>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {/* Recipient Target */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Geofenced Target Area
              </label>
              <select
                value={broadcastTarget}
                onChange={(e) => setBroadcastTarget(e.target.value)}
                className="bg-[#0b1326] text-[#dae2fc] font-mono text-xs p-2.5 rounded border border-[#222a3d]"
              >
                <option>Sector 4 & 5 (Tupul, Noney & Awangkhul) • 4,200 recipients</option>
                <option>Entire NH-37 Corridor (Imphal West to Jiribam) • 18,500 recipients</option>
                <option>Imphal Valley Gateways Only • 8,900 recipients</option>
              </select>
            </div>

            {/* Alert Priority */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Channel Priority
              </label>
              <select
                value={priorityLevel}
                onChange={(e) => setPriorityLevel(e.target.value)}
                className="bg-[#0b1326] text-[#ffb3ad] font-mono text-xs p-2.5 rounded border border-[#a40217]/50"
              >
                <option>PRESIDENTIAL / HIGH ALERT FLASH (Bypasses Do-Not-Disturb)</option>
                <option>ADVISORY TRAFFIC ROUTING (Standard SMS Gateway)</option>
              </select>
            </div>

            {/* Message Body */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                SMS Content (Multilingual Broadcast: English + Manipuri Meiteilon)
              </label>
              <textarea
                rows={4}
                value={messageBody}
                onChange={(e) => setMessageBody(e.target.value)}
                className="bg-[#0b1326] text-[#dae2fc] font-body text-xs p-2.5 rounded border border-[#222a3d] focus:outline-none focus:border-[#4cd7f6]"
              />
            </div>

            {/* Network Info */}
            <div className="p-3 bg-[#131b2e] rounded border border-[#222a3d] flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
                <span className="text-[#dae2fc]">DoT Emergency Cell Broadcast Gateway</span>
              </div>
              <span className="text-[#4cd7f6]">Active</span>
            </div>

            {/* Buttons */}
            <div className="flex items-center justify-end gap-3 mt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 font-mono text-xs text-[#bcc9cd] hover:text-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={isBroadcasting}
                className="px-4 py-2 bg-[#a40217] hover:bg-[#ef4444] text-white font-mono text-xs font-bold uppercase rounded flex items-center gap-1.5 shadow-lg transition-all cursor-pointer disabled:opacity-50"
              >
                {isBroadcasting ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                    <span>Broadcasting...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">campaign</span>
                    <span>Broadcast Alert Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
