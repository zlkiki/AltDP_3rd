// web/js/store/project_store.js
/**
 * AltDP Member Designer - Central Project Store (SSOT)
 * re-DCR (STRIX) Zustand / Snapshot Architecture Port
 * 
 * - Single Source of Truth for Layout, Members, Inputs, and Analysis Results
 * - Clean Startup by Default
 * - Export & Import Snapshot Serialization (Hydrate All)
 * - Event Observer / Subscriber Pattern
 */

(function () {
    // MemberDesign_Project_20260825_1408.json 기준 시스템 기본 레이아웃
    const SYSTEM_DEFAULT_LAYOUT = {
        mainSplitRatio: 0.481,   // Left Area (48.1%) : Right Report (51.9%)
        leftSplitHRatio: 0.524,  // Left-Left (52.4%) : Left-Right Graphic (47.6%)
        leftSplitVRatio: 0.35,   // Top MemberList (35%) : Bottom InputForm (65%)
        sidebarWidth: 250,
        sidebarCollapsed: false, // 첫 실행 시 좌측 메뉴가 보이도록 활성화
        sidebarPinned: false     // unpinned (자동 숨김 모드) 상태로 시작
    };

    const DEFAULT_META = {
        projectName: "단위부재 구조설계 프로젝트",
        standard: "KDS 2022 최신 기준",
        version: "1.0",
        savedAt: null
    };

    class ProjectStore {
        constructor() {
            this.listeners = [];
            this.initClean();
        }

        /**
         * Get user-defined custom default layout or fallback to system default
         */
        getDefaultLayout() {
            try {
                const saved = localStorage.getItem('altdp_custom_default_layout');
                if (saved) {
                    return { ...SYSTEM_DEFAULT_LAYOUT, ...JSON.parse(saved) };
                }
            } catch (e) {
                console.warn("[ProjectStore] Failed to parse custom default layout:", e);
            }
            return { ...SYSTEM_DEFAULT_LAYOUT };
        }

        /**
         * Clean Start: Reset all state to clean initial defaults without loading past cache
         */
        initClean() {
            this.state = {
                meta: { ...DEFAULT_META, createdAt: new Date().toISOString() },
                layout: this.getDefaultLayout(),
                activeContext: {
                    category: 'rc',
                    moduleKey: 'rc/beam/base',
                    activeMemberId: null
                },
                modules: {} // key -> { activeMemberId, members: [] }
            };
            this.notify('STORE_RESET', this.state);
        }

        /**
         * Save current layout and theme as permanent user default
         */
        saveCurrentAsDefault(currentTheme = 'dark') {
            try {
                const currentLayout = this.getLayout();
                localStorage.setItem('altdp_custom_default_layout', JSON.stringify(currentLayout));
                localStorage.setItem('altdp_custom_default_theme', currentTheme);
                this.notify('CUSTOM_DEFAULT_SAVED', { layout: currentLayout, theme: currentTheme });
                return true;
            } catch (err) {
                console.error("[ProjectStore] Failed to save custom default:", err);
                return false;
            }
        }

        // ==========================================
        // Observer / Subscriber Pattern
        // ==========================================
        subscribe(listenerFn) {
            if (typeof listenerFn === 'function' && !this.listeners.includes(listenerFn)) {
                this.listeners.push(listenerFn);
            }
            return () => {
                this.listeners = this.listeners.filter(fn => fn !== listenerFn);
            };
        }

        notify(event, payload = null) {
            this.listeners.forEach(fn => {
                try {
                    fn(event, payload, this.state);
                } catch (err) {
                    console.error(`[ProjectStore] Listener error on event '${event}':`, err);
                }
            });
        }

        getState() {
            return this.state;
        }

        // ==========================================
        // Layout State Actions
        // ==========================================
        getLayout() {
            return this.state.layout;
        }

        setLayout(newLayout) {
            this.state.layout = { ...this.state.layout, ...newLayout };
            this.notify('LAYOUT_CHANGED', this.state.layout);
        }

        resetLayout() {
            this.state.layout = this.getDefaultLayout();
            this.notify('LAYOUT_RESET', this.state.layout);
        }

        toggleSidebar() {
            this.state.layout.sidebarCollapsed = !this.state.layout.sidebarCollapsed;
            this.notify('SIDEBAR_TOGGLED', this.state.layout);
        }

        setSidebarCollapsed(collapsed) {
            this.state.layout.sidebarCollapsed = Boolean(collapsed);
            this.notify('SIDEBAR_COLLAPSED_CHANGED', this.state.layout);
        }

        setSidebarPinned(pinned) {
            this.state.layout.sidebarPinned = Boolean(pinned);
            this.notify('SIDEBAR_PIN_CHANGED', this.state.layout);
        }

        // ==========================================
        // Active Navigation Context Actions
        // ==========================================
        setActiveModule(moduleKey, category = null) {
            this.state.activeContext.moduleKey = moduleKey;
            if (category) {
                this.state.activeContext.category = category;
            } else if (moduleKey) {
                this.state.activeContext.category = moduleKey.split('/')[0] || 'rc';
            }
            // Ensure the module is initialized with at least 1 member immediately
            this.ensureModule(moduleKey);
            this.notify('MODULE_CHANGED', { moduleKey: this.state.activeContext.moduleKey });
        }

        // ==========================================
        // Module & Multi-Member Management Actions
        // ==========================================
        ensureModule(moduleKey, defaultInputs = {}) {
            if (!moduleKey) return null;
            if (!this.state.modules[moduleKey] || !this.state.modules[moduleKey].members || this.state.modules[moduleKey].members.length === 0) {
                const initialMemberId = `m-${Date.now()}-1`;
                const memberPrefix = this._getMemberPrefix(moduleKey);
                const initialMember = {
                    id: initialMemberId,
                    name: `${memberPrefix}01`,
                    inputs: { ...defaultInputs },
                    result: null,
                    dcr: 0.0,
                    status: 'READY',
                    updatedAt: Date.now()
                };

                this.state.modules[moduleKey] = {
                    activeMemberId: initialMemberId,
                    members: [initialMember]
                };
                this.notify('MEMBER_ADDED', { moduleKey, member: initialMember });
            } else if (defaultInputs && Object.keys(defaultInputs).length > 0) {
                // If member inputs are completely empty, populate schema defaults
                const active = this.getActiveMember(moduleKey);
                if (active && (!active.inputs || Object.keys(active.inputs).length === 0)) {
                    active.inputs = { ...defaultInputs };
                }
            }
            return this.state.modules[moduleKey];
        }

        getModuleData(moduleKey) {
            return this.state.modules[moduleKey] || null;
        }

        getMembers(moduleKey) {
            const mod = this.ensureModule(moduleKey);
            return mod ? mod.members : [];
        }

        getActiveMember(moduleKey) {
            if (!moduleKey) return null;
            const mod = this.ensureModule(moduleKey);
            if (!mod || !mod.members || mod.members.length === 0) return null;
            let active = mod.members.find(m => m.id === mod.activeMemberId);
            if (!active) {
                active = mod.members[0];
                mod.activeMemberId = active.id;
            }
            return active;
        }

        addMember(moduleKey, customName = null, baseInputs = {}) {
            const mod = this.ensureModule(moduleKey, baseInputs);
            const nextIdx = mod.members.length + 1;
            const prefix = this._getMemberPrefix(moduleKey);
            const numStr = String(nextIdx).padStart(2, '0');
            const newId = `m-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

            const newMember = {
                id: newId,
                name: customName || `${prefix}${numStr}`,
                inputs: { ...baseInputs },
                result: null,
                dcr: 0.0,
                status: 'READY',
                updatedAt: Date.now()
            };

            mod.members.push(newMember);
            mod.activeMemberId = newId;
            this.notify('MEMBER_ADDED', { moduleKey, member: newMember });
            return newMember;
        }

        duplicateMember(moduleKey, memberId) {
            const mod = this.state.modules[moduleKey];
            if (!mod) return null;

            const target = mod.members.find(m => m.id === memberId);
            if (!target) return null;

            const newId = `m-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            const copy = {
                id: newId,
                name: `${target.name}_Copy`,
                inputs: JSON.parse(JSON.stringify(target.inputs || {})),
                result: target.result ? JSON.parse(JSON.stringify(target.result)) : null,
                dcr: target.dcr || 0.0,
                status: target.status || 'READY',
                updatedAt: Date.now()
            };

            const idx = mod.members.findIndex(m => m.id === memberId);
            mod.members.splice(idx + 1, 0, copy);
            mod.activeMemberId = newId;

            this.notify('MEMBER_DUPLICATED', { moduleKey, member: copy });
            return copy;
        }

        deleteMember(moduleKey, memberId) {
            const mod = this.state.modules[moduleKey];
            if (!mod || mod.members.length <= 1) {
                // Keep at least one member
                return false;
            }

            const delIdx = mod.members.findIndex(m => m.id === memberId);
            if (delIdx === -1) return false;

            mod.members.splice(delIdx, 1);
            if (mod.activeMemberId === memberId) {
                const nextActive = mod.members[Math.max(0, delIdx - 1)] || mod.members[0];
                mod.activeMemberId = nextActive ? nextActive.id : null;
            }

            this.notify('MEMBER_DELETED', { moduleKey, deletedId: memberId, activeMemberId: mod.activeMemberId });
            return true;
        }

        renameMember(moduleKey, memberId, newName) {
            const mod = this.state.modules[moduleKey];
            if (!mod) return false;
            const target = mod.members.find(m => m.id === memberId);
            if (target && newName && newName.trim()) {
                target.name = newName.trim();
                target.updatedAt = Date.now();
                this.notify('MEMBER_RENAMED', { moduleKey, member: target });
                return true;
            }
            return false;
        }

        selectMember(moduleKey, memberId) {
            const mod = this.state.modules[moduleKey];
            if (!mod) return;
            const target = mod.members.find(m => m.id === memberId);
            if (target) {
                mod.activeMemberId = memberId;
                this.notify('MEMBER_SELECTED', { moduleKey, member: target });
            }
        }

        setActiveMember(moduleKey, memberId) {
            return this.selectMember(moduleKey, memberId);
        }

        updateMemberInputs(moduleKey, memberId, newInputs) {
            const mod = this.state.modules[moduleKey];
            if (!mod) return;
            const target = mod.members.find(m => m.id === memberId);
            if (target) {
                target.inputs = { ...target.inputs, ...newInputs };
                target.updatedAt = Date.now();
                this.notify('MEMBER_INPUTS_UPDATED', { moduleKey, member: target });
            }
        }

        updateMemberResult(moduleKey, memberId, resultData) {
            const mod = this.state.modules[moduleKey];
            if (!mod) return;
            const target = mod.members.find(m => m.id === memberId);
            if (target) {
                target.result = resultData;
                target.dcr = Number(resultData?.governing_dcr || resultData?.max_dcr || resultData?.dcr || 0.0);
                target.status = (resultData?.status === 'OK' || resultData?.status === 'PASS') ? 'PASS' : 'FAIL';
                target.updatedAt = Date.now();

                this.notify('MEMBER_RESULT_UPDATED', { moduleKey, member: target });
            }
        }

        _getMemberPrefix(moduleKey) {
            if (!moduleKey) return 'M';
            const k = moduleKey.toLowerCase();
            
            // 1. RC (26 Modules)
            if (k === 'rc/wall/base') return 'SW';
            if (k === 'rc/wall/bmt') return 'BW';
            if (k === 'rc/wall/canti') return 'CW';
            if (k === 'rc/beam/deep') return 'DB';
            if (k === 'rc/beam/tsect') return 'TB';
            if (k === 'rc/beam/torsion') return 'TRB';
            if (k.startsWith('rc/beam/')) return 'B';
            if (k === 'rc/column/irreg') return 'IC';
            if (k === 'rc/column/biaxial') return 'BC';
            if (k === 'rc/column/slender') return 'SC';
            if (k.startsWith('rc/column/')) return 'C';
            if (k === 'rc/footing/base') return 'F';
            if (k === 'rc/footing/com') return 'CF';
            if (k === 'rc/footing/pile_cap') return 'PF';
            if (k === 'rc/footing/reinf') return 'RF';
            if (k === 'rc/slab/slab_1way') return 'S1W';
            if (k === 'rc/slab/slab_2way') return 'S2W';
            if (k === 'rc/slab/flat') return 'FS';
            if (k === 'rc/slab/sog') return 'SOG';
            if (k.startsWith('rc/slab/')) return 'S';

            // 2. Steel (13~15 Modules)
            if (k === 'steel/member/beam') return 'SB';
            if (k === 'steel/member/column') return 'SC';
            if (k === 'steel/member/truss') return 'TR';
            if (k === 'steel/composite/beam') return 'CB';
            if (k === 'steel/composite/deck') return 'DK';
            if (k === 'steel/composite/web_open') return 'WO';
            if (k === 'steel/connection/baseplate') return 'BP';
            if (k === 'steel/connection/beam_bw') return 'BC';
            if (k === 'steel/connection/bolt') return 'BL';
            if (k === 'steel/connection/bolt_bear') return 'BLB';
            if (k === 'steel/connection/bolt_tens') return 'BLT';
            if (k === 'steel/connection/endplate') return 'EP';
            if (k === 'steel/connection/hbr_splice') return 'HBR';
            if (k === 'steel/connection/weld') return 'WD';
            if (k === 'steel/special/crane_girder') return 'CG';
            if (k === 'steel/special/floor_vib') return 'VB';

            // 3. PC (7 Modules)
            if (k === 'pc/beam/pc_beam') return 'PB';
            if (k === 'pc/beam/inverse_t') return 'ITB';
            if (k === 'pc/beam/psc_beam') return 'PSC';
            if (k === 'pc/connection/dap_end') return 'DAP';
            if (k === 'pc/connection/end_bearing') return 'EB';
            if (k === 'pc/slab/double_tee') return 'DT';
            if (k === 'pc/slab/half_slab') return 'HS';

            // 4. Misc (8~10 Modules)
            if (k === 'misc/special/bracket') return 'BK';
            if (k === 'misc/special/buttress') return 'BT';
            if (k === 'misc/special/stair') return 'ST';
            if (k === 'misc/special/water_tank') return 'WT';
            if (k === 'misc/src/beam') return 'SRB';
            if (k === 'misc/src/column') return 'SRC';
            if (k === 'misc/rebar/area') return 'RBA';
            if (k === 'misc/rebar/crack') return 'CRK';
            if (k === 'misc/rebar/dev_len') return 'DEV';
            if (k === 'misc/rebar/splice') return 'SPL';

            // Category/Group generic fallbacks
            const parts = moduleKey.split('/');
            const cat = parts[0] || '';
            const grp = parts[1] || '';
            if (grp.includes('beam')) return cat === 'steel' ? 'SB' : (cat === 'pc' ? 'PB' : 'B');
            if (grp.includes('column')) return cat === 'steel' ? 'SC' : (cat === 'src' ? 'SRC' : 'C');
            if (grp.includes('wall')) return 'SW';
            if (grp.includes('footing')) return 'F';
            if (grp.includes('slab')) return 'S';
            if (grp.includes('connection')) return 'CN';
            return 'M';
        }

        // ==========================================
        // Export & Import (re-DCR Snapshot Pattern)
        // ==========================================
        async exportProject() {
            const snapshot = {
                meta: {
                    ...this.state.meta,
                    savedAt: new Date().toISOString(),
                    exportedBy: "Antigravity Member Designer v1.0"
                },
                layout: this.state.layout,
                activeContext: this.state.activeContext,
                modules: this.state.modules
            };

            const jsonStr = JSON.stringify(snapshot, null, 2);
            const now = new Date();
            const dateStr = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}`;
            const fileName = `MemberDesign_Project_${dateStr}.json`;

            // 1. Native Save File Picker Dialog
            if (window.showSaveFilePicker) {
                try {
                    const handle = await window.showSaveFilePicker({
                        suggestedName: fileName,
                        types: [{
                            description: 'JSON Project File (*.json)',
                            accept: { 'application/json': ['.json'] }
                        }]
                    });
                    const writable = await handle.createWritable();
                    await writable.write(jsonStr);
                    await writable.close();
                    this.notify('PROJECT_EXPORTED', { fileName: handle.name || fileName });
                    return handle.name || fileName;
                } catch (err) {
                    if (err.name === 'AbortError') {
                        // User cancelled the save dialog
                        return null;
                    }
                    console.warn('[ProjectStore] showSaveFilePicker fallback:', err);
                }
            }

            // 2. Download Anchor Fallback
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.notify('PROJECT_EXPORTED', { fileName });
            return fileName;
        }

        importProject(jsonData) {
            try {
                const parsed = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
                if (!parsed || typeof parsed !== 'object') {
                    throw new Error("올바른 JSON 프로젝트 형식이 아닙니다.");
                }

                // Hydrate Store State
                this.state = {
                    meta: {
                        ...DEFAULT_META,
                        ...(parsed.meta || {}),
                        importedAt: new Date().toISOString()
                    },
                    layout: {
                        ...this.getDefaultLayout(),
                        ...(parsed.layout || {})
                    },
                    activeContext: {
                        category: parsed.activeContext?.category || 'rc',
                        moduleKey: parsed.activeContext?.moduleKey || 'rc/beam/base',
                        activeMemberId: parsed.activeContext?.activeMemberId || null
                    },
                    modules: parsed.modules || {}
                };

                // Ensure every module in the imported state has valid members
                Object.keys(this.state.modules).forEach(mk => {
                    const mdata = this.state.modules[mk];
                    if (!mdata.members || mdata.members.length === 0) {
                        this.ensureModule(mk);
                    }
                });

                // Notify all UI subscribers to re-render in one shot
                this.notify('HYDRATE_ALL', this.state);
                return { success: true };
            } catch (err) {
                console.error("[ProjectStore] Import failed:", err);
                return { success: false, error: err.message };
            }
        }
    }

    // Global Singleton Export
    window.ProjectStore = new ProjectStore();
})();
