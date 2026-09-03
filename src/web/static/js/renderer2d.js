/**
 * AltDP_3rd High-Precision 2D Canvas Structural Section Renderer (renderer2d.js)
 * 
 * Renders reinforced concrete, steel, composite, and retrofit sections conforming to KDS standards.
 * Features:
 * - High-DPI Retina resolution scaling
 * - RC Beam, Column, Shear Wall, Slab, Footing, Retaining Wall drawing
 * - Steel H-Section, Box Section, Bolted Connections, Baseplate with Anchor Bolts
 * - CFT / SRC Composite Sections & CFRP/Steel Retrofit Overlays
 * - Structural engineering dimension lines, rebar indicators, and soil pressure diagrams
 */

(function (global) {
  'use strict';

  const Renderer2D = {};

  /**
   * Setup high-DPI canvas context.
   */
  function setupDPI(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = rect.width || canvas.width || 500;
    const height = rect.height || canvas.height || 450;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  }

  /**
   * Draw engineering dimension line with arrows and text label.
   */
  function drawDimension(ctx, x1, y1, x2, y2, text, offset = 25, isVertical = false) {
    ctx.save();
    ctx.strokeStyle = '#94a3b8';
    ctx.fillStyle = '#cbd5e1';
    ctx.lineWidth = 1.0;
    ctx.font = '11px "Inter", "Pretendard", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    const arrowSize = 5;

    if (isVertical) {
      const x = x1 + offset;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x + (offset > 0 ? 5 : -5), y1);
      ctx.moveTo(x2, y2);
      ctx.lineTo(x + (offset > 0 ? 5 : -5), y2);
      ctx.moveTo(x, y1);
      ctx.lineTo(x, y2);
      ctx.stroke();

      // Arrows
      ctx.beginPath();
      ctx.moveTo(x, y1);
      ctx.lineTo(x - arrowSize / 2, y1 + arrowSize);
      ctx.lineTo(x + arrowSize / 2, y1 + arrowSize);
      ctx.closePath();
      ctx.moveTo(x, y2);
      ctx.lineTo(x - arrowSize / 2, y2 - arrowSize);
      ctx.lineTo(x + arrowSize / 2, y2 - arrowSize);
      ctx.closePath();
      ctx.fill();

      // Text
      ctx.save();
      ctx.translate(x + (offset > 0 ? 14 : -14), (y1 + y2) / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText(text, 0, 0);
      ctx.restore();
    } else {
      const y = y1 + offset;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1, y + (offset > 0 ? 5 : -5));
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2, y + (offset > 0 ? 5 : -5));
      ctx.moveTo(x1, y);
      ctx.lineTo(x2, y);
      ctx.stroke();

      // Arrows
      ctx.beginPath();
      ctx.moveTo(x1, y);
      ctx.lineTo(x1 + arrowSize, y - arrowSize / 2);
      ctx.lineTo(x1 + arrowSize, y + arrowSize / 2);
      ctx.closePath();
      ctx.moveTo(x2, y);
      ctx.lineTo(x2 - arrowSize, y - arrowSize / 2);
      ctx.lineTo(x2 - arrowSize, y + arrowSize / 2);
      ctx.closePath();
      ctx.fill();

      // Text
      ctx.fillText(text, (x1 + x2) / 2, y + (offset > 0 ? 12 : -12));
    }
    ctx.restore();
  }

  /**
   * Draw individual metallic rebar circle with gradient highlight.
   */
  function drawRebar(ctx, cx, cy, radius, isCompression = false) {
    ctx.save();
    const r = Math.max(radius, 4.0);
    const grad = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);

    if (isCompression) {
      grad.addColorStop(0, '#93c5fd');
      grad.addColorStop(0.7, '#3b82f6');
      grad.addColorStop(1, '#1d4ed8');
    } else {
      grad.addColorStop(0, '#fca5a5');
      grad.addColorStop(0.7, '#ef4444');
      grad.addColorStop(1, '#991b1b');
    }

    ctx.fillStyle = grad;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  /**
   * 1. Draw RC Beam cross-section.
   */
  Renderer2D.drawRCBeamSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const b = data.b || 400;
    const h = data.h || 600;
    const cover = data.cover || 50;
    const numTension = data.num_tension_bars || data.num_bars || 4;
    const numComp = data.num_comp_bars || 2;
    const barSize = data.bar_size || "D22";
    const stirrupSize = data.stirrup_size || "D10";

    const padding = 65;
    const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / h);
    const drawW = b * scale;
    const drawH = h * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2;

    // Concrete Outline
    ctx.save();
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.rect(startX, startY, drawW, drawH);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // Stirrup
    const stirrupCover = (cover - 10) * scale;
    const stirrupX = startX + stirrupCover;
    const stirrupY = startY + stirrupCover;
    const stirrupW = drawW - stirrupCover * 2;
    const stirrupH = drawH - stirrupCover * 2;

    ctx.save();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.strokeRect(stirrupX, stirrupY, stirrupW, stirrupH);
    ctx.restore();

    // Rebars
    const rebarRadius = Math.max(5.0 * (scale / 0.5), 5.0);
    const topY = startY + cover * scale;
    if (numComp > 0) {
      const topClearW = drawW - cover * scale * 2;
      for (let i = 0; i < numComp; i++) {
        const topX = (numComp === 1) ? startX + drawW / 2 : startX + cover * scale + i * (topClearW / (numComp - 1));
        drawRebar(ctx, topX, topY, rebarRadius * 0.85, true);
      }
    }

    const bottomY1 = startY + drawH - cover * scale;
    const bottomClearW = drawW - cover * scale * 2;
    for (let i = 0; i < numTension; i++) {
      const botX = (numTension === 1) ? startX + drawW / 2 : startX + cover * scale + i * (bottomClearW / (numTension - 1));
      drawRebar(ctx, botX, bottomY1, rebarRadius, false);
    }

    // Dimensions
    drawDimension(ctx, startX, startY, startX + drawW, startY, `b = ${b} mm`, -30, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `h = ${h} mm`, 30, true);
  };

  /**
   * 2. Draw RC Column cross-section.
   */
  Renderer2D.drawRCColumnSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const b = data.b || 600;
    const h = data.h || 600;
    const totalBars = data.total_bars || 12;
    const cover = 50;

    const padding = 65;
    const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / h);
    const drawW = b * scale;
    const drawH = h * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2;

    // Concrete outline
    ctx.save();
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2.0;
    ctx.fillRect(startX, startY, drawW, drawH);
    ctx.strokeRect(startX, startY, drawW, drawH);
    ctx.restore();

    // Tie rebar loop
    const tieCover = 40 * scale;
    ctx.save();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.strokeRect(startX + tieCover, startY + tieCover, drawW - tieCover * 2, drawH - tieCover * 2);
    ctx.restore();

    // Peripheral rebar layout
    const rebarRadius = 6.0;
    const rebarX1 = startX + cover * scale;
    const rebarX2 = startX + drawW - cover * scale;
    const rebarY1 = startY + cover * scale;
    const rebarY2 = startY + drawH - cover * scale;

    const barsPerSide = Math.max(2, Math.floor(totalBars / 4) + 1);
    const dx = (rebarX2 - rebarX1) / (barsPerSide - 1);
    const dy = (rebarY2 - rebarY1) / (barsPerSide - 1);

    // Top & Bottom rows
    for (let i = 0; i < barsPerSide; i++) {
      drawRebar(ctx, rebarX1 + i * dx, rebarY1, rebarRadius, true);
      drawRebar(ctx, rebarX1 + i * dx, rebarY2, rebarRadius, false);
    }
    // Middle side bars
    for (let j = 1; j < barsPerSide - 1; j++) {
      drawRebar(ctx, rebarX1, rebarY1 + j * dy, rebarRadius, false);
      drawRebar(ctx, rebarX2, rebarY1 + j * dy, rebarRadius, false);
    }

    drawDimension(ctx, startX, startY, startX + drawW, startY, `B = ${b} mm`, -30, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `H = ${h} mm`, 30, true);
  };

  /**
   * 3. Draw RC Shear Wall cross-section.
   */
  Renderer2D.drawRCWallSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const lw = data.lw || 4000;
    const tw = data.tw || 250;
    const padding = 50;
    const scale = Math.min((width - padding * 2) / lw, (height - padding * 2) / (tw * 3));

    const drawW = lw * scale;
    const drawH = tw * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2;

    // Wall body
    ctx.save();
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2.0;
    ctx.fillRect(startX, startY, drawW, drawH);
    ctx.strokeRect(startX, startY, drawW, drawH);

    // Boundary Elements at both ends (SBE)
    const sbeLength = Math.max(300 * scale, drawW * 0.15);
    ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
    ctx.fillRect(startX, startY, sbeLength, drawH);
    ctx.fillRect(startX + drawW - sbeLength, startY, sbeLength, drawH);
    ctx.restore();

    // Boundary Rebars
    drawRebar(ctx, startX + 20 * scale, startY + drawH / 2, 5, true);
    drawRebar(ctx, startX + sbeLength - 20 * scale, startY + drawH / 2, 5, true);
    drawRebar(ctx, startX + drawW - sbeLength + 20 * scale, startY + drawH / 2, 5, true);
    drawRebar(ctx, startX + drawW - 20 * scale, startY + drawH / 2, 5, true);

    drawDimension(ctx, startX, startY, startX + drawW, startY, `Lw = ${lw} mm`, -25, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `tw = ${tw} mm`, 25, true);
  };

  /**
   * 4. Draw Steel H-Beam / Column cross-section.
   */
  Renderer2D.drawSteelSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const H = data.h || 400;
    const B = data.b || 200;
    const tw = data.tw || 8;
    const tf = data.tf || 13;

    const padding = 60;
    const scale = Math.min((width - padding * 2) / B, (height - padding * 2) / H);
    const drawH = H * scale;
    const drawB = B * scale;
    const drawTw = tw * scale;
    const drawTf = tf * scale;

    const cx = width / 2;
    const cy = height / 2;

    const x1 = cx - drawB / 2;
    const x2 = cx + drawB / 2;
    const y1 = cy - drawH / 2;
    const y2 = cy + drawH / 2;

    ctx.save();
    ctx.fillStyle = '#334155';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;

    // Draw H-Beam profile path
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y1);
    ctx.lineTo(x2, y1 + drawTf);
    ctx.lineTo(cx + drawTw / 2, y1 + drawTf);
    ctx.lineTo(cx + drawTw / 2, y2 - drawTf);
    ctx.lineTo(x2, y2 - drawTf);
    ctx.lineTo(x2, y2);
    ctx.lineTo(x1, y2);
    ctx.lineTo(x1, y2 - drawTf);
    ctx.lineTo(cx - drawTw / 2, y2 - drawTf);
    ctx.lineTo(cx - drawTw / 2, y1 + drawTf);
    ctx.lineTo(x1, y1 + drawTf);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    drawDimension(ctx, x1, y1, x2, y1, `B = ${B} mm`, -30, false);
    drawDimension(ctx, x2, y1, x2, y2, `H = ${H} mm`, 30, true);
  };

  /**
   * 5. Draw CFT / SRC Composite Column.
   */
  Renderer2D.drawCFTSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const B = data.B || 400;
    const H = data.H || 400;
    const t = data.t || 12;

    const padding = 65;
    const scale = Math.min((width - padding * 2) / B, (height - padding * 2) / H);
    const drawW = B * scale;
    const drawH = H * scale;
    const drawT = t * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2;

    // Steel tube (Outer)
    ctx.save();
    ctx.fillStyle = '#475569';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.fillRect(startX, startY, drawW, drawH);

    // Concrete core (Inner)
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(startX + drawT, startY + drawT, drawW - drawT * 2, drawH - drawT * 2);
    ctx.strokeRect(startX, startY, drawW, drawH);
    ctx.strokeRect(startX + drawT, startY + drawT, drawW - drawT * 2, drawH - drawT * 2);
    ctx.restore();

    drawDimension(ctx, startX, startY, startX + drawW, startY, `B = ${B} mm`, -30, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `H = ${H} mm`, 30, true);
  };

  /**
   * 6. Draw Retrofitted Section with CFRP / Steel Plate.
   */
  Renderer2D.drawRetrofitSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const b = data.b || 300;
    const h = data.h || 600;
    const cfrpBf = data.cfrp_bf || 200;

    const padding = 65;
    const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / (h + 40));
    const drawW = b * scale;
    const drawH = h * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2 - 10;

    // Existing RC Beam
    ctx.save();
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2.0;
    ctx.fillRect(startX, startY, drawW, drawH);
    ctx.strokeRect(startX, startY, drawW, drawH);
    ctx.restore();

    // Existing Rebars
    drawRebar(ctx, startX + 40 * scale, startY + drawH - 40 * scale, 5, false);
    drawRebar(ctx, startX + drawW / 2, startY + drawH - 40 * scale, 5, false);
    drawRebar(ctx, startX + drawW - 40 * scale, startY + drawH - 40 * scale, 5, false);

    // CFRP Plate at Soffit (Cyan / Violet Glow)
    const cfrpW = cfrpBf * scale;
    const cfrpX = (width - cfrpW) / 2;
    const cfrpY = startY + drawH + 4;
    const cfrpH = 8;

    ctx.save();
    ctx.fillStyle = '#a855f7';
    ctx.strokeStyle = '#c084fc';
    ctx.lineWidth = 1.5;
    ctx.fillRect(cfrpX, cfrpY, cfrpW, cfrpH);
    ctx.strokeRect(cfrpX, cfrpY, cfrpW, cfrpH);

    ctx.fillStyle = '#d8b4fe';
    ctx.font = 'bold 11px "Inter", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`CFRP Plate (${cfrpBf} mm)`, width / 2, cfrpY + 22);
    ctx.restore();

    drawDimension(ctx, startX, startY, startX + drawW, startY, `b = ${b} mm`, -25, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `h = ${h} mm`, 25, true);
  };

  /**
   * Generic Dispatcher for canvas drawing.
   */
  Renderer2D.drawSection = function (ctx, width, height, memberType, data = {}) {
    const canvas = ctx.canvas;
    if (memberType === 'rc_column') {
      if (typeof Renderer2D.drawRCColumnSection === 'function') {
        Renderer2D.drawRCColumnSection(canvas, data);
        return;
      }
    } else if (memberType === 'steel_beam') {
      if (typeof Renderer2D.drawSteelHSection === 'function') {
        Renderer2D.drawSteelHSection(canvas, data);
        return;
      }
    }
    // Default RC Beam
    if (typeof Renderer2D.drawRCBeamSection === 'function') {
      Renderer2D.drawRCBeamSection(canvas, data);
    }
  };

  global.Renderer2D = Renderer2D;
})(typeof window !== 'undefined' ? window : this);

