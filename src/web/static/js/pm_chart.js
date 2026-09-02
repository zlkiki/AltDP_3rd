/**
 * PMChartRenderer: Interactive 2D/3D P-M Diagram Canvas Component for AltDP_3rd.
 * Visualizes Nominal & Design P-M curves, slenderness-magnified design force points,
 * and capacity envelopes according to KDS 14 20 20.
 */

class PMChartRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`PMChartRenderer: Canvas with id '${canvasId}' not found.`);
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.data = null;
        this.margin = { top: 40, right: 40, bottom: 50, left: 60 };
        this.initEvents();
    }

    initEvents() {
        if (!this.canvas) return;
        window.addEventListener('resize', () => {
            if (this.data) this.render(this.data);
        });
    }

    /**
     * Render the P-M Interaction Diagram.
     * @param {Object} data - { pm_curve: Array<{Pn, Mn, phi_Pn, phi_Mn}>, Pu, Mu, phi_Pn_max, phi_Pt }
     */
    render(data) {
        if (!this.canvas || !this.ctx || !data) return;
        this.data = data;

        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio || 600;
        this.canvas.height = rect.height * window.devicePixelRatio || 450;
        this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

        const w = rect.width;
        const h = rect.height;
        const ctx = this.ctx;

        ctx.clearRect(0, 0, w, h);

        const pts = data.pm_curve || [];
        if (pts.length === 0) return;

        // Calculate bounds
        let maxM = Math.max(...pts.map(p => Math.max(p.Mn || 0, p.phi_Mn || 0)), data.Mu || 0) * 1.15;
        let maxP = Math.max(...pts.map(p => Math.max(p.Pn || 0, p.phi_Pn || 0)), data.Pu || 0) * 1.10;
        let minP = Math.min(...pts.map(p => Math.min(p.Pn || 0, p.phi_Pn || 0, p.phi_Pt || 0)), data.Pu || 0) * 1.10;
        if (minP > 0) minP = -500;
        if (maxM <= 0) maxM = 500;

        const plotW = w - this.margin.left - this.margin.right;
        const plotH = h - this.margin.top - this.margin.bottom;

        const scaleX = (m) => this.margin.left + (m / maxM) * plotW;
        const scaleY = (p) => this.margin.top + ((maxP - p) / (maxP - minP)) * plotH;

        // 1. Grid & Axes
        ctx.strokeStyle = '#2d3748';
        ctx.lineWidth = 1;
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px sans-serif';

        // Horizontal Grid (P-levels)
        const pSteps = 6;
        for (let i = 0; i <= pSteps; i++) {
            const pVal = minP + (i / pSteps) * (maxP - minP);
            const y = scaleY(pVal);
            ctx.beginPath();
            ctx.moveTo(this.margin.left, y);
            ctx.lineTo(w - this.margin.right, y);
            ctx.stroke();
            ctx.fillText(`${Math.round(pVal)} kN`, 5, y + 4);
        }

        // Vertical Grid (M-levels)
        const mSteps = 5;
        for (let j = 0; j <= mSteps; j++) {
            const mVal = (j / mSteps) * maxM;
            const x = scaleX(mVal);
            ctx.beginPath();
            ctx.moveTo(x, this.margin.top);
            ctx.lineTo(x, h - this.margin.bottom);
            ctx.stroke();
            ctx.fillText(`${Math.round(mVal)} kNm`, x - 15, h - this.margin.bottom + 20);
        }

        // Zero-line for P=0
        const yZero = scaleY(0);
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(this.margin.left, yZero);
        ctx.lineTo(w - this.margin.right, yZero);
        ctx.stroke();

        // 2. Plot Nominal Curve (Pn - Mn) [Dashed Gray]
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 2;
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

        // 3. Plot Design Envelope (phi_Pn - phi_Mn) [Solid Blue / Cyan]
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 3;
        ctx.beginPath();
        pts.forEach((p, idx) => {
            const px = scaleX(p.phi_Mn || 0);
            const py = scaleY(p.phi_Pn || 0);
            if (idx === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });
        ctx.stroke();

        // Fill Design Region with Subtle Gradient
        ctx.lineTo(scaleX(0), scaleY(data.phi_Pt || pts[pts.length - 1].phi_Pn || 0));
        ctx.lineTo(scaleX(0), scaleY(data.phi_Pn_max || pts[0].phi_Pn || 0));
        ctx.closePath();
        ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
        ctx.fill();

        // 4. Plot Applied Design Load Point (Pu, Mu)
        if (data.Pu !== undefined && data.Mu !== undefined) {
            const loadX = scaleX(data.Mu);
            const loadY = scaleY(data.Pu);
            const isSafe = data.is_safe !== false;

            ctx.fillStyle = isSafe ? '#22c55e' : '#ef4444';
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(loadX, loadY, 6, 0, 2 * Math.PI);
            ctx.fill();
            ctx.stroke();

            // Label
            ctx.fillStyle = isSafe ? '#4ade80' : '#f87171';
            ctx.font = 'bold 12px sans-serif';
            ctx.fillText(`(Mu=${data.Mu.toFixed(1)}, Pu=${data.Pu.toFixed(0)}) [DCR=${(data.dcr || 0).toFixed(2)}]`, loadX + 10, loadY - 8);
        }

        // 5. Title & Legends
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 13px sans-serif';
        ctx.fillText('P-M Interaction Diagram (KDS 14 20 20)', this.margin.left, 24);

        // Legend markers
        ctx.font = '11px sans-serif';
        ctx.fillStyle = '#38bdf8';
        ctx.fillText('━ Design Capacity (φPn - φMn)', w - 220, 20);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('┅ Nominal (Pn - Mn)', w - 220, 35);
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.PMChartRenderer = PMChartRenderer;
}
