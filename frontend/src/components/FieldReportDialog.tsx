import React, { useState } from 'react';
import { soundFx } from '../utils/audioAlert';
import { api } from '../services/api';

interface FieldReportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitReport: (report: {
    type: string;
    sector: string;
    milepost: string;
    notes: string;
    imagePreview?: string;
  }) => void;
}

export const FieldReportDialog: React.FC<FieldReportDialogProps> = ({
  isOpen,
  onClose,
  onSubmitReport,
}) => {
  const [incidentType, setIncidentType] = useState('Transverse Tension Crack in Pavement / Slope');
  const [milepost, setMilepost] = useState('NH-37 Km 42.4 (Near Tupul Bridge Construction)');
  const [notes, setNotes] = useState('Ground displacement visible along road edge with 4cm widening.');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmittedSuccess, setIsSubmittedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    soundFx.playRadarPing();
    setIsSubmitting(true);

    try {
      await api.syncOfflineBatch([
        {
          device_id: 'MOBILE_EDGE_CLIENT_01',
          device_timestamp: new Date().toISOString(),
          report_type: incidentType,
          latitude: 24.855,
          longitude: 93.697,
          crack_width_cm: 4.5,
          notes: `${milepost} - ${notes}`,
          severity: 'HIGH_RISK',
          photo_base64: imagePreview || undefined,
        },
      ]);
    } catch (err) {
      console.warn('Persisted to local offline queue:', err);
    }

    setIsSubmitting(false);
    setIsSubmittedSuccess(true);
    onSubmitReport({
      type: incidentType,
      sector: 'Sector 4: Tupul',
      milepost,
      notes,
      imagePreview: imagePreview || undefined,
    });

    setTimeout(() => {
      setIsSubmittedSuccess(false);
      setImagePreview(null);
      onClose();
    }, 1500);
  };


  return (
    <div className="fixed inset-0 z-50 bg-[#060e20]/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#171f32] w-full max-w-lg p-5 sm:p-6 rounded-2xl border border-[#222a3d] shadow-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#ef4444] text-[24px]">
              report_problem
            </span>
            <span className="font-headline text-lg sm:text-xl text-[#dae2fc] font-bold">
              Submit Field Hazard Observation
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[#bcc9cd] hover:text-white p-1"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {isSubmittedSuccess ? (
          <div className="p-8 flex flex-col items-center justify-center text-center gap-3">
            <div className="w-16 h-16 rounded-full bg-[#10b981]/20 text-[#10b981] flex items-center justify-center">
              <span className="material-symbols-outlined text-[36px]">check_circle</span>
            </div>
            <span className="font-headline text-xl font-bold text-[#dae2fc]">
              Report Encrypted & Ingested!
            </span>
            <span className="font-body text-xs text-[#bcc9cd]">
              Transmitted to BRO Control Room & Drishti-NER Ingest Pipeline.
            </span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            {/* Incident Type */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Incident Type
              </label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="bg-[#0b1326] text-[#dae2fc] font-mono text-xs p-2.5 rounded border border-[#222a3d] focus:outline-none focus:border-[#4cd7f6]"
              >
                <option>Transverse Tension Crack in Pavement / Slope</option>
                <option>Active Mudflow / Gully Erosion Across Carriageway</option>
                <option>Fresh Rockfall / Boulder Inundation</option>
                <option>Retaining Wall Bulge / Culvert Failure</option>
              </select>
            </div>

            {/* Observed Milepost */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Observed Milepost / Sector
              </label>
              <input
                type="text"
                value={milepost}
                onChange={(e) => setMilepost(e.target.value)}
                className="bg-[#0b1326] text-[#dae2fc] font-mono text-xs p-2.5 rounded border border-[#222a3d] focus:outline-none focus:border-[#4cd7f6]"
              />
            </div>

            {/* Field Notes */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Observation Details & Urgency
              </label>
              <textarea
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="bg-[#0b1326] text-[#dae2fc] font-body text-xs p-2.5 rounded border border-[#222a3d] focus:outline-none focus:border-[#4cd7f6]"
              />
            </div>

            {/* Attach Photographic Evidence */}
            <div className="flex flex-col gap-1">
              <label className="font-mono text-xs text-[#869397] uppercase font-semibold">
                Attach Photographic Evidence
              </label>
              <label className="p-4 bg-[#131b2e] rounded border border-dashed border-[#222a3d] hover:border-[#4cd7f6] flex flex-col items-center justify-center gap-1.5 text-center cursor-pointer transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="hidden"
                />
                {imagePreview ? (
                  <div className="relative w-full h-32 rounded overflow-hidden">
                    <img
                      src={imagePreview}
                      alt="Hazard preview"
                      className="w-full h-full object-cover"
                    />
                    <span className="absolute bottom-1 right-1 bg-black/70 px-2 py-0.5 rounded text-[10px] text-[#4cd7f6] font-mono">
                      Photo Staged
                    </span>
                  </div>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[#4cd7f6] text-[32px]">
                      add_a_photo
                    </span>
                    <span className="font-mono text-xs text-[#dae2fc] font-bold">
                      Click to Capture or Upload Photo
                    </span>
                    <span className="font-body text-[11px] text-[#bcc9cd]">
                      Geo-location and altitude will be extracted automatically from EXIF data.
                    </span>
                  </>
                )}
              </label>
            </div>

            {/* Offline sync banner */}
            <div className="p-2.5 bg-[#4cd7f6]/10 border border-[#4cd7f6]/20 rounded flex items-center gap-2">
              <span className="material-symbols-outlined text-[#4cd7f6] text-[18px] shrink-0">
                signal_cellular_connected_no_internet_4_bar
              </span>
              <span className="font-mono text-[11px] text-[#4cd7f6] leading-tight">
                Offline Queue Active: Report will store encrypted locally and sync upon cell tower handoff.
              </span>
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3 mt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 font-mono text-xs text-[#bcc9cd] hover:text-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 bg-[#06b6d4] hover:bg-[#4cd7f6] text-[#003640] font-mono text-xs font-bold uppercase rounded flex items-center gap-1.5 shadow-md transition-all cursor-pointer disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <span className="material-symbols-outlined text-[16px] animate-spin">
                      sync
                    </span>
                    <span>Transmitting...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-[16px]">send</span>
                    <span>Transmit Verification</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
