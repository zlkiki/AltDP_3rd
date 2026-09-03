// web/js/visual/draw_rc.js
/**
 * AltDP Visual Engine - RC Concrete Domain Renderer (26 Modules)
 * Reconstructed from extracted_src/renderer/drawSection.js & footingCore.js
 * Supports 2-layer beam rebar (25mm clearance), Column cross-ties, Wall boundary zones, Footing pile grids
 */

window.DrawRc = {
    // 1. RC Rectangular Beam & Column & Wall
    drawRcRect(ctx, cx, cy, data, W, H, isLight) {
        const b = Number(data.b || data.col_b || data.bw || data.tw || data.b_w || 400);
        const h = Number(data.h || data.col_h || data.Lw || data.hw || data.height || 600);
        const maxAvailW = Math.max(80, W * 0.58), maxAvailH = Math.max(80, H * 0.58);
        const scale = Math.min(maxAvailW / Math.max(b, 1), maxAvailH / Math.max(h, 1));
        const dw = b * scale, dh = h * scale;
        const x0 = cx - dw / 2, y0 = cy - dh / 2;

        // Concrete body
        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3345';
        ctx.strokeStyle = isLight ? '#64748b' : '#4e5d78';
        ctx.lineWidth = 2;
        ctx.fillRect(x0, y0, dw, dh);
        ctx.strokeRect(x0, y0, dw, dh);

        // Stirrup / Tie (회색 점선)
        const cover = Number(data.cover || data.cc || data.c_c || 40) * scale;
        const stirDia = Number(data.stirrup_dia || data.tie_dia || data.stir_dia || 10);
        ctx.save();
        ctx.strokeStyle = isLight ? '#64748b' : '#94a3b8';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 3]);
        ctx.strokeRect(x0 + cover, y0 + cover, Math.max(0, dw - 2 * cover), Math.max(0, dh - 2 * cover));
        ctx.restore();

        const r_dot = Math.max(3, Math.min(6, 4.5 * (W / 360)));
        const offsetInner = cover + Math.max(stirDia * scale, 2) + r_dot;
        const innerW = Math.max(0, dw - 2 * offsetInner);

        // Check if Column 둘레 배치 (nB x nH)
        const nB = Number(data.nB || data.nb || data.nx || 0);
        const nH = Number(data.nH || data.nh || data.ny || 0);

        if (nB > 0 && nH > 0) {
            // Column 둘레 배근 & Cross-tie
            this.drawColumnBarsAndTies(ctx, x0, y0, dw, dh, offsetInner, nB, nH, r_dot, stirDia, scale, isLight);
        } else {
            // Beam 1단/2단 배근 (top1, top2, bot1, bot2)
            this.drawBeamBars(ctx, x0, y0, dw, dh, innerW, offsetInner, r_dot, data, scale, isLight);
        }

        // Dimension lines
        window.CanvasCore.drawDimH(ctx, x0, x0 + dw, y0 + dh + 34, `b = ${window.CanvasCore.fmtDim(b, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dh, `h = ${window.CanvasCore.fmtDim(h, 'length')}`, isLight);
    },

    drawBeamBars(ctx, x0, y0, dw, dh, innerW, offsetInner, r_dot, data, scale, isLight) {
        const top1 = Number(data.top_num || data.n_top || data.n_top1 || data.top_bar_num || 3);
        const top2 = Number(data.top_num2 || data.n_top2 || 0);
        const bot1 = Number(data.bot_num || data.n_bot || data.n_bot1 || data.bot_bar_num || 3);
        const bot2 = Number(data.bot_num2 || data.n_bot2 || 0);
        
        let topDia = String(data.top_dia || data.rebar_dia || data.D_bar || 22).replace(/^D/i, '');
        let botDia = String(data.bot_dia || data.rebar_dia || data.D_bar || 22).replace(/^D/i, '');
        const clearRow = Math.max(25 * scale, r_dot * 2.2);

        // Top 1 & 2
        ctx.fillStyle = isLight ? '#b91c1c' : '#ef4444';
        for (let i = 0; i < top1; i++) {
            const rx = x0 + offsetInner + (top1 > 1 ? innerW * (i / (top1 - 1)) : innerW / 2);
            ctx.beginPath(); ctx.arc(rx, y0 + offsetInner, r_dot, 0, Math.PI * 2); ctx.fill();
        }
        if (top2 > 0) {
            for (let i = 0; i < top2; i++) {
                const rx = x0 + offsetInner + (top2 > 1 ? innerW * (i / (top2 - 1)) : innerW / 2);
                ctx.beginPath(); ctx.arc(rx, y0 + offsetInner + clearRow, r_dot, 0, Math.PI * 2); ctx.fill();
            }
        }

        // Bot 1 & 2
        ctx.fillStyle = isLight ? '#1d4ed8' : '#3b82f6';
        for (let i = 0; i < bot1; i++) {
            const rx = x0 + offsetInner + (bot1 > 1 ? innerW * (i / (bot1 - 1)) : innerW / 2);
            ctx.beginPath(); ctx.arc(rx, y0 + dh - offsetInner, r_dot, 0, Math.PI * 2); ctx.fill();
        }
        if (bot2 > 0) {
            for (let i = 0; i < bot2; i++) {
                const rx = x0 + offsetInner + (bot2 > 1 ? innerW * (i / (bot2 - 1)) : innerW / 2);
                ctx.beginPath(); ctx.arc(rx, y0 + dh - offsetInner - clearRow, r_dot, 0, Math.PI * 2); ctx.fill();
            }
        }

        // Side skin bars
        const numSide = Number(data.side_num || data.n_side || data.skin_bar_num || 0);
        if (numSide > 0) {
            ctx.fillStyle = isLight ? '#059669' : '#10b981';
            const sideStep = (dh - 2 * offsetInner) / (numSide + 1);
            for (let i = 1; i <= numSide; i++) {
                const ry = y0 + offsetInner + i * sideStep;
                ctx.beginPath(); ctx.arc(x0 + offsetInner, ry, r_dot * 0.8, 0, Math.PI * 2); ctx.fill();
                ctx.beginPath(); ctx.arc(x0 + dw - offsetInner, ry, r_dot * 0.8, 0, Math.PI * 2); ctx.fill();
            }
        }

        // Rebar Specs Text
        ctx.font = '600 9.5px Consolas, monospace';
        ctx.fillStyle = isLight ? '#b91c1c' : '#f87171'; ctx.textAlign = 'center';
        ctx.fillText(`Top: ${top1 + top2}-D${topDia}`, x0 + dw / 2, y0 - 6);
        ctx.fillStyle = isLight ? '#1d4ed8' : '#60a5fa';
        ctx.fillText(`Bot: ${bot1 + bot2}-D${botDia}`, x0 + dw / 2, y0 + dh + 14);
    },

    drawColumnBarsAndTies(ctx, x0, y0, dw, dh, offsetInner, nB, nH, r_dot, stirDia, scale, isLight) {
        const inW = dw - 2 * offsetInner, inH = dh - 2 * offsetInner;
        ctx.fillStyle = isLight ? '#b91c1c' : '#ef4444';

        // Top & Bottom rows
        for (let i = 0; i < nB; i++) {
            const rx = x0 + offsetInner + inW * (i / (nB - 1 || 1));
            ctx.beginPath(); ctx.arc(rx, y0 + offsetInner, r_dot, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(rx, y0 + dh - offsetInner, r_dot, 0, Math.PI * 2); ctx.fill();
        }
        // Left & Right columns
        for (let j = 1; j < nH - 1; j++) {
            const ry = y0 + offsetInner + inH * (j / (nH - 1 || 1));
            ctx.beginPath(); ctx.arc(x0 + offsetInner, ry, r_dot, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(x0 + dw - offsetInner, ry, r_dot, 0, Math.PI * 2); ctx.fill();
        }

        // Cross-ties (보조대근 선)
        ctx.save();
        ctx.strokeStyle = isLight ? 'rgba(71, 85, 105, 0.6)' : 'rgba(148, 163, 184, 0.6)';
        ctx.lineWidth = 1;
        if (nB > 2) {
            for (let i = 1; i < nB - 1; i += 2) {
                const rx = x0 + offsetInner + inW * (i / (nB - 1));
                ctx.beginPath(); ctx.moveTo(rx, y0 + offsetInner); ctx.lineTo(rx, y0 + dh - offsetInner); ctx.stroke();
            }
        }
        if (nH > 2) {
            for (let j = 1; j < nH - 1; j += 2) {
                const ry = y0 + offsetInner + inH * (j / (nH - 1));
                ctx.beginPath(); ctx.moveTo(x0 + offsetInner, ry); ctx.lineTo(x0 + dw - offsetInner, ry); ctx.stroke();
            }
        }
        ctx.restore();
    },

    // 2. RC T-Section
    drawRcTSect(ctx, cx, cy, data, W, H, isLight) {
        const b = Number(data.b || data.bf || data.b_top || data.b_f || 600), h = Number(data.h || data.height || 800);
        const bw = Number(data.bw || data.b_w || data.stem_bw || 300), hf = Number(data.hf || data.h_f || data.flange_t || 150);
        const maxAvailW = Math.max(80, W * 0.60), maxAvailH = Math.max(80, H * 0.60);
        const scale = Math.min(maxAvailW / Math.max(b, 1), maxAvailH / Math.max(h, 1));
        const db = b * scale, dh = h * scale, dbw = bw * scale, dhf = hf * scale;
        const x0 = cx - db / 2, y0 = cy - dh / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3345';
        ctx.strokeStyle = isLight ? '#64748b' : '#4e5d78';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x0, y0); ctx.lineTo(x0 + db, y0); ctx.lineTo(x0 + db, y0 + dhf);
        ctx.lineTo(cx + dbw / 2, y0 + dhf); ctx.lineTo(cx + dbw / 2, y0 + dh);
        ctx.lineTo(cx - dbw / 2, y0 + dh); ctx.lineTo(cx - dbw / 2, y0 + dhf);
        ctx.lineTo(x0, y0 + dhf); ctx.closePath();
        ctx.fill(); ctx.stroke();

        window.CanvasCore.drawDimH(ctx, x0, x0 + db, y0 + dh + 18, `bf = ${window.CanvasCore.fmtDim(b, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dh, `h = ${window.CanvasCore.fmtDim(h, 'length')}`, isLight);
    },

    // 3. RC Footing & Pile Cap
    drawRcFooting(ctx, cx, cy, data, W, H, isLight) {
        const B = Number(data.B || data.b || data.Lx || 2500), L = Number(data.L || data.l || data.Ly || 2500);
        const cx_col = Number(data.cx || data.col_b || data.col_d || data.cx_col || 500);
        const cy_col = Number(data.cy || data.col_h || data.col_bf || data.cy_col || 500);
        const scale = Math.min((W * 0.58) / Math.max(B, 1), (H * 0.58) / Math.max(L, 1));
        const dB = B * scale, dL = L * scale, dcx = cx_col * scale, dcy = cy_col * scale;
        const x0 = cx - dB / 2, y0 = cy - dL / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#2c3e50';
        ctx.strokeStyle = isLight ? '#64748b' : '#7f8c8d';
        ctx.lineWidth = 2;
        ctx.fillRect(x0, y0, dB, dL); ctx.strokeRect(x0, y0, dB, dL);

        // Center Column Pedestal
        ctx.fillStyle = isLight ? '#fdba74' : '#e67e22';
        ctx.fillRect(cx - dcx / 2, cy - dcy / 2, dcx, dcy);
        ctx.strokeRect(cx - dcx / 2, cy - dcy / 2, dcx, dcy);

        // Pile Grid (if pile_cap module)
        const pileN = Number(data.pile_ea || data.pile_n || data.pile_count || 0);
        if (pileN > 0) {
            ctx.fillStyle = isLight ? '#3b82f6' : '#60a5fa';
            const pr = Math.max(4, 8 * scale * 50);
            const pOffX = dB * 0.3, pOffY = dL * 0.3;
            [[-pOffX, -pOffY], [pOffX, -pOffY], [-pOffX, pOffY], [pOffX, pOffY]].slice(0, Math.min(4, pileN)).forEach(([dx, dy]) => {
                ctx.beginPath(); ctx.arc(cx + dx, cy + dy, pr, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
            });
        }

        window.CanvasCore.drawDimH(ctx, x0, x0 + dB, y0 + dL + 18, `B = ${window.CanvasCore.fmtDim(B, 'length')}`, isLight);
        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + dL, `L = ${window.CanvasCore.fmtDim(L, 'length')}`, isLight);
    },

    // 4. RC Slab
    drawRcSlab(ctx, cx, cy, data, W, H, isLight) {
        const t = Number(data.thickness || data.thk || data.t || data.slab_t || data.tc || 200);
        const slabW = Math.max(100, W * 0.68), slabH = Math.max(30, Math.min(H * 0.55, t * 0.4));
        const x0 = cx - slabW / 2, y0 = cy - slabH / 2;

        ctx.fillStyle = isLight ? '#e2e8f0' : '#34495e';
        ctx.strokeStyle = isLight ? '#64748b' : '#95a5a6';
        ctx.lineWidth = 2;
        ctx.fillRect(x0, y0, slabW, slabH); ctx.strokeRect(x0, y0, slabW, slabH);

        // Bottom Rebars
        ctx.fillStyle = isLight ? '#dc2626' : '#e74c3c';
        const step = Math.max(18, slabW / 8);
        for (let x = x0 + step / 2; x < x0 + slabW; x += step) {
            ctx.beginPath(); ctx.arc(x, y0 + slabH - 8, 3.5, 0, Math.PI * 2); ctx.fill();
        }

        window.CanvasCore.drawDimV(ctx, x0 - 12, y0, y0 + slabH, `t = ${window.CanvasCore.fmtDim(t, 'length')}`, isLight);
    }
};
