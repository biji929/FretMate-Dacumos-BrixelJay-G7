// Metronome using Web Audio API with Lookahead Scheduling
// Eliminates timer drift for sample-accurate musical timing.

class Metronome {
    constructor(bpm = 120, beatsPerMeasure = 4, beatUnit = 4) {
        this.bpm = parseInt(bpm, 10);
        this.beatsPerMeasure = parseInt(beatsPerMeasure, 10);
        this.beatUnit = parseInt(beatUnit, 10); // Denominator: 4 (quarter notes), 8 (eighth notes)
        this.isPlaying = false;
        this.audioCtx = null;
        this.currentBeat = 0;
        this.nextNoteTime = 0.0;
        this.timerId = null;
        this.lookahead = 25.0; // Lookahead interval in ms
        this.scheduleAheadTime = 0.1; // Scheduling horizon in seconds
        this.onBeat = null; // Callback: (beatIndex, accentLevel: 'primary' | 'secondary' | 'normal')
    }

    start() {
        if (this.isPlaying) return;

        // Initialize AudioContext on user gesture
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }

        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }

        this.isPlaying = true;
        this.currentBeat = 0;
        this.nextNoteTime = this.audioCtx.currentTime + 0.05;

        // Run scheduler loop every 25ms
        this.timerId = setInterval(() => this.scheduler(), this.lookahead);
    }

    stop() {
        if (!this.isPlaying) return;
        this.isPlaying = false;
        clearInterval(this.timerId);
        this.timerId = null;
        this.currentBeat = 0;
    }

    scheduler() {
        // While there are notes that will need to play before next interval, schedule them
        while (this.nextNoteTime < this.audioCtx.currentTime + this.scheduleAheadTime) {
            this.scheduleNote(this.currentBeat, this.nextNoteTime);
            this.nextNote();
        }
    }

    nextNote() {
        // Quarter note = 60 / bpm.
        // If beatUnit is 8 (eighth notes), interval is half of quarter note.
        const baseSeconds = 60.0 / this.bpm;
        const secondsPerBeat = (this.beatUnit === 8) ? (baseSeconds / 2.0) : baseSeconds;

        this.nextNoteTime += secondsPerBeat;
        this.currentBeat = (this.currentBeat + 1) % this.beatsPerMeasure;
    }

    getAccentLevel(beatNumber) {
        if (beatNumber === 0) return 'primary';

        // Secondary accents for common compound or irregular meters
        if (this.beatsPerMeasure === 6 && beatNumber === 3) return 'secondary'; // 6/8
        if (this.beatsPerMeasure === 12 && (beatNumber === 3 || beatNumber === 6 || beatNumber === 9)) return 'secondary'; // 12/8
        if (this.beatsPerMeasure === 5 && beatNumber === 3) return 'secondary'; // 5/4 (3+2)
        if (this.beatsPerMeasure === 7 && beatNumber === 4) return 'secondary'; // 7/8 (4+3)
        if (this.beatsPerMeasure === 4 && beatNumber === 2) return 'secondary'; // 4/4 backbeat

        return 'normal';
    }

    scheduleNote(beatNumber, time) {
        const accentLevel = this.getAccentLevel(beatNumber);

        // Create oscillator & gain envelope
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();

        // Audio frequency pitches:
        // Primary accent: 1400 Hz (high, bright)
        // Secondary accent: 1050 Hz (medium-high)
        // Normal beat: 750 Hz (standard percussive click)
        let freq = 750;
        let volume = 0.8;
        if (accentLevel === 'primary') {
            freq = 1400;
            volume = 1.0;
        } else if (accentLevel === 'secondary') {
            freq = 1050;
            volume = 0.9;
        }

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, time);

        // Quick punchy percussive click envelope
        gain.gain.setValueAtTime(volume, time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.035);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);

        osc.start(time);
        osc.stop(time + 0.035);

        // Dispatch visual feedback timed with the sound
        const delayMs = Math.max(0, (time - this.audioCtx.currentTime) * 1000);
        setTimeout(() => {
            if (this.isPlaying && typeof this.onBeat === 'function') {
                this.onBeat(beatNumber, accentLevel);
            }
        }, delayMs);
    }

    setBpm(newBpm) {
        const parsed = parseInt(newBpm, 10);
        if (!isNaN(parsed) && parsed >= 30 && parsed <= 300) {
            this.bpm = parsed;
        }
    }

    setTimeSignature(numerator, denominator = 4) {
        const n = parseInt(numerator, 10);
        const d = parseInt(denominator, 10);
        if (!isNaN(n) && n >= 1 && n <= 16) {
            this.beatsPerMeasure = n;
        }
        if (!isNaN(d) && (d === 2 || d === 4 || d === 8 || d === 16)) {
            this.beatUnit = d;
        }
        this.currentBeat = 0;
    }
}
