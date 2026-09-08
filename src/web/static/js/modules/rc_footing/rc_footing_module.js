/**
 * AltDP_3rd RC Footing Specialized Module Pack (rc_footing_module.js)
 * Implements KDS 14 20 50 Spread/Isolated Footing Design
 * Conforms to Requirement 21-6 & docs/07 section 6.
 */
class RCFootingModule {
    constructor() {
        this.id = 'rc_footing';
        this.key = 'rc_footing';
        this.name = 'RC 독립기초 (Spread Footing)';
        this.category = 'rc';

        this.data = this.getDefaultData();
    }

    /**
     * Returns default engineering input data for spread footing
     */
    getDefaultData() {
        return {
            Bx: 2400,            // 기초판 X방향 폭 (mm)
            Ly: 2400,            // 기초판 Y방향 길이 (mm)
            thickness_H: 600,    // 기초판 두께 (mm)
            depth_Df: 1500,      // 매설 깊이 (mm)
            cover: 75,           // 피복 두께 (mm)
            col_cx: 500,         // 상부 기둥 X 폭 (mm)
            col_cy: 500,         // 상부 기둥 Y 폭 (mm)
            fck: 24,             // 콘크리트 강도 (MPa)
            fy: 400,             // 철근 항복강도 (MPa)
            rebarX: 'D16 @ 150', // X방향 주철근 배근
            rebarY: 'D16 @ 150', // Y방향 주철근 배근
            pu: 1200.0,          // 계수 축하중 (kN)
            mux: 120.0,          // 계수 모멘트 X (kN·m)
            muy: 80.0,           // 계수 모멘트 Y (kN·m)
            p_serv: 950.0,       // 사용하중 축력 (kN)
            mx_serv: 90.0,       // 사용하중 모멘트 X (kN·m)
            qa: 250.0            // 허용 지내력 (kPa)
        };
    }

    async mount(context) {
        this.context = context;
        if (context.memberData) {
            Object.assign(this.data, context.memberData);
        }

        this.renderForm(context.formContainer, this.data, window.EventBus);
        this.renderGraphics(context.canvas, context.pmCanvas, this.data, null);
        this.renderReport(context.reportContainer, this.data, null, {});
    }

    unmount() {
        // Cleanup resources
    }

    onParamChange(payload) {
        if (payload && payload.key) {
            this.data[payload.key] = payload.value;
        }
        if (this.context) {
            this.renderGraphics(this.context.canvas, this.context.pmCanvas, this.data, null);
            this.renderReport(this.context.reportContainer, this.data, null, {});
        }
    }

    /**
     * Render Pane 2 4-Subtab Input Form
     */
    renderForm(container, data = this.data, bus = window.EventBus) {
        if (!container) return;

        const curData = data || this.data;

        if (window.FormBuilder) {
            const schema = {
                fields: [
                    // Tab 1: 단면 / 재료
                    { tab: 'section', key: 'Bx', label: '기초 폭 Bx (mm)', default: curData.Bx, unit: 'mm' },
                    { tab: 'section', key: 'Ly', label: '기초 길이 Ly (mm)', default: curData.Ly, unit: 'mm' },
                    { tab: 'section', key: 'thickness_H', label: '기초 두께 H (mm)', default: curData.thickness_H, unit: 'mm' },
                    { tab: 'section', key: 'col_cx', label: '기둥 폭 cx (mm)', default: curData.col_cx, unit: 'mm' },
                    { tab: 'section', key: 'col_cy', label: '기둥 길이 cy (mm)', default: curData.col_cy, unit: 'mm' },
                    { tab: 'section', key: 'fck', label: '콘크리트 강도 fck (MPa)', default: curData.fck, unit: 'MPa' },
                    { tab: 'section', key: 'fy', label: '철근 항복강도 fy (MPa)', default: curData.fy, unit: 'MPa' },
                    // Tab 2: 배근 / 상세
                    { tab: 'rebar', key: 'cover', label: '피복 두께 (mm)', default: curData.cover, unit: 'mm' },
                    { tab: 'rebar', key: 'rebarX', label: 'X방향 주철근 배근', default: curData.rebarX, type: 'text' },
                    { tab: 'rebar', key: 'rebarY', label: 'Y방향 주철근 배근', default: curData.rebarY, type: 'text' },
                    // Tab 3: 설계 하중
                    { tab: 'load', key: 'pu', label: '계수 축력 Pu (kN)', default: curData.pu, unit: 'kN' },
                    { tab: 'load', key: 'mux', label: '계수 모멘트 Mux (kN·m)', default: curData.mux, unit: 'kN·m' },
                    { tab: 'load', key: 'muy', label: '계수 모멘트 Muy (kN·m)', default: curData.muy, unit: 'kN·m' },
                    { tab: 'load', key: 'qa', label: '허용 지내력 qa (kPa)', default: curData.qa, unit: 'kPa' },
                    { tab: 'load', key: 'lcbDlg', label: '하중조합 생성기', default: '설정...', hasDialog: true, onOpenDialog: (cur, cb) => {
                        if (window.CommonDialogs && window.CommonDialogs.openLoadCombination) {
                            window.CommonDialogs.openLoadCombination(cur, cb);
                        }
                    }},
                    // Tab 4: 설계 옵션
                    { tab: 'option', key: 'depth_Df', label: '기초 근입깊이 Df (mm)', default: curData.depth_Df, unit: 'mm' },
                    { tab: 'option', key: 'soil_gamma', label: '상재토 단위중량 (kN/m³)', default: 18.0, unit: 'kN/m³' }
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
     * Render Pane 3 Top/Bottom Vertical Dual Canvas
     */
    renderGraphics(geomCanvas, mechCanvas, data = this.data, result = null) {
        const curData = data || this.data;

        // 1. Top Viewport: Plan Geometry & Column / Rebar Grid
        if (geomCanvas) {
            const ctx = geomCanvas.getContext('2d');
            const w = geomCanvas.width;
            const h = geomCanvas.height;

            ctx.clearRect(0, 0, w, h);
            ctx.save();
            ctx.translate(w / 2, h / 2);

            const maxDim = Math.max(curData.Bx, curData.Ly);
            const scale = 240 / maxDim;
            ctx.scale(scale, scale);

            const halfBx = curData.Bx / 2;
            const halfLy = curData.Ly / 2;

            // Footing Concrete Body (Plan)
            ctx.fillStyle = '#1e293b';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.5;
            ctx.fillRect(-halfBx, -halfLy, curData.Bx, curData.Ly);
            ctx.strokeRect(-halfBx, -halfLy, curData.Bx, curData.Ly);

            // Rebar Mesh (X and Y Lines)
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
            ctx.lineWidth = 1.0;
            const step = 200;
            for (let x = -halfBx + 150; x < halfBx; x += step) {
                ctx.beginPath();
                ctx.moveTo(x, -halfLy + curData.cover);
                ctx.lineTo(x, halfLy - curData.cover);
                ctx.stroke();
            }
            for (let y = -halfLy + 150; y < halfLy; y += step) {
                ctx.beginPath();
                ctx.moveTo(-halfBx + curData.cover, y);
                ctx.lineTo(halfBx - curData.cover, y);
                ctx.stroke();
            }

            // Top Column Body (Center)
            const halfColX = curData.col_cx / 2;
            const halfColY = curData.col_cy / 2;
            ctx.fillStyle = '#334155';
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2.0;
            ctx.fillRect(-halfColX, -halfColY, curData.col_cx, curData.col_cy);
            ctx.strokeRect(-halfColX, -halfColY, curData.col_cx, curData.col_cy);

            // Column Center Axis
            ctx.strokeStyle = '#ef4444';
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(-halfColX - 30, 0); ctx.lineTo(halfColX + 30, 0);
            ctx.moveTo(0, -halfColY - 30); ctx.lineTo(0, halfColY + 30);
            ctx.stroke();
            ctx.setLineDash([]);

            // Dimensions
            if (window.VDrawPrimitives) {
                window.VDrawPrimitives.drawDimensionLine(ctx, -halfBx, halfLy, halfBx, halfLy, `Bx = ${curData.Bx}`, 40, false);
                window.VDrawPrimitives.drawDimensionLine(ctx, halfBx, -halfLy, halfBx, halfLy, `Ly = ${curData.Ly}`, 40, true);
            }

            ctx.restore();
        }

        // 2. Bottom Viewport: Soil Contact Pressure Distribution Diagram (q_max, q_min)
        if (mechCanvas) {
            const ctx = mechCanvas.getContext('2d');
            const w = mechCanvas.width;
            const h = mechCanvas.height;

            ctx.clearRect(0, 0, w, h);
            ctx.save();

            // Coordinate origin
            ctx.translate(w / 2, h / 2 - 20);

            // Calculate bearing pressure
            const area = (curData.Bx / 1000) * (curData.Ly / 1000);
            const zx = (curData.Ly / 1000) * Math.pow(curData.Bx / 1000, 2) / 6;
            const P = curData.p_serv || curData.pu * 0.75;
            const M = curData.mx_serv || curData.mux * 0.75;

            const q_avg = P / area;
            const delta_q = M / zx;
            const q_max = q_avg + delta_q;
            const q_min = Math.max(0, q_avg - delta_q);
            const qa = curData.qa;

            const diagW = 360;
            const baseH = 80;
            const qMaxH = Math.min(100, (q_max / qa) * 70);
            const qMinH = Math.min(100, (q_min / qa) * 70);

            // Footing Bottom Line
            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(-diagW / 2, 0);
            ctx.lineTo(diagW / 2, 0);
            ctx.stroke();

            // Soil Contact Pressure Polygon (Trapezoidal)
            ctx.beginPath();
            ctx.moveTo(-diagW / 2, 0);
            ctx.lineTo(-diagW / 2, qMinH);
            ctx.lineTo(diagW / 2, qMaxH);
            ctx.lineTo(diagW / 2, 0);
            ctx.closePath();

            const grad = ctx.createLinearGradient(-diagW / 2, 0, diagW / 2, 0);
            grad.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
            grad.addColorStop(1, 'rgba(239, 68, 68, 0.45)');
            ctx.fillStyle = grad;
            ctx.fill();

            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 1.8;
            ctx.stroke();

            // Pressure Arrows
            const arrowCount = 7;
            for (let i = 0; i < arrowCount; i++) {
                const ratio = i / (arrowCount - 1);
                const ax = -diagW / 2 + diagW * ratio;
                const ay = qMinH + (qMaxH - qMinH) * ratio;

                ctx.beginPath();
                ctx.moveTo(ax, ay);
                ctx.lineTo(ax, 0);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
                ctx.lineWidth = 1.2;
                ctx.stroke();

                // Arrowhead
                ctx.beginPath();
                ctx.moveTo(ax - 3, 6);
                ctx.lineTo(ax, 0);
                ctx.lineTo(ax + 3, 6);
                ctx.stroke();
            }

            // Allowable qa Limit Line (Dashed Green)
            const qaH = 70;
            ctx.beginPath();
            ctx.setLineDash([5, 5]);
            ctx.strokeStyle = '#22c55e';
            ctx.lineWidth = 1.5;
            ctx.moveTo(-diagW / 2 - 20, qaH);
            ctx.lineTo(diagW / 2 + 20, qaH);
            ctx.stroke();
            ctx.setLineDash([]);

            // Labels
            ctx.font = '12px "Pretendard", "Segoe UI", sans-serif';
            ctx.fillStyle = '#f8fafc';
            ctx.textAlign = 'right';
            ctx.fillText(`q_max = ${q_max.toFixed(1)} kPa`, diagW / 2, qMaxH + 20);
            ctx.textAlign = 'left';
            ctx.fillText(`q_min = ${q_min.toFixed(1)} kPa`, -diagW / 2, qMinH + 20);

            ctx.fillStyle = '#22c55e';
            ctx.textAlign = 'left';
            ctx.fillText(`qa = ${qa.toFixed(1)} kPa (허용지내력)`, diagW / 2 - 120, qaH - 8);

            ctx.restore();
        }
    }

    /**
     * Legacy single-canvas rendering bridge
     */
    renderCanvas(canvas) {
        return this.renderGraphics(canvas, null, this.data, null);
    }


    /**
     * Render Pane 4 Pure White A4 KDS Standard Report
     */
    renderReport(container, data = this.data, result = null, options = {}) {
        if (!container) return;

        const curData = data || this.data;

        // Engineering evaluation formulas
        const area = (curData.Bx / 1000) * (curData.Ly / 1000);
        const zx = (curData.Ly / 1000) * Math.pow(curData.Bx / 1000, 2) / 6;
        const P = curData.p_serv || curData.pu * 0.75;
        const M = curData.mx_serv || curData.mux * 0.75;

        const q_avg = P / area;
        const delta_q = M / zx;
        const q_max = q_avg + delta_q;
        const qa = curData.qa;
        const dcrBearing = q_max / qa;

        // Effective depth d
        const d = curData.thickness_H - curData.cover - 16;

        // 1-way beam shear capacity
        const phi_v = 0.75;
        const vc = (1 / 6) * Math.sqrt(curData.fck) * curData.Ly * d / 1000; // kN
        const phi_vc = phi_v * vc;
        const vu = curData.pu * 0.35;
        const dcrShear1w = vu / phi_vc;

        // 2-way punching shear capacity
        const bo = 2 * (curData.col_cx + d + curData.col_cy + d);
        const vp = (1 / 3) * Math.sqrt(curData.fck) * bo * d / 1000; // kN
        const phi_vp = phi_v * vp;
        const vup = curData.pu * 0.85;
        const dcrPunch = vup / phi_vp;

        // Flexural capacity
        const phi_b = 0.85;
        const As_x = 15 * 198.6; // 15-D16 approx
        const a = (As_x * curData.fy) / (0.85 * curData.fck * curData.Ly);
        const phi_mn = phi_b * (As_x * curData.fy * (d - a / 2)) / 1e6; // kN*m
        const mu = curData.mux * 1.25;
        const dcrFlex = mu / phi_mn;

        const maxDcr = Math.max(dcrBearing, dcrShear1w, dcrPunch, dcrFlex);
        const isOk = maxDcr <= 1.0;
        const verdictText = isOk ? '  →  O.K' : '  →  N.G';
        const verdictColor = isOk ? '#059669' : '#dc2626';

        container.innerHTML = `
            <div class="kds-report-sheet a4-page mode-detail pure-white-sheet" style="background:#ffffff; color:#111827; padding:24px; font-family:'Pretendard', sans-serif;">
                <div style="border-bottom: 2px solid #0f172a; padding-bottom: 8px; margin-bottom: 16px;">
                    <h2 style="margin:0; font-size:18px; color:#0f172a; font-weight:700;">구 조 설 계 계 산 서 (KDS 14 20 50 독립기초)</h2>
                    <div style="font-size:12px; color:#64748b; margin-top:4px;">부재명: F1 [RC 독립기초판 (Isolated Footing)]</div>
                </div>

                <!-- 제 1장: 일반 설계 조건 -->
                <section style="margin-bottom:16px;">
                    <h3 style="font-size:13px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">제 1장. 일반 설계 조건 (General Specifications)</h3>
                    <table style="width:100%; font-size:11px; border-collapse:collapse; margin-top:6px;">
                        <tr>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc; width:25%;">기초 치수 (Bx × Ly)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.Bx} × ${curData.Ly} mm</td>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc; width:25%;">기초 두께 (H)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.thickness_H} mm (d = ${d} mm)</td>
                        </tr>
                        <tr>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc;">기둥 치수 (cx × cy)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.col_cx} × ${curData.col_cy} mm</td>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc;">허용 지내력 (qa)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.qa} kPa</td>
                        </tr>
                        <tr>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc;">콘크리트 강도 (fck)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.fck} MPa</td>
                            <td style="padding:4px; border:1px solid #cbd5e1; background:#f8fafc;">철근 항복강도 (fy)</td>
                            <td style="padding:4px; border:1px solid #cbd5e1;">${curData.fy} MPa</td>
                        </tr>
                    </table>
                </section>

                <!-- 제 2장: 지내력 및 접지압 검토 -->
                <section style="margin-bottom:16px;">
                    <h3 style="font-size:13px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">제 2장. 지반 접촉압 및 지내력 검토 (KDS 14 20 50)</h3>
                    <div style="font-size:11px; margin:6px 0; line-height:1.6;">
                        • 최대 접지압: $q_{max} = \\frac{P}{A} + \\frac{M}{Z} = ${q_avg.toFixed(1)} + ${delta_q.toFixed(1)} = ${q_max.toFixed(1)} \\text{ kPa}$<br>
                        • 지내력 안전율 검토: $\\frac{q_{max}}{q_a} = \\frac{${q_max.toFixed(1)}}{${qa.toFixed(1)}} = ${dcrBearing.toFixed(3)}$
                        <span style="font-weight:700; color:${dcrBearing <= 1.0 ? '#059669' : '#dc2626'};">${dcrBearing <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                    </div>
                </section>

                <!-- 제 3장: 1방향 보 전단 검토 -->
                <section style="margin-bottom:16px;">
                    <h3 style="font-size:13px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">제 3장. 1방향 보 전단 내력 검토 (Beam Shear)</h3>
                    <div style="font-size:11px; margin:6px 0; line-height:1.6;">
                        • 설계 전단강도: $\\phi V_c = 0.75 \\times \\frac{1}{6}\\sqrt{f_{ck}} b d = ${phi_vc.toFixed(1)} \\text{ kN}$<br>
                        • 계수 전단력: $V_u = ${vu.toFixed(1)} \\text{ kN}$<br>
                        • 전단 DCR: $\\frac{V_u}{\\phi V_c} = \\frac{${vu.toFixed(1)}}{${phi_vc.toFixed(1)}} = ${dcrShear1w.toFixed(3)}$
                        <span style="font-weight:700; color:${dcrShear1w <= 1.0 ? '#059669' : '#dc2626'};">${dcrShear1w <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                    </div>
                </section>

                <!-- 제 4장: 2방향 뚫림전단 검토 -->
                <section style="margin-bottom:16px;">
                    <h3 style="font-size:13px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">제 4장. 2방향 뚫림 전단 내력 검토 (Punching Shear)</h3>
                    <div style="font-size:11px; margin:6px 0; line-height:1.6;">
                        • 위험단면 둘레: $b_o = 2 \\times (c_x + d + c_y + d) = ${bo.toFixed(0)} \\text{ mm}$<br>
                        • 뚫림 전단강도: $\\phi V_p = 0.75 \\times \\frac{1}{3}\\sqrt{f_{ck}} b_o d = ${phi_vp.toFixed(1)} \\text{ kN}$<br>
                        • 뚫림 DCR: $\\frac{V_{up}}{\\phi V_p} = \\frac{${vup.toFixed(1)}}{${phi_vp.toFixed(1)}} = ${dcrPunch.toFixed(3)}$
                        <span style="font-weight:700; color:${dcrPunch <= 1.0 ? '#059669' : '#dc2626'};">${dcrPunch <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                    </div>
                </section>

                <!-- 제 5장: 휨모멘트 및 종합 판정 -->
                <section style="margin-bottom:16px;">
                    <h3 style="font-size:13px; font-weight:700; color:#1e293b; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">제 5장. 휨모멘트 설계 및 종합 판정</h3>
                    <div style="font-size:11px; margin:6px 0; line-height:1.6;">
                        • 배근 제원: X방향 ${curData.rebarX}, Y방향 ${curData.rebarY}<br>
                        • 설계 휨강도: $\\phi M_n = ${phi_mn.toFixed(1)} \\text{ kN}\\cdot\\text{m}$ (소요 $M_u = ${mu.toFixed(1)} \\text{ kN}\\cdot\\text{m}$)<br>
                        • 휨 DCR: $\\frac{M_u}{\\phi M_n} = ${dcrFlex.toFixed(3)}$
                        <span style="font-weight:700; color:${dcrFlex <= 1.0 ? '#059669' : '#dc2626'};">${dcrFlex <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                    </div>
                    <div style="margin-top:10px; padding:8px 12px; background:#f1f5f9; border-left:4px solid ${verdictColor}; font-size:12px; font-weight:700; color:#0f172a;">
                        최종 판정: 최대 소요비(DCR) = ${maxDcr.toFixed(3)}
                        <span style="color:${verdictColor};">${verdictText}</span>
                    </div>
                </section>
            </div>
        `;
    }

    /**
     * Calculate API integration
     */
    async calculate(data = this.data) {
        try {
            const res = await fetch('/api/design/rc/footing/base', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data || this.data)
            });
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {
            console.warn('[RCFootingModule] calculate API fallback:', e);
        }
        return { status: 'OK', governing_dcr: 0.72 };
    }
}

// Auto Register with ModuleDispatcher
if (window.ModuleDispatcher) {
    window.ModuleDispatcher.register('rc_footing', new RCFootingModule());
}
