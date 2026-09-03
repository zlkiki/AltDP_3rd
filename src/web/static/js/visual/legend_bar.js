// web/js/visual/legend_bar.js
/**
 * AltDP Visual Engine - DCR Legend & Spectrum Bar Renderer
 * Reconstructed from extracted_src/renderer/legendCanvas.js
 */

window.LegendBar = {
    getDcrColor(dcr, isLight = false) {
        if (dcr === undefined || dcr === null || isNaN(dcr)) return isLight ? '#94a3b8' : '#64748b';
        if (dcr <= 0.7) return isLight ? '#2563eb' : '#3b82f6'; // Safe (Blue)
        if (dcr <= 1.0) return isLight ? '#059669' : '#10b981'; // OK (Green)
        if (dcr <= 1.1) return isLight ? '#d97706' : '#f59e0b'; // Warning (Amber)
        return isLight ? '#dc2626' : '#ef4444';                 // NG / Failure (Red)
    },

    getDcrVerdict(dcr) {
        if (dcr === undefined || dcr === null || isNaN(dcr)) return 'N/A';
        if (dcr <= 1.0) return 'OK (Safe)';
        if (dcr <= 1.1) return 'WARNING';
        return 'NG (Overstressed)';
    },

    drawDcrBadge(ctx, x, y, dcr, isLight) {
        if (dcr === undefined || dcr === null || isNaN(dcr)) return;
        const color = this.getDcrColor(dcr, isLight);
        const text = `DCR: ${dcr.toFixed(3)}`;

        ctx.save();
        ctx.font = 'bold 10px Consolas, monospace';
        const tw = ctx.measureText(text).width;
        const bw = tw + 14;
        const bh = 18;

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(x, y, bw, bh, 4) : ctx.rect(x, y, bw, bh);
        ctx.fill();

        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x + bw / 2, y + bh / 2 + 0.5);
        ctx.restore();
    },

    drawSpectrumBar(ctx, x, y, w, h, currentDcr, isLight) {
        ctx.save();
        const grad = ctx.createLinearGradient(x, y, x + w, y);
        grad.addColorStop(0.0, '#3b82f6'); // Blue <= 0.7
        grad.addColorStop(0.6, '#10b981'); // Green <= 1.0
        grad.addColorStop(0.8, '#f59e0b'); // Amber <= 1.1
        grad.addColorStop(1.0, '#ef4444'); // Red > 1.1

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(x, y, w, h, 3) : ctx.rect(x, y, w, h);
        ctx.fill();

        // Marker for current DCR
        if (currentDcr !== undefined && currentDcr !== null && !isNaN(currentDcr)) {
            const clamped = Math.max(0, Math.min(1.3, currentDcr));
            const markerX = x + (clamped / 1.3) * w;
            ctx.strokeStyle = isLight ? '#0f172a' : '#ffffff';
            ctx.fillStyle = isLight ? '#0f172a' : '#ffffff';
            ctx.lineWidth = 1.5;

            ctx.beginPath();
            ctx.moveTo(markerX, y - 2);
            ctx.lineTo(markerX, y + h + 2);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(markerX, y - 2);
            ctx.lineTo(markerX - 3, y - 5);
            ctx.lineTo(markerX + 3, y - 5);
            ctx.closePath();
            ctx.fill();
        }
        ctx.restore();
    }
};
