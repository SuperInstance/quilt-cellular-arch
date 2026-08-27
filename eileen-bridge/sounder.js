/* ════════════════════════════════════════════════════════════════
   sounder.js — Echogram + Oscilloscope for depth soundings
   ════════════════════════════════════════════════════════════════ */

class SounderView {
  constructor() {
    this.echogram = document.getElementById('canvas-echogram');
    this.osc = document.getElementById('canvas-oscilloscope');
    this.echogramCtx = this.echogram.getContext('2d');
    this.oscCtx = this.osc.getContext('2d');
    this.mode = 'echogram';
    this.range = 100; // meters
    this.gain = 65;
    this.freq = 200; // kHz
    this.depthHistory = [];   // for echogram: each sample {t, depth, samples}
    this.sampleBuffer = [];   // raw waveform for osc
    this.maxBuffer = 800;
    this.scrollPos = 0;
    this.synthesized = [];    // synthetic echogram profile
    this._initSynthetic();
    this._wireUI();
  }

  _initSynthetic() {
    // Synthesize a bottom profile so the echogram looks real
    // The depth varies with x-position (representing the boat moving over the bottom)
    for (let i = 0; i < 800; i++) {
      const x = i / 800;
      // Multi-frequency bottom + fish arches + thermoclines
      const bottom = 60 + Math.sin(x * 8) * 20 + Math.cos(x * 23) * 8;
      this.synthesized.push({ bottom });
    }
  }

  _wireUI() {
    document.querySelectorAll('.stab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.stab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.mode = btn.dataset.mode;
        this._applyMode();
      });
    });
    document.getElementById('sounder-range')?.addEventListener('change', e => {
      const r = e.target.value;
      const m = r.match(/0-(\d+)/);
      if (m) this.range = parseInt(m[1]);
    });
    document.getElementById('sounder-freq')?.addEventListener('change', e => {
      const f = e.target.value;
      this.freq = parseInt(f);
    });
    document.getElementById('sounder-gain')?.addEventListener('input', e => {
      this.gain = parseInt(e.target.value);
      document.getElementById('sounder-gain-val').textContent = this.gain;
    });
  }

  _applyMode() {
    if (this.mode === 'echogram') {
      this.echogram.style.display = 'block';
      this.osc.style.display = 'none';
    } else if (this.mode === 'oscilloscope') {
      this.echogram.style.display = 'none';
      this.osc.style.display = 'block';
    } else { // split
      this.echogram.style.display = 'block';
      this.osc.style.display = 'block';
      this.echogram.style.width = '50%';
      this.osc.style.width = '50%';
      this.osc.style.left = '50%';
      return;
    }
    this.echogram.style.width = '100%';
    this.osc.style.width = '100%';
    this.osc.style.left = '0';
  }

  start() {
    BUS.register('sounder.depth',   { value: 24.7,  gate: 0.1,  sampleRate: 0.5,  color: '#5ce0ff', kind: 'numeric', unit: 'm', label: 'Depth', track: 'sounder', min: 0, max: 1000 });
    BUS.register('sounder.sample',  { value: 0,     gate: 0,    sampleRate: 60,   color: '#5ce0ff', kind: 'numeric', unit: '',  label: 'Sample', track: 'sounder', min: -1, max: 1 });
    BUS.on('sounder.depth',  e => this._onDepth(e));
    BUS.on('sounder.sample', e => this._onSample(e));
    this._animate();
  }

  _onDepth(evt) {
    document.getElementById('depth-val').textContent = evt.value.toFixed(1);
  }

  _onSample(evt) {
    this.sampleBuffer.push(evt.value);
    if (this.sampleBuffer.length > this.maxBuffer) this.sampleBuffer.shift();
  }

  _animate() {
    this._drawEchogram();
    this._drawOsc();
    requestAnimationFrame(() => this._animate());
  }

  _drawEchogram() {
    const ctx = this.echogramCtx;
    const w = this.echogram.width;
    const h = this.echogram.height;

    // Background
    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    // Range scale (right side)
    ctx.strokeStyle = '#143550';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#5a7e92';
    for (let d = 0; d <= this.range; d += this.range / 10) {
      const y = h - (d / this.range) * h;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
      ctx.fillText(`${d}m`, 4, y - 2);
    }

    // Scroll the echogram left
    this.scrollPos += 1.5;
    const offsetX = this.scrollPos % w;

    // Draw a moving water column slice
    const depth = BUS.get('sounder.depth') || 24;
    const bottomPx = h - (depth / this.range) * h;

    // Surface noise
    ctx.fillStyle = 'rgba(76, 255, 176, 0.15)';
    for (let x = 0; x < w; x++) {
      const n = Math.random() * 0.3;
      ctx.fillRect(x, 0, 1, 4 + n * 4);
    }

    // Plankton layer
    ctx.fillStyle = 'rgba(92, 224, 255, 0.08)';
    for (let x = 0; x < w; x++) {
      const y = h * 0.4 + Math.sin((x + this.scrollPos) * 0.05) * 5;
      ctx.fillRect(x, y, 1, 2);
    }

    // Thermocline
    ctx.fillStyle = 'rgba(255, 184, 76, 0.12)';
    for (let x = 0; x < w; x++) {
      const y = h * 0.55 + Math.sin((x + this.scrollPos) * 0.02) * 3;
      ctx.fillRect(x, y, 1, 1);
    }

    // Fish arches (synthetic, with motion)
    for (let f = 0; f < 5; f++) {
      const fx = ((f * 150 + this.scrollPos * 0.7) % (w + 100)) - 50;
      const archY = h * 0.35 + f * 8;
      ctx.strokeStyle = '#4cffb0';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (let dx = -25; dx < 25; dx++) {
        const ay = archY + Math.cos(dx * 0.1) * 6;
        if (dx === -25) ctx.moveTo(fx + dx, ay);
        else ctx.lineTo(fx + dx, ay);
      }
      ctx.stroke();
    }

    // Bottom (with synthetic profile)
    ctx.fillStyle = 'rgba(255, 184, 76, 0.4)';
    ctx.strokeStyle = '#ffb84c';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const synoIdx = Math.floor((x + this.scrollPos) / w * 800) % this.synthesized.length;
      const b = this.synthesized[synoIdx].bottom;
      const by = h - (b / this.range) * h;
      if (x === 0) ctx.moveTo(x, by);
      else ctx.lineTo(x, by);
    }
    // Fill the bottom
    for (let x = 0; x < w; x += 4) {
      const synoIdx = Math.floor((x + this.scrollPos) / w * 800) % this.synthesized.length;
      const b = this.synthesized[synoIdx].bottom;
      const by = h - (b / this.range) * h;
      ctx.fillRect(x, by, 4, h - by);
    }
    ctx.stroke();

    // Depth cursor
    ctx.strokeStyle = '#ff5cb0';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(0, bottomPx);
    ctx.lineTo(w, bottomPx);
    ctx.stroke();
    ctx.setLineDash([]);

    // Track state indicator
    ctx.fillStyle = '#4cffb0';
    ctx.font = '10px monospace';
    ctx.fillText(`FREQ ${this.freq}kHz  GAIN ${this.gain}  RANGE 0-${this.range}m  DPT ${depth.toFixed(1)}m`, 10, h - 6);
  }

  _drawOsc() {
    const ctx = this.oscCtx;
    const w = this.osc.width;
    const h = this.osc.height;
    ctx.fillStyle = '#001018';
    ctx.fillRect(0, 0, w, h);

    // Grid
    ctx.strokeStyle = '#143550';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {
      const x = (i / 10) * w;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let i = 0; i <= 4; i++) {
      const y = (i / 4) * h;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Trigger line
    ctx.strokeStyle = '#1f5a85';
    ctx.beginPath();
    ctx.moveTo(0, h * 0.5);
    ctx.lineTo(w, h * 0.5);
    ctx.stroke();

    // Waveform
    if (this.sampleBuffer.length > 1) {
      ctx.strokeStyle = '#5ce0ff';
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#5ce0ff';
      ctx.shadowBlur = 4;
      ctx.beginPath();
      const step = w / this.maxBuffer;
      for (let i = 0; i < this.sampleBuffer.length; i++) {
        const x = i * step;
        const v = this.sampleBuffer[i];
        const y = h * 0.5 - v * h * 0.4;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // Labels
    ctx.fillStyle = '#5a7e92';
    ctx.font = '10px monospace';
    ctx.fillText('OSC', 8, 14);
    ctx.fillText(`SR 60Hz  BUF ${this.sampleBuffer.length}`, 8, h - 6);
  }
}

window.SounderView = SounderView;
