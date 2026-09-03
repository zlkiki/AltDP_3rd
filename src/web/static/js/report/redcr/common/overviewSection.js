// web/js/report/redcr/common/overviewSection.js
/**
 * AltDP Member Designer - Overview & Environmental Parameter Section
 * Zero-Build Vanilla JavaScript & Browser Global Namespace
 */

(function () {
    const H = (typeof window !== 'undefined' ? (window.RedcrFormat || (window.RedcrCommon && window.RedcrCommon.formatHelpers)) : null) || {
        esc: s => String(s || ''),
        nf: (v, d = 3) => Number(v || 0).toFixed(d)
    };
    const F = (typeof window !== 'undefined' ? window.RedcrFormulas : null) || {
        sectionHeader: (n, t, k) => `<h2>${n} ${t}</h2>`,
        inputBlock: (t, r) => `<div><b>${t}</b></div>`
    };

    function overviewSection(p) {
        if (!p) return '';
        const zoneLabel = { Z1: '1구역 (0.11g)', Z2: '2구역 (0.07g)' };
        const detailLabel = { seismic: '내진배근 상세', non_seismic: '일반 비내진 상세' };
        
        const rows = [
            { label: '지진구역 (Seismic Zone)', value: zoneLabel[p.seismicZone] ?? (p.seismicZone || '1구역'), unit: '' },
            { label: '지반 분류 (Site Class)', value: p.siteClass || 'S4 (연약지반)', unit: '' },
            { label: '중요도 계수 (Importance Factor Ie)', value: p.importance ?? 1.2, unit: '' },
            { label: '목표 성능수준 (Target Level)', value: p.performanceTarget || '인명안전 (LS)', unit: '' },
            { label: '설계 상세구분 (Design Detail)', value: detailLabel[p.seismicDetail] ?? (p.seismicDetail || '내진상세'), unit: '' },
            { label: '감쇠비 (Damping Ratio)', value: `${((p.dampingRatio ?? 0.05) * 100).toFixed(0)} %`, unit: '' }
        ];

        return F.sectionHeader('1', '설계 및 평가 개요 (Evaluation Overview)', 'KDS 14 20 / KDS 41 17')
            + F.inputBlock('설계 환경 및 내진 성능 파라미터', rows);
    }

    if (typeof window !== 'undefined') {
        window.RedcrCommon = window.RedcrCommon || {};
        window.RedcrCommon.overviewSection = overviewSection;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { overviewSection };
    }
})();
