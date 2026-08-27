/* ════════════════════════════════════════════════════════════════
   compass.js — Compass dial + autopilot head + wake zone
   ════════════════════════════════════════════════════════════════ */

class CompassView {
  constructor() {
    this.canvas = document.getElementById('canvas-compass');
    this.ctx = this.canvas.getContext('2d');
    this.wakeCanvas = document.getElementById('canvas-wake');
    this.wakeCtx = this.wakeCanvas.getContext('2d');
    this.lastHeading = null;
    this.lastCommanded = null;
    this.lastRudder = null;
    this._wireUI();
  }

  _wireUI() {
    document.getElementById('deadband')?.addEventListener('input', e => {
      document.getElementById('deadband-val').textContent = `${e.target.value}°`;
      this._drawWake();
    });
    document.getElementById('wake-delay')?.addEventListener('input', e => {
      document.getElementById('wake-delay-val').textContent = `${parseFloat(e.target.value).toFixed(1)}s`;
    });
    document.getElementById('ap-gain')?.addEventListener('input', e => {
      document.getElementById('ap-gain-val').textContent = `${e.target.value}%`;
    });
    document.getElementById('yaw-damp')?.addEventListener('input', e => {
      document.getElementById('yaw-damp-val').textContent = `${e.target.value}%`;
    });
  }

  start() {
    BUS.register('compass.heading',    { value: 92, gate: 0.5,  sampleRate: 5,  color: '#4cffb0', kind: 'numeric', unit: '°', label: 'Heading', track: 'compass', min: 0, max: 360 });
    BUS.register('compass.commanded',  { value: 90, gate: 0,    sampleRate: 0.5, color: '#ffb84c', kind: 'numeric', unit: '°', label: 'Commanded', track: 'compass', min: 0, max: 360 });
    BUS.register('autopilot.rudder',   { value: 0,  gate: 0.2,  sampleRate: 5,  color: '#ff5cb0', kind: 'numeric', unit: '°', label: 'Rudder', track: 'autopilot', min: -30, max: 30 });
    BUS.register('autopilot.error',    { value: 0,  gate: 0.1,  sampleRate: 5,  color: '#ff5050', kind: 'numeric', unit: '°', label: 'Error', track: 'autopilot', min: -180, max: 180 });
    BUS.on('compass.heading',   e => this._onHeading(e));
    BUS.on('compass.commanded', e => this._onCommanded(e));
    BUS.on('autopilot.rudder',  e => this._onRudder(e));
    this._animate();
  }

  _onHeading(evt) {
    document.getElementById('heading-val').textContent = evt.value.toFixed(1);
    this.lastHeading = evt.value;
    this._updateError();
    this._draw();
  }

  _onCommanded(evt) {
    document.getElementById('commanded-val').textContent = evt.value.toFixed(1);
    this.lastCommanded = evt.value;
    this._updateError();
    this._draw();
    this._drawWake();
  }

  _onRudder(evt) {
    document.getElementById('rudder-val').textContent = `${evt.value.toFixed(1)}°`;
    const pct = (evt.value + 30) / 60;  // -30..+30 → 0..1
    const needle = document.getElementById('rudder-needle');
    if (needle) {
      needle.style.left = `${pct * 100}%`;
      // color: amber when near edges
      if (Math.abs(evt.value) > 20) needle.style.background = '#ff5050';
      else if (Math.abs(evt.value) > 10) needle.style.background = '#ffb84c';
      else needle.style.background = '#4cffb0';
    }
  }

  _updateError() {
    if (this.lastHeading !== null && this.lastCommanded !== null) {
      let err = this.lastCommanded - this.lastHeading;
      while (err > 180) err -= 360;
      while (err < -180) err += 360;
      document.getElementById('error-val').textContent = err.toFixed(1);
      BUS.set('autopilot.error', err, 'force');
    }
  }

  _animate() {
    this._draw();
    this._drawWake();
    requestAnimationFrame(() => this._animate());
  }

  _draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const cx = w / 2, cy = h / 2;
    const r = Math.min(w, h) / 2 - 10;

    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    // Outer ring
    ctx.strokeStyle = '#1f5a85';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    // Tick marks (every 10°)
    ctx.strokeStyle = '#4cffb0';
    ctx.fillStyle = '#4cffb0';
    ctx.font = '11px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let deg = 0; deg < 360; deg += 10) {
      const isMajor = deg % 30 === 0;
      const isCardinal = deg % 90 === 0;
      const len = isCardinal ? 18 : isMajor ? 12 : 6;
      const a = (deg - 90) * Math.PI / 180;
      const x1 = cx + Math.cos(a) * r;
      const y1 = cy + Math.sin(a) * r;
      const x2 = cx + Math.cos(a) * (r - len);
      const y2 = cy + Math.sin(a) * (r - len);
      ctx.lineWidth = isCardinal ? 3 : isMajor ? 2 : 1;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      if (isMajor) {
        const lx = cx + Math.cos(a) * (r - 32);
        const ly = cy + Math.sin(a) * (r - 32);
        ctx.fillText(deg.toString().padStart(3, '0'), lx, ly);
      }
    }

    // Cardinal letters
    ctx.font = 'bold 18px monospace';
    ctx.fillStyle = '#ffb84c';
    const cardinals = [['N', 0], ['E', 90], ['S', 180], ['W', 270]];
    for (const [letter, deg] of cardinals) {
      const a = (deg - 90) * Math.PI / 180;
      const lx = cx + Math.cos(a) * (r - 50);
      const ly = cy + Math.sin(a) * (r - 50);
      ctx.fillText(letter, lx, ly);
    }

    // Heading pointer (red, fixed at top)
    ctx.fillStyle = '#ff5050';
    ctx.beginPath();
    ctx.moveTo(cx, cy - r + 5);
    ctx.lineTo(cx - 8, cy - r + 25);
    ctx.lineTo(cx + 8, cy - r + 25);
    ctx.closePath();
    ctx.fill();

    // Rotating compass card
    if (this.lastHeading !== null) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((this.lastHeading) * Math.PI / 180);

      // Card background
      ctx.fillStyle = 'rgba(76, 255, 176, 0.05)';
      ctx.beginPath();
      ctx.arc(0, 0, r - 5, 0, Math.PI * 2);
      ctx.fill();

      // Tick marks on the card (rotated with heading)
      ctx.strokeStyle = '#4cffb0';
      ctx.fillStyle = '#4cffb0';
      ctx.font = '10px monospace';
      for (let deg = 0; deg < 360; deg += 30) {
        const a = (deg - 90) * Math.PI / 180;
        const x1 = Math.cos(a) * (r - 5);
        const y1 = Math.sin(a) * (r - 5);
        const x2 = Math.cos(a) * (r - 18);
        const y2 = Math.sin(a) * (r - 18);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        const lx = Math.cos(a) * (r - 30);
        const ly = Math.sin(a) * (r - 30);
        ctx.fillText(deg.toString().padStart(3, '0'), lx, ly);
      }
      ctx.restore();
    }

    // Commanded course indicator (amber triangle, rotating with commanded)
    if (this.lastCommanded !== null) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((this.lastCommanded) * Math.PI / 180);
      ctx.fillStyle = '#ffb84c';
      ctx.beginPath();
      ctx.moveTo(0, -r + 30);
      ctx.lineTo(-7, -r + 14);
      ctx.lineTo(7, -r + 14);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    // Center digital readout
    ctx.fillStyle = 'rgba(0, 16, 24, 0.85)';
    ctx.fillRect(cx - 50, cy - 12, 100, 24);
    ctx.strokeStyle = '#1f5a85';
    ctx.strokeRect(cx - 50, cy - 12, 100, 24);
    ctx.fillStyle = '#4cffb0';
    ctx.font = 'bold 16px monospace';
    ctx.fillText(`${(this.lastHeading ?? 0).toFixed(1)}°M`, cx, cy + 4);
  }

  _drawWake() {
    const ctx = this.wakeCtx;
    const w = this.wakeCanvas.width;
    const h = this.wakeCanvas.height;
    const cx = w / 2, cy = h / 2;
    const r = Math.min(w, h) / 2 - 10;
    const deadband = parseFloat(document.getElementById('deadband')?.value || 5);
    const wakeDelay = parseFloat(document.getElementById('wake-delay')?.value || 2);

    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    // Outer ring
    ctx.strokeStyle = '#1f5a85';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    // Wake zone (the deadband arc, swept around the commanded course)
    if (this.lastCommanded !== null) {
      const a = (this.lastCommanded) * Math.PI / 180;
      // Sweep the deadband arc
      const a1 = a - deadband * Math.PI / 180;
      const a2 = a + deadband * Math.PI / 180;
      ctx.fillStyle = 'rgba(255, 184, 76, 0.15)';
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r - 2, a1, a2);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#ffb84c';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Wake trail (the heading path over time)
      if (this._history) {
        ctx.strokeStyle = 'rgba(76, 255, 176, 0.4)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let i = 0; i < this._history.length; i++) {
          const a = this._history[i] * Math.PI / 180;
          const x = cx + Math.cos(a) * (r - 2);
          const y = cy + Math.sin(a) * (r - 2);
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      if (this.lastHeading !== null) {
        if (!this._history) this._history = [];
        this._history.push(this.lastHeading);
        if (this._history.length > 100) this._history.shift();
      }
    }

    // Inner ring
    ctx.strokeStyle = '#143550';
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.6, 0, Math.PI * 2);
    ctx.stroke();

    // Labels
    ctx.fillStyle = '#5a7e92';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('WAKE', cx, cy - 8);
    ctx.fillText(`±${deadband.toFixed(0)}°`, cx, cy + 6);
    ctx.fillText(`${wakeDelay.toFixed(1)}s`, cx, cy + 18);
  }
}

window.CompassView = CompassView;
