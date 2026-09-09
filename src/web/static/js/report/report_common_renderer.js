// web/js/report/report_common_renderer.js
/**
 * AltDP_3rd Master Universal KDS Calculation Report Generator (report_common_renderer.js)
 * Conforms to docs/07 (Pure White #ffffff A4 Fixed Sheet) and docs/14 (5-Chapter KDS Structure)
 * Standard Global Object: window.ReportCommonRenderer
 * Fully retires legacy 4-pillar cards and arbitrary check table mocks.
 */

window.ReportCommonRenderer = {
    /**
     * Master render entry point.
     * Guaranteed pure white (#ffffff) A4 fixed sheet layout without legacy cards.
     */
    render(container, resultData, currentModulePath, inputParams) {
        if (!container) return;

        const isWip = !resultData || 
                      resultData.status === 'NOT_YET_IMPLEMENTED' || 
                      resultData.code === 'WIP_MODULE';

        if (isWip) {
            const modMeta = (window.allModules && window.allModules.find(m => m.key === currentModulePath)) || {
                key: currentModulePath,
                name: currentModulePath || '선택 부재',
                tier: 'Tier 3',
                engine_status: 'WIP'
            };
            if (window.ResultRenderer && typeof window.ResultRenderer.renderA4WIPSheet === 'function') {
                window.ResultRenderer.renderA4WIPSheet(container, modMeta, inputParams, resultData);
                return;
            }
        }

        // Render pure white A4 5-chapter sheet for computed results
        this.renderA4Sheet(container, resultData, currentModulePath, inputParams);
    },

    /**
     * Render KDS Standard 5-Chapter Calculation Sheet in Pure White (#ffffff) A4 format.
     */
    renderA4Sheet(container, resultData, currentModulePath, inputParams) {
        if (!container) return;

        const res = resultData || {};
        const inp = inputParams || res.inputs || {};
        const modMeta = (window.allModules && window.allModules.find(m => m.key === currentModulePath)) || {
            name: currentModulePath || '단위부재',
            standard: 'KDS 국가건설기준'
        };
        const modName = modMeta.name || currentModulePath || '단위부재';
        const std = modMeta.standard || 'KDS 국가건설기준';

        const dcr = Number(res.governing_dcr || res.max_dcr || res.dcr || 0.0);
        const hasResult = Boolean(res.status && res.status !== 'NOT_YET_IMPLEMENTED');
        const isOk = hasResult && (res.status === 'OK' || res.status === 'PASS' || dcr <= 1.0) && dcr <= 1.0;

        const dateStr = new Date().toISOString().slice(0, 10);

        let html = `
        <div class="a4-sheet-page pure-white-sheet altdp-report" style="background:#ffffff;padding:36px 44px;color:#0f172a;box-sizing:border-box;font-family:'Pretendard', 'Segoe UI', sans-serif;">
            <!-- Header Banner -->
            <div style="border-bottom:2px solid #0f172a;padding-bottom:12px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:flex-end;">
                <div>
                    <div style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;">KDS STRUCTURAL CALCULATION REPORT</div>
                    <h1 style="margin:4px 0 0;font-size:22px;font-weight:800;color:#0f172a;">${modName} 구조계산서</h1>
                </div>
                <div style="text-align:right;font-size:11px;color:#64748b;line-height:1.6;">
                    <div><b>검토일자:</b> ${dateStr}</div>
                    <div><b>검토엔진:</b> AltDP_3rd KDS Solver</div>
                    <div><b>적용기준:</b> ${std}</div>
                </div>
            </div>

            <!-- 제 1장. 일반 설계 조건 -->
            <section style="margin-bottom:22px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 1장. 일반 설계 조건 (General Design Criteria)</h2>
                <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;width:20%;font-weight:600;">적용 설계기준</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;width:30%;">${std}</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;width:20%;font-weight:600;">단위계</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;width:30%;">SI Unit (kN, mm, MPa)</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;font-weight:600;">부재 식별</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;">${modName}</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;font-weight:600;">설계 상태</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;font-weight:700;color:${isOk ? '#059669' : '#dc2626'};">${hasResult ? (isOk ? '설계기준 만족 (OK)' : '설계기준 초과 (NG)') : '검토 대기 중'}</td>
                    </tr>
                </table>
            </section>

            <!-- 제 2장. 재질 및 단면 제원 -->
            <section style="margin-bottom:22px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 2장. 재질 및 단면 제원 (Material & Section Properties)</h2>
                ${this.generateInputsTableHtml(inp, res)}
            </section>

            <!-- 제 3장. 소요 설계 하중 -->
            <section style="margin-bottom:22px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 3장. 소요 설계 하중 (Design Loads & Load Combinations)</h2>
                <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:8px 12px;border-radius:4px;font-size:11.5px;margin-bottom:8px;">
                    <b>지배 하중 조합 (Governing LCB):</b> ${res.governing_lcb || res.lcb || '1.2D + 1.6L (설계하중)'}
                </div>
                ${this.generateForcesTableHtml(inp, res)}
            </section>

            <!-- 제 4장. 단면 안전성 정밀 검토 -->
            <section style="margin-bottom:22px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 4장. 단면 안전성 정밀 검토 (Step-by-Step Code Verification)</h2>
                ${this.generateVerificationTableHtml(res)}
            </section>

            <!-- 제 5장. 종합 안전성 판정 -->
            <section style="margin-bottom:22px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 5장. 종합 안전성 판정 (Executive Summary & Final Verdict)</h2>
                ${hasResult ? `
                <div style="background:${isOk ? '#ecfdf5' : '#fef2f2'};border:1px solid ${isOk ? '#a7f3d0' : '#fecaca'};border-radius:6px;padding:14px;display:flex;align-items:center;gap:14px;">
                    <div style="font-size:24px;color:${isOk ? '#059669' : '#dc2626'};">${isOk ? '✓' : '⚠'}</div>
                    <div>
                        <div style="font-size:13px;font-weight:800;color:${isOk ? '#065f46' : '#991b1b'};margin-bottom:2px;">
                            ${isOk ? 'KDS 구조설계기준 만족 (STRUCTURAL INTEGRITY OK)' : 'KDS 구조설계기준 초과 (LIMIT STATE EXCEEDED)'}
                        </div>
                        <div style="font-size:11.5px;color:${isOk ? '#047857' : '#b91c1c'};">
                            본 부재 단면의 Governing DCR은 <b>${dcr.toFixed(3)}</b>로, 허용 한계상태(1.000)를 ${isOk ? '만족하여 구조적으로 안전합니다.' : '초과하여 단면 증대 또는 배근 보강이 필요합니다.'}
                        </div>
                    </div>
                </div>
                ` : `
                <div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:12px;border-radius:4px;font-size:11.5px;color:#64748b;text-align:center;">
                    구조 안전성 판정 대기 중 (실시간 검토 필요)
                </div>
                `}
            </section>

            <!-- Footer -->
            <div style="border-top:1px solid #e2e8f0;padding-top:12px;margin-top:32px;display:flex;justify-content:space-between;font-size:10.5px;color:#94a3b8;">
                <span>AltDP_3rd Structural Member Designer — KDS Engineering Engine</span>
                <span>Page 1 / 1</span>
            </div>
        </div>
        `;

        container.innerHTML = html;
    },

    generateInputsTableHtml(inp, res) {
        const src = Object.assign({}, inp || {}, res.inputs || {});
        const rows = [];
        const labelMap = {
            fck: { label: '콘크리트 설계강도 (fck)', unit: 'MPa' },
            fy: { label: '주철근 항복강도 (fy)', unit: 'MPa' },
            fys: { label: '전단철근 항복강도 (fys)', unit: 'MPa' },
            fyt: { label: '전단철근 항복강도 (fyt)', unit: 'MPa' },
            b: { label: '단면 폭 (b)', unit: 'mm' },
            h: { label: '단면 춤 (h)', unit: 'mm' },
            B: { label: '단면 폭 (B)', unit: 'mm' },
            H: { label: '단면 높이 (H)', unit: 'mm' },
            L: { label: '경간/길이 (L)', unit: 'mm' },
            cover: { label: '피복 두께 (cover)', unit: 'mm' },
            grade: { label: '강재 강종 (Grade)', unit: '' },
            steel_grade: { label: '강재 강종 (Grade)', unit: '' }
        };

        Object.keys(labelMap).forEach(k => {
            if (src[k] !== undefined && src[k] !== null && src[k] !== '') {
                const item = labelMap[k];
                rows.push(`<tr><td style="padding:5px 8px;border:1px solid #e2e8f0;background:#f8fafc;width:40%;font-weight:600;">${item.label}</td><td style="padding:5px 8px;border:1px solid #e2e8f0;">${src[k]} ${item.unit}</td></tr>`);
            }
        });

        if (rows.length === 0) {
            return '<div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:10px;text-align:center;font-size:11.5px;color:#64748b;">입력된 파라미터 제원이 없습니다.</div>';
        }

        return `<table style="width:100%;border-collapse:collapse;font-size:11.5px;">${rows.join('')}</table>`;
    },

    generateForcesTableHtml(inp, res) {
        const src = Object.assign({}, inp || {}, res.inputs || {}, res);
        const mu = src.Mu ?? src.mu ?? (res.flexure && res.flexure.Mu);
        const vu = src.Vu ?? src.vu ?? (res.shear && res.shear.Vu);
        const pu = src.Pu ?? src.pu ?? (res.axial && res.axial.Pu);
        const tu = src.Tu ?? src.tu;

        return `
        <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
            <thead>
                <tr style="background:#f8fafc;">
                    <th style="padding:6px;border:1px solid #e2e8f0;text-align:center;">설계 휨모멘트 (Mu)</th>
                    <th style="padding:6px;border:1px solid #e2e8f0;text-align:center;">설계 전단력 (Vu)</th>
                    <th style="padding:6px;border:1px solid #e2e8f0;text-align:center;">계수 축력 (Pu)</th>
                    <th style="padding:6px;border:1px solid #e2e8f0;text-align:center;">비틀림 모멘트 (Tu)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding:6px;border:1px solid #e2e8f0;text-align:center;">${mu !== undefined ? Number(mu).toFixed(2) + ' kN·m' : '-'}</td>
                    <td style="padding:6px;border:1px solid #e2e8f0;text-align:center;">${vu !== undefined ? Number(vu).toFixed(2) + ' kN' : '-'}</td>
                    <td style="padding:6px;border:1px solid #e2e8f0;text-align:center;">${pu !== undefined ? Number(pu).toFixed(2) + ' kN' : '-'}</td>
                    <td style="padding:6px;border:1px solid #e2e8f0;text-align:center;">${tu !== undefined ? Number(tu).toFixed(2) + ' kN·m' : '-'}</td>
                </tr>
            </tbody>
        </table>
        `;
    },

    generateVerificationTableHtml(res) {
        const checkRows = [];

        // 1. Flexure
        if (res.flexure || res.phi_Mn || res.phiMn_kNm) {
            const flex = res.flexure || res;
            const demand = Number(flex.Mu ?? flex.Mu_kNm ?? res.Mu ?? 0);
            const capacity = Number(flex.phi_Mn ?? flex.phiMn_kNm ?? res.phi_Mn ?? 0);
            const dcr = capacity > 0 ? (demand / capacity) : Number(flex.dcr || 0);
            checkRows.push({
                item: '휨 강도 검토 (Flexure)',
                std: 'KDS 14 20 20 / KDS 14 31 10',
                demand: `${demand.toFixed(2)} kN·m`,
                capacity: `${capacity.toFixed(2)} kN·m`,
                dcr: dcr.toFixed(3),
                pass: dcr <= 1.0
            });
        }

        // 2. Shear
        if (res.shear || res.phi_Vn || res.phiVn_kN) {
            const sh = res.shear || res;
            const demand = Number(sh.Vu ?? sh.Vu_kN ?? res.Vu ?? 0);
            const capacity = Number(sh.phi_Vn ?? sh.phiVn_kN ?? res.phi_Vn ?? 0);
            const dcr = capacity > 0 ? (demand / capacity) : Number(sh.dcr || 0);
            checkRows.push({
                item: '전단 강도 검토 (Shear)',
                std: 'KDS 14 20 22 / KDS 14 31 10',
                demand: `${demand.toFixed(2)} kN`,
                capacity: `${capacity.toFixed(2)} kN`,
                dcr: dcr.toFixed(3),
                pass: dcr <= 1.0
            });
        }

        // 3. Axial / Interaction
        if (res.interaction || res.pm || res.axial) {
            const ax = res.interaction || res.pm || res.axial;
            const dcr = Number(ax.dcr ?? ax.governing_dcr ?? res.governing_dcr ?? 0);
            checkRows.push({
                item: '축력 및 P-M 상관비 (Interaction)',
                std: 'KDS 14 20 20 / KDS 14 31 10',
                demand: `${dcr.toFixed(3)}`,
                capacity: '1.000',
                dcr: dcr.toFixed(3),
                pass: dcr <= 1.0
            });
        }

        // 4. Bearing / Soil
        if (res.soil || res.bearing || res.qa) {
            const soil = res.soil || res;
            const demand = Number(soil.q_max ?? soil.qmax ?? 0);
            const capacity = Number(soil.q_a ?? soil.qa ?? 0);
            const dcr = capacity > 0 ? (demand / capacity) : Number(soil.dcr || 0);
            checkRows.push({
                item: '지반 지지력 검토 (Soil Bearing)',
                std: 'KDS 14 20 70',
                demand: `${demand.toFixed(2)} kPa`,
                capacity: `${capacity.toFixed(2)} kPa`,
                dcr: dcr.toFixed(3),
                pass: dcr <= 1.0
            });
        }

        if (checkRows.length === 0) {
            return `
            <div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:14px;border-radius:4px;text-align:center;font-size:11.5px;color:#64748b;">
                KDS 기준 수식 전개식 계산 대기 중입니다. [⚡ 검토]를 실행하십시오.
            </div>
            `;
        }

        return `
        <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
            <thead>
                <tr style="background:#f8fafc;">
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:left;">검토 항목</th>
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:left;">설계 기준</th>
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:right;">소요 부재력</th>
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:right;">설계 내력</th>
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:center;">안전율 (DCR)</th>
                    <th style="padding:6px 10px;border:1px solid #e2e8f0;text-align:center;">판정</th>
                </tr>
            </thead>
            <tbody>
                ${checkRows.map(r => `
                <tr>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;font-weight:600;">${r.item}</td>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;color:#64748b;">${r.std}</td>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;text-align:right;">${r.demand}</td>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;text-align:right;">${r.capacity}</td>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;text-align:center;font-weight:700;">${r.dcr}</td>
                    <td style="padding:6px 10px;border:1px solid #e2e8f0;text-align:center;font-weight:700;color:${r.pass ? '#059669' : '#dc2626'};">${r.pass ? 'OK' : 'NG'}</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
        `;
    }
};

// Backwards compatibility
window.RedcrCommonRenderer = window.ReportCommonRenderer;
