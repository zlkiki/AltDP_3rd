// web/js/visual/vector/vector_slab.js
/**
 * AltDP Vector Visual Engine - RC 1-Way & 2-Way Slab SVG Renderer
 * Renders Slab Panel Plan (Span Lx, Ly, Moment direction arrows, Lambda ratio)
 * and Cross Section Detail (Unit width b=1000mm, thickness t, rebar layers).
 * Shared by Graphic View (Pane 3) and A4 Report Generator (SSOT compliant).
 */

window.VectorSlab = {
    renderSlabSectionSVG(data = {}, options = {}) {
        // 일체형 슬래브-보(rc/slab/pro) 또는 보 제원이 포함된 경우 T형 슬래브 렌더러로 자동 위임
        if (data.beam_b || data.beam_h || data.stem_b || data.b_w || data.bw || String(data.slab_type || '').includes('pro')) {
            return this.renderTSlabSectionSVG(data, options);
        }

        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 460;
        const H = options.height || 180;
        const pad = 20;

        // Parameters extraction with fallbacks
        const Lx = Number(data.Lx || data.lx || data.span_x || 4000);
        const Ly = Number(data.Ly || data.ly || data.span_y || 6000);
        const t = Number(data.t || data.thick || data.h || data.slab_t || 200);
        const d = Number(data.d || (t - 30));

        let content = '';

        // ==========================================
        // 1. Panel Plan View (Left Half: 0 ~ W/2 - 10)
        // ==========================================
        const planW = W / 2 - 15;
        const scalePlan = Math.min((planW - 2 * pad) / Lx, (H - 2 * pad) / Ly);
        const lxS = Lx * scalePlan, lyS = Ly * scalePlan;
        const ox1 = (planW - lxS) / 2 + 5, oy1 = (H - lyS) / 2;

        // Slab panel boundary
        content += C.rect(ox1, oy1, lxS, lyS, P.concreteFill, P.concreteStroke, 1.5, 2);

        // Rebar Direction Lines (X: Blue, Y: Red)
        content += C.line(ox1 + 8, oy1 + lyS / 2, ox1 + lxS - 8, oy1 + lyS / 2, P.rebarTie, 2.0);
        content += C.line(ox1 + lxS / 2, oy1 + 8, ox1 + lxS / 2, oy1 + lyS - 8, P.rebarMain, 2.0);

        // Plan dimensions & Lambda aspect ratio
        const lambda = (Ly / Math.max(1, Lx)).toFixed(2);
        const isOneWay = (Ly / Math.max(1, Lx)) >= 2.0;
        content += C.hDim(ox1, ox1 + lxS, Math.min(oy1 + lyS + 14, H - 6), `Lx=${C.f0(Lx)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy1, oy1 + lyS, Math.max(ox1 - 12, 8), `Ly=${C.f0(Ly)}`, P.dimText, 3, 8.5);
        content += C.text(ox1 + lxS / 2, oy1 + lyS / 2 - 8, `λ=${lambda} (${isOneWay ? '1방향' : '2방향'})`, { fill: isDark ? '#60a5fa' : '#1e3a8a', size: 8, bold: true });
        content += C.text(ox1 + lxS / 2, Math.max(10, oy1 - 6), '슬래브 패널 평면도', { fill: P.dimLine, size: 8 });

        // ==========================================
        // 2. Cross Section View (Right Half: W/2 + 10 ~ W)
        // ==========================================
        const ox2 = W / 2 + 15;
        const sectW = W / 2 - 25;
        const scaleSect = Math.min((sectW - 20) / 1000, (H - 2 * pad - 20) / (t * 2.5));
        const slabWS = 1000 * scaleSect, tS = t * scaleSect;
        const oy2 = H / 2 + 25;

        // Slab concrete section
        content += C.rect(ox2 + (sectW - slabWS) / 2, oy2 - tS, slabWS, tS, P.concreteFill, P.concreteStroke, 1.5, 2);

        // Main rebar line and distribution rebar dots
        const rebarY = oy2 - (t - d) * scaleSect;
        const secStartX = ox2 + (sectW - slabWS) / 2;
        content += C.line(secStartX + 5, rebarY, secStartX + slabWS - 5, rebarY, P.rebarTie, 2.0);

        for (let i = 1; i <= 5; i++) {
            const dotX = secStartX + i * (slabWS / 6);
            content += C.circle(dotX, rebarY, 3, P.rebarMain, P.concreteStroke, 0.5);
        }

        // Section dimensions & label
        content += C.hDim(secStartX, secStartX + slabWS, oy2 + 14, `b = 1,000mm`, P.dimText, 3, 8.5);
        content += C.vDim(oy2 - tS, oy2, secStartX + slabWS + 18, `t=${C.f0(t)} (d=${C.f0(d)})`, P.dimText, 3, 8.5);
        content += C.text(secStartX + slabWS / 2, oy2 - tS - 8, '주철근 / 배력철근 배근', { fill: P.rebarTie, size: 8 });
        content += C.text(ox2 + sectW / 2, oy1 - 5, '슬래브 단면 배근도', { fill: P.dimLine, size: 8 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    },

    /**
     * RC T형 일체형 슬래브-보 SVG 렌더러 — rc/slab/pro
     */
    renderTSlabSectionSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 460;
        const H = options.height || 200;
        const pad = 24;

        const beff = Number(data.beff || data.b_eff || data.b || data.Lx || 1200);
        const tf = Number(data.tf || data.thk || data.thickness || data.t || 180);
        const bw = Number(data.beam_b || data.bw || data.b_w || data.stem_bw || 350);
        const h = Number(data.beam_h || data.h || data.H || 600);

        const scale = Math.min((W - 2 * pad) / beff, (H - 2 * pad) / h);
        const bS = beff * scale, hS = h * scale, bwS = bw * scale, tfS = tf * scale;
        const ox = (W - bS) / 2, oy = (H - hS) / 2;
        const cx = W / 2;

        let content = '';

        // 1. T-Slab Concrete Polygon (8 꼭짓점)
        const polyPts = [
            { x: ox, y: oy }, { x: ox + bS, y: oy },
            { x: ox + bS, y: oy + tfS }, { x: cx + bwS / 2, y: oy + tfS },
            { x: cx + bwS / 2, y: oy + hS }, { x: cx - bwS / 2, y: oy + hS },
            { x: cx - bwS / 2, y: oy + tfS }, { x: ox, y: oy + tfS }
        ];
        content += C.polygon(polyPts, P.concreteFill, P.concreteStroke, 1.5, 'round');

        // 2. Beam Stirrup Ring (Inside stem)
        const stMargin = 25 * scale;
        const stX = cx - bwS / 2 + stMargin, stY = oy + stMargin;
        const stW = bwS - 2 * stMargin, stH = hS - 2 * stMargin;
        content += C.rect(stX, stY, stW, stH, 'none', P.rebarTie, 1.5, 3);

        // 3. Slab Top & Bottom Reinforcement lines
        content += C.line(ox + 8, oy + 12, ox + bS - 8, oy + 12, P.rebarTie, 1.2, '3,2');
        content += C.line(ox + 8, oy + tfS - 12, ox + bS - 8, oy + tfS - 12, P.rebarTie, 1.2, '3,2');

        // Slab rebar dots
        for (let i = 1; i <= 6; i++) {
            const dotX = ox + i * (bS / 7);
            content += C.circle(dotX, oy + 12, 2.5, P.rebarSec, P.concreteStroke, 0.5);
            content += C.circle(dotX, oy + tfS - 12, 2.5, P.rebarSec, P.concreteStroke, 0.5);
        }

        // 4. Beam Bottom Rebar Dots (Inside stirrup)
        const botRebarY = stY + stH - 8;
        content += C.circle(cx - bwS / 4, botRebarY, 3.5, P.rebarMain, P.concreteStroke, 0.5);
        content += C.circle(cx, botRebarY, 3.5, P.rebarMain, P.concreteStroke, 0.5);
        content += C.circle(cx + bwS / 4, botRebarY, 3.5, P.rebarMain, P.concreteStroke, 0.5);

        // 5. Dimensions
        content += C.hDim(ox, ox + bS, oy - 8, `beff = ${C.f0(beff)} mm`, P.dimText, 3, 8.5);
        content += C.hDim(cx - bwS / 2, cx + bwS / 2, H - 6, `bw = ${C.f0(bw)} mm`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, 8, `h = ${C.f0(h)} mm`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + tfS, W - 6, `tf = ${C.f0(tf)} mm`, P.dimText, 3, 8);
        content += C.text(W / 2, H - 24, '일체형 슬래브-보 (T-Slab Pro) 단면 배근도', { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H, content, { isDark, style: options.style });
    }
};
