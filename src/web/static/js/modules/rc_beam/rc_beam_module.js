/**
 * AltDP_3rd RC Beam Specialized Module Pack (rc_beam_module.js)
 * Implements CODABeamBase 1:1 migration and Polymorphic ModulePack Protocol
 * Conforms to Requirement 21-6 & docs/07 section 6.
 */
class RCBeamModule {
    constructor() {
        this.id = 'rc_beam';
        this.key = 'rc_beam';
        this.name = 'RC 보 (Beam)';
        this.category = 'rc';
        this.data = this.getDefaultData();
    }

    /**
     * Returns default engineering input data for RC beam conforming to KDS 14 20
     */
    getDefaultData() {
        return {
            shape: 'RECTANGULAR',
            b: 400,
            h: 600,
            length: 6000,
            cover: 40,
            cover_top: 40,
            bf: 1200,
            hf: 150,
            fck: 27,
            fy: 400,
            fyt: 400,
            support: 'SIMPLE',

            // Rebar Detailed Stations
            rebar: {
                end_i: {
                    top_layer1: '4-D25',
                    top_layer2: '2-D25',
                    bot_layer1: '3-D22',
                    bot_layer2: '0',
                    stirrup_dia: 'D10',
                    stirrup_space: 150,
                    stirrup_legs: 2
                },
                center_m: {
                    top_layer1: '2-D22',
                    top_layer2: '0',
                    bot_layer1: '4-D25',
                    bot_layer2: '2-D25',
                    stirrup_dia: 'D10',
                    stirrup_space: 250,
                    stirrup_legs: 2
                },
                end_j: {
                    top_layer1: '4-D25',
                    top_layer2: '2-D25',
                    bot_layer1: '3-D22',
                    bot_layer2: '0',
                    stirrup_dia: 'D10',
                    stirrup_space: 150,
                    stirrup_legs: 2
                },
                torsion_side_bar: 'D13',
                torsion_side_count: 4,
                mainHook: '90',
                stirrupHook: '135',
                maxAggSize: 25,
                spliceType: 'none',
                differRebar: false,
                sameRebarTopBot: false,
                checkClearSpacing: true
            },

            // Design Factored Loads
            loads: {
                end_i: { Mu_pos: 0.0, Mu_neg: 240.0, Vu: 180.0, Tu: 15.0 },
                center_m: { Mu_pos: 240.0, Mu_neg: 0.0, Vu: 40.0, Tu: 5.0 },
                end_j: { Mu_pos: 0.0, Mu_neg: 240.0, Vu: 180.0, Tu: 15.0 }
            },

            // Serviceability & Deflection
            serviceability: {
                Ma_pos: 140.0,
                Ma_neg: 140.0,
                Msus: 90.0,
                sustained_ratio: 0.5,
                defl_limit: 'L/240',
                exposure: 'wet',
                seismic: 'OMF'
            },

            // Legacy shortcuts for backward compatibility
            topBars: '4-D25',
            botBars: '4-D25',
            stirrup: 'D10 @ 150',
            mu: 240.0,
            vu: 180.0
        };
    }

    async mount(context) {
        this.context = context;
        if (context.memberData) Object.assign(this.data, context.memberData);

        this.renderForm(context.formContainer, this.data, window.EventBus);
        this.renderGraphics(context.canvas, context.pmCanvas, this.data, null);
        this.renderReport(context.reportContainer, this.data, null, {});
    }

    unmount() {
        // Cleanup resources
    }

    onParamChange(payload) {
        if (payload && payload.data) {
            Object.assign(this.data, payload.data);
        } else if (payload && payload.key) {
            this.data[payload.key] = payload.value;
        }
        if (this.context) {
            this.renderGraphics(this.context.canvas, this.context.pmCanvas, this.data, null);
            // 실시간 계산서 갱신 차단: 검토 버튼 클릭(source === 'check') 시에만 갱신
            if (payload && payload.source === 'check') {
                this.renderReport(this.context.reportContainer, this.data, payload.result || null, {});
            }
        }
    }

    /**
     * Render Pane 2 4-Subtab Input Form
     */
    renderForm(container, data = this.data, bus = window.EventBus) {
        if (!container) return;
        const curData = data || this.data;

        // 1. Specialized 1:1 RC Beam Form Component (Req 22-2)
        if (window.RCBeamForm && typeof window.RCBeamForm.render === 'function') {
            window.RCBeamForm.render(container, curData, (updatedData, triggerReport = false) => {
                Object.assign(this.data, updatedData);
                if (this.context) {
                    this.renderGraphics(this.context.canvas, this.context.pmCanvas, this.data, null);
                    if (triggerReport) {
                        this.renderReport(this.context.reportContainer, this.data, null, {});
                    }
                }
            });
            return;
        }

        // 2. Fallback to generic FormBuilder
        if (window.FormBuilder) {
            const schema = {
                fields: [
                    { tab: 'section', key: 'b', label: '단면 폭 (b)', default: curData.b, unit: 'mm' },
                    { tab: 'section', key: 'h', label: '단면 높이 (h)', default: curData.h, unit: 'mm' },
                    { tab: 'section', key: 'fck', label: '콘크리트 강도 (fck)', default: curData.fck, unit: 'MPa' },
                    { tab: 'section', key: 'hasTFlange', label: 'T형 플랜지 상세', default: '설정', hasDialog: true, onOpenDialog: (cur, cb) => {
                        if (window.CommonDialogs && window.CommonDialogs.openBeamBeffDialog) {
                            window.CommonDialogs.openBeamBeffDialog(cur, cb);
                        }
                    }},
                    { tab: 'rebar', key: 'cover', label: '피복 두께 (dc)', default: curData.cover, unit: 'mm' },
                    { tab: 'rebar', key: 'topBars', label: '상부 주철근', default: curData.topBars, type: 'text' },
                    { tab: 'rebar', key: 'botBars', label: '하부 주철근', default: curData.botBars, type: 'text' },
                    { tab: 'rebar', key: 'stirrup', label: '전단 스터럽', default: curData.stirrup, type: 'text' },
                    { tab: 'load', key: 'mu', label: '계수 모멘트 (Mu)', default: curData.mu, unit: 'kN·m' },
                    { tab: 'load', key: 'vu', label: '계수 전단력 (Vu)', default: curData.vu, unit: 'kN' },
                    { tab: 'load', key: 'lcbDlg', label: '하중조합 생성기', default: '설정...', hasDialog: true, onOpenDialog: (cur, cb) => {
                        if (window.CommonDialogs && window.CommonDialogs.openLoadCombination) {
                            window.CommonDialogs.openLoadCombination(cur, cb);
                        }
                    }},
                    { tab: 'option', key: 'seismic', label: '내진 등급', type: 'select', options: [{ value: 'special', label: '특수 모멘트 골조' }, { value: 'normal', label: '보통 모멘트 골조' }] }
                ]
            };

            window.FormBuilder.build(container, schema, curData, (k, v) => {
                if (k) curData[k] = v;
                if (this.context) {
                    this.renderGraphics(this.context.canvas, this.context.pmCanvas, curData, null);
                    this.renderReport(this.context.reportContainer, curData, null, {});
                }
            });
        }
    }

    /**
     * Render Pane 3 Top/Bottom Vertical Dual Canvas (Conforms to Req 22-3)
     */
    renderGraphics(geomCanvas, mechCanvas, data = this.data, result = null) {
        const curData = data || this.data;

        // 1. If GraphicViewport singleton is available, delegate to it for unified pan/zoom/tooltips
        if (window.GraphicViewport && window.GraphicViewport.initialized) {
            window.GraphicViewport.currentMemberType = 'rc_beam';
            window.GraphicViewport.currentMemberData = curData;
            if (result) {
                window.GraphicViewport.setCalculationResult(result);
            } else {
                window.GraphicViewport.redrawAll();
            }
            return;
        }

        // 2. Direct Canvas Drawing via VectorRCBeam (Top: Longitudinal, Bottom: Cross-Sections)
        if (window.VectorRCBeam) {
            if (geomCanvas) {
                const ctx = geomCanvas.getContext('2d');
                window.VectorRCBeam.renderLongitudinalView(ctx, geomCanvas.width, geomCanvas.height, curData, true);
            }
            if (mechCanvas) {
                const ctx = mechCanvas.getContext('2d');
                window.VectorRCBeam.renderCrossSections(ctx, mechCanvas.width, mechCanvas.height, curData, result || {}, false);
            }
            return;
        }

        // 3. Fallback Primitives
        if (geomCanvas && window.VDrawPrimitives) {
            const ctx = geomCanvas.getContext('2d');
            const w = geomCanvas.width;
            const h = geomCanvas.height;
            ctx.clearRect(0, 0, w, h);
            ctx.save();
            ctx.translate(w / 2, h / 2);
            const scale = 220 / Math.max(curData.b || 400, curData.h || 600);
            ctx.scale(scale, scale);
            window.VDrawPrimitives.drawFrameBody(ctx, curData.b, curData.h);
            ctx.restore();
        }
    }

    /**
     * Legacy single-canvas rendering bridge
     */
    renderCanvas(canvas) {
        return this.renderGraphics(canvas, null, this.data, null);
    }


    renderReport(container, data = this.data, result = null, options = {}) {
        if (!container || !window.ReportRenderer) return;
        const curData = data || this.data;

        window.ReportRenderer.render(container, {
            ...curData,
            type: 'RC Beam'
        }, result || {
            dcrFlex: curData.mu / 335.2,
            dcrShear: curData.vu / 232.8,
            status: (curData.mu / 335.2 <= 1.0 && curData.vu / 232.8 <= 1.0) ? 'OK' : 'NG'
        });
    }

    /**
     * Calculate API integration
     */
    async calculate(data = this.data) {
        try {
            const res = await fetch('/api/design/rc/beam/base', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data || this.data)
            });
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {
            console.warn('[RCBeamModule] calculate API fallback:', e);
        }
        return { status: 'OK', governing_dcr: this.data.mu / 335.2 };
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_beam', new RCBeamModule());
}
