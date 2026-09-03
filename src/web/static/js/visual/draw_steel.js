// web/js/visual/draw_steel.js
/**
 * AltDP Visual Engine - Steel Domain Renderer (13 Modules)
 * H-Section, Box/Pipe, Baseplate, Bolt Connections, Composite Beams
 */

window.DrawSteel = {
    drawSteelH(ctx, cx, cy, data, W, H, isLight) {
        let h = Number(data.h || data.d || data.H || data.height || 400);
        let b = Number(data.b || data.bf || data.B || data.width || 200);
        let tw = Number(data.tw || data.t || data.web_t || 8);
        let tf = Number(data.tf || data.tp || data.flange_t || 13);

        const secName = data.section_name || data.sec_name || data.girder_sec || data.beam_sec || data.col_sec || '';

        // Auto parse if section_name like H-400x200x8x13
        if (secName && typeof secName === 'string') {
            const m = secName.match(/(\d+)\s*[xX×]\s*(\d+)\s*[xX×]\s*([\d\.]+)\s*[xX×]\s*([\d\.]+)/);
            if (m) {
                h = Number(m[1]) || h;
                b = Number(m[2]) || b;
                tw = Number(m[3]) || tw;
                tf = Number(m[4]) || tf;
            }
        }

        const scale = Math.min((W * 0.60) / Math.max(b, 1), (H * 0.60) / Math.max(h, 1));
        const dh = h * scale, db = b * scale;
        const dtw = Math.max(tw * scale, 3), dtf = Math.max(tf * scale, 4);
        const x0 = cx - db / 2, y0 = cy - dh / 2;

        ctx.fillStyle = isLight ? '#93c5fd' : '#3498db';
        ctx.strokeStyle = isLight ? '#2563eb' : '#5dade2';
        ctx.lineWidth = 2;

        // Flanges & Web
        ctx.fillRect(x0, y0, db, dtf); ctx.strokeRect(x0, y0, db, dtf);
        ctx.fillRect(x0, y0 + dh - dtf, db, dtf); ctx.strokeRect(x0, y0 + dh - dtf, db, dtf);
        ctx.fillRect(cx - dtw / 2, y0 + dtf, dtw, Math.max(0, dh - 2 * dtf));
        ctx.strokeRect(cx - dtw / 2, y0 + dtf, dtw, Math.max(0, dh - 2 * dtf));

        // Dimension lines & Spec Title
        ctx.font = '600 10px Consolas, monospace';
        ctx.fillStyle = isLight ? '#1d4ed8' : '#60a5fa'; ctx.textAlign = 'center';
        const label = secName || `H-${h}×${b}×${tw}×${tf}`;
        ctx.fillText(label, cx, y0 - 6);

        window.CanvasCore.drawDimH(ctx, x0, x0 + db, y0 + dh + 18, `B = ${window.CanvasCore.fmtDim(b, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dh, `H = ${window.CanvasCore.fmtDim(h, 'length')}`, isLight);
    },

    drawSteelBoxPipe(ctx, cx, cy, data, W, H, isLight) {
        const B = Number(data.B || data.b || data.width || 400);
        const H_val = Number(data.H || data.h || data.height || 400);
        const t = Number(data.t || data.t_steel || data.tw || 12);
        const scale = Math.min((W * 0.60) / Math.max(B, 1), (H * 0.60) / Math.max(H_val, 1));
        const dB = B * scale, dH = H_val * scale, dt = Math.max(t * scale, 4);
        const x0 = cx - dB / 2, y0 = cy - dH / 2;

        ctx.fillStyle = isLight ? '#93c5fd' : '#34495e';
        ctx.strokeStyle = isLight ? '#2563eb' : '#5dade2';
        ctx.lineWidth = 2;
        ctx.fillRect(x0, y0, dB, dH); ctx.strokeRect(x0, y0, dB, dH);

        // Inner Hole
        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3345';
        ctx.fillRect(x0 + dt, y0 + dt, Math.max(0, dB - 2 * dt), Math.max(0, dH - 2 * dt));
        ctx.strokeRect(x0 + dt, y0 + dt, Math.max(0, dB - 2 * dt), Math.max(0, dH - 2 * dt));

        window.CanvasCore.drawDimH(ctx, x0, x0 + dB, y0 + dH + 18, `B = ${window.CanvasCore.fmtDim(B, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dH, `H = ${window.CanvasCore.fmtDim(H_val, 'length')}`, isLight);
    },

    drawSteelBaseplate(ctx, cx, cy, data, W, H, isLight) {
        const B = Number(data.B || data.b || data.width || 500);
        const N = Number(data.N || data.h || data.height || data.L || 500);
        const tp = Number(data.tp || data.t || data.thk || 25);
        const scale = Math.min((W * 0.60) / Math.max(B, 1), (H * 0.60) / Math.max(N, 1));
        const dB = B * scale, dN = N * scale;
        const x0 = cx - dB / 2, y0 = cy - dN / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#34495e';
        ctx.strokeStyle = isLight ? '#64748b' : '#bdc3c7';
        ctx.lineWidth = 2;
        ctx.fillRect(x0, y0, dB, dN); ctx.strokeRect(x0, y0, dB, dN);

        // 4 Anchor Bolts
        ctx.fillStyle = '#f59e0b';
        const offX = dB * 0.35, offY = dN * 0.35;
        [[-offX, -offY], [offX, -offY], [-offX, offY], [offX, offY]].forEach(([dx, dy]) => {
            ctx.beginPath(); ctx.arc(cx + dx, cy + dy, Math.max(3, 4.5 * (W / 360)), 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        });

        // Center H-Column
        const colH = Number(data.col_d || data.col_h || data.beam_d || 300);
        const colB = Number(data.col_bf || data.col_b || data.beam_bf || 300);
        this.drawSteelH(ctx, cx, cy, { h: colH, b: colB, tw: 10, tf: 15 }, W, H, isLight);

        ctx.font = '600 9.5px Consolas, monospace';
        ctx.fillStyle = isLight ? '#1d4ed8' : '#60a5fa'; ctx.textAlign = 'center';
        ctx.fillText(`PL-${tp}t × ${B} × ${N}`, cx, y0 - 6);

        window.CanvasCore.drawDimH(ctx, x0, x0 + dB, y0 + dN + 18, `B = ${window.CanvasCore.fmtDim(B, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dN, `N = ${window.CanvasCore.fmtDim(N, 'length')}`, isLight);
    }
};
