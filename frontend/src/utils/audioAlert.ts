// Web Audio API Synthesizer for Tactical Radar and Emergency Landslide Alarms

class SoundSystem {
  private ctx: AudioContext | null = null;
  private isAlarmPlaying = false;
  private alarmInterval: number | null = null;

  private initContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  // Tactical radar chirp
  public playRadarPing() {
    try {
      this.initContext();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(1440, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.12);

      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.12);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.13);
    } catch {
      // AudioContext could be blocked by browser policy prior to user interaction
    }
  }

  // Stage-4 emergency alert klaxon
  public startEmergencyAlarm() {
    if (this.isAlarmPlaying) return;
    this.isAlarmPlaying = true;

    const beep = () => {
      try {
        this.initContext();
        if (!this.ctx || !this.isAlarmPlaying) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, this.ctx.currentTime);
        osc.frequency.setValueAtTime(660, this.ctx.currentTime + 0.15);

        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.12, this.ctx.currentTime + 0.28);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.35);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.36);
      } catch {
        // audio policy ignored
      }
    };

    beep();
    this.alarmInterval = window.setInterval(beep, 900);
  }

  public stopEmergencyAlarm() {
    this.isAlarmPlaying = false;
    if (this.alarmInterval) {
      clearInterval(this.alarmInterval);
      this.alarmInterval = null;
    }
  }

  public toggleEmergencyAlarm(): boolean {
    if (this.isAlarmPlaying) {
      this.stopEmergencyAlarm();
      return false;
    } else {
      this.startEmergencyAlarm();
      return true;
    }
  }

  public isPlaying(): boolean {
    return this.isAlarmPlaying;
  }
}

export const soundFx = new SoundSystem();
