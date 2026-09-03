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

            // Header
            table.innerHTML = `
                <thead>
                    <tr>
                        <th style="width: 32px; text-align: center;">선택</th>
                        <th style="min-width: 70px;">부재명</th>
                        <th>단면 요약</th>
                        <th style="text-align: right; width: 75px;">DCR</th>
                    </tr>
                </thead>
            `;

            const tbody = document.createElement('tbody');

            members.forEach(m => {
                const isActive = activeMember && activeMember.id === m.id;
                const tr = document.createElement('tr');
                tr.className = `member-row ${isActive ? 'active' : ''}`;
                tr.dataset.memberId = m.id;

                // Section Summary Text
                const secText = this._extractSectionSummary(m.inputs);

                // DCR Badge
                const dcr = Number(m.dcr || 0.0);
                let badgeClass = 'ready';
                let badgeText = 'READY';

                if (m.status === 'PASS') {
                    badgeClass = 'pass';
                    badgeText = `${dcr.toFixed(3)} OK`;
                } else if (m.status === 'FAIL') {
                    badgeClass = 'fail';
                    badgeText = `${dcr.toFixed(3)} NG`;
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
                    <td style="text-align: right;">
                        <span class="dcr-badge ${badgeClass}">${badgeText}</span>
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
    }

    // Global Export
    window.MemberManager = new MemberManager();
})();
