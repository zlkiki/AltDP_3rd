// web/js/report/redcr/common/levelFactorsSection.js
/**
 * AltDP Member Designer - Level Factors & Load Combinations Section
 * Zero-Build Vanilla JavaScript & Browser Global Namespace
 */

(function () {
    const H = (typeof window !== 'undefined' ? (window.RedcrFormat || (window.RedcrCommon && window.RedcrCommon.formatHelpers)) : null) || {
        esc: s => String(s || ''),
        nf: (v, d = 3) => Number(v || 0).toFixed(d)
    };
    const F = (typeof window !== 'undefined' ? window.RedcrFormulas : null) || {
        sectionHeader: (n, t, k) => `<h2>${n} ${t}</h2>`
    };

    function levelFactorsSection(input) {
        if (!input || !input.level) return '';
        const { level, endI, endJ } = input;
        
        const factors = `
<div class="calc-block">
<div class="calc-title">내진 레벨 계수표 (재현주기 ${level.returnPeriod || 2400}yr · ${level.performanceLevel || 'LS'})</div>
<table class="inp-table">
  <tr><td class="inp-label">위험도 계수 I_r</td><td class="inp-val">${H.nf(level.Ir, 3)}</td><td></td></tr>
  <tr><td class="inp-label">응답스펙트럼 스케일</td><td class="inp-val">${H.nf(level.irScale, 3)}</td><td class="inp-unit">= I_r / rsaIr</td></tr>
  <tr><td class="inp-label">비탄성 변위 보정 C_1</td><td class="inp-val">${H.nf(level.C1, 3)}</td><td></td></tr>
  <tr><td class="inp-label">하중전달 계수 J</td><td class="inp-val">${H.nf(level.J, 3)}</td><td></td></tr>
  <tr><td class="inp-label">성능수준 계수 &#967;</td><td class="inp-val">${H.nf(level.chi, 3)}</td><td></td></tr>
</table>
</div>
<div class="calc-block">
<div class="calc-title">하중조합 수식 (내진성능평가 세부지침 §3.5)</div>
<div class="calc-step">
  <div class="calc-formula">변형지배 요구량: Q_UD = Q_G + Q_E &nbsp;&nbsp; (Eq. 3.5.6)</div>
  <div class="calc-formula">강도지배 요구량: Q_UF = Q_G + &#967; &middot; Q_E / (C &middot; J) &nbsp;&nbsp; (Eq. 3.5.7)</div>
</div>
</div>
`;
        return F.sectionHeader('2', '하중조합 및 성능계수 (Level Factors &amp; Load Combinations)', '세부지침 §3.5') + factors;
    }

    if (typeof window !== 'undefined') {
        window.RedcrCommon = window.RedcrCommon || {};
        window.RedcrCommon.levelFactorsSection = levelFactorsSection;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { levelFactorsSection };
    }
})();
