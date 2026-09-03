// web/js/visual/vector/vector_footing.js
/**
 * AltDP Vector Visual Engine - RC Isolated/Continuous Footing SVG Renderer
 * Renders Footing Plan (Punching shear d/2 perimeter), Elevation Section (Main bars, Dowels),
 * and Soil Pressure Distribution Diagram.
 * Shared by Graphic View (Pane 3) and A4 Report Generator (SSOT compliant).
 */

window.VectorFooting = {
    renderFootingSectionSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 460;
        const H = options.height || 180;
        const pad = 20;

        // Parameters extraction with fallbacks
        const Bx = Number(data.Bx || data.bx || data.lx || data.Lx || 2400);
        const By = Number(data.By || data.by || data.ly || data.Ly || 2400);
        const H_ftg = Number(data.H || data.h || data.D || data.thick || 600);
        const cx = Number(data.cx || data.col_b || data.col_x || 500);
        const cy = Number(data.cy || data.col_h || data.col_y || 500);
        const d = Number(data.d || (H_ftg - 80));

        let content = '';

        // ==========================================
        // 1. Plan View (Left Half: 0 ~ W/2 - 10)
        // ==========================================
        const planW = W / 2 - 15;
        const scalePlan = Math.min((planW - 2 * pad) / Bx, (H - 2 * pad) / By);
        const bxS = Bx * scalePlan, byS = By * scalePlan;
        const cxS = cx * scalePlan, cyS = cy * scalePlan;
        const ox1 = (planW - bxS) / 2 + 5, oy1 = (H - byS) / 2;

        // Footing slab plane
        content += C.rect(ox1, oy1, bxS, byS, P.concreteFill, P.concreteStroke, 1.5, 2);
        // Column stub
        content += C.rect(ox1 + (bxS - cxS) / 2, oy1 + (byS - cyS) / 2, cxS, cyS, isDark ? '#3f3f46' : '#d4d4d8', P.concreteStroke, 1.2);

        // Punching shear critical perimeter (d/2 offset dashed box)
        const punchX = Math.min(bxS, (cx + d) * scalePlan);
        const punchY = Math.min(byS, (cy + d) * scalePlan);
        content += `<rect x="${C.f1(ox1 + (bxS - punchX) / 2)}" y="${C.f1(oy1 + (byS - punchY) / 2)}" width="${C.f1(punchX)}" height="${C.f1(punchY)}" fill="none" stroke="${P.guideline}" stroke-width="1.2" stroke-dasharray="4,3"/>`;

        // Plan dimensions & label
        content += C.hDim(ox1, ox1 + bxS, Math.min(oy1 + byS + 14, H - 6), `Bx=${C.f0(Bx)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy1, oy1 + byS, Math.max(ox1 - 12, 8), `By=${C.f0(By)}`, P.dimText, 3, 8.5);
        content += C.text(ox1 + bxS / 2, oy1 + byS / 2 + 3, `${C.f0(cx)}×${C.f0(cy)}`, { fill: P.dimText, size: 7.5, bold: true });
        content += C.text(ox1 + bxS / 2, Math.max(10, oy1 - 6), '기초 평면도 (펀칭 위험단면)', { fill: P.dimLine, size: 8 });

        // ==========================================
        // 2. Elevation Section (Right Half: W/2 + 10 ~ W)
        // ==========================================
        const ox2 = W / 2 + 15;
        const elevW = W / 2 - 25;
        const scaleElev = Math.min((elevW - 20) / Bx, (H - 2 * pad - 20) / (H_ftg * 1.8));
        const bxS2 = Bx * scaleElev, hS2 = H_ftg * scaleElev;
        const cxS2 = cx * scaleElev;
        const oy2 = H / 2 + 25;

        // Footing concrete section
        content += C.rect(ox2 + (elevW - bxS2) / 2, oy2 - hS2, bxS2, hS2, P.concreteFill, P.concreteStroke, 1.5, 2);
        // Column stub elevation
        const colStartX = ox2 + (elevW - cxS2) / 2;
        content += C.rect(colStartX, oy2 - hS2 - 28, cxS2, 28, isDark ? '#3f3f46' : '#d4d4d8', P.concreteStroke, 1.2);

        // Bottom main rebar (Blue line)
        const barStartX = ox2 + (elevW - bxS2) / 2 + 6;
        const barEndX = barStartX + bxS2 - 12;
        content += C.line(barStartX, oy2 - 8, barEndX, oy2 - 8, P.rebarTie, 2.5);

        // Column Dowel bars (Red bent polyline)
        const dL = colStartX + 4;
        const dR = colStartX + cxS2 - 4;
        content += C.polyline([
            { x: dL, y: oy2 - hS2 - 32 },
            { x: dL, y: oy2 - 7 },
            { x: dL + 18, y: oy2 - 7 }
        ], 'none', P.rebarMain, 1.5);
        content += C.polyline([
            { x: dR, y: oy2 - hS2 - 32 },
            { x: dR, y: oy2 - 7 },
            { x: dR - 18, y: oy2 - 7 }
        ], 'none', P.rebarMain, 1.5);

        // Section dimensions & label
        content += C.hDim(barStartX - 6, barEndX + 6, oy2 + 14, `Bx=${C.f0(Bx)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy2 - hS2, oy2, ox2 + elevW + 6, `H=${C.f0(H_ftg)}`, P.dimText, 3, 8.5);
        content += C.text(ox2 + elevW / 2, oy2 - hS2 - 36, '다웰바 / 주철근 배근', { fill: P.rebarMain, size: 8 });
        content += C.text(ox2 + elevW / 2, oy1 - 5, '기초 입면 배근도', { fill: P.dimLine, size: 8 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    },

    renderFootingPlanSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);
        const W = options.width || 280, H = options.height || 220, pad = 24;

        const Bx = Number(data.Bx || data.bx || data.lx || data.Lx || 2400);
        const By = Number(data.By || data.by || data.ly || data.Ly || 2400);
        const H_ftg = Number(data.H || data.h || data.D || data.thick || 600);
        const cx = Number(data.cx || data.col_b || data.col_x || 500);
        const cy = Number(data.cy || data.col_h || data.col_y || 500);
        const d = Number(data.d || (H_ftg - 80));

        const scale = Math.min((W - 2 * pad) / Bx, (H - 2 * pad) / By);
        const bxS = Bx * scale, byS = By * scale, cxS = cx * scale, cyS = cy * scale;
        const ox = (W - bxS) / 2, oy = (H - byS) / 2;

        let content = '';
        content += C.rect(ox, oy, bxS, byS, P.concreteFill, P.concreteStroke, 1.5, 2);
        content += C.rect(ox + (bxS - cxS) / 2, oy + (byS - cyS) / 2, cxS, cyS, isDark ? '#3f3f46' : '#d4d4d8', P.concreteStroke, 1.2);

        const punchX = Math.min(bxS, (cx + d) * scale);
        const punchY = Math.min(byS, (cy + d) * scale);
        content += `<rect x="${C.f1(ox + (bxS - punchX) / 2)}" y="${C.f1(oy + (byS - punchY) / 2)}" width="${C.f1(punchX)}" height="${C.f1(punchY)}" fill="none" stroke="${P.guideline}" stroke-width="1.2" stroke-dasharray="4,3"/>`;

        content += C.hDim(ox, ox + bxS, H - 6, `Bx=${C.f0(Bx)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + byS, 8, `By=${C.f0(By)}`, P.dimText, 3, 8.5);
        content += C.text(ox + bxS / 2, oy + byS / 2 + 3, `${C.f0(cx)}×${C.f0(cy)}`, { fill: P.dimText, size: 7.5, bold: true });
        content += C.text(W / 2, oy - 6, '기초 평면도 (펀칭 위험단면)', { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    },

    renderFootingElevSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);
        const W = options.width || 280, H = options.height || 220, pad = 24;

        const Bx = Number(data.Bx || data.bx || data.lx || data.Lx || 2400);
        const H_ftg = Number(data.H || data.h || data.D || data.thick || 600);
        const cx = Number(data.cx || data.col_b || data.col_x || 500);

        const scale = Math.min((W - 2 * pad) / Bx, (H - 2 * pad) / (H_ftg * 1.8));
        const bxS = Bx * scale, hS = H_ftg * scale, cxS = cx * scale;
        const ox = (W - bxS) / 2, oy = H / 2 + 15;

        let content = '';
        content += C.rect(ox, oy - hS, bxS, hS, P.concreteFill, P.concreteStroke, 1.5, 2);
        const colStartX = ox + (bxS - cxS) / 2;
        content += C.rect(colStartX, oy - hS - 28, cxS, 28, isDark ? '#3f3f46' : '#d4d4d8', P.concreteStroke, 1.2);

        const barStartX = ox + 6, barEndX = ox + bxS - 6;
        content += C.line(barStartX, oy - 8, barEndX, oy - 8, P.rebarTie, 2.5);

        content += C.polyline([
            { x: colStartX + 4, y: oy - hS - 32 },
            { x: colStartX + 4, y: oy - 7 },
            { x: colStartX + 22, y: oy - 7 }
        ], 'none', P.rebarMain, 1.5);
        content += C.polyline([
            { x: colStartX + cxS - 4, y: oy - hS - 32 },
            { x: colStartX + cxS - 4, y: oy - 7 },
            { x: colStartX + cxS - 22, y: oy - 7 }
        ], 'none', P.rebarMain, 1.5);

        content += C.hDim(barStartX - 4, barEndX + 4, oy + 14, `Bx=${C.f0(Bx)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy - hS, oy, ox + bxS + 8, `H=${C.f0(H_ftg)}`, P.dimText, 3, 8.5);
        content += C.text(W / 2, oy - hS - 36, '기초 입면 배근도 (다웰바/주철근)', { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    },

    renderSoilPressureSVG(qmax = 180, qmin = 60, qa = 200, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 360;
        const H = options.height || 140;
        const pad = { left: 45, right: 35, top: 25, bottom: 35 };
        const pw = W - pad.left - pad.right;
        const ph = H - pad.top - pad.bottom;

        const maxQ = Math.max(Number(qmax || 0), Number(qa || 0), 10) * 1.15;
        const y0 = pad.top;
        const hMax = (Number(qmax || 0) / maxQ) * ph;
        const hMin = (Math.max(0, Number(qmin || 0)) / maxQ) * ph;
        const yMax = y0 + hMax;
        const yMin = y0 + hMin;
        const yQa = y0 + (Number(qa || 0) / maxQ) * ph;

        let content = '';

        // Footing base line
        content += C.line(pad.left - 5, y0, pad.left + pw + 5, y0, P.concreteStroke, 2.5);

        // Pressure trapezoid fill
        const trapPts = [
            { x: pad.left, y: y0 },
            { x: pad.left + pw, y: y0 },
            { x: pad.left + pw, y: yMin },
            { x: pad.left, y: yMax }
        ];
        content += `<polygon points="${trapPts.map(p => `${C.f1(p.x)},${C.f1(p.y)}`).join(' ')}" fill="${isDark ? 'rgba(59, 130, 246, 0.25)' : '#dbeafe'}" stroke="${P.steelFlange}" stroke-width="1.5"/>`;

        // Pressure arrows
        for (let i = 0; i <= 5; i++) {
            const x = pad.left + i * (pw / 5);
            const yB = yMax - (i / 5) * (yMax - yMin);
            content += C.line(x, y0 + 2, x, yB - 2, P.steelFlange, 1.0);
        }

        // Allowable bearing capacity Qa dashed line
        content += C.line(pad.left - 5, yQa, pad.left + pw + 5, yQa, P.guideline, 1.2, '4,3');
        content += C.text(pad.left + pw + 8, yQa + 3, `qa=${C.f0(qa)}`, { anchor: 'start', fill: P.guideline, size: 8.5 });

        // Qmax and Qmin labels
        content += C.text(pad.left - 4, yMax + 3, `qmax=${C.f1(qmax)}`, { anchor: 'end', fill: P.dimText, size: 8.5 });
        content += C.text(pad.left + pw + 4, yMin + 12, `qmin=${C.f1(qmin)}`, { anchor: 'start', fill: P.dimText, size: 8.5 });
        content += C.text(W / 2, H - 8, '지반 접지압 분포도 (kPa)', { fill: P.dimLine, size: 9 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    }
};
