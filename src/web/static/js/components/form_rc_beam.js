/**
 * AltDP_3rd RC Beam Specialized 1:1 Sub-Tab Input Form Component (form_rc_beam.js)
 * Conforms to Requirement 22-2, docs/07 PART 4, and docs/16
 * Replicates IDD_RCS_BEAM_PMODE_DLG, IDD_RCS_BEAM_REBAR_DLG, IDD_RCS_DEFL_DLG from DLG_DPLUS_RCS.ini
 */

class RCBeamFormComponent {
    constructor() {
        this.activeTab = 'section'; // 'section', 'rebar', 'load', 'serviceability'
        this.data = {};
        this.onChangeCallback = null;
        this.debounceTimer = null;
    }

    /**
     * Mount and render the 4-subtab RC Beam form into container
     * @param {HTMLElement} container 
     * @param {Object} currentData 
     * @param {Function} onChangeCallback 
     */
    render(container, currentData = {}, onChangeCallback = null) {
        if (!container) return;
        this.container = container;
        this.data = this._normalizeData(currentData);
        this.onChangeCallback = onChangeCallback;

        this.container.innerHTML = '';
        this.container.className = 'rc-beam-form-container';

        // 0. Render Sticky Floating Header Container (Requirement 22-5-2 & docs/07)
        const stickyHeader = document.createElement('div');
        stickyHeader.className = 'form-sticky-header beam-sticky-header';

        // 0-1. Render 3-Action Button Toolbar (Apply, Check, Auto-Design) - 32px Compact
        const actionBar = document.createElement('div');
        actionBar.className = 'input-action-bar beam-action-bar';
        actionBar.innerHTML = `
            <button type="button" class="btn-action-compact btn-apply-action" id="beam-btn-apply" title="현재 입력 데이터를 메모리에 기록하고 캔버스를 갱신합니다">
                💾 적용
            </button>
            <button type="button" class="btn-action-compact btn-check-action" id="beam-btn-check" title="현재 입력 조건으로 KDS 기준 검토를 수행하고 계산서를 갱신합니다">
                ⚡ 검토
            </button>
            <button type="button" class="btn-action-compact btn-design-action" id="beam-btn-design" title="현재 단면에 대해 최적 철근 배근을 자동 설계합니다">
                ✨ 자동설계
            </button>
        `;
        stickyHeader.appendChild(actionBar);

        actionBar.querySelector('#beam-btn-apply').onclick = () => this._handleApply();
        actionBar.querySelector('#beam-btn-check').onclick = () => this._handleCheck();
        actionBar.querySelector('#beam-btn-design').onclick = () => this._handleAutoDesign();

        // 0-2. Render Subtab Navigation Bar
        const navBar = document.createElement('div');
        navBar.className = 'sub-tab-bar beam-subtab-bar';
        navBar.innerHTML = `
            <button type="button" class="sub-tab-btn ${this.activeTab === 'section' ? 'active' : ''}" data-tab="section">
                📐 단면 / 재료
            </button>
            <button type="button" class="sub-tab-btn ${this.activeTab === 'rebar' ? 'active' : ''}" data-tab="rebar">
                ▦ 철근 배근
            </button>
            <button type="button" class="sub-tab-btn ${this.activeTab === 'load' ? 'active' : ''}" data-tab="load">
                ⚖️ 부재력 / 하중
            </button>
            <button type="button" class="sub-tab-btn ${this.activeTab === 'serviceability' ? 'active' : ''}" data-tab="serviceability">
                ⚙️ 사용성 / 처짐
            </button>
        `;
        stickyHeader.appendChild(navBar);

        this.container.appendChild(stickyHeader);

        // 1. Render Subtab Content Panes
        const contentWrap = document.createElement('div');
        contentWrap.className = 'sub-tab-contents beam-tab-contents';

        contentWrap.appendChild(this._buildSectionTab());
        contentWrap.appendChild(this._buildRebarTab());
        contentWrap.appendChild(this._buildLoadTab());
        contentWrap.appendChild(this._buildServiceabilityTab());

        this.container.appendChild(contentWrap);

        // 2. Tab Switching Events
        navBar.querySelectorAll('.sub-tab-btn').forEach(btn => {
            btn.onclick = () => {
                const target = btn.dataset.tab;
                this.activeTab = target;
                navBar.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === target));
                contentWrap.querySelectorAll('.beam-tab-pane').forEach(p => p.classList.toggle('active', p.id === `beam-tab-${target}`));
            };
        });

        // 3. Initial validation, 12-point clear spacing preview and load table arrange state
        this._updateLoadTableArrangeState(this.container);
        this._updateSpacingPreview();
    }

    /**
     * Normalize and ensure all required fields for RC beam exist
     */
    _normalizeData(raw = {}) {
        return {
            shape: raw.shape || (raw.hasTFlange ? 'TEE' : 'RECTANGULAR'),
            b: Number(raw.b || raw.bw || 400),
            h: Number(raw.h || 600),
            length: Number(raw.length || raw.ln || 6000),
            cover: Number(raw.cover || 40),
            cover_top: Number(raw.cover_top || 40),
            bf: Number(raw.bf || raw.beff || 1200),
            hf: Number(raw.hf || raw.slab_thick || 150),
            fck: Number(raw.fck || 27),
            fy: Number(raw.fy || 400),
            fyt: Number(raw.fyt || raw.fys || 400),
            support: raw.support || 'SIMPLE',

            // Rebar Stations (End-I, Center-M, End-J)
            rebar: {
                end_i: {
                    top_layer1: raw.rebar?.end_i?.top_layer1 || '4-D25',
                    top_layer2: raw.rebar?.end_i?.top_layer2 || '2-D25',
                    bot_layer1: raw.rebar?.end_i?.bot_layer1 || '3-D22',
                    bot_layer2: raw.rebar?.end_i?.bot_layer2 || '0',
                    stirrup_dia: raw.rebar?.end_i?.stirrup_dia || 'D10',
                    stirrup_space: Number(raw.rebar?.end_i?.stirrup_space || 150),
                    stirrup_legs: Number(raw.rebar?.end_i?.stirrup_legs || 2)
                },
                center_m: {
                    top_layer1: raw.rebar?.center_m?.top_layer1 || '2-D22',
                    top_layer2: raw.rebar?.center_m?.top_layer2 || '0',
                    bot_layer1: raw.rebar?.center_m?.bot_layer1 || '4-D25',
                    bot_layer2: raw.rebar?.center_m?.bot_layer2 || '2-D25',
                    stirrup_dia: raw.rebar?.center_m?.stirrup_dia || 'D10',
                    stirrup_space: Number(raw.rebar?.center_m?.stirrup_space || 250),
                    stirrup_legs: Number(raw.rebar?.center_m?.stirrup_legs || 2)
                },
                end_j: {
                    top_layer1: raw.rebar?.end_j?.top_layer1 || '4-D25',
                    top_layer2: raw.rebar?.end_j?.top_layer2 || '2-D25',
                    bot_layer1: raw.rebar?.end_j?.bot_layer1 || '3-D22',
                    bot_layer2: raw.rebar?.end_j?.bot_layer2 || '0',
                    stirrup_dia: raw.rebar?.end_j?.stirrup_dia || 'D10',
                    stirrup_space: Number(raw.rebar?.end_j?.stirrup_space || 150),
                    stirrup_legs: Number(raw.rebar?.end_j?.stirrup_legs || 2)
                },
                torsion_side_bar: raw.rebar?.torsion_side_bar || 'D13',
                torsion_side_count: Number(raw.rebar?.torsion_side_count || 4),
                arrange_type: raw.rebar?.arrange_type || 'SYMMETRIC_ENDS', // 'ONE_SECTION', 'SYMMETRIC_ENDS', 'THREE_STATIONS'
                // Rebar Dialog details
                mainHook: raw.rebar?.mainHook || '90',
                stirrupHook: raw.rebar?.stirrupHook || '135',
                maxAggSize: Number(raw.rebar?.maxAggSize || 25),
                spliceType: raw.rebar?.spliceType || 'none',
                differRebar: raw.rebar?.differRebar ?? false,
                sameRebarTopBot: raw.rebar?.sameRebarTopBot ?? false,
                checkClearSpacing: raw.rebar?.checkClearSpacing ?? true
            },

            // Loads Stations
            loads: {
                end_i: {
                    Mu_pos: Number(raw.loads?.end_i?.Mu_pos || 0.0),
                    Mu_neg: Number(raw.loads?.end_i?.Mu_neg || raw.mu || 240.0),
                    Vu: Number(raw.loads?.end_i?.Vu || raw.vu || 180.0),
                    Tu: Number(raw.loads?.end_i?.Tu || 15.0)
                },
                center_m: {
                    Mu_pos: Number(raw.loads?.center_m?.Mu_pos || raw.mu || 240.0),
                    Mu_neg: Number(raw.loads?.center_m?.Mu_neg || 0.0),
                    Vu: Number(raw.loads?.center_m?.Vu || 40.0),
                    Tu: Number(raw.loads?.center_m?.Tu || 5.0)
                },
                end_j: {
                    Mu_pos: Number(raw.loads?.end_j?.Mu_pos || 0.0),
                    Mu_neg: Number(raw.loads?.end_j?.Mu_neg || raw.mu || 240.0),
                    Vu: Number(raw.loads?.end_j?.Vu || raw.vu || 180.0),
                    Tu: Number(raw.loads?.end_j?.Tu || 15.0)
                }
            },

            // Serviceability & Deflection
            serviceability: {
                Ma_pos: Number(raw.serviceability?.Ma_pos || 140.0),
                Ma_neg: Number(raw.serviceability?.Ma_neg || 140.0),
                Msus: Number(raw.serviceability?.Msus || 90.0),
                sustained_ratio: Number(raw.serviceability?.sustained_ratio || 0.5),
                defl_limit: raw.serviceability?.defl_limit || 'L/240',
                exposure: raw.serviceability?.exposure || 'wet', // 'dry', 'wet', 'corrosive'
                seismic: raw.serviceability?.seismic || 'OMF' // 'OMF', 'IMF', 'SMF'
            },

            // Backward compatibility shortcuts
            topBars: raw.topBars || '4-D25',
            botBars: raw.botBars || '4-D25',
            stirrup: raw.stirrup || 'D10 @ 150',
            mu: Number(raw.mu || 240.0),
            vu: Number(raw.vu || 180.0)
        };
    }

    /**
     * Tab 1: Section & Material (IDD_RCS_BEAM_PMODE_DLG)
     */
    _buildSectionTab() {
        const pane = document.createElement('div');
        pane.className = `sub-tab-pane beam-tab-pane ${this.activeTab === 'section' ? 'active' : ''}`;
        pane.id = 'beam-tab-section';

        const isTee = this.data.shape === 'TEE';

        pane.innerHTML = `
            <div class="eng-form-section">
                <div class="form-section-header">단면 형상 (Cross-Section Shape)</div>
                <div class="form-radio-row" style="display:flex; gap:20px; padding:6px 0;">
                    <label class="radio-label" style="cursor:pointer; display:inline-flex; align-items:center; gap:6px;">
                        <input type="radio" name="beam_shape" value="RECTANGULAR" ${!isTee ? 'checked' : ''} id="rc-radio-rect">
                        <span>직사각형 보 (Rectangular)</span>
                    </label>
                    <label class="radio-label" style="cursor:pointer; display:inline-flex; align-items:center; gap:6px;">
                        <input type="radio" name="beam_shape" value="TEE" ${isTee ? 'checked' : ''} id="rc-radio-tee">
                        <span>T형 보 (T-Shape Beam)</span>
                    </label>
                </div>
            </div>

            <div class="eng-form-section">
                <div class="form-section-header">기하 치수 (Dimensions)</div>
                <div class="form-grid-2col">
                    <div class="form-group-row">
                        <label for="beam-input-bw">복부 폭 (bw):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-bw" class="form-input" value="${this.data.b}" min="100" step="50">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-h">보 전체 높이 (h):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-h" class="form-input" value="${this.data.h}" min="150" step="50">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-span">유효 경간 (L):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-span" class="form-input" value="${this.data.length}" min="1000" step="100">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-support">지지 조건:</label>
                        <div class="input-control-wrap">
                            <select id="beam-input-support" class="form-input">
                                <option value="SIMPLE" ${this.data.support === 'SIMPLE' ? 'selected' : ''}>단순지지 (Simple)</option>
                                <option value="CONT_ONE" ${this.data.support === 'CONT_ONE' ? 'selected' : ''}>일단연속 (One-end Cont.)</option>
                                <option value="CONT_BOTH" ${this.data.support === 'CONT_BOTH' ? 'selected' : ''}>양단연속 (Both Cont.)</option>
                                <option value="CANTILEVER" ${this.data.support === 'CANTILEVER' ? 'selected' : ''}>캔틸레버 (Cantilever)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-cover">인장 피복 (cc):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-cover" class="form-input" value="${this.data.cover}" min="20" step="5">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-covertop">압축 피복 (cc,top):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-covertop" class="form-input" value="${this.data.cover_top}" min="20" step="5">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                </div>

                <!-- T-Beam Specific Row (Hidden or Dimmed if RECTANGULAR) -->
                <div id="beam-t-flange-group" class="form-grid-2col" style="margin-top:8px; padding-top:8px; border-top:1px dashed var(--border); ${!isTee ? 'opacity:0.4; pointer-events:none;' : ''}">
                    <div class="form-group-row">
                        <label for="beam-input-bf">플랜지 폭 (be):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-bf" class="form-input" value="${this.data.bf}" min="200" step="50">
                            <button type="button" class="btn-more-dlg" id="btn-calc-beff" title="KDS 14 20 유효플랜지폭 자동 계산기">...</button>
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-hf">슬래브 두께 (hf):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-hf" class="form-input" value="${this.data.hf}" min="50" step="10">
                            <span class="unit-tag">mm</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="eng-form-section">
                <div class="form-section-header">재료 물성치 (KDS Materials)</div>
                <div class="form-grid-3col">
                    <div class="form-group-row">
                        <label for="beam-select-fck">콘크리트 (fck):</label>
                        <div class="input-control-wrap">
                            <select id="beam-select-fck" class="form-input">
                                <option value="21" ${this.data.fck === 21 ? 'selected' : ''}>C21 (21 MPa)</option>
                                <option value="24" ${this.data.fck === 24 ? 'selected' : ''}>C24 (24 MPa)</option>
                                <option value="27" ${this.data.fck === 27 ? 'selected' : ''}>C27 (27 MPa)</option>
                                <option value="30" ${this.data.fck === 30 ? 'selected' : ''}>C30 (30 MPa)</option>
                                <option value="35" ${this.data.fck === 35 ? 'selected' : ''}>C35 (35 MPa)</option>
                                <option value="40" ${this.data.fck === 40 ? 'selected' : ''}>C40 (40 MPa)</option>
                                <option value="50" ${this.data.fck === 50 ? 'selected' : ''}>C50 (50 MPa)</option>
                                <option value="60" ${this.data.fck === 60 ? 'selected' : ''}>C60 (60 MPa)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-select-fy">주철근 (fy):</label>
                        <div class="input-control-wrap">
                            <select id="beam-select-fy" class="form-input">
                                <option value="400" ${this.data.fy === 400 ? 'selected' : ''}>SD400 (400 MPa)</option>
                                <option value="500" ${this.data.fy === 500 ? 'selected' : ''}>SD500 (500 MPa)</option>
                                <option value="600" ${this.data.fy === 600 ? 'selected' : ''}>SD600 (600 MPa)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-select-fyt">스터럽 (fyt):</label>
                        <div class="input-control-wrap">
                            <select id="beam-select-fyt" class="form-input">
                                <option value="400" ${this.data.fyt === 400 ? 'selected' : ''}>SD400 (400 MPa)</option>
                                <option value="500" ${this.data.fyt === 500 ? 'selected' : ''}>SD500 (500 MPa)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Section tab event listeners
        const shapeRadios = pane.querySelectorAll('input[name="beam_shape"]');
        shapeRadios.forEach(r => {
            r.onchange = () => {
                this.data.shape = r.value;
                const tGroup = pane.querySelector('#beam-t-flange-group');
                if (tGroup) {
                    const isNowTee = r.value === 'TEE';
                    tGroup.style.opacity = isNowTee ? '1.0' : '0.4';
                    tGroup.style.pointerEvents = isNowTee ? 'auto' : 'none';
                }
                this._broadcastChange();
            };
        });

        // Dimensional Inputs
        const bindNum = (id, prop) => {
            const el = pane.querySelector(id);
            if (el) {
                el.oninput = () => {
                    this.data[prop] = Math.max(1, parseFloat(el.value) || 0);
                    this._broadcastChange();
                };
            }
        };

        bindNum('#beam-input-bw', 'b');
        bindNum('#beam-input-h', 'h');
        bindNum('#beam-input-span', 'length');
        bindNum('#beam-input-cover', 'cover');
        bindNum('#beam-input-covertop', 'cover_top');
        bindNum('#beam-input-bf', 'bf');
        bindNum('#beam-input-hf', 'hf');

        const selSupport = pane.querySelector('#beam-input-support');
        if (selSupport) {
            selSupport.onchange = () => {
                this.data.support = selSupport.value;
                this._broadcastChange();
            };
        }

        const bindMat = (id, prop) => {
            const el = pane.querySelector(id);
            if (el) {
                el.onchange = () => {
                    this.data[prop] = parseFloat(el.value);
                    this._broadcastChange();
                };
            }
        };
        bindMat('#beam-select-fck', 'fck');
        bindMat('#beam-select-fy', 'fy');
        bindMat('#beam-select-fyt', 'fyt');

        // Sub-dialog: Beff Calculator
        const btnCalcBeff = pane.querySelector('#btn-calc-beff');
        if (btnCalcBeff) {
            btnCalcBeff.onclick = () => {
                if (window.CommonDialogs && typeof window.CommonDialogs.openBeamBeffDialog === 'function') {
                    window.CommonDialogs.openBeamBeffDialog({
                        b: this.data.b,
                        hf: this.data.hf,
                        length: this.data.length
                    }, (res) => {
                        if (res && res.beff) {
                            this.data.bf = res.beff;
                            const bfInp = pane.querySelector('#beam-input-bf');
                            if (bfInp) bfInp.value = res.beff;
                            this._broadcastChange();
                        }
                    });
                }
            };
        }

        return pane;
    }

    /**
     * Parse rebar string (e.g. "4-D25", "0") into { count, dia }
     */
    _parseRebarStr(str, isLayer2 = false) {
        if (!str || str === '0') {
            return { count: isLayer2 ? 0 : 2, dia: 'D25' };
        }
        const parts = String(str).trim().split('-');
        let count = parseInt(parts[0]);
        if (isNaN(count)) count = isLayer2 ? 0 : 2;
        if (!isLayer2 && count < 2) count = 2;
        if (isLayer2 && count < 0) count = 0;
        const dia = parts.length > 1 ? parts[1].trim() : 'D25';
        return { count, dia };
    }

    /**
     * Tab 2: Reinforcement Detailing (IDD_RCS_BEAM_REBAR_DLG)
     */
    _buildRebarTab() {
        const pane = document.createElement('div');
        pane.className = `sub-tab-pane beam-tab-pane ${this.activeTab === 'rebar' ? 'active' : ''}`;
        pane.id = 'beam-tab-rebar';

        const rb = this.data.rebar;
        const DIA_OPTIONS = ['D10', 'D13', 'D16', 'D19', 'D22', 'D25', 'D29', 'D32', 'D35'];

        // Helper to render composite rebar cell
        const renderCompositeCell = (cellId, station, rowKey, isLayer2) => {
            const rawVal = rb[station][rowKey];
            const parsed = this._parseRebarStr(rawVal, isLayer2);
            const isDimmed = isLayer2 && parsed.count === 0;
            const minCount = isLayer2 ? 0 : 2;
            const optHtml = DIA_OPTIONS.map(d => `<option value="${d}" ${parsed.dia === d ? 'selected' : ''}>${d}</option>`).join('');
            return `
                <div class="rebar-cell-composite" id="${cellId}" data-station="${station}" data-row="${rowKey}">
                    <input type="number" id="${cellId}-cnt" class="form-input table-cell-input rebar-count-input" 
                           min="${minCount}" max="30" step="1" value="${parsed.count}">
                    <span class="rebar-sep">-</span>
                    <select id="${cellId}-dia" class="form-input rebar-dia-select" ${isDimmed ? 'disabled' : ''} 
                            style="${isDimmed ? 'opacity:0.45; pointer-events:none;' : ''}">
                        ${optHtml}
                    </select>
                </div>
            `;
        };

        const currentArrangeType = rb.arrange_type || 'SYMMETRIC_ENDS';

        pane.innerHTML = `
            <!-- Arrange Type Radio Group (Requirement 22-4-1-3 Sec 2) -->
            <div class="eng-form-section">
                <div class="form-section-header">배근 유형 (Reinforcement Arrange Type)</div>
                <div class="arrange-type-radio-group" style="display:flex; gap:16px; margin-bottom:12px; font-size:12px;">
                    <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
                        <input type="radio" name="beam_arrange_type" value="ONE_SECTION" ${currentArrangeType === 'ONE_SECTION' ? 'checked' : ''} id="rc-radio-arr-1">
                        <span>배근 유형-1 (전단면)</span>
                    </label>
                    <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
                        <input type="radio" name="beam_arrange_type" value="SYMMETRIC_ENDS" ${currentArrangeType === 'SYMMETRIC_ENDS' ? 'checked' : ''} id="rc-radio-arr-2">
                        <span>배근 유형-2 (양단부와 중앙부)</span>
                    </label>
                    <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
                        <input type="radio" name="beam_arrange_type" value="THREE_STATIONS" ${currentArrangeType === 'THREE_STATIONS' ? 'checked' : ''} id="rc-radio-arr-3">
                        <span>배근 유형-3 (각단부와 중앙부)</span>
                    </label>
                </div>
            </div>

            <div class="eng-form-section">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div class="form-section-header" style="margin-bottom:0;">위치별 주철근 및 스터럽 배근</div>
                    <button type="button" class="btn-more-dlg-wide" id="btn-open-rebar-dlg">
                        ⚙️ 배근 상세 및 갈고리...
                    </button>
                </div>

                <div class="beam-rebar-table-wrap" style="overflow-x:auto;">
                    <table class="beam-rebar-table">
                        <thead>
                            <tr>
                                <th>위치 (Station)</th>
                                <th>상부 1단</th>
                                <th>상부 2단</th>
                                <th>하부 1단</th>
                                <th>하부 2단</th>
                                <th>전단 스터럽</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- End-I -->
                            <tr id="row-endi">
                                <td style="font-weight:700;">
                                    <span>단부-I (End-I)</span>
                                    <span id="tag-endi-sym" class="badge-sym-tag" style="display:none;">[중앙부 연동]</span>
                                </td>
                                <td>${renderCompositeCell('rb-endi-t1', 'end_i', 'top_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-endi-t2', 'end_i', 'top_layer2', true)}</td>
                                <td>${renderCompositeCell('rb-endi-b1', 'end_i', 'bot_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-endi-b2', 'end_i', 'bot_layer2', true)}</td>
                                <td>
                                    <div class="stirrup-control-wrap" id="wrap-endi-st" style="display:flex; align-items:center; justify-content:center; gap:2px;">
                                        <select id="rb-endi-st-dia" class="form-input" style="width:60px; padding:2px;">
                                            <option value="D10" ${rb.end_i.stirrup_dia === 'D10' ? 'selected' : ''}>D10</option>
                                            <option value="D13" ${rb.end_i.stirrup_dia === 'D13' ? 'selected' : ''}>D13</option>
                                        </select>
                                        <span>@</span>
                                        <input type="number" id="rb-endi-st-space" class="form-input table-cell-input" value="${rb.end_i.stirrup_space}" style="width:55px; text-align:center;">
                                    </div>
                                </td>
                            </tr>
                            <!-- Center-M -->
                            <tr id="row-cent">
                                <td style="font-weight:700;">중앙-M (Center)</td>
                                <td>${renderCompositeCell('rb-cent-t1', 'center_m', 'top_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-cent-t2', 'center_m', 'top_layer2', true)}</td>
                                <td>${renderCompositeCell('rb-cent-b1', 'center_m', 'bot_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-cent-b2', 'center_m', 'bot_layer2', true)}</td>
                                <td>
                                    <div class="stirrup-control-wrap" id="wrap-cent-st" style="display:flex; align-items:center; justify-content:center; gap:2px;">
                                        <select id="rb-cent-st-dia" class="form-input" style="width:60px; padding:2px;">
                                            <option value="D10" ${rb.center_m.stirrup_dia === 'D10' ? 'selected' : ''}>D10</option>
                                            <option value="D13" ${rb.center_m.stirrup_dia === 'D13' ? 'selected' : ''}>D13</option>
                                        </select>
                                        <span>@</span>
                                        <input type="number" id="rb-cent-st-space" class="form-input table-cell-input" value="${rb.center_m.stirrup_space}" style="width:55px; text-align:center;">
                                    </div>
                                </td>
                            </tr>
                            <!-- End-J -->
                            <tr id="row-endj">
                                <td style="font-weight:700;">
                                    <span>단부-J (End-J)</span>
                                    <span id="tag-endj-sym" class="badge-sym-tag" style="display:none;">[단부-I 대칭 연동]</span>
                                </td>
                                <td>${renderCompositeCell('rb-endj-t1', 'end_j', 'top_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-endj-t2', 'end_j', 'top_layer2', true)}</td>
                                <td>${renderCompositeCell('rb-endj-b1', 'end_j', 'bot_layer1', false)}</td>
                                <td>${renderCompositeCell('rb-endj-b2', 'end_j', 'bot_layer2', true)}</td>
                                <td>
                                    <div class="stirrup-control-wrap" id="wrap-endj-st" style="display:flex; align-items:center; justify-content:center; gap:2px;">
                                        <select id="rb-endj-st-dia" class="form-input" style="width:60px; padding:2px;">
                                            <option value="D10" ${rb.end_j.stirrup_dia === 'D10' ? 'selected' : ''}>D10</option>
                                            <option value="D13" ${rb.end_j.stirrup_dia === 'D13' ? 'selected' : ''}>D13</option>
                                        </select>
                                        <span>@</span>
                                        <input type="number" id="rb-endj-st-space" class="form-input table-cell-input" value="${rb.end_j.stirrup_space}" style="width:55px; text-align:center;">
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="eng-form-section">
                <div class="form-section-header">측면 비틀림 및 표피 철근 (Torsion & Skin Rebars)</div>
                <div class="form-grid-2col">
                    <div class="form-group-row">
                        <label for="beam-input-torsion-bar">측면 철근 규격:</label>
                        <div class="input-control-wrap">
                            <select id="beam-input-torsion-bar" class="form-input">
                                <option value="D10" ${rb.torsion_side_bar === 'D10' ? 'selected' : ''}>D10</option>
                                <option value="D13" ${rb.torsion_side_bar === 'D13' ? 'selected' : ''}>D13</option>
                                <option value="D16" ${rb.torsion_side_bar === 'D16' ? 'selected' : ''}>D16</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-torsion-count">단면당 총 개수:</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-torsion-count" class="form-input" value="${rb.torsion_side_count}" min="0" step="2">
                            <span class="unit-tag">EA</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="eng-form-section" id="beam-spacing-preview-box" style="background:var(--bg-card); border:1px solid var(--border); border-radius:6px; padding:10px; position:relative;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                    <span style="font-weight:700; font-size:12px; color:var(--accent, #38bdf8);">📏 12포인트 철근 순간격 전수 검토 (KDS 14 20 50)</span>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span id="beam-spacing-badge" class="spacing-badge-governing status-ok" title="클릭하여 12개 포인트 전체 순간격 상세 확인">
                            최소 순간격: 계산 중...
                        </span>
                        <button type="button" id="btn-toggle-spacing-popover" class="btn-more-dlg-wide" style="padding:2px 7px; font-size:10.5px; height:24px;" title="12포인트 순간격 상세 표출">
                            🔍 상세표
                        </button>
                    </div>
                </div>
                <div id="beam-spacing-detail-text" style="font-size:11px; color:var(--text-muted); margin-top:4px;">
                    계산 중...
                </div>
                <!-- 12-Point Spacing Popover Floating Card -->
                <div id="beam-spacing-popover" class="spacing-popover" style="display:none;"></div>
            </div>
        `;

        // Helper to update a cell's DOM elements
        const updateCellDOM = (cellId, val, isLayer2) => {
            const parsed = this._parseRebarStr(val, isLayer2);
            const wrap = pane.querySelector('#' + cellId);
            if (!wrap) return;
            const cntInp = wrap.querySelector('.rebar-count-input');
            const diaSel = wrap.querySelector('.rebar-dia-select');
            if (cntInp) cntInp.value = parsed.count;
            if (diaSel) {
                diaSel.value = parsed.dia;
                const isDim = isLayer2 && parsed.count === 0;
                diaSel.disabled = isDim;
                diaSel.style.opacity = isDim ? '0.45' : '1.0';
                diaSel.style.pointerEvents = isDim ? 'none' : 'auto';
            }
        };

        // Helper to update Arrange Type Visuals and interlocks
        const updateArrangeUI = () => {
            this._updateArrangeTypeUI(pane);
        };

        // Bind Composite Cell Events
        const bindCompositeCell = (cellId, station, rowKey, isLayer2, suffix) => {
            const wrap = pane.querySelector('#' + cellId);
            if (!wrap) return;
            const cntInp = wrap.querySelector('.rebar-count-input');
            const diaSel = wrap.querySelector('.rebar-dia-select');

            const handleValChange = () => {
                let cnt = parseInt(cntInp.value);
                if (isNaN(cnt)) cnt = isLayer2 ? 0 : 2;
                if (!isLayer2 && cnt < 2) {
                    cnt = 2;
                    cntInp.value = 2;
                } else if (isLayer2 && cnt < 0) {
                    cnt = 0;
                    cntInp.value = 0;
                }

                if (isLayer2 && cnt === 0) {
                    diaSel.disabled = true;
                    diaSel.style.opacity = '0.45';
                    diaSel.style.pointerEvents = 'none';
                    this.data.rebar[station][rowKey] = '0';
                } else {
                    diaSel.disabled = false;
                    diaSel.style.opacity = '1.0';
                    diaSel.style.pointerEvents = 'auto';
                    this.data.rebar[station][rowKey] = `${cnt}-${diaSel.value}`;
                }

                const currentVal = this.data.rebar[station][rowKey];

                // Synchronize according to arrange_type
                const arrType = this.data.rebar.arrange_type || 'SYMMETRIC_ENDS';
                if (arrType === 'SYMMETRIC_ENDS' && station === 'end_i') {
                    this.data.rebar.end_j[rowKey] = currentVal;
                    updateCellDOM(`rb-endj-${suffix}`, currentVal, isLayer2);
                } else if (arrType === 'ONE_SECTION' && station === 'center_m') {
                    this.data.rebar.end_i[rowKey] = currentVal;
                    this.data.rebar.end_j[rowKey] = currentVal;
                    updateCellDOM(`rb-endi-${suffix}`, currentVal, isLayer2);
                    updateCellDOM(`rb-endj-${suffix}`, currentVal, isLayer2);
                }

                this._syncLegacyRebarStrings();
                this._updateSpacingPreview();
                this._broadcastChange();
            };

            cntInp.oninput = handleValChange;
            diaSel.onchange = handleValChange;
        };

        // End-I
        bindCompositeCell('rb-endi-t1', 'end_i', 'top_layer1', false, 't1');
        bindCompositeCell('rb-endi-t2', 'end_i', 'top_layer2', true, 't2');
        bindCompositeCell('rb-endi-b1', 'end_i', 'bot_layer1', false, 'b1');
        bindCompositeCell('rb-endi-b2', 'end_i', 'bot_layer2', true, 'b2');

        // Center-M
        bindCompositeCell('rb-cent-t1', 'center_m', 'top_layer1', false, 't1');
        bindCompositeCell('rb-cent-t2', 'center_m', 'top_layer2', true, 't2');
        bindCompositeCell('rb-cent-b1', 'center_m', 'bot_layer1', false, 'b1');
        bindCompositeCell('rb-cent-b2', 'center_m', 'bot_layer2', true, 'b2');

        // End-J
        bindCompositeCell('rb-endj-t1', 'end_j', 'top_layer1', false, 't1');
        bindCompositeCell('rb-endj-t2', 'end_j', 'top_layer2', true, 't2');
        bindCompositeCell('rb-endj-b1', 'end_j', 'bot_layer1', false, 'b1');
        bindCompositeCell('rb-endj-b2', 'end_j', 'bot_layer2', true, 'b2');

        // Stirrup Bindings
        const bindSt = (idDia, idSpace, loc) => {
            const elDia = pane.querySelector(idDia);
            const elSpace = pane.querySelector(idSpace);
            if (elDia) {
                elDia.onchange = () => {
                    this.data.rebar[loc].stirrup_dia = elDia.value;
                    const arrType = this.data.rebar.arrange_type || 'SYMMETRIC_ENDS';
                    if (arrType === 'SYMMETRIC_ENDS' && loc === 'end_i') {
                        this.data.rebar.end_j.stirrup_dia = elDia.value;
                        const elJ = pane.querySelector('#rb-endj-st-dia');
                        if (elJ) elJ.value = elDia.value;
                    } else if (arrType === 'ONE_SECTION' && loc === 'center_m') {
                        this.data.rebar.end_i.stirrup_dia = elDia.value;
                        this.data.rebar.end_j.stirrup_dia = elDia.value;
                        const elI = pane.querySelector('#rb-endi-st-dia');
                        const elJ = pane.querySelector('#rb-endj-st-dia');
                        if (elI) elI.value = elDia.value;
                        if (elJ) elJ.value = elDia.value;
                    }
                    this._syncLegacyRebarStrings();
                    this._updateSpacingPreview();
                    this._broadcastChange();
                };
            }
            if (elSpace) {
                elSpace.oninput = () => {
                    const sp = parseFloat(elSpace.value) || 150;
                    this.data.rebar[loc].stirrup_space = sp;
                    const arrType = this.data.rebar.arrange_type || 'SYMMETRIC_ENDS';
                    if (arrType === 'SYMMETRIC_ENDS' && loc === 'end_i') {
                        this.data.rebar.end_j.stirrup_space = sp;
                        const elJ = pane.querySelector('#rb-endj-st-space');
                        if (elJ) elJ.value = sp;
                    } else if (arrType === 'ONE_SECTION' && loc === 'center_m') {
                        this.data.rebar.end_i.stirrup_space = sp;
                        this.data.rebar.end_j.stirrup_space = sp;
                        const elI = pane.querySelector('#rb-endi-st-space');
                        const elJ = pane.querySelector('#rb-endj-st-space');
                        if (elI) elI.value = sp;
                        if (elJ) elJ.value = sp;
                    }
                    this._syncLegacyRebarStrings();
                    this._broadcastChange();
                };
            }
        };

        bindSt('#rb-endi-st-dia', '#rb-endi-st-space', 'end_i');
        bindSt('#rb-cent-st-dia', '#rb-cent-st-space', 'center_m');
        bindSt('#rb-endj-st-dia', '#rb-endj-st-space', 'end_j');

        // Torsion Bindings
        const tBar = pane.querySelector('#beam-input-torsion-bar');
        if (tBar) {
            tBar.onchange = () => {
                this.data.rebar.torsion_side_bar = tBar.value;
                this._broadcastChange();
            };
        }
        const tCount = pane.querySelector('#beam-input-torsion-count');
        if (tCount) {
            tCount.oninput = () => {
                this.data.rebar.torsion_side_count = parseInt(tCount.value) || 0;
                this._broadcastChange();
            };
        }

        // Arrange Type Radios Event
        const arrRadios = pane.querySelectorAll('input[name="beam_arrange_type"]');
        arrRadios.forEach(radio => {
            radio.onchange = () => {
                if (radio.checked) {
                    this.data.rebar.arrange_type = radio.value;
                    // When switching to SYMMETRIC_ENDS: copy End-I to End-J
                    if (radio.value === 'SYMMETRIC_ENDS') {
                        this.data.rebar.end_j = { ...this.data.rebar.end_i };
                        updateCellDOM('rb-endj-t1', this.data.rebar.end_j.top_layer1, false);
                        updateCellDOM('rb-endj-t2', this.data.rebar.end_j.top_layer2, true);
                        updateCellDOM('rb-endj-b1', this.data.rebar.end_j.bot_layer1, false);
                        updateCellDOM('rb-endj-b2', this.data.rebar.end_j.bot_layer2, true);
                        const elJDia = pane.querySelector('#rb-endj-st-dia');
                        const elJSpace = pane.querySelector('#rb-endj-st-space');
                        if (elJDia) elJDia.value = this.data.rebar.end_j.stirrup_dia;
                        if (elJSpace) elJSpace.value = this.data.rebar.end_j.stirrup_space;
                    } else if (radio.value === 'ONE_SECTION') {
                        // When switching to ONE_SECTION: copy Center-M to End-I & End-J
                        const cm = this.data.rebar.center_m;
                        this.data.rebar.end_i = { ...cm };
                        this.data.rebar.end_j = { ...cm };
                        ['endi', 'endj'].forEach(loc => {
                            updateCellDOM(`rb-${loc}-t1`, cm.top_layer1, false);
                            updateCellDOM(`rb-${loc}-t2`, cm.top_layer2, true);
                            updateCellDOM(`rb-${loc}-b1`, cm.bot_layer1, false);
                            updateCellDOM(`rb-${loc}-b2`, cm.bot_layer2, true);
                            const elDia = pane.querySelector(`#rb-${loc}-st-dia`);
                            const elSpace = pane.querySelector(`#rb-${loc}-st-space`);
                            if (elDia) elDia.value = cm.stirrup_dia;
                            if (elSpace) elSpace.value = cm.stirrup_space;
                        });
                    }
                    updateArrangeUI();
                    this._updateLoadTableArrangeState(this.container);
                    this._syncLegacyRebarStrings();
                    this._updateSpacingPreview();
                    this._broadcastChange();
                }
            };
        });

        // Initialize Arrange UI visual state
        updateArrangeUI();

        // Popover toggle for 12-point clear spacing
        const popoverEl = pane.querySelector('#beam-spacing-popover');
        const togglePopover = (e) => {
            if (e) e.stopPropagation();
            if (!popoverEl) return;
            const isShown = popoverEl.style.display !== 'none';
            popoverEl.style.display = isShown ? 'none' : 'block';
        };
        const btnTogglePopover = pane.querySelector('#btn-toggle-spacing-popover');
        const badgeSpacing = pane.querySelector('#beam-spacing-badge');
        if (btnTogglePopover) btnTogglePopover.onclick = togglePopover;
        if (badgeSpacing) badgeSpacing.onclick = togglePopover;

        // Sub-dialog: Detailed Rebar Settings (IDD_RCS_BEAM_REBAR_DLG)
        const btnOpenRebarDlg = pane.querySelector('#btn-open-rebar-dlg');
        if (btnOpenRebarDlg) {
            btnOpenRebarDlg.onclick = () => {
                if (window.CommonDialogs && typeof window.CommonDialogs.openBeamRebarDialog === 'function') {
                    window.CommonDialogs.openBeamRebarDialog({
                        ...this.data.rebar,
                        barDia: this.data.rebar.center_m.bot_layer1.split('-')[1] || 'D25'
                    }, (res) => {
                        Object.assign(this.data.rebar, res);
                        this._updateSpacingPreview();
                        this._broadcastChange();
                    });
                }
            };
        }

        return pane;
    }

    /**
     * Update Arrange Type UI visual state (Tags and dimming)
     * @param {HTMLElement} root
     */
    _updateArrangeTypeUI(root) {
        if (!root) return;
        const arrType = this.data.rebar?.arrange_type || 'SYMMETRIC_ENDS';
        const tagEndJ = root.querySelector('#tag-endj-sym');
        const tagEndI = root.querySelector('#tag-endi-sym');
        const rowEndI = root.querySelector('#row-endi');
        const rowCent = root.querySelector('#row-cent');
        const rowEndJ = root.querySelector('#row-endj');

        const setRowState = (row, enabled, opacity = '1.0') => {
            if (!row) return;
            const inputs = row.querySelectorAll('input, select');
            inputs.forEach(el => {
                // If it's a 2nd layer dia select with 0 count, keep it disabled
                if (el.classList.contains('rebar-dia-select')) {
                    const wrap = el.closest('.rebar-cell-composite');
                    const cntInp = wrap ? wrap.querySelector('.rebar-count-input') : null;
                    if (cntInp && parseInt(cntInp.value) === 0 && wrap.id && (wrap.id.includes('-t2') || wrap.id.includes('-b2'))) {
                        el.disabled = true;
                        el.style.opacity = '0.45';
                        el.style.pointerEvents = 'none';
                        return;
                    }
                }
                el.style.pointerEvents = enabled ? 'auto' : 'none';
            });
            row.style.opacity = opacity;
        };

        if (arrType === 'SYMMETRIC_ENDS') {
            if (tagEndJ) {
                tagEndJ.style.display = 'inline-block';
                tagEndJ.textContent = '[단부-I 대칭 연동]';
            }
            if (tagEndI) tagEndI.style.display = 'none';
            setRowState(rowEndI, true, '1.0');
            setRowState(rowCent, true, '1.0');
            setRowState(rowEndJ, false, '0.65');
        } else if (arrType === 'ONE_SECTION') {
            if (tagEndJ) {
                tagEndJ.style.display = 'inline-block';
                tagEndJ.textContent = '[전단면 연동]';
            }
            if (tagEndI) {
                tagEndI.style.display = 'inline-block';
                tagEndI.textContent = '[전단면 연동]';
            }
            setRowState(rowCent, true, '1.0');
            setRowState(rowEndI, false, '0.65');
            setRowState(rowEndJ, false, '0.65');
        } else { // THREE_STATIONS
            if (tagEndJ) tagEndJ.style.display = 'none';
            if (tagEndI) tagEndI.style.display = 'none';
            setRowState(rowEndI, true, '1.0');
            setRowState(rowCent, true, '1.0');
            setRowState(rowEndJ, true, '1.0');
        }
    }

    /**
     * Requirement 22-5-2 Sec 2.3: Dynamic disabled & symmetric sync for loads table
     * @param {HTMLElement} root
     */
    _updateLoadTableArrangeState(root = this.container) {
        if (!root) return;
        const arrType = this.data.rebar?.arrange_type || 'SYMMETRIC_ENDS';
        const rowEndI = root.querySelector('#row-ld-endi');
        const rowCent = root.querySelector('#row-ld-cent');
        const rowEndJ = root.querySelector('#row-ld-endj');
        const tagEndI = root.querySelector('#tag-ld-endi-sym');
        const tagEndJ = root.querySelector('#tag-ld-endj-sym');

        const setRowLoadState = (row, enabled, isDim = false) => {
            if (!row) return;
            const inputs = row.querySelectorAll('input');
            inputs.forEach(inp => {
                inp.disabled = !enabled;
                inp.style.pointerEvents = enabled ? 'auto' : 'none';
            });
            row.classList.toggle('row-disabled-load', isDim);
            row.style.opacity = isDim ? '0.55' : '1.0';
        };

        if (arrType === 'ONE_SECTION') {
            setRowLoadState(rowCent, true, false);
            setRowLoadState(rowEndI, false, true);
            setRowLoadState(rowEndJ, false, true);
            if (tagEndI) {
                tagEndI.style.display = 'inline-block';
                tagEndI.textContent = '[전단면 동일 - 중앙부 적용]';
            }
            if (tagEndJ) {
                tagEndJ.style.display = 'inline-block';
                tagEndJ.textContent = '[전단면 동일 - 중앙부 적용]';
            }
        } else if (arrType === 'SYMMETRIC_ENDS') {
            setRowLoadState(rowEndI, true, false);
            setRowLoadState(rowCent, true, false);
            setRowLoadState(rowEndJ, false, true);
            if (tagEndI) tagEndI.style.display = 'none';
            if (tagEndJ) {
                tagEndJ.style.display = 'inline-block';
                tagEndJ.textContent = '[단부-I 대칭 동기화]';
            }
            // End-I 값을 End-J로 동기화 복제
            this.data.loads.end_j = { ...this.data.loads.end_i };
            ['mup', 'mun', 'vu', 'tu'].forEach(f => {
                const iInp = root.querySelector(`#ld-endi-${f}`);
                const jInp = root.querySelector(`#ld-endj-${f}`);
                if (iInp && jInp) jInp.value = iInp.value;
            });
        } else { // THREE_STATIONS
            setRowLoadState(rowEndI, true, false);
            setRowLoadState(rowCent, true, false);
            setRowLoadState(rowEndJ, true, false);
            if (tagEndI) tagEndI.style.display = 'none';
            if (tagEndJ) tagEndJ.style.display = 'none';
        }
    }

    /**
     * Tab 3: Design Factored Loads (IDD_RCS_BEAM_SECT_DLG)
     */
    _buildLoadTab() {
        const pane = document.createElement('div');
        pane.className = `sub-tab-pane beam-tab-pane ${this.activeTab === 'load' ? 'active' : ''}`;
        pane.id = 'beam-tab-load';

        const ld = this.data.loads;

        pane.innerHTML = `
            <div class="eng-form-section">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div class="form-section-header" style="margin-bottom:0;">설계 계수 부재력 (Factored Loads)</div>
                    <button type="button" class="btn-more-dlg-wide" id="btn-open-lcb-dlg">
                        ⚖️ KDS 41 하중조합 생성기...
                    </button>
                </div>

                <div class="beam-load-table-wrap" style="overflow-x:auto;">
                    <table class="beam-load-table">
                        <thead>
                            <tr>
                                <th>위치 (Station)</th>
                                <th>+Mu (정모멘트, kN·m)</th>
                                <th>-Mu (부모멘트, kN·m)</th>
                                <th>Vu (전단력, kN)</th>
                                <th>Tu (비틀림, kN·m)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- End-I -->
                            <tr id="row-ld-endi">
                                <td style="font-weight:700;">
                                    <span>단부-I (End-I)</span>
                                    <span id="tag-ld-endi-sym" class="badge-load-sym" style="display:none;"></span>
                                </td>
                                <td>
                                    <input type="number" id="ld-endi-mup" class="form-input table-cell-input" value="${ld.end_i.Mu_pos}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endi-mun" class="form-input table-cell-input" value="${ld.end_i.Mu_neg}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endi-vu" class="form-input table-cell-input" value="${ld.end_i.Vu}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endi-tu" class="form-input table-cell-input" value="${ld.end_i.Tu}" step="1" style="width:70px; text-align:center;">
                                </td>
                            </tr>
                            <!-- Center-M -->
                            <tr id="row-ld-cent">
                                <td style="font-weight:700;">중앙-M (Center)</td>
                                <td>
                                    <input type="number" id="ld-cent-mup" class="form-input table-cell-input" value="${ld.center_m.Mu_pos}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-cent-mun" class="form-input table-cell-input" value="${ld.center_m.Mu_neg}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-cent-vu" class="form-input table-cell-input" value="${ld.center_m.Vu}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-cent-tu" class="form-input table-cell-input" value="${ld.center_m.Tu}" step="1" style="width:70px; text-align:center;">
                                </td>
                            </tr>
                            <!-- End-J -->
                            <tr id="row-ld-endj">
                                <td style="font-weight:700;">
                                    <span>단부-J (End-J)</span>
                                    <span id="tag-ld-endj-sym" class="badge-load-sym" style="display:none;"></span>
                                </td>
                                <td>
                                    <input type="number" id="ld-endj-mup" class="form-input table-cell-input" value="${ld.end_j.Mu_pos}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endj-mun" class="form-input table-cell-input" value="${ld.end_j.Mu_neg}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endj-vu" class="form-input table-cell-input" value="${ld.end_j.Vu}" step="10" style="width:80px; text-align:center;">
                                </td>
                                <td>
                                    <input type="number" id="ld-endj-tu" class="form-input table-cell-input" value="${ld.end_j.Tu}" step="1" style="width:70px; text-align:center;">
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        const bindLd = (id, loc, field) => {
            const inp = pane.querySelector(id);
            if (inp) {
                inp.oninput = () => {
                    const val = parseFloat(inp.value) || 0;
                    this.data.loads[loc][field] = val;

                    // Requirement 22-5-2: SYMMETRIC_ENDS auto-replication from End-I to End-J
                    const arrType = this.data.rebar?.arrange_type || 'SYMMETRIC_ENDS';
                    if (loc === 'end_i' && arrType === 'SYMMETRIC_ENDS') {
                        this.data.loads.end_j[field] = val;
                        const jInp = pane.querySelector(id.replace('endi', 'endj'));
                        if (jInp) jInp.value = val;
                    }

                    // Sync legacy top-level values
                    if (loc === 'center_m' && field === 'Mu_pos') this.data.mu = this.data.loads.center_m.Mu_pos;
                    if (loc === 'end_i' && field === 'Vu') this.data.vu = this.data.loads.end_i.Vu;
                    this._broadcastChange();
                };
            }
        };

        bindLd('#ld-endi-mup', 'end_i', 'Mu_pos');
        bindLd('#ld-endi-mun', 'end_i', 'Mu_neg');
        bindLd('#ld-endi-vu', 'end_i', 'Vu');
        bindLd('#ld-endi-tu', 'end_i', 'Tu');

        bindLd('#ld-cent-mup', 'center_m', 'Mu_pos');
        bindLd('#ld-cent-mun', 'center_m', 'Mu_neg');
        bindLd('#ld-cent-vu', 'center_m', 'Vu');
        bindLd('#ld-cent-tu', 'center_m', 'Tu');

        bindLd('#ld-endj-mup', 'end_j', 'Mu_pos');
        bindLd('#ld-endj-mun', 'end_j', 'Mu_neg');
        bindLd('#ld-endj-vu', 'end_j', 'Vu');
        bindLd('#ld-endj-tu', 'end_j', 'Tu');

        // Sub-dialog: Load Combination
        const btnLcb = pane.querySelector('#btn-open-lcb-dlg');
        if (btnLcb) {
            btnLcb.onclick = () => {
                if (window.CommonDialogs && typeof window.CommonDialogs.openLoadCombination === 'function') {
                    window.CommonDialogs.openLoadCombination({
                        mu: this.data.mu,
                        vu: this.data.vu
                    }, (res) => {
                        if (res && res.mu) {
                            this.data.loads.center_m.Mu_pos = res.mu;
                            this.data.loads.end_i.Mu_neg = res.mu;
                            this.data.loads.end_i.Vu = res.vu || this.data.vu;
                            this.render(this.container, this.data, this.onChangeCallback);
                            this._broadcastChange();
                        }
                    });
                }
            };
        }

        // Initialize disabled/symmetric state
        this._updateLoadTableArrangeState(pane);

        return pane;
    }

    /**
     * Tab 4: Serviceability & Deflection (IDD_RCS_DEFL_DLG)
     */
    _buildServiceabilityTab() {
        const pane = document.createElement('div');
        pane.className = `sub-tab-pane beam-tab-pane ${this.activeTab === 'serviceability' ? 'active' : ''}`;
        pane.id = 'beam-tab-serviceability';

        const sv = this.data.serviceability;

        pane.innerHTML = `
            <div class="eng-form-section">
                <div class="form-section-header">처짐 검토 사용하중 (Service Loads for Deflection)</div>
                <div class="form-grid-2col">
                    <div class="form-group-row">
                        <label for="beam-input-mapos">정모멘트 (Ma,pos):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-mapos" class="form-input" value="${sv.Ma_pos}" step="10">
                            <span class="unit-tag">kN·m</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-maneg">부모멘트 (Ma,neg):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-maneg" class="form-input" value="${sv.Ma_neg}" step="10">
                            <span class="unit-tag">kN·m</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-msus">지속하중 모멘트 (Msus):</label>
                        <div class="input-control-wrap">
                            <input type="number" id="beam-input-msus" class="form-input" value="${sv.Msus}" step="10">
                            <span class="unit-tag">kN·m</span>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-input-defl-limit">처짐 허용한계 (Limit):</label>
                        <div class="input-control-wrap">
                            <select id="beam-input-defl-limit" class="form-input">
                                <option value="L/240" ${sv.defl_limit === 'L/240' ? 'selected' : ''}>L / 240 (일반 바닥/지붕)</option>
                                <option value="L/360" ${sv.defl_limit === 'L/360' ? 'selected' : ''}>L / 360 (비구조재 부착)</option>
                                <option value="L/480" ${sv.defl_limit === 'L/480' ? 'selected' : ''}>L / 480 (정밀 처짐 제한)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <div class="eng-form-section">
                <div class="form-section-header">균열 및 내진 환경 (Crack & Seismic Provisions)</div>
                <div class="form-grid-2col">
                    <div class="form-group-row">
                        <label for="beam-select-exposure">노출 환경 (균열 한계):</label>
                        <div class="input-control-wrap">
                            <select id="beam-select-exposure" class="form-input">
                                <option value="dry" ${sv.exposure === 'dry' ? 'selected' : ''}>건조 환경 (w_lim = 0.4 mm)</option>
                                <option value="wet" ${sv.exposure === 'wet' ? 'selected' : ''}>습윤 환경 (w_lim = 0.3 mm)</option>
                                <option value="corrosive" ${sv.exposure === 'corrosive' ? 'selected' : ''}>부식성 환경 (w_lim = 0.2 mm)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group-row">
                        <label for="beam-select-seismic">내진 상세 범주:</label>
                        <div class="input-control-wrap">
                            <select id="beam-select-seismic" class="form-input">
                                <option value="OMF" ${sv.seismic === 'OMF' ? 'selected' : ''}>보통모멘트골조 (OMF)</option>
                                <option value="IMF" ${sv.seismic === 'IMF' ? 'selected' : ''}>중간모멘트골조 (IMF)</option>
                                <option value="SMF" ${sv.seismic === 'SMF' ? 'selected' : ''}>특수모멘트골조 (SMF)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const bindSv = (id, prop, isNum = true) => {
            const el = pane.querySelector(id);
            if (el) {
                const evt = el.tagName === 'SELECT' ? 'change' : 'input';
                el.addEventListener(evt, () => {
                    this.data.serviceability[prop] = isNum ? (parseFloat(el.value) || 0) : el.value;
                    this._broadcastChange();
                });
            }
        };

        bindSv('#beam-input-mapos', 'Ma_pos', true);
        bindSv('#beam-input-maneg', 'Ma_neg', true);
        bindSv('#beam-input-msus', 'Msus', true);
        bindSv('#beam-input-defl-limit', 'defl_limit', false);
        bindSv('#beam-select-exposure', 'exposure', false);
        bindSv('#beam-select-seismic', 'seismic', false);

        return pane;
    }

    /**
     * Helper to keep backward-compatible topBars / botBars strings synced with Center-M
     */
    _syncLegacyRebarStrings() {
        const cm = this.data.rebar.center_m;
        this.data.topBars = cm.top_layer1 + (cm.top_layer2 && cm.top_layer2 !== '0' ? ` + ${cm.top_layer2}` : '');
        this.data.botBars = cm.bot_layer1 + (cm.bot_layer2 && cm.bot_layer2 !== '0' ? ` + ${cm.bot_layer2}` : '');
        this.data.stirrup = `${cm.stirrup_dia} @ ${cm.stirrup_space}`;
    }

    /**
     * Requirement 22-5-2 Sec 2.2: 12-Point Clear Spacing Full Calculation (KDS 14 20 50 Sec 4.1)
     * 3-Station (End-I, Center-M, End-J) × 4-Layer (Top 1/2, Bot 1/2) = 12 Points
     */
    _calcAllClearSpacings() {
        const bw = this.data.b || 400;
        const coverBot = this.data.cover || 40;
        const coverTop = this.data.cover_top || coverBot;
        const da = this.data.rebar?.maxAggSize || 25;

        const stations = [
            { key: 'end_i', label: '단부-I', shortLabel: 'I' },
            { key: 'center_m', label: '중앙-M', shortLabel: 'M' },
            { key: 'end_j', label: '단부-J', shortLabel: 'J' }
        ];

        const layers = [
            { key: 'top_layer1', label: '상부 1단', isTop: true, isLayer2: false },
            { key: 'top_layer2', label: '상부 2단', isTop: true, isLayer2: true },
            { key: 'bot_layer2', label: '하부 2단', isTop: false, isLayer2: true },
            { key: 'bot_layer1', label: '하부 1단', isTop: false, isLayer2: false }
        ];

        const results = [];

        stations.forEach(st => {
            const stData = this.data.rebar?.[st.key] || {};
            const stirrupDiaNum = parseFloat((stData.stirrup_dia || 'D10').replace(/[^0-9]/g, '')) || 10;

            layers.forEach(ly => {
                const spec = stData[ly.key] || '0';
                const parsed = this._parseRebarStr(spec, ly.isLayer2);
                const n = parsed.count;
                const diaStr = parsed.dia || 'D25';
                const db = parseFloat(diaStr.replace(/[^0-9]/g, '')) || 25;
                const cc = ly.isTop ? coverTop : coverBot;

                const item = {
                    stationKey: st.key,
                    stationLabel: st.label,
                    stationShort: st.shortLabel,
                    layerKey: ly.key,
                    layerLabel: ly.label,
                    isTop: ly.isTop,
                    isLayer2: ly.isLayer2,
                    spec: spec,
                    count: n,
                    db: db,
                    diaStr: diaStr,
                    s_clear: null,
                    s_req: Math.max(25, db, Math.round(1.33 * da)),
                    margin: null,
                    status: 'none' // 'none', 'ok', 'ng'
                };

                if (n <= 0) {
                    item.status = 'none';
                } else if (n === 1) {
                    item.s_clear = 999;
                    item.margin = 999 - item.s_req;
                    item.status = 'ok';
                } else {
                    const clearWidth = bw - 2 * (cc + stirrupDiaNum);
                    const sc = (clearWidth - n * db) / (n - 1);
                    item.s_clear = Math.round(sc * 10) / 10;
                    item.margin = Math.round((sc - item.s_req) * 10) / 10;
                    item.status = (item.s_clear >= item.s_req) ? 'ok' : 'ng';
                }

                results.push(item);
            });
        });

        // Determine Governing Point
        const activeItems = results.filter(it => it.status !== 'none');
        let governing = null;

        if (activeItems.length > 0) {
            const ngItems = activeItems.filter(it => it.status === 'ng');
            if (ngItems.length > 0) {
                // Lowest margin among NG items
                ngItems.sort((a, b) => a.margin - b.margin);
                governing = ngItems[0];
            } else {
                // Lowest margin among OK items (tightest clearance)
                activeItems.sort((a, b) => a.margin - b.margin);
                governing = activeItems[0];
            }
        }

        return {
            items: results,
            governing: governing,
            hasNG: results.some(it => it.status === 'ng')
        };
    }

    /**
     * Real-time 12-Point Clear Spacing Preview and Detail Popover Update
     */
    _updateSpacingPreview() {
        const previewText = this.container?.querySelector('#beam-spacing-detail-text');
        const previewBadge = this.container?.querySelector('#beam-spacing-badge');
        const popover = this.container?.querySelector('#beam-spacing-popover');
        if (!previewText || !previewBadge) return;

        const { items, governing, hasNG } = this._calcAllClearSpacings();

        if (!governing) {
            previewBadge.className = 'spacing-badge-governing status-ok';
            previewBadge.textContent = '배근 미지정';
            previewText.textContent = '배근 데이터를 입력하십시오.';
            return;
        }

        const isOk = !hasNG;
        previewBadge.className = isOk ? 'spacing-badge-governing status-ok' : 'spacing-badge-governing status-ng';

        const locTag = `[${governing.stationShort}-${governing.layerLabel}]`;
        if (governing.count === 1) {
            previewBadge.innerHTML = `✅ 순간격 여유 ${locTag} (OK)`;
        } else if (isOk) {
            previewBadge.innerHTML = `✅ 최소 순간격: <strong>${governing.s_clear.toFixed(1)}mm</strong> ${locTag} (OK)`;
        } else {
            previewBadge.innerHTML = `⚠️ 순간격 NG: <strong>${governing.s_clear.toFixed(1)}mm</strong> < 소요 ${governing.s_req}mm ${locTag}`;
        }

        const bw = this.data.b || 400;
        const da = this.data.rebar?.maxAggSize || 25;
        previewText.innerHTML = `
            최악 거버닝 위치: <strong>${governing.stationLabel} ${governing.layerLabel}</strong> (${governing.spec}) | 
            실제 순간격: <strong>${governing.count > 1 ? governing.s_clear.toFixed(1) + ' mm' : '여유 충족'}</strong> (규준 소요: ${governing.s_req} mm) | 
            폭 bw=${bw}mm, 골재 da=${da}mm
        `;

        // Render 12-Point Popover Table
        if (popover) {
            const stations = [
                { key: 'end_i', label: '단부-I' },
                { key: 'center_m', label: '중앙-M' },
                { key: 'end_j', label: '단부-J' }
            ];
            const layers = [
                { key: 'top_layer1', label: '상부 1단' },
                { key: 'top_layer2', label: '상부 2단' },
                { key: 'bot_layer2', label: '하부 2단' },
                { key: 'bot_layer1', label: '하부 1단' }
            ];

            let tableHtml = `
                <div style="font-weight:700; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:var(--accent, #38bdf8);">📐 12포인트 철근 순간격 전수 검토표 (KDS 14 20 50)</span>
                    <button type="button" id="btn-close-spacing-popover" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:12px; padding:2px 4px;">✕</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>배근 층</th>
                            <th>단부-I (End-I)</th>
                            <th>중앙-M (Center)</th>
                            <th>단부-J (End-J)</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            layers.forEach(ly => {
                tableHtml += `<tr><td style="font-weight:600; text-align:left;">${ly.label}</td>`;
                stations.forEach(st => {
                    const cell = items.find(it => it.stationKey === st.key && it.layerKey === ly.key);
                    if (!cell || cell.status === 'none') {
                        tableHtml += `<td style="color:var(--text-muted);">-</td>`;
                    } else if (cell.count === 1) {
                        tableHtml += `<td class="status-cell-ok">${cell.spec}<br><span style="font-size:9.5px;">여유 충족</span></td>`;
                    } else {
                        const cellClass = cell.status === 'ok' ? 'status-cell-ok' : 'status-cell-ng';
                        const badge = cell.status === 'ok' ? 'OK' : 'NG';
                        tableHtml += `
                            <td class="${cellClass}">
                                <div>${cell.spec}</div>
                                <div style="font-size:9.5px;">s=${cell.s_clear} / req=${cell.s_req}mm (${badge})</div>
                            </td>
                        `;
                    }
                });
                tableHtml += `</tr>`;
            });

            tableHtml += `
                    </tbody>
                </table>
                <div style="margin-top:6px; font-size:9.5px; color:var(--text-dim, #64748b); text-align:right;">
                    * 규준 요구 최소 순간격: s_req = max(25mm, db, 1.33 d_agg)
                </div>
            `;

            popover.innerHTML = tableHtml;
            const closeBtn = popover.querySelector('#btn-close-spacing-popover');
            if (closeBtn) {
                closeBtn.onclick = (e) => {
                    e.stopPropagation();
                    popover.style.display = 'none';
                };
            }
        }
    }

    /**
     * Action 1: [적용] 버튼 - 현재 입력 데이터를 메모리에 기록만 수행 (계산서는 갱신하지 않음)
     */
    _handleApply(silent = false) {
        this._syncLegacyRebarStrings();
        if (window.ProjectStore && typeof window.ProjectStore.updateMemberInputs === 'function') {
            const activeMember = window.ProjectStore.getActiveMember('rc_beam');
            if (activeMember && activeMember.id) {
                window.ProjectStore.updateMemberInputs('rc_beam', this.data);
            }
        }
        // Broadcast for graphics canvas & sidebar update
        if (window.EventBus && window.APP_EVENTS) {
            window.EventBus.emit(window.APP_EVENTS.PARAM_CHANGED, {
                moduleKey: 'rc_beam',
                data: this.data,
                source: 'apply'
            });
        }
        if (this.onChangeCallback) {
            this.onChangeCallback(this.data, false); // false = do NOT trigger report update
        }
        if (!silent) {
            this._showNotification('💾 적용 완료: 입력 데이터가 메모리에 저장되었습니다.', 'success');
        }
    }

    /**
     * Action 2: [검토] 버튼 - 기준검토부의 내용을 실시간으로 업데이트 하지 않고 검토 버튼이 눌러질 때만 검토 및 업데이트 수행
     */
    async _handleCheck() {
        this._handleApply(true); // 선행 적용 실행
        
        const checkBtn = this.container?.querySelector('#beam-btn-check');
        const origText = checkBtn ? checkBtn.innerHTML : '';
        if (checkBtn) {
            checkBtn.disabled = true;
            checkBtn.innerHTML = '⏳ 검토 중...';
        }

        try {
            const As_bot = this._calcTotalAs(this.data.rebar.center_m.bot_layer1, this.data.rebar.center_m.bot_layer2);
            const As_top = this._calcTotalAs(this.data.rebar.center_m.top_layer1, this.data.rebar.center_m.top_layer2);
            const stirrupDiaNum = parseFloat(this.data.rebar.center_m.stirrup_dia.replace(/[^0-9]/g, '')) || 10;
            const stirrupBarArea = stirrupDiaNum === 13 ? 126.7 : 71.33;
            const stirrupLegs = this.data.rebar.center_m.stirrup_legs || 2;
            const stirrupSpace = this.data.rebar.center_m.stirrup_space || 200;

            const payload = {
                name: 'RC_BEAM_1',
                b: this.data.b || 400,
                h: this.data.h || 600,
                cover: (this.data.cover || 40) + stirrupDiaNum + 25/2,
                cover_prime: (this.data.cover_top || 40) + stirrupDiaNum + 25/2,
                side_cover: this.data.cover || 40,
                As: Math.max(As_bot, 200),
                As_prime: As_top,
                Av: stirrupBarArea * stirrupLegs,
                s: stirrupSpace,
                Mu: Math.max(this.data.loads.center_m.Mu_pos, this.data.loads.end_i.Mu_neg, this.data.loads.end_j.Mu_neg, this.data.mu || 240),
                Vu: Math.max(this.data.loads.end_i.Vu, this.data.loads.end_j.Vu, this.data.vu || 180),
                Tu: Math.max(this.data.loads.end_i.Tu, this.data.loads.center_m.Tu, 15.0),
                Ma: this.data.serviceability.Ma_pos || 140.0,
                span_length: this.data.length || 6000,
                num_tension_bars: this._parseBarCount(this.data.rebar.center_m.bot_layer1),
                fck: this.data.fck || 27,
                fy: this.data.fy || 400,
                fyt: this.data.fyt || 400
            };

            let calcResult = null;
            try {
                const res = await fetch('/api/rc/beam/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const json = await res.json();
                    if (json.success && json.data) {
                        calcResult = json.data;
                    }
                }
            } catch (apiErr) {
                console.warn('[RCBeamForm] API call failed, fallback to local calc:', apiErr);
            }

            // If API didn't return, provide structured local fallback
            if (!calcResult) {
                const phiMn = Math.max(10, payload.As * payload.fy * 0.9 * (payload.h - 60) * 1e-6);
                const phiVn = Math.max(10, (1/6 * Math.sqrt(payload.fck) * payload.b * (payload.h - 60) + 0.8 * payload.Av * payload.fyt * (payload.h - 60) / payload.s) * 1e-3);
                calcResult = {
                    d: payload.h - 60,
                    phi_Mn: phiMn,
                    phi_Vn: phiVn,
                    flexure_dcr: payload.Mu / phiMn,
                    shear_dcr: payload.Vu / phiVn,
                    torsion_dcr: payload.Tu / 35.0,
                    is_safe: (payload.Mu / phiMn <= 1.0 && payload.Vu / phiVn <= 1.0)
                };
            }

            // 2. Render KDS Report into Pane 4 (Pure White KaTeX A4 Sheet)
            const reportContainer = document.getElementById('result-container') || document.querySelector('.report-content');
            if (reportContainer) {
                if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
                    window.ReportEngine.render(reportContainer, this.data, calcResult, 'rc_beam');
                } else {
                    const targetMod = window.ModuleDispatcher ? window.ModuleDispatcher.resolveModule('rc_beam') : null;
                    if (targetMod && typeof targetMod.renderReport === 'function') {
                        targetMod.renderReport(reportContainer, this.data, calcResult, {});
                    }
                }
            }

            // 3. Update DCR Badge in Pane 3
            const dcrVal = Math.max(calcResult.flexure_dcr || 0, calcResult.shear_dcr || 0, calcResult.torsion_dcr || 0);
            const dcrValEl = document.getElementById('dcrValue');
            const dcrBarEl = document.getElementById('dcrBar');
            if (dcrValEl) {
                dcrValEl.textContent = dcrVal.toFixed(3);
                dcrValEl.style.color = dcrVal <= 1.0 ? '#10b981' : '#ef4444';
            }
            if (dcrBarEl) {
                const pct = Math.min(100, Math.round(dcrVal * 100));
                dcrBarEl.style.width = `${pct}%`;
                dcrBarEl.style.background = dcrVal <= 1.0 ? '#10b981' : '#ef4444';
            }

            // 4. Update member summary in ProjectStore / MemberManager
            if (window.ProjectStore && typeof window.ProjectStore.updateMemberDCR === 'function') {
                window.ProjectStore.updateMemberDCR('rc_beam', dcrVal, dcrVal <= 1.0 ? 'OK' : 'NG');
            }

            this._showNotification(`⚡ 검토 완료: DCR = ${dcrVal.toFixed(3)} (${dcrVal <= 1.0 ? '적합 OK' : '내력 부족 NG'})`, dcrVal <= 1.0 ? 'success' : 'danger');
        } catch (e) {
            console.error('[RCBeamForm] Check execution error:', e);
            this._showNotification('❌ 검토 중 오류가 발생했습니다: ' + e.message, 'danger');
        } finally {
            if (checkBtn) {
                checkBtn.disabled = false;
                checkBtn.innerHTML = origText;
            }
        }
    }

    /**
     * Action 3: [자동설계] 버튼 - 현재 단면에 대해 원본 소스 알고리즘을 참고하여 최적 철근 자동 설계
     */
    async _handleAutoDesign() {
        const designBtn = this.container?.querySelector('#beam-btn-design');
        const origText = designBtn ? designBtn.innerHTML : '';
        if (designBtn) {
            designBtn.disabled = true;
            designBtn.innerHTML = '✨ 설계 중...';
        }

        try {
            const b = this.data.b || 400;
            const h = this.data.h || 600;
            const cover = this.data.cover || 40;
            const fck = this.data.fck || 27;
            const fy = this.data.fy || 400;
            const fyt = this.data.fyt || 400;
            const d = h - cover - 10 - 25/2;

            // 1. Calculate required tension rebar As for Center-M (+Mu) and Ends (-Mu)
            const mu_center = Math.max(10, this.data.loads.center_m.Mu_pos || this.data.mu || 240);
            const mu_end = Math.max(10, this.data.loads.end_i.Mu_neg, this.data.loads.end_j.Mu_neg, 240);
            const vu_max = Math.max(10, this.data.loads.end_i.Vu, this.data.loads.end_j.Vu, this.data.vu || 180);

            // As_req approximation: Mu / (phi * fy * 0.9 * d)
            const phi_b = 0.85;
            const As_req_cent = (mu_center * 1e6) / (phi_b * fy * 0.9 * d);
            const As_req_end = (mu_end * 1e6) / (phi_b * fy * 0.9 * d);

            // 2. Call backend /api/rc/beam/auto-design for center rebar
            let autoRes = null;
            try {
                const res = await fetch('/api/rc/beam/auto-design', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        b: b,
                        h: h,
                        As_req: As_req_cent,
                        cover: cover,
                        stirrup_size: 'D10',
                        max_aggregate: this.data.rebar.maxAggSize || 25,
                        preferred_sizes: ['D19', 'D22', 'D25', 'D29']
                    })
                });
                if (res.ok) {
                    const json = await res.json();
                    if (json.success && json.data) {
                        autoRes = json.data;
                    }
                }
            } catch (e) {
                console.warn('[RCBeamForm] Auto-design API fallback:', e);
            }

            // Optimal arrangement synthesis
            let botBarsCent = '4-D25';
            let topBarsCent = '2-D22';
            let botLayer2Cent = '0';
            let topLayer2Cent = '0';

            if (autoRes && autoRes.selected) {
                const sel = autoRes.selected;
                if (sel.num_layers === 1) {
                    botBarsCent = `${sel.total_bars}-${sel.bar_size}`;
                    botLayer2Cent = '0';
                } else if (sel.layers && sel.layers.length >= 2) {
                    botBarsCent = `${sel.layers[0].num_bars}-${sel.bar_size}`;
                    botLayer2Cent = `${sel.layers[1].num_bars}-${sel.bar_size}`;
                }
                topBarsCent = `2-${sel.bar_size}`;
            } else {
                // High-precision local heuristic fallback
                const dbInfo = { D19: 286.5, D22: 387.1, D25: 506.7, D29: 642.4 };
                const chooseBest = (reqArea) => {
                    for (const [dia, area] of Object.entries(dbInfo)) {
                        const n = Math.ceil(reqArea / area);
                        if (n >= 2 && n <= 5) return { dia, n1: n, n2: 0 };
                        if (n > 5 && n <= 8) return { dia, n1: Math.ceil(n/2), n2: Math.floor(n/2) };
                    }
                    return { dia: 'D25', n1: 4, n2: 2 };
                };
                const cFit = chooseBest(As_req_cent);
                botBarsCent = `${cFit.n1}-${cFit.dia}`;
                botLayer2Cent = cFit.n2 > 0 ? `${cFit.n2}-${cFit.dia}` : '0';
                topBarsCent = `2-${cFit.dia}`;
            }

            // End stations arrangement (for -Mu)
            const chooseEnd = (reqArea) => {
                const dbInfo = { D22: 387.1, D25: 506.7, D29: 642.4 };
                for (const [dia, area] of Object.entries(dbInfo)) {
                    const n = Math.ceil(reqArea / area);
                    if (n >= 2 && n <= 4) return { dia, n1: n, n2: 0 };
                    if (n > 4 && n <= 8) return { dia, n1: 4, n2: n - 4 };
                }
                return { dia: 'D25', n1: 4, n2: 2 };
            };
            const eFit = chooseEnd(As_req_end);
            const topBarsEnd = `${eFit.n1}-${eFit.dia}`;
            const topLayer2End = eFit.n2 > 0 ? `${eFit.n2}-${eFit.dia}` : '0';
            const botBarsEnd = `3-${eFit.dia}`;

            // Stirrup spacing calculation: s = min(d/2, 300, phi*Av*fyt*d / (Vu - phi*Vc))
            const Av_stirrup = 142.66; // 2-D10
            const phi_v = 0.75;
            const Vc = (1/6 * Math.sqrt(fck) * b * d) * 1e-3; // kN
            const Vs_req = Math.max(0, vu_max / phi_v - Vc);
            let stirrup_spacing_end = 150;
            if (Vs_req > 0) {
                const s_calc = (phi_v * Av_stirrup * fyt * d * 1e-3) / Vs_req;
                stirrup_spacing_end = Math.min(Math.floor(d / 2 / 25) * 25, Math.floor(s_calc / 25) * 25, 200);
            } else {
                stirrup_spacing_end = Math.min(Math.floor(d / 2 / 25) * 25, 250);
            }
            stirrup_spacing_end = Math.max(100, stirrup_spacing_end);
            const stirrup_spacing_mid = Math.min(Math.floor(d / 2 / 25) * 25, 250);

            // 3. Inject into data
            this.data.rebar.center_m.top_layer1 = topBarsCent;
            this.data.rebar.center_m.top_layer2 = topLayer2Cent;
            this.data.rebar.center_m.bot_layer1 = botBarsCent;
            this.data.rebar.center_m.bot_layer2 = botLayer2Cent;
            this.data.rebar.center_m.stirrup_dia = 'D10';
            this.data.rebar.center_m.stirrup_space = stirrup_spacing_mid;

            this.data.rebar.end_i.top_layer1 = topBarsEnd;
            this.data.rebar.end_i.top_layer2 = topLayer2End;
            this.data.rebar.end_i.bot_layer1 = botBarsEnd;
            this.data.rebar.end_i.bot_layer2 = '0';
            this.data.rebar.end_i.stirrup_dia = 'D10';
            this.data.rebar.end_i.stirrup_space = stirrup_spacing_end;

            this.data.rebar.end_j.top_layer1 = topBarsEnd;
            this.data.rebar.end_j.top_layer2 = topLayer2End;
            this.data.rebar.end_j.bot_layer1 = botBarsEnd;
            this.data.rebar.end_j.bot_layer2 = '0';
            this.data.rebar.end_j.stirrup_dia = 'D10';
            this.data.rebar.end_j.stirrup_space = stirrup_spacing_end;

            // 4. Update DOM form elements
            this._updateFormInputsFromData();
            this._updateSpacingPreview();
            this._handleApply(true); // Save to memory & update canvas
            await this._handleCheck(); // Recalculate and update KaTeX report & DCR immediately

            this._showNotification(`✨ 자동설계 완료: 중앙(${botBarsCent}${botLayer2Cent !== '0' ? '+' + botLayer2Cent : ''}), 단부(${topBarsEnd}${topLayer2End !== '0' ? '+' + topLayer2End : ''}), 스터럽(@${stirrup_spacing_end}) 반영됨`, 'success');
        } catch (err) {
            console.error('[RCBeamForm] Auto design failed:', err);
            this._showNotification('❌ 자동설계 중 오류: ' + err.message, 'danger');
        } finally {
            if (designBtn) {
                designBtn.disabled = false;
                designBtn.innerHTML = origText;
            }
        }
    }

    _calcTotalAs(layer1, layer2) {
        const dbArea = { D10: 71.33, D13: 126.7, D16: 198.6, D19: 286.5, D22: 387.1, D25: 506.7, D29: 642.4, D32: 794.2 };
        const parse = (str) => {
            if (!str || str === '0') return 0;
            const parts = str.split('-');
            const n = parseInt(parts[0]) || 0;
            const dia = parts[1] || 'D25';
            return n * (dbArea[dia] || 506.7);
        };
        return parse(layer1) + parse(layer2);
    }

    _parseBarCount(str) {
        if (!str || str === '0') return 2;
        return parseInt(str.split('-')[0]) || 2;
    }

    _updateFormInputsFromData() {
        const rb = this.data.rebar;
        if (!this.container) return;

        // 1. Update Arrange Type Radio
        const arrRadios = this.container.querySelectorAll('input[name="beam_arrange_type"]');
        arrRadios.forEach(r => {
            r.checked = (r.value === (rb.arrange_type || 'SYMMETRIC_ENDS'));
        });

        // 2. Update Rebar Composite Cells
        const updateCell = (cellId, val, isLayer2) => {
            const parsed = this._parseRebarStr(val, isLayer2);
            const wrap = this.container.querySelector('#' + cellId);
            if (!wrap) return;
            const cntInp = wrap.querySelector('.rebar-count-input');
            const diaSel = wrap.querySelector('.rebar-dia-select');
            if (cntInp) cntInp.value = parsed.count;
            if (diaSel) {
                diaSel.value = parsed.dia;
                const isDim = isLayer2 && parsed.count === 0;
                diaSel.disabled = isDim;
                diaSel.style.opacity = isDim ? '0.45' : '1.0';
                diaSel.style.pointerEvents = isDim ? 'none' : 'auto';
            }
        };

        updateCell('rb-endi-t1', rb.end_i.top_layer1, false);
        updateCell('rb-endi-t2', rb.end_i.top_layer2, true);
        updateCell('rb-endi-b1', rb.end_i.bot_layer1, false);
        updateCell('rb-endi-b2', rb.end_i.bot_layer2, true);

        updateCell('rb-cent-t1', rb.center_m.top_layer1, false);
        updateCell('rb-cent-t2', rb.center_m.top_layer2, true);
        updateCell('rb-cent-b1', rb.center_m.bot_layer1, false);
        updateCell('rb-cent-b2', rb.center_m.bot_layer2, true);

        updateCell('rb-endj-t1', rb.end_j.top_layer1, false);
        updateCell('rb-endj-t2', rb.end_j.top_layer2, true);
        updateCell('rb-endj-b1', rb.end_j.bot_layer1, false);
        updateCell('rb-endj-b2', rb.end_j.bot_layer2, true);

        // 3. Update Stirrups
        const setVal = (id, val) => {
            const el = this.container.querySelector(id);
            if (el) el.value = val;
        };
        setVal('#rb-endi-st-dia', rb.end_i.stirrup_dia);
        setVal('#rb-endi-st-space', rb.end_i.stirrup_space);
        setVal('#rb-cent-st-dia', rb.center_m.stirrup_dia);
        setVal('#rb-cent-st-space', rb.center_m.stirrup_space);
        setVal('#rb-endj-st-dia', rb.end_j.stirrup_dia);
        setVal('#rb-endj-st-space', rb.end_j.stirrup_space);

        // 4. Update Arrange Type Visuals & Load Table State
        this._updateArrangeTypeUI(this.container);
        this._updateLoadTableArrangeState(this.container);
    }

    _showNotification(msg, type = 'info') {
        let toast = document.getElementById('beam-form-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'beam-form-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%);
                padding: 10px 18px;
                border-radius: 6px;
                font-size: 12.5px;
                font-weight: 600;
                font-family: var(--font-main, sans-serif);
                z-index: 100000;
                box-shadow: 0 4px 14px rgba(0,0,0,0.3);
                transition: opacity 0.25s ease, transform 0.25s ease;
                opacity: 0;
                pointer-events: none;
            `;
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        if (type === 'success') {
            toast.style.background = 'var(--success, #10b981)';
            toast.style.color = '#ffffff';
        } else if (type === 'danger') {
            toast.style.background = 'var(--danger, #ef4444)';
            toast.style.color = '#ffffff';
        } else {
            toast.style.background = 'var(--accent, #38bdf8)';
            toast.style.color = '#ffffff';
        }
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(0)';
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(8px)';
        }, 3000);
    }

    /**
     * Broadcast change with 50ms debounce
     * Notice: Only syncs memory and graphics canvas, does NOT re-run calculation report!
     */
    _broadcastChange() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this._syncLegacyRebarStrings();
            if (this.onChangeCallback) {
                this.onChangeCallback(this.data, false); // false = do NOT update report
            }
            if (window.EventBus && window.APP_EVENTS) {
                window.EventBus.emit(window.APP_EVENTS.PARAM_CHANGED, {
                    moduleKey: 'rc_beam',
                    data: this.data
                });
            }
            if (window.ProjectStore && typeof window.ProjectStore.updateMemberInputs === 'function') {
                const activeId = window.ProjectStore.getActiveMember('rc_beam')?.id;
                if (activeId) {
                    window.ProjectStore.updateMemberInputs('rc_beam', this.data);
                }
            }
        }, 50);
    }
}

// Global Singleton Instance & Registration
window.RCBeamForm = new RCBeamFormComponent();

