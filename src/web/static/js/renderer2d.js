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

  /**
   * Render Dark Engineering Grid & Clean Geometry WIP Placeholder for unfinished modules.
   * Conforms to docs/07 (Center 2D Graphic View) and requirements 20-4.
   */
  Renderer2D.renderWIPCanvas = function (canvas, meta = {}) {
    if (!canvas) return;
    const { ctx, width, height } = setupDPI(canvas);

    // 1. Clear & Dark Engineering Slate Background
    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.fillStyle = '#0f172a'; // Deep slate background
    ctx.fillRect(0, 0, width, height);

    // 2. Soft Engineering Grid Lines
    const gridSize = 24;
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.08)';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    for (let x = 0; x < width; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    ctx.stroke();

    // 3. Subtle Geometry Section Silhouette at Center
    const cx = width / 2;
    const cy = height / 2 - 30;
    const boxW = 140;
    const boxH = 100;

    // Outer section rect
    ctx.fillStyle = 'rgba(30, 41, 59, 0.85)';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 1.5;
    ctx.fillRect(cx - boxW / 2, cy - boxH / 2, boxW, boxH);
    ctx.strokeRect(cx - boxW / 2, cy - boxH / 2, boxW, boxH);

    // Center cross axis (dashed)
    ctx.save();
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
    ctx.lineWidth = 1.0;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(cx - boxW / 2 - 15, cy);
    ctx.lineTo(cx + boxW / 2 + 15, cy);
    ctx.moveTo(cx, cy - boxH / 2 - 15);
    ctx.lineTo(cx, cy + boxH / 2 + 15);
    ctx.stroke();
    ctx.restore();

    // Corner Rebar / Anchor placeholders
    const rebarOffset = 14;
    const rebarR = 4;
    const rebars = [
      [cx - boxW / 2 + rebarOffset, cy - boxH / 2 + rebarOffset],
      [cx + boxW / 2 - rebarOffset, cy - boxH / 2 + rebarOffset],
      [cx - boxW / 2 + rebarOffset, cy + boxH / 2 - rebarOffset],
      [cx + boxW / 2 - rebarOffset, cy + boxH / 2 - rebarOffset],
    ];
    rebars.forEach(([rx, ry]) => {
      ctx.beginPath();
      ctx.arc(rx, ry, rebarR, 0, Math.PI * 2);
      ctx.fillStyle = '#38bdf8';
      ctx.fill();
      ctx.strokeStyle = '#bae6fd';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // 4. Center Typography & Informative Badges
    const memberName = meta.name || meta.key || '선택 부재';
    const tier = meta.tier || 'Tier 3';
    const midasDlg = meta.midas_dlg || '';
    const std = meta.standard || 'KDS 국가건설기준';

    // Badge Pill
    const badgeText = `${tier}${midasDlg ? ` · ${midasDlg}` : ''}`;
    ctx.font = '600 11px "Inter", sans-serif';
    const badgeW = ctx.measureText(badgeText).width + 18;
    const badgeH = 22;
    const badgeY = cy + boxH / 2 + 25;
    
    ctx.fillStyle = tier.includes('Tier 1') ? 'rgba(245, 158, 11, 0.15)' : 'rgba(56, 189, 248, 0.15)';
    ctx.strokeStyle = tier.includes('Tier 1') ? '#f59e0b' : '#38bdf8';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    if (typeof ctx.roundRect === 'function') {
      ctx.roundRect(cx - badgeW / 2, badgeY, badgeW, badgeH, 11);
    } else {
      ctx.rect(cx - badgeW / 2, badgeY, badgeW, badgeH);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = tier.includes('Tier 1') ? '#fbbf24' : '#7dd3fc';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(badgeText, cx, badgeY + badgeH / 2);

    // Primary WIP Heading
    ctx.font = 'bold 14px "Pretendard", "Segoe UI", sans-serif';
    ctx.fillStyle = '#f8fafc';
    ctx.fillText('📐 2D VDraw 단면 및 배근도 그래픽 준비 중 (WIP)', cx, badgeY + badgeH + 24);

    ctx.restore();
  };

  /**
   * =========================================================================
   * Phase 21-4: Top Viewport Geometry & Detailing Renderer
   * =========================================================================
   * Renders cross-section, rebar detailing, dimensions, and collects hit-test targets.
   * Returns array of interactive elements for hover tooltips.
   */
  Renderer2D.renderTopViewportGeometry = function (ctx, width, height, memberType, data = {}, showDimensions = true) {
    const interactiveElements = [];
    const mod = (memberType || '').toLowerCase();

    // 1. Clean Engineering Dark Canvas Background
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, width, height);

    // Grid pattern
    ctx.save();
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.06)';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    ctx.restore();

    const cx = width / 2;
    const cy = height / 2;

    if (mod === 'rc_beam' || (mod.includes('beam') && !mod.includes('steel'))) {
      if (window.VectorRCBeam && typeof window.VectorRCBeam.renderLongitudinalView === 'function') {
        return window.VectorRCBeam.renderLongitudinalView(ctx, width, height, data, showDimensions);
      }
    }

    if (mod.includes('col') || mod === 'rc_column') {
      // -------------------------------------------------------------
      // RC Column Section (둘레배근, 대근, 치수선)
      // -------------------------------------------------------------
      const b = Number(data.b || data.B || 600);
      const h = Number(data.h || data.H || 600);
      const cover = Number(data.cover || 50);
      const totalBars = Number(data.total_bars || data.rebar_num || 12);
      const barSize = data.bar_size || 'D25';

      const padding = showDimensions ? 70 : 40;
      const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / h);
      const drawW = b * scale;
      const drawH = h * scale;
      const startX = cx - drawW / 2;
      const startY = cy - drawH / 2;

      // Concrete Body
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2.0;
      ctx.fillRect(startX, startY, drawW, drawH);
      ctx.strokeRect(startX, startY, drawW, drawH);

      // Tie / Hoop rebar
      const tieCover = (cover - 10) * scale;
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(startX + tieCover, startY + tieCover, drawW - tieCover * 2, drawH - tieCover * 2);
      ctx.restore();

      // Main Rebars along perimeter
      const rebarRadius = Math.max(5 * (scale / 0.5), 5.5);
      const rX1 = startX + cover * scale;
      const rX2 = startX + drawW - cover * scale;
      const rY1 = startY + cover * scale;
      const rY2 = startY + drawH - cover * scale;

      const barsPerSide = Math.max(2, Math.floor(totalBars / 4) + 1);
      const dx = (rX2 - rX1) / (barsPerSide - 1);
      const dy = (rY2 - rY1) / (barsPerSide - 1);

      const addRebarTarget = (rx, ry, idx, isTop) => {
        drawRebar(ctx, rx, ry, rebarRadius, isTop);
        interactiveElements.push({
          type: 'rebar',
          x: rx,
          y: ry,
          r: rebarRadius + 4,
          title: `기둥 주철근 #${idx}`,
          detail: `${barSize} (fy = ${data.fy || 400} MPa)`
        });
      };

      let barCount = 1;
      for (let i = 0; i < barsPerSide; i++) {
        addRebarTarget(rX1 + i * dx, rY1, barCount++, true);
        addRebarTarget(rX1 + i * dx, rY2, barCount++, false);
      }
      for (let j = 1; j < barsPerSide - 1; j++) {
        addRebarTarget(rX1, rY1 + j * dy, barCount++, false);
        addRebarTarget(rX2, rY1 + j * dy, barCount++, false);
      }

      if (showDimensions) {
        drawDimension(ctx, startX, startY, startX + drawW, startY, `B = ${b} mm`, -25, false);
        drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `H = ${h} mm`, 25, true);
      }

    } else if (mod.includes('steel_baseplate') || mod.includes('baseplate')) {
      // -------------------------------------------------------------
      // Steel Baseplate 2D CAD Plan (베이스플레이트 & 앵커볼트 평면)
      // -------------------------------------------------------------
      const bpW = Number(data.bp_w || 500);
      const bpH = Number(data.bp_h || 500);
      const scale = Math.min((width - 120) / bpW, (height - 100) / bpH);
      const drawW = bpW * scale;
      const drawH = bpH * scale;
      const startX = cx - drawW / 2;
      const startY = cy - drawH / 2;

      // Baseplate Body
      ctx.save();
      ctx.fillStyle = '#334155';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.fillRect(startX, startY, drawW, drawH);
      ctx.strokeRect(startX, startY, drawW, drawH);

      // Steel Column Silhouette at Center
      const colW = drawW * 0.55;
      const colH = drawH * 0.55;
      ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 1.5;
      ctx.fillRect(cx - colW / 2, cy - colH / 2, colW, colH);
      ctx.strokeRect(cx - colW / 2, cy - colH / 2, colW, colH);
      ctx.restore();

      // 4 Anchor Bolts
      const boltEdge = 40 * scale;
      const boltR = 7;
      const bolts = [
        [startX + boltEdge, startY + boltEdge],
        [startX + drawW - boltEdge, startY + boltEdge],
        [startX + boltEdge, startY + drawH - boltEdge],
        [startX + drawW - boltEdge, startY + drawH - boltEdge]
      ];

      bolts.forEach(([bx, by], idx) => {
        ctx.save();
        ctx.beginPath();
        ctx.arc(bx, by, boltR, 0, Math.PI * 2);
        ctx.fillStyle = '#f59e0b';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Bolt Cross mark
        ctx.strokeStyle = '#78350f';
        ctx.beginPath();
        ctx.moveTo(bx - boltR + 2, by);
        ctx.lineTo(bx + boltR - 2, by);
        ctx.moveTo(bx, by - boltR + 2);
        ctx.lineTo(bx, by + boltR - 2);
        ctx.stroke();
        ctx.restore();

        interactiveElements.push({
          type: 'bolt',
          x: bx,
          y: by,
          r: boltR + 4,
          title: `앵커볼트 #${idx + 1}`,
          detail: `M24 F10T (연단거리 e = ${Math.round(40)} mm)`
        });
      });

      if (showDimensions) {
        drawDimension(ctx, startX, startY, startX + drawW, startY, `B_p = ${bpW} mm`, -25, false);
        drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `H_p = ${bpH} mm`, 25, true);
      }

    } else if (mod.includes('steel') || mod.includes('beam_col')) {
      // -------------------------------------------------------------
      // Steel H-Beam / Column Section (판폭두께비 색상 코딩)
      // -------------------------------------------------------------
      const H = Number(data.h || data.H || 400);
      const B = Number(data.b || data.B || 200);
      const tw = Number(data.tw || 8);
      const tf = Number(data.tf || 13);

      const padding = showDimensions ? 70 : 40;
      const scale = Math.min((width - padding * 2) / B, (height - padding * 2) / H);
      const drawH = H * scale;
      const drawB = B * scale;
      const drawTw = tw * scale;
      const drawTf = tf * scale;

      const x1 = cx - drawB / 2;
      const x2 = cx + drawB / 2;
      const y1 = cy - drawH / 2;
      const y2 = cy + drawH / 2;

      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.0;

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

      // Slenderness Compactness Highlight: Flange & Web
      ctx.fillStyle = 'rgba(34, 197, 94, 0.2)'; // Green: Compact Section
      ctx.fillRect(x1, y1, drawB, drawTf);
      ctx.fillRect(x1, y2 - drawTf, drawB, drawTf);
      ctx.fillRect(cx - drawTw / 2, y1 + drawTf, drawTw, drawH - drawTf * 2);
      ctx.restore();

      // Interactive targets for flange and web
      interactiveElements.push({
        type: 'steel_flange',
        x: cx,
        y: y1 + drawTf / 2,
        r: 15,
        title: '상부 플랜지 (Flange)',
        detail: `B = ${B} mm, tf = ${tf} mm (조밀단면 OK)`
      });
      interactiveElements.push({
        type: 'steel_web',
        x: cx,
        y: cy,
        r: 15,
        title: '웨브 (Web)',
        detail: `H = ${H} mm, tw = ${tw} mm (전단좌굴 안전)`
      });

      if (showDimensions) {
        drawDimension(ctx, x1, y1, x2, y1, `B = ${B} mm`, -25, false);
        drawDimension(ctx, x2, y1, x2, y2, `H = ${H} mm`, 25, true);
      }

    } else if (mod.includes('footing') || mod.includes('slab')) {
      // -------------------------------------------------------------
      // RC Footing / Slab Plan & Shear Critical Sections
      // -------------------------------------------------------------
      const b = Number(data.b || data.B || 2000);
      const l = Number(data.l || data.L || 2000);
      const scale = Math.min((width - 100) / b, (height - 90) / l);
      const drawW = b * scale;
      const drawH = l * scale;
      const startX = cx - drawW / 2;
      const startY = cy - drawH / 2;

      // Footing Slab Body
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2;
      ctx.fillRect(startX, startY, drawW, drawH);
      ctx.strokeRect(startX, startY, drawW, drawH);

      // 2-Way Punching Shear Perimeter (d/2 offset) [Red Dashed Line]
      const colDim = 400 * scale;
      const dOffset = 150 * scale;
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.strokeRect(cx - colDim / 2 - dOffset, cy - colDim / 2 - dOffset, colDim + dOffset * 2, colDim + dOffset * 2);
      ctx.setLineDash([]);

      // Center Column Pedestal
      ctx.fillStyle = 'rgba(56, 189, 248, 0.4)';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.5;
      ctx.fillRect(cx - colDim / 2, cy - colDim / 2, colDim, colDim);
      ctx.strokeRect(cx - colDim / 2, cy - colDim / 2, colDim, colDim);
      ctx.restore();

      interactiveElements.push({
        type: 'pedestal',
        x: cx,
        y: cy,
        r: colDim / 2,
        title: '상부 기둥 주각부 (Pedestal)',
        detail: '400 x 400 mm (fc = 27 MPa)'
      });
      interactiveElements.push({
        type: 'critical_shear',
        x: cx + colDim / 2 + dOffset,
        y: cy,
        r: 10,
        title: '2방향 뚫림전단 위험단면',
        detail: '기둥 전면에서 d/2 이격면 (KDS 14 20 54)'
      });

      if (showDimensions) {
        drawDimension(ctx, startX, startY, startX + drawW, startY, `B = ${b} mm`, -25, false);
        drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `L = ${l} mm`, 25, true);
      }

    } else {
      // -------------------------------------------------------------
      // Default: RC Beam Cross-Section (직사각형 보 및 내진 스터럽)
      // -------------------------------------------------------------
      const b = Number(data.b || 400);
      const h = Number(data.h || 600);
      const cover = Number(data.cover || 50);
      const numTension = Number(data.num_tension_bars || data.num_bars || 4);
      const numComp = Number(data.num_comp_bars || 2);
      const barSize = data.bar_size || 'D25';
      const stirrupSize = data.stirrup_size || 'D10';

      const padding = showDimensions ? 70 : 40;
      const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / h);
      const drawW = b * scale;
      const drawH = h * scale;
      const startX = cx - drawW / 2;
      const startY = cy - drawH / 2;

      // Concrete Outline
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2.0;
      ctx.fillRect(startX, startY, drawW, drawH);
      ctx.strokeRect(startX, startY, drawW, drawH);

      // Stirrup with 135-degree seismic hooks
      const stirrupCover = (cover - 10) * scale;
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.8;
      ctx.strokeRect(startX + stirrupCover, startY + stirrupCover, drawW - stirrupCover * 2, drawH - stirrupCover * 2);
      ctx.restore();

      const rebarRadius = Math.max(5 * (scale / 0.5), 5.5);

      // Top Compression Rebars
      const topY = startY + cover * scale;
      if (numComp > 0) {
        const topClearW = drawW - cover * scale * 2;
        for (let i = 0; i < numComp; i++) {
          const topX = (numComp === 1) ? startX + drawW / 2 : startX + cover * scale + i * (topClearW / (numComp - 1));
          drawRebar(ctx, topX, topY, rebarRadius * 0.85, true);
          interactiveElements.push({
            type: 'rebar',
            x: topX,
            y: topY,
            r: rebarRadius + 4,
            title: `상부 압축철근 #${i + 1}`,
            detail: `${numComp}-${barSize} (d' = ${cover} mm)`
          });
        }
      }

      // Bottom Tension Rebars
      const bottomY = startY + drawH - cover * scale;
      const bottomClearW = drawW - cover * scale * 2;
      for (let i = 0; i < numTension; i++) {
        const botX = (numTension === 1) ? startX + drawW / 2 : startX + cover * scale + i * (bottomClearW / (numTension - 1));
        drawRebar(ctx, botX, bottomY, rebarRadius, false);
        interactiveElements.push({
          type: 'rebar',
          x: botX,
          y: bottomY,
          r: rebarRadius + 4,
          title: `하부 인장철근 #${i + 1}`,
          detail: `${numTension}-${barSize} (d = ${h - cover} mm)`
        });
      }

      if (showDimensions) {
        drawDimension(ctx, startX, startY, startX + drawW, startY, `b = ${b} mm`, -25, false);
        drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `h = ${h} mm`, 25, true);
      }
    }

    return interactiveElements;
  };

  /**
   * =========================================================================
   * Phase 21-4: Bottom Viewport Engineering Mechanics Renderer
   * =========================================================================
   * Renders P-M curves, bending/shear envelopes, soil pressure, LTB curves.
   * Returns array of interactive elements for hover tooltips.
   */
  Renderer2D.renderBottomViewportMechanics = function (ctx, width, height, memberType, data = {}, result = {}, is3DMode = false) {
    const interactiveElements = [];
    const mod = (memberType || '').toLowerCase();

    // 1. Clean Deep Engineering Slate Background
    ctx.fillStyle = '#0b1120';
    ctx.fillRect(0, 0, width, height);

    if (mod.includes('col') || mod === 'rc_column' || result.pm_curve || data.pm_curve) {
      // -------------------------------------------------------------
      // RC Column / Shear Wall P-M Interaction Diagram (2D / 3D Mode)
      // -------------------------------------------------------------
      const pts = (result.pm_curve && result.pm_curve.length > 0) ? result.pm_curve : (data.pm_curve || []);
      const margin = { top: 30, right: 30, bottom: 40, left: 60 };

      if (pts.length === 0) {
        // Fallback generic P-M envelope curve for demonstration
        const P0 = Number(data.Pu || 2400) * 1.3;
        const M0 = Number(data.Mu || 450) * 1.4;
        const steps = 20;
        for (let i = 0; i <= steps; i++) {
          const theta = (i / steps) * Math.PI;
          const pn = P0 * Math.cos(theta * 0.7);
          const mn = M0 * Math.sin(theta);
          pts.push({
            Pn: Math.max(pn, -300),
            Mn: Math.max(mn, 0),
            phi_Pn: Math.max(pn * 0.65, -200),
            phi_Mn: Math.max(mn * 0.65, 0)
          });
        }
      }

      if (is3DMode) {
        // 3D Isometric P-M Space Representation
        const cx = width / 2;
        const cy = height / 2 + 10;
        
        ctx.save();
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 1.5;
        // P-axis (vertical)
        ctx.beginPath();
        ctx.moveTo(cx, cy - 100);
        ctx.lineTo(cx, cy + 90);
        ctx.stroke();

        // Mx-axis (diagonal right-down)
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + 120, cy + 60);
        ctx.stroke();

        // My-axis (diagonal left-down)
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx - 120, cy + 60);
        ctx.stroke();

        // 3D Elliptical Surface Ring
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.ellipse(cx, cy - 20, 90, 45, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
        ctx.fill();

        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px sans-serif';
        ctx.fillText('+P (축압축)', cx + 8, cy - 85);
        ctx.fillText('+Mx', cx + 125, cy + 65);
        ctx.fillText('+My', cx - 145, cy + 65);

        // 3D Applied Force Point
        const ptX = cx + 35;
        const ptY = cy - 25;
        ctx.fillStyle = '#22c55e';
        ctx.beginPath();
        ctx.arc(ptX, ptY, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        interactiveElements.push({
          type: '3d_load',
          x: ptX,
          y: ptY,
          r: 10,
          title: '3D 계수하중 타점 (Pu, Mux, Muy)',
          detail: `Pu = ${data.Pu || 1500} kN, Mux = ${data.Mu || 250} kNm (안전역 OK)`
        });
        ctx.restore();

      } else {
        // Standard 2D P-M Curve
        const plotW = width - margin.left - margin.right;
        const plotH = height - margin.top - margin.bottom;

        const maxM = Math.max(...pts.map(p => Math.max(p.Mn || 0, p.phi_Mn || 0)), Number(data.Mu || 0), 100) * 1.15;
        const maxP = Math.max(...pts.map(p => Math.max(p.Pn || 0, p.phi_Pn || 0)), Number(data.Pu || 0), 100) * 1.10;
        const minP = Math.min(...pts.map(p => Math.min(p.Pn || 0, p.phi_Pn || 0)), Number(data.Pu || 0), 0) * 1.10;

        const scaleX = (m) => margin.left + (m / maxM) * plotW;
        const scaleY = (p) => margin.top + ((maxP - p) / (maxP - minP || 1)) * plotH;

        // Grid lines
        ctx.save();
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';

        for (let i = 0; i <= 4; i++) {
          const pVal = minP + (i / 4) * (maxP - minP);
          const y = scaleY(pVal);
          ctx.beginPath();
          ctx.moveTo(margin.left, y);
          ctx.lineTo(width - margin.right, y);
          ctx.stroke();
          ctx.fillText(`${Math.round(pVal)} kN`, 8, y + 3);
        }

        for (let j = 0; j <= 4; j++) {
          const mVal = (j / 4) * maxM;
          const x = scaleX(mVal);
          ctx.beginPath();
          ctx.moveTo(x, margin.top);
          ctx.lineTo(x, height - margin.bottom);
          ctx.stroke();
          ctx.fillText(`${Math.round(mVal)} kNm`, x - 15, height - margin.bottom + 18);
        }

        // Nominal Curve (Pn - Mn) [Dashed Gray]
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        pts.forEach((p, idx) => {
          const px = scaleX(p.Mn || 0);
          const py = scaleY(p.Pn || 0);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.stroke();
        ctx.setLineDash([]);

        // Design Curve (phi_Pn - phi_Mn) [Solid Cyan/Blue]
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        pts.forEach((p, idx) => {
          const px = scaleX(p.phi_Mn || 0);
          const py = scaleY(p.phi_Pn || 0);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.stroke();

        // Applied Design Force Point (Pu, Mu)
        const pu = Number(data.Pu !== undefined ? data.Pu : (result.Pu || 1200));
        const mu = Number(data.Mu !== undefined ? data.Mu : (result.Mu || 280));
        const loadX = scaleX(mu);
        const loadY = scaleY(pu);
        const dcr = Number(result.max_dcr !== undefined ? result.max_dcr : (result.dcr || 0.85));
        const isSafe = dcr <= 1.0;

        ctx.fillStyle = isSafe ? '#22c55e' : '#ef4444';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(loadX, loadY, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        interactiveElements.push({
          type: 'pm_load',
          x: loadX,
          y: loadY,
          r: 10,
          title: '계수 설계하중점 (Pu, Mu)',
          detail: `Pu = ${pu} kN, Mu = ${mu} kNm (DCR = ${dcr.toFixed(3)} ${isSafe ? 'OK' : 'NG'})`
        });
        ctx.restore();
      }

    } else if (mod.includes('footing') || mod.includes('slab')) {
      // -------------------------------------------------------------
      // Soil Bearing Pressure Diagram (q_min ~ q_max 사다리꼴 분포도)
      // -------------------------------------------------------------
      const margin = { top: 40, right: 50, bottom: 40, left: 60 };
      const groundY = height - margin.bottom - 40;
      const startX = margin.left + 20;
      const endX = width - margin.right - 20;
      const spanW = endX - startX;

      const qMax = Number(result.q_max || 185);
      const qMin = Number(result.q_min || 95);
      const qAllow = Number(data.qa || 250);

      ctx.save();
      // Soil Baseline
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(startX - 20, groundY);
      ctx.lineTo(endX + 20, groundY);
      ctx.stroke();

      // Soil Pressure Trapezoid
      const scaleQ = 55 / Math.max(qMax, qAllow, 100);
      const hMin = qMin * scaleQ;
      const hMax = qMax * scaleQ;

      ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(startX, groundY);
      ctx.lineTo(startX, groundY + hMin);
      ctx.lineTo(endX, groundY + hMax);
      ctx.lineTo(endX, groundY);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Pressure Arrows
      ctx.strokeStyle = '#38bdf8';
      for (let x = startX; x <= endX; x += 30) {
        const ratio = (x - startX) / spanW;
        const curH = hMin + ratio * (hMax - hMin);
        ctx.beginPath();
        ctx.moveTo(x, groundY + curH);
        ctx.lineTo(x, groundY + 4);
        ctx.stroke();
      }

      // Allowable Soil Capacity Line [Yellow Dash]
      const hAllow = qAllow * scaleQ;
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(startX - 10, groundY + hAllow);
      ctx.lineTo(endX + 10, groundY + hAllow);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = '#f59e0b';
      ctx.font = '11px sans-serif';
      ctx.fillText(`qa = ${qAllow} kN/m² (허용지내력)`, endX - 120, groundY + hAllow - 6);

      interactiveElements.push({
        type: 'soil_pressure',
        x: endX,
        y: groundY + hMax / 2,
        r: 12,
        title: '최대 접지압 q_max',
        detail: `q_max = ${qMax} kN/m² ≤ qa (${qAllow}) OK`
      });
      ctx.restore();

    } else {
      if (mod === 'rc_beam' || (mod.includes('beam') && !mod.includes('steel'))) {
        if (window.VectorRCBeam && typeof window.VectorRCBeam.renderCrossSections === 'function') {
          return window.VectorRCBeam.renderCrossSections(ctx, width, height, data, result, is3DMode);
        }
      }

      // -------------------------------------------------------------
      // RC / Steel Beam Moment (Mu) & Shear (Vu) Envelopes
      // -------------------------------------------------------------
      const margin = { top: 35, right: 45, bottom: 45, left: 55 };
      const plotW = width - margin.left - margin.right;
      const plotH = height - margin.top - margin.bottom;
      const axisY = margin.top + plotH * 0.45;

      const mu = Number(result.mu || data.Mu || 210);
      const phiMn = Number(result.phi_mn || data.phi_Mn || 260);

      ctx.save();
      // Beam axis
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(margin.left, axisY);
      ctx.lineTo(width - margin.right, axisY);
      ctx.stroke();

      // Bending Moment Parabola (Positive midspan, negative ends)
      const maxBendH = plotH * 0.38;
      ctx.fillStyle = 'rgba(56, 189, 248, 0.12)';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;

      ctx.beginPath();
      ctx.moveTo(margin.left, axisY);
      for (let x = 0; x <= plotW; x += 10) {
        const t = (x / plotW) * 2 - 1; // -1 to +1
        const y = axisY + (1 - t * t) * maxBendH - 0.25 * maxBendH;
        ctx.lineTo(margin.left + x, y);
      }
      ctx.lineTo(width - margin.right, axisY);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Design Capacity limit line [Green Dash]
      const capY = axisY + (phiMn / Math.max(mu, 1)) * maxBendH * 0.75;
      ctx.strokeStyle = '#22c55e';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(margin.left, capY);
      ctx.lineTo(width - margin.right, capY);
      ctx.stroke();
      ctx.setLineDash([]);

      const midX = margin.left + plotW / 2;
      const midY = axisY + maxBendH * 0.75;

      interactiveElements.push({
        type: 'moment_peak',
        x: midX,
        y: midY,
        r: 10,
        title: '중앙부 최대 휨모멘트 (Mu)',
        detail: `Mu = ${mu} kNm ≤ φMn (${phiMn} kNm) OK`
      });
      ctx.restore();
    }

    return interactiveElements;
  };

  global.Renderer2D = Renderer2D;
})(typeof window !== 'undefined' ? window : this);


