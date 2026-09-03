// web/js/visual/vector/vector_wall.js
/**
 * AltDP Vector Visual Engine - RC Shear Wall & Basement Wall SVG Renderer
 * Renders wall section, 2-layer vertical & horizontal rebar, boundary element reinforcement, and dimensions.
 * Shared by Graphic View (Pane 3) and A4 Report Generator (SSOT compliant).
 */

window.VectorWall = {
    renderWallSectionSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 460;
        const H = options.height || 140;

        // Parameters extraction with fallbacks
        const lw = Number(data.Lw || data.lw || data.wall_len || data.l || data.L || 3000);
        const tw = Number(data.tw || data.t || data.wall_thick || data.thick || data.thk || 250);
        const barDia = Number(data.vert_dia || data.vertDia || data.bar_dia || data.dia_v || 13);
        const spacing = Number(data.vert_spacing || data.vertSpacing || data.spacing || data.s_v || 200);
        const cover = Number(data.cover || 40);
        const nBars = Math.max(4, Math.min(30, Math.round(lw / Math.max(50, spacing))));

        const padL = 40, padT = 25;
        const pw = W - 80;
        const ph = Math.max(30, Math.min(60, tw * (pw / Math.max(lw, 1000))));

        let content = '';

        // 1. Concrete Outline
        content += C.rect(padL, padT, pw, ph, P.concreteFill, P.concreteStroke, 1.5, 2);

        // 2. Horizontal Rebar Guidelines (Top/Bottom Ties)
        const rebarTopY = padT + 8;
        const rebarBotY = padT + ph - 8;
        content += C.line(padL + 6, rebarTopY, padL + pw - 6, rebarTopY, P.rebarTie, 1.0);
        content += C.line(padL + 6, rebarBotY, padL + pw - 6, rebarBotY, P.rebarTie, 1.0);

        // 3. Vertical Rebar (2-Layer Dots)
        const step = (pw - 20) / (nBars - 1);
        for (let i = 0; i < nBars; i++) {
            const cx = padL + 10 + i * step;
            // Boundary element highlight for first 2 and last 2 bars
            const isBoundary = i < 2 || i >= nBars - 2;
            const rFill = isBoundary ? P.rebarMain : (isDark ? '#fbbf24' : '#b45309');
            const rSize = isBoundary ? 3.5 : 2.8;

            content += C.circle(cx, rebarTopY, rSize, rFill, P.concreteStroke, 0.5);
            content += C.circle(cx, rebarBotY, rSize, rFill, P.concreteStroke, 0.5);
        }

        // 4. Dimensions
        content += C.hDim(padL, padL + pw, padT + ph + 16, `Lw = ${C.f0(lw)} mm`, P.dimText, 3, 9.5);
        content += C.vDim(padT, padT + ph, padL + pw + 18, `tw = ${C.f0(tw)} mm`, P.dimText, 3, 9.5);

        // 5. Boundary Element Annotation (if space allows)
        content += C.text(padL + 20, padT - 8, '단부(BE)', { fill: P.rebarMain, size: 8.5, bold: true });
        content += C.text(padL + pw - 20, padT - 8, '단부(BE)', { fill: P.rebarMain, size: 8.5, bold: true });
        content += C.text(padL + pw / 2, padT - 8, `전단벽 단면 배근도 (${nBars * 2} - D${barDia})`, { fill: P.dimLine, size: 9 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    }
};
