/**
 * AltDP_3rd High-Precision 2D VDraw Canvas RC Beam Renderer (vector_rc_beam.js)
 * Conforms to Requirement 22-3 (Phase V1-1 Step 3) & docs/07 section 4.3.
 * 
 * Features:
 * - Viewport A (Top): Longitudinal Rebar Detailing & Factored Moment/Shear Envelope (BMD/SFD)
 *   - Scaled beam span L (e.g. 6000mm) with Hinge/Roller boundary conditions
 *   - L/4 and L/2 zone partition lines (End-I, Center-M, End-J)
 *   - Longitudinal top & bottom main rebars with 90° standard hooks
 *   - Longitudinal stirrup pitch spacing array
 *   - Factored Bending Moment Diagram (BMD, Mu) & Shear Force Diagram (SFD, Vu) overlay
 * - Viewport B (Bottom): 3-Station Cross-Section Detailing (End-I, Center-M, End-J)
 *   - Rectangular or T-Beam concrete outlines with engineering hatching
 *   - Closed stirrups with 135-degree seismic hooks (r_bend = 2 * d_tie)
 *   - Multi-layer top/bottom rebars (1st & 2nd layer 25mm clearance) & torsion skin bars
 *   - Dimension lines (bw, h, d, d') & rebar callout leader tags
 *   - Interactive hover targets with real-time stress & safety factor tooltips
 */

(function (global) {
  'use strict';

  const VectorRCBeam = {};

  // ---------------------------------------------------------------------------
  // Helper: Parse Rebar String (e.g. "4-D25" -> { count: 4, dia: 25 })
  // ---------------------------------------------------------------------------
  function parseRebarSpec(spec) {
    if (!spec || spec === '0' || spec === 'none') {
      return { count: 0, dia: 0, str: '-' };
    }
    const str = String(spec).trim();
    const match = str.match(/(\d+)\s*[-_xX@]?\s*[dD]?(\d+)/);
    if (match) {
      return {
        count: parseInt(match[1], 10),
        dia: parseInt(match[2], 10),
        str: `${match[1]}-D${match[2]}`
      };
    }
    return { count: 0, dia: 0, str };
  }

  function parseStirrupSpec(diaSpec, spaceSpec) {
    let dia = 10;
    let space = 150;
    if (typeof diaSpec === 'number') dia = diaSpec;
    else if (typeof diaSpec === 'string') {
      const m = diaSpec.match(/(\d+)/);
      if (m) dia = parseInt(m[1], 10);
    }
    if (typeof spaceSpec === 'number') space = spaceSpec;
    else if (typeof spaceSpec === 'string') {
      const m = spaceSpec.match(/(\d+)/);
      if (m) space = parseInt(m[1], 10);
    }
    return { dia, space, text: `D${dia}@${space}` };
  }

  // ---------------------------------------------------------------------------
  // Helper: Normalize RC Beam Data Structure
  // ---------------------------------------------------------------------------
  function extractBeamData(data = {}) {
    const b = Number(data.b || data.bw || 400);
    const h = Number(data.h || 600);
    const length = Number(data.length || data.span || 6000);
    const cover = Number(data.cover || 40);
    const shape = String(data.shape || (data.bf && data.bf > b ? 'T_BEAM' : 'RECTANGULAR')).toUpperCase();
    const bf = Number(data.bf || (shape === 'T_BEAM' ? b * 2.5 : b));
    const hf = Number(data.hf || 150);

    // Rebar station data
    const r = data.rebar || {};
    const endI = r.end_i || {};
    const centerM = r.center_m || {};
    const endJ = r.end_j || {};

    const stations = {
      end_i: {
        top1: parseRebarSpec(endI.top_layer1 || data.top_layer1 || '4-D25'),
        top2: parseRebarSpec(endI.top_layer2 || '2-D25'),
        bot1: parseRebarSpec(endI.bot_layer1 || data.bot_layer1 || '3-D22'),
        bot2: parseRebarSpec(endI.bot_layer2 || '0'),
        stirrup: parseStirrupSpec(endI.stirrup_dia || 'D10', endI.stirrup_space || 150),
        legs: Number(endI.stirrup_legs || 2)
      },
      center_m: {
        top1: parseRebarSpec(centerM.top_layer1 || '2-D22'),
        top2: parseRebarSpec(centerM.top_layer2 || '0'),
        bot1: parseRebarSpec(centerM.bot_layer1 || '4-D25'),
        bot2: parseRebarSpec(centerM.bot_layer2 || '2-D25'),
        stirrup: parseStirrupSpec(centerM.stirrup_dia || 'D10', centerM.stirrup_space || 250),
        legs: Number(centerM.stirrup_legs || 2)
      },
      end_j: {
        top1: parseRebarSpec(endJ.top_layer1 || '4-D25'),
        top2: parseRebarSpec(endJ.top_layer2 || '2-D25'),
        bot1: parseRebarSpec(endJ.bot_layer1 || '3-D22'),
        bot2: parseRebarSpec(endJ.bot_layer2 || '0'),
        stirrup: parseStirrupSpec(endJ.stirrup_dia || 'D10', endJ.stirrup_space || 150),
        legs: Number(endJ.stirrup_legs || 2)
      }
    };

    const torsionSideCount = Number(r.torsion_side_count || data.torsion_side_count || 2);
    const torsionSideBar = parseRebarSpec(r.torsion_side_bar || data.torsion_side_bar || 'D13');

    // Factored Loads
    const loads = data.loads || {};
    const loadI = loads.end_i || {};
    const loadM = loads.center_m || {};
    const loadJ = loads.end_j || {};

    const factored = {
      end_i: {
        Mu_pos: Number(loadI.Mu_pos || 0),
        Mu_neg: Number(loadI.Mu_neg || data.mu || 240.0),
        Vu: Number(loadI.Vu || data.vu || 180.0)
      },
      center_m: {
        Mu_pos: Number(loadM.Mu_pos || data.mu || 240.0),
        Mu_neg: Number(loadM.Mu_neg || 0),
        Vu: Number(loadM.Vu || 40.0)
      },
      end_j: {
        Mu_pos: Number(loadJ.Mu_pos || 0),
        Mu_neg: Number(loadJ.Mu_neg || data.mu || 240.0),
        Vu: Number(loadJ.Vu || data.vu || 180.0)
      }
    };

    return {
      b,
      h,
      length,
      cover,
      shape,
      bf,
      hf,
      stations,
      torsionSideCount,
      torsionSideBar,
      factored
    };
  }

  // ---------------------------------------------------------------------------
  // Helper: Theme Palette Detector (Dark / Light)
  // ---------------------------------------------------------------------------
  function getThemePalette() {
    const isDark = (typeof document !== 'undefined' && document.body)
      ? document.body.getAttribute('data-theme') !== 'light'
      : true;

    return {
      isDark,
      bg: isDark ? '#0f172a' : '#ffffff',
      concGradStart: isDark ? '#1e293b' : '#f8fafc',
      concGradEnd: isDark ? '#0f172a' : '#e2e8f0',
      concStroke: isDark ? '#475569' : '#94a3b8',
      centerLine: isDark ? 'rgba(148, 163, 184, 0.25)' : 'rgba(100, 116, 139, 0.35)',
      dimStroke: isDark ? '#94a3b8' : '#64748b',
      dimText: isDark ? '#cbd5e1' : '#334155',
      badgeBg: isDark ? 'rgba(15, 23, 42, 0.85)' : 'rgba(241, 245, 249, 0.95)',
      calloutTop: isDark ? '#cbd5e1' : '#1e293b',
      calloutBot: isDark ? '#cbd5e1' : '#1e293b',
      stirrupBadge: isDark ? '#f59e0b' : '#d97706',
      longitudinalFill: isDark ? '#1e293b' : '#f1f5f9',
      longitudinalStroke: isDark ? '#475569' : '#94a3b8'
    };
  }

  // ---------------------------------------------------------------------------
  // Helper: Draw Dimension Line (Horizontal / Vertical)
  // ---------------------------------------------------------------------------
  function drawCADDimension(ctx, x1, y1, x2, y2, text, offset = 22, isVertical = false) {
    const pal = getThemePalette();
    ctx.save();
    ctx.strokeStyle = pal.dimStroke;
    ctx.fillStyle = pal.dimText;
    ctx.lineWidth = 1.0;
    ctx.font = '10px "Inter", "Pretendard", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    const arrow = 4;

    if (isVertical) {
      const x = x1 + offset;
      ctx.beginPath();
      ctx.moveTo(x1, y1); ctx.lineTo(x + (offset > 0 ? 4 : -4), y1);
      ctx.moveTo(x2, y2); ctx.lineTo(x + (offset > 0 ? 4 : -4), y2);
      ctx.moveTo(x, y1); ctx.lineTo(x, y2);
      ctx.stroke();

      // Arrows
      ctx.beginPath();
      ctx.moveTo(x, y1); ctx.lineTo(x - arrow / 2, y1 + arrow); ctx.lineTo(x + arrow / 2, y1 + arrow); ctx.closePath();
      ctx.moveTo(x, y2); ctx.lineTo(x - arrow / 2, y2 - arrow); ctx.lineTo(x + arrow / 2, y2 - arrow); ctx.closePath();
      ctx.fill();

      // Text
      ctx.save();
      ctx.translate(x + (offset > 0 ? 12 : -12), (y1 + y2) / 2);
      ctx.rotate(-Math.PI / 2);
      ctx.fillText(text, 0, 0);
      ctx.restore();
    } else {
      const y = y1 + offset;
      ctx.beginPath();
      ctx.moveTo(x1, y1); ctx.lineTo(x1, y + (offset > 0 ? 4 : -4));
      ctx.moveTo(x2, y2); ctx.lineTo(x2, y + (offset > 0 ? 4 : -4));
      ctx.moveTo(x1, y); ctx.lineTo(x2, y);
      ctx.stroke();

      // Arrows
      ctx.beginPath();
      ctx.moveTo(x1, y); ctx.lineTo(x1 + arrow, y - arrow / 2); ctx.lineTo(x1 + arrow, y + arrow / 2); ctx.closePath();
      ctx.moveTo(x2, y); ctx.lineTo(x2 - arrow, y - arrow / 2); ctx.lineTo(x2 - arrow, y + arrow / 2); ctx.closePath();
      ctx.fill();

      ctx.fillText(text, (x1 + x2) / 2, y + (offset > 0 ? 10 : -10));
    }
    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Helper: Draw Metallic Solid Rebar Dot with Highlight
  // ---------------------------------------------------------------------------
  function drawRebarDot(ctx, cx, cy, radius, isTop = false) {
    ctx.save();
    const r = Math.max(radius, 4.0);

    const grad = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
    if (isTop) {
      grad.addColorStop(0, '#93c5fd');
      grad.addColorStop(0.65, '#3b82f6');
      grad.addColorStop(1, '#1d4ed8');
    } else {
      grad.addColorStop(0, '#fca5a5');
      grad.addColorStop(0.65, '#ef4444');
      grad.addColorStop(1, '#991b1b');
    }

    ctx.fillStyle = grad;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // White specular highlight
    ctx.beginPath();
    ctx.arc(cx - r * 0.3, cy - r * 0.3, r * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.fill();

    ctx.restore();
  }

  // ===========================================================================
  // 1. Viewport A (Top): Longitudinal Rebar & Force Envelope (renderLongitudinalView)
  // ===========================================================================
  VectorRCBeam.renderLongitudinalView = function (ctx, width, height, rawData = {}, showDimensions = true) {
    const interactiveElements = [];
    const beam = extractBeamData(rawData);
    const pal = getThemePalette();

    // 1. Engineering Slate Dark/Light Canvas Background
    ctx.fillStyle = pal.bg;
    ctx.fillRect(0, 0, width, height);

    // Margins
    const padL = 60;
    const padR = 50;
    const padT = 36;
    const padB = 40;

    const availW = width - padL - padR;
    const availH = height - padT - padB;

    // Longitudinal Beam Geometry
    // Scale span L to fit availW * 0.85
    const spanPixels = Math.max(availW * 0.85, 200);
    const startX = padL + (availW - spanPixels) / 2;
    const endX = startX + spanPixels;
    const midX = (startX + endX) / 2;

    // Beam depth representation on longitudinal elevation
    const beamH = Math.min(Math.max(availH * 0.35, 45), 75);
    const beamTopY = padT + (availH - beamH) / 2 - 12;
    const beamBotY = beamTopY + beamH;
    const beamCenterY = (beamTopY + beamBotY) / 2;

    // Station X Coordinates
    const xL4_I = startX + spanPixels * 0.25;
    const xL4_J = endX - spanPixels * 0.25;

    // -------------------------------------------------------------
    // 2. Concrete Beam Body & Boundary Supports (Hinge / Roller)
    // -------------------------------------------------------------
    ctx.save();
    // Concrete Body Gradient
    const beamGrad = ctx.createLinearGradient(0, beamTopY, 0, beamBotY);
    beamGrad.addColorStop(0, '#1e293b');
    beamGrad.addColorStop(1, '#0f172a');
    ctx.fillStyle = beamGrad;
    ctx.strokeStyle = '#64748b';
    ctx.lineWidth = 2.0;

    ctx.fillRect(startX, beamTopY, spanPixels, beamH);
    ctx.strokeRect(startX, beamTopY, spanPixels, beamH);

    // Left Support: Hinge Symbol (End-I)
    const supSize = 14;
    ctx.fillStyle = '#475569';
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(startX, beamBotY);
    ctx.lineTo(startX - supSize * 0.8, beamBotY + supSize);
    ctx.lineTo(startX + supSize * 0.8, beamBotY + supSize);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Hinge Ground Line & Hatching
    ctx.beginPath();
    ctx.moveTo(startX - supSize - 4, beamBotY + supSize);
    ctx.lineTo(startX + supSize + 4, beamBotY + supSize);
    ctx.stroke();
    for (let hx = startX - supSize - 2; hx <= startX + supSize + 2; hx += 5) {
      ctx.moveTo(hx, beamBotY + supSize);
      ctx.lineTo(hx - 4, beamBotY + supSize + 5);
    }
    ctx.stroke();

    // Right Support: Roller Symbol (End-J)
    ctx.beginPath();
    ctx.moveTo(endX, beamBotY);
    ctx.lineTo(endX - supSize * 0.8, beamBotY + supSize * 0.65);
    ctx.lineTo(endX + supSize * 0.8, beamBotY + supSize * 0.65);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Roller wheels (2 small circles)
    const rWheel = 2.5;
    ctx.beginPath();
    ctx.arc(endX - supSize * 0.4, beamBotY + supSize * 0.65 + rWheel + 1, rWheel, 0, Math.PI * 2);
    ctx.arc(endX + supSize * 0.4, beamBotY + supSize * 0.65 + rWheel + 1, rWheel, 0, Math.PI * 2);
    ctx.fillStyle = '#cbd5e1';
    ctx.fill();
    ctx.stroke();

    // Roller Ground Line & Hatching
    const rollerGroundY = beamBotY + supSize * 0.65 + rWheel * 2 + 2;
    ctx.beginPath();
    ctx.moveTo(endX - supSize - 4, rollerGroundY);
    ctx.lineTo(endX + supSize + 4, rollerGroundY);
    ctx.stroke();
    for (let hx = endX - supSize - 2; hx <= endX + supSize + 2; hx += 5) {
      ctx.moveTo(hx, rollerGroundY);
      ctx.lineTo(hx - 4, rollerGroundY + 5);
    }
    ctx.stroke();
    ctx.restore();

    // -------------------------------------------------------------
    // 3. Zone Partition Lines (End-I: L/4, Center-M: L/2, End-J: L/4)
    // -------------------------------------------------------------
    ctx.save();
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
    ctx.lineWidth = 1.0;
    ctx.setLineDash([4, 4]);

    ctx.beginPath();
    ctx.moveTo(xL4_I, beamTopY - 14);
    ctx.lineTo(xL4_I, beamBotY + 18);
    ctx.moveTo(xL4_J, beamTopY - 14);
    ctx.lineTo(xL4_J, beamBotY + 18);
    ctx.stroke();
    ctx.setLineDash([]);

    // Zone Title Badges
    ctx.font = '600 10px "Inter", "Pretendard", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(`End-I (L/4: ${(beam.length / 4).toFixed(0)}mm)`, (startX + xL4_I) / 2, beamTopY - 18);
    ctx.fillStyle = '#34d399';
    ctx.fillText(`Center-M (L/2: ${(beam.length / 2).toFixed(0)}mm)`, midX, beamTopY - 18);
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(`End-J (L/4: ${(beam.length / 4).toFixed(0)}mm)`, (xL4_J + endX) / 2, beamTopY - 18);
    ctx.restore();

    // -------------------------------------------------------------
    // 4. Longitudinal Stirrup Pitch Spacing (Vertical Ticks)
    // -------------------------------------------------------------
    ctx.save();
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 1.2;

    const stirTopY = beamTopY + 6;
    const stirBotY = beamBotY - 6;

    // End-I stirrup lines
    const stirPitchI = 14;
    for (let sx = startX + 8; sx <= xL4_I - 4; sx += stirPitchI) {
      ctx.beginPath();
      ctx.moveTo(sx, stirTopY);
      ctx.lineTo(sx, stirBotY);
      ctx.stroke();
    }

    // Center-M stirrup lines (wider pitch)
    const stirPitchM = 24;
    for (let sx = xL4_I + 8; sx <= xL4_J - 8; sx += stirPitchM) {
      ctx.beginPath();
      ctx.moveTo(sx, stirTopY);
      ctx.lineTo(sx, stirBotY);
      ctx.stroke();
    }

    // End-J stirrup lines
    const stirPitchJ = 14;
    for (let sx = xL4_J + 4; sx <= endX - 8; sx += stirPitchJ) {
      ctx.beginPath();
      ctx.moveTo(sx, stirTopY);
      ctx.lineTo(sx, stirBotY);
      ctx.stroke();
    }
    ctx.restore();

    // -------------------------------------------------------------
    // 5. Longitudinal Main Rebar Lines & Hooks
    // -------------------------------------------------------------
    ctx.save();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    const rebarTopY = beamTopY + 8;
    const rebarBotY = beamBotY - 8;
    const hookH = beamH * 0.45;
    const l3_I = startX + spanPixels * 0.33;
    const l3_J = endX - spanPixels * 0.33;

    // Top Rebar: End-I 부모멘트 철근 (90° Downward Hook -> L/3 연장)
    ctx.beginPath();
    ctx.moveTo(startX + 6, rebarTopY + hookH);
    ctx.lineTo(startX + 6, rebarTopY);
    ctx.lineTo(l3_I, rebarTopY);
    ctx.stroke();

    // Top Rebar: End-J 부모멘트 철근 (L/3 연장 -> 90° Downward Hook)
    ctx.beginPath();
    ctx.moveTo(l3_J, rebarTopY);
    ctx.lineTo(endX - 6, rebarTopY);
    ctx.lineTo(endX - 6, rebarTopY + hookH);
    ctx.stroke();

    // Top Rebar: Center Assembly bar (Thin connection)
    ctx.save();
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3, 2]);
    ctx.beginPath();
    ctx.moveTo(l3_I, rebarTopY);
    ctx.lineTo(l3_J, rebarTopY);
    ctx.stroke();
    ctx.restore();

    // Bottom Rebar: 전 경간 연속 정모멘트 철근 (90° Upward Hooks on both ends)
    ctx.beginPath();
    ctx.moveTo(startX + 6, rebarBotY - hookH);
    ctx.lineTo(startX + 6, rebarBotY);
    ctx.lineTo(endX - 6, rebarBotY);
    ctx.lineTo(endX - 6, rebarBotY - hookH);
    ctx.stroke();

    // 2nd Layer Bottom Rebar if exists
    if (beam.stations.center_m.bot2.count > 0) {
      ctx.save();
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 2.0;
      const bot2Y = rebarBotY - 6;
      ctx.beginPath();
      ctx.moveTo(startX + spanPixels * 0.15, bot2Y);
      ctx.lineTo(endX - spanPixels * 0.15, bot2Y);
      ctx.stroke();
      ctx.restore();
    }
    ctx.restore();

    // -------------------------------------------------------------
    // 6. Factored Force Envelope Overlays (BMD / SFD)
    // -------------------------------------------------------------
    const muPos = beam.factored.center_m.Mu_pos || 240.0;
    const muNegI = beam.factored.end_i.Mu_neg || 240.0;
    const muNegJ = beam.factored.end_j.Mu_neg || 240.0;
    const vuI = beam.factored.end_i.Vu || 180.0;
    const vuJ = beam.factored.end_j.Vu || 180.0;

    // (A) Bending Moment Diagram (BMD) Parabolic Overlay [Blue]
    ctx.save();
    const maxBmdHeight = Math.min(availH * 0.32, 55);
    ctx.fillStyle = 'rgba(59, 130, 246, 0.22)';
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2.0;

    ctx.beginPath();
    // Start at End-I negative moment (drawn upwards)
    const bmdBaseY = beamBotY + 8;
    ctx.moveTo(startX, bmdBaseY);

    const bmdSteps = 40;
    for (let i = 0; i <= bmdSteps; i++) {
      const t = i / bmdSteps; // 0 to 1
      const x = startX + t * spanPixels;
      // Moment equation: Negative at ends, positive at center
      // M(t) = -Mu_neg * (1 - 4*(t-0.5)^2) + Mu_pos * 4*t*(1-t)
      const normM = (4 * t * (1 - t)) * (muPos / Math.max(muPos, 1)) - (1 - 4 * Math.pow(t - 0.5, 2) * 0.5) * (muNegI / Math.max(muPos, 1)) * 0.45;
      const y = bmdBaseY + normM * maxBmdHeight;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(endX, bmdBaseY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // BMD Labels
    ctx.fillStyle = '#60a5fa';
    ctx.font = 'bold 10px "Inter", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`+Mu = ${muPos.toFixed(1)} kN·m`, midX, bmdBaseY + maxBmdHeight + 14);
    ctx.fillText(`-Mu = ${muNegI.toFixed(1)}`, startX + 28, bmdBaseY - 6);
    ctx.fillText(`-Mu = ${muNegJ.toFixed(1)}`, endX - 28, bmdBaseY - 6);
    ctx.restore();

    // (B) Shear Force Diagram (SFD) Linear Overlay [Orange]
    ctx.save();
    const sfdBaseY = beamTopY - 6;
    const maxSfdH = Math.min(availH * 0.22, 38);
    ctx.fillStyle = 'rgba(249, 115, 22, 0.20)';
    ctx.strokeStyle = '#f97316';
    ctx.lineWidth = 1.8;

    ctx.beginPath();
    ctx.moveTo(startX, sfdBaseY);
    ctx.lineTo(startX, sfdBaseY - maxSfdH);
    ctx.lineTo(midX, sfdBaseY);
    ctx.lineTo(endX, sfdBaseY + maxSfdH);
    ctx.lineTo(endX, sfdBaseY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // SFD Labels
    ctx.fillStyle = '#fb923c';
    ctx.font = 'bold 10px "Inter", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`+Vu = ${vuI.toFixed(1)} kN`, startX + 4, sfdBaseY - maxSfdH - 4);
    ctx.textAlign = 'right';
    ctx.fillText(`-Vu = ${vuJ.toFixed(1)} kN`, endX - 4, sfdBaseY + maxSfdH + 12);
    ctx.restore();

    // -------------------------------------------------------------
    // 7. Legend and Dimension Lines
    // -------------------------------------------------------------
    // Legend Box (Top Right)
    ctx.save();
    const legX = width - padR - 150;
    const legY = 10;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.fillRect(legX, legY, 150, 22);
    ctx.strokeRect(legX, legY, 150, 22);

    ctx.font = '9px "Pretendard", sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    ctx.fillStyle = '#38bdf8';
    ctx.fillRect(legX + 8, legY + 7, 8, 8);
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('BMD(휨)', legX + 20, legY + 11);

    ctx.fillStyle = '#f97316';
    ctx.fillRect(legX + 68, legY + 7, 8, 8);
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('SFD(전단)', legX + 80, legY + 11);
    ctx.restore();

    if (showDimensions) {
      drawCADDimension(ctx, startX, beamBotY, endX, beamBotY, `L = ${beam.length.toLocaleString()} mm`, 44, false);
      drawCADDimension(ctx, startX, beamTopY, startX, beamBotY, `h = ${beam.h} mm`, -32, true);
    }

    // -------------------------------------------------------------
    // 8. Collect Interactive Hover Targets
    // -------------------------------------------------------------
    // Midspan Moment Peak Target
    interactiveElements.push({
      type: 'moment_mid',
      x: midX,
      y: bmdBaseY + maxBmdHeight * 0.7,
      r: 12,
      title: '중앙부 최대 휨모멘트 (Mu)',
      detail: `+Mu = ${muPos.toFixed(1)} kN·m | 배근: 하부 ${beam.stations.center_m.bot1.str}`
    });

    // End-I Shear Peak Target
    interactiveElements.push({
      type: 'shear_end_i',
      x: startX + 15,
      y: sfdBaseY - maxSfdH * 0.5,
      r: 12,
      title: 'End-I 최대 전단력 (Vu)',
      detail: `Vu = ${vuI.toFixed(1)} kN | 스터럽: ${beam.stations.end_i.stirrup.text}`
    });

    // End-J Shear Peak Target
    interactiveElements.push({
      type: 'shear_end_j',
      x: endX - 15,
      y: sfdBaseY + maxSfdH * 0.5,
      r: 12,
      title: 'End-J 최대 전단력 (Vu)',
      detail: `Vu = ${vuJ.toFixed(1)} kN | 스터럽: ${beam.stations.end_j.stirrup.text}`
    });

    return interactiveElements;
  };

  // ===========================================================================
  // 2. Viewport B (Bottom): 3-Station Cross-Sections (renderCrossSections)
  // ===========================================================================
  VectorRCBeam.renderCrossSections = function (ctx, width, height, rawData = {}, result = {}, is3DMode = false) {
    const interactiveElements = [];
    const beam = extractBeamData(rawData);
    const pal = getThemePalette();

    // 1. Clean Deep Engineering Slate Background (Theme-Aware)
    ctx.fillStyle = pal.bg;
    ctx.fillRect(0, 0, width, height);

    // 3 Stations: [End-I] | [Center-M] | [End-J]
    const slotKeys = [
      { key: 'end_i', label: '[End-I] 좌단부 단면', color: '#38bdf8' },
      { key: 'center_m', label: '[Center-M] 중앙부 단면', color: '#34d399' },
      { key: 'end_j', label: '[End-J] 우단부 단면', color: '#38bdf8' }
    ];

    const slotW = width / 3;
    const margin = 20;

    // Cross-Section Scale: Compute fit based on max(b, h)
    const availSlotW = slotW - margin * 2;
    const availSlotH = height - 70;
    const maxDim = Math.max(beam.b, beam.h, beam.shape === 'T_BEAM' ? beam.bf : 0);
    const scale = Math.min(availSlotW / maxDim, availSlotH / beam.h);

    const drawB = beam.b * scale;
    const drawH = beam.h * scale;
    const centerY = height / 2 + 10;

    slotKeys.forEach((slot, idx) => {
      const centerX = slotW * idx + slotW / 2;
      const st = beam.stations[slot.key];

      // -----------------------------------------------------------
      // A. Station Title Header Badge
      // -----------------------------------------------------------
      ctx.save();
      const badgeY = 16;
      ctx.font = '600 11px "Inter", "Pretendard", sans-serif';
      const textW = ctx.measureText(slot.label).width + 16;
      ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
      ctx.strokeStyle = slot.color;
      ctx.lineWidth = 1.0;
      ctx.strokeRect(centerX - textW / 2, badgeY, textW, 20);
      ctx.fillRect(centerX - textW / 2, badgeY, textW, 20);

      ctx.fillStyle = slot.color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(slot.label, centerX, badgeY + 10);
      ctx.restore();

      // -----------------------------------------------------------
      // B. Concrete Outline (Rectangular or T-Beam)
      // -----------------------------------------------------------
      const secX0 = centerX - drawB / 2;
      const secY0 = centerY - drawH / 2;

      ctx.save();
      // Concrete Body Fill & Stroke
      const concGrad = ctx.createLinearGradient(secX0, secY0, secX0 + drawB, secY0 + drawH);
      concGrad.addColorStop(0, '#1e293b');
      concGrad.addColorStop(1, '#0f172a');
      ctx.fillStyle = concGrad;
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2.0;

      if (beam.shape === 'T_BEAM') {
        const drawBf = beam.bf * scale;
        const drawHf = beam.hf * scale;
        const tfX0 = centerX - drawBf / 2;
        ctx.beginPath();
        ctx.moveTo(tfX0, secY0);
        ctx.lineTo(tfX0 + drawBf, secY0);
        ctx.lineTo(tfX0 + drawBf, secY0 + drawHf);
        ctx.lineTo(secX0 + drawB, secY0 + drawHf);
        ctx.lineTo(secX0 + drawB, secY0 + drawH);
        ctx.lineTo(secX0, secY0 + drawH);
        ctx.lineTo(secX0, secY0 + drawHf);
        ctx.lineTo(tfX0, secY0 + drawHf);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else {
        ctx.fillRect(secX0, secY0, drawB, drawH);
        ctx.strokeRect(secX0, secY0, drawB, drawH);
      }

      // Subtle Centerlines
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(centerX, secY0 - 8); ctx.lineTo(centerX, secY0 + drawH + 8);
      ctx.moveTo(secX0 - 8, centerY); ctx.lineTo(secX0 + drawB + 8, centerY);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();

      // -----------------------------------------------------------
      // C. Closed Stirrup with 135-Degree Seismic Hooks
      // -----------------------------------------------------------
      const coverPx = beam.cover * scale;
      const stirX = secX0 + coverPx;
      const stirY = secY0 + coverPx;
      const stirW = drawB - coverPx * 2;
      const stirH = drawH - coverPx * 2;
      const stirDia = st.stirrup.dia;

      ctx.save();
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2.0;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';

      // 1. Closed rectangular loop
      ctx.strokeRect(stirX, stirY, stirW, stirH);

      // 2. 135-degree seismic hooks at top-left and top-right corners
      const hookLen = Math.max(12, stirDia * scale * 1.6);
      const hookRad = (135 * Math.PI) / 180;
      const hookDx = Math.cos(hookRad) * hookLen;
      const hookDy = Math.sin(hookRad) * hookLen;

      // Top-Left Corner Hook
      ctx.beginPath();
      ctx.moveTo(stirX, stirY);
      ctx.lineTo(stirX - hookDx, stirY + hookDy);
      ctx.stroke();

      // Top-Right Corner Hook
      ctx.beginPath();
      ctx.moveTo(stirX + stirW, stirY);
      ctx.lineTo(stirX + stirW + hookDx, stirY + hookDy);
      ctx.stroke();

      // Cross-tie for 4-leg stirrups
      if (st.legs >= 4) {
        ctx.setLineDash([3, 2]);
        ctx.beginPath();
        ctx.moveTo(centerX, stirY);
        ctx.lineTo(centerX, stirY + stirH);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.restore();

      // -----------------------------------------------------------
      // D. Multi-Layer Rebars (Top 1/2 & Bottom 1/2) & Torsion Bars
      // -----------------------------------------------------------
      const clearStepY = Math.max(25 * scale, 12);
      const rebarDiaBase = Math.max(st.top1.dia, st.bot1.dia, 22);
      const rebarR = Math.max((rebarDiaBase / 2) * scale, 4.5);

      const innerPad = 4;
      const barXMin = stirX + innerPad;
      const barXMax = stirX + stirW - innerPad;
      const barW = barXMax - barXMin;

      // (1) Top Layer 1 Rebars
      if (st.top1.count > 0) {
        const yTop1 = stirY + innerPad + rebarR;
        for (let bIdx = 0; bIdx < st.top1.count; bIdx++) {
          const x = (st.top1.count === 1) ? centerX : barXMin + (bIdx / (st.top1.count - 1)) * barW;
          drawRebarDot(ctx, x, yTop1, rebarR, true);

          interactiveElements.push({
            type: 'rebar_top1',
            x: x,
            y: yTop1,
            r: rebarR + 3,
            title: `${slot.label} - 상부 1단 #${bIdx + 1}`,
            detail: `규격: D${st.top1.dia} | 총 배근: ${st.top1.str} (d' = ${beam.cover}mm)`
          });
        }
      }

      // (2) Top Layer 2 Rebars
      if (st.top2.count > 0) {
        const yTop2 = stirY + innerPad + rebarR + clearStepY;
        for (let bIdx = 0; bIdx < st.top2.count; bIdx++) {
          const x = (st.top2.count === 1) ? centerX : barXMin + (bIdx / (st.top2.count - 1)) * barW;
          drawRebarDot(ctx, x, yTop2, rebarR * 0.9, true);

          interactiveElements.push({
            type: 'rebar_top2',
            x: x,
            y: yTop2,
            r: rebarR + 3,
            title: `${slot.label} - 상부 2단 #${bIdx + 1}`,
            detail: `규격: D${st.top2.dia} | 2단 배근: ${st.top2.str} (순간격 25mm)`
          });
        }
      }

      // (3) Bottom Layer 1 Rebars
      if (st.bot1.count > 0) {
        const yBot1 = stirY + stirH - innerPad - rebarR;
        for (let bIdx = 0; bIdx < st.bot1.count; bIdx++) {
          const x = (st.bot1.count === 1) ? centerX : barXMin + (bIdx / (st.bot1.count - 1)) * barW;
          drawRebarDot(ctx, x, yBot1, rebarR, false);

          interactiveElements.push({
            type: 'rebar_bot1',
            x: x,
            y: yBot1,
            r: rebarR + 3,
            title: `${slot.label} - 하부 1단 #${bIdx + 1}`,
            detail: `규격: D${st.bot1.dia} | 총 배근: ${st.bot1.str} (d = ${beam.h - beam.cover}mm)`
          });
        }
      }

      // (4) Bottom Layer 2 Rebars
      if (st.bot2.count > 0) {
        const yBot2 = stirY + stirH - innerPad - rebarR - clearStepY;
        for (let bIdx = 0; bIdx < st.bot2.count; bIdx++) {
          const x = (st.bot2.count === 1) ? centerX : barXMin + (bIdx / (st.bot2.count - 1)) * barW;
          drawRebarDot(ctx, x, yBot2, rebarR * 0.9, false);

          interactiveElements.push({
            type: 'rebar_bot2',
            x: x,
            y: yBot2,
            r: rebarR + 3,
            title: `${slot.label} - 하부 2단 #${bIdx + 1}`,
            detail: `규격: D${st.bot2.dia} | 2단 배근: ${st.bot2.str} (순간격 25mm)`
          });
        }
      }

      // (5) Torsion Side Rebars
      if (beam.torsionSideCount > 0) {
        const numSideRows = Math.floor(beam.torsionSideCount / 2);
        const ySideTop = stirY + innerPad + rebarR + clearStepY + 10;
        const ySideBot = stirY + stirH - innerPad - rebarR - clearStepY - 10;
        const sideStep = (ySideBot - ySideTop) / Math.max(numSideRows, 1);

        for (let sIdx = 0; sIdx < numSideRows; sIdx++) {
          const sy = ySideTop + sIdx * sideStep;
          drawRebarDot(ctx, barXMin, sy, rebarR * 0.75, false);
          drawRebarDot(ctx, barXMax, sy, rebarR * 0.75, false);

          interactiveElements.push({
            type: 'torsion_side',
            x: barXMin,
            y: sy,
            r: rebarR + 2,
            title: `${slot.label} - 측면 비틀림 철근`,
            detail: `규격: D${beam.torsionSideBar.dia || 13} (피복 유지)`
          });
        }
      }

      // -----------------------------------------------------------
      // E. Rebar Callout Tags & Leader Lines
      // -----------------------------------------------------------
      ctx.save();
      ctx.font = '10px "Inter", "Pretendard", sans-serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.strokeStyle = '#64748b';
      ctx.lineWidth = 1.0;

      // Top Tag
      const topTagText = st.top2.count > 0 ? `${st.top1.str} (2단:${st.top2.str})` : st.top1.str;
      const topTagY = secY0 - 12;
      ctx.textAlign = 'center';
      ctx.fillText(topTagText, centerX, topTagY);

      // Bottom Tag
      const botTagText = st.bot2.count > 0 ? `${st.bot1.str} (2단:${st.bot2.str})` : st.bot1.str;
      const botTagY = secY0 + drawH + 24;
      ctx.fillText(botTagText, centerX, botTagY);

      // Stirrup Tag (Left side)
      ctx.fillStyle = '#f59e0b';
      ctx.textAlign = 'right';
      ctx.fillText(st.stirrup.text, secX0 - 6, centerY);
      ctx.restore();

      // Dimension Lines for End-I (or slot 0) only to prevent clutter
      if (idx === 0) {
        drawCADDimension(ctx, secX0, secY0 + drawH, secX0 + drawB, secY0 + drawH, `b=${beam.b}`, 34, false);
        drawCADDimension(ctx, secX0, secY0, secX0, secY0 + drawH, `h=${beam.h}`, -24, true);
      }
    });

    return interactiveElements;
  };

  // ===========================================================================
  // 3. Station Dedicated Cross-Section (renderStationSection)
  // Conforms to Req 22 / 22-3 Bugfix: 3-tier vertical stacked station view
  // ===========================================================================
  VectorRCBeam.renderStationSection = function (ctx, width, height, stationKey = 'center_m', rawData = {}, result = {}, showDimensions = true) {
    const interactiveElements = [];
    const beam = extractBeamData(rawData);
    const pal = getThemePalette();

    // 1. Clean Deep Engineering Slate Background (Theme-Aware)
    ctx.fillStyle = pal.bg;
    ctx.fillRect(0, 0, width, height);

    const stationMeta = {
      end_i: { key: 'end_i', label: '단부( i ) 단면 배근도', code: 'End-I', color: '#38bdf8' },
      center_m: { key: 'center_m', label: '중앙( m ) 단면 배근도', code: 'Center-M', color: '#34d399' },
      end_j: { key: 'end_j', label: '단부( j ) 단면 배근도', code: 'End-J', color: '#38bdf8' }
    };
    const meta = stationMeta[stationKey] || stationMeta.center_m;
    const st = beam.stations[stationKey] || beam.stations.center_m;

    // Cross-Section Scale: Center in canvas with generous margins for CAD dimensions and callout tags
    const padX = 75;
    const padY = 48;
    const availW = Math.max(width - padX * 2, 80);
    const availH = Math.max(height - padY * 2, 80);
    const maxDim = Math.max(beam.b, beam.h, beam.shape === 'T_BEAM' ? beam.bf : 0);
    const scale = Math.min(availW / maxDim, availH / beam.h);

    const drawB = beam.b * scale;
    const drawH = beam.h * scale;
    const centerX = width / 2;
    const centerY = height / 2;
    const secX0 = centerX - drawB / 2;
    const secY0 = centerY - drawH / 2;

    // -----------------------------------------------------------
    // A. Subtle Station Badge (Top-Left corner)
    // -----------------------------------------------------------
    ctx.save();
    ctx.font = '600 11px "Inter", "Pretendard", sans-serif';
    ctx.fillStyle = pal.badgeBg;
    ctx.strokeStyle = meta.color;
    ctx.lineWidth = 1.0;
    const badgeText = `${meta.label} [${meta.code}]`;
    const textW = ctx.measureText(badgeText).width + 16;
    ctx.strokeRect(12, 10, textW, 22);
    ctx.fillRect(12, 10, textW, 22);
    ctx.fillStyle = meta.color;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(badgeText, 20, 21);
    ctx.restore();

    // -----------------------------------------------------------
    // B. Concrete Outline (Rectangular or T-Beam)
    // -----------------------------------------------------------
    ctx.save();
    const concGrad = ctx.createLinearGradient(secX0, secY0, secX0 + drawB, secY0 + drawH);
    concGrad.addColorStop(0, pal.concGradStart);
    concGrad.addColorStop(1, pal.concGradEnd);
    ctx.fillStyle = concGrad;
    ctx.strokeStyle = pal.concStroke;
    ctx.lineWidth = 2.0;

    if (beam.shape === 'T_BEAM') {
      const drawBf = beam.bf * scale;
      const drawHf = beam.hf * scale;
      const tfX0 = centerX - drawBf / 2;
      ctx.beginPath();
      ctx.moveTo(tfX0, secY0);
      ctx.lineTo(tfX0 + drawBf, secY0);
      ctx.lineTo(tfX0 + drawBf, secY0 + drawHf);
      ctx.lineTo(secX0 + drawB, secY0 + drawHf);
      ctx.lineTo(secX0 + drawB, secY0 + drawH);
      ctx.lineTo(secX0, secY0 + drawH);
      ctx.lineTo(secX0, secY0 + drawHf);
      ctx.lineTo(tfX0, secY0 + drawHf);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else {
      ctx.fillRect(secX0, secY0, drawB, drawH);
      ctx.strokeRect(secX0, secY0, drawB, drawH);
    }

    // Subtle Centerlines
    ctx.strokeStyle = pal.centerLine;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(centerX, secY0 - 10); ctx.lineTo(centerX, secY0 + drawH + 10);
    ctx.moveTo(secX0 - 10, centerY); ctx.lineTo(secX0 + drawB + 10, centerY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // -----------------------------------------------------------
    // C. Closed Stirrup with 135-Degree Seismic Hooks
    // -----------------------------------------------------------
    const coverPx = beam.cover * scale;
    const stirX = secX0 + coverPx;
    const stirY = secY0 + coverPx;
    const stirW = Math.max(drawB - coverPx * 2, 10);
    const stirH = Math.max(drawH - coverPx * 2, 10);
    const stirDia = st.stirrup.dia;

    ctx.save();
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 2.0;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    // 1. Closed rectangular loop
    ctx.strokeRect(stirX, stirY, stirW, stirH);

    // 2. 135-degree seismic hooks at top-left and top-right corners
    const hookLen = Math.max(12, stirDia * scale * 1.6);
    const hookRad = (135 * Math.PI) / 180;
    const hookDx = Math.cos(hookRad) * hookLen;
    const hookDy = Math.sin(hookRad) * hookLen;

    ctx.beginPath();
    ctx.moveTo(stirX, stirY);
    ctx.lineTo(stirX - hookDx, stirY + hookDy);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(stirX + stirW, stirY);
    ctx.lineTo(stirX + stirW + hookDx, stirY + hookDy);
    ctx.stroke();

    // Cross-tie for 4-leg stirrups
    if (st.legs >= 4) {
      ctx.setLineDash([3, 2]);
      ctx.beginPath();
      ctx.moveTo(centerX, stirY);
      ctx.lineTo(centerX, stirY + stirH);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.restore();

    // -----------------------------------------------------------
    // D. Multi-Layer Rebars (Top 1/2 & Bottom 1/2) & Torsion Bars
    // -----------------------------------------------------------
    const clearStepY = Math.max(25 * scale, 14);
    const rebarDiaBase = Math.max(st.top1.dia, st.bot1.dia, 22);
    const rebarR = Math.max((rebarDiaBase / 2) * scale, 5.0);

    const innerPad = 4;
    const barXMin = stirX + innerPad;
    const barXMax = stirX + stirW - innerPad;
    const barW = barXMax - barXMin;

    // (1) Top Layer 1 Rebars
    if (st.top1.count > 0) {
      const yTop1 = stirY + innerPad + rebarR;
      for (let bIdx = 0; bIdx < st.top1.count; bIdx++) {
        const x = (st.top1.count === 1) ? centerX : barXMin + (bIdx / (st.top1.count - 1)) * barW;
        drawRebarDot(ctx, x, yTop1, rebarR, true);

        interactiveElements.push({
          type: 'rebar_top1',
          x: x,
          y: yTop1,
          r: rebarR + 4,
          title: `${meta.label} - 상부 1단 #${bIdx + 1}`,
          detail: `규격: D${st.top1.dia} | 총 배근: ${st.top1.str} (d' = ${beam.cover}mm)`
        });
      }
    }

    // (2) Top Layer 2 Rebars
    if (st.top2.count > 0) {
      const yTop2 = stirY + innerPad + rebarR + clearStepY;
      for (let bIdx = 0; bIdx < st.top2.count; bIdx++) {
        const x = (st.top2.count === 1) ? centerX : barXMin + (bIdx / (st.top2.count - 1)) * barW;
        drawRebarDot(ctx, x, yTop2, rebarR * 0.9, true);

        interactiveElements.push({
          type: 'rebar_top2',
          x: x,
          y: yTop2,
          r: rebarR + 4,
          title: `${meta.label} - 상부 2단 #${bIdx + 1}`,
          detail: `규격: D${st.top2.dia} | 2단 배근: ${st.top2.str} (순간격 25mm)`
        });
      }
    }

    // (3) Bottom Layer 1 Rebars
    if (st.bot1.count > 0) {
      const yBot1 = stirY + stirH - innerPad - rebarR;
      for (let bIdx = 0; bIdx < st.bot1.count; bIdx++) {
        const x = (st.bot1.count === 1) ? centerX : barXMin + (bIdx / (st.bot1.count - 1)) * barW;
        drawRebarDot(ctx, x, yBot1, rebarR, false);

        interactiveElements.push({
          type: 'rebar_bot1',
          x: x,
          y: yBot1,
          r: rebarR + 4,
          title: `${meta.label} - 하부 1단 #${bIdx + 1}`,
          detail: `규격: D${st.bot1.dia} | 총 배근: ${st.bot1.str} (d = ${beam.h - beam.cover}mm)`
        });
      }
    }

    // (4) Bottom Layer 2 Rebars
    if (st.bot2.count > 0) {
      const yBot2 = stirY + stirH - innerPad - rebarR - clearStepY;
      for (let bIdx = 0; bIdx < st.bot2.count; bIdx++) {
        const x = (st.bot2.count === 1) ? centerX : barXMin + (bIdx / (st.bot2.count - 1)) * barW;
        drawRebarDot(ctx, x, yBot2, rebarR * 0.9, false);

        interactiveElements.push({
          type: 'rebar_bot2',
          x: x,
          y: yBot2,
          r: rebarR + 4,
          title: `${meta.label} - 하부 2단 #${bIdx + 1}`,
          detail: `규격: D${st.bot2.dia} | 2단 배근: ${st.bot2.str} (순간격 25mm)`
        });
      }
    }

    // (5) Torsion Side Rebars
    if (beam.torsionSideCount > 0) {
      const numSideRows = Math.floor(beam.torsionSideCount / 2);
      const ySideTop = stirY + innerPad + rebarR + clearStepY + 10;
      const ySideBot = stirY + stirH - innerPad - rebarR - clearStepY - 10;
      const sideStep = (ySideBot - ySideTop) / Math.max(numSideRows, 1);

      for (let sIdx = 0; sIdx < numSideRows; sIdx++) {
        const sy = ySideTop + sIdx * sideStep;
        drawRebarDot(ctx, barXMin, sy, rebarR * 0.75, false);
        drawRebarDot(ctx, barXMax, sy, rebarR * 0.75, false);

        interactiveElements.push({
          type: 'torsion_side',
          x: barXMin,
          y: sy,
          r: rebarR + 3,
          title: `${meta.label} - 측면 비틀림 철근`,
          detail: `규격: D${beam.torsionSideBar.dia || 13} (피복 유지)`
        });
        interactiveElements.push({
          type: 'torsion_side',
          x: barXMax,
          y: sy,
          r: rebarR + 3,
          title: `${meta.label} - 측면 비틀림 철근`,
          detail: `규격: D${beam.torsionSideBar.dia || 13} (피복 유지)`
        });
      }
    }

    // -----------------------------------------------------------
    // E. Rebar Callout Tags & Leader Lines
    // -----------------------------------------------------------
    ctx.save();
    ctx.font = '11px "Inter", "Pretendard", sans-serif';
    ctx.fillStyle = pal.calloutTop;
    ctx.strokeStyle = pal.dimStroke;
    ctx.lineWidth = 1.0;

    // Top Tag
    const topTagText = st.top2.count > 0 ? `상부: ${st.top1.str} (2단:${st.top2.str})` : `상부: ${st.top1.str}`;
    const topTagY = secY0 - 10;
    ctx.textAlign = 'center';
    ctx.fillText(topTagText, centerX, topTagY);

    // Bottom Tag
    const botTagText = st.bot2.count > 0 ? `하부: ${st.bot1.str} (2단:${st.bot2.str})` : `하부: ${st.bot1.str}`;
    const botTagY = secY0 + drawH + 24;
    ctx.fillStyle = pal.calloutBot;
    ctx.fillText(botTagText, centerX, botTagY);

    // Stirrup Tag (Right side with badge)
    ctx.fillStyle = pal.stirrupBadge;
    ctx.textAlign = 'left';
    ctx.fillText(`늑근: ${st.stirrup.text} (${st.legs}L)`, secX0 + drawB + 10, centerY);
    ctx.restore();

    // -----------------------------------------------------------
    // F. CAD Dimension Lines
    // -----------------------------------------------------------
    if (showDimensions) {
      // Width b (at bottom below bottom tag)
      drawCADDimension(ctx, secX0, secY0 + drawH, secX0 + drawB, secY0 + drawH, `b = ${beam.b}`, 40, false);
      // Height h (at left)
      drawCADDimension(ctx, secX0, secY0, secX0, secY0 + drawH, `h = ${beam.h}`, -36, true);
      // T-Beam Flange Dimensions
      if (beam.shape === 'T_BEAM') {
        const drawBf = beam.bf * scale;
        const tfX0 = centerX - drawBf / 2;
        drawCADDimension(ctx, tfX0, secY0, tfX0 + drawBf, secY0, `bf = ${beam.bf}`, -24, false);
      }
    }

    return interactiveElements;
  };

  // ---------------------------------------------------------------------------
  // Global Export
  // ---------------------------------------------------------------------------
  global.VectorRCBeam = VectorRCBeam;

})(typeof window !== 'undefined' ? window : this);
