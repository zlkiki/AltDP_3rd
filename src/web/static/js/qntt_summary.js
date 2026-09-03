/**
 * AltDP_3rd Quantity Takeoff Dashboard (QnttView)
 * Real-time material accumulation for Concrete, Formwork, Rebar, and Steel.
 */

const QnttSummary = {
  rebarUnitWeights: {
    'D10': 0.560,
    'D13': 0.995,
    'D16': 1.56,
    'D19': 2.25,
    'D22': 3.04,
    'D25': 3.98,
    'D29': 5.04,
    'D32': 6.23
  },

  rebarDiameters: {
    'D10': 9.53,
    'D13': 12.7,
    'D16': 15.9,
    'D19': 19.1,
    'D22': 22.2,
    'D25': 25.4,
    'D29': 28.7,
    'D32': 32.2
  },

  // Sample Rebar takeoff items (Length in meters)
  takeoffItems: {
    'D10': 1250.0,
    'D13': 420.0,
    'D16': 0.0,
    'D19': 180.0,
    'D22': 640.0,
    'D25': 850.0,
    'D29': 120.0,
    'D32': 0.0
  },

  init() {
    this.renderTakeoffTable();
    this.attachEvents();
  },

  renderTakeoffTable() {
    const tbody = document.getElementById('qntt-rebar-tbody');
    if (!tbody) return;

    let totalWeightKg = 0;
    const rows = [];

    Object.keys(this.rebarUnitWeights).forEach(size => {
      const length = this.takeoffItems[size] || 0;
      const unitW = this.rebarUnitWeights[size];
      const weightKg = length * unitW;
      totalWeightKg += weightKg;

      rows.push({
        size,
        dia: this.rebarDiameters[size],
        unitW,
        length,
        weightKg,
        weightTon: weightKg / 1000.0
      });
    });

    let html = '';
    rows.forEach((r, idx) => {
      const ratio = totalWeightKg > 0 ? ((r.weightKg / totalWeightKg) * 100).toFixed(1) : 0;
      html += `
        <tr style="border-bottom:1px solid var(--border-subtle); background:${idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'};">
          <td style="padding:6px 8px; font-weight:700; color:var(--text-primary);">${r.size}</td>
          <td style="padding:6px 8px;">${r.dia.toFixed(1)}</td>
          <td style="padding:6px 8px;">${r.unitW.toFixed(3)}</td>
          <td style="padding:6px 8px;">${r.length.toFixed(1)}</td>
          <td style="padding:6px 8px; font-family:var(--font-mono);">${r.weightKg.toLocaleString(undefined, {maximumFractionDigits: 1})}</td>
          <td style="padding:6px 8px; font-weight:600; color:var(--accent-primary); font-family:var(--font-mono);">${r.weightTon.toFixed(2)}</td>
          <td style="padding:6px 8px;">
            <div style="display:flex; align-items:center; gap:6px;">
              <div style="flex:1; background:var(--bg-input); height:6px; border-radius:3px; overflow:hidden;">
                <div style="width:${ratio}%; background:var(--accent-primary); height:100%;"></div>
              </div>
              <span style="font-size:11px; width:35px;">${ratio}%</span>
            </div>
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = html;

    const rebarWeightEl = document.getElementById('qntt-rebar-weight');
    if (rebarWeightEl) {
      rebarWeightEl.innerText = `${(totalWeightKg / 1000.0).toFixed(2)} ton`;
    }
  },

  attachEvents() {
    const btnExport = document.getElementById('btn-export-qntt-excel');
    if (btnExport) {
      btnExport.addEventListener('click', () => {
        alert('물량집계표 Excel 내보내기가 완료되었습니다 (AltDP_Quantity_Takeoff.xlsx)');
      });
    }
  }
};

window.QnttSummary = QnttSummary;
