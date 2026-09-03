// web/js/visual/vector/vector_steel.js
/**
 * AltDP Vector Visual Engine - Steel H-Section, Box/Pipe & Baseplate SVG Renderer
 * Renders H-Section, RHS/CHS Hollow Section, and Baseplate with Anchor Bolts.
 * Shared by Graphic View (Pane 3) and A4 Report Generator (SSOT compliant).
 */

window.VectorSteel = {
    renderSteelSectionSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 240;
        const H_svg = options.height || 240;
        const padL = 36, padR = 18, padT = 24, padB = 26;

        const H = Number(data.H || data.h || data.depth || data.col_d || data.beam_d || data.steel_H || data.col_h || data.beam_h || 400);
        const B = Number(data.B || data.b || data.width || data.col_bf || data.beam_bf || data.col_b || data.beam_b || data.steel_B || 200);
        const tw = Number(data.tw || data.t_w || data.col_tw || data.beam_tw || data.steel_tw || data.t || 8);
        const tf = Number(data.tf || data.t_f || data.col_tf || data.beam_tf || data.steel_tf || data.t || 13);
        const shape = String(data.shape || data.shape_type || data.section_shape || data.section_type || data.sec_shape || (data.section_name && (data.section_name.includes('□') || data.section_name.toLowerCase().includes('box')) ? 'BOX' : (data.section_name && (data.section_name.includes('○') || data.section_name.toLowerCase().includes('pipe')) ? 'PIPE' : 'H'))).toUpperCase();

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / B, availH / H);
        const bS = B * scale, hS = H * scale;
        const twS = Math.max(tw * scale, 3), tfS = Math.max(tf * scale, 4);
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - hS) / 2;

        let content = '';

        if (shape.includes('BOX') || shape.includes('RECT') || shape.includes('TUBE')) {
            // Box section (Outer rect + Inner rect)
            content += C.rect(ox, oy, bS, hS, P.steelFlange, P.steelStroke, 1.5, 2);
            content += C.rect(ox + tfS, oy + tfS, bS - 2 * tfS, hS - 2 * tfS, isDark ? P.bg : '#ffffff', P.steelStroke, 1.2);
        } else if (shape.includes('PIPE') || shape.includes('CIRC')) {
            // Circular Pipe (Outer circle + Inner circle)
            const rO = Math.min(bS, hS) / 2;
            const rI = Math.max(2, rO - tfS);
            content += C.circle(W / 2, H_svg / 2, rO, P.steelFlange, P.steelStroke, 1.5);
            content += C.circle(W / 2, H_svg / 2, rI, isDark ? P.bg : '#ffffff', P.steelStroke, 1.2);
        } else {
            // Standard H-Beam Section
            // Top flange
            content += C.rect(ox, oy, bS, tfS, P.steelFlange, P.steelStroke, 1.2);
            // Web
            const webX = ox + (bS - twS) / 2;
            const webY = oy + tfS;
            const webH = hS - 2 * tfS;
            content += C.rect(webX, webY, twS, webH, P.steelWeb, P.steelStroke, 1.2);
            // Bottom flange
            content += C.rect(ox, oy + hS - tfS, bS, tfS, P.steelFlange, P.steelStroke, 1.2);
        }

        // Dimensions
        content += C.hDim(ox, ox + bS, oy + hS + 14, `B=${C.f0(B)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, ox - 14, `H=${C.f0(H)}`, P.dimText, 3, 8.5);
        content += C.text(W / 2, Math.max(10, oy - 7), `강재 단면 (${C.f0(H)}×${C.f0(B)}×${C.f0(tw)}×${C.f0(tf)})`, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    },

    renderBaseplateSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 280;
        const H_svg = options.height || 260;
        const padL = 36, padR = 18, padT = 24, padB = 26;

        const N = Number(data.N || data.bp_len || data.L || 500);
        const B = Number(data.B || data.bp_wid || data.W || 400);
        const col_d = Number(data.col_d || data.H || 250);
        const col_bf = Number(data.col_bf || data.B || 250);
        const nBolts = Number(data.n_bolts || data.nBolts || 4);

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / B, availH / N);
        const bS = B * scale, nS = N * scale;
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - nS) / 2;

        let content = '';

        // 1. Baseplate Rect
        content += C.rect(ox, oy, bS, nS, isDark ? '#27272a' : '#e2e8f0', P.concreteStroke, 2, 3);

        // 2. Steel Column Stamp Outline
        const colWS = col_bf * scale, colHS = col_d * scale;
        const colOX = ox + (bS - colWS) / 2, colOY = oy + (nS - colHS) / 2;
        content += C.rect(colOX, colOY, colWS, colHS, 'none', P.steelFlange, 1.5);
        content += C.line(colOX, colOY, colOX + colWS, colOY + colHS, P.steelFlange, 0.8, '2,2');
        content += C.line(colOX + colWS, colOY, colOX, colOY + colHS, P.steelFlange, 0.8, '2,2');

        // 3. Anchor Bolts (Circles)
        const boltPadX = bS * 0.15, boltPadY = nS * 0.15;
        const boltPos = [
            { x: ox + boltPadX, y: oy + boltPadY },
            { x: ox + bS - boltPadX, y: oy + boltPadY },
            { x: ox + boltPadX, y: oy + nS - boltPadY },
            { x: ox + bS - boltPadX, y: oy + nS - boltPadY }
        ];
        if (nBolts >= 6) {
            boltPos.push({ x: ox + bS / 2, y: oy + boltPadY });
            boltPos.push({ x: ox + bS / 2, y: oy + nS - boltPadY });
        }
        for (const bp of boltPos) {
            content += C.circle(bp.x, bp.y, 5, P.rebarMain, P.concreteStroke, 1.0);
            content += C.circle(bp.x, bp.y, 1.5, '#ffffff', 'none');
        }

        // Dimensions
        content += C.hDim(ox, ox + bS, oy + nS + 14, `B=${C.f0(B)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + nS, ox - 14, `N=${C.f0(N)}`, P.dimText, 3, 8.5);
        content += C.text(W / 2, Math.max(10, oy - 7), `베이스플레이트 (${nBolts}-Bolts)`, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    }
};
