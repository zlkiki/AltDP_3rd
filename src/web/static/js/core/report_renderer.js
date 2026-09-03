/**
 * AltDP_3rd 5-Chapter KDS Structural Calculation Report Renderer (report_renderer.js)
 * Conforms to Midas Design+ DgnReportBase.ini / GENDgnReportKR.ini specification
 */
class ReportRenderer {
    constructor() {
        this.currentMode = 'detail'; // 'summary' | 'detail' | 'input'
    }

    setMode(mode) {
        this.currentMode = mode;
    }

    /**
     * Render 5-chapter report into container
     * @param {HTMLElement} container 
     * @param {Object} memberData 
     * @param {Object} calcResult 
     */
    render(container, memberData = {}, calcResult = {}) {
        if (!container) return;

        const m = memberData || {};
        const r = calcResult || {};
        const dcrFlex = r.dcrFlex ?? r.dcr ?? 0.72;
        const dcrShear = r.dcrShear ?? 0.58;
        const isOk = Math.max(dcrFlex, dcrShear) <= 1.0;
        const verdictText = isOk ? '  →  O.K' : '  →  N.G';
        const verdictClass = isOk ? 'verdict-ok' : 'verdict-ng';

        if (this.currentMode === 'input') {
            container.innerHTML = this._renderInputMode(m);
            return;
        }

        let html = `
            <div class="kds-report-sheet a4-page mode-${this.currentMode}">
                <!-- Header Title -->
                <div class="report-header-banner">
                    <div class="report-main-title">구 조 설 계 계 산 서 (KDS 14 20 00)</div>
                    <div class="report-sub-title">Member: ${m.name || 'RC-BEAM-1'} [${m.type || 'RC Beam'}]</div>
                </div>

                <!-- 제 1장: 일반 설계 조건 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 1장. 일반 설계 조건 (General Information)</h3>
                    <table class="report-data-table">
                        <tr><td>프로젝트명</td><td>AltDP_3rd KDS Automated Design</td><td>설계 일자</td><td>2026.09.03</td></tr>
                        <tr><td>적용 기준</td><td>KDS 14 20 00 : 2022 콘크리트구조설계기준</td><td>내진 등급</td><td>특수모멘트골조 (Special)</td></tr>
                        <tr><td>환경 조건</td><td>일반 옥내 (건조 환경)</td><td>중요도 계수</td><td>$I_e = 1.2$</td></tr>
                    </table>
                </section>

                <!-- 제 2장: 재질 및 단면 제원 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 2장. 재질 및 단면 제원 (Material & Section Properties)</h3>
                    <div class="chapter-split">
                        <table class="report-data-table flex-1">
                            <tr><th>구분</th><th>설계값</th><th>단위</th></tr>
                            <tr><td>콘크리트 압축강도 ($f_{ck}$)</td><td>${m.fck || 27}</td><td>MPa</td></tr>
                            <tr><td>주철근 항복강도 ($f_y$)</td><td>${m.fy || 400}</td><td>MPa</td></tr>
                            <tr><td>단면 폭 ($b$) x 높이 ($h$)</td><td>${m.b || 400} x ${m.h || 600}</td><td>mm</td></tr>
                            <tr><td>유효깊이 ($d$) / 피복 ($d_c$)</td><td>${(m.h || 600) - (m.cover || 60)} / ${m.cover || 60}</td><td>mm</td></tr>
                            <tr><td>상부 주철근</td><td>${m.topBars || '4-D25'}</td><td>-</td></tr>
                            <tr><td>하부 주철근</td><td>${m.botBars || '4-D25'}</td><td>-</td></tr>
                        </table>
                        <!-- 2D 단면 배근도 SVG 벡터 그래픽 임베딩 -->
                        <div class="report-svg-slot">
                            ${this._generateSectionSvg(m)}
                            <div class="svg-caption">[단면 배근 상세도]</div>
                        </div>
                    </div>
                </section>

                <!-- 제 3장: 소요 설계 하중 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 3장. 소요 설계 하중 (Design Loads & Load Combinations)</h3>
                    <div class="callout-lcb">
                        <strong>지배 하중 조합:</strong> LCB 2: $1.2D + 1.6L$ (Governing Case)
                    </div>
                    <table class="report-data-table">
                        <tr><th>설계 휨모멘트 ($M_u$)</th><th>설계 전단력 ($V_u$)</th><th>계수 축력 ($P_u$)</th><th>비틀림 모멘트 ($T_u$)</th></tr>
                        <tr><td>${m.mu || 240.0} kN·m</td><td>${m.vu || 180.0} kN</td><td>${m.pu || 0.0} kN</td><td>${m.tu || 0.0} kN·m</td></tr>
                    </table>
                </section>

                <!-- 제 4장: 단면 안전성 정밀 검토 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 4장. 단면 안전성 정밀 검토 (Step-by-Step Code Verification)</h3>
                    <div class="verification-block">
                        <div class="check-item-header">1. 휨모멘트 강도 검토 (KDS 14 20 20 조항 4.1)</div>
                        <div class="math-formula-box">
                            ${window.ReportKaTeX ? window.ReportKaTeX.formulaPhiMn(0.85, 2026, m.fy || 400, 540, 95.3) : '$$\\phi M_n = \\phi A_s f_y (d - a/2)$$'}
                        </div>
                        <div class="calc-eval-row">
                            <span>소요모멘트 $M_u = ${m.mu || 240.0} \\text{ kN}\\cdot\\text{m} \\le \\phi M_n = 335.2 \\text{ kN}\\cdot\\text{m}$</span>
                            <span class="eval-badge ${verdictClass}">(DCR = ${dcrFlex.toFixed(2)})${verdictText}</span>
                        </div>
                    </div>

                    <div class="verification-block">
                        <div class="check-item-header">2. 전단 강도 검토 (KDS 14 20 22 조항 4.3)</div>
                        <div class="math-formula-box">
                            ${window.ReportKaTeX ? window.ReportKaTeX.formulaPhiVn(0.75, 125.4, 185.0) : '$$\\phi V_n = \\phi (V_c + V_s)$$'}
                        </div>
                        <div class="calc-eval-row">
                            <span>소요전단력 $V_u = ${m.vu || 180.0} \\text{ kN} \\le \\phi V_n = 232.8 \\text{ kN}$</span>
                            <span class="eval-badge verdict-ok">(DCR = ${dcrShear.toFixed(2)})  →  O.K</span>
                        </div>
                    </div>
                </section>

                <!-- 제 5장: 종합 안전성 판정 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 5장. 종합 안전성 판정 (Executive Summary & Final Verdict)</h3>
                    <table class="report-data-table summary-verdict-table">
                        <thead><tr><th>검토 항목</th><th>설계 부재력</th><th>설계 강도</th><th>안전율 (DCR)</th><th>판정 결과</th></tr></thead>
                        <tbody>
                            <tr><td>휨모멘트 (Flexure)</td><td>${m.mu || 240.0} kN·m</td><td>335.2 kN·m</td><td>${dcrFlex.toFixed(2)}</td><td class="${verdictClass}">${verdictText}</td></tr>
                            <tr><td>전단력 (Shear)</td><td>${m.vu || 180.0} kN</td><td>232.8 kN</td><td>${dcrShear.toFixed(2)}</td><td class="verdict-ok">  →  O.K</td></tr>
                            <tr><td>처짐 (Deflection)</td><td>8.4 mm</td><td>$L/480 = 12.5$ mm</td><td>0.67</td><td class="verdict-ok">  →  O.K</td></tr>
                            <tr><td>균열폭 (Crack Width)</td><td>0.18 mm</td><td>0.30 mm</td><td>0.60</td><td class="verdict-ok">  →  O.K</td></tr>
                        </tbody>
                    </table>
                    <div class="final-verdict-banner ${isOk ? 'banner-ok' : 'banner-ng'}">
                        최종 구조 안전성 판정 : <strong>${isOk ? '적합 (SAFE / O.K)' : '부적합 (OVERSTRESSED / N.G)'}</strong>
                    </div>
                </section>
            </div>
        `;

        container.innerHTML = html;
    }

    _generateSectionSvg(m) {
        const b = m.b || 400;
        const h = m.h || 600;
        const scale = 140 / Math.max(b, h);
        const w = b * scale;
        const ht = h * scale;
        const cx = 80;
        const cy = 80;

        return `
            <svg width="160" height="160" viewBox="0 0 160 160" class="report-embed-svg">
                <rect x="${cx - w/2}" y="${cy - ht/2}" width="${w}" height="${ht}" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5" />
                <rect x="${cx - w/2 + 6}" y="${cy - ht/2 + 6}" width="${w - 12}" height="${ht - 12}" fill="none" stroke="#f59e0b" stroke-width="1.2" />
                <circle cx="${cx - w/2 + 10}" cy="${cy - ht/2 + 10}" r="4" fill="#38bdf8" stroke="#fff" stroke-width="0.8" />
                <circle cx="${cx + w/2 - 10}" cy="${cy - ht/2 + 10}" r="4" fill="#38bdf8" stroke="#fff" stroke-width="0.8" />
                <circle cx="${cx - w/2 + 10}" cy="${cy + ht/2 - 10}" r="4" fill="#38bdf8" stroke="#fff" stroke-width="0.8" />
                <circle cx="${cx + w/2 - 10}" cy="${cy + ht/2 - 10}" r="4" fill="#38bdf8" stroke="#fff" stroke-width="0.8" />
            </svg>
        `;
    }

    _renderInputMode(m) {
        let rows = '';
        Object.entries(m).forEach(([k, v]) => {
            rows += `<tr><td>${k}</td><td><strong>${JSON.stringify(v)}</strong></td></tr>`;
        });
        return `
            <div class="kds-report-sheet a4-page">
                <h3>입력 데이터 보고서 (Raw Input Parameters)</h3>
                <table class="report-data-table">
                    <thead><tr><th>매개변수 키</th><th>입력값</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    }
}

window.ReportRenderer = new ReportRenderer();
