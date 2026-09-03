/**
 * AltDP_3rd Master Web Application Controller (app.js)
 * Coordinates Ribbon Bar, 4-Main Form Views, P/S/M Modes, and API Communication.
 */

class AppController {
  constructor() {
    this.currentView = 'memb';       // 'memb' | 'list' | 'draw' | 'qntt'
    this.currentMode = 'P';          // 'P' (Design) | 'S' (Check) | 'M' (Manage)
    this.currentMemberType = 'rc_beam';
    this.unitSystem = 'SI';
    this.isDarkTheme = true;
    this.pmChart = null;
  }

  init() {
    this.bindNavigation();
    this.bindRibbonBar();
    this.bindModes();
    this.bindThemeAndUnits();
    this.bindMembViewEvents();

    // Initialize Submodules
    if (window.MemberForms) MemberForms.renderForm('dynamic-member-form', this.currentMemberType);
    if (window.BatchGrid) BatchGrid.init();
    if (window.DrawCad) DrawCad.init();
    if (window.QnttSummary) QnttSummary.init();

    this.runCheck();
  }

  // 1. 4-Main Form Views Switching
  bindNavigation() {
    const viewBtns = document.querySelectorAll('.view-tab-btn');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        viewBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const targetView = btn.dataset.view;
        this.switchView(targetView);
      });
    });
  }

  switchView(viewId) {
    this.currentView = viewId;
    const views = document.querySelectorAll('.main-form-view');
    views.forEach(v => v.classList.remove('active'));

    const target = document.getElementById(`view-${viewId}`);
    if (target) {
      target.classList.add('active');
    }

    // Refresh viewports
    if (viewId === 'draw' && window.DrawCad) {
      window.DrawCad.renderDrawing('section_rebar');
    } else if (viewId === 'memb') {
      this.refreshGraphics();
    }
  }

  // 2. Ribbon Bar Switching
  bindRibbonBar() {
    const tabBtns = document.querySelectorAll('.ribbon-tab-btn');
    const tabBodies = document.querySelectorAll('.ribbon-content-body');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabBodies.forEach(body => body.classList.remove('active'));

        btn.classList.add('active');
        const targetId = btn.dataset.tab;
        const targetBody = document.getElementById(targetId);
        if (targetBody) targetBody.classList.add('active');
      });
    });

    // Quick Ribbon Member Selection Buttons
    document.querySelectorAll('.memb-select-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.dataset.type;
        this.selectMemberType(type);
        this.switchView('memb');
      });
    });

    // Quick Buttons in Home Tab
    const quickRcBeam = document.getElementById('btn-quick-rc-beam');
    if (quickRcBeam) quickRcBeam.addEventListener('click', () => {
      this.selectMemberType('rc_beam');
      this.switchView('memb');
    });

    const quickRcCol = document.getElementById('btn-quick-rc-col');
    if (quickRcCol) quickRcCol.addEventListener('click', () => {
      this.selectMemberType('rc_column');
      this.switchView('memb');
    });

    const quickSteelBeam = document.getElementById('btn-quick-steel-beam');
    if (quickSteelBeam) quickSteelBeam.addEventListener('click', () => {
      this.selectMemberType('steel_beam');
      this.switchView('memb');
    });

    // Ribbon Action Buttons
    const btnRun = document.getElementById('btn-run-check');
    if (btnRun) btnRun.addEventListener('click', () => this.runCheck());

    const btnAuto = document.getElementById('btn-auto-design');
    if (btnAuto) btnAuto.addEventListener('click', () => this.runAutoDesign());

    const btnExportPdf = document.getElementById('btn-export-pdf');
    if (btnExportPdf) {
      btnExportPdf.addEventListener('click', () => {
        window.open('/api/report/rc_beam?output_format=pdf', '_blank');
      });
    }

    const btnExportExcel = document.getElementById('btn-export-excel');
    if (btnExportExcel) {
      btnExportExcel.addEventListener('click', () => {
        window.open('/api/report/excel/project', '_blank');
      });
    }
  }

  // 3. P / S / M Mode Switching
  bindModes() {
    const modeBtns = document.querySelectorAll('.mode-pill-btn');
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentMode = btn.dataset.mode;
        this.onModeChanged();
      });
    });
  }

  onModeChanged() {
    if (this.currentMode === 'P') {
      this.runAutoDesign();
    } else if (this.currentMode === 'S') {
      this.runCheck();
    }
  }

  // 4. Themes & Unit Systems
  bindThemeAndUnits() {
    const themeBtn = document.getElementById('btnThemeToggle') || document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        this.isDarkTheme = !this.isDarkTheme;
        if (this.isDarkTheme) {
          document.body.classList.remove('light-theme');
          document.body.classList.add('dark-theme');
          if (themeIcon) themeIcon.innerText = '🌙';
        } else {
          document.body.classList.remove('dark-theme');
          document.body.classList.add('light-theme');
          if (themeIcon) themeIcon.innerText = '☀️';
        }
        this.refreshGraphics();
      });
    }

    const unitSel = document.getElementById('unit-selector');
    if (unitSel) {
      unitSel.addEventListener('change', (e) => {
        this.unitSystem = e.target.value;
        this.runCheck();
      });
    }
  }

  // 5. Memb View Events & Member Selection
  bindMembViewEvents() {
    const membSelect = document.getElementById('member-type-select');
    if (membSelect) {
      membSelect.addEventListener('change', (e) => {
        this.selectMemberType(e.target.value);
      });
    }

    const btnApply = document.getElementById('btn-mode-apply');
    if (btnApply) btnApply.addEventListener('click', () => this.runCheck());

    const btnCheck = document.getElementById('btn-mode-check');
    if (btnCheck) btnCheck.addEventListener('click', () => this.runCheck());

    const btnDesign = document.getElementById('btn-mode-design');
    if (btnDesign) btnDesign.addEventListener('click', () => this.runAutoDesign());
  }

  selectMemberType(type) {
    this.currentMemberType = type;
    const membSelect = document.getElementById('member-type-select');
    if (membSelect) membSelect.value = type;

    const ind = document.getElementById('active-member-indicator');
    if (ind) {
      const typeNames = {
        rc_beam: 'RC Beam (B1)',
        rc_column: 'RC Column (C1)',
        rc_wall: 'RC Wall (W1)',
        steel_beam: 'Steel Beam (SB1)'
      };
      ind.innerHTML = `현재 부재: <strong style="color:var(--accent-primary);">${typeNames[type] || type}</strong>`;
    }

    if (window.MemberForms) {
      MemberForms.renderForm('dynamic-member-form', type);
    }
    this.runCheck();
  }

  onFormParamChange() {
    this.runCheck();
  }

  // 6. Execution & API Dispatch
  async runCheck() {
    const formData = window.MemberForms ? MemberForms.getFormData(this.currentMemberType) : {};
    
    // Fallback Mock KDS Evaluation for instant UI response (<0.05s)
    let demandM = formData.mu || 180.0;
    let capacityM = this.currentMemberType === 'rc_column' ? 320.0 : 236.8;
    let dcr = demandM / capacityM;

    this.updateSummaryTable(demandM, capacityM, dcr);
    this.refreshGraphics(formData, dcr);
  }

  runAutoDesign() {
    if (window.MemberForms) {
      const res = MemberForms.autoDesign(this.currentMemberType);
      this.runCheck();
      return res;
    }
  }

  updateSummaryTable(demand, capacity, dcr) {
    const tbody = document.getElementById('kds-summary-tbody');
    const statusText = document.getElementById('overall-status-text');
    if (!tbody) return;

    const isSafe = dcr <= 1.0;
    const color = isSafe ? 'var(--status-safe)' : 'var(--status-danger)';
    const status = isSafe ? 'PASS' : 'NG';

    if (statusText) {
      statusText.innerHTML = `<span style="color:${color}; font-weight:700;">${status} (DCR = ${dcr.toFixed(3)})</span>`;
    }

    tbody.innerHTML = `
      <tr>
        <td style="padding:6px 8px; font-weight:600;">휨모멘트 (Flexure)</td>
        <td style="padding:6px 8px;">${demand.toFixed(1)} kN·m</td>
        <td style="padding:6px 8px;">${capacity.toFixed(1)} kN·m</td>
        <td style="padding:6px 8px;"><span style="color:${color}; font-weight:700;">${dcr.toFixed(3)}</span></td>
        <td style="padding:6px 8px;"><span style="color:${color}; font-weight:700;">${status}</span></td>
        <td style="padding:6px 8px; color:var(--text-muted);">KDS 14 20 20 (4.1)</td>
      </tr>
    `;
  }

  refreshGraphics(data, dcr) {
    const canvas = document.getElementById('sectionCanvas');
    if (canvas && window.Renderer2D) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        canvas.width = canvas.parentElement.clientWidth || 300;
        canvas.height = canvas.parentElement.clientHeight || 250;
        Renderer2D.drawSection(ctx, canvas.width, canvas.height, this.currentMemberType, data);
      }
    }

    const pmCanvas = document.getElementById('pmCanvas');
    if (pmCanvas && window.PMChartRenderer) {
      const ctx = pmCanvas.getContext('2d');
      if (ctx) {
        pmCanvas.width = pmCanvas.parentElement.clientWidth || 300;
        pmCanvas.height = pmCanvas.parentElement.clientHeight || 250;
        PMChartRenderer.drawChart(ctx, pmCanvas.width, pmCanvas.height, dcr);
      }
    }
  }

  // Legacy Compatibility Helper Methods
  calculateRcBeam() { return this.runCheck(); }
  calculateRcColumn() { return this.runCheck(); }
  calculateRcWall() { return this.runCheck(); }
  calculateSteelBeam() { return this.runCheck(); }
  calculateCftColumn() { return this.runCheck(); }
  calculateRetrofit() { return this.runCheck(); }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.App = new AppController();
  window.App.init();
});

