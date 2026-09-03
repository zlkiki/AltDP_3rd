// web/js/report/redcr/BeamReportGenerator.js
/**
 * AltDP Member Designer - RC Beam Step-by-Step KDS Calculation Sheet Generator
 * KDS 14 20 20 (휨 및 압축) / KDS 14 20 22 (전단 및 비틀림)
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

    // ── 보 단면도 SVG 생성 (260x320 px) ─────────────────────────
    function generateBeamCrossSectionSVG(r) {
        if (!r) return '';
        if (window.VectorRcSec && typeof window.VectorRcSec.renderBeamSectionSVG === 'function') {
            return window.VectorRcSec.renderBeamSectionSVG(r, { mode: 'report', width: 260, height: 300 });
        }
        return '';
    }

    /**
     * RC 보 8단계 KDS 상세 계산서 생성
     * @param {Object} r - 백엔드 결과 및 입력 데이터
     * @param {Boolean} isCheck - 검토 모드 여부
     */
    function generateBeamReportHTML(r, isCheck = true) {
        if (!r) return '<div class="warn-box">부재 계산 결과가 없습니다.</div>';

        const b = Number(r.b || r.width || 400);
        const h = Number(r.h || r.height || 600);
        const cover = Number(r.cover || r.dc || 40);
        const d = Number(r.d || (h - cover - 10 - 25 / 2));
        const fck = Number(r.fck || 24);
        const fy = Number(r.fy || 400);
        const fys = Number(r.fys || r.fyt || fy || 400);
        const Es = Number(r.Es || 200000);

        // 단위 정규화 (kN·m 및 kN 기준)
        const rawMu = r.flexure?.Mu_kNm ?? (r.Mu > 1e4 ? r.Mu * 1e-6 : (r.Mu || 150));
        const Mu = Number(rawMu);
        const rawVu = r.shear?.Vu_kN ?? (r.Vu > 1e2 ? r.Vu * 1e-3 : (r.Vu || 120));
        const Vu = Number(rawVu);

        const rawPhiMn = r.flexure?.phiMn_kNm ?? (r.phi_Mn > 1e4 ? r.phi_Mn * 1e-6 : (r.phi_Mn || r.phiMn || 220));
        const phiMn = Number(rawPhiMn);
        const Mn = phiMn > 0 ? phiMn / 0.85 : 0;

        const rawPhiVn = r.shear?.phiVn_kN ?? (r.phi_Vn > 1e2 ? r.phi_Vn * 1e-3 : (r.phi_Vn || r.phiVn || 160));
        const phiVn = Number(rawPhiVn);
        const Vn = phiVn > 0 ? phiVn / 0.75 : 0;
        const Vc = Number(r.shear?.Vc_kN ?? (r.Vc > 1e2 ? r.Vc * 1e-3 : (0.17 * Math.sqrt(fck) * b * d / 1000)));
        const Vs = Math.max(0, Vn - Vc);

        const dcrFlex = Number(r.flexure?.dcr ?? (phiMn > 0 ? Math.abs(Mu) / phiMn : (r.dcr_flex || 0)));
        const dcrShear = Number(r.shear?.dcr ?? (phiVn > 0 ? Math.abs(Vu) / phiVn : (r.dcr_shear || 0)));
        const governingDcr = Number(r.governing_dcr || r.max_dcr || Math.max(dcrFlex, dcrShear));
        const isOk = (r.status === 'OK' || r.status === 'PASS' || governingDcr <= 1.0);

        const top1Num = Number(r.top_layer1_num ?? r.top_num ?? r.n_top ?? r.top1 ?? r.top_bars_1 ?? r.top_rebar_count ?? 3);
        const top2Num = Number(r.top_layer2_num ?? r.top2 ?? r.top_bars_2 ?? 0);
        const top1Dia = Number(r.top_layer1_dia || r.top_dia || r.topDia || r.main_rebar_dia || 22);
        const top2Dia = Number(r.top_layer2_dia || r.top2Dia || top1Dia);

        const bot1Num = Number(r.bot_layer1_num ?? r.bot_num ?? r.n_bot ?? r.bot1 ?? r.bot_bars_1 ?? r.bot_rebar_count ?? 3);
        const bot2Num = Number(r.bot_layer2_num ?? r.bot2 ?? r.bot_bars_2 ?? 0);
        const bot1Dia = Number(r.bot_layer1_dia || r.bot_dia || r.botDia || r.main_rebar_dia || 25);
        const bot2Dia = Number(r.bot_layer2_dia || r.bot2Dia || bot1Dia);

        const sideDia = Number(r.side_dia || r.sideDia || 13);
        const sideNum = Number(r.side_num || r.sideNum || r.n_side || 0);

        const stirDia = Number(r.stirrup_dia || r.stirDia || 10);
        const stirSpacing = Number(r.stirrup_spacing || r.stirSpacing || 150);
        const stirLegs = Number(r.stirrup_legs || r.stirLegs || 2);

        // 철근 단면적 산출
        const AsTop = Number(r.As_top || (top1Num * Math.PI * (top1Dia / 2) ** 2 + top2Num * Math.PI * (top2Dia / 2) ** 2));
        const AsBot = Number(r.As_bot || (bot1Num * Math.PI * (bot1Dia / 2) ** 2 + bot2Num * Math.PI * (bot2Dia / 2) ** 2));
        const AsSide = sideNum * 2 * Math.PI * (sideDia / 2) ** 2;
        const Av = Number(r.Av || (stirLegs * Math.PI * (stirDia / 2) ** 2));

        const rho = AsBot / (b * d);
        const rhoMin = Math.max(0.25 * Math.sqrt(fck) / fy, 1.4 / fy);
        const beta1 = fck <= 28 ? 0.85 : Math.max(0.65, 0.85 - ((fck - 28) / 7) * 0.05);
        const rhoMax = 0.85 * beta1 * (fck / fy) * (0.003 / (0.003 + 0.004));

        const headerHtml = window.RedcrCommon && window.RedcrCommon.memberHeader
            ? window.RedcrCommon.memberHeader.memberHeaderRcBeam({
                memberName: r.memberName || 'RC-B1',
                sectionLabel: `${b}x${h}`,
                story: r.story || '1F',
                dcrFlex: dcrFlex,
                dcrShear: dcrShear
            })
            : '';

        const bannerHtml = V.okNgBanner(isOk, governingDcr, dcrFlex >= dcrShear ? '휨 지배' : '전단 지배');

        const topRebarText = top2Num > 0 ? `1단: ${top1Num}-D${top1Dia}, 2단: ${top2Num}-D${top2Dia} (As=${f1(AsTop)} mm²)` : `${top1Num}-D${top1Dia} (As=${f1(AsTop)} mm²)`;
        const botRebarText = bot2Num > 0 ? `1단: ${bot1Num}-D${bot1Dia}, 2단: ${bot2Num}-D${bot2Dia} (As=${f1(AsBot)} mm²)` : `${bot1Num}-D${bot1Dia} (As=${f1(AsBot)} mm²)`;
        const sideRebarRow = sideNum > 0 ? `<tr><td class="inp-label">측면 표피철근</td><td class="inp-val">${sideNum * 2}-D${sideDia} (${sideNum}단 양측, As=${f1(AsSide)} mm²)</td><td class="inp-unit"></td></tr>` : '';

        const isTBeam = (r.bw !== undefined || r.hf !== undefined || r.b_eff !== undefined || r.beff !== undefined || String(r.shape || '').includes('T_') || String(r.shape || '').includes('L_'));
        const bw = Number(r.bw || r.b_w || b);
        const hf = Number(r.hf || r.h_f || 0);
        const be = Number(r.effective_flange?.be_effective_mm || r.be || r.b_eff || r.beff || b);

        const dimRows = isTBeam ? `
        <tr><td class="inp-label">웨브 폭 (bw)</td><td class="inp-val">${f0(bw)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">유효 플랜지 폭 (be)</td><td class="inp-val"><b>${f0(be)}</b></td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">플랜지 두께 (hf)</td><td class="inp-val">${f0(hf)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">전체 춤 (h)</td><td class="inp-val">${f0(h)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">유효 깊이 (d)</td><td class="inp-val">${f1(d)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">순피복 두께 (cover)</td><td class="inp-val">${f0(cover)}</td><td class="inp-unit">mm</td></tr>
        ` : `
        <tr><td class="inp-label">단면 폭 (b)</td><td class="inp-val">${f0(b)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">단면 높이 (h)</td><td class="inp-val">${f0(h)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">유효 깊이 (d)</td><td class="inp-val">${f1(d)}</td><td class="inp-unit">mm</td></tr>
        <tr><td class="inp-label">순피복 두께 (cover)</td><td class="inp-val">${f0(cover)}</td><td class="inp-unit">mm</td></tr>
        `;

        return `
<div class="dcr-rpt-beam a4-sheet-content">
  ${headerHtml}
  ${bannerHtml}

  <!-- 1. 부재 형상 및 비주얼 단면도 -->
  ${F.sectionHeader('1', isTBeam ? 'T/L형 부재 형상 및 단면 제원 (T-Beam Geometry &amp; Rebar Layout)' : '부재 형상 및 단면 제원 (Section Geometry &amp; Rebar Layout)', 'KDS 14 20 20')}
  <div style="display:flex;gap:20px;margin-bottom:12px;align-items:flex-start;">
    <div style="flex:0 0 260px;">
      ${generateBeamCrossSectionSVG(r)}
    </div>
    <div style="flex:1;">
      <table class="inp-table" style="width:100%;">
        ${dimRows}
        <tr><td class="inp-label">상단 배근</td><td class="inp-val">${topRebarText}</td><td class="inp-unit"></td></tr>
        <tr><td class="inp-label">하단 배근</td><td class="inp-val">${botRebarText}</td><td class="inp-unit"></td></tr>
        ${sideRebarRow}
        <tr><td class="inp-label">전단 전단철근</td><td class="inp-val">${stirLegs}-D${stirDia} @ ${f0(stirSpacing)} mm</td><td class="inp-unit"></td></tr>
      </table>
    </div>
  </div>

  <!-- 2. 재료 특성 및 설계 기준 계수 -->
  ${F.sectionHeader('2', '사용 재료 및 기준 계수 (Materials &amp; Design Parameters)', 'KDS 14 20 20')}
  <div class="calc-block">
    <table class="chk-table">
      <thead>
        <tr><th>재료 항목</th><th>설계 기준값</th><th>단위</th><th>비고</th></tr>
      </thead>
      <tbody>
        <tr><td>콘크리트 설계기준압축강도 (fck)</td><td class="num">${f1(fck)}</td><td class="ctr">MPa</td><td>KDS 14 20 10</td></tr>
        <tr><td>주철근 항복강도 (fy)</td><td class="num">${f0(fy)}</td><td class="ctr">MPa</td><td>SD400 / SD500</td></tr>
        <tr><td>전단철근 항복강도 (fys)</td><td class="num">${f0(fys)}</td><td class="ctr">MPa</td><td>SD400</td></tr>
        <tr><td>철근 탄성계수 (Es)</td><td class="num">${f0(Es)}</td><td class="ctr">MPa</td><td>200,000 MPa</td></tr>
        <tr><td>등가응력블록 계수 (β1)</td><td class="num">${f3(beta1)}</td><td class="ctr">—</td><td>fck ≤ 28 MPa: 0.85</td></tr>
      </tbody>
    </table>
  </div>

  <!-- 3. 철근비 및 배근 적합성 검토 -->
  ${F.sectionHeader('3', '배근율 및 최소/최대 철근비 검토 (Reinforcement Limits)', 'KDS 14 20 20 §4.1.2')}
  <div class="calc-block">
    <div class="calc-step">
      <div class="calc-formula">최소 철근비: ρ_min = max(0.25√fck / fy, 1.4 / fy) = ${f5(rhoMin)}</div>
      <div class="calc-formula">최대 철근비: ρ_max = 0.85 β1 (fck / fy) (0.003 / 0.007) = ${f5(rhoMax)}</div>
      <div class="calc-sub">현재 인장 철근비: ρ = As / (b·d) = ${f1(AsBot)} / (${f0(b)} × ${f1(d)}) = <b>${f5(rho)}</b></div>
      <div class="calc-result">
        검토 결과: ${rho >= rhoMin && rho <= rhoMax ? '<span class="chk-pass">만족 (ρ_min ≤ ρ ≤ ρ_max) ✓</span>' : '<span class="chk-fail">기준 미달 ✗</span>'}
      </div>
    </div>
  </div>

  <!-- 4. 휨강도 상세 산정 -->
  ${F.sectionHeader('4', '공칭 및 설계 휨강도 산정 (Flexural Capacity)', 'KDS 14 20 20 §4.2')}
  <div class="calc-block">
    <div class="calc-step">
      <div class="calc-formula">등가직사각형 응력블록 깊이 a = (As · fy) / (0.85 · fck · b)</div>
      <div class="calc-sub">a = (${f1(AsBot)} × ${f0(fy)}) / (0.85 × ${f1(fck)} × ${f0(b)}) = <b>${f2((AsBot * fy) / (0.85 * fck * b))} mm</b></div>
      <div class="calc-formula">중립축 깊이 c = a / β1 = ${f2((AsBot * fy) / (0.85 * fck * b) / beta1)} mm</div>
      <div class="calc-formula">공칭 휨강도 Mn = As · fy · (d - a/2) = <b>${f2(Mn)} kN·m</b></div>
      <div class="calc-formula">설계 휨강도 φMn = 0.85 × Mn = <b>${f2(phiMn)} kN·m</b></div>
    </div>
  </div>

  <!-- 5. 전단강도 상세 산정 -->
  ${F.sectionHeader('5', '공칭 및 설계 전단강도 산정 (Shear Capacity)', 'KDS 14 20 22 §4.2')}
  <div class="calc-block">
    <div class="calc-step">
      <div class="calc-formula">콘크리트 부담 전단강도: Vc = 0.17 · √fck · bw · d = <b>${f2(Vc)} kN</b></div>
      <div class="calc-formula">전단철근 부담 전단강도: Vs = (Av · fys · d) / s = <b>${f2(Vs)} kN</b></div>
      <div class="calc-formula">공칭 전단강도: Vn = Vc + Vs = <b>${f2(Vn)} kN</b> &nbsp;&le;&nbsp; 상한값 0.66√fck·bw·d (${f2(0.66 * Math.sqrt(fck) * b * d / 1000)} kN)</div>
      <div class="calc-formula">설계 전단강도: φVn = 0.75 × Vn = <b>${f2(phiVn)} kN</b></div>
    </div>
  </div>

  <!-- 6. 한계상태별 안전성 종합 검토표 (DCR Summary) -->
  ${F.sectionHeader('6', '안전성 검토 결과 종합 (Design Check Ratio Summary)', 'KDS 14 20')}
  <div class="calc-block">
    <table class="chk-table">
      <thead>
        <tr>
          <th>검토 항목 (Limit State)</th>
          <th>소요 강도 (Demand)</th>
          <th>설계 강도 (Capacity)</th>
          <th>DCR (비율)</th>
          <th>판정</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>휨강도 (정/부모멘트)</b></td>
          <td class="num">${f2(Mu)} kN·m</td>
          <td class="num">${f2(phiMn)} kN·m</td>
          <td class="num" style="color:${H.dcrColor(dcrFlex)};font-weight:700;">${f3(dcrFlex)}</td>
          <td class="ctr">${H.okNg(dcrFlex <= 1.0)}</td>
        </tr>
        <tr>
          <td><b>전단강도 (전단력)</b></td>
          <td class="num">${f2(Vu)} kN</td>
          <td class="num">${f2(phiVn)} kN</td>
          <td class="num" style="color:${H.dcrColor(dcrShear)};font-weight:700;">${f3(dcrShear)}</td>
          <td class="ctr">${H.okNg(dcrShear <= 1.0)}</td>
        </tr>
      </tbody>
    </table>
    <div style="margin-top:8px;font-size:10pt;color:#555;text-align:right;">
      최대 지배 DCR: <b style="color:${H.dcrColor(governingDcr)};font-size:11pt;">${f3(governingDcr)}</b> &nbsp;|&nbsp; 
      최종 결과: <b>${isOk ? '<span class="chk-pass">PASS (만족)</span>' : '<span class="chk-fail">FAIL (초과)</span>'}</b>
    </div>
  </div>
</div>`;
    }

    /** N부재 묶음 번들 A4 문서 생성 */
    function generateBeamReportHTMLMulti(members, projectName = '') {
        const wrap = (window.RedcrDetailWrapper && window.RedcrDetailWrapper.wrapDetailDocument) ||
            ((t, s, sets) => sets.map(x => x.bodyHtml).join('\n'));
        const sets = (members || []).map((m, i) => ({
            title: m.name || `RC Beam ${i + 1}`,
            bodyHtml: generateBeamReportHTML(m)
        }));
        return wrap('RC Beam Structural Design Sheet', 'KDS 14 20 RC 보 상세 구조계산서', sets, projectName);
    }

    const RedcrBeamReport = {
        generateBeamCrossSectionSVG,
        generateBeamReportHTML,
        generateBeamReportHTMLMulti
    };

    if (typeof window !== 'undefined') {
        window.RedcrBeamReport = RedcrBeamReport;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = RedcrBeamReport;
    }
})();
