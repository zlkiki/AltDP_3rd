// web/js/report/redcr/detailWrapper.js
// 부재 상세 계산서 최종 HTML 문서 래핑 (A4 및 @media print 최적화)

(function () {
    function wrapDetailDocument(evalTitle, subtitle, sets, projectName = '') {
        const wrapSeismicSheet = (window.RedcrSeismicUtils && window.RedcrSeismicUtils.wrapSeismicSheet) ||
            ((t, s, b) => b);

        if (!sets || sets.length === 0) {
            return wrapSeismicSheet(evalTitle, subtitle, `<div class="warn-box"><b>선택된 부재의 계산 결과가 없습니다.</b></div>`, projectName);
        }
        
        const body = sets.map((s, i) => `
<div class="detail-set${i === 0 ? ' first' : ''}" data-set-index="${i + 1}">
${s.bodyHtml}
</div>
`).join('\n');

        const FONT_UI = `'Segoe UI', 'Segoe UI Variable', 'Malgun Gothic', '맑은 고딕', Arial, sans-serif`;
        const FONT_NUM = `Consolas, 'Courier New', monospace`;
        const extraCss = `
<style>
.no-print { display: none !important; }
body { font-family: ${FONT_UI}; font-size: 10pt; color: #222; }
h1 { font-family: ${FONT_UI}; font-size: 14pt; }
h2 { font-family: ${FONT_UI}; font-size: 11pt; page-break-after: avoid; }
table, th, td { font-family: ${FONT_UI}; font-size: 10pt; }
td.num, .calc-block, .calc-formula, .calc-sub, .calc-result, .calc-note,
.inp-val, code { font-family: ${FONT_NUM}; font-size: 10pt; }
.calc-title { font-family: ${FONT_UI}; font-size: 10.5pt; }
.meta, .note-box, .warn-box { font-size: 9pt; }
.inp-unit { font-size: 9pt; }

.detail-set { page-break-before: always; }
.detail-set.first { page-break-before: auto; }
.detail-set-header { padding:4px 0 6px; border-bottom:1.5px solid #1a3a5c; margin-bottom:8px; }
table { page-break-inside: avoid; }
.calc-block { page-break-inside: avoid; }
</style>
`;
        return wrapSeismicSheet(evalTitle, subtitle, extraCss + body, projectName);
    }

    const DetailWrapper = { wrapDetailDocument };

    if (typeof window !== 'undefined') {
        window.RedcrDetailWrapper = DetailWrapper;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = DetailWrapper;
    }
})();
