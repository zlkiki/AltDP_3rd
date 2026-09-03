// web/js/report/redcr/sheetFormulas.js
// DesignPad — Formula/calculation step helpers for A4 HTML sheets
// Zero-Build Vanilla JavaScript & UMD support.

(function () {
    const FORMULA_CSS = `
.calc-block { margin:8px 0 12px; font-family: Consolas,'Courier New',monospace; font-size:10.5pt; }
.calc-title { font-weight:700; color:#1a3a5c; margin-bottom:4px; font-family: Arial,sans-serif; font-size:11pt; }
.calc-step { padding:1px 0; }
.calc-formula { color:#333; }
.calc-sub    { color:#555; padding-left:16px; }
.calc-result { color:#1a5c2a; font-weight:700; padding-left:16px; }
.calc-note   { color:#888; font-size:9.5pt; font-style:italic; padding-left:16px; }
.chk-table { border-collapse:collapse; width:100%; margin:6px 0; font-size:10.5pt; }
.chk-table th { background:#d8e4f0; padding:4px 8px; text-align:left; border:1px solid #bbb; font-size:10pt; }
.chk-table td { padding:4px 8px; border:1px solid #ccc; }
.chk-pass { color:#1a7a4a; font-weight:700; }
.chk-fail { color:#cc2222; font-weight:700; }
.inp-table { border-collapse:collapse; margin:4px 0; font-size:10.5pt; }
.inp-table td { padding:3px 12px 3px 0; }
.inp-label { color:#444; font-weight:600; }
.inp-val   { font-family:Consolas,'Courier New',monospace; color:#222; }
.inp-unit  { color:#888; font-size:9.5pt; }
.warn-box { background:#fff8e1; border-left:3px solid #f9a825; padding:4px 8px; margin:4px 0; font-size:10pt; }
.note-box { background:#e8f4fd; border-left:3px solid #1976d2; padding:4px 8px; margin:4px 0; font-size:10pt; }
`;

    /** HTML-escape for safe injection of user strings */
    function esc(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    /**
     * Returns an H2-style section header.
     * e.g. sectionHeader('3.2', 'Negative Flexure Check', 'KDS 14 20 20, §4.1.2')
     */
    function sectionHeader(n, title, kds) {
        const kdsPart = kds ? `  <span style="font-weight:400;font-size:10.5pt;color:#555">(${esc(kds)})</span>` : '';
        return `<h2>${esc(n)}&nbsp; ${esc(title)}${kdsPart}</h2>\n`;
    }

    /**
     * Single row: label ... value unit
     */
    function inputRow(label, value, unit) {
        const valStr = typeof value === 'number' ? n(value, 4) : esc(String(value));
        const unitStr = unit ? `<td class="inp-unit">${esc(unit)}</td>` : '<td></td>';
        return `<tr>
  <td class="inp-label">${esc(label)}</td>
  <td class="inp-val">${valStr}</td>
  ${unitStr}
</tr>`;
    }

    /**
     * Wraps multiple inputRow calls into a compact display block with a title.
     */
    function inputBlock(title, rows) {
        const rowsHtml = rows.map(r => inputRow(r.label, r.value, r.unit)).join('\n');
        return `<div class="calc-block">
<div class="calc-title">${esc(title)}</div>
<table class="inp-table">
${rowsHtml}
</table>
</div>\n`;
    }

    /**
     * Single calculation step with formula / substitution / result / optional note.
     */
    function calcStep(p) {
        const noteHtml = p.note
            ? `\n  <div class="calc-note">${p.note}</div>`
            : '';
        const subHtml = p.substitution
            ? `\n  <div class="calc-sub">${p.substitution}</div>`
            : '';
        return `<div class="calc-step">
  <div class="calc-formula">${p.formula}</div>${subHtml}
  <div class="calc-result">${p.result}</div>${noteHtml}
</div>`;
    }

    /**
     * Titled block wrapping multiple calcStep calls OR pre-rendered HTML strings.
     */
    function calcBlock(title, steps, kds) {
        const stepsHtml = steps.map(s => typeof s === 'string' ? s : calcStep(s)).join('\n');
        const kdsPart = kds ? `  <span style="font-weight:400;font-size:9.5pt;color:#888">(${esc(kds)})</span>` : '';
        return `<div class="calc-block">
<div class="calc-title">${esc(title)}${kdsPart}</div>
${stepsHtml}
</div>\n`;
    }

    /**
     * Single TR row for check results table.
     */
    function checkRow(p) {
        const passClass = p.pass ? 'chk-pass' : 'chk-fail';
        const passText = p.pass ? 'PASS ✓' : 'FAIL ✗';
        const dcStr = typeof p.dc === 'number' ? p.dc.toFixed(3) : esc(String(p.dc || '0.000'));
        const noteCell = p.note ? esc(p.note) : '';
        return `<tr>
  <td>${esc(p.label)}</td>
  <td><span style="font-family:Consolas,'Courier New',monospace">${p.formula || ''}</span></td>
  <td style="text-align:right">${n(p.demand, 2)}</td>
  <td style="text-align:right">${n(p.capacity, 2)}</td>
  <td>${esc(p.unit || '')}</td>
  <td style="text-align:right">${dcStr}</td>
  <td class="${passClass}">${passText}</td>
  ${noteCell ? `<td style="font-size:9pt;color:#888">${noteCell}</td>` : '<td></td>'}
</tr>`;
    }

    /**
     * Full check results table with header + all check rows + overall verdict.
     */
    function checkTable(title, rows) {
        const allPass = rows.every(r => r.pass);
        const verdictClass = allPass ? 'chk-pass' : 'chk-fail';
        const verdictText = allPass ? 'All checks PASS ✓' : 'Some checks FAIL ✗';
        const rowsHtml = rows.map(r => checkRow(r)).join('\n');
        return `<div class="calc-block">
<div class="calc-title">${esc(title)}</div>
<table class="chk-table">
<thead>
<tr>
  <th>Check Item</th>
  <th>Formula</th>
  <th style="text-align:right">Demand</th>
  <th style="text-align:right">Capacity</th>
  <th>Unit</th>
  <th style="text-align:right">D/C</th>
  <th>Result</th>
  <th>Note</th>
</tr>
</thead>
<tbody>
${rowsHtml}
</tbody>
</table>
<div style="text-align:right;margin-top:4px;font-size:11pt">
  <span class="${verdictClass}">${verdictText}</span>
</div>
</div>\n`;
    }

    /** Yellow warning box */
    function warnBox(msg) {
        return `<div class="warn-box">&#9888; ${esc(msg)}</div>\n`;
    }

    /** Blue note/info box */
    function noteBox(msg) {
        return `<div class="note-box">&#9432; ${esc(msg)}</div>\n`;
    }

    /** Format a number with comma thousands separator */
    function n(value, digits = 2, unit) {
        if (!Number.isFinite(value))
            return '—';
        const formatted = value.toLocaleString('en-US', {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        });
        return unit ? `${formatted} ${unit}` : formatted;
    }

    /** Light formula formatting */
    function fmtFormula(latex) {
        return `<span class="calc-formula">${latex}</span>`;
    }

    /**
     * Converts backend variable keys into readable KDS engineering symbols.
     */
    function formatSymbol(key) {
        if (!key) return '';
        let sym = key.replace(/_(kNm|kN|MPa|mm2|mm4|cm2|cm4|kPa|mm|m|percent|ratio)$/i, '');
        
        const symbolMap = {
            'phi_Mn': 'φMn', 'phiMn': 'φMn', 'Mn': 'Mn', 'Mu': 'Mu', 'Mu_face': 'Mu,face',
            'phi_Vn': 'φVn', 'phiVn': 'φVn', 'phi_Vc': 'φVc', 'phiVc': 'φVc', 'phi_Vs': 'φVs', 'phiVs': 'φVs',
            'Vc': 'Vc', 'Vs': 'Vs', 'Vu': 'Vu',
            'phi_Pn': 'φPn', 'phiPn': 'φPn', 'phi_Pn_max': 'φPn,max', 'Pn': 'Pn', 'Pu': 'Pu',
            'fck': 'fck', 'fy': 'fy', 'fys': 'fys', 'fyt': 'fyt', 'E': 'E', 'Es': 'Es', 'Ec': 'Ec',
            'beta1': 'β1', 'eta': 'η', 'lambda': 'λ', 'ecu': 'εcu', 'eps_cu': 'εcu', 'eps_t': 'εt',
            'rho': 'ρ', 'rho_min': 'ρmin', 'rho_max': 'ρmax', 'rho_v': 'ρv', 'rho_h': 'ρh', 'rho_percent': 'ρ (%)',
            'As': 'As', 'As_prov': 'As,prov', 'As_req': 'As,req', 'As_min': 'As,min', 'Av': 'Av',
            'q_max': 'qmax', 'q_min': 'qmin', 'q_avg': 'qavg', 'qa': 'qa',
            'dcr': 'DCR', 'dcr_flex': 'DCR (Flexure)', 'dcr_shear': 'DCR (Shear)',
            'dcr_soil': 'DCR (Soil Bearing)', 'dcr_punch': 'DCR (Punching)', 'dcr_1way': 'DCR (1-way Shear)',
            'governing_dcr': 'Governing DCR', 'max_dcr': 'Max DCR',
            'Lb': 'Lb', 'Lp': 'Lp', 'Lr': 'Lr', 'Cb': 'Cb',
            'Zx': 'Zx', 'Zy': 'Zy', 'Sx': 'Sx', 'Sy': 'Sy', 'Ix': 'Ix', 'Iy': 'Iy', 'Ag': 'Ag', 'Aw': 'Aw',
            'bo': 'bo', 'c': 'c', 'a': 'a', 'd': 'd'
        };

        if (symbolMap[sym]) return symbolMap[sym];
        if (symbolMap[key]) return symbolMap[key];

        return sym.replace(/_/g, ' ');
    }

    /**
     * Extracts value and engineering unit from a key-value pair.
     */
    function formatValueAndUnit(key, val) {
        if (val === null || val === undefined) return { valueStr: '—', unitStr: '' };
        
        let unit = '';
        let qType = null;
        const lk = key.toLowerCase();
        if (lk.endsWith('_knm') || lk.endsWith('knm')) { unit = 'kN·m'; qType = 'moment'; }
        else if (lk.endsWith('_kn') || lk.endsWith('kn')) { unit = 'kN'; qType = 'force'; }
        else if (lk.endsWith('_mpa') || lk.endsWith('mpa')) { unit = 'MPa'; qType = 'stress'; }
        else if (lk.endsWith('_kpa') || lk.endsWith('kpa')) { unit = 'kN/m²'; qType = 'areaLoad'; }
        else if (lk.endsWith('_mm2') || lk.endsWith('mm2')) { unit = 'mm²'; qType = 'area'; }
        else if (lk.endsWith('_mm4') || lk.endsWith('mm4')) { unit = 'mm⁴'; }
        else if (lk.endsWith('_cm2') || lk.endsWith('cm2')) { unit = 'cm²'; }
        else if (lk.endsWith('_cm4') || lk.endsWith('cm4')) { unit = 'cm⁴'; }
        else if (lk.endsWith('_mm') || lk.endsWith('mm')) { unit = 'mm'; qType = 'length'; }
        else if (lk.endsWith('_m') || lk.endsWith('m')) { unit = 'm'; qType = 'length_m'; }
        else if (lk.endsWith('_deg') || lk.endsWith('deg')) { unit = '°'; }
        else if (lk.endsWith('_percent') || lk.endsWith('percent')) { unit = '%'; }
        else if (lk.includes('dcr') || lk.includes('ratio')) { unit = ''; }

        let convertedVal = val;
        if (typeof window !== 'undefined' && window.UnitManager && qType && typeof val === 'number') {
            convertedVal = window.UnitManager.fromCanonical(val, qType);
            unit = window.UnitManager.getUnitString(qType);
        }

        let valueStr = '';
        if (typeof convertedVal === 'number') {
            if (Number.isInteger(convertedVal)) {
                valueStr = String(convertedVal);
            } else if (Math.abs(convertedVal) >= 1000) {
                valueStr = n(convertedVal, 1);
            } else if (Math.abs(convertedVal) >= 10) {
                valueStr = n(convertedVal, 2);
            } else if (Math.abs(convertedVal) >= 0.001) {
                valueStr = n(convertedVal, 3);
            } else if (convertedVal === 0) {
                valueStr = '0.0';
            } else {
                valueStr = convertedVal.toExponential(4);
            }
        } else if (typeof convertedVal === 'boolean') {
            valueStr = convertedVal ? 'PASS (OK)' : 'FAIL (NG)';
        } else if (typeof convertedVal === 'object') {
            valueStr = JSON.stringify(convertedVal);
        } else {
            valueStr = esc(String(convertedVal));
        }

        return { valueStr, unitStr: unit };
    }

    /**
     * Renders an Array of objects or a nested Dictionary as a clean HTML data table.
     */
    function dataTable(title, data, kds) {
        if (!data) return '';
        let rows = [];
        if (Array.isArray(data)) {
            rows = data;
        } else if (typeof data === 'object') {
            rows = Object.keys(data).map(k => {
                const item = data[k];
                return typeof item === 'object' && item !== null ? { id: k, ...item } : { name: k, value: item };
            });
        }

        if (rows.length === 0) return '';

        const cols = [];
        rows.forEach(r => {
            if (typeof r === 'object' && r !== null) {
                Object.keys(r).forEach(k => {
                    if (!cols.includes(k)) cols.push(k);
                });
            }
        });

        if (cols.length === 0) return '';

        const ths = cols.map(c => `<th>${esc(formatSymbol(c))}</th>`).join('');
        const trs = rows.map(r => {
            const tds = cols.map(c => {
                const v = r[c];
                if (v === null || v === undefined) return '<td style="text-align:center">—</td>';
                if (typeof v === 'number') {
                    const numStr = Number.isInteger(v) ? String(v) : (Math.abs(v) >= 100 ? v.toFixed(1) : v.toFixed(2));
                    return `<td style="text-align:right">${numStr}</td>`;
                }
                if (typeof v === 'boolean') {
                    return `<td style="text-align:center;font-weight:bold" class="${v ? 'chk-pass' : 'chk-fail'}">${v ? 'PASS' : 'FAIL'}</td>`;
                }
                if (typeof v === 'object') {
                    return `<td>${esc(JSON.stringify(v))}</td>`;
                }
                return `<td>${esc(String(v))}</td>`;
            }).join('');
            return `<tr>${tds}</tr>`;
        }).join('\n');

        const kdsPart = kds ? ` <span style="font-weight:400;font-size:9.5pt;color:#888">(${esc(kds)})</span>` : '';

        return `<div class="calc-block">
  <div class="calc-title">${esc(title)}${kdsPart}</div>
  <table class="chk-table rpt-data-table">
    <thead><tr>${ths}</tr></thead>
    <tbody>${trs}</tbody>
  </table>
</div>\n`;
    }

    const RedcrFormulas = {
        FORMULA_CSS, esc, sectionHeader, inputRow, inputBlock,
        calcStep, calcBlock, checkRow, checkTable, warnBox, noteBox, n, fmtFormula,
        formatSymbol, formatValueAndUnit, dataTable
    };

    if (typeof window !== 'undefined') {
        window.RedcrFormulas = RedcrFormulas;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = RedcrFormulas;
    }
})();
