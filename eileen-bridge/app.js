/* ════════════════════════════════════════════════════════════════
   app.js — Main app, wires everything together
   ════════════════════════════════════════════════════════════════ */

class App {
  constructor() {
    this.startTime = Date.now();
    this.playing = false;
    this._init();
  }

  _init() {
    // Set log handler
    BUS.setLogFn(entry => this._log(entry));
    // Subscribe to symmetry events
    BUS.onSymmetry(sym => this._onSymmetry(sym));
    // Listen to all cells for track-state
    setTimeout(() => {
      this._wireTrackStates();
    }, 500);

    // Transport buttons
    document.getElementById('btn-play')?.addEventListener('click', () => this.play());
    document.getElementById('btn-pause')?.addEventListener('click', () => this.pause());
    document.getElementById('btn-stop')?.addEventListener('click', () => this.stop());
    document.getElementById('btn-record')?.addEventListener('click', () => this.toggleRecord());

    // BPM / sample-rate / gate
    document.getElementById('bpm')?.addEventListener('input', e => {
      const bpm = parseInt(e.target.value);
      const interval = 60000 / bpm / 4; // 16th notes
      // Re-set sample rates?
    });
    document.getElementById('sample-rate')?.addEventListener('change', e => {
      const newRate = parseFloat(e.target.value);
      // Update all numeric cells
      for (const cell of BUS.list()) {
        if (cell.kind === 'numeric') cell.sampleRate = newRate;
      }
      BUS.log(`sample-rate set to ${newRate}Hz`, 'transport', 'info');
    });
    document.getElementById('gate')?.addEventListener('change', e => {
      const newGate = parseFloat(e.target.value);
      for (const cell of BUS.list()) {
        if (cell.kind === 'numeric') cell.gate = newGate;
      }
      BUS.log(`gate set to ${newGate}`, 'transport', 'info');
    });

    // Clock
    this._tickClock();

    // Initial views
    this.sounder = new SounderView();
    this.compass = new CompassView();
    this.gps = new GPSView();
    this.cameras = new CamerasView();
    this.engine = new EngineView();
    this.weather = new WeatherView();
    this.arrangement = new ArrangementView();
    this.mixer = new MixerView();

    // Start all views
    this.sounder.start();
    this.compass.start();
    this.gps.start();
    this.cameras.start();
    this.engine.start();
    this.weather.start();
    this.arrangement.start();
    this.mixer.start();

    // Start sensor simulation
    SIM = new SensorSim(BUS);
    SIM.start();

    this.play();
    BUS.log('Eileen\'s Bridge online. All cells alive.', 'system', 'info');
    BUS.log('Each piece of information is a cell. Deltas are the TICKs.', 'system', 'info');
  }

  _wireTrackStates() {
    // Set track state indicators active
    document.querySelectorAll('.track-state').forEach(el => {
      el.classList.add('active');
    });
  }

  _tickClock() {
    const update = () => {
      const now = new Date();
      const t = now.toTimeString().slice(0, 8);
      document.getElementById('clock').textContent = t;
      // Position (mm:ss)
      const elapsed = (now - this.startTime) / 1000;
      const mm = Math.floor(elapsed / 60);
      const ss = Math.floor(elapsed % 60);
      const ms = Math.floor((elapsed - mm*60 - ss) * 10);
      document.getElementById('position').textContent = `${mm}:${ss.toString().padStart(2,'0')}:${ms}`;
      setTimeout(update, 100);
    };
    update();
  }

  _log(entry) {
    const list = document.getElementById('log-list');
    if (!list) return;
    const e = document.createElement('div');
    e.className = 'log-entry' + (entry.kind === 'error' ? ' le-error' : '');
    const t = new Date(entry.time).toTimeString().slice(0, 8);
    e.innerHTML = `<span class="le-time">${t}</span><span class="le-track">${entry.track}</span><span class="le-msg">${entry.msg}</span>`;
    list.insertBefore(e, list.firstChild);
    if (list.children.length > 100) list.removeChild(list.lastChild);
  }

  _onSymmetry(sym) {
    const list = document.getElementById('sym-list');
    if (list) {
      const e = document.createElement('div');
      e.className = 'sym-entry';
      const t = new Date(sym.time).toTimeString().slice(0, 8);
      e.innerHTML = `<span class="se-time">${t}</span><span class="se-msg">${sym.a}=${sym.aValue?.toFixed(2)} ⊥ ${sym.b}=${sym.bValue?.toFixed(2)} Δt=${sym.dt}ms</span>`;
      list.insertBefore(e, list.firstChild);
      if (list.children.length > 30) list.removeChild(list.lastChild);
    }
    this._log({
      msg: `SYM: ${sym.a} ⊥ ${sym.b} (${sym.dt}ms)`,
      track: 'symmetry',
      kind: 'info',
      time: sym.time,
    });
  }

  play() {
    this.playing = true;
    document.getElementById('btn-play')?.classList.add('active');
    BUS.log('transport: PLAY', 'transport', 'info');
  }
  pause() {
    this.playing = false;
    document.getElementById('btn-play')?.classList.remove('active');
    BUS.log('transport: PAUSE', 'transport', 'info');
  }
  stop() {
    this.playing = false;
    this.startTime = Date.now();
    document.getElementById('btn-play')?.classList.remove('active');
    BUS.log('transport: STOP', 'transport', 'info');
  }
  toggleRecord() {
    document.getElementById('btn-record')?.classList.toggle('active');
    BUS.log('transport: RECORD toggle', 'transport', 'info');
  }
}

class MixerView {
  constructor() {
    this.list = document.getElementById('mixer-list');
  }
  start() {
    this._render();
    setInterval(() => this._update(), 500);
  }
  _render() {
    this.list.innerHTML = '';
    for (const cell of BUS.list()) {
      const row = document.createElement('div');
      row.className = 'mtrk mixer-track';
      row.dataset.cellName = cell.name;
      row.innerHTML = `
        <div class="mt-color" style="background: ${cell.color}"></div>
        <div class="mt-name" title="${cell.name}">${cell.label || cell.name}</div>
        <div class="mt-value" id="mv-${cell.name}">--</div>
        <div class="mt-delta" id="md-${cell.name}">--</div>
        <button class="mt-btn mt-mute">M</button>
        <button class="mt-btn mt-solo">S</button>
      `;
      this.list.appendChild(row);
      row.querySelector('.mt-mute').addEventListener('click', () => {
        cell.muted = !cell.muted;
        row.classList.toggle('muted', cell.muted);
        row.querySelector('.mt-mute').classList.toggle('solo', cell.muted);
      });
      row.querySelector('.mt-solo').addEventListener('click', () => {
        cell.solo = !cell.solo;
        row.querySelector('.mt-solo').classList.toggle('solo', cell.solo);
      });
    }
  }
  _update() {
    for (const cell of BUS.list()) {
      const v = document.getElementById(`mv-${cell.name}`);
      const d = document.getElementById(`md-${cell.name}`);
      if (!v) continue;
      const val = cell.lastValue;
      if (val === null || val === undefined) v.textContent = '--';
      else if (typeof val === 'number') v.textContent = val.toFixed(1) + (cell.unit ? ' ' + cell.unit : '');
      else v.textContent = String(val);
      d.textContent = cell.fireCount > 0 ? `${cell.fireCount} firings` : '--';
    }
  }
}

window.App = App;
window.MixerView = MixerView;

// ─── BOOT ───
window.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
