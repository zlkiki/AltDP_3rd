/**
 * AltDP_3rd Member Parametric Forms Controller
 * Handles dynamic property grids & P-Mode Auto Design for RC and Steel members.
 */

const MemberForms = {
  // Current member definitions
  schemas: {
    rc_beam: [
      { id: 'b', label: '단면 폭 b (mm)', type: 'number', val: 400, step: 50 },
      { id: 'h', label: '단면 높이 h (mm)', type: 'number', val: 600, step: 50 },
      { id: 'fck', label: '콘크리트 강도 fck (MPa)', type: 'number', val: 27, step: 3 },
      { id: 'fy', label: '철근 항복강도 fy (MPa)', type: 'number', val: 400, step: 100 },
      { id: 'cover', label: '피복두께 cc (mm)', type: 'number', val: 40, step: 5 },
      { id: 'top_rebar', label: '상부근 규격', type: 'text', val: '4-D22' },
      { id: 'bot_rebar', label: '하부근 규격', type: 'text', val: '4-D25' },
      { id: 'stirrup', label: '전단 늑근 규격', type: 'text', val: 'D10 @ 150' },
      { id: 'mu', label: '설계 휨모멘트 Mu (kN·m)', type: 'number', val: 180.0, step: 10 },
      { id: 'vu', label: '설계 전단력 Vu (kN)', type: 'number', val: 140.0, step: 10 }
    ],
    rc_column: [
      { id: 'b', label: '기둥 폭 b (mm)', type: 'number', val: 600, step: 50 },
      { id: 'h', label: '기둥 높이 h (mm)', type: 'number', val: 600, step: 50 },
      { id: 'fck', label: '콘크리트 강도 fck (MPa)', type: 'number', val: 30, step: 3 },
      { id: 'fy', label: '주철근 강도 fy (MPa)', type: 'number', val: 500, step: 100 },
      { id: 'main_rebar', label: '주철근 배치', type: 'text', val: '12-D25' },
      { id: 'tie_rebar', label: '띠철근 (Tie)', type: 'text', val: 'D10 @ 200' },
      { id: 'pu', label: '설계 축력 Pu (kN)', type: 'number', val: 1200.0, step: 100 },
      { id: 'mu', label: '설계 모멘트 Mu (kN·m)', type: 'number', val: 240.0, step: 20 }
    ],
    steel_beam: [
      { id: 'section_name', label: '형강 규격', type: 'text', val: 'H-400x200x8x13' },
      { id: 'fy', label: '강재 항복강도 Fy (MPa)', type: 'number', val: 355, step: 10 },
      { id: 'length', label: '부재 길이 L (m)', type: 'number', val: 6.0, step: 0.5 },
      { id: 'lb', label: '비지지 길이 Lb (m)', type: 'number', val: 2.0, step: 0.5 },
      { id: 'mu', label: '설계 휨모멘트 Mu (kN·m)', type: 'number', val: 220.0, step: 10 },
      { id: 'vu', label: '설계 전단력 Vu (kN)', type: 'number', val: 110.0, step: 10 }
    ]
  },

  renderForm(containerId, memberType) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const fields = this.schemas[memberType] || this.schemas.rc_beam;
    let html = `<div style="display:flex; flex-direction:column; gap:8px;">`;

    fields.forEach(f => {
      html += `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
          <label style="font-size:11px; color:var(--text-secondary); flex:1;">${f.label}</label>
          <input type="${f.type}" id="field-${f.id}" value="${f.val}" 
            style="width:130px; background:var(--bg-input); color:var(--text-primary); border:1px solid var(--border-glass); border-radius:var(--radius-xs); padding:4px 8px; font-size:12px;"
            ${f.step ? `step="${f.step}"` : ''}>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;

    // Attach change event
    fields.forEach(f => {
      const el = document.getElementById(`field-${f.id}`);
      if (el) {
        el.addEventListener('input', () => {
          if (window.App && typeof window.App.onFormParamChange === 'function') {
            window.App.onFormParamChange();
          }
        });
      }
    });
  },

  getFormData(memberType) {
    const fields = this.schemas[memberType] || this.schemas.rc_beam;
    const data = { member_type: memberType };
    fields.forEach(f => {
      const el = document.getElementById(`field-${f.id}`);
      if (el) {
        data[f.id] = f.type === 'number' ? parseFloat(el.value) || 0 : el.value;
      }
    });
    return data;
  },

  // P-Mode: Parametric Auto-Design algorithm
  autoDesign(memberType) {
    const cur = this.getFormData(memberType);
    if (memberType === 'rc_beam') {
      const reqMu = cur.mu || 180;
      // Auto estimate rebar requirement
      let suggestedRebar = '4-D25';
      if (reqMu > 280) suggestedRebar = '5-D29';
      else if (reqMu > 200) suggestedRebar = '4-D29';
      else if (reqMu < 120) suggestedRebar = '3-D19';

      const botEl = document.getElementById('field-bot_rebar');
      if (botEl) botEl.value = suggestedRebar;
      return { bot_rebar: suggestedRebar, message: `P-Mode 자동설계 완료: ${suggestedRebar}` };
    } else if (memberType === 'rc_column') {
      const reqPu = cur.pu || 1200;
      let suggestedMain = '12-D25';
      if (reqPu > 2000) suggestedMain = '16-D29';
      else if (reqPu < 800) suggestedMain = '8-D22';

      const mainEl = document.getElementById('field-main_rebar');
      if (mainEl) mainEl.value = suggestedMain;
      return { main_rebar: suggestedMain, message: `P-Mode 자동설계 완료: ${suggestedMain}` };
    }
    return { message: '자동설계가 지원되지 않는 부재 유형입니다.' };
  }
};

window.MemberForms = MemberForms;
