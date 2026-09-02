/**
 * src/web/static/js/stress_contour.js
 * ===================================
 * Pure Canvas 2D Real-time Stress & Moment Contour Map Renderer for AltDP_3rd FEM Engine.
 * 
 * Zero-dependency standalone visualization module.
 */

class StressContourRenderer {
    /**
     * @param {HTMLCanvasElement} canvas 
     */
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.nodes = [];         // [[x, y], ...]
        this.elements = [];      // [[n1, n2, n3, n4] or [n1, n2, n3], ...]
        this.values = [];        // [val_node0, val_node1, ...]
        this.showWireframe = true;
        this.colorScheme = 'jet'; // 'jet' or 'rainbow'
        this.unitLabel = 'kNm/m';
    }

    /**
     * Set mesh geometry and nodal field values.
     * @param {Array<Array<number>>} nodes N x 2 array
     * @param {Array<Array<number>>} elements M x 4 or M x 3 connectivity
     * @param {Array<number>} values N values corresponding to nodes
     * @param {string} unitLabel
     */
    setData(nodes, elements, values, unitLabel = 'kNm/m') {
        this.nodes = nodes || [];
        this.elements = elements || [];
        this.values = values || [];
        this.unitLabel = unitLabel;
        this.render();
    }

    /**
     * Get RGB color for normalized value t in [0, 1].
     */
    getColor(t) {
        const clamp = Math.max(0.0, Math.min(1.0, t));
        let r = 0, g = 0, b = 0;
        
        // Jet / Rainbow Colormap: Blue(0) -> Cyan(0.25) -> Green(0.5) -> Yellow(0.75) -> Red(1.0)
        if (clamp < 0.25) {
            const f = clamp / 0.25;
            r = 0;
            g = Math.floor(255 * f);
            b = 255;
        } else if (clamp < 0.5) {
            const f = (clamp - 0.25) / 0.25;
            r = 0;
            g = 255;
            b = Math.floor(255 * (1.0 - f));
        } else if (clamp < 0.75) {
            const f = (clamp - 0.5) / 0.25;
            r = Math.floor(255 * f);
            g = 255;
            b = 0;
        } else {
            const f = (clamp - 0.75) / 0.25;
            r = 255;
            g = Math.floor(255 * (1.0 - f));
            b = 0;
        }
        return `rgb(${r}, ${g}, ${b})`;
    }

    /**
     * Render the contour map and color legend.
     */
    render() {
        if (!this.ctx || this.nodes.length === 0) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        const ctx = this.ctx;
        
        ctx.clearRect(0, 0, width, height);
        
        // Find bounding box
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        this.nodes.forEach(pt => {
            if (pt[0] < minX) minX = pt[0];
            if (pt[0] > maxX) maxX = pt[0];
            if (pt[1] < minY) minY = pt[1];
            if (pt[1] > maxY) maxY = pt[1];
        });
        
        const spanX = Math.max(1e-4, maxX - minX);
        const spanY = Math.max(1e-4, maxY - minY);
        
        // Reserve right margin for legend bar
        const legendWidth = 60;
        const padding = 30;
        const drawW = width - legendWidth - padding * 2;
        const drawH = height - padding * 2;
        
        const scale = Math.min(drawW / spanX, drawH / spanY);
        const offsetX = padding + (drawW - spanX * scale) / 2;
        const offsetY = padding + (drawH - spanY * scale) / 2;
        
        const transformX = (x) => offsetX + (x - minX) * scale;
        const transformY = (y) => height - (offsetY + (y - minY) * scale); // Flip Y
        
        // Find min and max field values
        let minVal = Infinity, maxVal = -Infinity;
        this.values.forEach(v => {
            if (v < minVal) minVal = v;
            if (v > maxVal) maxVal = v;
        });
        if (minVal === maxVal) {
            maxVal += 1.0;
        }
        const valSpan = maxVal - minVal;

        // Render filled elements
        this.elements.forEach(elem => {
            ctx.beginPath();
            const p0 = this.nodes[elem[0]];
            ctx.moveTo(transformX(p0[0]), transformY(p0[1]));
            
            let avgVal = 0;
            elem.forEach(idx => {
                const pt = this.nodes[idx];
                ctx.lineTo(transformX(pt[0]), transformY(pt[1]));
                avgVal += (this.values[idx] !== undefined ? this.values[idx] : minVal);
            });
            avgVal /= elem.length;
            ctx.closePath();
            
            const norm = (avgVal - minVal) / valSpan;
            ctx.fillStyle = this.getColor(norm);
            ctx.fill();
            
            if (this.showWireframe) {
                ctx.strokeStyle = 'rgba(30, 41, 59, 0.4)';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        });

        // Render Color Legend Bar on right side
        this.renderLegend(width - legendWidth - 10, padding, 18, drawH, minVal, maxVal);
    }

    /**
     * Render the vertical color bar legend.
     */
    renderLegend(x, y, barW, barH, minVal, maxVal) {
        const ctx = this.ctx;
        const grad = ctx.createLinearGradient(0, y, 0, y + barH);
        grad.addColorStop(0.0, this.getColor(1.0));   // Max: Red (top)
        grad.addColorStop(0.25, this.getColor(0.75));
        grad.addColorStop(0.5, this.getColor(0.5));
        grad.addColorStop(0.75, this.getColor(0.25));
        grad.addColorStop(1.0, this.getColor(0.0));   // Min: Blue (bottom)
        
        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barW, barH);
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, barW, barH);
        
        // Text labels
        ctx.fillStyle = '#0f172a';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        
        ctx.fillText(`${maxVal.toFixed(2)}`, x + barW + 4, y + 10);
        ctx.fillText(`${((maxVal + minVal)/2).toFixed(2)}`, x + barW + 4, y + barH/2 + 4);
        ctx.fillText(`${minVal.toFixed(2)}`, x + barW + 4, y + barH);
        ctx.fillText(`(${this.unitLabel})`, x - 5, y - 8);
    }
}

// Export for ES module or browser window
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StressContourRenderer };
} else if (typeof window !== 'undefined') {
    window.StressContourRenderer = StressContourRenderer;
}
