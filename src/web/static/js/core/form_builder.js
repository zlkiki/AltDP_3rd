/**
 * AltDP_3rd 4-SubTab Dynamic Form Builder (form_builder.js)
 * Structures input parameters into 4 original tabs with real-time broadcasting
 */
class FormBuilder {
    constructor() {
        this.activeSubTab = 'section';
        this.debounceTimer = null;
    }

    /**
     * Build 4-subtab layout into form container
     * @param {HTMLElement} formEl 
     * @param {Object} schema 
     * @param {Object} currentValues 
     * @param {Function} onChangeCallback 
     */
    build(formEl, schema, currentValues = {}, onChangeCallback) {
        if (!formEl) return;
        formEl.innerHTML = '';

        // 1. Sub-tab headers
        const tabs = [
            { id: 'section', label: '단면 및 재료', icon: '📐' },
            { id: 'rebar', label: '철근 배근', icon: '▦' },
            { id: 'load', label: '하중 및 부재력', icon: '⚖️' },
            { id: 'option', label: '검토 옵션', icon: '⚙️' }
        ];

        let tabHeadersHtml = '<div class="sub-tab-bar">';
        tabs.forEach(t => {
            tabHeadersHtml += `
                <button type="button" class="sub-tab-btn ${t.id === this.activeSubTab ? 'active' : ''}" data-tab="${t.id}">
                    ${t.icon} ${t.label}
                </button>
            `;
        });
        tabHeadersHtml += '</div>';

        // 2. Tab Contents Container
        let tabContentsHtml = '<div class="sub-tab-contents">';
        tabs.forEach(t => {
            tabContentsHtml += `<div class="sub-tab-pane ${t.id === this.activeSubTab ? 'active' : ''}" id="pane-${t.id}"></div>`;
        });
        tabContentsHtml += '</div>';

        formEl.innerHTML = tabHeadersHtml + tabContentsHtml;

        // Sub-tab button events
        formEl.querySelectorAll('.sub-tab-btn').forEach(btn => {
            btn.onclick = () => {
                const targetTab = btn.dataset.tab;
                this.activeSubTab = targetTab;
                formEl.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === targetTab));
                formEl.querySelectorAll('.sub-tab-pane').forEach(p => p.classList.toggle('active', p.id === `pane-${targetTab}`));
            };
        });

        // 3. Populate Fields
        this._populateFields(formEl, schema, currentValues, onChangeCallback);
    }

    _populateFields(formEl, schema, currentValues, onChangeCallback) {
        const fields = schema?.fields || [];

        fields.forEach(f => {
            const tabId = f.tab || 'section';
            const pane = formEl.querySelector(`#pane-${tabId}`);
            if (!pane) return;

            const val = currentValues[f.key] ?? f.default ?? '';
            const row = document.createElement('div');
            row.className = 'form-group-row';

            let inputHtml = '';
            if (f.type === 'select') {
                const opts = (f.options || []).map(o => `<option value="${o.value}" ${o.value == val ? 'selected' : ''}>${o.label}</option>`).join('');
                inputHtml = `<select id="input-${f.key}" class="form-input">${opts}</select>`;
            } else {
                inputHtml = `<input type="${f.type || 'number'}" id="input-${f.key}" value="${val}" class="form-input">`;
            }

            const dialogBtn = f.hasDialog ? `<button type="button" class="btn-more-dlg" id="btn-dlg-${f.key}" title="상세 대화창 열기">...</button>` : '';
            const unitTag = f.unit ? `<span class="unit-tag">${f.unit}</span>` : '';

            row.innerHTML = `
                <label for="input-${f.key}">${f.label}:</label>
                <div class="input-control-wrap">
                    ${inputHtml}
                    ${dialogBtn}
                    ${unitTag}
                </div>
            `;
            pane.appendChild(row);

            // Change event with 50ms debounce
            const inputEl = row.querySelector(`#input-${f.key}`);
            if (inputEl) {
                inputEl.addEventListener('input', () => {
                    clearTimeout(this.debounceTimer);
                    this.debounceTimer = setTimeout(() => {
                        const parsedVal = inputEl.type === 'number' ? parseFloat(inputEl.value) : inputEl.value;
                        if (onChangeCallback) onChangeCallback(f.key, parsedVal);
                        if (window.EventBus && window.APP_EVENTS) {
                            window.EventBus.emit(window.APP_EVENTS.PARAM_CHANGED, { key: f.key, value: parsedVal });
                        }
                    }, 50);
                });
            }

            // Sub-dialog click
            if (f.hasDialog && f.onOpenDialog) {
                const btnDlg = row.querySelector(`#btn-dlg-${f.key}`);
                if (btnDlg) {
                    btnDlg.onclick = () => f.onOpenDialog(currentValues, (newVals) => {
                        Object.assign(currentValues, newVals);
                        if (onChangeCallback) onChangeCallback(null, currentValues);
                    });
                }
            }
        });
    }
}

window.FormBuilder = new FormBuilder();
