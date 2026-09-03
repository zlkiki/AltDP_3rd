/**
 * AltDP_3rd Batch Grid Controller (ListView)
 * High-performance spreadsheet editor & batch DCR evaluation.
 */

const BatchGrid = {
  members: [
    { id: 'B1', story: '1F', type: 'RC Beam', section: '400x600', rebar: '4-D25', mu: 180, vu: 140, dcr: 0.76, status: 'OK' },
    { id: 'C1', story: '1F', type: 'RC Column', section: '600x600', rebar: '12-D25', mu: 240, vu: 90, dcr: 0.65, status: 'OK' },
    { id: 'W1', story: '1F', type: 'RC Wall', section: 'thk 200', rebar: 'D10@200', mu: 320, vu: 210, dcr: 0.82, status: 'OK' },
    { id: 'B2', story: '2F', type: 'RC Beam', section: '400x500', rebar: '4-D22', mu: 160, vu: 120, dcr: 0.88, status: 'OK' },
    { id: 'SB1', story: '2F', type: 'Steel Beam', section: 'H-400x200', rebar: 'Fy355', mu: 220, vu: 110, dcr: 0.72, status: 'OK' }
  ],

  init() {
    this.renderTable();
    this.attachEvents();
  },

  renderTable() {
    const tbody = document.getElementById('batch-tbody');
    if (!tbody) return;

    let html = '';
    let ngCount = 0;

    this.members.forEach((m, idx) => {
      const isNG = m.dcr > 1.0;
      if (isNG) ngCount++;
      const color = isNG ? 'var(--status-danger)' : (m.dcr > 0.9 ? 'var(--status-warning)' : 'var(--status-safe)');

      html += `
        <tr style="border-bottom:1px solid var(--border-subtle); background:${idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)'};">
          <td style="padding:6px 8px; text-align:center;"><input type="checkbox" class="batch-row-check" data-idx="${idx}"></td>
          <td style="padding:6px 8px; font-weight:600; color:var(--text-primary);">${m.id}</td>
          <td style="padding:6px 8px; color:var(--text-secondary);">${m.story}</td>
          <td style="padding:6px 8px;">${m.type}</td>
          <td style="padding:6px 8px; font-family:var(--font-mono);">${m.section}</td>
          <td style="padding:6px 8px; font-family:var(--font-mono);">${m.rebar}</td>
          <td style="padding:6px 8px;">${m.mu}</td>
          <td style="padding:6px 8px;">${m.vu}</td>
          <td style="padding:6px 8px; font-weight:700; color:${color};">${m.dcr.toFixed(2)}</td>
          <td style="padding:6px 8px;"><span style="color:${color}; font-weight:600;">${m.status}</span></td>
        </tr>
      `;
    });

    tbody.innerHTML = html;

    const totalEl = document.getElementById('batch-total-count');
    const ngEl = document.getElementById('batch-ng-count');
    const badgeEl = document.getElementById('list-count-badge');
    if (totalEl) totalEl.innerText = this.members.length;
    if (ngEl) ngEl.innerText = ngCount;
    if (badgeEl) badgeEl.innerText = this.members.length;
  },

  attachEvents() {
    const btnCheck = document.getElementById('btn-batch-check');
    if (btnCheck) {
      btnCheck.addEventListener('click', () => this.runAllBatch());
    }

    const btnAdd = document.getElementById('btn-batch-add-row');
    if (btnAdd) {
      btnAdd.addEventListener('click', () => {
        const newId = `M${this.members.length + 1}`;
        this.members.push({
          id: newId, story: '1F', type: 'RC Beam', section: '400x600', rebar: '4-D25', mu: 150, vu: 100, dcr: 0.60, status: 'OK'
        });
        this.renderTable();
      });
    }

    const btnDel = document.getElementById('btn-batch-delete-row');
    if (btnDel) {
      btnDel.addEventListener('click', () => {
        if (this.members.length > 1) {
          this.members.pop();
          this.renderTable();
        }
      });
    }
  },

  runAllBatch() {
    // Simulate high-speed batch evaluation
    this.members.forEach(m => {
      // Re-evaluate pseudo DCR
      const factor = (m.mu / 240.0) * (0.95 + Math.random() * 0.1);
      m.dcr = parseFloat(factor.toFixed(2));
      m.status = m.dcr <= 1.0 ? 'OK' : 'NG';
    });
    this.renderTable();
  }
};

window.BatchGrid = BatchGrid;
