// web/js/report/redcr/FootingReportGenerator.js
// RC 독립기초 / 복합기초 / 말뚝기초 상세 계산서 생성기 — MIDAS Gen / KDS 스타일 (re-DCR 직이식)

(function() {
const kN = (n) => (Number(n || 0) / 1e3).toFixed(1);
const kNm = (n) => (Number(n || 0) / 1e6).toFixed(2);
const f0 = (n) => Number(n || 0).toFixed(0);
const f1 = (n) => Number(n || 0).toFixed(1);
const f2 = (n) => Number(n || 0).toFixed(2);
const f3 = (n) => Number(n || 0).toFixed(3);
const f4 = (n) => Number(n || 0).toFixed(4);
const f5 = (n) => Number(n || 0).toFixed(5);
const pct = (n) => (Number(n || 0) * 100).toFixed(2);
const sci = (n) => (n ? Number(n).toExponential(6) : '0.000000e+0');

function okNg(dcr) {
    return dcr <= 1.0
        ? '<span class="ok" style="font-size:12px;font-weight:700;color:#10b981;">OK</span>'
        : '<span class="ng" style="font-size:12px;font-weight:700;color:#ef4444;">NG</span>';
}

function okStr(ok) {
    return ok ? '<span class="ok" style="font-size:12px;font-weight:700;color:#10b981;">O.K</span>' : '<span class="ng" style="font-size:12px;font-weight:700;color:#ef4444;">N.G</span>';
}

// ── 기초 평면 및 단면 배근도 SVG 생성 ─────────────────────────────────────
function generateFootingSVG(r) {
    if (!r) return '';
    if (window.VectorFooting && typeof window.VectorFooting.renderFootingSectionSVG === 'function') {
        return window.VectorFooting.renderFootingSectionSVG(r, { mode: 'report', width: 320, height: 220 });
    }
    return '';
}

// ── 지반 접지압 분포 다이어그램 SVG 생성 ─────────────────────────────
function generateSoilPressureSVG(qmax = 180, qmin = 60, qa = 200) {
    if (window.VectorFooting && typeof window.VectorFooting.renderSoilPressureSVG === 'function') {
        return window.VectorFooting.renderSoilPressureSVG(qmax, qmin, qa, { mode: 'report', width: 360, height: 140 });
    }
    return '';
}

window.RedcrFootingReport = {
    generateFootingSVG,
    generateSoilPressureSVG,
    generateFootingReportHTML(r) {
        if (!r) return '<div class="empty-state">결과 데이터가 없습니다.</div>';

        const dcr = Number(r.governing_dcr || r.max_dcr || r.dcr || 0);
        const sb = r.soil_bearing || {};
        const fl = r.flexure || {};
        const ow = r.one_way_shear || {};
        const ps = r.punching_shear || {};

        const qmax = Number(sb.q_max || sb.qmax || r.qmax || 0);
        const qmin = Number(sb.q_min || sb.qmin || r.qmin || 0);
        const qa = Number(sb.qa || r.qa || 200);
        const dcr_sb = Number(sb.dcr || (qa > 0 ? qmax / qa : 0));

        const Mu_x = Number(fl.Mu_x || fl.Mux || r.Mu_x || r.Mu || 0);
        const phiMn_x = Number(fl.phiMn_x || fl.phiMn || r.phiMn || 1);
        const dcr_fl = Number(fl.dcr || (phiMn_x > 0 ? Mu_x / phiMn_x : 0));

        const Vu_1w = Number(ow.Vu || ow.Vu_kN || r.Vu_1w || 0);
        const phiVc_1w = Number(ow.phiVc || ow.phiVc_kN || r.phiVc_1w || 1);
        const dcr_ow = Number(ow.dcr || (phiVc_1w > 0 ? Vu_1w / phiVc_1w : 0));

        const Vu_2w = Number(ps.Vu || ps.Vu_kN || r.Vu_2w || 0);
        const phiVc_2w = Number(ps.phiVc || ps.phiVc_kN || r.phiVc_2w || 1);
        const dcr_ps = Number(ps.dcr || (phiVc_2w > 0 ? Vu_2w / phiVc_2w : 0));

        const soilSvg = generateSoilPressureSVG(qmax, qmin, qa);

        return `
<div class="dcr-report a4-sheet-container pure-white-sheet" style="font-family:'Segoe UI',Arial,sans-serif;font-size:12px;color:#1f2937;background:#fff;padding:24px;line-height:1.5;">
  <!-- 헤더 -->
  <div style="border-bottom:2px solid #1e3a8a;padding-bottom:8px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <h1 style="font-size:18px;font-weight:700;color:#1e3a8a;margin:0;">RC 독립/복합 기초 구조계산서 (Spread Footing Design Report)</h1>
      <span style="font-size:11px;color:#6b7280;">KDS 14 20 70 : 2022 / KDS 14 20 22 콘크리트구조설계기준</span>
    </div>
    <div style="text-align:right;">
      <span class="badge ${dcr <= 1.0 ? 'ok' : 'ng'}" style="display:inline-block;padding:4px 12px;border-radius:4px;font-weight:700;background:${dcr <= 1.0 ? '#d1fae5;color:#065f46' : '#fee2e2;color:#991b1b'};">
        ${dcr <= 1.0 ? '● PASS (만족)' : '▲ FAIL (초과)'} (Max DCR: ${f3(dcr)})
      </span>
    </div>
  </div>

  <!-- 요약 & SVG 배치 (2단) -->
  <div style="display:grid;grid-template-columns:1fr 340px;gap:16px;margin-bottom:20px;align-items:start;">
    <div>
      <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:0 0 8px 0;">1. 설계 입력 및 단면 형상 제원</h2>
      <table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:12px;">
        <tbody>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">기초 크기 (Lx × Ly)</td>
            <td style="padding:4px;">${f0(r.Bx || r.B || r.Lx || 2000)} × ${f0(r.By || r.L || r.Ly || 2000)} mm</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">기초 두께 (H / d)</td>
            <td style="padding:4px;">${f0(r.H || r.h || r.D || 600)} / ${f0(r.d || 520)} mm</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">기둥 제원 (cx × cy)</td>
            <td style="padding:4px;">${f0(r.cx || r.col_w || 500)} × ${f0(r.cy || r.col_h || 500)} mm</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">허용 지내력 (qa)</td>
            <td style="padding:4px;">${f1(qa)} kN/m²</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">콘크리트 강도 (fck)</td>
            <td style="padding:4px;">${f1(r.fck || 24)} MPa</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">철근 항복강도 (fy)</td>
            <td style="padding:4px;">${f1(r.fy || 400)} MPa</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">작용 하중 (Pu / Pserv)</td>
            <td style="padding:4px;">${f1(r.Pu || 800)} / ${f1(r.P_serv || r.Pserv || 600)} kN</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">모멘트 (Mux / Muy)</td>
            <td style="padding:4px;">${f1(r.Mux || r.Mu || 50)} / ${f1(r.Muy || 0)} kN·m</td>
          </tr>
        </tbody>
      </table>

      <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:0 0 8px 0;">2. 한계상태 종합 검토 요약표</h2>
      <table style="width:100%;border-collapse:collapse;font-size:11px;">
        <thead>
          <tr style="background:#f3f4f6;border-bottom:1.5px solid #9ca3af;text-align:center;">
            <th style="padding:5px;border:1px solid #e5e7eb;">검토 항목</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">소요력 (Demand)</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">설계내력 (Capacity)</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">DCR</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">판정</th>
          </tr>
        </thead>
        <tbody style="text-align:center;">
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">1. 지반 접지압 (Soil Bearing)</td>
            <td style="padding:5px;">qmax = ${f1(qmax)} kN/m²</td>
            <td style="padding:5px;">qa = ${f1(qa)} kN/m²</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_sb)}</td>
            <td style="padding:5px;">${okNg(dcr_sb)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">2. 기초판 휨모멘트 (Flexure X)</td>
            <td style="padding:5px;">Mu = ${f1(Mu_x)} kN·m</td>
            <td style="padding:5px;">φMn = ${f1(phiMn_x)} kN·m</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_fl)}</td>
            <td style="padding:5px;">${okNg(dcr_fl)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">3. 1방향 보전단 (One-way Shear)</td>
            <td style="padding:5px;">Vu = ${f1(Vu_1w)} kN</td>
            <td style="padding:5px;">φVc = ${f1(phiVc_1w)} kN</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_ow)}</td>
            <td style="padding:5px;">${okNg(dcr_ow)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">4. 2방향 펀칭전단 (Punching)</td>
            <td style="padding:5px;">Vu = ${f1(Vu_2w)} kN</td>
            <td style="padding:5px;">φVc = ${f1(phiVc_2w)} kN</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_ps)}</td>
            <td style="padding:5px;">${okNg(dcr_ps)}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 우측 배근도 SVG -->
    <div style="text-align:center;">
      <h3 style="font-size:12px;color:#1e3a8a;margin:0 0 6px 0;font-weight:600;">기초 배근도 및 위험단면</h3>
      ${generateFootingSVG(r)}
    </div>
  </div>

  <!-- 상세 수식 단계 (Step-by-Step) -->
  <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:16px 0 8px 0;">3. Step-by-Step 상세 계산 근거</h2>
  
  <!-- Step 1: 지내력 & 접지압 분포도 -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(1) 지반 접지압 및 편심 검토 (Soil Bearing Pressure & Distribution)</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 70 §4.2.1</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 340px;gap:12px;align-items:center;">
      <div style="font-size:11px;">
        <div style="margin-bottom:4px;">• 작용 하중/모멘트: P_serv = ${f1(r.P_serv || r.Pserv || 600)} kN, M_serv = ${f1(r.M_serv || r.Mserv || r.Mux || 50)} kN·m</div>
        <div style="margin-bottom:4px;">• 편심량: e = M / P = ${f3((r.M_serv || r.Mux || 0) / (r.P_serv || r.Pu || 1))} m (한계 e_allow = B/6 = ${f3((r.Bx || 2000) / 6000)} m)</div>
        <div style="margin-bottom:4px;">• 접지압 분포: ${((r.M_serv || r.Mux || 0) / (r.P_serv || r.Pu || 1)) <= (r.Bx || 2000) / 6000 ? '사다리꼴 분포 (e ≤ B/6)' : '삼각형 분포 (e > B/6)'}</div>
        <div style="margin-bottom:4px;">• 최대/최소 접지압: qmax = <b>${f1(qmax)} kN/m²</b>, qmin = <b>${f1(qmin)} kN/m²</b></div>
        <div>• 판정: qmax = ${f1(qmax)} kN/m² ≤ qa = ${f1(qa)} kN/m² → ${okStr(dcr_sb <= 1.0)}</div>
      </div>
      <div>
        ${soilSvg}
      </div>
    </div>
  </div>

  <!-- Step 2: 휨모멘트 & 배근 -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(2) 휨모멘트 및 소요 철근량 검토 (Flexural Capacity φMn)</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 20 §4.1</span>
    </div>
    <div style="font-size:11px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div>• 캔틸레버 길이: L_cant = (Lx - cx)/2 = ${f0(((r.Bx || 2000) - (r.cx || 500)) / 2)} mm</div>
      <div>• 설계 휨모멘트: Mu = q_avg × L_cant² / 2 = <b>${f1(Mu_x)} kN·m</b></div>
      <div>• 배근 단면적: As = ${f0(fl.As || r.As || 2800)} mm² (ρ = ${f4(fl.rho || 0.0035)})</div>
      <div>• 설계 휨강도: φMn = φ As fy (d - a/2) = <b>${f1(phiMn_x)} kN·m</b> (φ = 0.85)</div>
    </div>
  </div>

  <!-- Step 3: 전단 (1방향 및 펀칭) -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(3) 전단 안전성 검토 (One-way & Two-way Punching Shear)</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 22 §4.2 / §4.5</span>
    </div>
    <div style="font-size:11px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div>• 1방향 보전단 위험단면: d = ${f0(r.d || 520)} mm 위치 (Vu1 = ${f1(Vu_1w)} kN)</div>
      <div>• 1방향 콘크리트 전단강도: φVc1 = (1/6) φ √fck b d = <b>${f1(phiVc_1w)} kN</b> (φ = 0.75)</div>
      <div>• 2방향 펀칭 위험단면 둘레: b0 = 2(cx + d) + 2(cy + d) = ${f0(2 * ((r.cx || 500) + (r.d || 520)) + 2 * ((r.cy || 500) + (r.d || 520)))} mm</div>
      <div>• 2방향 펀칭 전단강도: φVc2 = min(1/3, 1/6(1+2/β), ...) φ √fck b0 d = <b>${f1(phiVc_2w)} kN</b></div>
    </div>
  </div>
</div>
        `;
    }
};
})();
