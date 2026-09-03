// web/js/report/redcr/seismicSheetUtils.js
// 내진성능평가 및 KDS 상세 계산서 공통 유틸 (Vanilla JS & UMD)

(function () {
    const F = (typeof window !== 'undefined' ? window.RedcrFormulas : null) || {};
    const esc = F.esc || ((s) => String(s));
    const FORMULA_CSS = F.FORMULA_CSS || '';

    /** 소수점 d자리, 천단위 콤마 없음 */
    function nf(v, d = 3) {
        if (v === Number.POSITIVE_INFINITY)
            return 'INF';
        if (!Number.isFinite(v))
            return '—';
        return v.toFixed(d);
    }

    /** 단위 포함 표시 */
    function nfu(v, unit, d = 2) {
        return `${nf(v, d)} ${unit}`;
    }

    /** 합격/불합격/N/A 태그 */
    function passTag(pass) {
        if (pass === true)
            return '<span class="pass">PASS ✓</span>';
        if (pass === false)
            return '<span class="fail">FAIL ✗</span>';
        return '<span style="color:#888">— (N/A)</span>';
    }

    /** 단순 정보 행 (label: value unit) */
    function infoRow(label, value, unit = '') {
        const v = typeof value === 'number' ? nf(value, 3) : esc(String(value));
        const u = unit ? ` <span style="color:#888;font-size:9.5pt">${esc(unit)}</span>` : '';
        return `<tr>
  <td style="padding:3px 10px 3px 0;color:#444;font-weight:600;white-space:nowrap">${esc(label)}</td>
  <td style="padding:3px 0;font-family:Consolas,'Courier New',monospace">${v}${u}</td>
</tr>`;
    }

    /** 가로 정보 테이블 래퍼 */
    function infoTable(title, rows) {
        return `<div style="margin:8px 0 12px">
<div style="font-weight:700;color:#1a3a5c;margin-bottom:4px;font-size:11pt">${esc(title)}</div>
<table style="border-collapse:collapse;font-size:10.5pt">
${rows.join('\n')}
</table>
</div>\n`;
    }

    /** 판정 배지 */
    function verdictBadge(text, pass) {
        const cls = pass ? 'pass' : 'fail';
        return `<span class="${cls}" style="font-size:12pt;padding:2px 8px;border:1px solid currentColor;border-radius:2px">${esc(text)}</span>`;
    }

    /** A4 HTML 래퍼 */
    function wrapSeismicSheet(evalTitle, subtitle, bodyHtml, projectName = '') {
        const date = new Date().toISOString().slice(0, 10);
        const proj = projectName ? esc(projectName) : 'KDS Member Designer';
        return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>${esc(evalTitle)}</title>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family:'Segoe UI','Malgun Gothic','맑은 고딕',Arial,sans-serif; font-size:11pt; color:#222; margin:0; }
  .page { width:178mm; margin:0 auto; }
  h1 { font-size:15pt; color:#1a3a5c; border-bottom:2.5px solid #1a3a5c; padding-bottom:4px; margin:0 0 4px; }
  h2 { font-size:12pt; font-weight:700; color:#1a3a5c; border-bottom:1px solid #bbb;
       padding-bottom:3px; margin:18px 0 6px; page-break-after:avoid; }
  table { border-collapse:collapse; width:100%; margin:4px 0; }
  th { border:1px solid #bbb; padding:4px 8px; background:#e8eef4; font-weight:600;
       text-align:left; font-size:10.5pt; }
  td { border:1px solid #bbb; padding:4px 8px; font-size:10.5pt; }
  td.num { font-family:Consolas,'Courier New',monospace; text-align:right; }
  td.ctr { text-align:center; }
  .meta { font-size:9pt; color:#666; margin-bottom:14px; }
  .pass  { color:#1a7a4a; font-weight:700; }
  .fail  { color:#b00020; font-weight:700; }
  .warn  { color:#7a5c00; font-weight:700; }
  .note-box { background:#e8f4fd; border-left:3px solid #1976d2; padding:4px 8px; margin:6px 0; font-size:10pt; }
  .warn-box { background:#fff8e1; border-left:3px solid #f9a825; padding:4px 8px; margin:6px 0; font-size:10pt; }
  .no-print { display:block; }
  @media print { .no-print { display:none !important; } }
  ${FORMULA_CSS}
</style>
</head>
<body>
<div class="no-print" style="position:fixed;top:8px;right:12px;z-index:999">
  <button onclick="window.print()"
    style="padding:6px 18px;background:#1a3a5c;color:#fff;border:none;border-radius:3px;
           font-size:11pt;cursor:pointer;font-family:inherit">
    🖨 Print / PDF
  </button>
</div>
<div class="page">
  <h1>${esc(evalTitle)}</h1>
  <div class="meta">
    <span>${esc(subtitle)}</span> &nbsp;|&nbsp;
    <span>프로젝트: ${proj}</span> &nbsp;|&nbsp;
    <span>출력일자: ${date}</span> &nbsp;|&nbsp;
    <span>설계기준: KDS Standard</span>
  </div>
  ${bodyHtml}
</div>
</body>
</html>`;
    }

    const SeismicSheetUtils = {
        nf, nfu, passTag, infoRow, infoTable, verdictBadge, wrapSeismicSheet
    };

    if (typeof window !== 'undefined') {
        window.RedcrSeismicUtils = SeismicSheetUtils;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = SeismicSheetUtils;
    }
})();
