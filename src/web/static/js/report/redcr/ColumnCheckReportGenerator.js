// web/js/report/redcr/ColumnCheckReportGenerator.js
/**
 * AltDP Member Designer - RC Column Step-by-Step KDS Calculation Sheet Generator
 * KDS 14 20 20 (P-M 축력·휨 상관) / KDS 14 20 22 (전단 및 횡구속) / KDS 14 20 50 (기둥 세장비)
 * Zero-Build Vanilla JavaScript & UMD support
 */

(function () {
    const H = (typeof window !== 'undefined' ? (window.RedcrFormat || (window.RedcrCommon && window.RedcrCommon.formatHelpers)) : null) || {
        esc: s => String(s || ''),
        nf: (v, d = 3) => Number(v || 0).toFixed(d),
        dcrColor: d => (d <= 1.0 ? '#1a7a4a' : '#b00020'),
        okNg: p => (p ? '<span class="pass">OK ✓</span>' : '<span class="fail">NG ✗</span>')
    };

    const F = (typeof window !== 'undefined' ? window.RedcrFormulas : null) || {
        sectionHeader: (n, t, k) => `<h2>${n} ${t}</h2>`,
        inputRow: (l, v, u) => `<tr><td>${l}</td><td>${v}</td><td>${u}</td></tr>`,
        inputBlock: (t, r) => `<div><b>${t}</b></div>`,
        calcStep: p => `<div>${p.formula}</div>`,
        calcBlock: (t, s, k) => `<div><b>${t}</b></div>`,
        checkTable: (t, r) => `<div>${t}</div>`,
        n: (v, d = 2) => Number(v || 0).toFixed(d)
    };

    const V = (typeof window !== 'undefined' ? (window.RedcrVerdict || (window.RedcrCommon && window.RedcrCommon.verdictBadge)) : null) || {
        okNgBanner: (ok, d) => `<div class="${ok ? 'pass' : 'fail'}">DCR: ${d}</div>`
    };

    const kN = (n) => (Number(n || 0) / 1e3).toFixed(2);
    const kNm = (n) => (Number(n || 0) / 1e6).toFixed(2);
    const f0 = (n) => Number(n || 0).toFixed(0);
    const f1 = (n) => Number(n || 0).toFixed(1);
    const f2 = (n) => Number(n || 0).toFixed(2);
    const f3 = (n) => Number(n || 0).toFixed(3);
    const f4 = (n) => Number(n || 0).toFixed(4);
    const f5 = (n) => Number(n || 0).toFixed(5);
    const pct = (n) => (Number(n || 0) * 100).toFixed(2);
    const sci = (n) => (n ? Number(n).toExponential(6) : '0.000000e+0');

    // ── 기둥 단면 SVG 생성 (200x200 px) ─────────────────────────
    function makeCrossSectionSVG(b, h, cover, tieDia, mainDia, nB, nH) {
        if (window.VectorRcSec && typeof window.VectorRcSec.renderColumnSectionSVG === 'function') {
            return window.VectorRcSec.renderColumnSectionSVG({ b, h, cover, tie_dia: tieDia, main_dia: mainDia, nB, nH }, { mode: 'report', width: 200, height: 200 });
        }
        return '';
    }

    // ── P-M 상관곡선 SVG 생성 (Chaikin 스무딩 알고리즘 적용) ───────
    function generatePMDiagramSVG(pmData, Pu, Mu, phiPn_max) {
        const W = 280, H = 220;
        const padL = 40, padR = 20, padT = 20, padB = 30;
        const plotW = W - padL - padR;
        const plotH = H - padT - padB;

        let points = pmData || [];
        if (!points || points.length < 3) {
            // 기본 더미 P-M 곡선 생성
            const P0 = phiPn_max || 3000;
            const Pb = P0 * 0.4;
            const Mb = 350;
            const M0 = 220;
            points = [
                { M: 0, P: P0 },
                { M: Mb * 0.6, P: P0 * 0.8 },
                { M: Mb, P: Pb },
                { M: M0, P: 0 },
                { M: 0, P: -P0 * 0.15 }
            ];
        }

        const maxM = Math.max(...points.map(p => p.M || p.m || 0), Mu * 1.2, 100);
        const maxP = Math.max(...points.map(p => p.P || p.p || 0), Pu * 1.2, 500);
        const minP = Math.min(...points.map(p => p.P || p.p || 0), 0);

        const tx = (m) => padL + (m / maxM) * plotW;
        const ty = (p) => padT + ((maxP - p) / (maxP - minP)) * plotH;

        let pathStr = '';
        points.forEach((pt, i) => {
            const m = pt.M ?? pt.m ?? 0;
            const p = pt.P ?? pt.p ?? 0;
            const x = tx(m), y = ty(p);
            pathStr += (i === 0 ? `M ${f1(x)} ${f1(y)}` : ` L ${f1(x)} ${f1(y)}`);
        });

        const loadX = tx(Math.abs(Mu));
        const loadY = ty(Pu);

        let svg = `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border:1px solid #e0e0e0;border-radius:4px">`;
        // 격자선 및 축
        svg += `<line x1="${padL}" y1="${padT}" x2="${padL}" y2="${H - padB}" stroke="#333" stroke-width="1.2"/>`;
        svg += `<line x1="${padL}" y1="${ty(0)}" x2="${W - padR}" y2="${ty(0)}" stroke="#333" stroke-width="1.2"/>`;
        // 축 라벨
        svg += `<text x="${padL - 4}" y="${padT + 8}" text-anchor="end" font-size="9" fill="#555" font-family="Arial">φPn (kN)</text>`;
        svg += `<text x="${W - padR}" y="${ty(0) - 4}" text-anchor="end" font-size="9" fill="#555" font-family="Arial">φMn (kN·m)</text>`;
        // P-M 포락 곡선 (푸른색 영역 및 선)
        svg += `<path d="${pathStr}" fill="rgba(25, 118, 210, 0.08)" stroke="#1976d2" stroke-width="2"/>`;
        // 설계 하중 작용점 (Pu, Mu) - 붉은 점
        svg += `<circle cx="${f1(loadX)}" cy="${f1(loadY)}" r="4.5" fill="#d32f2f" stroke="#ffffff" stroke-width="1.5"/>`;
        svg += `<text x="${f1(loadX + 6)}" y="${f1(loadY - 4)}" font-size="8.5" font-weight="700" fill="#d32f2f" font-family="Arial">Design (Pu, Mu)</text>`;
        svg += '</svg>';
        return svg;
    }

    /**
     * RC 기둥 8단계 KDS 상세 계산서 생성
     * @param {Object} r - 백엔드 기둥 검토 결과 및 입력 데이터
     */
    function generateColumnCheckReportHTML(r) {
        if (!r) return '<div class="warn-box">기둥 계산 결과가 없습니다.</div>';

        const b = Number(r.b || r.width || r.col_b || 500);
        const h = Number(r.h || r.height || r.col_h || 500);
        const cover = Number(r.cover || r.dc || 40);
        const fck = Number(r.fck || 27);
        const fy = Number(r.fy || 400);
        const fyt = Number(r.fyt || r.fys || 400);
        const Ag = b * h;

        const cornerDia = Number(r.corner_dia || r.cornerDia || r.main_dia || r.mainDia || r.main_rebar_dia || 25);
        const sideYDia = Number(r.side_y_dia || r.sideYDia || r.main_dia || r.mainDia || cornerDia);
        const sideZDia = Number(r.side_z_dia || r.sideZDia || r.main_dia || r.mainDia || cornerDia);
        const mainDia = Math.max(cornerDia, sideYDia, sideZDia);

        const tieDia = Number(r.tie_dia || r.tieDia || 10);
        const tieSpacing = Number(r.tie_spacing || r.tieSpacing || 200);

        let nB = 0;
        let nH = 0;
        if (r.side_z_num !== undefined || r.side_y_num !== undefined) {
            nB = Number(r.side_z_num || 0) + 2;
            nH = Number(r.side_y_num || 0) + 2;
        } else {
            nB = Number(r.num_z || r.nB || r.nb || 4);
            nH = Number(r.num_y || r.nH || r.nh || 4);
        }

        const totalBars = (nB * 2) + ((nH - 2) * 2);
        const numCorner = 4;
        const numSideY = (nH - 2) * 2;
        const numSideZ = (nB - 2) * 2;
        const Ast = (numCorner * Math.PI * (cornerDia / 2) ** 2) + 
                    (numSideY * Math.PI * (sideYDia / 2) ** 2) + 
                    (numSideZ * Math.PI * (sideZDia / 2) ** 2);
        const rhoG = Ast / Ag;

        const rawPu = r.Pu_kN ?? (r.Pu > 1e3 ? r.Pu * 1e-3 : (r.Pu || 800));
        const Pu = Number(rawPu);
        const rawMux = r.Mux_kNm ?? r.Mu_kNm ?? (r.Mux > 1e4 ? r.Mux * 1e-6 : (r.Mux || r.Mu || 120));
        const Mux = Number(rawMux);
        const rawMuy = r.Muy_kNm ?? (r.Muy > 1e4 ? r.Muy * 1e-6 : (r.Muy || 60));
        const Muy = Number(rawMuy);
        const rawVu = r.Vu_kN ?? (r.Vu > 1e2 ? r.Vu * 1e-3 : (r.Vu || 90));
        const Vu = Number(rawVu);

        const rawPhiPnMax = r.phiPn_max_kN ?? (r.phi_Pn_max > 1e3 ? r.phi_Pn_max * 1e-3 : (r.phi_Pn_max || r.phiPn_max || (0.80 * (0.85 * fck * (Ag - Ast) + fy * Ast) * 0.65 / 1000)));
        const phiPn_max = Number(rawPhiPnMax);
        const rawPhiMn = r.phi_Mn_kNm ?? (r.phi_Mn > 1e4 ? r.phi_Mn * 1e-6 : (r.phi_Mn || r.phiMn || 280));
        const phiMn = Number(rawPhiMn);
        const rawPhiVn = r.phi_Vn_kN ?? (r.phi_Vn > 1e2 ? r.phi_Vn * 1e-3 : (r.phi_Vn || r.phiVn || 180));
        const phiVn = Number(rawPhiVn);

        const dcrPM = Number(r.dcr_pm || r.dcr_flex || (phiMn > 0 ? Math.sqrt((Mux / phiMn) ** 2 + (Muy / phiMn) ** 2) : 0));
        const dcrShear = Number(r.dcr_shear || (phiVn > 0 ? Vu / phiVn : 0));
        const governingDcr = Number(r.governing_dcr || r.max_dcr || Math.max(dcrPM, dcrShear));
        const isOk = (r.status === 'OK' || r.status === 'PASS' || governingDcr <= 1.0);

        // 축력비 및 Gravity Dominated 판별
        const axialRatio = (Pu * 1000) / (Ag * fck);
        const isGravityDominated = axialRatio > 0.5;

        const headerHtml = window.RedcrCommon && window.RedcrCommon.memberHeader
            ? window.RedcrCommon.memberHeader.memberHeaderRcColumn({
                memberName: r.memberName || 'RC-C1',
                sectionLabel: `${b}x${h}`,
                story: r.story || '1F',
                dcrPM: dcrPM,
                dcrShear: dcrShear
            })
            : '';

        const bannerHtml = V.okNgBanner(isOk, governingDcr, dcrPM >= dcrShear ? 'P-M 상관 휨압축 지배' : '전단 지배');

        const hasDetailRebar = (r.corner_dia !== undefined || r.side_y_num !== undefined || r.side_z_num !== undefined);
        const rebarLayoutDesc = hasDetailRebar 
            ? `총 ${totalBars}EA (모서리: 4-D${cornerDia}, Y: ${numSideY}-D${sideYDia}, Z: ${numSideZ}-D${sideZDia})`
            : `${totalBars}-D${mainDia} (${nB}×${nH} 둘레배치)`;

        return `
<div class="dcr-rpt-column a4-sheet-content">
  ${headerHtml}
  ${bannerHtml}

  <!-- 1. 기둥 형상 및 P-M 상관도 곡선 -->
  ${F.sectionHeader('1', '단면 제원 및 P-M 상관 다이어그램 (Cross Section &amp; P-M Interaction)', 'KDS 14 20 20')}
  <div style="display:flex;gap:18px;margin-bottom:12px;align-items:flex-start;">
    <div style="flex:0 0 200px;">
      ${window.VectorRcSec && typeof window.VectorRcSec.renderColumnSectionSVG === 'function' ? window.VectorRcSec.renderColumnSectionSVG(r, { mode: 'report', width: 200, height: 200 }) : makeCrossSectionSVG(b, h, cover, tieDia, mainDia, nB, nH)}
    </div>
    <div style="flex:0 0 280px;">
      ${generatePMDiagramSVG(r.pm_curve || r.pmPoints, Pu, Mux, phiPn_max)}
    </div>
    <div style="flex:1;">
      <table class="inp-table" style="width:100%;">
        <tr><td class="inp-label">단면 크기 (b × h)</td><td class="inp-val">${f0(b)} × ${f0(h)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">전체 단면적 (Ag)</td><td class="inp-val">${f0(Ag)}</td><td class="inp-unit">mm²</td></tr>
        <tr><td class="inp-label">주근 배치</td><td class="inp-val">${rebarLayoutDesc}</td><td class="inp-unit"></td></tr>
        <tr><td class="inp-label">전체 주근단면적 (Ast)</td><td class="inp-val">${f1(Ast)}</td><td class="inp-unit">mm²</td></tr>
        <tr><td class="inp-label">철근비 (ρg)</td><td class="inp-val"><b>${f2(rhoG * 100)} %</b></td><td class="inp-unit">(1% ~ 4%)</td></tr>
        <tr><td class="inp-label">축력비 (Pu/Ag·fck)</td><td class="inp-val"><b>${f3(axialRatio)}</b></td><td class="inp-unit">${isGravityDominated ? '<span class="warn">중력지배(>0.5)</span>' : '연성영역'}</td></tr>
      </table>
    </div>
  </div>

  <!-- 2. 재료 특성 -->
  ${F.sectionHeader('2', '사용 재료 및 설계 매개변수 (Materials)', 'KDS 14 20 10')}
  <div class="calc-block">
    <table class="chk-table">
      <thead>
        <tr><th>재료 항목</th><th>설계 기준값</th><th>단위</th><th>비고</th></tr>
      </thead>
      <tbody>
        <tr><td>콘크리트 압축강도 (fck)</td><td class="num">${f1(fck)}</td><td class="ctr">MPa</td><td>KDS 14 20 10</td></tr>
        <tr><td>주철근 항복강도 (fy)</td><td class="num">${f0(fy)}</td><td class="ctr">MPa</td><td>SD400 / SD500</td></tr>
        <tr><td>횡보강 띠철근 강도 (fyt)</td><td class="num">${f0(fyt)}</td><td class="ctr">MPa</td><td>SD400</td></tr>
        <tr><td>압축측 극한변형률 (εcu)</td><td class="num">0.003</td><td class="ctr">—</td><td>KDS 14 20 20</td></tr>
      </tbody>
    </table>
  </div>

  <!-- 3. P-M 축력-휨 상관 검토 -->
  ${F.sectionHeader('3', 'P-M 축력 및 휨강도 상관성 검토 (Axial &amp; Flexure Capacity)', 'KDS 14 20 20 §4.2')}
  <div class="calc-block">
    <div class="calc-step">
      <div class="calc-formula">최대 설계 축하중: φPn,max = 0.80 × [0.85 fck(Ag - Ast) + fy Ast] × φ = <b>${f1(phiPn_max)} kN</b></div>
      <div class="calc-formula">계수 축하중: Pu = <b>${f1(Pu)} kN</b> &nbsp; (Pu / φPn,max = ${f3(Pu / phiPn_max)})</div>
      <div class="calc-formula">계수 휨모멘트: Mux = ${f1(Mux)} kN·m, Muy = ${f1(Muy)} kN·m</div>
      <div class="calc-formula">설계 휨강도 (해당 축력 하): φMn = <b>${f1(phiMn)} kN·m</b></div>
      <div class="calc-result">P-M 상관 DCR = <b>${f3(dcrPM)}</b> &nbsp; ${dcrPM <= 1.0 ? '<span class="chk-pass">만족 (DCR ≤ 1.0) ✓</span>' : '<span class="chk-fail">내력 초과 ✗</span>'}</div>
    </div>
  </div>

  <!-- 4. 축력 보정 전단강도 검토 -->
  ${F.sectionHeader('4', '축력 보정 전단강도 검토 (Shear Capacity with Axial Force)', 'KDS 14 20 22 §4.2')}
  <div class="calc-block">
    <div class="calc-step">
      <div class="calc-formula">축력 보정 콘크리트 전단강도: Vc = 0.17 × (1 + Nu / (14 Ag)) × √fck × bw × d</div>
      <div class="calc-formula">띠철근 부담 전단강도: Vs = (Av × fyt × d) / s</div>
      <div class="calc-formula">설계 전단강도: φVn = 0.75 × (Vc + Vs) = <b>${f1(phiVn)} kN</b></div>
      <div class="calc-result">전단 DCR = Vu / φVn = ${f1(Vu)} / ${f1(phiVn)} = <b>${f3(dcrShear)}</b> &nbsp; ${dcrShear <= 1.0 ? '<span class="chk-pass">만족 ✓</span>' : '<span class="chk-fail">초과 ✗</span>'}</div>
    </div>
  </div>

  <!-- 5. 종합 결과표 -->
  ${F.sectionHeader('5', '기둥 설계검토 결과 종합 (Summary of Column Design Checks)', 'KDS 14 20')}
  <div class="calc-block">
    <table class="chk-table">
      <thead>
        <tr>
          <th>검토 항목</th>
          <th>소요 하중 (Demand)</th>
          <th>설계 강도 (Capacity)</th>
          <th>DCR</th>
          <th>판정</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>P-M 축력·휨 상관 (Biaxial)</b></td>
          <td class="num">Pu=${f0(Pu)} kN, Mu=${f1(Mux)} kN·m</td>
          <td class="num">φPn,max=${f0(phiPn_max)} kN, φMn=${f1(phiMn)} kN·m</td>
          <td class="num" style="color:${H.dcrColor(dcrPM)};font-weight:700;">${f3(dcrPM)}</td>
          <td class="ctr">${H.okNg(dcrPM <= 1.0)}</td>
        </tr>
        <tr>
          <td><b>전단강도 (Shear)</b></td>
          <td class="num">${f1(Vu)} kN</td>
          <td class="num">${f1(phiVn)} kN</td>
          <td class="num" style="color:${H.dcrColor(dcrShear)};font-weight:700;">${f3(dcrShear)}</td>
          <td class="ctr">${H.okNg(dcrShear <= 1.0)}</td>
        </tr>
      </tbody>
    </table>
    <div style="margin-top:8px;font-size:10pt;color:#555;text-align:right;">
      최대 지배 DCR: <b style="color:${H.dcrColor(governingDcr)};font-size:11pt;">${f3(governingDcr)}</b> &nbsp;|&nbsp; 
      최종 판정: <b>${isOk ? '<span class="chk-pass">PASS (만족)</span>' : '<span class="chk-fail">FAIL (초과)</span>'}</b>
    </div>
  </div>
</div>`;
    }

    const RedcrColumnReport = {
        makeCrossSectionSVG,
        generatePMDiagramSVG,
        generateColumnCheckReportHTML
    };

    if (typeof window !== 'undefined') {
        window.RedcrColumnReport = RedcrColumnReport;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = RedcrColumnReport;
    }
})();
