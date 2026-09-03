// web/js/components/form_combobox.js
/**
 * KS Standard Database Combobox, Context-aware Strict Dropdowns & AutoFill Controller
 * - KS D 3504 Standard Rebar Designation (D10 ~ D57)
 * - KS B 1010 / 0233 / 1016 Standard Bolt Designation (M16 ~ M36, F10T/F13T/4.6/SS275)
 * - KS Structural Steel Grades (SS275, SM355, SHN520, SNRT275, SNT355, etc.)
 * - KS Section Database Combobox (H-Beam, Box, Pipe) with shape_type Dynamic Filtering & Instant Auto-fill
 * - Premium Readonly Strict Dropdowns (open_shape, splice_class, crane_class, fatigue_category, hole_type, etc.)
 */

window.FormCombobox = {
    _activeMenu: null,

    init() {
        if (!this._listenerBound) {
            document.addEventListener('click', (e) => {
                if (this._activeMenu && !e.target.closest('.custom-combobox-wrap')) {
                    this._activeMenu.classList.remove('active');
                    this._activeMenu = null;
                }
            });
            this._listenerBound = true;
        }
    },

    /**
     * Strict Enum Dropdown Configurations (Context-aware, No manual arbitrary typing)
     */
    getStrictDropdownConfig(fieldName, defaultValue, moduleKey = '') {
        const lk = fieldName.toLowerCase();
        const mod = (moduleKey || (window.App && window.App.currentModule) || '').toLowerCase();

        // 1. T/L Beam Section Shape (rc/beam/tsect -> ONLY for shape fields)
        if ((lk === 'shape' || lk === 'shape_type' || lk === 'beam_shape') && (mod.includes('tsect') || mod.includes('beam') || mod.includes('t_beam'))) {
            return {
                options: [
                    { value: 'T_shape', label: 'T형 단면 (T-Beam)' },
                    { value: 'L_shape', label: 'L형 단면 (L-Beam)' }
                ]
            };
        }

        // 2. Irregular Column Section Shape (rc/column/irreg -> ONLY for shape fields)
        if ((lk === 'shape' || lk === 'shape_type' || lk === 'col_shape') && (mod.includes('irreg') || (mod.includes('column') && !mod.includes('steel') && !mod.includes('src')))) {
            return {
                options: [
                    { value: 'L_shape', label: 'L형 단면 (L-Shape Column)' },
                    { value: 'T_shape', label: 'T형 단면 (T-Shape Column)' },
                    { value: 'Cross', label: '십자형 단면 (Cross Column)' }
                ]
            };
        }

        // 3. Steel Column Section Shape (steel/member/column -> H_beam, box, pipe)
        if (mod.includes('steel') && (lk === 'shape_type' || lk === 'section_type')) {
            return {
                options: [
                    { value: 'H_beam', label: 'H형강 (H-Beam)' },
                    { value: 'box', label: '각형강관 (Box Tube)' },
                    { value: 'pipe', label: '원형강관 (Circular Pipe)' }
                ]
            };
        }

        // 4. Opening Shape
        if (['open_shape', 'opening_shape', 'shape_open'].includes(lk)) {
            return {
                options: [
                    { value: 'circle', label: '원형 개구부 (Circular)' },
                    { value: 'rect', label: '직사각형 개구부 (Rectangular)' }
                ]
            };
        }

        // 5. Lap Splice Class
        if (['splice_class', 'lap_class'].includes(lk)) {
            return {
                options: [
                    { value: 'B', label: 'B급 이음 (1.3 × ld - 실무 표준)' },
                    { value: 'A', label: 'A급 이음 (1.0 × ld)' }
                ]
            };
        }

        // 6. Exposure Condition / Crack Width Limit
        if (['exposure_condition', 'exposure_class', 'exposure_category'].includes(lk)) {
            return {
                options: [
                    { value: '건조환경 (0.3mm)', label: '1등급: 건조환경 / 실내 (허용균열폭 0.3mm)' },
                    { value: '습윤환경 (0.2mm)', label: '2등급: 습윤환경 / 옥외 (허용균열폭 0.2mm)' },
                    { value: '부식성/해안환경 (0.2mm)', label: '3등급: 부식성 / 해안환경 (허용균열폭 0.2mm)' }
                ]
            };
        }

        // 7. Crane Duty Class (KDS 14 31 10)
        if (['crane_class', 'crane_duty'].includes(lk)) {
            return {
                options: [
                    { value: 'C', label: 'Class C: 보통작업용 (실무 표준)' },
                    { value: 'A', label: 'Class A: 대기/비상용' },
                    { value: 'B', label: 'Class B: 경작업용' },
                    { value: 'D', label: 'Class D: 중작업용' },
                    { value: 'E', label: 'Class E: 연속중작업용' },
                    { value: 'F', label: 'Class F: 가혹연속작업용' }
                ]
            };
        }

        // 8. Fatigue Detail Category (KDS 14 31 10 Table 4.1-3)
        if (['fatigue_category', 'fatigue_cat'].includes(lk)) {
            return {
                options: [
                    { value: 'B', label: 'Category B (모재 및 양호한 연속 맞댐용접)' },
                    { value: 'A', label: 'Category A (압연 모재)' },
                    { value: "B'", label: "Category B' (부분용입 및 특수 플랜지)" },
                    { value: 'C', label: 'Category C (스티프너 연결부 / 횡방향 필릿용접)' },
                    { value: "C'", label: "Category C' (스터드 볼트 연결부)" },
                    { value: 'D', label: 'Category D (리벳 및 일반 볼트 연결부)' },
                    { value: 'E', label: 'Category E (필릿용접 종단부)' }
                ]
            };
        }

        // 9. Hole Type
        if (['hole_type', 'bolt_hole_type'].includes(lk)) {
            return {
                options: [
                    { value: '표준구멍', label: '표준구멍 (Standard Hole - dh = d + 2~3mm)' },
                    { value: '대형구멍', label: '대형구멍 (Oversized Hole)' },
                    { value: '단슬롯', label: '단슬롯 (Short Slot)' },
                    { value: '장슬롯', label: '장슬롯 (Long Slot)' }
                ]
            };
        }

        // 10. Support / Boundary Condition
        if (['support_condition', 'boundary_condition', 'end_condition'].includes(lk)) {
            return {
                options: [
                    { value: '1단 연속 (L/24)', label: '1단 연속 (One end continuous - L/24)' },
                    { value: '단순지지 (L/20)', label: '단순 지지 (Simply supported - L/20)' },
                    { value: '양단 연속 (L/28)', label: '양단 연속 (Both ends continuous - L/28)' },
                    { value: '캔틸레버 (L/10)', label: '캔틸레버 (Cantilever - L/10)' }
                ]
            };
        }

        // 11. Floor Vibration Occupancy Type
        if (['occupancy_type', 'room_type'].includes(lk)) {
            return {
                options: [
                    { value: 'office', label: '사무실 (Office - 기준 0.5%g)' },
                    { value: 'residential', label: '주거/호텔 (Residential - 기준 0.5%g)' },
                    { value: 'shopping', label: '쇼핑몰 (Shopping Mall - 기준 1.5%g)' },
                    { value: 'outdoor', label: '옥외 보행로 (Outdoor Bridge - 기준 5.0%g)' }
                ]
            };
        }

        // 12. Generic Section / Profile Shape Selector Fallback
        if (lk === 'shape_type' || lk === 'section_type' || lk === 'shape') {
            return {
                options: [
                    { value: 'H_beam', label: 'H형강 (H-Beam)' },
                    { value: 'box', label: '각형강관 (Box Tube)' },
                    { value: 'pipe', label: '원형강관 (Pipe)' },
                    { value: 'T_shape', label: 'T형 단면 (T-Shape)' },
                    { value: 'L_shape', label: 'L형 단면 (L-Shape)' },
                    { value: 'Cross', label: '십자형 단면 (Cross)' }
                ]
            };
        }

        return null;
    },

    /**
     * Create Premium Custom Combobox Layout with Readonly input (Strict Dropdown)
     */
    createStrictDropdown(fieldName, defaultValue, config, formElement, onValueChange) {
        this.init();
        const wrap = document.createElement('div');
        wrap.className = 'custom-combobox-wrap strict-dropdown-wrap';

        const box = document.createElement('div');
        box.className = 'combo-input-box';

        const input = document.createElement('input');
        input.type = 'text';
        input.id = `field_${fieldName}`;
        input.name = fieldName;
        input.readOnly = true;
        input.style.cursor = 'pointer';
        input.style.caretColor = 'transparent';

        const initialOpt = config.options.find(o => String(o.value).toLowerCase() === String(defaultValue).toLowerCase()) || config.options[0];
        input.value = initialOpt ? initialOpt.label : defaultValue;
        input.dataset.actualValue = initialOpt ? initialOpt.value : defaultValue;

        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'combo-toggle-btn';
        toggleBtn.innerHTML = '▼';
        toggleBtn.title = '항목 목록 열기/닫기';

        box.appendChild(input);
        box.appendChild(toggleBtn);
        wrap.appendChild(box);

        const menu = document.createElement('div');
        menu.className = 'combo-dropdown-menu';

        config.options.forEach(opt => {
            const optEl = document.createElement('div');
            optEl.className = 'combo-option';
            optEl.dataset.val = opt.value;
            optEl.innerHTML = `
                <span class="combo-option-main">${opt.label}</span>
                ${opt.desc ? `<span class="combo-option-desc">${opt.desc}</span>` : ''}
            `;

            optEl.addEventListener('click', (e) => {
                e.stopPropagation();
                input.value = opt.label;
                input.dataset.actualValue = opt.value;
                menu.classList.remove('active');
                this._activeMenu = null;

                // If shape_type changed, refresh section and grade comboboxes
                if (fieldName === 'shape_type' || fieldName === 'section_type') {
                    this.refreshDynamicComboboxes(formElement, opt.value);
                }

                onValueChange(fieldName);
            });

            menu.appendChild(optEl);
        });

        wrap.appendChild(menu);

        const toggleMenu = (e) => {
            e.stopPropagation();
            if (menu.classList.contains('active')) {
                menu.classList.remove('active');
                this._activeMenu = null;
            } else {
                if (this._activeMenu && this._activeMenu !== menu) {
                    this._activeMenu.classList.remove('active');
                }
                menu.classList.add('active');
                this._activeMenu = menu;
            }
        };

        input.addEventListener('click', toggleMenu);
        toggleBtn.addEventListener('click', toggleMenu);

        return wrap;
    },

    /**
     * Get Current Shape Type from Form (H_beam, box, pipe)
     */
    getCurrentShapeType(formElement) {
        if (!formElement) return 'H_beam';
        const shapeInput = formElement.querySelector('[name="shape_type"], [name="section_type"], [name="shape"]');
        if (shapeInput) {
            const val = shapeInput.dataset?.actualValue || shapeInput.value || '';
            const sVal = val.toLowerCase();
            if (sVal.includes('box') || sVal.includes('각')) return 'box';
            if (sVal.includes('pipe') || sVal.includes('원형') || sVal.includes('강관')) return 'pipe';
            return 'H_beam';
        }
        return 'H_beam';
    },

    /**
     * Combobox Configuration Builder with Dynamic Shape Filtering
     */
    getComboboxConfig(fieldName, defaultValue, moduleKey = '', formElement = null) {
        const lk = fieldName.toLowerCase();

        // 0. Exclude spacing/pitch/quantity fields from combobox
        if (lk.includes('spacing') || lk.includes('pitch') || lk.includes('간격') || lk.includes('count') || lk.includes('num') || lk.includes('legs') || lk.includes('curtain') || lk.includes('cycle')) {
            return null;
        }

        // 1. Bolt Grade (F10T, F13T, F8T, 4.6, 8.8, SS275, Gr.55, etc.)
        if (['bolt_grade', 'anchor_grade'].includes(lk)) {
            if (window.KS_ALL_BOLT_GRADE_DB) {
                return {
                    type: 'bolt_grade',
                    options: window.KS_ALL_BOLT_GRADE_DB.map(b => ({
                        value: b.grade,
                        main: b.grade,
                        desc: b.name
                    }))
                };
            }
        }

        // 2. Bolt Diameter (M16 ~ M36)
        if (['bolt_dia', 'anchor_dia', 'd_bolt', 'db_bolt', 'bolt_size'].includes(lk)) {
            if (window.KS_BOLT_DIA_DB) {
                return {
                    type: 'bolt_dia',
                    options: window.KS_BOLT_DIA_DB.map(b => ({
                        value: String(b.dia),
                        main: b.size,
                        desc: `Ø${b.dia}mm, ${b.nominalArea}mm² (홀 ${b.holeDia}mm)`
                    })),
                    autoFill: (formEl, val) => {
                        const b = window.KS_BOLT_DIA_DB.find(x => String(x.dia) === String(val) || x.size.toUpperCase() === String(val).toUpperCase());
                        if (b && window.FormGenerator) {
                            window.FormGenerator.setFormData(formEl, { hole_dia: b.holeDia, d_hole: b.holeDia });
                        }
                    }
                };
            }
        }

        // 3. Rebar Grade (SD300, SD400, SD500, SD600)
        if (['rebar_grade', 'fy_rebar', 'grade_rebar'].includes(lk)) {
            if (window.KS_REBAR_GRADE_DB) {
                return {
                    type: 'rebar_grade',
                    options: window.KS_REBAR_GRADE_DB.map(r => ({
                        value: r.grade,
                        main: `${r.grade} (${r.fy} MPa)`,
                        desc: r.name
                    })),
                    autoFill: (formEl, val) => {
                        const r = window.KS_REBAR_GRADE_DB.find(x => x.grade.toLowerCase() === String(val).toLowerCase() || String(x.fy) === String(val));
                        if (r && window.FormGenerator) {
                            window.FormGenerator.setFormData(formEl, { fy: r.fy, fys: r.fy, fyt: r.fy });
                        }
                    }
                };
            }
        }

        // 4. Concrete Compressive Strength (fck)
        if (['fck', 'f_ck', 'fck_c', 'fc', 'fci'].includes(lk)) {
            if (window.KS_CONCRETE_FCK_DB) {
                return {
                    type: 'fck',
                    options: window.KS_CONCRETE_FCK_DB.map(c => ({
                        value: String(c.value),
                        main: `${c.value} MPa`,
                        desc: c.name
                    }))
                };
            }
        }

        // 5. Rebar Yield Strength Value (fy, fys, fyt in MPa)
        if (['fy', 'fys', 'fyt', 'fy_h', 'fy_v', 'fyk', 'fy_main', 'fy_sub'].includes(lk)) {
            if (window.KS_REBAR_GRADE_DB) {
                return {
                    type: 'rebar_fy',
                    options: window.KS_REBAR_GRADE_DB.map(r => ({
                        value: String(r.fy),
                        main: `${r.fy} MPa (${r.grade})`,
                        desc: r.name
                    }))
                };
            }
        }

        // 6. Steel Material Grade (SS275, SM355, SHN520, SNRT275, etc.) - Dynamic Filter by shape_type
        if (['steel_grade', 'material', 'grade', 'steel_type', 'mat', 'plate_grade', 'beam_grade'].includes(lk)) {
            if (window.KS_STEEL_GRADE_DB) {
                const shape = this.getCurrentShapeType(formElement);
                let filteredGrades = window.KS_STEEL_GRADE_DB;

                if (shape === 'box') {
                    filteredGrades = window.KS_STEEL_GRADE_DB.filter(s => s.grade.includes('SRT') || s.grade.includes('SNRT') || s.grade.startsWith('SS') || s.grade.startsWith('SM'));
                } else if (shape === 'pipe') {
                    filteredGrades = window.KS_STEEL_GRADE_DB.filter(s => s.grade.includes('SNT') || s.grade.startsWith('SS') || s.grade.startsWith('SM'));
                } else {
                    // H-Beam
                    filteredGrades = window.KS_STEEL_GRADE_DB.filter(s => s.grade.includes('SHN') || s.grade.startsWith('SS') || s.grade.startsWith('SM') || s.grade.startsWith('SN'));
                }

                return {
                    type: 'steel_grade',
                    options: filteredGrades.map(s => ({
                        value: s.grade,
                        main: s.grade,
                        desc: s.name
                    })),
                    autoFill: (formEl, val) => {
                        this.autoFillSteelGradeProps(formEl, val);
                    }
                };
            }
        }

        // 7. Rebar Diameter (D10 ~ D57)
        if (lk.includes('dia') || lk.includes('rebar') || ['db', 'dt', 'd_b', 'd_t', 'bar', 'top_dia', 'bot_dia', 'tie_dia', 'stir_dia', 'stirrup_dia', 'side_dia', 'top_layer1_dia', 'top_layer2_dia', 'bot_layer1_dia', 'bot_layer2_dia', 'dowel_dia', 'vert_dia', 'horiz_dia'].includes(lk)) {
            if (window.KS_REBAR_DB) {
                return {
                    type: 'rebar',
                    options: window.KS_REBAR_DB.map(r => ({
                        value: String(parseInt(r.name.substring(1), 10)),
                        main: r.name,
                        desc: `Ø${r.dia}mm, ${r.area}mm² (${r.weight}kg/m)`
                    }))
                };
            }
        }

        // 8. KS Steel Section Database (H-Beam, Box, Pipe) - Dynamic Filter by shape_type
        if (lk.includes('section') || lk.includes('sec') || lk === 'sec_name' || lk === 'col_sec' || lk === 'beam_sec' || lk === 'steel_sec' || lk === 'profile' || lk === 'section_name' || lk === 'steel_section') {
            const shape = this.getCurrentShapeType(formElement);
            const opts = [];

            if (shape === 'box') {
                if (window.KS_BOX_DB) {
                    window.KS_BOX_DB.forEach(s => opts.push({
                        value: s.name,
                        main: s.name,
                        desc: `Box ${s.b}x${s.h}x${s.t}`
                    }));
                }
            } else if (shape === 'pipe') {
                if (window.KS_PIPE_DB) {
                    window.KS_PIPE_DB.forEach(s => opts.push({
                        value: s.name,
                        main: s.name,
                        desc: `Pipe D${s.d}x${s.t}`
                    }));
                }
            } else {
                // H-Beam
                if (window.KS_H_BEAM_DB) {
                    window.KS_H_BEAM_DB.forEach(s => opts.push({
                        value: s.name,
                        main: s.name,
                        desc: `H-Beam ${s.h}x${s.bf}x${s.tw}x${s.tf} (${s.weight}kg/m)`
                    }));
                }
            }

            return {
                type: 'section',
                options: opts,
                autoFill: (formEl, val) => {
                    this.autoFillSteelProps(formEl, val);
                }
            };
        }

        return null;
    },

    /**
     * Create Combobox Element
     */
    createCombobox(fieldName, defaultValue, config, formElement, onValueChange) {
        this.init();
        const wrap = document.createElement('div');
        wrap.className = 'custom-combobox-wrap';
        wrap.dataset.comboField = fieldName;

        const box = document.createElement('div');
        box.className = 'combo-input-box';

        const input = document.createElement('input');
        input.type = 'text';
        input.id = `field_${fieldName}`;
        input.name = fieldName;

        // Display formatting
        if (config.type === 'rebar' && defaultValue) {
            const dVal = String(defaultValue);
            input.value = dVal.startsWith('D') ? dVal : `D${dVal}`;
        } else if (config.type === 'bolt_dia' && defaultValue) {
            const dVal = String(defaultValue);
            input.value = dVal.startsWith('M') ? dVal : `M${dVal}`;
        } else {
            input.value = defaultValue;
        }

        input.placeholder = '선택 또는 직접 입력';
        input.autocomplete = 'off';

        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'combo-toggle-btn';
        toggleBtn.innerHTML = '▼';
        toggleBtn.title = '항목 목록 열기/닫기';

        box.appendChild(input);
        box.appendChild(toggleBtn);
        wrap.appendChild(box);

        // Dropdown Menu
        const menu = document.createElement('div');
        menu.className = 'combo-dropdown-menu';

        this.populateComboboxMenu(menu, input, config, formElement, onValueChange, fieldName);

        wrap.appendChild(menu);

        // Toggle Event
        const toggleMenu = (e) => {
            e.stopPropagation();
            if (menu.classList.contains('active')) {
                menu.classList.remove('active');
                this._activeMenu = null;
            } else {
                if (this._activeMenu && this._activeMenu !== menu) {
                    this._activeMenu.classList.remove('active');
                }
                menu.classList.add('active');
                this._activeMenu = menu;
            }
        };

        input.addEventListener('click', toggleMenu);
        toggleBtn.addEventListener('click', toggleMenu);

        input.addEventListener('input', () => {
            if (config.autoFill) {
                config.autoFill(formElement, input.value);
            }
            onValueChange(fieldName);
        });

        return wrap;
    },

    populateComboboxMenu(menu, input, config, formElement, onValueChange, fieldName) {
        menu.innerHTML = '';
        config.options.forEach(opt => {
            const optEl = document.createElement('div');
            optEl.className = 'combo-option';
            optEl.dataset.val = opt.value;
            optEl.innerHTML = `
                <span class="combo-option-main">${opt.main}</span>
                ${opt.desc ? `<span class="combo-option-desc">${opt.desc}</span>` : ''}
            `;

            optEl.addEventListener('click', (e) => {
                e.stopPropagation();
                if (config.type === 'rebar') {
                    input.value = `D${opt.value}`;
                } else if (config.type === 'bolt_dia') {
                    input.value = `M${opt.value}`;
                } else {
                    input.value = opt.value;
                }

                menu.classList.remove('active');
                this._activeMenu = null;
                if (config.autoFill) {
                    config.autoFill(formElement, opt.value);
                }
                onValueChange(fieldName);
            });

            menu.appendChild(optEl);
        });
    },

    /**
     * Refresh Comboboxes when shape_type changes (Dynamic Filter & First Option Auto-Select Sync)
     */
    refreshDynamicComboboxes(formElement, shapeValue) {
        if (!formElement) return;
        const modKey = (window.ProjectStore && window.ProjectStore.getState().activeContext?.moduleKey) || '';

        ['section_name', 'col_sec', 'beam_sec', 'steel_sec', 'sec_name', 'steel_grade', 'grade', 'material'].forEach(fn => {
            const wrap = formElement.querySelector(`[data-combo-field="${fn}"]`);
            if (wrap) {
                const input = wrap.querySelector('input');
                const menu = wrap.querySelector('.combo-dropdown-menu');
                const newCfg = this.getComboboxConfig(fn, input ? input.value : '', modKey, formElement);
                if (newCfg && menu && input) {
                    this.populateComboboxMenu(menu, input, newCfg, formElement, () => {
                        if (window.ProjectStore && window.FormGenerator) {
                            window.ProjectStore.updateActiveMemberInputs(window.FormGenerator.getFormData(formElement));
                        }
                    }, fn);

                    // Auto-select first filtered option if current value is invalid or shape changed
                    if (newCfg.options && newCfg.options.length > 0) {
                        const firstOpt = newCfg.options[0];
                        input.value = firstOpt.value;
                        if (newCfg.autoFill) {
                            newCfg.autoFill(formElement, firstOpt.value);
                        }
                    }
                }
            }
        });

        // Sync Store and Redraw Canvas immediately
        if (window.FormGenerator && window.ProjectStore) {
            const updatedData = window.FormGenerator.getFormData(formElement);
            window.ProjectStore.updateActiveMemberInputs(updatedData);
            if (typeof window.updateCanvasOnly === 'function') {
                window.updateCanvasOnly();
            } else if (window.CanvasRenderer) {
                window.CanvasRenderer.redrawCurrent();
            }
        }
    },

    autoFillSteelGradeProps(formElement, gradeName) {
        if (!window.KS_STEEL_GRADE_DB || !gradeName || !window.FormGenerator) return;
        const g = window.KS_STEEL_GRADE_DB.find(s => s.grade.toLowerCase() === gradeName.trim().toLowerCase());
        if (g) {
            window.FormGenerator.setFormData(formElement, { Fy: g.Fy, Fu: g.Fu, fy: g.Fy, f_y: g.Fy });
        }
    },

    autoFillSteelProps(formElement, sectionName) {
        if (!sectionName || !window.FormGenerator) return;
        const sName = sectionName.trim().toLowerCase();
        
        // 1. H-Beam
        if (window.KS_H_BEAM_DB) {
            const sec = window.KS_H_BEAM_DB.find(s => s.name.toLowerCase() === sName);
            if (sec) {
                window.FormGenerator.setFormData(formElement, {
                    b: sec.bf,
                    bf: sec.bf,
                    b_f: sec.bf,
                    B: sec.bf,
                    col_b: sec.bf,
                    beam_b: sec.bf,
                    col_bf: sec.bf,
                    beam_bf: sec.bf,
                    steel_B: sec.bf,
                    h: sec.h,
                    d: sec.h,
                    H: sec.h,
                    col_h: sec.h,
                    beam_h: sec.h,
                    col_d: sec.h,
                    beam_d: sec.h,
                    steel_H: sec.h,
                    tw: sec.tw,
                    t_w: sec.tw,
                    col_tw: sec.tw,
                    beam_tw: sec.tw,
                    steel_tw: sec.tw,
                    tf: sec.tf,
                    t_f: sec.tf,
                    col_tf: sec.tf,
                    beam_tf: sec.tf,
                    steel_tf: sec.tf,
                    r: sec.r,
                    A: sec.A,
                    Ix: sec.Ix * 10000,
                    Iy: sec.Iy * 10000,
                    Zx: sec.Zx * 1000,
                    Zy: sec.Zy * 1000
                });
                return;
            }
        }
        // 2. Box Tube
        if (window.KS_BOX_DB) {
            const sec = window.KS_BOX_DB.find(s => s.name.toLowerCase() === sName);
            if (sec) {
                window.FormGenerator.setFormData(formElement, {
                    b: sec.b,
                    bf: sec.b,
                    B: sec.b,
                    col_b: sec.b,
                    beam_b: sec.b,
                    col_bf: sec.b,
                    beam_bf: sec.b,
                    h: sec.h,
                    d: sec.h,
                    H: sec.h,
                    col_h: sec.h,
                    beam_h: sec.h,
                    col_d: sec.h,
                    beam_d: sec.h,
                    t: sec.t,
                    tw: sec.t,
                    t_w: sec.t,
                    col_tw: sec.t,
                    beam_tw: sec.t,
                    tf: sec.t,
                    t_f: sec.t,
                    col_tf: sec.t,
                    beam_tf: sec.t
                });
                return;
            }
        }
        // 3. Pipe
        if (window.KS_PIPE_DB) {
            const sec = window.KS_PIPE_DB.find(s => s.name.toLowerCase() === sName);
            if (sec) {
                window.FormGenerator.setFormData(formElement, {
                    d: sec.d,
                    h: sec.d,
                    b: sec.d,
                    D: sec.d,
                    H: sec.d,
                    B: sec.d,
                    col_d: sec.d,
                    beam_d: sec.d,
                    col_h: sec.d,
                    col_b: sec.d,
                    t: sec.t,
                    tw: sec.t,
                    t_w: sec.t,
                    col_tw: sec.t,
                    tf: sec.t,
                    t_f: sec.t,
                    col_tf: sec.t
                });
            }
        }
    }
};
