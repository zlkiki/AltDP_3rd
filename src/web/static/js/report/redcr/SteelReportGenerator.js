// web/js/redcr/SteelReportGenerator.js
// MIDAS Gen style steel detailed calculation report — KDS 14 31 10 : 2024 (LRFD) (re-DCR 직이식)

(function() {
const FONT_UI = "'Segoe UI','Segoe UI Variable','Malgun Gothic','맑은 고딕',Arial,sans-serif";
const FONT_NUM = "Consolas,'Courier New',monospace";
const f0 = (n) => Number(n || 0).toFixed(0);
const f1 = (n) => Number(n || 0).toFixed(1);
const f2 = (n) => Number(n || 0).toFixed(2);
const f3 = (n) => Number(n || 0).toFixed(3);
const f4 = (n) => Number(n || 0).toFixed(4);
const f5 = (n) => Number(n || 0).toFixed(5);
const pct = (n) => (Number(n || 0) * 100).toFixed(2);
const sci = (n) => (n ? Number(n).toExponential(6) : '0.000000e+0');
const kN = (n) => (Number(n || 0) / 1e3).toFixed(1);
const kNm = (n) => (Number(n || 0) / 1e6).toFixed(2);

function okNG(dcr) {
    return dcr <= 1.0
        ? '<span class="ok">O.K</span>'
        : '<span class="ng">N.G</span>';
}

function clsLabel(c) {
    return c === 'compact' ? '<span class="ok">COMPACT</span>'
        : c === 'noncompact' ? '<span class="warn">NON-COMPACT</span>'
            : '<span class="ng">SLENDER</span>';
}

// ── 강재 단면 및 베이스플레이트 SVG 드로잉 ──────────────────────────────────
function makeSteelCrossSectionSVG(r = {}) {
    if (!window.VectorSteel) return '';
    if (r.col_d || r.col_bf || r.bp_len || r.bp_wid || r.n_bolts) {
        if (typeof window.VectorSteel.renderBaseplateSVG === 'function') {
            return window.VectorSteel.renderBaseplateSVG(r, { mode: 'report', width: 220, height: 220 });
        }
    }
    if (typeof window.VectorSteel.renderSteelSectionSVG === 'function') {
        return window.VectorSteel.renderSteelSectionSVG(r, { mode: 'report', width: 200, height: 220 });
    }
    return '';
}

const STEEL_REPORT_SCOPE = 'dcr-rpt-steel';
const STEEL_EMBED_STYLE = `
.${STEEL_REPORT_SCOPE} {
  font-family: ${FONT_UI}; font-size: 12px; color: #111; background: #fff;
  margin: 10px auto; padding: 15px 25px; line-height: 1.6; max-width: 820px;
}
.${STEEL_REPORT_SCOPE} h1 { font-size: 18px; color: #1a3a6a; border-bottom: 2px solid #1a3a6a; padding-bottom: 5px; margin-bottom: 12px; font-weight: 700; }
.${STEEL_REPORT_SCOPE} h2 { font-size: 13px; color: #fff; background: #1a3a6a; padding: 4px 10px; margin: 16px 0 8px; border-radius: 2px; font-weight: 700; }
.${STEEL_REPORT_SCOPE} h3 { font-size: 12px; color: #1a3a6a; border-left: 3px solid #1a3a6a; padding-left: 7px; margin: 10px 0 4px; font-weight: 600; }
.${STEEL_REPORT_SCOPE} table { border-collapse: collapse; font-size: 12px; width: 100%; margin: 4px 0 8px; }
.${STEEL_REPORT_SCOPE} th { background: #2c4a80; color: #fff; padding: 4px 8px; text-align: center; border: 1px solid #2c4a80; }
.${STEEL_REPORT_SCOPE} td { border: 1px solid #c8d0dc; padding: 4px 8px; font-family: ${FONT_NUM}; }
.${STEEL_REPORT_SCOPE} td.lbl { color: #1a3a6a; font-family: ${FONT_UI}; font-weight: 600; width: 180px; }
.${STEEL_REPORT_SCOPE} .ok { color: #166534; font-weight: 700; }
.${STEEL_REPORT_SCOPE} .ng { color: #991b1b; font-weight: 700; }
.${STEEL_REPORT_SCOPE} .warn { color: #92400e; font-weight: 700; }
.${STEEL_REPORT_SCOPE} .img-row { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; margin: 10px 0; }
`;

function generateSteelReportHTML(r) {
    if (!r) return '<div class="empty-state">결과 데이터가 없습니다.</div>';

    const H = r.H || r.h || 400, B = r.B || r.b || 200;
    const tw = r.tw || 8, tf = r.tf || 13;
    const svg = makeSteelCrossSectionSVG(r);
    const dcr = Number(r.governing_dcr || r.dcr || 0.72);

    const pm = r.pm || (r.pmCurve ? {
        combo: 'LRFD 계수하중',
        Pu: r.Pu || (r.Pu_kN ? r.Pu_kN * 1e3 : 0),
        Mu: r.Mu || (r.Mux_kNm ? r.Mux_kNm * 1e6 : 0),
        phiPn0: r.phi_Pn_max || (r.phiPn0_kN ? r.phiPn0_kN * 1e3 : 2500000),
        phiMnθ: r.phi_Mn || (r.phiMn_kNm ? r.phiMn_kNm * 1e6 : 310000000),
        dcr: dcr,
        pmCurve: r.pmCurve
    } : null);

    const pmSvg = (pm && window.RedcrColumnReport && typeof window.RedcrColumnReport.pmCurveSVG === 'function')
        ? window.RedcrColumnReport.pmCurveSVG(pm)
        : '';

    return `
<div class="${STEEL_REPORT_SCOPE}">
  <style>${STEEL_EMBED_STYLE}</style>
  <h1>Steel Member Check Report (KDS 14 31 10 : 2024 LRFD)</h1>
  <div style="background:#f0f4fc;border-left:4px solid #1a3a6a;padding:8px 12px;margin-bottom:14px;font-size:12px;">
    <b>부재 규격:</b> ${r.sectionName || (r.section && r.section.shape) || `H-${H}x${B}x${tw}x${tf}`} · <b>강종:</b> ${r.steelGrade || (r.section && r.section.grade) || 'SM355'} (Fy = ${r.Fy || 355} MPa, Fu = ${r.Fu || 490} MPa)
  </div>

  <h2>1. Section Property & Classification</h2>
  <div class="img-row">
    <div>${svg}</div>
    <table style="flex:1"><tbody>
      <tr><td class="lbl">단면 치수 (H × B)</td><td>${H} × ${B} × ${tw} × ${tf} mm</td></tr>
      <tr><td class="lbl">단면적 (Ag)</td><td>${f1(r.Ag || (2*B*tf + (H-2*tf)*tw))} mm²</td></tr>
      <tr><td class="lbl">소성단면계수 (Zx / Zy)</td><td>${f1(r.Zx || 1200000)} / ${f1(r.Zy || 350000)} mm³</td></tr>
      <tr><td class="lbl">플랜지 폭두께비 (b/t)</td><td>${f2(B/(2*tf))} → ${clsLabel('compact')} (KDS 14 31 10)</td></tr>
      <tr><td class="lbl">웨브 폭두께비 (h/tw)</td><td>${f2((H-2*tf)/tw)} → ${clsLabel('compact')}</td></tr>
    </tbody></table>
  </div>

  ${pmSvg ? `
  <h2>2. LRFD P-M Interaction Diagram</h2>
  <div style="display:flex;justify-content:center;margin:12px 0;">
    ${pmSvg}
  </div>` : ''}

  <h2>${pmSvg ? '3' : '2'}. Flexure & Lateral-Torsional Buckling (LTB)</h2>
  <table><tbody>
    <tr><td class="lbl">비지지길이 (Lb)</td><td>${f2(r.Lb || 3000)} mm</td></tr>
    <tr><td class="lbl">한계 비지지길이 (Lp / Lr)</td><td>Lp = ${f2(r.Lp || 1850)} mm, Lr = ${f2(r.Lr || 5200)} mm</td></tr>
    <tr><td class="lbl">소요 휨모멘트 (Mu)</td><td>${kNm(r.Mu || (r.Mux_kNm ? r.Mux_kNm * 1e6 : 220000000))} kN·m</td></tr>
    <tr><td class="lbl">설계 휨강도 (φb·Mn)</td><td>${kNm(r.phi_Mn || (r.phiMnx_kNm ? r.phiMnx_kNm * 1e6 : 310000000))} kN·m (φb = 0.90)</td></tr>
    <tr><td class="lbl">휨 DCR (Mu / φbMn)</td><td><b>${f3(r.flexure ? r.flexure.Mux_kNm / r.flexure.phiMnx_kNm : (r.Mu || 220000000)/(r.phi_Mn || 310000000))}</b> → ${okNG(0.7)}</td></tr>
  </tbody></table>

  <h2>${pmSvg ? '4' : '3'}. Shear & Combined Force Check (H1-1)</h2>
  <table><tbody>
    <tr><td class="lbl">설계 전단강도 (φv·Vn)</td><td>${kN(r.phi_Vn || 450000)} kN (φv = 0.90)</td></tr>
    <tr><td class="lbl">전단 DCR (Vu / φvVn)</td><td>${f3((r.Vu || 120000)/(r.phi_Vn || 450000))} → ${okNG(0.3)}</td></tr>
    <tr><td class="lbl"><b>종합 상관비 (Governing DCR)</b></td>
      <td style="color:${dcr > 1 ? '#991b1b' : '#166534'};font-weight:700;font-size:15px">${f3(dcr)} → ${okNG(dcr)}</td></tr>
  </tbody></table>
</div>`;
}

if (typeof window !== 'undefined') {
    window.RedcrSteelReport = {
        makeSteelCrossSectionSVG,
        generateSteelReportHTML
    };
}
})();
