/**
 * AltDP_3rd RC Column Specialized Module Pack (rc_column_module.js)
 * Implements KDS 14 20 20 / 22 / 50 Column Design with AltDP-Core Platform
 * Conforms to Requirement 23 (4-Subtab Form, Dual Canvas Viewport, Tracer KaTeX A4 Report).
 */
class RCColumnModule {
    constructor() {
        this.id = 'rc_column';
        this.key = 'rc_column';
        this.name = 'RC 기둥 (Column)';
        this.category = 'rc';
        this.data = this.getDefaultData();
        this.lastResult = null;
        this.activeTab = 'section';
    }

    /**
     * Returns standard engineering default inputs for RC column
     */
    getDefaultData() {
        return {
            name: 'C1',
            b: 600,
            h: 600,
            cover: 60,
            fck: 30,
            fy: 400,
            bar_diam: 25,
            total_bars: 12,
            tie_diam: 10,
            tie_spacing: 300,
            tie_legs_x: 2,
            tie_legs_y: 2,
            is_spiral: false,
            Pu: 2500,
            Mux: 350,
            Muy: 0,
            Vux: 0,
            Vuy: 120,
            Lu: 3600,
            k: 1.0,
            is_braced: true,
            M1x: 0,
            M2x: 350,
            M1y: 0,
            M2y: 0,
            beta_dns: 0.2
        };
    }

    async mount(context) {
        this.context = context;
        if (context.memberData) Object.assign(this.data, context.memberData);

        this.renderForm(context.formContainer, this.data, window.EventBus);
        this.renderGraphics(context.canvas, context.pmCanvas, this.data, this.lastResult);
        this.renderReport(context.reportContainer, this.data, this.lastResult, {});
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
            this.renderGraphics(this.context.canvas, this.context.pmCanvas, this.data, this.lastResult);
            if (payload && payload.source === 'check') {
                this.renderReport(this.context.reportContainer, this.data, payload.result || this.lastResult, {});
            }
        }
    }

    /**
     * Pane 2: 4-Subtab Input Form & 3 Action Buttons [💾 적용] [⚡ 검토] [✨ 자동설계]
     */
    renderForm(container, data = this.data, bus = window.EventBus) {
        if (!container) return;
        const curData = data || this.data;

        container.innerHTML = `
            <div class="rc-column-form-container" style="display:flex;flex-direction:column;height:100%;font-family:'Pretendard', sans-serif;">
                <!-- 4 Subtabs Header -->
                <div class="subtab-header" style="display:flex;border-bottom:2px solid #e2e8f0;background:#f8fafc;padding:4px 8px 0;">
                    <button type="button" class="col-tab-btn ${this.activeTab === 'section' ? 'active' : ''}" data-tab="section" style="padding:8px 14px;font-size:12px;font-weight:700;border:none;background:${this.activeTab === 'section' ? '#ffffff' : 'transparent'};color:${this.activeTab === 'section' ? '#1e3a8a' : '#64748b'};border-bottom:${this.activeTab === 'section' ? '2px solid #1e3a8a' : 'none'};cursor:pointer;">📐 단면/재료</button>
                    <button type="button" class="col-tab-btn ${this.activeTab === 'rebar' ? 'active' : ''}" data-tab="rebar" style="padding:8px 14px;font-size:12px;font-weight:700;border:none;background:${this.activeTab === 'rebar' ? '#ffffff' : 'transparent'};color:${this.activeTab === 'rebar' ? '#1e3a8a' : '#64748b'};border-bottom:${this.activeTab === 'rebar' ? '2px solid #1e3a8a' : 'none'};cursor:pointer;">🔩 철근배근</button>
                    <button type="button" class="col-tab-btn ${this.activeTab === 'load' ? 'active' : ''}" data-tab="load" style="padding:8px 14px;font-size:12px;font-weight:700;border:none;background:${this.activeTab === 'load' ? '#ffffff' : 'transparent'};color:${this.activeTab === 'load' ? '#1e3a8a' : '#64748b'};border-bottom:${this.activeTab === 'load' ? '2px solid #1e3a8a' : 'none'};cursor:pointer;">⚖️ 설계하중</button>
                    <button type="button" class="col-tab-btn ${this.activeTab === 'option' ? 'active' : ''}" data-tab="option" style="padding:8px 14px;font-size:12px;font-weight:700;border:none;background:${this.activeTab === 'option' ? '#ffffff' : 'transparent'};color:${this.activeTab === 'option' ? '#1e3a8a' : '#64748b'};border-bottom:${this.activeTab === 'option' ? '2px solid #1e3a8a' : 'none'};cursor:pointer;">⚙️ 장주/옵션</button>
                </div>

                <!-- Subtab Body Content -->
                <div class="subtab-body" style="flex:1;overflow-y:auto;padding:14px;background:#ffffff;">
                    <!-- 1. Section / Material Tab -->
                    <div id="tab-content-section" class="tab-pane" style="display:${this.activeTab === 'section' ? 'block' : 'none'};">
                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">단면 치수 (Section Geometry)</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">단면 폭 (b, mm)</label>
                                <input type="number" id="inp-col-b" value="${curData.b}" min="150" max="3000" step="50" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">단면 높이 (h, mm)</label>
                                <input type="number" id="inp-col-h" value="${curData.h}" min="150" max="3000" step="50" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                        <div style="margin-bottom:14px;">
                            <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">철근 중심 피복 (dc, mm)</label>
                            <input type="number" id="inp-col-cover" value="${curData.cover}" min="20" max="150" step="5" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                        </div>

                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">재료 강도 (Materials)</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">콘크리트 강도 (fck, MPa)</label>
                                <input type="number" id="inp-col-fck" value="${curData.fck}" min="15" max="100" step="3" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">주철근 항복강도 (fy, MPa)</label>
                                <input type="number" id="inp-col-fy" value="${curData.fy}" min="200" max="800" step="100" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                    </div>

                    <!-- 2. Rebar Detailing Tab -->
                    <div id="tab-content-rebar" class="tab-pane" style="display:${this.activeTab === 'rebar' ? 'block' : 'none'};">
                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">주철근 배근 (Longitudinal Bars)</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">주철근 직경 (db, mm)</label>
                                <select id="inp-col-bar_diam" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                                    <option value="19" ${curData.bar_diam === 19 ? 'selected' : ''}>D19 (19.1mm)</option>
                                    <option value="22" ${curData.bar_diam === 22 || curData.bar_diam === 22.2 ? 'selected' : ''}>D22 (22.2mm)</option>
                                    <option value="25" ${curData.bar_diam === 25 || curData.bar_diam === 25.4 ? 'selected' : ''}>D25 (25.4mm)</option>
                                    <option value="29" ${curData.bar_diam === 29 ? 'selected' : ''}>D29 (28.6mm)</option>
                                    <option value="32" ${curData.bar_diam === 32 ? 'selected' : ''}>D32 (31.8mm)</option>
                                </select>
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">주철근 총 개수 (EA)</label>
                                <input type="number" id="inp-col-total_bars" value="${curData.total_bars}" min="4" max="48" step="2" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>

                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">띠철근 / 전단보강 (Ties & Hoops)</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">띠철근 직경 (dt, mm)</label>
                                <select id="inp-col-tie_diam" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                                    <option value="10" ${curData.tie_diam === 10 || curData.tie_diam === 9.53 ? 'selected' : ''}>D10 (9.53mm)</option>
                                    <option value="13" ${curData.tie_diam === 13 ? 'selected' : ''}>D13 (12.7mm)</option>
                                    <option value="16" ${curData.tie_diam === 16 ? 'selected' : ''}>D16 (15.9mm)</option>
                                </select>
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">띠철근 간격 (s, mm)</label>
                                <input type="number" id="inp-col-tie_spacing" value="${curData.tie_spacing}" min="50" max="600" step="25" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">전단 다리수 (X/Y)</label>
                                <input type="number" id="inp-col-tie_legs_x" value="${curData.tie_legs_x || 2}" min="2" max="6" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div style="display:flex;align-items:center;padding-top:16px;">
                                <label style="font-size:11.5px;color:#334155;display:inline-flex;align-items:center;gap:6px;cursor:pointer;">
                                    <input type="checkbox" id="inp-col-is_spiral" ${curData.is_spiral ? 'checked' : ''}>
                                    나선철근(Spiral) 적용
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- 3. Factored Loads Tab -->
                    <div id="tab-content-load" class="tab-pane" style="display:${this.activeTab === 'load' ? 'block' : 'none'};">
                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">위험단면 계수부재력 (Factored Loads)</div>
                        <div style="margin-bottom:10px;">
                            <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">계수 축하중 (Pu, kN) <span style="font-size:10px;color:#94a3b8;">압축(+)</span></label>
                            <input type="number" id="inp-col-Pu" value="${curData.Pu}" step="50" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">휨모멘트 X (Mux, kN·m)</label>
                                <input type="number" id="inp-col-Mux" value="${curData.Mux}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">휨모멘트 Y (Muy, kN·m)</label>
                                <input type="number" id="inp-col-Muy" value="${curData.Muy}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">계수 전단력 X (Vux, kN)</label>
                                <input type="number" id="inp-col-Vux" value="${curData.Vux}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">계수 전단력 Y (Vuy, kN)</label>
                                <input type="number" id="inp-col-Vuy" value="${curData.Vuy}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                    </div>

                    <!-- 4. Slenderness & Framing Options Tab -->
                    <div id="tab-content-option" class="tab-pane" style="display:${this.activeTab === 'option' ? 'block' : 'none'};">
                        <div style="font-size:11.5px;font-weight:700;color:#334155;margin-bottom:8px;border-bottom:1px solid #f1f5f9;padding-bottom:4px;">장주 및 골조 지지조건 (KDS 14 20 20)</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">비지지 길이 (Lu, mm)</label>
                                <input type="number" id="inp-col-Lu" value="${curData.Lu}" min="500" max="20000" step="100" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">유효좌굴길이계수 (k)</label>
                                <input type="number" id="inp-col-k" value="${curData.k}" min="0.5" max="5.0" step="0.05" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                        <div style="margin-bottom:10px;">
                            <label style="font-size:11.5px;color:#334155;display:inline-flex;align-items:center;gap:6px;cursor:pointer;">
                                <input type="checkbox" id="inp-col-is_braced" ${curData.is_braced ? 'checked' : ''}>
                                횡구속(Non-sway) 골조
                            </label>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">상단 모멘트 X (M1x, kN·m)</label>
                                <input type="number" id="inp-col-M1x" value="${curData.M1x}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                            <div>
                                <label style="font-size:11px;color:#64748b;display:block;margin-bottom:3px;">하단 모멘트 X (M2x, kN·m)</label>
                                <input type="number" id="inp-col-M2x" value="${curData.M2x}" step="10" style="width:100%;padding:6px 8px;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3 Action Buttons [💾 적용] [⚡ 검토] [✨ 자동설계] -->
                <div class="col-actions-bar" style="display:flex;gap:8px;padding:10px 14px;background:#f1f5f9;border-top:1px solid #e2e8f0;">
                    <button type="button" id="btn-col-apply" style="flex:1;padding:8px 0;background:#ffffff;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;font-weight:700;color:#334155;cursor:pointer;">💾 적용</button>
                    <button type="button" id="btn-col-check" style="flex:1.4;padding:8px 0;background:#2563eb;border:1px solid #1d4ed8;border-radius:4px;font-size:12px;font-weight:800;color:#ffffff;cursor:pointer;">⚡ 검토</button>
                    <button type="button" id="btn-col-autodesign" style="flex:1.2;padding:8px 0;background:#059669;border:1px solid #047857;border-radius:4px;font-size:12px;font-weight:700;color:#ffffff;cursor:pointer;">✨ 자동설계</button>
                </div>
            </div>
        `;

        // Event Listeners: Subtabs
        container.querySelectorAll('.col-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.getAttribute('data-tab');
                this.activeTab = tab;
                container.querySelectorAll('.col-tab-btn').forEach(b => {
                    const isCur = b.getAttribute('data-tab') === tab;
                    b.style.background = isCur ? '#ffffff' : 'transparent';
                    b.style.color = isCur ? '#1e3a8a' : '#64748b';
                    b.style.borderBottom = isCur ? '2px solid #1e3a8a' : 'none';
                });
                container.querySelectorAll('.tab-pane').forEach(p => {
                    p.style.display = p.id === `tab-content-${tab}` ? 'block' : 'none';
                });
            });
        });

        // Event Listeners: Input changes
        const syncInputs = () => {
            curData.b = parseFloat(document.getElementById('inp-col-b')?.value || curData.b);
            curData.h = parseFloat(document.getElementById('inp-col-h')?.value || curData.h);
            curData.cover = parseFloat(document.getElementById('inp-col-cover')?.value || curData.cover);
            curData.fck = parseFloat(document.getElementById('inp-col-fck')?.value || curData.fck);
            curData.fy = parseFloat(document.getElementById('inp-col-fy')?.value || curData.fy);
            curData.bar_diam = parseFloat(document.getElementById('inp-col-bar_diam')?.value || curData.bar_diam);
            curData.total_bars = parseInt(document.getElementById('inp-col-total_bars')?.value || curData.total_bars, 10);
            curData.tie_diam = parseFloat(document.getElementById('inp-col-tie_diam')?.value || curData.tie_diam);
            curData.tie_spacing = parseFloat(document.getElementById('inp-col-tie_spacing')?.value || curData.tie_spacing);
            curData.tie_legs_x = parseInt(document.getElementById('inp-col-tie_legs_x')?.value || curData.tie_legs_x, 10);
            curData.is_spiral = Boolean(document.getElementById('inp-col-is_spiral')?.checked);
            curData.Pu = parseFloat(document.getElementById('inp-col-Pu')?.value || curData.Pu);
            curData.Mux = parseFloat(document.getElementById('inp-col-Mux')?.value || curData.Mux);
            curData.Muy = parseFloat(document.getElementById('inp-col-Muy')?.value || curData.Muy);
            curData.Vux = parseFloat(document.getElementById('inp-col-Vux')?.value || curData.Vux);
            curData.Vuy = parseFloat(document.getElementById('inp-col-Vuy')?.value || curData.Vuy);
            curData.Lu = parseFloat(document.getElementById('inp-col-Lu')?.value || curData.Lu);
            curData.k = parseFloat(document.getElementById('inp-col-k')?.value || curData.k);
            curData.is_braced = Boolean(document.getElementById('inp-col-is_braced')?.checked);
            curData.M1x = parseFloat(document.getElementById('inp-col-M1x')?.value || curData.M1x);
            curData.M2x = parseFloat(document.getElementById('inp-col-M2x')?.value || curData.M2x);
        };

        container.querySelectorAll('input, select').forEach(el => {
            el.addEventListener('input', () => {
                syncInputs();
                if (this.context) {
                    this.renderGraphics(this.context.canvas, this.context.pmCanvas, curData, this.lastResult);
                }
            });
        });

        // 3 Action Buttons Handlers
        const btnApply = document.getElementById('btn-col-apply');
        const btnCheck = document.getElementById('btn-col-check');
        const btnAuto = document.getElementById('btn-col-autodesign');

        if (btnApply) {
            btnApply.addEventListener('click', () => {
                syncInputs();
                if (window.ProjectStore && typeof window.ProjectStore.updateActiveMemberInputs === 'function') {
                    window.ProjectStore.updateActiveMemberInputs(curData);
                }
                if (this.context) {
                    this.renderGraphics(this.context.canvas, this.context.pmCanvas, curData, this.lastResult);
                }
            });
        }

        if (btnCheck) {
            btnCheck.addEventListener('click', async () => {
                syncInputs();
                await this.calculateAndRender();
            });
        }

        if (btnAuto) {
            btnAuto.addEventListener('click', () => {
                // Auto-design rebar estimate
                const Pu = curData.Pu || 2000;
                const Ag = curData.b * curData.h;
                // Target rho ~ 1.5%
                const targetAst = 0.015 * Ag;
                const barArea = Math.PI * (curData.bar_diam ** 2) / 4.0;
                let neededBars = Math.max(4, Math.ceil(targetAst / barArea));
                if (neededBars % 2 !== 0) neededBars += 1;
                curData.total_bars = neededBars;
                const inpBars = document.getElementById('inp-col-total_bars');
                if (inpBars) inpBars.value = neededBars;
                this.renderGraphics(this.context.canvas, this.context.pmCanvas, curData, this.lastResult);
            });
        }
    }

    /**
     * Call API and render A4 KaTeX Structural Report within 100ms
     */
    async calculateAndRender() {
        try {
            const res = await this.calculate(this.data);
            if (res && res.success && res.data) {
                this.lastResult = res.data;
                if (this.context) {
                    this.renderGraphics(this.context.canvas, this.context.pmCanvas, this.data, this.lastResult);
                    this.renderReport(this.context.reportContainer, this.data, this.lastResult, {});
                }
            }
        } catch (e) {
            console.error('[RCColumnModule] calculation error:', e);
        }
    }

    /**
     * Legacy single-canvas rendering bridge
     */
    renderCanvas(canvas) {
        return this.renderGraphics(canvas, null, this.data, this.lastResult);
    }

    /**
     * Pane 3: 2-Tier Stacked Viewport (Top: CAD Section, Bottom: 200-Fiber P-M Curve)
     */
    renderGraphics(geomCanvas, mechCanvas, data = this.data, result = this.lastResult) {
        const curData = data || this.data;

        // 1. If GraphicViewport is available, delegate to it
        if (window.GraphicViewport && window.GraphicViewport.initialized) {
            window.GraphicViewport.currentMemberType = 'rc_column';
            window.GraphicViewport.currentMemberData = curData;
            if (result) {
                window.GraphicViewport.setCalculationResult(result);
            } else {
                window.GraphicViewport.redrawAll();
            }
            return;
        }

        // 2. Direct Canvas Drawing
        const c1 = document.getElementById('canvas-geometry') || document.getElementById('sectionCanvas') || geomCanvas;
        const c2 = document.getElementById('canvas-mechanics') || document.getElementById('pmChartCanvas') || mechCanvas;

        // --- Top Viewport: Section Detailing ---
        if (c1) {
            const ctx = c1.getContext('2d');
            const w = c1.width;
            const h = c1.height;
            ctx.clearRect(0, 0, w, h);
            ctx.save();
            ctx.translate(w / 2, h / 2);

            const scale = Math.min((w - 80) / curData.b, (h - 80) / curData.h, 0.45);
            ctx.scale(scale, scale);

            // Concrete body
            ctx.fillStyle = '#1e293b';
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 2.0 / scale;
            ctx.fillRect(-curData.b / 2, -curData.h / 2, curData.b, curData.h);
            ctx.strokeRect(-curData.b / 2, -curData.h / 2, curData.b, curData.h);

            // Tie hoop with 135-deg hook
            const sc = curData.cover - curData.tie_diam / 2;
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.0 / scale;
            ctx.strokeRect(-curData.b / 2 + sc, -curData.h / 2 + sc, curData.b - sc * 2, curData.h - sc * 2);

            // Rebars from geometry or calculated perimeter
            const rebars = (result && result.geometry && result.geometry.rebars) ? result.geometry.rebars : [];
            if (rebars.length > 0) {
                rebars.forEach(r => {
                    ctx.beginPath();
                    ctx.arc(r.x, r.y, (r.dia || 25) / 2, 0, Math.PI * 2);
                    ctx.fillStyle = '#f59e0b';
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.0 / scale;
                    ctx.stroke();
                });
            } else {
                // Fallback 4 corners + mid bars
                const xL = -curData.b / 2 + curData.cover;
                const xR = curData.b / 2 - curData.cover;
                const yB = -curData.h / 2 + curData.cover;
                const yT = curData.h / 2 - curData.cover;
                [[-xL, -yT], [xR, -yT], [xR, -yB], [-xL, -yB]].forEach(([rx, ry]) => {
                    ctx.beginPath();
                    ctx.arc(rx, ry, curData.bar_diam / 2, 0, Math.PI * 2);
                    ctx.fillStyle = '#f59e0b';
                    ctx.fill();
                });
            }

            // Dimensions
            ctx.font = '12px Pretendard, sans-serif';
            ctx.fillStyle = '#94a3b8';
            ctx.textAlign = 'center';
            ctx.fillText(`b = ${curData.b} mm`, 0, curData.h / 2 + 25 / scale);
            ctx.restore();
        }

        // --- Bottom Viewport: 200-Fiber P-M Diagram ---
        if (c2) {
            const ctx = c2.getContext('2d');
            const w = c2.width;
            const h = c2.height;
            ctx.clearRect(0, 0, w, h);

            const pts = (result && result.pm_curve_x && result.pm_curve_x.length > 0) 
                ? result.pm_curve_x 
                : [];

            if (pts.length > 0) {
                const maxP = Math.max(...pts.map(p => p.Pn || p.phi_Pn || 1000), curData.Pu * 1.2);
                const maxM = Math.max(...pts.map(p => p.Mn || p.phi_Mn || 300), curData.Mux * 1.2);
                const margin = { left: 50, right: 30, top: 30, bottom: 40 };
                const plotW = w - margin.left - margin.right;
                const plotH = h - margin.top - margin.bottom;

                const toX = (m) => margin.left + (m / maxM) * plotW;
                const toY = (p) => margin.top + plotH - (p / maxP) * plotH;

                // Axes
                ctx.strokeStyle = '#475569';
                ctx.lineWidth = 1.0;
                ctx.beginPath();
                ctx.moveTo(margin.left, margin.top); ctx.lineTo(margin.left, margin.top + plotH);
                ctx.lineTo(margin.left + plotW, margin.top + plotH);
                ctx.stroke();

                // Design Curve (phi_Pn vs phi_Mn)
                ctx.beginPath();
                pts.forEach((p, idx) => {
                    const x = toX(p.phi_Mn || 0);
                    const y = toY(p.phi_Pn || 0);
                    if (idx === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.lineTo(toX(0), toY(0));
                ctx.closePath();
                ctx.fillStyle = 'rgba(56, 189, 248, 0.12)';
                ctx.fill();
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 2.0;
                ctx.stroke();

                // Factored Demand Point (Mux, Pu)
                const dX = toX(curData.Mux || 0);
                const dY = toY(curData.Pu || 0);
                const dcr = result.pm_dcr || (curData.Mux / maxM);
                const isSafe = dcr <= 1.0;

                ctx.beginPath();
                ctx.arc(dX, dY, 6, 0, Math.PI * 2);
                ctx.fillStyle = isSafe ? '#10b981' : '#ef4444';
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2.0;
                ctx.stroke();

                // Axis Labels
                ctx.fillStyle = '#94a3b8';
                ctx.font = '10px Pretendard, sans-serif';
                ctx.fillText(`P (kN)`, margin.left - 4, margin.top - 10);
                ctx.fillText(`M (kN·m)`, margin.left + plotW - 20, margin.top + plotH + 25);
                ctx.fillText(`(${curData.Mux}, ${curData.Pu}) DCR=${Number(dcr).toFixed(3)}`, dX + 8, dY - 8);
            }
        }
    }

    /**
     * Pane 4: Pure White A4 KaTeX Report (Conforms to Requirement 23 Step 4)
     */
    renderReport(container, data = this.data, result = this.lastResult, options = {}) {
        if (!container) return;
        const curData = data || this.data;

        if (result && result.tracer && window.TracerReportRenderer) {
            window.TracerReportRenderer.render(container, result.tracer, options);
        } else if (window.TracerReportRenderer) {
            window.TracerReportRenderer.render(container, null, options);
        } else if (window.ReportCommonRenderer) {
            window.ReportCommonRenderer.render(container, result, 'rc_column', curData);
        }
    }

    /**
     * Calculate API integration
     */
    async calculate(data = this.data) {
        try {
            const payload = {
                name: data.name || 'C1',
                b: parseFloat(data.b),
                h: parseFloat(data.h),
                cover: parseFloat(data.cover),
                bar_diam: parseFloat(data.bar_diam),
                total_bars: parseInt(data.total_bars, 10),
                tie_diam: parseFloat(data.tie_diam),
                tie_spacing: parseFloat(data.tie_spacing),
                tie_legs_x: parseInt(data.tie_legs_x || 2, 10),
                tie_legs_y: parseInt(data.tie_legs_y || 2, 10),
                is_spiral: Boolean(data.is_spiral),
                Pu: parseFloat(data.Pu),
                Mux: parseFloat(data.Mux),
                Muy: parseFloat(data.Muy || 0),
                Vux: parseFloat(data.Vux || 0),
                Vuy: parseFloat(data.Vuy || 0),
                Lu: parseFloat(data.Lu),
                k: parseFloat(data.k),
                is_braced: Boolean(data.is_braced),
                M1x: parseFloat(data.M1x || 0),
                M2x: parseFloat(data.M2x || data.Mux),
                M1y: parseFloat(data.M1y || 0),
                M2y: parseFloat(data.M2y || data.Muy || 0),
                fck: parseFloat(data.fck),
                fy: parseFloat(data.fy)
            };

            const res = await fetch('/api/rc/column/design', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {
            console.warn('[RCColumnModule] calculate API error:', e);
        }
        return { success: false, data: null };
    }
}

if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_column', new RCColumnModule());
}
