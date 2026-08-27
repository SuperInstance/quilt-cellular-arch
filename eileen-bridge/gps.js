/* ════════════════════════════════════════════════════════════════
   gps.js — Lat/Lon rendered as a Nav Chart
   ════════════════════════════════════════════════════════════════ */

class GPSView {
  constructor() {
    this.canvas = document.getElementById('canvas-navchart');
    this.ctx = this.canvas.getContext('2d');
    this.track = [];          // past positions
    this.maxTrack = 500;
    this.waypoints = [
      { lat: 44.6526, lon: -124.0535, name: 'Newport Bar', symbol: 'home' },
      { lat: 44.6200, lon: -124.0700, name: 'YB', symbol: 'waypoint' },
      { lat: 44.6800, lon: -124.0200, name: 'Tuna Ground', symbol: 'fish' },
    ];
    this.bounds = {
      minLat: 44.60, maxLat: 44.71,
      minLon: -124.10, maxLon: -124.00,
    };
  }

  start() {
    BUS.register('gps.lat',   { value: 44.6526, gate: 0.00001, sampleRate: 2, color: '#ff5cb0', kind: 'numeric', unit: '°', label: 'Lat', track: 'gps', min: -90, max: 90 });
    BUS.register('gps.lon',   { value: -124.0535, gate: 0.00001, sampleRate: 2, color: '#ff5cb0', kind: 'numeric', unit: '°', label: 'Lon', track: 'gps', min: -180, max: 180 });
    BUS.register('gps.sog',   { value: 6.2, gate: 0.1, sampleRate: 1, color: '#ff5cb0', kind: 'numeric', unit: 'kt', label: 'SOG', track: 'gps', min: 0, max: 30 });
    BUS.register('gps.cog',   { value: 88, gate: 1, sampleRate: 1, color: '#ff5cb0', kind: 'numeric', unit: '°T', label: 'COG', track: 'gps', min: 0, max: 360 });
    BUS.on('gps.lat', e => this._onLat(e));
    BUS.on('gps.lon', e => this._onLon(e));
    BUS.on('gps.sog', e => this._onSog(e));
    BUS.on('gps.cog', e => this._onCog(e));
    this._animate();
  }

  _onLat(evt) {
    document.getElementById('lat-val').textContent = evt.value.toFixed(5) + '°N';
    this._record();
  }
  _onLon(evt) {
    document.getElementById('lon-val').textContent = Math.abs(evt.value).toFixed(5) + '°W';
    this._record();
  }
  _onSog(evt) {
    document.getElementById('sog-val').textContent = evt.value.toFixed(1);
  }
  _onCog(evt) {
    document.getElementById('cog-val').textContent = evt.value.toFixed(0);
  }

  _record() {
    const lat = BUS.get('gps.lat');
    const lon = BUS.get('gps.lon');
    if (lat === null || lon === null) return;
    this.track.push({ lat, lon });
    if (this.track.length > this.maxTrack) this.track.shift();

    // Update waypoint distance
    let minDist = Infinity, minWp = null;
    for (const wp of this.waypoints) {
      const d = this._distance(lat, lon, wp.lat, wp.lon);
      if (d < minDist) { minDist = d; minWp = wp; }
    }
    if (minWp) {
      document.getElementById('wp-val').textContent = minWp.name;
      document.getElementById('dist-val').textContent = minDist.toFixed(2);
      // ETA at current SOG
      const sog = BUS.get('gps.sog') || 1;
      const hours = minDist / sog;
      const h = Math.floor(hours);
      const m = Math.floor((hours - h) * 60);
      document.getElementById('eta-val').textContent = `${h}h${m.toString().padStart(2, '0')}`;
    }
  }

  _distance(lat1, lon1, lat2, lon2) {
    // Haversine
    const R = 3440.065; // nm
    const toR = d => d * Math.PI / 180;
    const dLat = toR(lat2 - lat1);
    const dLon = toR(lon2 - lon1);
    const a = Math.sin(dLat/2)**2 + Math.cos(toR(lat1)) * Math.cos(toR(lat2)) * Math.sin(dLon/2)**2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  _project(lat, lon) {
    const w = this.canvas.width;
    const h = this.canvas.height;
    const x = ((lon - this.bounds.minLon) / (this.bounds.maxLon - this.bounds.minLon)) * w;
    const y = h - ((lat - this.bounds.minLat) / (this.bounds.maxLat - this.bounds.minLat)) * h;
    return { x, y };
  }

  _animate() {
    this._draw();
    requestAnimationFrame(() => this._animate());
  }

  _draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Background (sea blue gradient)
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, '#021624');
    grad.addColorStop(1, '#010a14');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Grid (lat/lon)
    ctx.strokeStyle = '#143550';
    ctx.lineWidth = 1;
    ctx.font = '9px monospace';
    ctx.fillStyle = '#5a7e92';
    for (let lon = Math.floor(this.bounds.minLon * 10) / 10; lon <= this.bounds.maxLon; lon += 0.02) {
      const { x } = this._project((this.bounds.minLat + this.bounds.maxLat) / 2, lon);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
      ctx.fillText(`${lon.toFixed(2)}°`, x + 2, h - 4);
    }
    for (let lat = Math.floor(this.bounds.minLat * 10) / 10; lat <= this.bounds.maxLat; lat += 0.02) {
      const { y } = this._project(lat, this.bounds.minLon);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
      ctx.fillText(`${lat.toFixed(2)}°N`, 4, y - 2);
    }

    // Compass rose (small, top-right)
    this._drawCompassRose(w - 50, 50, 30);

    // Range scale (bottom-left)
    this._drawScale(20, h - 30);

    // Track
    if (this.track.length > 1) {
      ctx.strokeStyle = '#ff5cb0';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#ff5cb0';
      ctx.shadowBlur = 4;
      ctx.beginPath();
      for (let i = 0; i < this.track.length; i++) {
        const { x, y } = this._project(this.track[i].lat, this.track[i].lon);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // Waypoints
    for (const wp of this.waypoints) {
      const { x, y } = this._project(wp.lat, wp.lon);
      ctx.fillStyle = '#ffb84c';
      ctx.strokeStyle = '#ffb84c';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.stroke();
      ctx.font = '10px monospace';
      ctx.fillText(wp.name, x + 10, y + 3);
    }

    // Current position
    const lat = BUS.get('gps.lat');
    const lon = BUS.get('gps.lon');
    if (lat !== null && lon !== null) {
      const { x, y } = this._project(lat, lon);
      // Boat shape (triangle, rotated by COG)
      const cog = BUS.get('gps.cog') || 0;
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate((cog - 90) * Math.PI / 180);
      ctx.fillStyle = '#4cffb0';
      ctx.strokeStyle = '#4cffb0';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#4cffb0';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.moveTo(0, -12);
      ctx.lineTo(-7, 8);
      ctx.lineTo(7, 8);
      ctx.closePath();
      ctx.fill();
      ctx.shadowBlur = 0;
      // Heading line
      ctx.strokeStyle = 'rgba(76, 255, 176, 0.4)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, -50);
      ctx.stroke();
      ctx.restore();

      // Pulse
      const t = (Date.now() % 2000) / 2000;
      ctx.strokeStyle = `rgba(76, 255, 176, ${1 - t})`;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(x, y, 8 + t * 20, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  _drawCompassRose(x, y, r) {
    const ctx = this.ctx;
    ctx.strokeStyle = '#5a7e92';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = '#5a7e92';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('N', x, y - r - 6);
    ctx.fillText('E', x + r + 6, y);
    ctx.fillText('S', x, y + r + 6);
    ctx.fillText('W', x - r - 6, y);
  }

  _drawScale(x, y) {
    const ctx = this.ctx;
    // 0.5 nm scale bar
    const lat = BUS.get('gps.lat') || 44.65;
    const lon1 = this.bounds.minLon;
    const lon2 = lon1 + 0.01;
    const { x: x1 } = this._project(lat, lon1);
    const { x: x2 } = this._project(lat, lon2);
    const d = this._distance(lat, lon1, lat, lon2);
    const pxPerNm = (x2 - x1) / d;
    const scaleNm = 0.5;
    const scalePx = scaleNm * pxPerNm;
    ctx.strokeStyle = '#c8e1f0';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + scalePx, y);
    ctx.stroke();
    ctx.fillStyle = '#c8e1f0';
    ctx.font = '10px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(`${scaleNm} nm`, x, y - 4);
  }
}

window.GPSView = GPSView;
