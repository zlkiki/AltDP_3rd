// web/js/report/result_renderer.js
/**
 * AltDP Member Designer - Master Result Dispatcher & A4 Fixed Sheet Controller
 * Supports Universal Dimensional Analysis (SI, SI-M, MKS, US) via localizeCanonicalReportHtml
 * - [Layer 1] Top Sticky Summary Toolbar & Zoom Controller Bar
 * - [Layer 2] Pure White Background (#ffffff) A4 Fixed Calculation Sheet (794px)
 * - [Layer 3] Dual View Modes: 4-Pillar Interactive Dashboard vs 8-Step Official A4 Sheet
 */

window.ResultRenderer = {
    currentResult: null,
    currentModulePath: '',
    currentInputs: null,
    viewMode: 'pillars', // 'pillars' | 'print_preview'

    // 모듈별 전용 re-DCR 직이식 렌더러 레지스트리 (1:1 완벽 일치 모듈만 등록, 나머지는 공용 4-Pillar Universal Engine 자동 적용)
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

    render(container, resultData, modulePath, inputParams) {
        if (!container) return;
        container.innerHTML = '';
        
        this.currentResult = resultData || null;
        this.currentModulePath = modulePath || '';
        this.currentInputs = inputParams || {};

        if (!resultData) {
            container.innerHTML = '<div class="empty-state">부재 파라미터를 입력하고 <b>[검토]</b> 또는 <b>[설계]</b> 버튼을 누르면 실시간 KDS 기준검토 계산서가 표시됩니다.</div>';
            return;
        }

        const dcr = Number(resultData.governing_dcr) || Number(resultData.max_dcr) || Number(resultData.dcr) || 0.0;
        const isOk = (resultData.status === 'OK' || resultData.status === 'PASS') && dcr <= 1.0;

        // 1. 상단 공통 Sticky 툴바 & Governing DCR 게이지 & 줌 컨트롤러 바
        const topToolbar = document.createElement('div');
        topToolbar.className = 'top-summary-toolbar sticky-toolbar';
        
        const pct = Math.min(dcr * 100, 100);
        const gaugeColor = dcr <= 0.85 ? '#10b981' : (dcr <= 1.0 ? '#f59e0b' : '#ef4444');
        const badgeClass = isOk ? 'badge-ok' : 'badge-ng';
        const badgeText = isOk ? '● PASS (만족)' : '▲ FAIL (초과)';

        topToolbar.innerHTML = `
            <div class="toolbar-left">
                <div class="status-pill ${badgeClass}">${badgeText}</div>
                <div class="dcr-indicator">
                    <span class="dcr-label">Governing DCR:</span>
                    <span class="dcr-number" style="color:${gaugeColor}">${dcr.toFixed(3)}</span>
                </div>
                <div class="mini-gauge-track">
                    <div class="mini-gauge-fill" style="width:${pct}%;background-color:${gaugeColor}"></div>
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
                    <button class="btn-toggle btn-view-pillars ${this.viewMode === 'pillars' ? 'active' : ''}" onclick="window.ResultRenderer.switchView('pillars')">📐 세부내용</button>
                    <button class="btn-toggle btn-view-print ${this.viewMode === 'print_preview' ? 'active' : ''}" onclick="window.ResultRenderer.switchView('print_preview')">👁️ 미리보기</button>
                </div>
                <button class="btn-print" onclick="window.ResultRenderer.printDocument()">🖨️ 인쇄</button>
            </div>
        `;
        container.appendChild(topToolbar);

        // 2. 줌 래퍼 및 메인 뷰포트 컨테이너 (항상 흰색 배경 고정)
        const zoomViewport = document.createElement('div');
        zoomViewport.className = 'a4-zoom-viewport';

        const mainViewport = document.createElement('div');
        mainViewport.id = 'main-result-viewport';
        mainViewport.className = 'main-result-viewport a4-sheet-container pure-white-sheet';
        
        zoomViewport.appendChild(mainViewport);
        container.appendChild(zoomViewport);

        // 3. 뷰 모드에 따른 렌더링 실행
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

        if (!this.currentResult) {
            viewport.innerHTML = '<div class="empty-state" style="padding:40px;text-align:center;color:#666;">부재 파라미터를 입력하고 <b>[검토]</b> 또는 <b>[설계]</b> 버튼을 누르면 실시간 KDS 기준검토 계산서가 표시됩니다.</div>';
            return;
        }

        const res = Object.assign({}, this.currentInputs || {}, this.currentResult || {});
        const mod = this.currentModulePath;
        const customType = this.moduleRegistry[mod];
        let rawHtml = '';

        if (this.viewMode === 'print_preview') {
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
                } else if (window.RedcrCommonRenderer) {
                    const commonHtml = document.createElement('div');
                    if (typeof window.RedcrCommonRenderer.renderA4Sheet === 'function') {
                        window.RedcrCommonRenderer.renderA4Sheet(commonHtml, res, mod, this.currentInputs);
                    } else {
                        window.RedcrCommonRenderer.render(commonHtml, res, mod, this.currentInputs);
                    }
                    rawHtml = commonHtml.innerHTML;
                } else {
                    rawHtml = `<pre class="fallback-json">${JSON.stringify(res, null, 2)}</pre>`;
                }
            } catch (err) {
                console.error('[ResultRenderer] Error rendering print preview:', err);
                rawHtml = `<div class="warn-box">미리보기 렌더링 중 오류가 발생했습니다: ${err.message}</div>`;
            }

            // Localize Canonical Report to Active Unit System
            const localized = typeof window.localizeCanonicalReportHtml === 'function'
                ? window.localizeCanonicalReportHtml(rawHtml)
                : rawHtml;

            const printWrap = document.createElement('div');
            printWrap.className = 'a4-print-container';
            printWrap.innerHTML = localized;
            viewport.appendChild(printWrap);
        } else {
            // 기본 종합 4대 영역 뷰 모드 (세부내용)
            try {
                if (window.RedcrCommonRenderer && typeof window.RedcrCommonRenderer.render === 'function') {
                    window.RedcrCommonRenderer.render(viewport, res, mod, this.currentInputs);
                    
                    // Localize text content in pillars view while preserving canvas
                    if (window.UnitManager && window.UnitManager.getCurrentSystem().id !== 'SI' && typeof window.localizeCanonicalReportHtml === 'function') {
                        const panels = viewport.querySelectorAll('.pillar-card .card-body:not(.canvas-body), .pillar-card .card-header');
                        panels.forEach(p => {
                            p.innerHTML = window.localizeCanonicalReportHtml(p.innerHTML);
                        });
                    }
                } else if (customType === 'beam' && window.RedcrBeamReport) {
                    const raw = window.RedcrBeamReport.generateBeamReportHTML(res);
                    viewport.innerHTML = typeof window.localizeCanonicalReportHtml === 'function' ? window.localizeCanonicalReportHtml(raw) : raw;
                } else if (customType === 'column' && window.RedcrColumnReport) {
                    const raw = window.RedcrColumnReport.generateColumnCheckReportHTML(res);
                    viewport.innerHTML = typeof window.localizeCanonicalReportHtml === 'function' ? window.localizeCanonicalReportHtml(raw) : raw;
                } else {
                    viewport.innerHTML = `<pre class="fallback-json">${JSON.stringify(res, null, 2)}</pre>`;
                }
            } catch (err) {
                console.error('[ResultRenderer] Error rendering pillars view:', err);
                viewport.innerHTML = `<div class="warn-box">세부내용 렌더링 중 오류가 발생했습니다: ${err.message}</div>`;
            }
        }
    },

    printDocument() {
        window.print();
    }
};
