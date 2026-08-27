/* ════════════════════════════════════════════════════════════════
   arrangement.js — DAW-style arrangement view: events as notes on a timeline
   ════════════════════════════════════════════════════════════════ */

class ArrangementView {
  constructor() {
    this.canvas = document.getElementById('canvas-arrangement');
    this.ctx = this.canvas.getContext('2d');
    this.scrollX = 0;
    this.maxTime = 60; // 60 second window
    this.startTime = Date.now();
    this.lastDraw = Date.now();
    this.symmetryEvents = [];
  }

  start() {
    BUS.onSymmetry(sym => {
      this.symmetryEvents.push(sym);
      if (this.symmetryEvents.length > 50) this.symmetryEvents.shift();
    });
    this._animate();
  }

  _animate() {
    this._draw();
    requestAnimationFrame(() => this._animate());
  }

  _draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const now = Date.now();
    const elapsed = (now - this.startTime) / 1000;
    document.getElementById('arr-time-cursor').textContent = `${elapsed.toFixed(0)}s`;

    // Auto-scroll
    if (elapsed > this.maxTime) {
      this.startTime = now - this.maxTime * 1000;
    }

    // Background
    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    // Time grid
    const startSec = (now - this.startTime) / 1000 - this.maxTime;
    const endSec = (now - this.startTime) / 1000;
    ctx.strokeStyle = '#143550';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#5a7e92';
    ctx.font = '9px monospace';
    for (let t = Math.floor(startSec); t < endSec; t++) {
      if (t % 5 !== 0) continue;
      const x = ((t - startSec) / this.maxTime) * w;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
      ctx.fillText(`${t}s`, x + 2, 10);
    }

    // Track lanes
    const tracks = [
      { name: 'compass',   color: '#4cffb0', y: 30 },
      { name: 'sounder',   color: '#5ce0ff', y: 60 },
      { name: 'gps',       color: '#ff5cb0', y: 90 },
      { name: 'cameras',   color: '#ffe85c', y: 120 },
      { name: 'rudder',    color: '#ffb84c', y: 150 },
      { name: 'autopilot', color: '#ff5050', y: 180 },
    ];
    ctx.fillStyle = 'rgba(76, 255, 176, 0.04)';
    for (const t of tracks) {
      ctx.fillRect(0, t.y - 8, w, 16);
    }
    // Track labels
    for (const t of tracks) {
      ctx.fillStyle = t.color;
      ctx.font = 'bold 9px monospace';
      ctx.fillText(t.name, 4, t.y + 3);
    }

    // Draw events
    const winStart = now - this.maxTime * 1000;
    for (const cell of BUS.list()) {
      const track = tracks.find(t => t.name === cell.track);
      if (!track) continue;
      const history = cell.history;
      for (let i = Math.max(0, history.length - 100); i < history.length; i++) {
        const e = history[i];
        const dt = (e.time - winStart) / 1000;
        if (dt < 0 || dt > this.maxTime) continue;
        const x = (dt / this.maxTime) * w;
        // Height based on value (if numeric)
        let valNorm = 0.5;
        if (typeof e.value === 'number') {
          valNorm = (e.value - cell.min) / (cell.max - cell.min);
          valNorm = Math.max(0, Math.min(1, valNorm));
        }
        // For 'rudder' (bipolar), center
        if (cell.min < 0) {
          valNorm = (e.value - cell.min) / (cell.max - cell.min);
        }
        const barH = 4 + valNorm * 12;
        ctx.fillStyle = cell.color;
        ctx.fillRect(x, track.y - barH/2, 2, barH);
        // Pulse for recent
        if (e.time > now - 500) {
          ctx.globalAlpha = 0.5;
          ctx.fillRect(x - 2, track.y - 4, 6, 8);
          ctx.globalAlpha = 1;
        }
      }
    }

    // Symmetry events
    for (const sym of this.symmetryEvents) {
      const dt = (sym.time - winStart) / 1000;
      if (dt < 0 || dt > this.maxTime) continue;
      const x = (dt / this.maxTime) * w;
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.shadowColor = '#fff';
      ctx.shadowBlur = 6;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
      ctx.shadowBlur = 0;
      // Star burst
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(x, h/2, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

window.ArrangementView = ArrangementView;
