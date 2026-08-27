/* ════════════════════════════════════════════════════════════════
   cameras.js — Camera feeds as DAW-synoptic frames
   Each camera is a "frame" on the DAW. The frame has ticks:
     - GPS position
     - Sounder depth (if relevant)
     - Time
     - Camera tick (frame number)
   ════════════════════════════════════════════════════════════════ */

class CamerasView {
  constructor() {
    this.area = document.getElementById('cam-area');
    this.mode = 'grid';
    this.cameras = [
      { id: 'bow',        name: 'BOW',        enabled: true, kind: 'outside', az: 0,   el: 5 },
      { id: 'stern',      name: 'STERN',      enabled: true, kind: 'outside', az: 180, el: 5 },
      { id: 'port',       name: 'PORT',       enabled: true, kind: 'outside', az: 270, el: 5 },
      { id: 'stbd',       name: 'STBD',       enabled: true, kind: 'outside', az: 90,  el: 5 },
      { id: 'engineroom', name: 'ENGINE',     enabled: false, kind: 'inside', az: 0,   el: 0 },
      { id: 'wheelhouse', name: 'WHEELHOUSE', enabled: false, kind: 'inside', az: 0,   el: 0 },
    ];
    this.frames = new Map(); // id -> { canvas, ctx, ticks: [], lastFrame: 0 }
    this._wireUI();
    this._render();
  }

  _wireUI() {
    document.querySelectorAll('.cmode').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.cmode').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.mode = btn.dataset.cmode;
        this._render();
      });
    });
    document.querySelectorAll('.cam-tick').forEach(cb => {
      cb.addEventListener('change', () => {
        const cam = this.cameras.find(c => c.id === cb.value);
        if (cam) cam.enabled = cb.checked;
        this._render();
      });
    });
  }

  start() {
    BUS.register('camera.tick', { value: 0, gate: 1, sampleRate: 30, color: '#ffe85c', kind: 'numeric', unit: '', label: 'CamTick', track: 'cameras', min: 0, max: 1e9 });
    BUS.on('camera.tick', e => this._onTick(e));
    this._animate();
  }

  _onTick(evt) {
    // Stamp each enabled camera with a frame tick + GPS + time
    for (const cam of this.cameras) {
      if (!cam.enabled) continue;
      const f = this.frames.get(cam.id);
      if (!f) continue;
      f.tickData = {
        tick: evt.value,
        lat: BUS.get('gps.lat'),
        lon: BUS.get('gps.lon'),
        sog: BUS.get('gps.sog'),
        cog: BUS.get('gps.cog'),
        depth: BUS.get('sounder.depth'),
        rudder: BUS.get('autopilot.rudder'),
        hdg: BUS.get('compass.heading'),
        time: new Date().toISOString().split('T')[1].slice(0, 8),
      };
    }
  }

  _render() {
    const enabled = this.cameras.filter(c => c.enabled);
    let cols, rows;
    if (this.mode === 'single') {
      cols = 1; rows = 1;
    } else if (this.mode === 'synoptic') {
      cols = 1; rows = 1;
    } else {
      cols = Math.min(3, enabled.length);
      rows = Math.ceil(enabled.length / cols);
    }

    this.area.innerHTML = '';
    this.area.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    this.area.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    this.area.classList.remove('single-mode', 'synoptic-mode');
    if (this.mode === 'single') this.area.classList.add('single-mode');
    if (this.mode === 'synoptic') this.area.classList.add('synoptic-mode');

    for (const cam of enabled) {
      const tile = document.createElement('div');
      tile.className = 'cam-tile';
      tile.dataset.camId = cam.id;
      const label = document.createElement('div');
      label.className = 'cam-tile-label';
      label.textContent = cam.name;
      tile.appendChild(label);
      const tickLabel = document.createElement('div');
      tickLabel.className = 'cam-tile-tick';
      tickLabel.id = `cam-${cam.id}-tick`;
      tickLabel.textContent = 'tick 0';
      tile.appendChild(tickLabel);
      const marker = document.createElement('div');
      marker.className = 'cam-tile-marker';
      marker.id = `cam-${cam.id}-marker`;
      tile.appendChild(marker);
      const canvas = document.createElement('canvas');
      canvas.width = 320;
      canvas.height = 200;
      tile.appendChild(canvas);
      this.area.appendChild(tile);
      const ctx = canvas.getContext('2d');
      this.frames.set(cam.id, { canvas, ctx, tile, tickData: null });
    }
  }

  _animate() {
    for (const [id, f] of this.frames) {
      this._drawCamera(id, f);
    }
    requestAnimationFrame(() => this._animate());
  }

  _drawCamera(id, frame) {
    const ctx = frame.ctx;
    const w = frame.canvas.width;
    const h = frame.canvas.height;
    const cam = this.cameras.find(c => c.id === id);
    if (!cam) return;

    // ─── SYNOPTIC MODE: render a synoptic view with all 4 camera angles overlaid + DAW bars ───
    if (this.mode === 'synoptic') {
      this._drawSynoptic(ctx, w, h, cam);
    } else {
      this._drawStandard(ctx, w, h, cam);
    }

    // Update tick labels
    if (frame.tickData) {
      const tickEl = document.getElementById(`cam-${id}-tick`);
      if (tickEl) tickEl.textContent = `T ${frame.tickData.tick}`;
      const markerEl = document.getElementById(`cam-${id}-marker`);
      if (markerEl && this.mode === 'synoptic') {
        markerEl.textContent = `${frame.tickData.time}  ${frame.tickData.hdg?.toFixed(0) || 0}°M  ${frame.tickData.depth?.toFixed(1) || 0}m`;
      }
    }
  }

  _drawSynoptic(ctx, w, h, cam) {
    // Dark background
    ctx.fillStyle = '#000408';
    ctx.fillRect(0, 0, w, h);

    // Quartered synoptic — bow/stern/port/stbd in 4 quadrants
    const qw = w / 2, qh = h / 2;
    const views = [
      { name: 'BOW',  az: 0 },
      { name: 'PORT', az: 270 },
      { name: 'STBD', az: 90 },
      { name: 'STERN', az: 180 },
    ];
    for (let i = 0; i < 4; i++) {
      const v = views[i];
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = col * qw;
      const y = row * qh;
      ctx.save();
      ctx.beginPath();
      ctx.rect(x, y, qw, qh);
      ctx.clip();
      this._drawCameraView(ctx, x, y, qw, qh, v, cam);
      ctx.restore();
      // Border
      ctx.strokeStyle = '#143550';
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, qw, qh);
      // Label
      ctx.fillStyle = '#4cffb0';
      ctx.font = 'bold 14px monospace';
      ctx.fillText(v.name, x + 6, y + 16);
    }

    // ─── DAW BARS: GPS / Sounder / Heading / Rudder ───
    const barY = qh - 32;
    const barX = qw + 4;
    const barW = w - barX - 4;
    const barH = 4;
    const tick = frame.tickData || {};
    const hdg = (tick.hdg ?? 0) / 360;
    const cog = (tick.cog ?? 0) / 360;
    const depth = Math.min(1, (tick.depth ?? 0) / 100);
    const rudder = ((tick.rudder ?? 0) + 30) / 60;
    const sog = Math.min(1, (tick.sog ?? 0) / 12);

    // Heading bar
    ctx.fillStyle = '#143550';
    ctx.fillRect(barX, barY, barW, barH);
    ctx.fillStyle = '#4cffb0';
    ctx.fillRect(barX + hdg * barW - 2, barY - 1, 4, barH + 2);
    ctx.fillStyle = '#ffb84c';
    ctx.fillRect(barX + cog * barW - 1, barY - 2, 2, barH + 4);

    // Depth bar
    ctx.fillStyle = '#143550';
    ctx.fillRect(barX, barY + 8, barW, barH);
    ctx.fillStyle = '#5ce0ff';
    ctx.fillRect(barX, barY + 8, depth * barW, barH);

    // Rudder bar (centered)
    ctx.fillStyle = '#143550';
    ctx.fillRect(barX, barY + 16, barW, barH);
    ctx.fillStyle = '#ff5cb0';
    ctx.fillRect(barX + rudder * barW - 2, barY + 15, 4, barH + 2);

    // SOG bar
    ctx.fillStyle = '#143550';
    ctx.fillRect(barX, barY + 24, barW, barH);
    ctx.fillStyle = '#ffb84c';
    ctx.fillRect(barX, barY + 24, sog * barW, barH);

    // Time/date stamp
    if (tick.time) {
      ctx.fillStyle = '#ffe85c';
      ctx.font = 'bold 16px monospace';
      ctx.fillText(tick.time, 8, h - 8);
    }
  }

  _drawStandard(ctx, w, h, cam) {
    // Standard camera view: render a synthetic "outside" or "inside" scene
    if (cam.kind === 'outside') {
      this._drawOutside(ctx, w, h, cam);
    } else {
      this._drawInside(ctx, w, h, cam);
    }

    // Crosshair (camera-typical)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(w/2, 0);
    ctx.lineTo(w/2, h);
    ctx.moveTo(0, h/2);
    ctx.lineTo(w, h/2);
    ctx.stroke();

    // Camera info overlay
    const tick = frame.tickData || {};
    if (tick.time) {
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(4, h - 32, 200, 28);
      ctx.fillStyle = '#ffe85c';
      ctx.font = '11px monospace';
      ctx.fillText(`${tick.time}`, 8, h - 18);
      ctx.fillText(`HDG ${(tick.hdg ?? 0).toFixed(0)}°  SOG ${(tick.sog ?? 0).toFixed(1)}kt  DPT ${(tick.depth ?? 0).toFixed(1)}m`, 8, h - 6);
    }
  }

  _drawCameraView(ctx, x, y, w, h, view, cam) {
    // Helper for synoptic quadrants
    const innerCtx = ctx;
    innerCtx.save();
    innerCtx.translate(x, y);

    // Mini sky/sea
    const grad = innerCtx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, '#0a1a2a');
    grad.addColorStop(0.5, '#143550');
    grad.addColorStop(0.5, '#021624');
    grad.addColorStop(1, '#010a14');
    innerCtx.fillStyle = grad;
    innerCtx.fillRect(0, 0, w, h);

    // Horizon line
    innerCtx.strokeStyle = '#1f5a85';
    innerCtx.lineWidth = 1;
    innerCtx.beginPath();
    innerCtx.moveTo(0, h/2);
    innerCtx.lineTo(w, h/2);
    innerCtx.stroke();

    // Sea ripples
    innerCtx.strokeStyle = '#143550';
    innerCtx.lineWidth = 0.5;
    for (let r = 0; r < 4; r++) {
      const yy = h/2 + 10 + r * 8;
      innerCtx.beginPath();
      for (let xx = 0; xx < w; xx += 4) {
        const yy2 = yy + Math.sin(xx * 0.05 + r + Date.now() * 0.001) * 1.5;
        if (xx === 0) innerCtx.moveTo(xx, yy2);
        else innerCtx.lineTo(xx, yy2);
      }
      innerCtx.stroke();
    }

    // Camera-specific markers
    if (view.name === 'BOW') {
      // Bow wave
      innerCtx.fillStyle = 'rgba(76, 255, 176, 0.1)';
      innerCtx.beginPath();
      innerCtx.moveTo(w/2, h/2);
      innerCtx.lineTo(w/2 - 60, h);
      innerCtx.lineTo(w/2 + 60, h);
      innerCtx.closePath();
      innerCtx.fill();
    }

    innerCtx.restore();
  }

  _drawOutside(ctx, w, h, cam) {
    // Sky gradient
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    const t = (Date.now() / 3000) % 1;
    if (t < 0.3) {
      // Dawn
      grad.addColorStop(0, '#1a0a2a');
      grad.addColorStop(0.5, '#3a1a3a');
      grad.addColorStop(1, '#5a3030');
    } else if (t < 0.7) {
      // Day
      grad.addColorStop(0, '#143550');
      grad.addColorStop(0.4, '#5a8eb0');
      grad.addColorStop(0.5, '#a0c0d0');
      grad.addColorStop(1, '#1f5a85');
    } else {
      // Dusk
      grad.addColorStop(0, '#1a1a2a');
      grad.addColorStop(0.5, '#5a3030');
      grad.addColorStop(1, '#3a1a1a');
    }
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Sun/moon
    const sx = w * 0.7, sy = h * 0.2;
    ctx.fillStyle = '#fff5b0';
    ctx.shadowColor = '#fff5b0';
    ctx.shadowBlur = 30;
    ctx.beginPath();
    ctx.arc(sx, sy, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Sea
    const seaGrad = ctx.createLinearGradient(0, h/2, 0, h);
    seaGrad.addColorStop(0, '#1f5a85');
    seaGrad.addColorStop(1, '#021624');
    ctx.fillStyle = seaGrad;
    ctx.fillRect(0, h/2, w, h/2);

    // Waves
    ctx.strokeStyle = 'rgba(76, 255, 176, 0.3)';
    ctx.lineWidth = 1;
    for (let r = 0; r < 8; r++) {
      const yy = h/2 + 8 + r * 12;
      const phase = (Date.now() / 200) + r;
      ctx.beginPath();
      for (let xx = 0; xx < w; xx += 2) {
        const yy2 = yy + Math.sin(xx * 0.04 + phase) * 1.5;
        if (xx === 0) ctx.moveTo(xx, yy2);
        else ctx.lineTo(xx, yy2);
      }
      ctx.stroke();
    }

    // Horizon
    ctx.strokeStyle = '#1f5a85';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h/2);
    ctx.lineTo(w, h/2);
    ctx.stroke();

    // Camera direction indicator
    ctx.fillStyle = 'rgba(76, 255, 176, 0.6)';
    ctx.font = '10px monospace';
    ctx.fillText(`AZ ${cam.az}°`, w - 50, 14);
  }

  _drawInside(ctx, w, h, cam) {
    // Engine room / wheelhouse
    if (cam.id === 'engineroom') {
      ctx.fillStyle = '#1a1208';
      ctx.fillRect(0, 0, w, h);
      // Big engine block
      ctx.fillStyle = '#2a2418';
      ctx.fillRect(w/4, h/3, w/2, h/2);
      ctx.strokeStyle = '#5a4a30';
      ctx.lineWidth = 2;
      ctx.strokeRect(w/4, h/3, w/2, h/2);
      // RPM gauge
      const rpm = BUS.get('engine.rpm') || 0;
      const angle = (rpm / 2500) * Math.PI * 1.5 - Math.PI * 0.75;
      ctx.strokeStyle = '#4cffb0';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(w/2, h/2, 50, -Math.PI * 0.75, angle);
      ctx.stroke();
      ctx.fillStyle = '#4cffb0';
      ctx.font = 'bold 16px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${rpm.toFixed(0)} RPM`, w/2, h/2 + 30);
    } else {
      // Wheelhouse
      ctx.fillStyle = '#0a1a26';
      ctx.fillRect(0, 0, w, h);
      // Window
      ctx.fillStyle = '#143550';
      ctx.fillRect(w/4, h/4, w/2, h/2);
      // Compass on dashboard
      const heading = BUS.get('compass.heading') || 0;
      ctx.fillStyle = '#4cffb0';
      ctx.font = 'bold 24px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`${heading.toFixed(0)}°`, w/2, h - 30);
    }
  }
}

window.CamerasView = CamerasView;
