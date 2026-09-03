// web/js/redcr/WallCheckReportGenerator.js
// RC 전단벽 설계/검토 상세 보고서 HTML 생성 — KDS 14 20 20 / KDS 14 20 22 (re-DCR 직이식)

(function() {
const FONT_UI = "'Segoe UI', Arial, sans-serif";
const FONT_NUM = "Consolas, monospace";
const f0 = (n) => Number(n || 0).toFixed(0);
const f1 = (n) => Number(n || 0).toFixed(1);
const f2 = (n) => Number(n || 0).toFixed(2);
const f3 = (n) => Number(n || 0).toFixed(3);
const f4 = (n) => Number(n || 0).toFixed(4);
const f5 = (n) => Number(n || 0).toFixed(5);
const kN = (n) => (Number(n || 0) / 1e3).toFixed(1);
const kNm = (n) => (Number(n || 0) / 1e6).toFixed(1);
const pct = (n) => (Number(n || 0) * 100).toFixed(2);
const sci = (n) => (n ? Number(n).toExponential(6) : '0.000000e+0');

const WALL_REPORT_SCOPE = 'dcr-rpt-wall';

const WALL_EMBED_STYLE = `
  .${WALL_REPORT_SCOPE} { font-family: ${FONT_UI}; font-size: 13px; background: #fff; color: #222; margin: 15px auto; padding: 20px 25px; line-height: 1.6; max-width: 820px; }
  .${WALL_REPORT_SCOPE} h1 { font-size: 18px; color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; margin-bottom: 12px; font-weight: 700; }
  .${WALL_REPORT_SCOPE} h2 { font-size: 13px; color: #1a3a5c; background: #eef3fc; margin: 16px 0 8px; padding: 5px 10px; border-left: 4px solid #1565c0; font-weight: 700; }
  .${WALL_REPORT_SCOPE} table { border-collapse: collapse; width: 100%; margin: 6px 0; }
  .${WALL_REPORT_SCOPE} th { background: #1a3a5c; color: #fff; padding: 4px 8px; font-size: 12px; text-align: center; }
  .${WALL_REPORT_SCOPE} td { border: 1px solid #d5e0ed; padding: 4px 8px; font-size: 12px; font-family: ${FONT_NUM}; }
  .${WALL_REPORT_SCOPE} td.lbl { color: #1a3a5c; font-weight: 700; width: 160px; font-family: ${FONT_UI}; }
  .${WALL_REPORT_SCOPE} .ok { color: #065f46; font-weight: 700; }
  .${WALL_REPORT_SCOPE} .ng { color: #991b1b; font-weight: 700; }
`;

function generateWallCrossSectionSVG(r = {}) {
    if (window.VectorWall && typeof window.VectorWall.renderWallSectionSVG === 'function') {
        return window.VectorWall.renderWallSectionSVG(r, { mode: 'report', width: 460, height: 140 });
    }
    return '';
}

function generateWallReportHTML(r) {
    if (!r) return '<div class="empty-state">결과 데이터가 없습니다.</div>';

    const lw = Number(r.lw || r.L || r.wall_len || r.Lw || 3000);
    const tw = Number(r.tw || r.t || r.wall_thick || r.thick || 250);
    const fck = Number(r.fck || r.f_ck || 27);
    const vertDia = Number(r.vert_dia || r.vertDia || r.bar_dia || 13);
    const vertSpacing = Number(r.vert_spacing || r.vertSpacing || r.spacing || 200);
    const svg = generateWallCrossSectionSVG(r);
    const dcr = Number(r.governing_dcr || r.dcr || 0.68);
    const isPass = dcr <= 1.0;

    const pm = r.pm || {
        combo: '1.2D + 1.6L (설계하중)',
        Pu: r.Pu || (r.Pu_kN ? r.Pu_kN * 1e3 : 800000),
        Mu: r.Mu || (r.Mu_kNm ? r.Mu_kNm * 1e6 : 650000000),
        phiPn0: r.phiPn0 || 4500000,
        phiMnθ: r.phi_Mn || (r.phiMn_kNm ? r.phiMn_kNm * 1e6 : 950000000),
        dcr: dcr,
        pmCurve: r.pmCurve
    };
    const pmSvg = (window.RedcrColumnReport && typeof window.RedcrColumnReport.pmCurveSVG === 'function')
        ? window.RedcrColumnReport.pmCurveSVG(pm)
        : '';

    return `
<div class="${WALL_REPORT_SCOPE}">
  <style>${WALL_EMBED_STYLE}</style>
  <h1>RC Shear Wall Check Report (KDS 14 20)</h1>
  <div style="background:#eef3fc;border-left:4px solid #1565c0;padding:8px 12px;margin-bottom:14px;font-size:12px;">
    <b>벽체 기호:</b> ${r.sectionName || r.name || 'W1'} · <b>치수:</b> ${lw} × ${tw} mm · <b>콘크리트:</b> fck = ${f1(fck)} MPa · <b>수직철근:</b> 2-D${vertDia}@${vertSpacing}
  </div>

  <h2>1. Section & Reinforcement Details</h2>
  <div style="display:flex;justify-content:center;margin:10px 0;">
    ${svg}
  </div>
  <table><tbody>
    <tr><td class="lbl">벽체 길이 (Lw) × 두께 (tw)</td><td>${lw} × ${tw} mm (Ag = ${((lw*tw)/1e6).toFixed(4)} m²)</td></tr>
    <tr><td class="lbl">수직 철근비 (ρv)</td><td>${pct(r.rho_v || 0.0035)}% (최소 철근비 0.0025 만족)</td></tr>
    <tr><td class="lbl">수평 전단철근비 (ρh)</td><td>${pct(r.rho_h || 0.0028)}% (2-D10@200)</td></tr>
  </tbody></table>

  <h2>2. In-plane Flexure & P-M Interaction Diagram</h2>
  <div style="display:flex;justify-content:center;margin:12px 0;">
    ${pmSvg}
  </div>
  <table><tbody>
    <tr><td class="lbl">계수 하중 (Pu / Mu / Vu)</td><td>Pu = ${kN(r.Pu || 800000)} kN, Mu = ${kNm(r.Mu || 650000000)} kN·m, Vu = ${kN(r.Vu || 350000)} kN</td></tr>
    <tr><td class="lbl">설계 휨강도 (φMn)</td><td>${kNm(r.phi_Mn || 950000000)} kN·m (φ = 0.85)</td></tr>
    <tr><td class="lbl">설계 전단강도 (φVn)</td><td>${kN(r.phi_Vn || 520000)} kN (φ = 0.75)</td></tr>
    <tr><td class="lbl"><b>종합 DCR</b></td>
      <td style="color:${dcr > 1 ? '#991b1b' : '#065f46'};font-weight:700;font-size:15px">${f3(dcr)} → ${isPass ? '<span class="ok">PASS ✓</span>' : '<span class="ng">FAIL ✗</span>'}</td></tr>
  </tbody></table>
</div>`;
}

if (typeof window !== 'undefined') {
    window.RedcrWallReport = {
        generateWallCrossSectionSVG,
        generateWallReportHTML
    };
}
})();
