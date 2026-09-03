/**
 * AltDP_3rd CAD Vector Drawing Engine (DrawView)
 * Interactive SVG CAD viewer for structural rebar details and schedule tables.
 */

const DrawCad = {
  svg: null,
  zoom: 1.0,
  panX: 0,
  panY: 0,
  isDragging: false,
  startX: 0,
  startY: 0,

  init() {
    this.svg = document.getElementById('cadSvgViewport');
    if (!this.svg) return;

    this.attachEvents();
    this.renderDrawing('section_rebar');
  },

  renderDrawing(type) {
    if (!this.svg) return;

    const width = this.svg.clientWidth || 800;
    const height = this.svg.clientHeight || 500;
    const cx = width / 2;
    const cy = height / 2;

    let content = '';

    if (type === 'section_rebar') {
      // Draw RC Beam Cross Section (b=400, h=600)
      const scale = 0.5;
      const bw = 400 * scale;
      const bh = 600 * scale;
      const x0 = cx - bw / 2;
      const y0 = cy - bh / 2;

      // Concrete outline
      content += `<rect x="${x0}" y="${y0}" width="${bw}" height="${bh}" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />`;
      // Rebar stirrup
      content += `<rect x="${x0 + 15}" y="${y0 + 15}" width="${bw - 30}" height="${bh - 30}" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4 2" />`;
      // Top Rebars (4-D22)
      for (let i = 0; i < 4; i++) {
        const rx = x0 + 25 + i * ((bw - 50) / 3);
        content += `<circle cx="${rx}" cy="${y0 + 25}" r="6" fill="#ef4444" stroke="#fff" stroke-width="1" />`;
      }
      // Bottom Rebars (4-D25)
      for (let i = 0; i < 4; i++) {
        const rx = x0 + 25 + i * ((bw - 50) / 3);
        content += `<circle cx="${rx}" cy="${y0 + bh - 25}" r="7" fill="#10b981" stroke="#fff" stroke-width="1" />`;
      }
      // Dimensions
      content += `<line x1="${x0}" y1="${y0 - 20}" x2="${x0 + bw}" y2="${y0 - 20}" stroke="#94a3b8" stroke-width="1" />`;
      content += `<text x="${cx}" y="${y0 - 25}" fill="#94a3b8" font-size="12" text-anchor="middle" font-family="monospace">400 mm</text>`;
      content += `<line x1="${x0 - 20}" y1="${y0}" x2="${x0 - 20}" y2="${y0 + bh}" stroke="#94a3b8" stroke-width="1" />`;
      content += `<text x="${x0 - 28}" y="${cy}" fill="#94a3b8" font-size="12" text-anchor="middle" font-family="monospace" transform="rotate(-90 ${x0 - 28} ${cy})">600 mm</text>`;
      // Title
      content += `<text x="${cx}" y="${y0 + bh + 40}" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">B1 SECTION (400x600)</text>`;
    } else {
      // Schedule Table
      content += `
        <rect x="50" y="50" width="700" height="300" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
        <line x1="50" y1="90" x2="750" y2="90" stroke="#38bdf8" stroke-width="1"/>
        <text x="70" y="75" fill="#f8fafc" font-size="14" font-weight="bold">BEAM SCHEDULE TABLE (KDS 14 20 00)</text>
        <text x="70" y="130" fill="#94a3b8" font-size="12">ID: B1 | Size: 400x600 | Top: 4-D22 | Bot: 4-D25 | Stirrup: D10@150</text>
        <text x="70" y="160" fill="#94a3b8" font-size="12">ID: B2 | Size: 400x500 | Top: 3-D22 | Bot: 4-D22 | Stirrup: D10@200</text>
        <text x="70" y="190" fill="#94a3b8" font-size="12">ID: C1 | Size: 600x600 | Main: 12-D25 | Tie: D10@200</text>
      `;
    }

    this.svg.innerHTML = `
      <g transform="translate(${this.panX}, ${this.panY}) scale(${this.zoom})">
        ${content}
      </g>
    `;
  },

  attachEvents() {
    const typeSelect = document.getElementById('draw-type-select');
    if (typeSelect) {
      typeSelect.addEventListener('change', (e) => this.renderDrawing(e.target.value));
    }

    // Zoom and Pan
    this.svg.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoom *= delta;
      this.renderDrawing(document.getElementById('draw-type-select')?.value || 'section_rebar');
    });

    this.svg.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.startX = e.clientX - this.panX;
      this.startY = e.clientY - this.panY;
      this.svg.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      this.panX = e.clientX - this.startX;
      this.panY = e.clientY - this.startY;
      this.renderDrawing(document.getElementById('draw-type-select')?.value || 'section_rebar');
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
      if (this.svg) this.svg.style.cursor = 'grab';
    });
  }
};

window.DrawCad = DrawCad;
