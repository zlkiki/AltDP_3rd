// web/js/components/form_generator.js
/**
 * Schema-driven Dynamic Form Generator (Ultra-slim Orchestrator)
 * - Delegates Combobox, Strict Dropdowns & AutoFill to FormCombobox (form_combobox.js)
 * - 4-Pillar Section Grouping: Geometry, Materials, Reinforcement, Design Forces
 * - Action Toolbar: [⚡ 검토], [✨ 설계]
 * - Bidirectional Canonical SI <-> Display Unit conversion
 */

window.FormGenerator = {
    _currentSchema: null,
    _currentModuleKey: '',

    init() {
        if (window.FormCombobox) {
            window.FormCombobox.init();
        }
    },

    renderForm(schema, formElement, onValueChange, onCheckClick, onDesignClick, moduleKey = '', onApplyClick = null) {
        this.init();
        if (!formElement) return;
        formElement.innerHTML = '';
        this._currentSchema = schema || {};
        this._currentModuleKey = moduleKey || (window.App && window.App.currentModule) || '';
        const properties = this._currentSchema.properties || {};

        // 1. Action Toolbar: [💾 적용], [⚡ 검토], [✨ 설계] (최상단 고정 배치)
        const actionBar = document.createElement('div');
        actionBar.className = 'input-action-bar';
        actionBar.innerHTML = `
            <button type="button" class="btn-apply-action" id="btn-run-apply" title="수정된 입력값을 메모리에 저장하고 캔버스를 즉시 갱신합니다">💾 적용 (Apply)</button>
            <button type="button" class="btn-check-action" id="btn-run-check" title="현재 입력 조건으로 KDS 기준 검토 실행">⚡ 검토 (Check)</button>
            <button type="button" class="btn-design-action" id="btn-run-design" title="모든 검토 항목을 만족하도록 배근/단면 자동 최적화">✨ 설계 (Design)</button>
        `;

        const btnApply = actionBar.querySelector('#btn-run-apply');
        const btnCheck = actionBar.querySelector('#btn-run-check');
        const btnDesign = actionBar.querySelector('#btn-run-design');

        if (btnApply && onApplyClick) {
            btnApply.addEventListener('click', () => onApplyClick());
        }
        if (btnCheck && onCheckClick) {
            btnCheck.addEventListener('click', () => onCheckClick());
        }
        if (btnDesign && onDesignClick) {
            btnDesign.addEventListener('click', () => onDesignClick());
        }

        formElement.appendChild(actionBar);

        // 2. Group properties into re-DCR 4 Pillars
        const groups = {
            geom: { title: '1. 단면 제원 (Section Geometry)', icon: '📐', fields: [] },
            mat:  { title: '2. 재료 강도 (Materials)', icon: '🧱', fields: [] },
            reinf:{ title: '3. 배근 및 상세 (Reinforcement & Details)', icon: '🔩', fields: [] },
            force:{ title: '4. 설계 하중 및 단면력 (Design Forces)', icon: '⚡', fields: [] }
        };

        Object.keys(properties).forEach(fieldName => {
            const pillar = this.categorizeField(fieldName);
            groups[pillar].fields.push(fieldName);
        });

        // 3. Render Section Cards
        Object.keys(groups).forEach(pillarKey => {
            const grp = groups[pillarKey];
            if (grp.fields.length === 0) return;

            const card = document.createElement('div');
            card.className = 'form-section-card';

            const header = document.createElement('div');
            header.className = 'form-section-header';
            header.innerHTML = `
                <span class="form-section-icon">${grp.icon}</span>
                <span class="form-section-title">${grp.title}</span>
            `;
            card.appendChild(header);

            const body = document.createElement('div');
            body.className = 'form-section-body';

            grp.fields.forEach(fieldName => {
                const prop = properties[fieldName];
                const fieldGroup = this.createFieldElement(fieldName, prop, formElement, onValueChange);
                body.appendChild(fieldGroup);
            });

            card.appendChild(body);
            formElement.appendChild(card);
        });
    },

    createFieldElement(fieldName, prop, formElement, onValueChange) {
        const group = document.createElement('div');
        group.className = 'form-field-group';

        const qtyType = this.getFieldQuantityType(fieldName);
        const unitStr = qtyType && window.UnitManager ? window.UnitManager.getUnitString(qtyType) : '';

        const label = document.createElement('label');
        label.htmlFor = `field_${fieldName}`;
        const cleanDesc = (prop.description || fieldName).replace(/\s*\([^)]*\)\s*$/, '').trim();

        label.innerHTML = `
            <span class="field-title">${cleanDesc}</span>
            ${unitStr ? `<span class="inp-unit-badge" data-field="${fieldName}" data-qty="${qtyType}">[${unitStr}]</span>` : ''}
        `;
        label.title = `${prop.description || fieldName} (${fieldName})`;
        group.appendChild(label);

        const fieldType = prop.type;
        let defaultValue = prop.default !== undefined ? prop.default : '';

        // Format default value if canonical numeric
        if (defaultValue !== '' && qtyType && window.UnitManager && typeof defaultValue === 'number') {
            defaultValue = window.UnitManager.fromCanonical(defaultValue, qtyType);
            if (typeof defaultValue === 'number') {
                const sys = window.UnitManager.getCurrentSystem();
                const digits = sys.digits?.[qtyType] ?? 2;
                defaultValue = Number(defaultValue.toFixed(digits));
            }
        }

        // 1. Strict Enum Dropdown Check
        if (window.FormCombobox) {
            const strictConfig = window.FormCombobox.getStrictDropdownConfig(fieldName, defaultValue, this._currentModuleKey);
            if (strictConfig) {
                const selectEl = window.FormCombobox.createStrictDropdown(fieldName, defaultValue, strictConfig, formElement, onValueChange);
                group.appendChild(selectEl);
                return group;
            }

            // 2. KS Standard Combobox (Rebar, Bolt, Section, Material)
            const comboConfig = window.FormCombobox.getComboboxConfig(fieldName, defaultValue, this._currentModuleKey, formElement);
            if (comboConfig) {
                const comboEl = window.FormCombobox.createCombobox(fieldName, defaultValue, comboConfig, formElement, onValueChange);
                group.appendChild(comboEl);
                return group;
            }
        }

        // 3. Boolean Checkbox
        if (fieldType === 'boolean') {
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.id = `field_${fieldName}`;
            input.name = fieldName;
            input.checked = Boolean(defaultValue);
            input.addEventListener('change', () => onValueChange(fieldName));
            group.appendChild(input);
            return group;
        }

        // 4. General Numeric or Text Input with Min=0 Protection
        const input = document.createElement('input');
        input.type = fieldType === 'integer' || fieldType === 'number' ? 'number' : 'text';
        input.id = `field_${fieldName}`;
        input.name = fieldName;
        input.value = defaultValue;

        if (fieldType === 'integer' || fieldType === 'number') {
            input.min = '0';
            if (fieldType === 'integer') input.step = '1';
            else input.step = 'any';
        }

        if (unitStr) {
            input.placeholder = `${cleanDesc} (${unitStr})`;
        }
        input.addEventListener('input', () => onValueChange(fieldName));
        group.appendChild(input);

        return group;
    },

    categorizeField(fieldName) {
        const lk = fieldName.toLowerCase();
        // 1. Geometry (Dimensions, Spans, Thickness, Width, Height)
        if (['b', 'bw', 'h', 'h1', 'b1', 'd', 'tw', 'tf', 'cover', 'cx', 'cy', 't_steel', 'slab_thick', 'pile_dia', 'pile_cap_dia', 'edge_dist', 'r', 'b_f', 'h_f', 'bf', 'b_top', 'h_top', 'col_b', 'col_h', 'col_d', 'col_bf', 'lw', 'thickness', 't', 'cc', 'c_c', 'span', 'span_x', 'span_y', 'span_horiz', 'l', 'lx', 'ly', 'lb', 'l_clear', 'ln', 'height_story', 'h_story', 'len', 'tread_r', 'tread_t', 'width', 'depth', 'flange_w', 'flange_t', 'web_t', 'd_eff', 'open_size', 'open_width', 'clear_spacing', 'wheel_spacing', 'section_name', 'shape', 'shape_type', 'section_type'].includes(lk)) {
            return 'geom';
        }
        // 2. Materials (Concrete fck, Steel Fy, Rebar fy, E)
        if (['fck', 'fci', 'fy', 'fys', 'fyt', 'fy_steel', 'fy_rebar', 'fu', 'fyk', 'fpu', 'fps', 'e', 'es', 'ec', 'f_ck', 'fck_c', 'fy_h', 'fy_v', 'fy_main', 'fy_sub', 'steel_grade', 'material', 'grade', 'steel_type', 'rebar_grade', 'plate_grade', 'beam_grade', 'qa_soil', 'fb', 'ft', 'fv', 'f_y', 'f_u', 'mat', 'anchor_grade', 'bolt_grade'].includes(lk)) {
            return 'mat';
        }
        // 3. Reinforcement & Details
        if (lk.includes('dia') || lk.includes('bar') || lk.includes('rebar') || lk.includes('stirrup') || lk.includes('bolt') || lk.includes('layer') || ['top_num', 'bot_num', 'stirrup_legs', 'legs', 'db', 'dt', 'main_num', 'tie_num', 'anchor_num', 'nx', 'ny', 'side_num', 'vert_curtains', 'stirrup_spacing', 'bar_spacing', 'rebar_spacing', 'top_rebar_num', 'bot_rebar_num', 'diag_rebar_num', 'num_bolts', 'num_shear_planes', 'bolt_num', 'num_tension_bolts'].includes(lk)) {
            return 'reinf';
        }
        // 4. Design Forces & Loads
        if (['mu', 'vu', 'pu', 'tu', 'mux', 'muy', 'muz', 'mx_serv', 'my_serv', 'm_serv', 'p_serv', 'p1', 'p2', 'p_allow', 'v_u', 'p_u', 'axial_force', 'p_serv_tot', 'f_tension', 'f_shear', 't_u', 'wheel_load', 'pe_eff', 'qa', 'll', 'dl', 'dead_load_finish', 'finish_load', 'live_load', 'qsurf', 'qsurface', 'soil_pressure', 'w_dead', 'w_live', 'w_total', 'load'].includes(lk)) {
            return 'force';
        }
        return 'geom';
    },

    getFormData(formElement) {
        const formData = {};
        if (!formElement) return formData;
        const inputs = formElement.querySelectorAll('input, select');
        const schemaProps = this._currentSchema?.properties || {};

        inputs.forEach(input => {
            const name = input.name;
            if (!name) return;

            const prop = schemaProps[name] || {};
            const expectedType = prop.type || 'number';

            if (input.type === 'checkbox') {
                formData[name] = input.checked;
            } else if (input.dataset && input.dataset.actualValue !== undefined) {
                // Strict dropdown value priority
                formData[name] = input.dataset.actualValue;
            } else if (expectedType === 'string') {
                formData[name] = String(input.value).trim();
            } else if (expectedType === 'integer') {
                let rawStr = String(input.value).trim().toUpperCase();
                if (rawStr.startsWith('D') || rawStr.startsWith('M')) {
                    rawStr = rawStr.substring(1);
                }
                const num = parseInt(rawStr, 10);
                const val = isNaN(num) ? 0 : num;
                formData[name] = Math.max(0, val); // Non-negative constraint
            } else {
                // Number / Float
                let rawStr = String(input.value).trim().toUpperCase();
                if (rawStr.startsWith('D') || rawStr.startsWith('M')) {
                    rawStr = rawStr.substring(1);
                }
                const rawVal = parseFloat(rawStr);
                const numVal = isNaN(rawVal) ? 0.0 : Math.max(0.0, rawVal); // Non-negative constraint
                const qtyType = this.getFieldQuantityType(name);
                if (qtyType && window.UnitManager) {
                    formData[name] = window.UnitManager.toCanonical(numVal, qtyType);
                } else {
                    formData[name] = numVal;
                }
            }
        });
        return formData;
    },

    setFormData(formElement, data = {}) {
        if (!formElement || !data) return;

        Object.keys(data).forEach(key => {
            const field = formElement.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = Boolean(data[key]);
                } else if (field.tagName === 'SELECT') {
                    field.value = String(data[key]);
                } else {
                    let val = data[key];
                    const lk = key.toLowerCase();
                    const qtyType = this.getFieldQuantityType(key);

                    // Check if field is strict dropdown
                    if (window.FormCombobox) {
                        const strictCfg = window.FormCombobox.getStrictDropdownConfig(key, val, this._currentModuleKey);
                        if (strictCfg) {
                            const opt = strictCfg.options.find(o => String(o.value).toLowerCase() === String(val).toLowerCase());
                            field.value = opt ? opt.label : val;
                            field.dataset.actualValue = opt ? opt.value : val;
                            return;
                        }
                    }

                    // 1. Bolt Diameter M16~M36 formatting
                    if (['bolt_dia', 'anchor_dia', 'd_bolt', 'db_bolt'].includes(lk) && typeof val === 'number') {
                        field.value = `M${val}`;
                        return;
                    }

                    // 2. Rebar Diameter D10~D57 formatting (exclude spacing, count, pitch)
                    if (!lk.includes('spacing') && !lk.includes('pitch') && !lk.includes('간격') && !lk.includes('num') && !lk.includes('count') && (lk.includes('dia') || ['db', 'dt'].includes(lk)) && typeof val === 'number') {
                        field.value = `D${val}`;
                        return;
                    }

                    // 3. Dimensional Unit Conversion Display
                    if (qtyType && typeof val === 'number' && window.UnitManager) {
                        const displayVal = window.UnitManager.fromCanonical(val, qtyType);
                        const sys = window.UnitManager.getCurrentSystem();
                        const digits = sys.digits?.[qtyType] ?? 2;
                        field.value = Number(displayVal.toFixed(digits));
                    } else {
                        field.value = val !== undefined && val !== null ? val : '';
                    }
                }
            }
        });
    },

    rebaseFormInputs(formElement, prevSys, nextSys) {
        if (!formElement || !window.UnitManager) return;

        // 1. Update Unit Badges on Labels
        const badges = formElement.querySelectorAll('.inp-unit-badge');
        badges.forEach(badge => {
            const qty = badge.dataset.qty;
            if (qty) {
                const newUnitStr = window.UnitManager.getUnitString(qty);
                badge.innerText = `[${newUnitStr}]`;
            }
        });

        // 2. Rebase Input Values from Canonical SSOT (ProjectStore) to avoid floating-point drift
        if (window.ProjectStore) {
            const modKey = window.ProjectStore.getState().activeContext.moduleKey;
            const activeMember = window.ProjectStore.getActiveMember(modKey);
            if (activeMember && activeMember.inputs) {
                // Set form data directly from Canonical SSOT inputs with active unit conversion
                this.setFormData(formElement, activeMember.inputs);
                return;
            }
        }

        // Fallback if no store
        const inputs = formElement.querySelectorAll('input[type="number"], input[type="text"]');
        inputs.forEach(input => {
            const name = input.name;
            if (!name) return;
            const qty = this.getFieldQuantityType(name);
            if (qty && input.value !== '' && !input.value.startsWith('D') && !input.value.startsWith('M') && !input.readOnly) {
                const rebased = window.UnitManager.rebaseUnitDraftText(input.value, prevSys, nextSys, qty);
                input.value = rebased;
                const newUnitStr = window.UnitManager.getUnitString(qty);
                if (newUnitStr && input.placeholder && input.placeholder.includes('(')) {
                    input.placeholder = input.placeholder.replace(/\([^)]*\)/, `(${newUnitStr})`);
                }
            }
        });
    },

    getFieldQuantityType(fieldName) {
        const lk = fieldName.toLowerCase();
        // Forces (kN)
        if (['pu', 'vu', 'tu', 'p_serv', 'p1', 'p2', 'p_allow', 'v_u', 'p_u', 'axial_force', 'p_serv_tot', 'f_tension', 'f_shear', 't_u', 'wheel_load', 'pe_eff'].includes(lk)) return 'force';
        // Moments (kN·m)
        if (['mu', 'mux', 'muy', 'muz', 'mx_serv', 'my_serv', 'm_serv', 'moment', 'mu_x', 'mu_y', 'mn', 'mnx', 'mny', 'mt_local'].includes(lk)) return 'moment';
        // Stresses / Material Strengths (MPa)
        if (['fck', 'fci', 'fy', 'fys', 'fyt', 'fy_steel', 'fy_rebar', 'fu', 'fyk', 'fpu', 'fps', 'e', 'es', 'ec', 'f_ck', 'fck_c', 'fy_h', 'fy_v', 'fy_main', 'fy_sub', 'qa_soil', 'fb', 'ft', 'fv', 'f_y', 'f_u'].includes(lk)) return 'stress';
        // Area Loads / Pressures (kN/m²)
        if (['qa', 'll', 'dl', 'dead_load_finish', 'finish_load', 'live_load', 'qsurf', 'qsurface', 'soil_pressure', 'w_dead', 'w_live', 'w_total', 'load'].includes(lk)) return 'areaLoad';
        // Length in Meters (Spans / Story heights)
        if (['span', 'span_x', 'span_y', 'span_horiz', 'l', 'lx', 'ly', 'lb', 'l_clear', 'height_story', 'h_story', 'len'].includes(lk)) return 'length_m';
        // Section Dimensions / Length in Millimeters (Steel, RC, Bolt, Rebar)
        if (['b', 'bw', 'h', 'h1', 'b1', 'd', 'tw', 'tf', 't_w', 't_f', 'cover', 'cx', 'cy', 't_steel', 'slab_thick', 'tread_r', 'tread_t', 'pile_dia', 'pile_cap_dia', 'edge_dist', 'bolt_spacing', 'r', 'b_f', 'h_f', 'bf', 'b_top', 'h_top', 'col_b', 'col_h', 'col_d', 'col_bf', 'lw', 'thickness', 't', 'cc', 'c_c', 'width', 'depth', 'flange_w', 'flange_t', 'web_t', 'd_eff', 'bar_spacing', 'rebar_spacing', 'stirrup_spacing', 'pitch', 'gap', 'db', 'dt', 'main_dia', 'tie_dia', 'stir_dia', 'top_dia', 'bot_dia', 'vert_dia', 'horiz_dia', 'dia', 'stirrup_dia', 'top_layer1_dia', 'top_layer2_dia', 'bot_layer1_dia', 'bot_layer2_dia', 'side_dia', 'dowel_dia', 'bolt_dia', 'd_bolt', 'hole_dia', 'd_hole', 'bot_rebar_x_spacing', 'bot_rebar_y_spacing', 'web_h_spacing', 'web_v_spacing', 'stem_rebar_spacing', 'ln', 'wheel_spacing', 'open_size', 'open_width', 'clear_spacing'].includes(lk)) return 'length';
        // Section Areas (mm²)
        if (['a', 'as', 'as_req', 'as_prov', 'ast', 'ag', 'av', 'as_top', 'as_bot'].includes(lk)) return 'area';
        return null;
    }
};
