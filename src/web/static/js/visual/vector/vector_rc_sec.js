// web/js/visual/vector/vector_rc_sec.js
/**
 * AltDP Vector Visual Engine - RC Beam & Column Cross Section SVG Renderer
 * Implements rigorous rebar geometry from extracted_src/renderer/drawSection.js
 * - Column: Peripheral rebar spread (nB x nH), Outer Tie, Cross-ties.
 * - Beam: Stirrup ring, Top/Bottom multi-layer rebar spread, Effective depth d.
 * Shared by Graphic View (Pane 3) and A4 Report Generator (SSOT compliant).
 */

window.VectorRcSec = {
    renderColumnSectionSVG(data = {}, options = {}) {
        // 이형 기둥 형상 파라미터가 있는 경우 이형기둥 렌더러로 자동 위임
        const shapeStr = String(data.shape || data.shape_type || data.col_shape || '').toLowerCase();
        if (shapeStr.includes('l_shape') || shapeStr.includes('t_shape') || shapeStr.includes('cross') || shapeStr.includes('irreg')) {
            return this.renderIrregularColumnSVG(data, options);
        }

        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 280;
        const H_svg = options.height || 260;
        const padL = 36, padR = 18, padT = 24, padB = 26;

        const b = Number(data.b || data.col_b || data.B || data.width || 600);
        const h = Number(data.h || data.col_h || data.H || data.depth || 600);
        const cover = Number(data.cover || 40);
        const tieDia = Number(data.tie_dia || data.tieDia || data.stirrup_dia || 10);
        const tieSpacing = Number(data.tie_spacing || data.tieSpacing || data.spacing || data.s || data.tie_s || 200);

        // 상세 배근 기둥 파라미터 (corner_dia, side_y_num/dia, side_z_num/dia) 지원
        const cornerDia = Number(data.corner_dia || data.cornerDia || data.main_dia || data.mainDia || data.bar_dia || 25);
        const sideYDia = Number(data.side_y_dia || data.sideYDia || data.main_dia || data.mainDia || cornerDia);
        const sideZDia = Number(data.side_z_dia || data.sideZDia || data.main_dia || data.mainDia || cornerDia);
        const mainDia = Math.max(cornerDia, sideYDia, sideZDia);

        // 총 주근 개수 또는 변당 철근 개수 산출 (side_z_num, side_y_num, num_z, num_y 지원)
        let nB = 0;
        let nH = 0;
        if (data.side_z_num !== undefined || data.side_y_num !== undefined) {
            nB = Number(data.side_z_num || 0) + 2;
            nH = Number(data.side_y_num || 0) + 2;
        } else {
            nB = Number(data.num_z || data.nB || data.bars_b || data.nb || data.nx || 0);
            nH = Number(data.num_y || data.nH || data.bars_h || data.nh || data.ny || 0);
        }

        const totalNum = Number(data.main_num || data.n_bars || data.total_bars || 0);

        if (!nB && !nH && totalNum >= 4) {
            nB = Math.max(2, Math.floor(totalNum / 4) + 1);
            nH = Math.max(2, Math.ceil((totalNum - 2 * nB) / 2) + 2);
        } else {
            if (!nB) nB = 4;
            if (!nH) nH = 4;
        }
        const totalBars = (nB * 2) + ((nH - 2) * 2);

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / b, availH / h);
        const bS = b * scale, hS = h * scale;
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - hS) / 2;

        let content = '';

        // 1. Concrete Outline
        content += C.rect(ox, oy, bS, hS, P.concreteFill, P.concreteStroke, 1.5, 2);

        // 2. Outer Tie Ring (Inside Cover)
        const tieMargin = cover * scale;
        const tieX = ox + tieMargin, tieY = oy + tieMargin;
        const tieW = bS - 2 * tieMargin, tieH = hS - 2 * tieMargin;
        content += C.rect(tieX, tieY, tieW, tieH, 'none', P.rebarTie, 1.5, 3);

        // 3. Rebar Positions & Sizes
        const inX = tieW / 2 - (tieDia + mainDia / 2) * scale * 0.7;
        const inY = tieH / 2 - (tieDia + mainDia / 2) * scale * 0.7;
        const rDotCorner = Math.max(2.5, (cornerDia / 2) * scale * 0.85);
        const rDotSideZ = Math.max(2.5, (sideZDia / 2) * scale * 0.85);
        const rDotSideY = Math.max(2.5, (sideYDia / 2) * scale * 0.85);

        const cxMid = ox + bS / 2;
        const cyMid = oy + hS / 2;

        const xs = C.spread(nB, inX);
        const ys = C.spread(nH, inY);

        // Cross-ties (if internal bars exist)
        if (nB > 2) {
            for (let i = 1; i < nB - 1; i++) {
                const bx = cxMid + xs[i];
                content += C.line(bx, tieY + 2, bx, tieY + tieH - 2, P.rebarTie, 1.0, '3,2');
            }
        }
        if (nH > 2) {
            for (let i = 1; i < nH - 1; i++) {
                const by = cyMid + ys[i];
                content += C.line(tieX + 2, by, tieX + tieW - 2, by, P.rebarTie, 1.0, '3,2');
            }
        }

        // Draw Main Rebar Dots
        // Top and Bottom rows (Z-direction)
        for (let i = 0; i < xs.length; i++) {
            const x = xs[i];
            const isCorner = (i === 0 || i === xs.length - 1);
            const rDot = isCorner ? rDotCorner : rDotSideZ;
            const rFill = isCorner ? P.rebarMain : '#f97316';
            content += C.circle(cxMid + x, cyMid - inY, rDot, rFill, P.concreteStroke, 0.5);
            content += C.circle(cxMid + x, cyMid + inY, rDot, rFill, P.concreteStroke, 0.5);
        }
        // Left and Right columns (Y-direction, excluding corners)
        if (nH > 2) {
            for (let i = 1; i < nH - 1; i++) {
                content += C.circle(cxMid - inX, cyMid + ys[i], rDotSideY, '#f97316', P.concreteStroke, 0.5);
                content += C.circle(cxMid + inX, cyMid + ys[i], rDotSideY, '#f97316', P.concreteStroke, 0.5);
            }
        }

        // Dimensions
        const hasDetailRebar = (data.corner_dia !== undefined || data.side_y_num !== undefined || data.side_z_num !== undefined);
        const tieInfo = `대근: D${tieDia}@${tieSpacing}`;
        const rebarTitle = hasDetailRebar 
            ? `기둥 배근 (모서리:4-D${cornerDia} / Y:${(nH-2)*2}-D${sideYDia} / Z:${(nB-2)*2}-D${sideZDia} / ${tieInfo})`
            : `기둥 단면 배근 (${totalBars}-D${mainDia} / ${tieInfo})`;
        
        // 치수선: 단면 바로 아래 및 바로 왼쪽에 배치
        content += C.hDim(ox, ox + bS, oy + hS + 14, `b=${C.f0(b)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, ox - 14, `h=${C.f0(h)}`, P.dimText, 3, 8.5);
        content += C.text(W / 2, Math.max(10, oy - 7), rebarTitle, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    },

    renderTBeamSectionSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 280;
        const H_svg = options.height || 280;
        const padL = 36, padR = 24, padT = 24, padB = 26;

        const beff = Number(data.b_eff || data.beff || data.bf || data.b_f || data.b || 800);
        const h = Number(data.h || data.beam_h || data.H || data.depth || 650);
        const bw = Number(data.bw || data.b_w || data.stem_bw || (data.b && data.b < beff ? data.b : 350));
        const hf = Number(data.hf || data.h_f || data.flange_t || data.tf || 150);
        const cover = Number(data.cover || 40);
        const stirrupDia = Number(data.stirrup_dia || data.stirrupDia || data.stir_dia || 10);
        const stirrupSpacing = Number(data.stirrup_spacing || data.stirrupSpacing || data.spacing || data.s || data.stir_spacing || 150);
        
        const topDia = Number(data.top_dia || data.topDia || data.main_dia || 22);
        const botDia = Number(data.bot_dia || data.botDia || data.main_dia || 22);

        const top1 = Number(data.top_num || data.n_top || data.top1 || 4);
        const bot1 = Number(data.bot_num || data.n_bot || data.bot1 || 3);
        const bot2 = Number(data.bot2 || data.bot_bars_2 || 0);

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / beff, availH / h);
        const bS = beff * scale, hS = h * scale, bwS = bw * scale, hfS = hf * scale;
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - hS) / 2;
        const cx = ox + bS / 2;

        let content = '';

        // 1. T-Section Concrete Polygon Path
        const p1 = `${C.f1(ox)},${C.f1(oy)}`;
        const p2 = `${C.f1(ox + bS)},${C.f1(oy)}`;
        const p3 = `${C.f1(ox + bS)},${C.f1(oy + hfS)}`;
        const p4 = `${C.f1(cx + bwS / 2)},${C.f1(oy + hfS)}`;
        const p5 = `${C.f1(cx + bwS / 2)},${C.f1(oy + hS)}`;
        const p6 = `${C.f1(cx - bwS / 2)},${C.f1(oy + hS)}`;
        const p7 = `${C.f1(cx - bwS / 2)},${C.f1(oy + hfS)}`;
        const p8 = `${C.f1(ox)},${C.f1(oy + hfS)}`;

        content += `<polygon points="${p1} ${p2} ${p3} ${p4} ${p5} ${p6} ${p7} ${p8}" fill="${P.concreteFill}" stroke="${P.concreteStroke}" stroke-width="1.5" stroke-linejoin="round"/>`;

        // 2. Web Stirrup Ring
        const stMargin = cover * scale;
        const stX = cx - bwS / 2 + stMargin, stY = oy + stMargin;
        const stW = bwS - 2 * stMargin, stH = hS - 2 * stMargin;
        content += C.rect(stX, stY, stW, stH, 'none', P.rebarTie, 1.5, 3);

        // 3. Flange Horizontal Tie Line
        const flTieY = oy + hfS / 2;
        content += C.line(ox + stMargin, flTieY, ox + bS - stMargin, flTieY, P.rebarTie, 1.0, '3,2');

        // 4. Top Rebars (Spread across flange)
        const rDotTop = Math.max(2.5, (topDia / 2) * scale * 0.85);
        const inXFlange = (bS - 2 * stMargin) / 2 - 4;
        const xsTop = C.spread(top1, inXFlange);
        for (const x of xsTop) {
            content += C.circle(cx + x, oy + stMargin + rDotTop + 2, rDotTop, P.rebarSec, P.concreteStroke, 0.5);
        }

        // 5. Bottom Rebars (Inside stem)
        const inXStem = stW / 2 - (stirrupDia + botDia / 2) * scale * 0.7;
        const rDotBot = Math.max(2.5, (botDia / 2) * scale * 0.85);
        const botY1 = stY + stH - (stirrupDia + botDia / 2) * scale * 0.7;
        const xsBot1 = C.spread(bot1, inXStem);
        for (const x of xsBot1) {
            content += C.circle(cx + x, botY1, rDotBot, P.rebarMain, P.concreteStroke, 0.5);
        }
        if (bot2 > 0) {
            const botY2 = botY1 - (botDia + 25) * scale;
            const xsBot2 = C.spread(bot2, inXStem);
            for (const x of xsBot2) {
                content += C.circle(cx + x, botY2, rDotBot, P.rebarMain, P.concreteStroke, 0.5);
            }
        }

        // Dimensions
        const stirrupInfo = `늑근: D${stirrupDia}@${stirrupSpacing}`;
        content += C.hDim(cx - bwS / 2, cx + bwS / 2, oy + hS + 14, `bw=${C.f0(bw)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, ox - 14, `h=${C.f0(h)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hfS, ox + bS + 14, `hf=${C.f0(hf)}`, P.dimText, 3, 8);
        content += C.text(W / 2, Math.max(10, oy - 7), `T형 배근 (상${top1}-D${topDia} / 하${bot1 + bot2}-D${botDia} / ${stirrupInfo})`, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    },

    renderBeamSectionSVG(data = {}, options = {}) {
        // T-Beam 또는 플랜지 파라미터가 있는 경우 T형 렌더러로 자동 위임
        const isTBeam = (data.b_eff !== undefined || data.beff !== undefined || data.hf !== undefined || data.flange_t !== undefined || String(data.shape || data.shape_type || '').toLowerCase().includes('t_shape') || String(data.shape || data.shape_type || '').toLowerCase().includes('tsect'));
        if (isTBeam) {
            return this.renderTBeamSectionSVG(data, options);
        }

        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 280;
        const H_svg = options.height || 280;
        const padL = 36, padR = 18, padT = 24, padB = 26;

        const b = Number(data.b || data.beam_b || data.B || data.width || 400);
        const h = Number(data.h || data.beam_h || data.H || data.depth || 600);
        const cover = Number(data.cover || 40);
        const stirrupDia = Number(data.stirrup_dia || data.stirrupDia || data.stir_dia || data.fys_dia || data.shear_rebar_dia || 10);
        const stirrupSpacing = Number(data.stirrup_spacing || data.stirrupSpacing || data.spacing || data.s || data.stir_spacing || 150);
        const stirrupLegs = Number(data.stirrup_legs || data.stirrupLegs || data.legs || data.n_legs || 2);
        
        const top1Dia = Number(data.top_layer1_dia || data.top_dia || data.topDia || data.main_dia || data.bar_dia || 22);
        const top2Dia = Number(data.top_layer2_dia || data.top2Dia || top1Dia);
        const bot1Dia = Number(data.bot_layer1_dia || data.bot_dia || data.botDia || data.main_dia || data.bar_dia || 25);
        const bot2Dia = Number(data.bot_layer2_dia || data.bot2Dia || bot1Dia);
        const sideDia = Number(data.side_dia || data.sideDia || 13);
        const sideNum = Number(data.side_num || data.sideNum || data.n_side || 0);

        const top1 = Number(data.top_layer1_num ?? data.top_num ?? data.n_top ?? data.top1 ?? data.top_bars_1 ?? data.top_rebar_count ?? 3);
        const top2 = Number(data.top_layer2_num ?? data.top2 ?? data.top_bars_2 ?? 0);
        const bot1 = Number(data.bot_layer1_num ?? data.bot_num ?? data.n_bot ?? data.bot1 ?? data.bot_bars_1 ?? data.bot_rebar_count ?? 3);
        const bot2 = Number(data.bot_layer2_num ?? data.bot2 ?? data.bot_bars_2 ?? 0);
        const d = Number(data.d || (h - cover - stirrupDia - bot1Dia / 2));

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / b, availH / h);
        const bS = b * scale, hS = h * scale;
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - hS) / 2;

        let content = '';

        // 1. Concrete Outline
        content += C.rect(ox, oy, bS, hS, P.concreteFill, P.concreteStroke, 1.5, 2);

        // 2. Stirrup Ring (Inside Cover)
        const stMargin = cover * scale;
        const stX = ox + stMargin, stY = oy + stMargin;
        const stW = bS - 2 * stMargin, stH = hS - 2 * stMargin;
        content += C.rect(stX, stY, stW, stH, 'none', P.rebarTie, 1.5, 3);

        const inX = stW / 2 - (stirrupDia + Math.max(top1Dia, bot1Dia) / 2) * scale * 0.7;
        const rDotTop1 = Math.max(2.5, (top1Dia / 2) * scale * 0.85);
        const rDotTop2 = Math.max(2.5, (top2Dia / 2) * scale * 0.85);
        const rDotBot1 = Math.max(2.5, (bot1Dia / 2) * scale * 0.85);
        const rDotBot2 = Math.max(2.5, (bot2Dia / 2) * scale * 0.85);
        const rDotSide = Math.max(2.0, (sideDia / 2) * scale * 0.85);
        const cxMid = ox + bS / 2;

        // 3. Top Rebar (Layer 1 & Layer 2)
        const topY1 = stY + (stirrupDia + top1Dia / 2) * scale * 0.7;
        if (top1 > 0) {
            const xsTop1 = C.spread(top1, inX);
            for (const x of xsTop1) {
                content += C.circle(cxMid + x, topY1, rDotTop1, P.rebarSec, P.concreteStroke, 0.5);
            }
        }
        if (top2 > 0) {
            const topY2 = topY1 + (top1Dia + 25) * scale;
            const xsTop2 = C.spread(top2, inX);
            for (const x of xsTop2) {
                content += C.circle(cxMid + x, topY2, rDotTop2, P.rebarSec, P.concreteStroke, 0.5);
            }
        }

        // 4. Bottom Rebar (Layer 1 & Layer 2)
        const botY1 = stY + stH - (stirrupDia + bot1Dia / 2) * scale * 0.7;
        if (bot1 > 0) {
            const xsBot1 = C.spread(bot1, inX);
            for (const x of xsBot1) {
                content += C.circle(cxMid + x, botY1, rDotBot1, P.rebarMain, P.concreteStroke, 0.5);
            }
        }
        if (bot2 > 0) {
            const botY2 = botY1 - (bot1Dia + 25) * scale;
            const xsBot2 = C.spread(bot2, inX);
            for (const x of xsBot2) {
                content += C.circle(cxMid + x, botY2, rDotBot2, P.rebarMain, P.concreteStroke, 0.5);
            }
        }

        // 5. Side Skin Rebars (표피철근)
        if (sideNum > 0) {
            const sideTopY = topY1 + (top2 > 0 ? (top1Dia + 35) * scale : 35 * scale);
            const sideBotY = botY1 - (bot2 > 0 ? (bot1Dia + 35) * scale : 35 * scale);
            const sideDist = (sideBotY - sideTopY) / (sideNum + 1);
            for (let i = 1; i <= sideNum; i++) {
                const sy = sideTopY + i * sideDist;
                content += C.circle(cxMid - inX, sy, rDotSide, '#eab308', P.concreteStroke, 0.5);
                content += C.circle(cxMid + inX, sy, rDotSide, '#eab308', P.concreteStroke, 0.5);
            }
        }

        // 6. Effective Depth Guideline d
        const dLineY = oy + d * scale;
        content += C.line(ox - 3, dLineY, ox + bS + 3, dLineY, P.guideline, 0.8, '2,2');

        // Dimensions & Title
        const topLabel = top2 > 0 ? `상${top1}+${top2}단` : `상${top1}-D${top1Dia}`;
        const botLabel = bot2 > 0 ? `하${bot1}+${bot2}단` : `하${bot1}-D${bot1Dia}`;
        const stirrupLabel = `늑근:${stirrupLegs > 2 ? stirrupLegs + '-' : ''}D${stirrupDia}@${stirrupSpacing}`;
        
        // 치수선: 단면 바로 아래 및 바로 왼쪽에 배치
        content += C.hDim(ox, ox + bS, oy + hS + 14, `b=${C.f0(b)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, ox - 14, `h=${C.f0(h)} (d=${C.f0(d)})`, P.dimText, 3, 8.5);
        content += C.text(W / 2, Math.max(10, oy - 7), `보 배근 (${topLabel} / ${botLabel} / ${stirrupLabel}${sideNum > 0 ? ` / 측${sideNum * 2}-D${sideDia}` : ''})`, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    },

    /**
     * RC 이형 기둥 SVG 렌더러 (L형, T형, 십자형 Cross) — rc/column/irreg
     */
    renderIrregularColumnSVG(data = {}, options = {}) {
        const C = window.VectorCore;
        const isDark = options.mode === 'report' ? false : (options.isDark !== undefined ? options.isDark : document.body.getAttribute('data-theme') === 'dark');
        const P = C.getPalette(isDark);

        const W = options.width || 280;
        const H_svg = options.height || 280;
        const padL = 36, padR = 18, padT = 24, padB = 26;

        const b = Number(data.b || data.B || data.width || 600);
        const h = Number(data.h || data.H || data.depth || 600);
        const tf = Number(data.tf || data.t_f || data.flange_t || data.b1 || 250);
        const tw = Number(data.tw || data.t_w || data.stem_w || data.h1 || 250);
        const cover = Number(data.cover || 40);
        const mainDia = Number(data.main_dia || data.mainDia || data.bar_dia || 22);

        const shapeStr = String(data.shape || data.shape_type || data.col_shape || 'L_shape').toLowerCase();
        const isCross = shapeStr.includes('cross') || shapeStr.includes('십자');
        const isTShape = shapeStr.includes('t_shape') || shapeStr.includes('t형');

        const availW = W - padL - padR;
        const availH = H_svg - padT - padB;
        const scale = Math.min(availW / b, availH / h);
        const bS = b * scale, hS = h * scale, tfS = tf * scale, twS = tw * scale;
        const ox = padL + (availW - bS) / 2;
        const oy = padT + (availH - hS) / 2;
        const rDot = Math.max(2.5, (mainDia / 2) * scale * 0.85);

        let content = '';
        let polyPts = [];
        let rebarPos = [];

        if (isCross) {
            // 십자형 기둥 (12각 다각형)
            const cX1 = ox + (bS - twS) / 2, cX2 = cX1 + twS;
            const cY1 = oy + (hS - tfS) / 2, cY2 = cY1 + tfS;

            polyPts = [
                { x: cX1, y: oy }, { x: cX2, y: oy },
                { x: cX2, y: cY1 }, { x: ox + bS, y: cY1 },
                { x: ox + bS, y: cY2 }, { x: cX2, y: cY2 },
                { x: cX2, y: oy + hS }, { x: cX1, y: oy + hS },
                { x: cX1, y: cY2 }, { x: ox, y: cY2 },
                { x: ox, y: cY1 }, { x: cX1, y: cY1 }
            ];

            const cMargin = cover * scale;
            rebarPos = [
                { x: cX1 + cMargin, y: oy + cMargin }, { x: cX2 - cMargin, y: oy + cMargin },
                { x: ox + bS - cMargin, y: cY1 + cMargin }, { x: ox + bS - cMargin, y: cY2 - cMargin },
                { x: cX2 - cMargin, y: oy + hS - cMargin }, { x: cX1 + cMargin, y: oy + hS - cMargin },
                { x: ox + cMargin, y: cY2 - cMargin }, { x: ox + cMargin, y: cY1 + cMargin },
                { x: cX1 + cMargin, y: cY1 + cMargin }, { x: cX2 - cMargin, y: cY1 + cMargin },
                { x: cX1 + cMargin, y: cY2 - cMargin }, { x: cX2 - cMargin, y: cY2 - cMargin }
            ];
        } else if (isTShape) {
            // T형 기둥 (8각 다각형)
            const cxMid = ox + bS / 2;
            polyPts = [
                { x: ox, y: oy }, { x: ox + bS, y: oy },
                { x: ox + bS, y: oy + tfS }, { x: cxMid + twS / 2, y: oy + tfS },
                { x: cxMid + twS / 2, y: oy + hS }, { x: cxMid - twS / 2, y: oy + hS },
                { x: cxMid - twS / 2, y: oy + tfS }, { x: ox, y: oy + tfS }
            ];

            const cMargin = cover * scale;
            rebarPos = [
                { x: ox + cMargin, y: oy + cMargin }, { x: cxMid, y: oy + cMargin }, { x: ox + bS - cMargin, y: oy + cMargin },
                { x: ox + bS - cMargin, y: oy + tfS - cMargin }, { x: ox + cMargin, y: oy + tfS - cMargin },
                { x: cxMid - twS / 2 + cMargin, y: oy + tfS + cMargin }, { x: cxMid + twS / 2 - cMargin, y: oy + tfS + cMargin },
                { x: cxMid - twS / 2 + cMargin, y: oy + hS - cMargin }, { x: cxMid + twS / 2 - cMargin, y: oy + hS - cMargin }
            ];
        } else {
            // L형 기둥 (6각 다각형)
            polyPts = [
                { x: ox, y: oy }, { x: ox + bS, y: oy },
                { x: ox + bS, y: oy + tfS }, { x: ox + twS, y: oy + tfS },
                { x: ox + twS, y: oy + hS }, { x: ox, y: oy + hS }
            ];

            const cMargin = cover * scale;
            rebarPos = [
                { x: ox + cMargin, y: oy + cMargin }, { x: ox + bS / 2, y: oy + cMargin }, { x: ox + bS - cMargin, y: oy + cMargin },
                { x: ox + bS - cMargin, y: oy + tfS - cMargin },
                { x: ox + twS - cMargin, y: oy + tfS + cMargin }, { x: ox + twS - cMargin, y: oy + hS - cMargin },
                { x: ox + cMargin, y: oy + hS - cMargin }, { x: ox + cMargin, y: oy + hS / 2 }
            ];
        }

        // 1. Concrete Outline Polygon
        content += C.polygon(polyPts, P.concreteFill, P.concreteStroke, 1.5, 'round');

        // 2. Tie Inner Guide Line (Dashed)
        content += C.polyline(polyPts, 'none', P.rebarTie, 1.2);

        // 3. Main Rebar Dots
        for (const pt of rebarPos) {
            content += C.circle(pt.x, pt.y, rDot, P.rebarMain, P.concreteStroke, 0.5);
        }

        // Dimensions
        content += C.hDim(ox, ox + bS, oy + hS + 14, `B=${C.f0(b)}`, P.dimText, 3, 8.5);
        content += C.vDim(oy, oy + hS, ox - 14, `H=${C.f0(h)}`, P.dimText, 3, 8.5);
        const shapeLabel = isCross ? '십자형(Cross)' : (isTShape ? 'T형(T-Shape)' : 'L형(L-Shape)');
        content += C.text(W / 2, Math.max(10, oy - 7), `이형 기둥 배근 (${shapeLabel} ${rebarPos.length}-D${mainDia})`, { fill: P.dimLine, size: 8.5 });

        return C.createSvgRoot(W, H_svg, content, { isDark, style: options.style });
    }
};
