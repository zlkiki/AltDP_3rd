// web/js/visual/canvas_renderer.js
/**
 * AltDP Visual Engine - Master Visual & Graphics Orchestrator & Dispatcher
 * Sub-renderers: VectorCore, VectorWall, VectorFooting, VectorSlab, VectorSteel, VectorRcSec,
 *                CanvasCore, LegendBar, DrawRc, DrawSteel, DrawPcMisc
 * Fully compliant with AGENTS.md (SSOT, 4-Unit Systems, Zero-Build)
 */

window.CanvasRenderer = {
    lastGeomType: 'rc_rect',
    lastData: {},
    lastModulePath: '',

    initObserver() {
        if (window.CanvasCore) {
            window.CanvasCore.initObserver('canvas-wrap', () => {
                this.redrawCurrent();
            });
        }
    },

    render(canvas, resultData, modulePath) {
        if (!canvas) return;
        this.lastModulePath = modulePath || '';
        const geomType = (window.allModules && window.allModules.find(m => m.key === modulePath)?.geomType) || 'rc_rect';
        this.draw(canvas, geomType, resultData);
    },

    redrawCurrent() {
        const canvas = document.getElementById('sectionCanvas');
        if (canvas && this.lastData) {
            const wrap = canvas.parentElement;
            if (wrap) {
                const rect = wrap.getBoundingClientRect();
                const w = Math.max(160, Math.floor(rect.width - 20));
                const h = Math.max(160, Math.floor(rect.height - 20));
                if (w > 0 && h > 0 && (Math.abs(canvas.width - w) > 2 || Math.abs(canvas.height - h) > 2)) {
                    canvas.width = w;
                    canvas.height = h;
                }
            }
            this.draw(canvas, this.lastGeomType, this.lastData);
        }
    },

    fmtDim(canonicalVal, qtyType = 'length') {
        return window.CanvasCore ? window.CanvasCore.fmtDim(canonicalVal, qtyType) : `${canonicalVal}`;
    },

    dispatchVectorSVG(geomType, data, W, H, customOpts = {}) {
        if (!data) return '';
        const opts = Object.assign({ mode: 'viewport', width: W, height: H }, customOpts);
        const modKey = (opts.modulePath || this.lastModulePath || '').toLowerCase();
        
        if (geomType === 'rc_tsect' || modKey.includes('tsect')) {
            if (window.VectorRcSec && typeof window.VectorRcSec.renderTBeamSectionSVG === 'function') {
                return window.VectorRcSec.renderTBeamSectionSVG(data, opts);
            }
        } else if (geomType === 'rc_col_irreg' || modKey.includes('irreg')) {
            if (window.VectorRcSec && typeof window.VectorRcSec.renderIrregularColumnSVG === 'function') {
                return window.VectorRcSec.renderIrregularColumnSVG(data, opts);
            }
        } else if (geomType === 'rc_slab_pro' || modKey.includes('slab/pro')) {
            if (window.VectorSlab && typeof window.VectorSlab.renderTSlabSectionSVG === 'function') {
                return window.VectorSlab.renderTSlabSectionSVG(data, opts);
            }
        } else if (geomType === 'rc_rect') {
            // 1. Check if it's explicitly a wall module or wall data
            if (modKey.includes('/wall/') || data.Lw !== undefined || data.tw !== undefined || data.wall_t !== undefined || data.wall_l !== undefined) {
                if (window.VectorWall && typeof window.VectorWall.renderWallSectionSVG === 'function') {
                    return window.VectorWall.renderWallSectionSVG(data, opts);
                }
            }
            // 2. Check if it's explicitly a beam module or has beam data
            const isBeamMod = modKey.includes('/beam/') || (
                data.n_top !== undefined || 
                data.top_rebar_count !== undefined || 
                data.topDia !== undefined || 
                data.top1 !== undefined || 
                data.beam_b !== undefined ||
                data.top_dia !== undefined ||
                data.top_num !== undefined ||
                data.top_layer1_num !== undefined ||
                data.top_layer2_num !== undefined ||
                data.bot_dia !== undefined ||
                data.bot_num !== undefined ||
                data.bot_layer1_num !== undefined ||
                data.bot_layer2_num !== undefined ||
                data.side_dia !== undefined ||
                data.side_num !== undefined
            );

            if (isBeamMod && window.VectorRcSec && typeof window.VectorRcSec.renderBeamSectionSVG === 'function') {
                return window.VectorRcSec.renderBeamSectionSVG(data, opts);
            } else if (window.VectorRcSec && typeof window.VectorRcSec.renderColumnSectionSVG === 'function') {
                return window.VectorRcSec.renderColumnSectionSVG(data, opts);
            }
        } else if (geomType === 'rc_column' && window.VectorRcSec && typeof window.VectorRcSec.renderColumnSectionSVG === 'function') {
            return window.VectorRcSec.renderColumnSectionSVG(data, opts);
        } else if (geomType === 'rc_wall' && window.VectorWall && typeof window.VectorWall.renderWallSectionSVG === 'function') {
            return window.VectorWall.renderWallSectionSVG(data, opts);
        } else if (geomType === 'rc_footing' && window.VectorFooting && typeof window.VectorFooting.renderFootingSectionSVG === 'function') {
            return window.VectorFooting.renderFootingSectionSVG(data, opts);
        } else if (geomType === 'rc_slab' && window.VectorSlab && typeof window.VectorSlab.renderSlabSectionSVG === 'function') {
            return window.VectorSlab.renderSlabSectionSVG(data, opts);
        } else if ((geomType === 'steel_h' || geomType === 'steel_box_pipe') && window.VectorSteel && typeof window.VectorSteel.renderSteelSectionSVG === 'function') {
            return window.VectorSteel.renderSteelSectionSVG(data, opts);
        } else if (geomType === 'steel_baseplate' && window.VectorSteel && typeof window.VectorSteel.renderBaseplateSVG === 'function') {
            return window.VectorSteel.renderBaseplateSVG(data, opts);
        } else if (geomType === 'src_section') {
            if (window.VectorRcSec && typeof window.VectorRcSec.renderBeamSectionSVG === 'function') {
                return window.VectorRcSec.renderBeamSectionSVG(data, opts);
            }
        }
        return '';
    },

    draw(canvas, geomType, data, modulePath) {
        if (!canvas) return;
        this.initObserver();
        this.lastGeomType = geomType || 'rc_rect';
        this.lastData = data || {};
        if (modulePath) this.lastModulePath = modulePath;

        const ctx = canvas.getContext('2d');
        const W = canvas.width, H = canvas.height;
        const isLight = document.body.getAttribute('data-theme') === 'light';

        const wrap = canvas.parentElement;
        let svgContainer = document.getElementById('vector-svg-overlay');
        if (!svgContainer && wrap) {
            svgContainer = document.createElement('div');
            svgContainer.id = 'vector-svg-overlay';
            svgContainer.style.position = 'absolute';
            svgContainer.style.top = '0';
            svgContainer.style.left = '0';
            svgContainer.style.width = '100%';
            svgContainer.style.height = '100%';
            svgContainer.style.display = 'flex';
            svgContainer.style.alignItems = 'center';
            svgContainer.style.justifyContent = 'center';
            svgContainer.style.zIndex = '10';
            wrap.style.position = 'relative';
            wrap.appendChild(svgContainer);
        }

        const svgHtml = this.dispatchVectorSVG(this.lastGeomType, data, W, H, { modulePath: this.lastModulePath });

        if (svgHtml && svgContainer) {
            svgContainer.innerHTML = svgHtml;
            svgContainer.style.display = 'flex';
            svgContainer.style.backgroundColor = isLight ? '#ffffff' : '#1e1e1e';
            canvas.style.display = 'none'; // Hide Canvas 2D
        } else {
            if (svgContainer) svgContainer.style.display = 'none';
            canvas.style.display = 'block';

            ctx.clearRect(0, 0, W, H);
            ctx.save();

            // 1. Draw Grid & Background
            if (window.CanvasCore) {
                window.CanvasCore.drawGrid(ctx, W, H, isLight);
            }

            const cx = W / 2 + 10;
            const cy = H / 2 - 6;

            // 2. Dispatch to Domain Sub-Renderer (Canvas 2D Graphics Engine)
            if (geomType === 'rc_rect' && window.DrawRc) {
                window.DrawRc.drawRcRect(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'rc_tsect' && window.DrawRc) {
                window.DrawRc.drawRcTSect(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'steel_h' && window.DrawSteel) {
                window.DrawSteel.drawSteelH(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'steel_box_pipe' && window.DrawSteel) {
                window.DrawSteel.drawSteelBoxPipe(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'rc_footing' && window.DrawRc) {
                window.DrawRc.drawRcFooting(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'rc_slab' && window.DrawRc) {
                window.DrawRc.drawRcSlab(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'steel_baseplate' && window.DrawSteel) {
                window.DrawSteel.drawSteelBaseplate(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'pc_double_tee' && window.DrawPcMisc) {
                window.DrawPcMisc.drawPcDoubleTee(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'bracket' && window.DrawPcMisc) {
                window.DrawPcMisc.drawBracketCorbel(ctx, cx, cy, data, W, H, isLight);
            } else if (geomType === 'src_section' && window.DrawPcMisc) {
                window.DrawPcMisc.drawSrcSection(ctx, cx, cy, data, W, H, isLight);
            } else if (window.DrawRc) {
                window.DrawRc.drawRcRect(ctx, cx, cy, data, W, H, isLight);
            }

            // 3. Draw DCR Badge & Spectrum (Top Left)
            const dcr = Number(data.governing_dcr || data.max_dcr || data.DCR || data.dcr || data.dcr_flex || 0);
            if (dcr > 0 && window.LegendBar) {
                window.LegendBar.drawDcrBadge(ctx, 10, 8, dcr, isLight);
                window.LegendBar.drawSpectrumBar(ctx, 10, 30, 90, 4, dcr, isLight);
            }

            // 4. Draw Unit Badge (Top Right)
            if (window.CanvasCore) {
                window.CanvasCore.drawUnitBadge(ctx, W, H, isLight);
            }

            ctx.restore();
        }
    },

    // --- Vector SVG Section Renderers (SSOT Shared between Visual & A4 Reports) ---
    renderWallSVG(data, opts = {}) {
        return window.VectorWall ? window.VectorWall.renderWallSectionSVG(data, opts) : '';
    },
    renderFootingSVG(data, opts = {}) {
        return window.VectorFooting ? window.VectorFooting.renderFootingSectionSVG(data, opts) : '';
    },
    renderSoilPressureSVG(qmax, qmin, qa, opts = {}) {
        return window.VectorFooting ? window.VectorFooting.renderSoilPressureSVG(qmax, qmin, qa, opts) : '';
    },
    renderSlabSVG(data, opts = {}) {
        return window.VectorSlab ? window.VectorSlab.renderSlabSectionSVG(data, opts) : '';
    },
    renderSteelSVG(data, opts = {}) {
        return window.VectorSteel ? window.VectorSteel.renderSteelSectionSVG(data, opts) : '';
    },
    renderBaseplateSVG(data, opts = {}) {
        return window.VectorSteel ? window.VectorSteel.renderBaseplateSVG(data, opts) : '';
    },
    renderColumnSVG(data, opts = {}) {
        return window.VectorRcSec ? window.VectorRcSec.renderColumnSectionSVG(data, opts) : '';
    },
    renderBeamSVG(data, opts = {}) {
        return window.VectorRcSec ? window.VectorRcSec.renderBeamSectionSVG(data, opts) : '';
    },

    // --- Legacy / Direct Dispatch Proxies for A4 Report Generators & External Modules ---
    drawRcRect(...args) { if (window.DrawRc) window.DrawRc.drawRcRect(...args); },
    drawRcTSect(...args) { if (window.DrawRc) window.DrawRc.drawRcTSect(...args); },
    drawRcFooting(...args) { if (window.DrawRc) window.DrawRc.drawRcFooting(...args); },
    drawRcSlab(...args) { if (window.DrawRc) window.DrawRc.drawRcSlab(...args); },
    drawSteelH(...args) { if (window.DrawSteel) window.DrawSteel.drawSteelH(...args); },
    drawSteelBoxPipe(...args) { if (window.DrawSteel) window.DrawSteel.drawSteelBoxPipe(...args); },
    drawSteelBaseplate(...args) { if (window.DrawSteel) window.DrawSteel.drawSteelBaseplate(...args); },
    drawPcDoubleTee(...args) { if (window.DrawPcMisc) window.DrawPcMisc.drawPcDoubleTee(...args); },
    drawBracketCorbel(...args) { if (window.DrawPcMisc) window.DrawPcMisc.drawBracketCorbel(...args); },
    drawSrcSection(...args) { if (window.DrawPcMisc) window.DrawPcMisc.drawSrcSection(...args); }
};

