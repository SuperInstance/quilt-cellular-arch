/* ════════════════════════════════════════════════════════════════
   daw-engine.js — The Quilt's Cell Bus

   Each piece of information is a CELL. The DAW is the bus.
   - At startup, every cell PLAYS its initial value (the "loop")
   - After that, the cell only fires EVENTS when the value changes
   - The SAMPLE-RATE is the snap grid (values get quantized to it)
   - The GATE is the trigger threshold (only values that cross fire)
   - SYMMETRY between cells is found ASYNCHRONOUSLY — when two events
     from different cells happen within a tolerance window, they
     "align" (a symmetry-event fires)
   ════════════════════════════════════════════════════════════════ */

class CellBus {
  constructor() {
    this.cells = new Map();   // name -> { value, prevValue, gate, sampleRate, color, source, lastSnap, lastFire, track }
    this.listeners = new Map(); // name -> [fn, fn, ...]
    this.toleranceWindow = 2000; // ms for symmetry detection
    this.recentEvents = [];     // { name, time, value } for symmetry detection
    this.symmetryListeners = [];
    this.startTime = Date.now();
    this.tickCount = 0;
    this.playing = false;
  }

  // ─── REGISTER A CELL ───
  register(name, opts = {}) {
    const cell = {
      name,
      value: opts.value ?? null,
      prevValue: null,
      gate: opts.gate ?? 0,                  // min delta to fire
      sampleRate: opts.sampleRate ?? 0.1,    // snap to this rate (Hz)
      color: opts.color ?? '#4cffb0',
      source: opts.source ?? 'sim',          // 'sim' | 'manual' | 'serial'
      track: opts.track ?? 'mixer',
      kind: opts.kind ?? 'numeric',          // 'numeric' | 'string' | 'boolean'
      unit: opts.unit ?? '',
      label: opts.label ?? name,
      visible: true,
      muted: false,
      solo: false,
      lastSnap: 0,
      lastFire: 0,
      lastValue: null,
      fireCount: 0,
      min: opts.min ?? 0,
      max: opts.max ?? 100,
      history: [],                          // for arrangement view
      historyMax: opts.historyMax ?? 200,
    };
    this.cells.set(name, cell);
    this.log(`register ${name} (${cell.kind}, gate=${cell.gate}, rate=${cell.sampleRate}Hz)`, 'compass', 'info');
    return cell;
  }

  // ─── SET VALUE (THE TICK) ───
  set(name, rawValue, source = 'sim') {
    const cell = this.cells.get(name);
    if (!cell) return;
    if (cell.muted) return;

    const now = Date.now();
    const elapsed = (now - cell.lastSnap) / 1000;
    const rate = cell.sampleRate || 0.1;
    const period = 1 / rate;

    // ─── SAMPLE-RATE SNAP: only update if period elapsed (unless forced) ───
    if (source !== 'force' && elapsed < period && cell.lastSnap !== 0) {
      return; // too soon
    }

    // ─── GATE: only fire if delta crosses threshold ───
    let fire = false;
    let displayValue = rawValue;

    if (cell.kind === 'numeric') {
      const delta = cell.lastValue !== null ? Math.abs(rawValue - cell.lastValue) : Infinity;
      if (delta >= cell.gate || cell.lastValue === null) {
        fire = true;
      } else {
        // Below gate: snap to last snapped value (no event)
        return;
      }
    } else if (cell.kind === 'string' || cell.kind === 'boolean') {
      if (cell.lastValue !== rawValue) {
        fire = true;
      } else {
        return;
      }
    }

    if (!fire) return;

    // ─── FIRE THE EVENT ───
    const prev = cell.lastValue;
    cell.lastValue = rawValue;
    cell.lastSnap = now;
    cell.fireCount++;

    const evt = {
      name,
      value: rawValue,
      prevValue: prev,
      delta: typeof rawValue === 'number' && typeof prev === 'number' ? rawValue - prev : null,
      time: now,
      fireCount: cell.fireCount,
    };
    cell.history.push(evt);
    if (cell.history.length > cell.historyMax) cell.history.shift();

    // ─── NOTIFY LISTENERS ───
    this._fire(name, evt);

    // ─── RECORD FOR SYMMETRY DETECTION ───
    if (cell.kind === 'numeric') {
      this.recentEvents.push({ name, time: now, value: rawValue });
      // Keep only events within the tolerance window
      this.recentEvents = this.recentEvents.filter(e => now - e.time < this.toleranceWindow);
      this._checkSymmetry();
    }
  }

  // ─── SUBSCRIBE TO CELL EVENTS ───
  on(name, fn) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(fn);
  }

  onSymmetry(fn) {
    this.symmetryListeners.push(fn);
  }

  _fire(name, evt) {
    const list = this.listeners.get(name);
    if (list) list.forEach(fn => fn(evt));
  }

  // ─── SYMMETRY DETECTION ───
  // When two events from different cells happen within the tolerance window,
  // they "align" — a symmetry-event fires.
  _checkSymmetry() {
    if (this.recentEvents.length < 2) return;
    const now = Date.now();
    // Find pairs of events from different cells within window
    const recent = this.recentEvents.slice(-20);
    for (let i = 0; i < recent.length; i++) {
      for (let j = i + 1; j < recent.length; j++) {
        const a = recent[i], b = recent[j];
        if (a.name === b.name) continue;
        const dt = Math.abs(a.time - b.time);
        if (dt < this.toleranceWindow / 4) {  // tight alignment
          // Check if this pair has been reported recently
          const key = `${a.name}:${b.name}:${Math.floor(a.time / 1000)}`;
          if (this._lastSymKeys && this._lastSymKeys.has(key)) continue;
          if (!this._lastSymKeys) this._lastSymKeys = new Set();
          this._lastSymKeys.add(key);
          // Cleanup
          if (this._lastSymKeys.size > 200) {
            const arr = [...this._lastSymKeys];
            this._lastSymKeys = new Set(arr.slice(-100));
          }
          // Report symmetry
          const sym = {
            a: a.name, b: b.name,
            aValue: a.value, bValue: b.value,
            time: Math.max(a.time, b.time),
            dt,
          };
          this.symmetryListeners.forEach(fn => fn(sym));
          this._fire('__symmetry__', sym);
        }
      }
    }
  }

  // ─── UTILITIES ───

  get(name) {
    const c = this.cells.get(name);
    return c ? c.lastValue : null;
  }

  list() {
    return Array.from(this.cells.values());
  }

  log(msg, track = 'system', kind = 'info') {
    const entry = { msg, track, kind, time: Date.now() };
    if (this._logFn) this._logFn(entry);
    // Also log to console
    if (kind === 'error') console.error(`[${track}] ${msg}`);
    else console.log(`[${track}] ${msg}`);
  }

  setLogFn(fn) { this._logFn = fn; }

  tick() {
    this.tickCount++;
  }
}

// ─── SIMULATED SENSORS ───
// In real deployment, this would be NMEA 0183/2000 over serial/websocket.
// For now, we simulate with believable dynamics.

class SensorSim {
  constructor(bus) {
    this.bus = bus;
    this.simHandle = null;
    this.startTime = Date.now();
    this.state = {
      heading: 92,    // degrees magnetic
      commandedCourse: 90,
      depth: 24.7,
      lat: 44.6526,   // Newport OR
      lon: -124.0535,
      sog: 6.2,       // knots
      cog: 88,
      windSpeed: 12,
      windDir: 220,
      airTemp: 14.5,
      baro: 1014.2,
      seaTemp: 11.8,
      rpm: 1450,
      engineTemp: 78,
      oilPressure: 52,
      fuel: 78,
      battery: 12.6,
      hours: 4521.7,
      rudder: 0,
    };
    this._lastTick = Date.now();
  }

  start() {
    if (this.simHandle) return;
    this.simHandle = setInterval(() => this._step(), 200);
  }

  stop() {
    if (this.simHandle) clearInterval(this.simHandle);
    this.simHandle = null;
  }

  _step() {
    const now = Date.now();
    const dt = (now - this._lastTick) / 1000;
    this._lastTick = now;
    const t = (now - this.startTime) / 1000;

    // ─── COMPASS / HEADING (slight oscillation) ───
    this.state.heading += Math.sin(t * 0.13) * 0.4 + (Math.random() - 0.5) * 0.6;
    this.state.heading = ((this.state.heading + 540) % 360) - 180;
    this.bus.set('compass.heading', this.state.heading);

    // ─── COMMANDED COURSE (occasionally changes) ───
    if (Math.random() < 0.005) {
      this.state.commandedCourse += (Math.random() - 0.5) * 30;
      this.state.commandedCourse = ((this.state.commandedCourse + 360) % 360);
      this.bus.set('compass.commanded', this.state.commandedCourse);
    }

    // ─── RUDDER (responds to error, with delay/yaw-damp) ───
    const err = this._angleDiff(this.state.heading, this.state.commandedCourse);
    const wake = parseFloat(document.getElementById('wake-delay')?.value || 2);
    const gain = (parseFloat(document.getElementById('ap-gain')?.value || 50)) / 100;
    const yawDamp = (parseFloat(document.getElementById('yaw-damp')?.value || 40)) / 100;
    const targetRudder = Math.max(-30, Math.min(30, -err * gain * 2.5));
    this.state.rudder += (targetRudder - this.state.rudder) * (dt / (wake + 0.1)) * (1 - yawDamp * 0.5);
    this.state.rudder += (Math.random() - 0.5) * 0.1;
    this.state.rudder = Math.max(-30, Math.min(30, this.state.rudder));
    if (Math.abs(this.state.rudder) > 0.2) {
      this.bus.set('autopilot.rudder', this.state.rudder);
    }

    // ─── SOUNDER / DEPTH ───
    this.state.depth += (Math.random() - 0.5) * 0.3 + Math.sin(t * 0.05) * 0.1;
    this.state.depth = Math.max(2, Math.min(120, this.state.depth));
    this.bus.set('sounder.depth', this.state.depth);

    // ─── Sounder raw sample (for oscilloscope) ───
    const sounderSample = (Math.random() - 0.5) * 0.4 +
                         Math.sin(t * 4) * 0.2 * Math.exp(-Math.abs(this.state.depth - 30) / 20) +
                         (Math.sin(t * 80) * 0.05);
    this.bus.set('sounder.sample', sounderSample);

    // ─── GPS / POSITION ───
    this.state.lat += Math.cos(this.state.heading * Math.PI / 180) * this.state.sog * 0.000005 * dt;
    this.state.lon += Math.sin(this.state.heading * Math.PI / 180) * this.state.sog * 0.000008 * dt;
    this.bus.set('gps.lat', this.state.lat);
    this.bus.set('gps.lon', this.state.lon);

    // ─── SOG ───
    this.state.sog += (Math.random() - 0.5) * 0.05;
    this.state.sog = Math.max(0, Math.min(12, this.state.sog));
    if (Math.abs(this.state.sog - (this.bus.get('gps.sog') ?? 0)) > 0.1) {
      this.bus.set('gps.sog', this.state.sog);
    }

    // ─── COG (course over ground) ───
    this.state.cog = this.state.heading + (Math.random() - 0.5) * 2;
    this.bus.set('gps.cog', this.state.cog);

    // ─── WIND ───
    this.state.windSpeed += (Math.random() - 0.5) * 0.4;
    this.state.windSpeed = Math.max(0, Math.min(45, this.state.windSpeed));
    if (Math.abs(this.state.windSpeed - (this.bus.get('weather.wind') ?? 0)) > 0.5) {
      this.bus.set('weather.wind', this.state.windSpeed);
    }
    this.state.windDir += (Math.random() - 0.5) * 4;
    this.state.windDir = ((this.state.windDir + 360) % 360);
    this.bus.set('weather.winddir', this.state.windDir);

    // ─── AIR/SEA TEMP ───
    if (Math.random() < 0.02) {
      this.state.airTemp += (Math.random() - 0.5) * 0.1;
      this.bus.set('weather.airtemp', this.state.airTemp);
    }
    if (Math.random() < 0.02) {
      this.state.seaTemp += (Math.random() - 0.5) * 0.05;
      this.bus.set('weather.seatemp', this.state.seaTemp);
    }
    if (Math.random() < 0.01) {
      this.state.baro += (Math.random() - 0.5) * 0.2;
      this.bus.set('weather.baro', this.state.baro);
    }

    // ─── ENGINE ───
    this.state.rpm += (Math.random() - 0.5) * 8;
    this.state.rpm = Math.max(700, Math.min(2200, this.state.rpm));
    if (Math.abs(this.state.rpm - (this.bus.get('engine.rpm') ?? 0)) > 5) {
      this.bus.set('engine.rpm', this.state.rpm);
    }
    this.state.engineTemp += (Math.random() - 0.5) * 0.3;
    this.state.engineTemp = Math.max(50, Math.min(110, this.state.engineTemp));
    if (Math.abs(this.state.engineTemp - (this.bus.get('engine.temp') ?? 0)) > 0.5) {
      this.bus.set('engine.temp', this.state.engineTemp);
    }
    this.state.oilPressure += (Math.random() - 0.5) * 0.5;
    this.state.oilPressure = Math.max(20, Math.min(80, this.state.oilPressure));
    if (Math.abs(this.state.oilPressure - (this.bus.get('engine.oilp') ?? 0)) > 1) {
      this.bus.set('engine.oilp', this.state.oilPressure);
    }
    if (Math.random() < 0.005) {
      this.state.fuel -= 0.01;
      this.bus.set('engine.fuel', this.state.fuel);
    }
    if (Math.random() < 0.01) {
      this.state.battery += (Math.random() - 0.5) * 0.05;
      this.bus.set('engine.battery', this.state.battery);
    }
    this.state.hours += dt / 600;  // accumulate
    if (Math.abs(this.state.hours - (this.bus.get('engine.hours') ?? 0)) > 0.1) {
      this.bus.set('engine.hours', this.state.hours);
    }

    // ─── CAMERA TICK (frame count) ───
    if (Math.random() < 0.3) {
      this.bus.set('camera.tick', Math.floor(t * 30));
    }
  }

  _angleDiff(a, b) {
    let d = b - a;
    while (d > 180) d -= 360;
    while (d < -180) d += 360;
    return d;
  }
}

// ─── GLOBAL ───
const BUS = new CellBus();
let SIM = null;

console.log("Eileen's Bridge DAW Engine loaded");
console.log('Each piece of information is a cell. Deltas are the TICKs.');
