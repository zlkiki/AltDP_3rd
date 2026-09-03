// web/js/visual/vector/vector_core.js
/**
 * AltDP Vector Visual Engine - Core SVG Generation Helper & Utilities
 * Provides theme-aware palette, dimension lines, rebar dots/lines, and responsive SVG wrapping.
 * Zero-Build & Token-Optimized Vanilla JS (SSOT compliant)
 */

window.VectorCore = {
    // Theme Palette Resolver
    getPalette(isDark = false) {
        if (isDark) {
            return {
                bg: '#18181b',
                concreteFill: '#27272a',
                concreteStroke: '#71717a',
                rebarMain: '#f87171',
                rebarTie: '#60a5fa',
                rebarSec: '#fbbf24',
                steelFlange: '#3b82f6',
                steelWeb: '#60a5fa',
                steelStroke: '#93c5fd',
                dimLine: '#a1a1aa',
                dimText: '#e4e4e7',
                guideline: '#ef4444',
                gridLine: 'rgba(255, 255, 255, 0.05)',
                badgeBg: 'rgba(39, 39, 42, 0.8)',
                badgeText: '#f4f4f5'
            };
        }
        return {
            bg: '#fafafa',
            concreteFill: '#f4f4f5',
            concreteStroke: '#3f3f46',
            rebarMain: '#dc2626',
            rebarTie: '#2563eb',
            rebarSec: '#d97706',
            steelFlange: '#3b82f6',
            steelWeb: '#60a5fa',
            steelStroke: '#1e3a8a',
            dimLine: '#71717a',
            dimText: '#27272a',
            guideline: '#dc2626',
            gridLine: 'rgba(0, 0, 0, 0.04)',
            badgeBg: 'rgba(244, 244, 245, 0.9)',
            badgeText: '#18181b'
        };
    },

    f0(n) { return Number(n || 0).toFixed(0); },
    f1(n) { return Number(n || 0).toFixed(1); },
    f2(n) { return Number(n || 0).toFixed(2); },

    // Root SVG Tag Wrapper with responsive viewBox
    createSvgRoot(w, h, content, opts = {}) {
        const bg = opts.bg || (opts.isDark ? '#18181b' : '#fafafa');
        const border = opts.border !== false ? `border: 1px solid ${opts.isDark ? '#3f3f46' : '#e4e4e7'}; border-radius: 6px;` : '';
        const style = `background: ${bg}; ${border} display: block; max-width: 100%; height: auto; margin: 0 auto; ${opts.style || ''}`;
        return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="${style}">${content}</svg>`;
    },

    // Rectangle
    rect(x, y, w, h, fill, stroke, strokeWidth = 1.5, rx = 0) {
        return `<rect x="${this.f1(x)}" y="${this.f1(y)}" width="${this.f1(w)}" height="${this.f1(h)}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" rx="${rx}"/>`;
    },

    // Circle (Rebar dot)
    circle(cx, cy, r, fill, stroke = 'none', strokeWidth = 0.5) {
        return `<circle cx="${this.f1(cx)}" cy="${this.f1(cy)}" r="${this.f1(r)}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}"/>`;
    },

    // Line
    line(x1, y1, x2, y2, stroke, strokeWidth = 1.5, dash = '') {
        const dashAttr = dash ? `stroke-dasharray="${dash}"` : '';
        return `<line x1="${this.f1(x1)}" y1="${this.f1(y1)}" x2="${this.f1(x2)}" y2="${this.f1(y2)}" stroke="${stroke}" stroke-width="${strokeWidth}" ${dashAttr}/>`;
    },

    // Polyline
    polyline(points, fill = 'none', stroke = '#dc2626', strokeWidth = 1.5) {
        const pts = Array.isArray(points) ? points.map(p => `${this.f1(p.x || p[0])},${this.f1(p.y || p[1])}`).join(' ') : points;
        return `<polyline points="${pts}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}"/>`;
    },

    // Polygon (Custom closed shapes: L/T/Cross columns, T-beam/slab, etc.)
    polygon(points, fill = '#27272a', stroke = '#71717a', strokeWidth = 1.5, strokeJoin = 'round') {
        const pts = Array.isArray(points) ? points.map(p => `${this.f1(p.x || p[0])},${this.f1(p.y || p[1])}`).join(' ') : points;
        return `<polygon points="${pts}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" stroke-linejoin="${strokeJoin}"/>`;
    },

    // Text Label
    text(x, y, str, opts = {}) {
        const anchor = opts.anchor || 'middle';
        const size = opts.size || 10;
        const fill = opts.fill || '#333';
        const rot = opts.rot ? `transform="rotate(${opts.rot}, ${this.f1(x)}, ${this.f1(y)})"` : '';
        const weight = opts.bold ? 'font-weight="bold"' : '';
        return `<text x="${this.f1(x)}" y="${this.f1(y)}" text-anchor="${anchor}" font-size="${size}" font-family="Consolas, 'Segoe UI', Arial, sans-serif" fill="${fill}" ${weight} ${rot}>${str}</text>`;
    },

    // Horizontal Dimension Line
    hDim(x1, x2, y, valText, color = '#555', tick = 4, txtSize = 9) {
        let svg = this.line(x1, y, x2, y, color, 1.2);
        svg += this.line(x1, y - tick, x1, y + tick, color, 1.2);
        svg += this.line(x2, y - tick, x2, y + tick, color, 1.2);
        svg += this.text((x1 + x2) / 2, y - 4, valText, { fill: color, size: txtSize });
        return svg;
    },

    // Vertical Dimension Line
    vDim(y1, y2, x, valText, color = '#555', tick = 4, txtSize = 9) {
        let svg = this.line(x, y1, x, y2, color, 1.2);
        svg += this.line(x - tick, y1, x + tick, y1, color, 1.2);
        svg += this.line(x - tick, y2, x + tick, y2, color, 1.2);
        svg += this.text(x - 5, (y1 + y2) / 2, valText, { fill: color, size: txtSize, rot: -90 });
        return svg;
    },

    // Equal Spacing Generator
    spread(n, halfWidth) {
        if (n <= 0) return [];
        if (n === 1) return [0];
        return Array.from({ length: n }, (_, i) => -halfWidth + (2 * halfWidth * i) / (n - 1));
    }
};
