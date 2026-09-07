// web/js/report/result_renderer.js
/**
 * AltDP Member Designer - Master Result Dispatcher & A4 Fixed Sheet Controller
 * Supports Universal Dimensional Analysis (SI, SI-M, MKS, US) via localizeCanonicalReportHtml
 * - [Layer 1] Top Sticky Summary Toolbar & Zoom Controller Bar
 * - [Layer 2] Pure White Background (#ffffff) A4 Fixed Calculation Sheet (794px)
 * - [Layer 3] KDS 3-Mode Report & 5-Chapter Standard Calculation Sheet (docs/07, docs/14)
 */

window.ResultRenderer = {
    currentResult: null,
    currentModulePath: '',
    currentInputs: null,
    viewMode: 'pillars', // 'pillars' (상세내용) | 'print_preview' (인쇄미리보기)

    // 모듈별 전용 상세 계산서 렌더러 레지스트리 (1:1 완벽 일치 모듈만 등록, 나머지는 KDS 5대 장구분 표준 시트 자동 적용)
    moduleRegistry: {
        // RC 1:1 매칭 전용 계산서
        'rc/beam/base': 'beam',
        'rc/beam/tsect': 'beam',
        'rc/beam/reinf': 'beam',
        'rc/column/base': 'column',
        'rc/column/reinf': 'column',
        'rc/column/irreg': 'column',
        'rc/column/bar_stress': 'column',
        'rc/wall/base': 'wall',
        'rc/wall/bmt': 'wall',
        'rc/wall/canti': 'wall',
        'rc/footing/base': 'footing',
        'rc/footing/com': 'footing',
        'rc/footing/pile_cap': 'footing',
        'rc/footing/reinf': 'footing',
        'rc/slab/base': 'slab',
        'rc/slab/slab_1way': 'slab',
        'rc/slab/pro': 'slab',
        'rc/slab/sog': 'slab',
        'rc/slab/reinf': 'slab',

        // Steel 1:1 매칭 전용 계산서
        'steel/member/beam': 'steel',
        'steel/member/column': 'steel',
        'steel/connection/baseplate': 'steel'
    },

    /**
     * docs/14 5대 장구분 규격에 기반한 상시 순백색(#ffffff) A4 계산서 WIP 표준 시트
     */
    renderA4WIPSheet(container, modMeta = {}, inputParams = {}, resultData = {}) {
        if (!container) return;

        const meta = modMeta || {};
        const memberName = meta.name || meta.key || this.currentModulePath || '구조 부재';
        const tier = meta.tier || 'Tier 3';
        const midasDlg = meta.midas_dlg || '';
        const std = meta.standard || 'KDS 국가건설기준';
        const dateStr = new Date().toISOString().slice(0, 10);
        const inputs = Object.assign({}, this.currentInputs || {}, inputParams || {});

        const inputRows = [];
        const labelMap = {
            fck: '콘크리트 설계강도 (fck)',
            fy: '주철근 항복강도 (fy)',
            fys: '전단철근 항복강도 (fys)',
            b: '단면 폭 (b)',
            h: '단면 춤 (h)',
            B: '폭 (B)',
            H: '높이 (H)',
            L: '경간/길이 (L)',
            cover: '피복 두께 (cover)',
            Mu: '소요 휨모멘트 (Mu)',
            Vu: '소요 전단력 (Vu)',
            Pu: '소요 축력 (Pu)'
        };
        Object.entries(inputs).forEach(([k, v]) => {
            if (v !== undefined && v !== null && typeof v !== 'object') {
                const label = labelMap[k] || k;
                inputRows.push(`<tr><td style="padding:6px 10px;border:1px solid #e2e8f0;font-weight:600;background:#f8fafc;width:40%;">${label}</td><td style="padding:6px 10px;border:1px solid #e2e8f0;">${v}</td></tr>`);
            }
        });

        const html = `
        <div class="a4-sheet-page pure-white-sheet" style="background:#ffffff;padding:36px 44px;color:#0f172a;box-sizing:border-box;font-family:'Pretendard', 'Segoe UI', sans-serif;">
            <!-- 상단 문서 표제부 -->
            <div style="border-bottom:2px solid #0f172a;padding-bottom:12px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:flex-end;">
                <div>
                    <div style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;">KDS STRUCTURAL CALCULATION REPORT (WIP)</div>
                    <h1 style="margin:4px 0 0;font-size:22px;font-weight:800;color:#0f172a;">${memberName} 구조계산서</h1>
                </div>
                <div style="text-align:right;font-size:11px;color:#64748b;line-height:1.6;">
                    <div><b>검토일자:</b> ${dateStr}</div>
                    <div><b>검토엔진:</b> AltDP_3rd KDS Automated Solver</div>
                    <div><b>적용기준:</b> ${std}</div>
                </div>
            </div>

            <!-- 부재 정보 뱃지 배너 -->
            <div style="background:#f1f5f9;border-left:4px solid #3b82f6;padding:10px 14px;border-radius:0 4px 4px 0;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:12px;color:#334155;">
                    <span style="font-weight:700;background:#e2e8f0;padding:2px 8px;border-radius:4px;margin-right:8px;font-size:11px;">${tier}</span>
                    <b>원본앱 식별 코드:</b> <code style="font-family:Consolas, monospace;color:#1e40af;">${midasDlg || 'N/A'}</code>
                </div>
                <div style="font-size:11px;color:#64748b;">상시 순백색 A4 표준 고정 (#ffffff)</div>
            </div>

            <!-- 제 1장: 일반 설계 조건 -->
            <section style="margin-bottom:24px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 1장. 일반 설계 조건 (General Information)</h2>
                <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;width:20%;font-weight:600;">적용 설계기준</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;width:30%;">${std}</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;width:20%;font-weight:600;">단위계</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;width:30%;">SI Unit (kN, mm, MPa)</td>
                    </tr>
                    <tr>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;font-weight:600;">모듈 구분</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;">${memberName} (${meta.key || 'WIP'})</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;background:#f8fafc;font-weight:600;">진행 상태</td>
                        <td style="padding:6px 10px;border:1px solid #e2e8f0;color:#d97706;font-weight:700;">개발 준비 중 (WIP)</td>
                    </tr>
                </table>
            </section>

            <!-- 제 2장: 재질 및 단면 제원 -->
            <section style="margin-bottom:24px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 2장. 재질 및 단면 제원 (Material & Section Properties)</h2>
                ${inputRows.length > 0 ? `
                <table style="width:100%;border-collapse:collapse;font-size:11.5px;">
                    ${inputRows.join('')}
                </table>
                ` : `
                <div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:12px;border-radius:4px;font-size:11.5px;color:#64748b;text-align:center;">
                    제원 데이터 수신 대기 중 (Left-Sub 입력폼에서 제원을 입력하십시오)
                </div>
                `}
            </section>

            <!-- 제 3장: 소요 설계 하중 -->
            <section style="margin-bottom:24px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 3장. 소요 설계 하중 (Design Loads & Load Combinations)</h2>
                <div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:12px;border-radius:4px;font-size:11.5px;color:#64748b;text-align:center;">
                    위험 하중조합 (Governing LCB) 산정 준비 중
                </div>
            </section>

            <!-- 제 4장: 단면 안전성 정밀 검토 -->
            <section style="margin-bottom:24px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 4장. 단면 안전성 정밀 검토 (Step-by-Step Code Verification)</h2>
                <div style="background:#f8fafc;border:1px dashed #cbd5e1;padding:18px;border-radius:4px;text-align:center;">
                    <div style="font-size:24px;margin-bottom:6px;">📐</div>
                    <div style="font-size:12px;font-weight:700;color:#334155;margin-bottom:4px;">KDS 공식 수식 전개식 작성 예정 (WIP)</div>
                    <div style="font-size:11px;color:#64748b;">본 부재의 원본앱 1:1 KDS 수치 해석 엔진 및 단계별 상세 수식 전개식이 순차 탑재됩니다.</div>
                </div>
            </section>

            <!-- 제 5장: 종합 안전성 판정 -->
            <section style="margin-bottom:24px;">
                <h2 style="font-size:14px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;">제 5장. 종합 안전성 판정 (Executive Summary & Final Verdict)</h2>
                <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:14px;display:flex;align-items:center;gap:14px;">
                    <div style="font-size:24px;color:#d97706;">⏳</div>
                    <div>
                        <div style="font-size:13px;font-weight:800;color:#92400e;margin-bottom:2px;">종합 판정: [미구현 (WIP)]</div>
                        <div style="font-size:11.5px;color:#b45309;">본 부재(${memberName})는 전용 KDS 계산서 개발 로드맵에 따라 순차 탑재됩니다. 가짜 강도치나 임의의 O.K 판정을 배제하고 정직한 WIP 상태를 유지합니다.</div>
                    </div>
                </div>
            </section>

            <!-- 문서 바닥글 -->
            <div style="border-top:1px solid #e2e8f0;padding-top:12px;margin-top:32px;display:flex;justify-content:space-between;font-size:10.5px;color:#94a3b8;">
                <span>AltDP_3rd Structural Member Designer — KDS Engineering Engine</span>
                <span>Page 1 / 1</span>
            </div>
        </div>
        `;

        container.innerHTML = html;
    },

    render(container, resultData, modulePath, inputParams) {
        if (!container) return;
        container.innerHTML = '';
        
        this.currentResult = resultData || null;
        this.currentModulePath = modulePath || '';
        this.currentInputs = inputParams || {};

        const isWip = !resultData || 
                      resultData.status === 'NOT_YET_IMPLEMENTED' || 
                      resultData.code === 'WIP_MODULE';

        const dcr = Number((resultData && (resultData.governing_dcr || resultData.max_dcr || resultData.dcr)) || 0.0);
        const hasResult = Boolean(resultData && resultData.status && resultData.status !== 'NOT_YET_IMPLEMENTED');
        const isOk = hasResult && (resultData.status === 'OK' || resultData.status === 'PASS' || dcr <= 1.0) && dcr <= 1.0;

        // 1. 상단 공통 Sticky 툴바 & Governing DCR 게이지 & 줌 컨트롤러 바
        const topToolbar = document.createElement('div');
        topToolbar.className = 'top-summary-toolbar sticky-toolbar';
        
        const pct = Math.min(dcr * 100, 100);
        const gaugeColor = !hasResult ? '#94a3b8' : (dcr <= 0.85 ? '#10b981' : (dcr <= 1.0 ? '#f59e0b' : '#ef4444'));
        const badgeClass = !hasResult ? 'badge-wip' : (isOk ? 'badge-ok' : 'badge-ng');
        const badgeText = !hasResult ? '⏳ WIP (준비중)' : (isOk ? '● PASS (만족)' : '▲ FAIL (초과)');
        const dcrDisplay = hasResult ? dcr.toFixed(3) : '대기중';

        topToolbar.innerHTML = `
            <div class="toolbar-left">
                <div class="status-pill ${badgeClass}" style="${!hasResult ? 'background:#f1f5f9;color:#64748b;border:1px solid #cbd5e1;' : ''}">${badgeText}</div>
                <div class="dcr-indicator">
                    <span class="dcr-label">Governing DCR:</span>
                    <span class="dcr-number" style="color:${gaugeColor}">${dcrDisplay}</span>
                </div>
                <div class="mini-gauge-track">
                    <div class="mini-gauge-fill" style="width:${hasResult ? pct : 0}%;background-color:${gaugeColor}"></div>
                </div>
            </div>
            
            <div class="toolbar-center zoom-toolbar-group">
                <button class="zoom-btn" id="btn-zoom-out" title="축소 (−10%)">−</button>
                <input type="range" id="report-zoom-slider" min="0.5" max="2.0" step="0.05" value="1.0" title="확대율 슬라이더">
                <button class="zoom-btn" id="btn-zoom-in" title="확대 (+10%)">+</button>
                <span class="zoom-label" id="zoom-level-label">100%</span>
                <button class="zoom-btn-mini" id="btn-zoom-reset" title="100% 기본 크기">100%</button>
                <button class="zoom-btn-mini" id="btn-zoom-fit" title="창 너비 맞춤">Fit</button>
            </div>

            <div class="toolbar-right">
                <div class="view-toggle-group">
                    <button class="btn-toggle btn-view-pillars ${this.viewMode === 'pillars' ? 'active' : ''}" onclick="window.ResultRenderer.switchView('pillars')">📐 상세내용</button>
                    <button class="btn-toggle btn-view-print ${this.viewMode === 'print_preview' ? 'active' : ''}" onclick="window.ResultRenderer.switchView('print_preview')">👁️ 미리보기</button>
                </div>
                <button class="btn-print" onclick="window.ResultRenderer.printDocument()">🖨️ 인쇄</button>
            </div>
        `;
        container.appendChild(topToolbar);

        // 2. 줌 래퍼 및 메인 뷰포트 컨테이너 (항상 순백색 배경 고정)
        const zoomViewport = document.createElement('div');
        zoomViewport.className = 'a4-zoom-viewport';

        const mainViewport = document.createElement('div');
        mainViewport.id = 'main-result-viewport';
        mainViewport.className = 'main-result-viewport a4-sheet-container pure-white-sheet';
        
        zoomViewport.appendChild(mainViewport);
        container.appendChild(zoomViewport);

        // 3. 뷰포트 렌더링 실행
        this.renderViewport(mainViewport);

        // 4. 줌 컨트롤러 초기화
        if (window.ZoomController) {
            window.ZoomController.init();
        }
    },

    switchView(mode) {
        this.viewMode = mode;
        const vp = document.getElementById('main-result-viewport');
        if (vp) {
            this.renderViewport(vp);
        }
        document.querySelectorAll('.btn-view-pillars').forEach(btn => {
            btn.classList.toggle('active', mode === 'pillars');
        });
        document.querySelectorAll('.btn-view-print').forEach(btn => {
            btn.classList.toggle('active', mode === 'print_preview');
        });
    },

    renderViewport(viewport) {
        if (!viewport) return;
        viewport.innerHTML = '';

        const mod = this.currentModulePath;
        const modMeta = (window.allModules && window.allModules.find(m => m.key === mod)) || {
            key: mod,
            name: mod || '선택 부재',
            tier: 'Tier 3',
            engine_status: 'WIP'
        };

        const isWip = !this.currentResult || 
                      this.currentResult.status === 'NOT_YET_IMPLEMENTED' || 
                      this.currentResult.code === 'WIP_MODULE';

        if (isWip) {
            this.renderA4WIPSheet(viewport, modMeta, this.currentInputs, this.currentResult);
            return;
        }

        const res = Object.assign({}, this.currentInputs || {}, this.currentResult || {});
        const customType = this.moduleRegistry[mod];
        let rawHtml = '';

        try {
            if (customType === 'beam' && window.RedcrBeamReport && typeof window.RedcrBeamReport.generateBeamReportHTML === 'function') {
                rawHtml = window.RedcrBeamReport.generateBeamReportHTML(res);
            } else if (customType === 'column' && window.RedcrColumnReport && typeof window.RedcrColumnReport.generateColumnCheckReportHTML === 'function') {
                rawHtml = window.RedcrColumnReport.generateColumnCheckReportHTML(res);
            } else if (customType === 'steel' && window.RedcrSteelReport && typeof window.RedcrSteelReport.generateSteelReportHTML === 'function') {
                rawHtml = window.RedcrSteelReport.generateSteelReportHTML(res);
            } else if (customType === 'wall' && window.RedcrWallReport && typeof window.RedcrWallReport.generateWallReportHTML === 'function') {
                rawHtml = window.RedcrWallReport.generateWallReportHTML(res);
            } else if (customType === 'footing' && window.RedcrFootingReport && typeof window.RedcrFootingReport.generateFootingReportHTML === 'function') {
                rawHtml = window.RedcrFootingReport.generateFootingReportHTML(res);
            } else if (customType === 'slab' && window.RedcrSlabReport && typeof window.RedcrSlabReport.generateSlabReportHTML === 'function') {
                rawHtml = window.RedcrSlabReport.generateSlabReportHTML(res);
            } else if (window.RedcrCommonRenderer && typeof window.RedcrCommonRenderer.renderA4Sheet === 'function') {
                const commonWrap = document.createElement('div');
                window.RedcrCommonRenderer.renderA4Sheet(commonWrap, res, mod, this.currentInputs);
                rawHtml = commonWrap.innerHTML;
            } else {
                this.renderA4WIPSheet(viewport, modMeta, this.currentInputs, this.currentResult);
                return;
            }
        } catch (err) {
            console.error('[ResultRenderer] Error rendering report:', err);
            rawHtml = `<div class="warn-box" style="padding:16px;background:#fef2f2;border:1px solid #fecaca;color:#991b1b;border-radius:4px;">계산서 렌더링 중 오류가 발생했습니다: ${err.message}</div>`;
        }

        // Localize Canonical Report to Active Unit System
        const localized = typeof window.localizeCanonicalReportHtml === 'function'
            ? window.localizeCanonicalReportHtml(rawHtml)
            : rawHtml;

        const printWrap = document.createElement('div');
        printWrap.className = 'a4-print-container pure-white-sheet';
        printWrap.innerHTML = localized;
        viewport.appendChild(printWrap);
    },

    printDocument() {
        window.print();
    }
};
