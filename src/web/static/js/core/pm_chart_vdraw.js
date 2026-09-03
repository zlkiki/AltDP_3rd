/**
 * AltDP_3rd VDraw P-M Interaction Diagram Chart Renderer
 * Renders Pn-Mn nominal and phiPn-phiMn design curves with (Pu, Mu) operating points
 */
class PMChartVDraw {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    }

    render(data) {
        if (!this.canvas || !this.ctx) return;
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.clearRect(0, 0, w, h);

        // Extract curve points or provide standard demo curve
        const pn = data?.curvePn || [2500, 2400, 2000, 1400, 800, 0, -400];
        const mn = data?.curveMn || [0, 150, 320, 420, 400, 260, 0];
        const phiPn = data?.curvePhiPn || pn.map(p => p > 0 ? p * 0.65 : p * 0.85);
        const phiMn = data?.curvePhiMn || mn.map(m => m * 0.65);

        const pu = data?.pu ?? 850;
        const mu = data?.mu ?? 220;

        // Coordinate scaling
        const maxP = Math.max(...pn) * 1.15;
        const minP = Math.min(...pn, -100) * 1.15;
        const maxM = Math.max(...mn) * 1.25;

        const margin = { top: 30, right: 30, bottom: 40, left: 50 };
        const plotW = w - margin.left - margin.right;
        const plotH = h - margin.top - margin.bottom;

        const mapX = (m) => margin.left + (m / maxM) * plotW;
        const mapY = (p) => margin.top + ((maxP - p) / (maxP - minP)) * plotH;

        // 1. Grid and Axes
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        ctx.beginPath();
        // X-axis (P=0)
        const y0 = mapY(0);
        ctx.moveTo(margin.left, y0);
        ctx.lineTo(w - margin.right, y0);
        // Y-axis (M=0)
        ctx.moveTo(margin.left, margin.top);
        ctx.lineTo(margin.left, h - margin.bottom);
        ctx.stroke();

        // 2. Nominal curve (Pn-Mn) - Light dashed blue
        ctx.strokeStyle = '#60a5fa';
        ctx.setLineDash([4, 4]);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        for (let i = 0; i < pn.length; i++) {
            const x = mapX(mn[i]);
            const y = mapY(pn[i]);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // 3. Design curve (phiPn-phiMn) - Solid cyan
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        for (let i = 0; i < phiPn.length; i++) {
            const x = mapX(phiMn[i]);
            const y = mapY(phiPn[i]);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();

        // 4. Fill safe design zone
        ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
        ctx.lineTo(mapX(0), mapY(phiPn[phiPn.length - 1]));
        ctx.closePath();
        ctx.fill();

        // 5. Operating point (Pu, Mu)
        const ptX = mapX(mu);
        const ptY = mapY(pu);

        // Ray from origin
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(margin.left, y0);
        ctx.lineTo(ptX, ptY);
        ctx.stroke();

        // Point marker
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(ptX, ptY, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#f8fafc';
        ctx.font = '11px "Inter", sans-serif';
        ctx.fillText(`(Mu=${mu}, Pu=${pu})`, ptX + 8, ptY - 8);
    }
}

window.PMChartVDraw = PMChartVDraw;
