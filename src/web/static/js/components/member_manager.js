// web/js/components/member_manager.js
/**
 * Member Manager Component (Table & CRUD Operations)
 * Handles multi-member design within the active module.
 */

(function () {
    class MemberManager {
        constructor() {
            this.containerEl = null;
            this.countBadgeEl = null;
            this.activeTagEl = null;
        }

        init() {
            this.containerEl = document.getElementById('member-list-container');
            this.countBadgeEl = document.getElementById('member-count-badge');
            this.activeTagEl = document.getElementById('active-member-tag');

            this.bindToolbarButtons();

            if (window.ProjectStore) {
                window.ProjectStore.subscribe((event, payload, state) => {
                    if (
                        event === 'MODULE_CHANGED' ||
                        event === 'MEMBER_ADDED' ||
                        event === 'MEMBER_DUPLICATED' ||
                        event === 'MEMBER_DELETED' ||
                        event === 'MEMBER_RENAMED' ||
                        event === 'MEMBER_SELECTED' ||
                        event === 'MEMBER_RESULT_UPDATED' ||
                        event === 'MEMBER_INPUTS_UPDATED' ||
                        event === 'HYDRATE_ALL' ||
                        event === 'STORE_RESET'
                    ) {
                        this.renderMemberList();
                    }
                });
            }

            // Initial render
            this.renderMemberList();
        }

        /**
         * Save current dynamic form state into currently active member before switching/adding
         */
        _syncCurrentFormToActiveMember() {
            if (!window.ProjectStore) return;
            const state = window.ProjectStore.getState();
            const modKey = state.activeContext.moduleKey;
            if (!modKey) return;

            const activeMember = window.ProjectStore.getActiveMember(modKey);
            const formEl = document.getElementById('dynamic-form');
            if (activeMember && formEl && window.FormGenerator) {
                const currentInputs = window.FormGenerator.getFormData(formEl);
                if (currentInputs && Object.keys(currentInputs).length > 0) {
                    window.ProjectStore.updateMemberInputs(modKey, activeMember.id, currentInputs);
                }
            }
        }

        bindToolbarButtons() {
            const btnAdd = document.getElementById('btn-add-member');
            const btnDup = document.getElementById('btn-dup-member');
            const btnDel = document.getElementById('btn-del-member');

            if (btnAdd && !btnAdd.dataset.bound) {
                btnAdd.dataset.bound = 'true';
                btnAdd.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (!window.ProjectStore) return;
                    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
                    if (!modKey) return;

                    // 1. Sync current form
                    this._syncCurrentFormToActiveMember();

                    // 2. Base inputs from current form or empty
                    const formEl = document.getElementById('dynamic-form');
                    const currentInputs = window.FormGenerator ? window.FormGenerator.getFormData(formEl) : {};

                    // 3. Add new member
                    window.ProjectStore.addMember(modKey, null, currentInputs);
                    this.onActiveMemberChanged();
                });
            }

            if (btnDup && !btnDup.dataset.bound) {
                btnDup.dataset.bound = 'true';
                btnDup.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (!window.ProjectStore) return;
                    const state = window.ProjectStore.getState();
                    const modKey = state.activeContext.moduleKey;
                    if (!modKey) return;

                    // 1. Sync current form
                    this._syncCurrentFormToActiveMember();

                    // 2. Duplicate active member
                    const activeMember = window.ProjectStore.getActiveMember(modKey);
                    if (activeMember) {
                        window.ProjectStore.duplicateMember(modKey, activeMember.id);
                        this.onActiveMemberChanged();
                    }
                });
            }

            if (btnDel && !btnDel.dataset.bound) {
                btnDel.dataset.bound = 'true';
                btnDel.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (!window.ProjectStore) return;
                    const state = window.ProjectStore.getState();
                    const modKey = state.activeContext.moduleKey;
                    if (!modKey) return;

                    const activeMember = window.ProjectStore.getActiveMember(modKey);
                    if (activeMember) {
                        const members = window.ProjectStore.getMembers(modKey);
                        if (members.length <= 1) {
                            alert("최소 1개의 부재는 유지되어야 합니다.");
                            return;
                        }
                        if (confirm(`'${activeMember.name}' 부재를 삭제하시겠습니까?`)) {
                            window.ProjectStore.deleteMember(modKey, activeMember.id);
                            this.onActiveMemberChanged();
                        }
                    }
                });
            }
        }

        renderMemberList() {
            this.containerEl = this.containerEl || document.getElementById('member-list-container');
            this.countBadgeEl = this.countBadgeEl || document.getElementById('member-count-badge');
            this.activeTagEl = this.activeTagEl || document.getElementById('active-member-tag');

            if (!this.containerEl || !window.ProjectStore) return;

            const state = window.ProjectStore.getState();
            const modKey = state.activeContext.moduleKey;
            if (!modKey) return;

            let members = window.ProjectStore.getMembers(modKey);
            let activeMember = window.ProjectStore.getActiveMember(modKey);

            if ((!members || members.length === 0) && modKey) {
                window.ProjectStore.ensureModule(modKey);
                members = window.ProjectStore.getMembers(modKey);
                activeMember = window.ProjectStore.getActiveMember(modKey);
            }

            const count = members ? members.length : 0;
            if (this.countBadgeEl) {
                this.countBadgeEl.innerText = `${count}개`;
            }
            if (this.activeTagEl && activeMember) {
                this.activeTagEl.innerText = activeMember.name;
            }

            if (!members || members.length === 0) {
                this.containerEl.innerHTML = '<div style="padding: 14px; font-size: 11.5px; color: var(--text-muted); text-align: center;">등록된 부재가 없습니다.</div>';
                return;
            }

            const table = document.createElement('table');
            table.className = 'member-table';

            // Header (Req 21-3: 부재명 | 단면 치수 | 주요 배근/형강 규격 | 소요력 | DCR 상태)
            table.innerHTML = `
                <thead>
                    <tr>
                        <th style="width: 26px; text-align: center;">선택</th>
                        <th style="min-width: 65px;">부재명</th>
                        <th style="min-width: 80px;">단면 치수</th>
                        <th style="min-width: 95px;">주요 배근 / 형강</th>
                        <th style="min-width: 75px;">소요력</th>
                        <th style="text-align: right; width: 75px;">DCR 상태</th>
                    </tr>
                </thead>
            `;

            const tbody = document.createElement('tbody');

            members.forEach(m => {
                const isActive = activeMember && activeMember.id === m.id;
                const tr = document.createElement('tr');
                tr.className = `member-row ${isActive ? 'active' : ''}`;
                tr.dataset.memberId = m.id;

                // 1. Section Summary Text
                const secText = this._extractSectionSummary(m.inputs);

                // 2. Rebar / Steel Spec Summary Text
                const rebarText = this._extractRebarSummary(m.inputs);

                // 3. Design Force Summary Text
                const forceText = this._extractForceSummary(m.inputs);

                // 4. DCR Text (Req 21-3: 칩/배경색 제거, 폰트 컬러로만 표기)
                const dcr = Number(m.dcr || 0.0);
                let dcrClass = 'dcr-text-ready';
                let dcrText = '- READY';

                if (m.status === 'PASS') {
                    dcrClass = 'dcr-text-ok';
                    dcrText = `${dcr.toFixed(3)} OK`;
                } else if (m.status === 'FAIL') {
                    dcrClass = 'dcr-text-ng';
                    dcrText = `${dcr.toFixed(3)} NG`;
                }

                tr.innerHTML = `
                    <td style="text-align: center;">
                        <input type="radio" name="member-select-radio" value="${m.id}" ${isActive ? 'checked' : ''} style="cursor: pointer;">
                    </td>
                    <td class="member-name-cell" title="더블클릭하여 이름 수정">
                        <span class="name-display">${m.name}</span>
                    </td>
                    <td style="color: var(--text-muted); font-family: var(--font-mono); font-size: 11px;">
                        ${secText}
                    </td>
                    <td style="color: var(--text-dim); font-family: var(--font-mono); font-size: 11px;">
                        ${rebarText}
                    </td>
                    <td style="color: var(--text-dim); font-family: var(--font-mono); font-size: 11px;">
                        ${forceText}
                    </td>
                    <td style="text-align: right;">
                        <span class="dcr-status-text ${dcrClass}" data-member-id="${m.id}">${dcrText}</span>
                    </td>
                `;

                // Radio Button Change
                const radioInput = tr.querySelector('input[type="radio"]');
                if (radioInput) {
                    radioInput.addEventListener('change', () => {
                        this._selectMemberById(modKey, m.id);
                    });
                }

                // Row Click -> Select Member
                tr.addEventListener('click', (e) => {
                    if (e.target.tagName === 'INPUT') return; // radio or text edit handled separately
                    this._selectMemberById(modKey, m.id);
                });

                // NG Text Click -> Scroll to Report calculation failure point
                const dcrSpan = tr.querySelector('.dcr-status-text.dcr-text-ng');
                if (dcrSpan) {
                    dcrSpan.style.cursor = 'pointer';
                    dcrSpan.title = '클릭 시 계산서 검토 불합격 위치로 이동합니다';
                    dcrSpan.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this._selectMemberById(modKey, m.id);
                        const rightPane = document.getElementById('right-pane');
                        if (rightPane) {
                            const ngElement = rightPane.querySelector('.calc-fail, .verdict-fail, .fail');
                            if (ngElement) {
                                ngElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        }
                    });
                }

                // Double Click Name -> Inline Edit
                const nameDisplay = tr.querySelector('.name-display');
                if (nameDisplay) {
                    nameDisplay.addEventListener('dblclick', (e) => {
                        e.stopPropagation();
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.className = 'member-name-input';
                        input.value = m.name;

                        const commitName = () => {
                            const newName = input.value.trim();
                            if (newName && newName !== m.name) {
                                window.ProjectStore.renameMember(modKey, m.id, newName);
                            } else {
                                this.renderMemberList();
                            }
                        };

                        input.addEventListener('blur', commitName);
                        input.addEventListener('keydown', (ke) => {
                            if (ke.key === 'Enter') {
                                input.blur();
                            } else if (ke.key === 'Escape') {
                                this.renderMemberList();
                            }
                        });

                        nameDisplay.replaceWith(input);
                        input.focus();
                        input.select();
                    });
                }

                tbody.appendChild(tr);
            });

            table.appendChild(tbody);
            this.containerEl.innerHTML = '';
            this.containerEl.appendChild(table);
        }

        _selectMemberById(modKey, memberId) {
            const activeMember = window.ProjectStore.getActiveMember(modKey);
            if (activeMember && activeMember.id === memberId) return;

            // 1. Sync current form to previously active member
            this._syncCurrentFormToActiveMember();

            // 2. Select new member
            window.ProjectStore.selectMember(modKey, memberId);

            // 3. Update Form, 2D Canvas, and Report
            this.onActiveMemberChanged();
        }

        onActiveMemberChanged() {
            if (typeof window.syncActiveMemberToForm === 'function') {
                window.syncActiveMemberToForm(false);
            }
            if (window.ProjectStore) {
                const state = window.ProjectStore.getState();
                const modKey = state.activeContext.moduleKey;
                const activeMember = window.ProjectStore.getActiveMember(modKey);
                const resultContainer = document.getElementById('result-container');
                if (resultContainer && window.ResultRenderer) {
                    if (activeMember && activeMember.result) {
                        window.ResultRenderer.render(resultContainer, activeMember.result, modKey, activeMember.inputs);
                    } else {
                        window.ResultRenderer.render(resultContainer, null, modKey, activeMember ? activeMember.inputs : {});
                    }
                }
            }
            this.renderMemberList();
        }

        _extractSectionSummary(inputs = {}) {
            if (!inputs || typeof inputs !== 'object') return '-';
            const fmt = (v) => {
                if (v === undefined || v === null || isNaN(Number(v))) return v;
                if (!window.UnitManager) return v;
                const conv = window.UnitManager.fromCanonical(Number(v), 'length');
                const sys = window.UnitManager.getCurrentSystem();
                const digits = sys.digits?.length ?? 0;
                return Number(conv.toFixed(digits));
            };
            const u = window.UnitManager ? window.UnitManager.getUnitString('length') : 'mm';

            if (inputs.section_name) return `${inputs.section_name}`;
            if (inputs.b && inputs.h) return `${fmt(inputs.b)}×${fmt(inputs.h)} ${u}`;
            if (inputs.B && inputs.H && inputs.L) return `${fmt(inputs.B)}×${fmt(inputs.L)}×${fmt(inputs.H)} ${u}`;
            if (inputs.B && inputs.H) return `${fmt(inputs.B)}×${fmt(inputs.H)} ${u}`;
            if (inputs.tw && inputs.Lw) return `t${fmt(inputs.tw)} L${fmt(inputs.Lw)} ${u}`;
            if (inputs.b_f && inputs.h_f) return `B${fmt(inputs.b_f)} L${fmt(inputs.h_f)} ${u}`;
            if (inputs.D) return `D${fmt(inputs.D)} ${u}`;
            if (inputs.thickness || inputs.thk || inputs.t) return `t${fmt(inputs.thickness || inputs.thk || inputs.t)} ${u}`;
            return '-';
        }

        _extractRebarSummary(inputs = {}) {
            if (!inputs || typeof inputs !== 'object') return '-';
            // 1. RC Beam: Top / Bottom Rebar
            if (inputs.top_num && inputs.top_dia && inputs.bot_num && inputs.bot_dia) {
                return `상 ${inputs.top_num}-D${inputs.top_dia}, 하 ${inputs.bot_num}-D${inputs.bot_dia}`;
            }
            if (inputs.top_num && inputs.top_dia) {
                return `상 ${inputs.top_num}-D${inputs.top_dia}`;
            }
            if (inputs.bot_num && inputs.bot_dia) {
                return `하 ${inputs.bot_num}-D${inputs.bot_dia}`;
            }
            // 2. RC Column: Main Rebar
            if (inputs.main_num && inputs.main_dia) {
                return `${inputs.main_num}-D${inputs.main_dia}`;
            }
            if (inputs.nx && inputs.ny && inputs.main_dia) {
                return `${(inputs.nx * 2 + (inputs.ny - 2) * 2)}-D${inputs.main_dia}`;
            }
            // 3. RC Slab / Wall / Footing: Diameter @ Spacing
            if (inputs.dia && inputs.spacing) {
                return `D${inputs.dia}@${inputs.spacing}`;
            }
            if (inputs.bar_dia && inputs.bar_spacing) {
                return `D${inputs.bar_dia}@${inputs.bar_spacing}`;
            }
            // 4. Steel Section Name
            if (inputs.section_name) {
                return inputs.steel_grade || 'SM355';
            }
            if (inputs.shape) {
                return inputs.shape;
            }
            // 5. Bolt Connections
            if (inputs.num_bolts && inputs.bolt_dia) {
                return `${inputs.num_bolts}-M${inputs.bolt_dia}`;
            }
            return '-';
        }

        _extractForceSummary(inputs = {}) {
            if (!inputs || typeof inputs !== 'object') return '-';
            const forces = [];
            const mu = inputs.mu ?? inputs.mux ?? inputs.m_u;
            const vu = inputs.vu ?? inputs.v_u;
            const pu = inputs.pu ?? inputs.p_u;

            if (mu !== undefined && mu !== null && Number(mu) !== 0) {
                forces.push(`Mu ${Number(mu).toFixed(0)}`);
            }
            if (vu !== undefined && vu !== null && Number(vu) !== 0) {
                forces.push(`Vu ${Number(vu).toFixed(0)}`);
            }
            if (pu !== undefined && pu !== null && Number(pu) !== 0) {
                forces.push(`Pu ${Number(pu).toFixed(0)}`);
            }

            if (forces.length > 0) {
                return forces.join(', ');
            }
            return '-';
        }
    }

    // Global Export
    window.MemberManager = new MemberManager();
})();
