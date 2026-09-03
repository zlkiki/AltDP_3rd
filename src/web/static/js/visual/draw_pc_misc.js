// web/js/visual/draw_pc_misc.js
/**
 * AltDP Visual Engine - PC & Misc Domain Renderer (15 Modules)
 * PC Double-Tee, Inverse-T, Dapped-End, SRC Composite, Corbel/Bracket, Stair
 */

window.DrawPcMisc = {
    // 1. PC Double-Tee Slab
    drawPcDoubleTee(ctx, cx, cy, data, W, H, isLight) {
        const width = Number(data.width || data.b || data.B || 2400);
        const h = Number(data.stem_h || data.h || data.height || 600);
        const tf = Number(data.flange_t || data.tf || data.hf || 50);
        const bw = Number(data.stem_bw || data.bw || data.b_w || 150);

        const scale = Math.min((W * 0.70) / Math.max(width, 1), (H * 0.55) / Math.max(h, 1));
        const dw = width * scale, dh = h * scale, dtf = Math.max(tf * scale, 6), dbw = Math.max(bw * scale, 8);
        const x0 = cx - dw / 2, y0 = cy - dh / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3e50';
        ctx.strokeStyle = isLight ? '#64748b' : '#95a5a6';
        ctx.lineWidth = 2;

        // Flange + 2 Tapered Stems
        ctx.beginPath();
        ctx.moveTo(x0, y0); ctx.lineTo(x0 + dw, y0); ctx.lineTo(x0 + dw, y0 + dtf);
        // Right Stem
        const s2x = x0 + dw * 0.75;
        ctx.lineTo(s2x + dbw / 2, y0 + dtf); ctx.lineTo(s2x + dbw / 3, y0 + dh);
        ctx.lineTo(s2x - dbw / 3, y0 + dh); ctx.lineTo(s2x - dbw / 2, y0 + dtf);
        // Left Stem
        const s1x = x0 + dw * 0.25;
        ctx.lineTo(s1x + dbw / 2, y0 + dtf); ctx.lineTo(s1x + dbw / 3, y0 + dh);
        ctx.lineTo(s1x - dbw / 3, y0 + dh); ctx.lineTo(s1x - dbw / 2, y0 + dtf);
        ctx.lineTo(x0, y0 + dtf); ctx.closePath();
        ctx.fill(); ctx.stroke();

        // Tendon Strands (Red dots at stem bottoms)
        ctx.fillStyle = '#ef4444';
        ctx.beginPath(); ctx.arc(s1x, y0 + dh - 6, 3, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(s2x, y0 + dh - 6, 3, 0, Math.PI * 2); ctx.fill();

        window.CanvasCore.drawDimH(ctx, x0, x0 + dw, y0 + dh + 18, `W = ${window.CanvasCore.fmtDim(width, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dh, `H = ${window.CanvasCore.fmtDim(h, 'length')}`, isLight);
    },

    // 2. Corbel / Bracket (사다리꼴 경사면)
    drawBracketCorbel(ctx, cx, cy, data, W, H, isLight) {
        const b = Number(data.b || data.width || 400);
        const h = Number(data.h || data.height || 600);
        const h1 = Number(data.h1 || data.h_dap || 300);
        const a = Number(data.a || data.dist_a || data.av || 250);

        const scale = Math.min((W * 0.60) / Math.max(a + 200, 1), (H * 0.60) / Math.max(h, 1));
        const dh = h * scale, dh1 = h1 * scale, da = a * scale;
        const x0 = cx - (da + 100 * scale) / 2, y0 = cy - dh / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3345';
        ctx.strokeStyle = isLight ? '#64748b' : '#4e5d78';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(x0, y0); ctx.lineTo(x0 + da + 60 * scale, y0);
        ctx.lineTo(x0 + da + 60 * scale, y0 + dh1);
        ctx.lineTo(x0, y0 + dh); ctx.closePath();
        ctx.fill(); ctx.stroke();

        // Top Main Tension Bar (Red)
        ctx.strokeStyle = '#ef4444'; ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.moveTo(x0 + 10, y0 + 10); ctx.lineTo(x0 + da + 40 * scale, y0 + 10); ctx.stroke();

        // Load Arrow (Down)
        const lx = x0 + da;
        ctx.strokeStyle = '#f59e0b'; ctx.fillStyle = '#f59e0b'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(lx, y0 - 24); ctx.lineTo(lx, y0); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(lx, y0); ctx.lineTo(lx - 4, y0 - 8); ctx.lineTo(lx + 4, y0 - 8); ctx.closePath(); ctx.fill();

        window.CanvasCore.drawDimH(ctx, x0, lx, y0 - 12, `a = ${window.CanvasCore.fmtDim(a, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dh, `h = ${window.CanvasCore.fmtDim(h, 'length')}`, isLight);
    },

    // 3. SRC Composite Section (매립형 H형강 + RC 콘크리트)
    drawSrcSection(ctx, cx, cy, data, W, H, isLight) {
        // Outer RC Rect
        window.DrawRc.drawRcRect(ctx, cx, cy, data, W, H, isLight);
        // Inner Steel H
        const stH = Number(data.col_d || data.steel_h || data.steel_d || 250);
        const stB = Number(data.col_bf || data.steel_b || data.steel_bf || 250);
        window.DrawSteel.drawSteelH(ctx, cx, cy, { 
            h: stH, 
            b: stB, 
            tw: data.steel_tw || 8, 
            tf: data.steel_tf || 12,
            section_name: data.steel_sec || data.steel_section || ''
        }, W, H, isLight);
    }
};
