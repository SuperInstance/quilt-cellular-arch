/* ════════════════════════════════════════════════════════════════
   engine.js — Engine / Substrate panel
   ════════════════════════════════════════════════════════════════ */

class EngineView {
  constructor() {
    this.canvas = document.getElementById('canvas-engine');
    this.ctx = this.canvas.getContext('2d');
    this.history = [];
  }

  start() {
    BUS.register('engine.rpm',     { value: 1450, gate: 5,    sampleRate: 2, color: '#ffb84c', kind: 'numeric', unit: 'rpm', label: 'RPM', track: 'engine', min: 0, max: 2500 });
    BUS.register('engine.temp',    { value: 78,   gate: 0.5,  sampleRate: 1, color: '#ffb84c', kind: 'numeric', unit: '°C', label: 'Temp', track: 'engine', min: 0, max: 120 });
    BUS.register('engine.oilp',    { value: 52,   gate: 1,    sampleRate: 0.5, color: '#ffb84c', kind: 'numeric', unit: 'psi', label: 'OilP', track: 'engine', min: 0, max: 100 });
    BUS.register('engine.fuel',    { value: 78,   gate: 0.01, sampleRate: 0.1, color: '#ffb84c', kind: 'numeric', unit: '%', label: 'Fuel', track: 'engine', min: 0, max: 100 });
    BUS.register('engine.battery', { value: 12.6, gate: 0.05, sampleRate: 0.5, color: '#4cffb0', kind: 'numeric', unit: 'V', label: 'Batt', track: 'engine', min: 0, max: 16 });
    BUS.register('engine.hours',   { value: 4521.7, gate: 0.1, sampleRate: 0.1, color: '#5ce0ff', kind: 'numeric', unit: 'h', label: 'Hours', track: 'engine', min: 0, max: 10000 });
    BUS.on('engine.rpm', e => { document.getElementById('rpm-val').textContent = e.value.toFixed(0); this._record(e); });
    BUS.on('engine.temp', e => { document.getElementById('temp-val').textContent = e.value.toFixed(1); });
    BUS.on('engine.oilp', e => { document.getElementById('oilp-val').textContent = e.value.toFixed(1); });
    BUS.on('engine.fuel', e => { document.getElementById('fuel-val').textContent = e.value.toFixed(1); });
    BUS.on('engine.battery', e => { document.getElementById('batt-val').textContent = e.value.toFixed(2); });
    BUS.on('engine.hours', e => { document.getElementById('hours-val').textContent = e.value.toFixed(1); });
    this._animate();
  }

  _record(evt) {
    this.history.push({ t: Date.now(), v: evt.value });
    if (this.history.length > 200) this.history.shift();
  }

  _animate() {
    this._draw();
    requestAnimationFrame(() => this._animate());
  }

  _draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    if (this.history.length < 2) return;

    // Y scale 0-2500
    const ymax = 2500;
    ctx.strokeStyle = '#143550';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = h - (i / 5) * h;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // RPM trace
    ctx.strokeStyle = '#ffb84c';
    ctx.lineWidth = 1.5;
    ctx.shadowColor = '#ffb84c';
    ctx.shadowBlur = 3;
    ctx.beginPath();
    for (let i = 0; i < this.history.length; i++) {
      const x = (i / (this.history.length - 1)) * w;
      const y = h - (this.history[i].v / ymax) * h;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Last value
    if (this.history.length > 0) {
      const last = this.history[this.history.length - 1];
      ctx.fillStyle = '#ffb84c';
      ctx.font = 'bold 14px monospace';
      ctx.fillText(`${last.v.toFixed(0)} rpm`, 10, 18);
    }
  }
}

class WeatherView {
  constructor() {}

  start() {
    BUS.register('weather.wind',    { value: 12,   gate: 0.5,   sampleRate: 1, color: '#5ce0ff', kind: 'numeric', unit: 'kt', label: 'Wind', track: 'weather', min: 0, max: 60 });
    BUS.register('weather.winddir', { value: 220,  gate: 1,     sampleRate: 1, color: '#5ce0ff', kind: 'numeric', unit: '°', label: 'WindDir', track: 'weather', min: 0, max: 360 });
    BUS.register('weather.airtemp', { value: 14.5, gate: 0.1,   sampleRate: 0.1, color: '#5ce0ff', kind: 'numeric', unit: '°C', label: 'AirT', track: 'weather', min: -30, max: 50 });
    BUS.register('weather.baro',    { value: 1014.2, gate: 0.1, sampleRate: 0.1, color: '#5ce0ff', kind: 'numeric', unit: 'hPa', label: 'Baro', track: 'weather', min: 950, max: 1050 });
    BUS.register('weather.seatemp', { value: 11.8, gate: 0.05,  sampleRate: 0.1, color: '#5ce0ff', kind: 'numeric', unit: '°C', label: 'SeaT', track: 'weather', min: -2, max: 30 });
    BUS.on('weather.wind',    e => { document.getElementById('wind-val').textContent = e.value.toFixed(1); });
    BUS.on('weather.winddir', e => { document.getElementById('winddir-val').textContent = e.value.toFixed(0) + '°'; });
    BUS.on('weather.airtemp', e => { document.getElementById('airt-val').textContent = e.value.toFixed(1); });
    BUS.on('weather.baro',    e => { document.getElementById('baro-val').textContent = e.value.toFixed(1); });
    BUS.on('weather.seatemp', e => { document.getElementById('seat-val').textContent = e.value.toFixed(1); });
  }
}

window.EngineView = EngineView;
window.WeatherView = WeatherView;
