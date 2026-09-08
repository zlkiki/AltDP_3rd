/**
 * AltDP_3rd Structural Calculation Report Renderer Bridge (report_renderer.js)
 * Legacy 5-chapter report renderer has been deprecated and unified into ReportEngine (report_engine.js).
 * All render() calls are directly delegated to window.ReportEngine to ensure 1:1 original app calculation sheet.
 */
class ReportRenderer {
    constructor() {
        this.currentMode = 'detail';
    }

    setMode(mode) {
        this.currentMode = mode;
        if (window.ReportEngine && typeof window.ReportEngine.setReportMode === 'function') {
            window.ReportEngine.setReportMode(mode);
        }
    }

    /**
     * Render KDS structural calculation report via unified ReportEngine
     * @param {HTMLElement} container 
     * @param {Object} memberData 
     * @param {Object} calcResult 
     * @param {Object} [options]
     */
    render(container, memberData = {}, calcResult = {}, options = {}) {
        if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
            const moduleKey = memberData.moduleKey || memberData.type?.toLowerCase().replace(/\s+/g, '_') || 'rc_beam';
            window.ReportEngine.render(container, memberData, calcResult, moduleKey);
            return;
        }

        console.warn('[ReportRenderer] window.ReportEngine not found, rendering fallback notice.');
        if (container) {
            container.innerHTML = `
                <div class="a4-sheet-container pure-white-sheet" style="padding:40px; text-align:center;">
                    <h3>구조계산서 로딩 중...</h3>
                </div>
            `;
        }
    }

    /**
     * Legacy 5-Chapter Architecture Reference (Unified into ReportEngine KaTeX Sheet):
     * - 제 1장. 설계 개요 및 적용 기준 (Design Overview)
     * - 제 2장. 재료 성질 및 설계 강도 (Material Properties)
     * - 제 3장. 단면 제원 및 배근 상세 (Section Geometry & Detailing)
     * - 제 4장. 부재력 및 단면 내력 검토 (Member Forces & Capacities:   →  O.K /   →  N.G)
     * - 제 5장. 사용성 및 내구성 검토 (Serviceability & Durability)
     */
    _generateSectionSvg(data) {
        return '';
    }
}

window.ReportRenderer = new ReportRenderer();
