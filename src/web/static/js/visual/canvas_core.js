// web/js/visual/canvas_core.js
/**
 * AltDP Visual Engine - Canvas Core Utility
 * - ResizeObserver responsive scaling
 * - 4-Unit System (SI, SI-M, MKS, US) dimension line & badge formatting
 * - Theme-aware styling (Dark / Light) & background grid
 */

window.CanvasCore = {
    resizeObserver: null,

    initObserver(canvasWrapId, onResize) {
        if (this.resizeObserver) return;
        const wrap = document.getElementById(canvasWrapId || 'canvas-wrap');
        if (wrap && window.ResizeObserver) {
            this.resizeObserver = new ResizeObserver(() => {
                if (typeof onResize === 'function') onResize();
            });
            this.resizeObserver.observe(wrap);
        }
    },

    fmtDim(canonicalVal, qtyType = 'length') {
        if (canonicalVal === undefined || canonicalVal === null || isNaN(canonicalVal)) return '';
        if (!window.UnitManager) return `${canonicalVal} mm`;
        const val = window.UnitManager.fromCanonical(canonicalVal, qtyType);
        const unit = window.UnitManager.getUnitString(qtyType);
        const sys = window.UnitManager.getCurrentSystem();
        const digits = sys.digits?.[qtyType] ?? 1;
        return `${Number(val.toFixed(digits))} ${unit}`;
    },

    drawDimH(ctx, x1, x2, y, text, isLight) {
        ctx.save();
        ctx.strokeStyle = isLight ? '#475569' : '#94a3b8';
        ctx.fillStyle = isLight ? '#1e293b' : '#f1f5f9';
        ctx.lineWidth = 1;
        ctx.font = '10px Consolas, monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';

        ctx.beginPath();
        ctx.moveTo(x1, y); ctx.lineTo(x2, y);
        ctx.moveTo(x1, y - 4); ctx.lineTo(x1, y + 4);
        ctx.moveTo(x2, y - 4); ctx.lineTo(x2, y + 4);
        ctx.stroke();

        const midX = (x1 + x2) / 2;
        ctx.fillText(text, midX, y - 2);
        ctx.restore();
    },

    drawDimV(ctx, x, y1, y2, text, isLight) {
        ctx.save();
        ctx.strokeStyle = isLight ? '#475569' : '#94a3b8';
        ctx.fillStyle = isLight ? '#1e293b' : '#f1f5f9';
        ctx.lineWidth = 1;
        ctx.font = '10px Consolas, monospace';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';

        ctx.beginPath();
        ctx.moveTo(x, y1); ctx.lineTo(x, y2);
        ctx.moveTo(x - 4, y1); ctx.lineTo(x + 4, y1);
        ctx.moveTo(x - 4, y2); ctx.lineTo(x + 4, y2);
        ctx.stroke();

        const midY = (y1 + y2) / 2;
        ctx.fillText(text, x - 4, midY);
        ctx.restore();
    },

    drawUnitBadge(ctx, W, H, isLight) {
        if (!window.UnitManager) return;
        const curSys = window.UnitManager.getCurrentSystem();
        ctx.save();
        ctx.font = 'bold 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'top';
        ctx.fillStyle = isLight ? 'rgba(30, 41, 59, 0.6)' : 'rgba(241, 245, 249, 0.6)';
        ctx.fillText(`Unit: ${curSys.name}`, W - 8, 8);
        ctx.restore();
    },

    drawGrid(ctx, W, H, isLight) {
        ctx.fillStyle = isLight ? '#ffffff' : '#1e222d';
        ctx.fillRect(0, 0, W, H);

        ctx.strokeStyle = isLight ? '#f1f5f9' : '#2a2e3d';
        ctx.lineWidth = 1;
        for (let x = 20; x < W; x += 20) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 20; y < H; y += 20) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }
    }
};
