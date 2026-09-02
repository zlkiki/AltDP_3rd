/**
 * AltDP_3rd Web Application Client Controller (app.js)
 * 
 * Manages parametric input binding, asynchronous API dispatching, DCR updates,
 * 2D vector section rendering, and theme toggle interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  let currentType = 'rc_beam';
  let pmChart = null;

  // DOM Elements
  const tabs = document.querySelectorAll('.tab-btn');
  const formSections = document.querySelectorAll('.form-section');
  const btnCalculate = document.getElementById('btnCalculate');
  const canvas = document.getElementById('sectionCanvas');
  const btnThemeToggle = document.getElementById('btnThemeToggle');

  const dcrValue = document.getElementById('dcrValue');
  const dcrBar = document.getElementById('dcrBar');
  const statusBadge = document.getElementById('statusBadge');
  const resultTable = document.getElementById('resultTable');
  const chartContainer = document.getElementById('chartContainer');

  // Theme Toggle Handler
  if (btnThemeToggle) {
    btnThemeToggle.addEventListener('click', () => {
      const isDark = document.body.classList.contains('dark-theme');
      if (isDark) {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        btnThemeToggle.innerText = '☀️';
      } else {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        btnThemeToggle.innerText = '🌙';
      }
      runCalculation();
    });
  }

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentType = tab.dataset.type;

      formSections.forEach(sec => sec.classList.remove('active'));
      
      const formMap = {
        'rc_beam': 'formRcBeam',
        'rc_column': 'formRcColumn',
        'rc_wall': 'formRcWall',
        'steel_beam': 'formSteelBeam',
        'cft_column': 'formCftColumn',
        'retrofit': 'formRetrofit',
        'section_db': 'formSectionDb'
      };

      const targetFormId = formMap[currentType];
      if (targetFormId && document.getElementById(targetFormId)) {
        document.getElementById(targetFormId).classList.add('active');
      }

      if (currentType === 'section_db') {
        fetchSectionDb();
      }

      // Show/hide P-M Chart Container for columns
      if (chartContainer) {
        chartContainer.style.display = (currentType === 'rc_column' || currentType === 'cft_column') ? 'flex' : 'none';
      }

      runCalculation();
    });
  });

  // Calculate triggers & debounce
  btnCalculate?.addEventListener('click', runCalculation);
  document.querySelectorAll('input, select').forEach(el => {
    el.addEventListener('input', debounce(runCalculation, 50));
  });

  // Print button
  document.getElementById('btnReport')?.addEventListener('click', () => {
    window.print();
  });

  // Zoom controls
  document.getElementById('btnResetView')?.addEventListener('click', () => {
    runCalculation();
  });

  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  // Master calculation dispatcher
  async function runCalculation() {
    switch (currentType) {
      case 'rc_beam':
        await calculateRcBeam();
        break;
      case 'rc_column':
        await calculateRcColumn();
        break;
      case 'rc_wall':
        await calculateRcWall();
        break;
      case 'steel_beam':
        await calculateSteelBeam();
        break;
      case 'cft_column':
        await calculateCftColumn();
        break;
      case 'retrofit':
        await calculateRetrofit();
        break;
      default:
        await calculateRcBeam();
        break;
    }
  }

  // 1. RC Beam
  async function calculateRcBeam() {
    const b = parseFloat(document.getElementById('beam_b')?.value) || 400;
    const h = parseFloat(document.getElementById('beam_h')?.value) || 600;
    const cover = parseFloat(document.getElementById('beam_cover')?.value) || 50;
    const As = parseFloat(document.getElementById('beam_as')?.value) || 1935;
    const Av = parseFloat(document.getElementById('beam_av')?.value) || 142.6;
    const s = parseFloat(document.getElementById('beam_s')?.value) || 200;
    const Mu = parseFloat(document.getElementById('beam_mu')?.value) || 250;
    const Vu = parseFloat(document.getElementById('beam_vu')?.value) || 150;
    const fck = parseFloat(document.getElementById('beam_fck')?.value) || 24;
    const fy = parseFloat(document.getElementById('beam_fy')?.value) || 400;

    const numTension = Math.max(Math.round(As / 387), 2);

    if (window.Renderer2D && window.Renderer2D.drawRCBeamSection && canvas) {
      window.Renderer2D.drawRCBeamSection(canvas, {
        b, h, cover, num_tension_bars: numTension, num_comp_bars: 2, bar_size: 'D22', stirrup_size: 'D10'
      });
    }

    try {
      const res = await fetch('/api/rc/beam/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ b, h, cover, As, Av, s, Mu, Vu, Tu: 0, Ma: 160, fck, fy, num_tension_bars: numTension })
      });
      const json = await res.json();
      if (json.success) {
        const d = json.data;
        const maxDcr = Math.max(d.flexure_dcr, d.shear_dcr);
        updateDcr(maxDcr);
        resultTable.innerHTML = `
          <tbody>
            <tr><td>설계 휨강도 (\\phi M_n)</td><td>${d.phi_Mn.toFixed(1)} kN·m</td></tr>
            <tr><td>휨 DCR (M_u / \\phi M_n)</td><td>${d.flexure_dcr.toFixed(3)}</td></tr>
            <tr><td>설계 전단강도 (\\phi V_n)</td><td>${d.phi_Vn.toFixed(1)} kN</td></tr>
            <tr><td>전단 DCR (V_u / \\phi V_n)</td><td>${d.shear_dcr.toFixed(3)}</td></tr>
            <tr><td>철근비 (\\rho)</td><td>${(d.rho * 100).toFixed(2)} %</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.warn("API request fallback: ", err);
    }
  }

  // 2. RC Column
  async function calculateRcColumn() {
    const b = parseFloat(document.getElementById('col_b')?.value) || 600;
    const h = parseFloat(document.getElementById('col_h')?.value) || 600;
    const bar_diam = parseFloat(document.getElementById('col_bar_diam')?.value) || 25;
    const total_bars = parseInt(document.getElementById('col_total_bars')?.value) || 12;
    const Pu = parseFloat(document.getElementById('col_pu')?.value) || 2500;
    const Mu = parseFloat(document.getElementById('col_mu')?.value) || 350;
    const fck = parseFloat(document.getElementById('col_fck')?.value) || 30;
    const fy = parseFloat(document.getElementById('col_fy')?.value) || 500;

    if (window.Renderer2D && window.Renderer2D.drawRCColumnSection && canvas) {
      window.Renderer2D.drawRCColumnSection(canvas, { b, h, total_bars });
    }

    try {
      const res = await fetch('/api/rc/column/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ b, h, cover: 60, bar_diam, total_bars, Pu, Mu, Vu: 120, fck, fy })
      });
      const json = await res.json();
      if (json.success) {
        const d = json.data;
        updateDcr(d.dcr);
        resultTable.innerHTML = `
          <tbody>
            <tr><td>최대 축강도 (\\phi P_{n,max})</td><td>${d.phi_Pn_max.toFixed(0)} kN</td></tr>
            <tr><td>소요 모멘트강도 (\\phi M_{n,cap})</td><td>${d.capacity_Mu.toFixed(1)} kN·m</td></tr>
            <tr><td>기둥 DCR</td><td>${d.dcr.toFixed(3)}</td></tr>
            <tr><td>철근비 (\\rho_g)</td><td>${(d.rho_g * 100).toFixed(2)} %</td></tr>
          </tbody>
        `;
        if (d.pm_curve) renderPmChart(d.pm_curve, Pu, Mu);
      }
    } catch (err) {
      console.warn(err);
    }
  }

  // 3. RC Shear Wall
  async function calculateRcWall() {
    const lw = parseFloat(document.getElementById('wall_lw')?.value) || 4000;
    const tw = parseFloat(document.getElementById('wall_tw')?.value) || 250;
    const hw = parseFloat(document.getElementById('wall_hw')?.value) || 3000;
    const fck = parseFloat(document.getElementById('wall_fck')?.value) || 24;
    const Vu = parseFloat(document.getElementById('wall_vu')?.value) || 450;
    const Pu = parseFloat(document.getElementById('wall_pu')?.value) || 1200;

    if (window.Renderer2D && window.Renderer2D.drawRCWallSection && canvas) {
      window.Renderer2D.drawRCWallSection(canvas, { lw, tw });
    }

    try {
      const res = await fetch('/api/v1/rc/wall/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lw, tw, hw, fck, fy: 400,
          rho_v: 0.0025, rho_h: 0.0025,
          Vu, Pu, Mu: 800
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        updateDcr(json.dcr_shear);
        resultTable.innerHTML = `
          <tbody>
            <tr><td>설계 전단강도 (\\phi V_n)</td><td>${json.phi_Vn.toFixed(1)} kN</td></tr>
            <tr><td>전단 DCR</td><td>${json.dcr_shear.toFixed(3)}</td></tr>
            <tr><td>특수경계요소(SBE) 필요여부</td><td>${json.sbe_required ? '필요 (Required)' : '불필요 (Not Required)'}</td></tr>
            <tr><td>최대 전단한계 (\\phi V_{n,max})</td><td>${json.phi_Vn_max.toFixed(1)} kN</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.warn(err);
    }
  }

  // 4. Steel Beam
  async function calculateSteelBeam() {
    const H = parseFloat(document.getElementById('st_h')?.value) || 400;
    const B = parseFloat(document.getElementById('st_b')?.value) || 200;
    const tw = parseFloat(document.getElementById('st_tw')?.value) || 8;
    const tf = parseFloat(document.getElementById('st_tf')?.value) || 13;
    const Lb = parseFloat(document.getElementById('st_lb')?.value) || 3000;
    const Mu = parseFloat(document.getElementById('st_mu')?.value) || 180;
    const Vu = parseFloat(document.getElementById('st_vu')?.value) || 120;
    const Fy = parseFloat(document.getElementById('st_fy')?.value) || 275;

    if (window.Renderer2D && window.Renderer2D.drawSteelSection && canvas) {
      window.Renderer2D.drawSteelSection(canvas, { h: H, b: B, tw, tf });
    }

    try {
      const res = await fetch('/api/steel/beam/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ H, B, tw, tf, Lb, Cb: 1.0, Mu, Vu, Fy })
      });
      const json = await res.json();
      if (json.success) {
        const d = json.data;
        updateDcr(Math.max(d.flexure_dcr, d.shear_dcr));
        resultTable.innerHTML = `
          <tbody>
            <tr><td>소성모멘트 (M_p)</td><td>${d.Mp.toFixed(1)} kN·m</td></tr>
            <tr><td>설계 휨강도 (\\phi M_n)</td><td>${d.phi_Mn.toFixed(1)} kN·m</td></tr>
            <tr><td>휨 DCR</td><td>${d.flexure_dcr.toFixed(3)}</td></tr>
            <tr><td>설계 전단강도 (\\phi V_n)</td><td>${d.phi_Vn.toFixed(1)} kN</td></tr>
            <tr><td>단면 조밀성</td><td>${d.is_flange_compact ? 'Compact (조밀)' : 'Non-compact'}</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.warn(err);
    }
  }

  // 5. CFT Column
  async function calculateCftColumn() {
    const B = parseFloat(document.getElementById('cft_b')?.value) || 400;
    const t = parseFloat(document.getElementById('cft_t')?.value) || 12;
    const fck = parseFloat(document.getElementById('cft_fck')?.value) || 30;
    const Fy = parseFloat(document.getElementById('cft_fy')?.value) || 355;
    const Pu = parseFloat(document.getElementById('cft_pu')?.value) || 3000;
    const L = parseFloat(document.getElementById('cft_l')?.value) || 4000;

    if (window.Renderer2D && window.Renderer2D.drawCFTSection && canvas) {
      window.Renderer2D.drawCFTSection(canvas, { B, H: B, t });
    }

    try {
      const res = await fetch('/api/v1/special/cft-column/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cft_type: 'RECTANGULAR',
          B, H: B, D: B, t, fck, Fy, L, K: 1.0, Pu
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        updateDcr(json.dcr_axial);
        resultTable.innerHTML = `
          <tbody>
            <tr><td>소성압축강도 (P_{no})</td><td>${json.Pno.toFixed(0)} kN</td></tr>
            <tr><td>설계 압축강도 (\\phi P_n)</td><td>${json.phi_Pn.toFixed(0)} kN</td></tr>
            <tr><td>축하중 DCR</td><td>${json.dcr_axial.toFixed(3)}</td></tr>
            <tr><td>강재 단면적 비율</td><td>${json.steel_ratio.toFixed(2)} %</td></tr>
            <tr><td>폭두께비 조밀성</td><td>${json.is_compact ? 'Compact (조밀)' : 'Non-compact'}</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.warn(err);
    }
  }

  // 6. Retrofit
  async function calculateRetrofit() {
    const b = parseFloat(document.getElementById('ret_b')?.value) || 300;
    const h = parseFloat(document.getElementById('ret_h')?.value) || 600;
    const cfrp_bf = parseFloat(document.getElementById('ret_cfrp_bf')?.value) || 200;
    const cfrp_tf = parseFloat(document.getElementById('ret_cfrp_tf')?.value) || 1.2;
    const Mu = parseFloat(document.getElementById('ret_mu')?.value) || 350;
    const Vu = parseFloat(document.getElementById('ret_vu')?.value) || 180;

    if (window.Renderer2D && window.Renderer2D.drawRetrofitSection && canvas) {
      window.Renderer2D.drawRetrofitSection(canvas, { b, h, cfrp_bf });
    }

    try {
      const res = await fetch('/api/v1/special/retrofit/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          retrofit_type: 'FLEXURE',
          method: 'CFRP_PLATE',
          b, h, d: h - 60, fck: 24, As: 1520, fy: 400, Av: 142.6, s: 200,
          cfrp_tf, cfrp_bf, num_plies: 1, Mu, Vu
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        updateDcr(json.dcr_flexure);
        resultTable.innerHTML = `
          <tbody>
            <tr><td>보강 전 휨강도 (\\phi M_{n0})</td><td>${json.phi_Mn_orig.toFixed(1)} kN·m</td></tr>
            <tr><td>CFRP 보강 후 휨강도 (\\phi M_{nr})</td><td>${json.phi_Mn_ret.toFixed(1)} kN·m</td></tr>
            <tr><td>휨 내력 증진율</td><td>+${((json.flexure_gain_ratio - 1) * 100).toFixed(1)} %</td></tr>
            <tr><td>휨 DCR</td><td>${json.dcr_flexure.toFixed(3)}</td></tr>
            <tr><td>박리 파괴 지배여부</td><td>${json.debonding_governed ? '박리 제어 (Governed)' : '항복 지배'}</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.warn(err);
    }
  }

  // Section DB Fetch
  async function fetchSectionDb() {
    const dbCode = document.getElementById('db_code')?.value || 'KS';
    const query = document.getElementById('db_search')?.value || '';
    const listEl = document.getElementById('dbResultsList');
    if (!listEl) return;

    try {
      const res = await fetch(`/api/db/sections?db=${dbCode}&query=${encodeURIComponent(query)}`);
      const json = await res.json();
      if (json.success) {
        listEl.innerHTML = json.data.map(item => `
          <div class="db-item" data-h="${item.H}" data-b="${item.B}" data-tw="${item.tw}" data-tf="${item.tf}">
            <span>${item.name}</span>
            <span>A: ${item.A.toFixed(1)} cm²</span>
          </div>
        `).join('');

        listEl.querySelectorAll('.db-item').forEach(item => {
          item.addEventListener('click', () => {
            const stH = document.getElementById('st_h');
            const stB = document.getElementById('st_b');
            const stTw = document.getElementById('st_tw');
            const stTf = document.getElementById('st_tf');
            if (stH) stH.value = item.dataset.h;
            if (stB) stB.value = item.dataset.b;
            if (stTw) stTw.value = item.dataset.tw;
            if (stTf) stTf.value = item.dataset.tf;
            document.getElementById('tabSteelBeam')?.click();
          });
        });
      }
    } catch (err) {
      console.warn(err);
    }
  }

  document.getElementById('db_search')?.addEventListener('input', debounce(fetchSectionDb, 200));
  document.getElementById('db_code')?.addEventListener('change', fetchSectionDb);

  // DCR UI Helper
  function updateDcr(dcr) {
    if (!dcrValue || !dcrBar || !statusBadge) return;
    dcrValue.innerText = dcr.toFixed(3);
    const pct = Math.min(dcr * 100, 100);
    dcrBar.style.width = pct + '%';

    if (dcr <= 0.90) {
      dcrValue.className = 'dcr-number';
      dcrBar.className = 'progress-bar-fill ok';
      statusBadge.className = 'dcr-badge status-ok';
      statusBadge.innerText = 'SAFE (안전)';
    } else if (dcr <= 1.0) {
      dcrValue.className = 'dcr-number warn';
      dcrBar.className = 'progress-bar-fill warn';
      statusBadge.className = 'dcr-badge status-warn';
      statusBadge.innerText = 'WARN (주의)';
    } else {
      dcrValue.className = 'dcr-number ng';
      dcrBar.className = 'progress-bar-fill ng';
      statusBadge.className = 'dcr-badge status-ng';
      statusBadge.innerText = 'NG (초과)';
    }
  }

  // P-M Chart Renderer Helper
  function renderPmChart(curveData, Pu, Mu) {
    const chartCanvas = document.getElementById('pmChartCanvas');
    if (!chartCanvas) return;

    if (window.PMChartRenderer) {
      const pm = new window.PMChartRenderer('pmChartCanvas');
      pm.render({ pm_curve: curveData, Pu, Mu, is_safe: Pu > 0 });
    }
  }

  // Initial Calculation Run
  runCalculation();
});
