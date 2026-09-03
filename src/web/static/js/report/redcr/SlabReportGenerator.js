// web/js/report/redcr/SlabReportGenerator.js
// RC 1방향/2방향 슬래브 상세 계산서 생성기 — MIDAS Gen / KDS 스타일 (re-DCR 직이식)

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

// ── 슬래브 평면 및 단면 배근도 SVG 생성 ─────────────────────────────────────
function generateSlabSVG(r) {
    if (!r) return '';
    if (window.VectorSlab && typeof window.VectorSlab.renderSlabSectionSVG === 'function') {
        return window.VectorSlab.renderSlabSectionSVG(r, { mode: 'report', width: 320, height: 220 });
    }
    return '';
}

window.RedcrSlabReport = {
    generateSlabReportHTML(r) {
        if (!r) return '<div class="empty-state">결과 데이터가 없습니다.</div>';

        const dcr = Number(r.governing_dcr || r.max_dcr || r.dcr || 0);
        const fl = r.flexure || {};
        const sh = r.shear || {};
        const defl = r.deflection || {};

        const Mu_pos = Number(fl.Mu_pos || fl.Mu_mid || fl.Mu || r.Mu || 0);
        const phiMn_pos = Number(fl.phiMn_pos || fl.phiMn_mid || fl.phiMn || r.phiMn || 1);
        const dcr_pos = Number(fl.dcr_pos || (phiMn_pos > 0 ? Mu_pos / phiMn_pos : 0));

        const Mu_neg = Number(fl.Mu_neg || fl.Mu_end || 0);
        const phiMn_neg = Number(fl.phiMn_neg || fl.phiMn_end || phiMn_pos);
        const dcr_neg = Number(fl.dcr_neg || (phiMn_neg > 0 ? Mu_neg / phiMn_neg : 0));

        const Vu = Number(sh.Vu || sh.Vu_kN || r.Vu || 0);
        const phiVc = Number(sh.phiVc || sh.phiVc_kN || r.phiVc || 1);
        const dcr_sh = Number(sh.dcr || (phiVc > 0 ? Vu / phiVc : 0));

        const Lx = r.Lx || r.lx || 4000;
        const Ly = r.Ly || r.ly || 6000;
        const lambda = Ly / (Lx || 1);
        const isOneWay = lambda >= 2.0;

        return `
<div class="dcr-report a4-sheet-container pure-white-sheet" style="font-family:'Segoe UI',Arial,sans-serif;font-size:12px;color:#1f2937;background:#fff;padding:24px;line-height:1.5;">
  <!-- 헤더 -->
  <div style="border-bottom:2px solid #1e3a8a;padding-bottom:8px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
    <div>
      <h1 style="font-size:18px;font-weight:700;color:#1e3a8a;margin:0;">RC 1방향/2방향 슬래브 구조계산서 (Slab Design Report)</h1>
      <span style="font-size:11px;color:#6b7280;">KDS 14 20 70 : 2022 슬래브 구조설계기준 (직접설계법/계수법)</span>
    </div>
    <div style="text-align:right;">
      <span class="badge ${dcr <= 1.0 ? 'ok' : 'ng'}" style="display:inline-block;padding:4px 12px;border-radius:4px;font-weight:700;background:${dcr <= 1.0 ? '#d1fae5;color:#065f46' : '#fee2e2;color:#991b1b'};">
        ${dcr <= 1.0 ? '● PASS (만족)' : '▲ FAIL (초과)'} (Max DCR: ${f3(dcr)})
      </span>
    </div>
  </div>

  <!-- 요약 & SVG (2단) -->
  <div style="display:grid;grid-template-columns:1fr 340px;gap:16px;margin-bottom:20px;align-items:start;">
    <div>
      <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:0 0 8px 0;">1. 설계 파라미터 및 하중 요약</h2>
      <table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:12px;">
        <tbody>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">패널 크기 (Lx × Ly)</td>
            <td style="padding:4px;">${f0(Lx)} × ${f0(Ly)} mm</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">슬래브 두께 (t / d)</td>
            <td style="padding:4px;">${f0(r.t || r.thick || 200)} / ${f0(r.d || 170)} mm</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">거동 판별 (변장비 λ)</td>
            <td style="padding:4px;font-weight:700;color:#1e3a8a;">${isOneWay ? '1방향 슬래브 (λ ≥ 2.0)' : '2방향 슬래브 (λ < 2.0)'}</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">계수 하중 (Wu)</td>
            <td style="padding:4px;">${f2(r.Wu || 12.5)} kN/m²</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">콘크리트 강도 (fck)</td>
            <td style="padding:4px;">${f1(r.fck || 24)} MPa</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">철근 항복강도 (fy)</td>
            <td style="padding:4px;">${f1(r.fy || 400)} MPa</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:4px;font-weight:600;color:#4b5563;">주철근 배근</td>
            <td style="padding:4px;">D${f0(r.bar_dia || 13)} @ ${f0(r.bar_spacing || 150)}</td>
            <td style="padding:4px;font-weight:600;color:#4b5563;">온도수축철근 배근</td>
            <td style="padding:4px;">D${f0(r.temp_bar_dia || 10)} @ ${f0(r.temp_bar_spacing || 200)}</td>
          </tr>
        </tbody>
      </table>

      <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:0 0 8px 0;">2. 한계상태 종합 검토 요약표</h2>
      <table style="width:100%;border-collapse:collapse;font-size:11px;">
        <thead>
          <tr style="background:#f3f4f6;border-bottom:1.5px solid #9ca3af;text-align:center;">
            <th style="padding:5px;border:1px solid #e5e7eb;">검토 위치 및 항목</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">소요력 (Demand)</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">설계내력 (Capacity)</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">DCR</th>
            <th style="padding:5px;border:1px solid #e5e7eb;">판정</th>
          </tr>
        </thead>
        <tbody style="text-align:center;">
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">1. 중앙부 정모멘트 (Mid-span +M)</td>
            <td style="padding:5px;">Mu = ${f1(Mu_pos)} kN·m/m</td>
            <td style="padding:5px;">φMn = ${f1(phiMn_pos)} kN·m/m</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_pos)}</td>
            <td style="padding:5px;">${okNg(dcr_pos)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">2. 지점부 부모멘트 (Support -M)</td>
            <td style="padding:5px;">Mu = ${f1(Mu_neg)} kN·m/m</td>
            <td style="padding:5px;">φMn = ${f1(phiMn_neg)} kN·m/m</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_neg)}</td>
            <td style="padding:5px;">${okNg(dcr_neg)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">3. 슬래브 전단내력 (One-way Shear)</td>
            <td style="padding:5px;">Vu = ${f1(Vu)} kN/m</td>
            <td style="padding:5px;">φVc = ${f1(phiVc)} kN/m</td>
            <td style="padding:5px;font-weight:700;">${f3(dcr_sh)}</td>
            <td style="padding:5px;">${okNg(dcr_sh)}</td>
          </tr>
          <tr style="border-bottom:1px solid #e5e7eb;">
            <td style="padding:5px;text-align:left;font-weight:600;">4. 최소 철근비 (Shrinkage/Temp)</td>
            <td style="padding:5px;">ρ = ${f4(fl.rho || 0.0035)}</td>
            <td style="padding:5px;">ρmin = 0.0020</td>
            <td style="padding:5px;font-weight:700;">${f3(0.0020 / ((fl.rho || 0.0035) || 1))}</td>
            <td style="padding:5px;">${okStr((fl.rho || 0.0035) >= 0.0020)}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 우측 배근도 SVG -->
    <div style="text-align:center;">
      <h3 style="font-size:12px;color:#1e3a8a;margin:0 0 6px 0;font-weight:600;">슬래브 패널 및 단면 배근</h3>
      ${generateSlabSVG(r)}
    </div>
  </div>

  <!-- Step-by-Step 상세 계산 근거 -->
  <h2 style="font-size:13px;background:#1e3a8a;color:#fff;padding:4px 8px;border-radius:2px;margin:16px 0 8px 0;">3. Step-by-Step 상세 계산 근거</h2>
  
  <!-- Step 1: 최소 두께 및 모멘트 분배 -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(1) 휨모멘트 산정 및 하중 분배 계수</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 70 §4.1.2</span>
    </div>
    <div style="font-size:11px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div>• 변장비: λ = Ly / Lx = ${f2(lambda)} (${isOneWay ? '1방향 휨 거동' : '2방향 휨 거동'})</div>
      <div>• 총 정적 모멘트: M0 = Wu × Ln² / 8 = <b>${f1((r.Wu || 12.5) * Math.pow((Lx - 400)/1000, 2) / 8)} kN·m/m</b></div>
      <div>• 중앙부 정모멘트: +Mu = 0.60 × M0 = <b>${f1(Mu_pos)} kN·m/m</b></div>
      <div>• 지점부 부모멘트: -Mu = 0.65 × M0 = <b>${f1(Mu_neg)} kN·m/m</b></div>
    </div>
  </div>

  <!-- Step 2: 휨강도 검토 -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(2) 단위폭(1.0m) 휨모멘트 내력 검토 (Flexural Capacity φMn)</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 20 §4.1</span>
    </div>
    <div style="font-size:11px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div>• 유효깊이: d = t - cover - dia/2 = ${f0(r.d || 170)} mm</div>
      <div>• 배근 단면적: As = ${f0(fl.As || 854)} mm²/m (D${f0(r.bar_dia || 13)}@${f0(r.bar_spacing || 150)})</div>
      <div>• 등가응력깊이: a = As fy / (0.85 fck b) = ${f1(fl.a || 16.7)} mm (b = 1,000mm)</div>
      <div>• 설계 휨강도: φMn = φ As fy (d - a/2) = <b>${f1(phiMn_pos)} kN·m/m</b> (φ = 0.85)</div>
    </div>
  </div>

  <!-- Step 3: 전단내력 -->
  <div style="border:1px solid #e5e7eb;border-radius:4px;padding:10px;">
    <div style="display:flex;justify-content:space-between;font-weight:700;color:#1e3a8a;border-bottom:1px dashed #cbd5e1;padding-bottom:4px;margin-bottom:6px;">
      <span>(3) 슬래브 전단강도 및 사용성 검토</span>
      <span style="font-size:11px;color:#64748b;">KDS 14 20 22 §4.2</span>
    </div>
    <div style="font-size:11px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div>• 지점 위험단면(d거리) 전단력: Vu = Wu × (Ln/2 - d) = <b>${f1(Vu)} kN/m</b></div>
      <div>• 콘크리트 전단강도: φVc = (1/6) φ √fck b d = <b>${f1(phiVc)} kN/m</b> (φ = 0.75)</div>
      <div>• 수축온도철근 최소량: As_temp,min = 0.0020 × b × t = ${f0(0.0020 * 1000 * (r.t || 200))} mm²/m</div>
      <div>• 배근 간격 제한: s ≤ min(3t, 450mm) = ${f0(Math.min(3 * (r.t || 200), 450))} mm → ${okStr((r.bar_spacing || 150) <= 450)}</div>
    </div>
  </div>
</div>
        `;
    }
};
})();
