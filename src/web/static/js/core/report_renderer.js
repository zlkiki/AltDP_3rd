/**
 * AltDP_3rd 5-Chapter KDS Structural Calculation Report Renderer (report_renderer.js)
 * Conforms to KDS Standard 5-Section Structural Calculation Report Specification
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
        const flexure = r.flexure || {};
        const shear = r.shear || {};

        const mu = r.Mu ?? flexure.Mu ?? m.mu ?? 0;
        const vu = r.Vu ?? shear.Vu ?? m.vu ?? 0;
        const pu = r.Pu ?? m.pu ?? 0;
        const tu = r.Tu ?? m.tu ?? 0;

        const phiMn = r.phi_Mn ?? flexure.phi_Mn ?? r.phiMn ?? 0;
        const phiVn = r.phi_Vn ?? shear.phi_Vn ?? r.phiVn ?? 0;

        const dcrFlex = r.dcrFlex ?? flexure.dcr ?? (phiMn > 0 ? (mu / phiMn) : 0);
        const dcrShear = r.dcrShear ?? shear.dcr ?? (phiVn > 0 ? (vu / phiVn) : 0);
        const maxDcr = Number(r.governing_dcr ?? r.max_dcr ?? Math.max(dcrFlex, dcrShear));

        const hasResult = Boolean(r.status || phiMn > 0 || phiVn > 0 || maxDcr > 0);
        const isOk = hasResult && (r.status === 'OK' || r.status === 'PASS' || maxDcr <= 1.0) && maxDcr <= 1.0;
        const verdictText = hasResult ? (isOk ? '  →  O.K' : '  →  N.G') : '  →  [검토 대기]';
        const verdictClass = hasResult ? (isOk ? 'verdict-ok' : 'verdict-ng') : 'verdict-wip';

        if (this.currentMode === 'input') {
            container.innerHTML = this._renderInputMode(m);
            return;
        }

        let html = `
            <div class="kds-report-sheet a4-page mode-${this.currentMode} pure-white-sheet">
                <!-- Header Title -->
                <div class="report-header-banner">
                    <div class="report-main-title">구 조 설 계 계 산 서 (KDS 14 20 00)</div>
                    <div class="report-sub-title">Member: ${m.name || 'RC-MEMBER'} [${m.type || 'RC 부재'}]</div>
                </div>

                <!-- 제 1장: 일반 설계 조건 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 1장. 일반 설계 조건 (General Information)</h3>
                    <table class="report-data-table">
                        <tr><td>프로젝트명</td><td>AltDP_3rd KDS Automated Design</td><td>설계 일자</td><td>${new Date().toISOString().slice(0, 10)}</td></tr>
                        <tr><td>적용 기준</td><td>KDS 14 20 00 콘크리트구조설계기준</td><td>내진 등급</td><td>${m.seismic_grade || '보통모멘트골조'}</td></tr>
                        <tr><td>환경 조건</td><td>${m.environment || '일반 옥내 (건조 환경)'}</td><td>단위계</td><td>SI Unit (kN, mm, MPa)</td></tr>
                    </table>
                </section>

                <!-- 제 2장: 재질 및 단면 제원 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 2장. 재질 및 단면 제원 (Material & Section Properties)</h3>
                    <div class="chapter-split">
                        <table class="report-data-table flex-1">
                            <tr><th>구분</th><th>설계값</th><th>단위</th></tr>
                            <tr><td>콘크리트 압축강도 ($f_{ck}$)</td><td>${m.fck || '-'}</td><td>MPa</td></tr>
                            <tr><td>주철근 항복강도 ($f_y$)</td><td>${m.fy || '-'}</td><td>MPa</td></tr>
                            <tr><td>단면 폭 ($b$) x 높이 ($h$)</td><td>${m.b || '-'} x ${m.h || '-'}</td><td>mm</td></tr>
                            <tr><td>유효깊이 ($d$) / 피복 ($d_c$)</td><td>${m.h && m.cover ? (m.h - m.cover) : '-'} / ${m.cover || '-'}</td><td>mm</td></tr>
                            <tr><td>상부 주철근</td><td>${m.topBars || m.top_rebar || '-'}</td><td>-</td></tr>
                            <tr><td>하부 주철근</td><td>${m.botBars || m.bot_rebar || '-'}</td><td>-</td></tr>
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
                        <strong>지배 하중 조합:</strong> ${r.governing_lcb || r.lcb || '위험 하중조합 (Governing LCB) 산정 대기'}
                    </div>
                    <table class="report-data-table">
                        <tr><th>설계 휨모멘트 ($M_u$)</th><th>설계 전단력 ($V_u$)</th><th>계수 축력 ($P_u$)</th><th>비틀림 모멘트 ($T_u$)</th></tr>
                        <tr><td>${mu ? Number(mu).toFixed(2) + ' kN·m' : '-'}</td><td>${vu ? Number(vu).toFixed(2) + ' kN' : '-'}</td><td>${pu ? Number(pu).toFixed(2) + ' kN' : '-'}</td><td>${tu ? Number(tu).toFixed(2) + ' kN·m' : '-'}</td></tr>
                    </table>
                </section>

                <!-- 제 4장: 단면 안전성 정밀 검토 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 4장. 단면 안전성 정밀 검토 (Step-by-Step Code Verification)</h3>
                    ${hasResult ? `
                    <div class="verification-block">
                        <div class="check-item-header">1. 휨모멘트 강도 검토 (KDS 14 20 20)</div>
                        <div class="calc-eval-row">
                            <span>소요모멘트 $M_u = ${Number(mu).toFixed(2)} \\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${Number(phiMn).toFixed(2)} \\text{ kN}\\cdot\\text{m}$</span>
                            <span class="eval-badge ${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">(DCR = ${dcrFlex.toFixed(3)})${dcrFlex <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                        </div>
                    </div>

                    <div class="verification-block">
                        <div class="check-item-header">2. 전단 강도 검토 (KDS 14 20 22)</div>
                        <div class="calc-eval-row">
                            <span>소요전단력 $V_u = ${Number(vu).toFixed(2)} \\text{ kN} \\le \\phi V_n = ${Number(phiVn).toFixed(2)} \\text{ kN}$</span>
                            <span class="eval-badge ${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">(DCR = ${dcrShear.toFixed(3)})${dcrShear <= 1.0 ? '  →  O.K' : '  →  N.G'}</span>
                        </div>
                    </div>
                    ` : `
                    <div class="verification-block empty-calc-notice" style="padding:16px;text-align:center;color:#64748b;background:#f8fafc;border-radius:4px;">
                        <span>KDS 기준 수식 전개식 계산 대기 중입니다. 상단 툴바의 <b>[⚡ 검토]</b> 또는 <b>[✨ 설계]</b> 버튼을 누르면 동적 계산이 수행됩니다.</span>
                    </div>
                    `}
                </section>

                <!-- 제 5장: 종합 안전성 판정 -->
                <section class="report-chapter">
                    <h3 class="chapter-title">제 5장. 종합 안전성 판정 (Executive Summary & Final Verdict)</h3>
                    ${hasResult ? `
                    <table class="report-data-table summary-verdict-table">
                        <thead><tr><th>검토 항목</th><th>설계 부재력</th><th>설계 강도</th><th>안전율 (DCR)</th><th>판정 결과</th></tr></thead>
                        <tbody>
                            <tr><td>휨모멘트 (Flexure)</td><td>${Number(mu).toFixed(2)} kN·m</td><td>${Number(phiMn).toFixed(2)} kN·m</td><td>${dcrFlex.toFixed(3)}</td><td class="${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${dcrFlex <= 1.0 ? '  →  O.K' : '  →  N.G'}</td></tr>
                            <tr><td>전단력 (Shear)</td><td>${Number(vu).toFixed(2)} kN</td><td>${Number(phiVn).toFixed(2)} kN</td><td>${dcrShear.toFixed(3)}</td><td class="${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${dcrShear <= 1.0 ? '  →  O.K' : '  →  N.G'}</td></tr>
                        </tbody>
                    </table>
                    <div class="final-verdict-banner ${isOk ? 'banner-ok' : 'banner-ng'}">
                        최종 구조 안전성 판정 : <strong>${isOk ? '적합 (SAFE / O.K)' : '부적합 (OVERSTRESSED / N.G)'} (최대 DCR = ${maxDcr.toFixed(3)})</strong>
                    </div>
                    ` : `
                    <div class="final-verdict-banner banner-wip" style="background:#f1f5f9;border:1px dashed #cbd5e1;color:#475569;padding:12px;text-align:center;border-radius:4px;">
                        구조 안전성 판정 대기 중 (WIP)
                    </div>
                    `}
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
