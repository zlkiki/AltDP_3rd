/**
 * AltDP_3rd Web Application Client Controller & 2D Section Renderer
 */

document.addEventListener('DOMContentLoaded', () => {
  // Current active member type
  let currentType = 'rc_beam';
  let pmChart = null;

  // DOM Elements
  const tabs = document.querySelectorAll('.tab-btn');
  const formSections = document.querySelectorAll('.form-section');
  const btnCalculate = document.getElementById('btnCalculate');
  const canvas = document.getElementById('sectionCanvas');
  const ctx = canvas.getContext('2d');

  const dcrValue = document.getElementById('dcrValue');
  const dcrBar = document.getElementById('dcrBar');
  const statusBadge = document.getElementById('statusBadge');
  const resultTable = document.getElementById('resultTable');
  const chartContainer = document.getElementById('chartContainer');

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentType = tab.dataset.type;

      formSections.forEach(sec => sec.classList.remove('active'));
      if (currentType === 'rc_beam') document.getElementById('formRcBeam').classList.add('active');
      if (currentType === 'rc_column') document.getElementById('formRcColumn').classList.add('active');
      if (currentType === 'steel_beam') document.getElementById('formSteelBeam').classList.add('active');
      if (currentType === 'section_db') {
        document.getElementById('formSectionDb').classList.add('active');
        fetchSectionDb();
      }

      chartContainer.style.display = (currentType === 'rc_column') ? 'flex' : 'none';
      runCalculation();
    });
  });

  // Calculation button & input change triggers
  btnCalculate.addEventListener('click', runCalculation);
  document.querySelectorAll('input, select').forEach(el => {
    el.addEventListener('input', debounce(runCalculation, 300));
  });

  // Print button
  document.getElementById('btnReport').addEventListener('click', () => {
    window.print();
  });

  // Debounce utility
  function debounce(func, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  // Master calculation dispatcher
  async function runCalculation() {
    if (currentType === 'rc_beam') {
      await calculateRcBeam();
    } else if (currentType === 'rc_column') {
      await calculateRcColumn();
    } else if (currentType === 'steel_beam') {
      await calculateSteelBeam();
    }
  }

  // 1. RC Beam Calculation & Rendering
  async function calculateRcBeam() {
    const b = parseFloat(document.getElementById('beam_b').value) || 400;
    const h = parseFloat(document.getElementById('beam_h').value) || 600;
    const cover = parseFloat(document.getElementById('beam_cover').value) || 50;
    const As = parseFloat(document.getElementById('beam_as').value) || 1935;
    const Av = parseFloat(document.getElementById('beam_av').value) || 142.6;
    const s = parseFloat(document.getElementById('beam_s').value) || 200;
    const Mu = parseFloat(document.getElementById('beam_mu').value) || 250;
    const Vu = parseFloat(document.getElementById('beam_vu').value) || 150;
    const fck = parseFloat(document.getElementById('beam_fck').value) || 24;
    const fy = parseFloat(document.getElementById('beam_fy').value) || 400;

    renderRcBeamCanvas(b, h, cover, As);

    try {
      const res = await fetch('/api/rc/beam/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ b, h, cover, As, Av, s, Mu, Vu, fck, fy })
      });
      const json = await res.json();
      if (json.success) {
        const d = json.data;
        updateDcr(Math.max(d.flexure_dcr, d.shear_dcr));
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
      console.error(err);
    }
  }

  // 2. RC Column Calculation & Rendering
  async function calculateRcColumn() {
    const b = parseFloat(document.getElementById('col_b').value) || 600;
    const h = parseFloat(document.getElementById('col_h').value) || 600;
    const bar_diam = parseFloat(document.getElementById('col_bar_diam').value) || 25;
    const total_bars = parseInt(document.getElementById('col_total_bars').value) || 12;
    const Pu = parseFloat(document.getElementById('col_pu').value) || 2500;
    const Mu = parseFloat(document.getElementById('col_mu').value) || 350;
    const fck = parseFloat(document.getElementById('col_fck').value) || 30;
    const fy = parseFloat(document.getElementById('col_fy').value) || 500;

    renderRcColumnCanvas(b, h, bar_diam, total_bars);

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
        renderPmChart(d.pm_curve, Pu, Mu);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 3. Steel Beam Calculation & Rendering
  async function calculateSteelBeam() {
    const H = parseFloat(document.getElementById('st_h').value) || 400;
    const B = parseFloat(document.getElementById('st_b').value) || 200;
    const tw = parseFloat(document.getElementById('st_tw').value) || 8;
    const tf = parseFloat(document.getElementById('st_tf').value) || 13;
    const Lb = parseFloat(document.getElementById('st_lb').value) || 3000;
    const Mu = parseFloat(document.getElementById('st_mu').value) || 180;
    const Vu = parseFloat(document.getElementById('st_vu').value) || 120;
    const Fy = parseFloat(document.getElementById('st_fy').value) || 275;

    renderSteelBeamCanvas(H, B, tw, tf);

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
            <tr><td>휨 DCR (M_u / \\phi M_n)</td><td>${d.flexure_dcr.toFixed(3)}</td></tr>
            <tr><td>설계 전단강도 (\\phi V_n)</td><td>${d.phi_Vn.toFixed(1)} kN</td></tr>
            <tr><td>플랜지 콤팩트 여부</td><td>${d.is_flange_compact ? 'Compact (OK)' : 'Non-compact'}</td></tr>
          </tbody>
        `;
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 4. Section DB Fetch
  async function fetchSectionDb() {
    const dbCode = document.getElementById('db_code').value;
    const query = document.getElementById('db_search').value;
    const listEl = document.getElementById('dbResultsList');

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
            document.getElementById('st_h').value = item.dataset.h;
            document.getElementById('st_b').value = item.dataset.b;
            document.getElementById('st_tw').value = item.dataset.tw;
            document.getElementById('st_tf').value = item.dataset.tf;
            document.getElementById('tabSteelBeam').click();
          });
        });
      }
    } catch (err) {
      console.error(err);
    }
  }

  document.getElementById('db_search')?.addEventListener('input', debounce(fetchSectionDb, 300));
  document.getElementById('db_code')?.addEventListener('change', fetchSectionDb);

  // DCR UI Helper
  function updateDcr(dcr) {
    dcrValue.innerText = dcr.toFixed(3);
    const pct = Math.min(dcr * 100, 100);
    dcrBar.style.width = pct + '%';

    if (dcr <= 1.0) {
      dcrValue.className = 'dcr-number';
      dcrBar.className = 'progress-bar-fill ok';
      statusBadge.className = 'dcr-badge status-ok';
      statusBadge.innerText = 'OK (안전)';
    } else {
      dcrValue.className = 'dcr-number ng';
      dcrBar.className = 'progress-bar-fill ng';
      statusBadge.className = 'dcr-badge status-ng';
      statusBadge.innerText = 'NG (초과)';
    }
  }

  // 2D Canvas Renderers
  function renderRcBeamCanvas(b, h, cover, As) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scale = Math.min((canvas.width - 120) / b, (canvas.height - 120) / h);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    const w_px = b * scale;
    const h_px = h * scale;
    const x0 = cx - w_px / 2;
    const y0 = cy - h_px / 2;

    // Concrete section
    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2;
    ctx.fillRect(x0, y0, w_px, h_px);
    ctx.strokeRect(x0, y0, w_px, h_px);

    // Stirrup
    const cov_px = cover * scale;
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 2;
    ctx.strokeRect(x0 + cov_px, y0 + cov_px, w_px - 2 * cov_px, h_px - 2 * cov_px);

    // Main tension rebars (Bottom 4~5 bars)
    const num_bars = 4;
    const r_px = 7;
    ctx.fillStyle = '#ef4444';
    for (let i = 0; i < num_bars; i++) {
      const bx = x0 + cov_px + r_px + (i * (w_px - 2 * cov_px - 2 * r_px) / (num_bars - 1));
      const by = y0 + h_px - cov_px - r_px;
      ctx.beginPath();
      ctx.arc(bx, by, r_px, 0, 2 * Math.PI);
      ctx.fill();
    }

    // Dimension labels
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px JetBrains Mono';
    ctx.fillText(`b = ${b} mm`, cx - 30, y0 - 15);
    ctx.fillText(`h = ${h} mm`, x0 + w_px + 15, cy);
  }

  function renderRcColumnCanvas(b, h, bar_diam, total_bars) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scale = Math.min((canvas.width - 120) / b, (canvas.height - 120) / h);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    const w_px = b * scale;
    const h_px = h * scale;
    const x0 = cx - w_px / 2;
    const y0 = cy - h_px / 2;

    ctx.fillStyle = '#1e293b';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2;
    ctx.fillRect(x0, y0, w_px, h_px);
    ctx.strokeRect(x0, y0, w_px, h_px);

    // Tie
    const cov_px = 60 * scale;
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.strokeRect(x0 + cov_px, y0 + cov_px, w_px - 2 * cov_px, h_px - 2 * cov_px);

    // Rebars around perimeter
    ctx.fillStyle = '#ef4444';
    const r_px = 8;
    const pts = [
      [x0 + cov_px + r_px, y0 + cov_px + r_px],
      [x0 + w_px - cov_px - r_px, y0 + cov_px + r_px],
      [x0 + cov_px + r_px, y0 + h_px - cov_px - r_px],
      [x0 + w_px - cov_px - r_px, y0 + h_px - cov_px - r_px],
      [cx, y0 + cov_px + r_px],
      [cx, y0 + h_px - cov_px - r_px],
      [x0 + cov_px + r_px, cy],
      [x0 + w_px - cov_px - r_px, cy]
    ];
    pts.forEach(([px, py]) => {
      ctx.beginPath();
      ctx.arc(px, py, r_px, 0, 2 * Math.PI);
      ctx.fill();
    });
  }

  function renderSteelBeamCanvas(H, B, tw, tf) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scale = Math.min((canvas.width - 120) / B, (canvas.height - 120) / H);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    const H_px = H * scale;
    const B_px = B * scale;
    const tw_px = Math.max(tw * scale, 3);
    const tf_px = Math.max(tf * scale, 4);

    const x0 = cx - B_px / 2;
    const y0 = cy - H_px / 2;

    ctx.fillStyle = '#38bdf8';
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 1;

    // Top flange
    ctx.fillRect(x0, y0, B_px, tf_px);
    // Web
    ctx.fillRect(cx - tw_px / 2, y0 + tf_px, tw_px, H_px - 2 * tf_px);
    // Bottom flange
    ctx.fillRect(x0, y0 + H_px - tf_px, B_px, tf_px);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px JetBrains Mono';
    ctx.fillText(`H = ${H}`, cx + B_px / 2 + 15, cy);
    ctx.fillText(`B = ${B}`, cx - 20, y0 - 15);
  }

  // P-M Chart Renderer
  function renderPmChart(curveData, Pu, Mu) {
    const chartCanvas = document.getElementById('pmChartCanvas');
    if (!chartCanvas) return;

    const labels = curveData.map(p => p.phi_Mn.toFixed(0));
    const nominalData = curveData.map(p => ({ x: p.Mn, y: p.Pn }));
    const designData = curveData.map(p => ({ x: p.phi_Mn, y: p.phi_Pn }));

    if (pmChart) {
      pmChart.destroy();
    }

    pmChart = new Chart(chartCanvas, {
      type: 'line',
      data: {
        datasets: [
          {
            label: '공칭강도 (Pn-Mn)',
            data: nominalData,
            borderColor: '#64748b',
            borderDash: [5, 5],
            borderWidth: 1.5,
            fill: false,
            tension: 0.1
          },
          {
            label: '설계강도 (φPn-φMn)',
            data: designData,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.1
          },
          {
            label: '설계하중 (Pu, Mu)',
            data: [{ x: Mu, y: Pu }],
            backgroundColor: '#ef4444',
            borderColor: '#ffffff',
            borderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            showLine: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'linear',
            title: { display: true, text: 'Moment M (kN·m)', color: '#94a3b8' },
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#94a3b8' }
          },
          y: {
            title: { display: true, text: 'Axial P (kN)', color: '#94a3b8' },
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#94a3b8' }
          }
        },
        plugins: {
          legend: { labels: { color: '#f8fafc', font: { size: 10 } } }
        }
      }
    });
  }

  // Initial Calculation
  runCalculation();
});
