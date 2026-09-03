// web/js/report/redcr/common/verdictBadge.js
/**
 * AltDP Member Designer - Report Verdict & Performance Badges
 * Zero-Build Vanilla JavaScript & Browser Global Namespace
 */

(function () {
    const H = (typeof window !== 'undefined' ? (window.RedcrFormat || (window.RedcrCommon && window.RedcrCommon.formatHelpers)) : null) || {
        esc: s => String(s),
        nf: (v, d = 3) => Number(v || 0).toFixed(d),
        dcrColor: d => (d <= 1.0 ? '#1a7a4a' : '#b00020'),
        okNg: p => (p ? '<span class="pass">OK ✓</span>' : '<span class="fail">NG ✗</span>')
    };

    const PERF_COLOR = {
        IO: '#1a7a4a',
        LS: '#b26a00',
        CP: '#8b3a00',
        collapse: '#b00020',
        OK: '#1a7a4a',
        NG: '#b00020',
        PASS: '#1a7a4a',
        FAIL: '#b00020'
    };

    function bigBadge(level) {
        const lv = level || '—';
        const color = PERF_COLOR[lv] ?? '#444';
        return `<span style="display:inline-block;padding:3px 12px;border-radius:3px;border:2px solid ${color};color:${color};font-weight:700;font-size:11pt">${H.esc(lv)}</span>`;
    }

    function levelBadge(level) {
        const lv = level || '—';
        const color = PERF_COLOR[lv] ?? '#444';
        return `<span style="display:inline-block;padding:1px 8px;border-radius:3px;border:1.5px solid ${color};color:${color};font-weight:700;font-size:9pt">${H.esc(lv)}</span>`;
    }

    /** 최악 성능수준 판별 helper */
    const PERF_ORDER = { IO: 0, LS: 1, CP: 2, collapse: 3 };
    function worstPerf(a, b) {
        if (!a) return b ?? '—';
        if (!b) return a;
        return (PERF_ORDER[a] ?? 0) >= (PERF_ORDER[b] ?? 0) ? a : b;
    }

    /** KDS 및 내진 종합 판정 배너 */
    function okNgBanner(isOk, governingDcr, governingMode) {
        const cls = isOk ? 'pass-banner' : 'fail-banner';
        const title = isOk ? '● KDS 기준 검토 만족 (PASS)' : '▲ KDS 기준 검토 초과 (FAIL)';
        const dcrText = governingDcr !== undefined ? `Governing DCR = ${H.nf(governingDcr, 3)}` : '';
        const modeText = governingMode ? ` (${H.esc(governingMode)})` : '';
        
        return `
<div class="${cls}" style="margin:10px 0;padding:8px 14px;border-radius:4px;border:1.5px solid ${isOk ? '#1a7a4a' : '#b00020'};background:${isOk ? '#e8f5e9' : '#ffebee'};display:flex;justify-content:space-between;align-items:center;">
    <div style="font-weight:700;font-size:11pt;color:${isOk ? '#1a7a4a' : '#b00020'};">${title}</div>
    <div style="font-weight:600;font-size:10pt;color:${isOk ? '#1a7a4a' : '#b00020'};">${dcrText}${modeText}</div>
</div>`;
    }

    const VerdictBadge = {
        PERF_COLOR,
        bigBadge,
        levelBadge,
        worstPerf,
        okNgBanner
    };

    if (typeof window !== 'undefined') {
        window.RedcrCommon = window.RedcrCommon || {};
        window.RedcrCommon.verdictBadge = VerdictBadge;
        window.RedcrVerdict = VerdictBadge;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = VerdictBadge;
    }
})();
