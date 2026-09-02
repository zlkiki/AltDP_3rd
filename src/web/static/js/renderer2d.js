/**
 * AltDP_3rd High-Precision 2D Canvas Structural Section Renderer (renderer2d.js)
 * 
 * Renders reinforced concrete and steel sections conforming to KDS construction standards.
 * Features:
 * - Exact physical scale mapping with padding & Retina display DPI scaling
 * - Outer concrete boundary with concrete hatching & chamfer
 * - Outermost closed stirrup loop with 135-degree hooks
 * - Multi-layer rebar arrangements with metallic radial gradient and highlight
 * - Structural engineering dimension lines, leader arrows, and callouts
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
    const width = rect.width || canvas.width || 400;
    const height = rect.height || canvas.height || 400;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  }

  /**
   * Draw engineering dimension line with arrows and label.
   */
  function drawDimension(ctx, x1, y1, x2, y2, text, offset = 25, isVertical = false) {
    ctx.save();
    ctx.strokeStyle = '#94a3b8';
    ctx.fillStyle = '#cbd5e1';
    ctx.lineWidth = 1.0;
    ctx.font = '11px "Inter", -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    const arrowSize = 5;

    if (isVertical) {
      const x = x1 + offset;
      // Extension lines
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x + (offset > 0 ? 5 : -5), y1);
      ctx.moveTo(x2, y2);
      ctx.lineTo(x + (offset > 0 ? 5 : -5), y2);
      // Dimension main line
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
      // Extension lines
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1, y + (offset > 0 ? 5 : -5));
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2, y + (offset > 0 ? 5 : -5));
      // Dimension main line
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
   * Draw individual metallic rebar circle.
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
   * Draw RC Beam cross-section.
   * 
   * @param {HTMLCanvasElement} canvas
   * @param {Object} data - Section parameters (b, h, cover, As, As_prime, num_bars, stirrup)
   */
  Renderer2D.drawRCBeamSection = function (canvas, data) {
    const { ctx, width, height } = setupDPI(canvas);
    ctx.clearRect(0, 0, width, height);

    const b = data.b || 400;
    const h = data.h || 600;
    const cover = data.cover || 40;
    const numTension = data.num_tension_bars || data.num_bars || 4;
    const numComp = data.num_comp_bars || 2;
    const barSize = data.bar_size || "D22";
    const stirrupSize = data.stirrup_size || "D10";

    const padding = 70;
    const scale = Math.min((width - padding * 2) / b, (height - padding * 2) / h);

    const drawW = b * scale;
    const drawH = h * scale;
    const startX = (width - drawW) / 2;
    const startY = (height - drawH) / 2;

    // 1. Concrete Outline
    ctx.save();
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2.0;

    ctx.beginPath();
    ctx.rect(startX, startY, drawW, drawH);
    ctx.fill();
    ctx.stroke();

    // Subtle hatching pattern
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1.0;
    for (let i = -drawH; i < drawW; i += 20) {
      ctx.beginPath();
      ctx.moveTo(Math.max(startX + i, startX), startY);
      ctx.lineTo(Math.min(startX + i + drawH, startX + drawW), startY + drawH);
      ctx.stroke();
    }
    ctx.restore();

    // 2. Outermost Closed Stirrup
    const stirrupCover = (cover - 10) * scale;
    const stirrupX = startX + stirrupCover;
    const stirrupY = startY + stirrupCover;
    const stirrupW = drawW - stirrupCover * 2;
    const stirrupH = drawH - stirrupCover * 2;

    ctx.save();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.setLineDash([]);
    ctx.strokeRect(stirrupX, stirrupY, stirrupW, stirrupH);

    // 135-deg hook indicators at top corners
    ctx.beginPath();
    ctx.moveTo(stirrupX + 10, stirrupY + 15);
    ctx.lineTo(stirrupX + 15, stirrupY + 5);
    ctx.moveTo(stirrupX + stirrupW - 10, stirrupY + 15);
    ctx.lineTo(stirrupX + stirrupW - 15, stirrupY + 5);
    ctx.stroke();
    ctx.restore();

    // 3. Longitudinal Compression Rebars (Top)
    const rebarRadius = Math.max(5.0 * (scale / 0.5), 5.0);
    const topY = startY + cover * scale;
    if (numComp > 0) {
      const topClearW = drawW - cover * scale * 2;
      for (let i = 0; i < numComp; i++) {
        const topX = (numComp === 1)
          ? startX + drawW / 2
          : startX + cover * scale + i * (topClearW / (numComp - 1));
        drawRebar(ctx, topX, topY, rebarRadius * 0.85, true);
      }
    }

    // 4. Longitudinal Tension Rebars (Bottom, supports 1-layer and 2-layer)
    const bottomY1 = startY + drawH - cover * scale;
    const bottomClearW = drawW - cover * scale * 2;

    if (numTension <= 5) {
      // 1-Layer
      for (let i = 0; i < numTension; i++) {
        const botX = (numTension === 1)
          ? startX + drawW / 2
          : startX + cover * scale + i * (bottomClearW / (numTension - 1));
        drawRebar(ctx, botX, bottomY1, rebarRadius, false);
      }
    } else {
      // 2-Layers
      const n1 = Math.ceil(numTension / 2);
      const n2 = numTension - n1;
      const bottomY2 = bottomY1 - 25 * scale;

      // Layer 1
      for (let i = 0; i < n1; i++) {
        const botX = startX + cover * scale + i * (bottomClearW / (n1 - 1));
        drawRebar(ctx, botX, bottomY1, rebarRadius, false);
      }
      // Layer 2
      for (let i = 0; i < n2; i++) {
        const botX = startX + cover * scale + i * (bottomClearW / (n2 - 1));
        drawRebar(ctx, botX, bottomY2, rebarRadius, false);
      }
    }

    // 5. Dimension Lines & Callouts
    drawDimension(ctx, startX, startY, startX + drawW, startY, `b = ${b} mm`, -35, false);
    drawDimension(ctx, startX + drawW, startY, startX + drawW, startY + drawH, `h = ${h} mm`, 35, true);
    drawDimension(ctx, startX, startY, startX, startY + drawH - cover * scale, `d = ${Math.round(h - cover)} mm`, -35, true);

    // Callout labels
    ctx.save();
    ctx.font = '12px "Inter", -apple-system, sans-serif';
    ctx.fillStyle = '#f87171';
    ctx.textAlign = 'center';
    ctx.fillText(`${numTension}-${barSize} (Tension)`, startX + drawW / 2, startY + drawH + 30);

    ctx.fillStyle = '#60a5fa';
    ctx.fillText(`${numComp}-D19 (Top Rebar)`, startX + drawW / 2, startY - 45);

    ctx.fillStyle = '#38bdf8';
    ctx.fillText(`Stirrup: 2-${stirrupSize}@200`, startX + drawW + 15, startY + drawH / 2);
    ctx.restore();
  };

  global.Renderer2D = Renderer2D;
})(typeof window !== 'undefined' ? window : this);
