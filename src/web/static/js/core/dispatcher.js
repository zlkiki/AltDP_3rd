/**
 * AltDP_3rd ModuleDispatcher & ModuleRegistry
 * High-speed Polymorphic Module Pack Dispatcher (< 50ms switching)
 * Coordinates switching of 1열(Tree), 2열(Canvas), 3열(Input Form), and 4열(KDS Report)
 * Conforms to Requirement 21-6 & docs/07 section 6.
 */
class ModuleDispatcher {
    constructor() {
        this.modules = new Map();
        this.currentModule = null;
        this.currentMemberId = null;
        this.context = null;

        // Standard Alias Mapping for 5 Flagships + Slab
        this.aliasMap = {
            'rc_beam': ['rc/beam/base', 'rc/beam/rc_beam', 'beam_base', 'rc_beam'],
            'rc_column': ['rc/column/base', 'rc/column/rc_column', 'column_base', 'rc_column'],
            'rc_footing': ['rc/footing/base', 'rc/footing/rc_iso_footing', 'footing_base', 'rc_footing', 'rc_iso_footing'],
            'steel_beam': ['steel/member/beam', 'steel/member/column', 'steel/beam/steel_beam_column', 'steel_beam', 'steel_column', 'steel_beam_column'],
            'steel_baseplate': ['steel/connection/baseplate', 'steel/baseplate/steel_baseplate', 'steel_baseplate'],
            'rc_slab': ['rc/slab/base', 'rc/slab/rc_slab', 'slab_base', 'rc_slab']
        };
    }

    /**
     * Initialize dispatcher with DOM containers
     * @param {Object} context 
     */
    init(context) {
        this.context = context || {};
        this._setupEventListeners();
    }

    _setupEventListeners() {
        if (!window.EventBus || !window.APP_EVENTS) return;

        window.EventBus.on(window.APP_EVENTS.MEMBER_SELECTED, (payload) => {
            if (payload && (payload.type || payload.moduleKey)) {
                const modKey = payload.type || payload.moduleKey;
                this.switchModule(modKey, payload.memberId, payload.data || payload.inputs);
            }
        });

        window.EventBus.on(window.APP_EVENTS.PARAM_CHANGED, (payload) => {
            if (this.currentModule && typeof this.currentModule.onParamChange === 'function') {
                this.currentModule.onParamChange(payload);
            }
        });

        window.EventBus.on(window.APP_EVENTS.MEMBER_UPDATED || 'member:updated', (payload) => {
            if (this.currentModule && typeof this.currentModule.onParamChange === 'function' && payload?.inputs) {
                Object.keys(payload.inputs).forEach(key => {
                    this.currentModule.onParamChange({ key, value: payload.inputs[key] });
                });
            }
        });

        window.EventBus.on(window.APP_EVENTS.DISPATCHER_SWITCH || 'dispatcher:switch', (payload) => {
            if (payload && payload.key) {
                this.switchModule(payload.key, payload.memberId, payload.data);
            }
        });
    }

    /**
     * Register a specialized member module pack
     * @param {string} key 
     * @param {Object} moduleInstance 
     */
    register(key, moduleInstance) {
        if (!key || !moduleInstance) return;
        this.modules.set(key, moduleInstance);
        console.log(`[ModuleDispatcher] Registered polymorphic module pack: ${key}`);
    }

    /**
     * Resolve module instance by direct key or known alias
     * @param {string} key 
     * @returns {Object|null}
     */
    resolveModule(key) {
        if (!key) return null;
        if (this.modules.has(key)) return this.modules.get(key);

        const cleanKey = key.trim().toLowerCase();

        // 1. Check direct aliasMap reverse lookup
        for (const [primaryKey, aliases] of Object.entries(this.aliasMap)) {
            if (aliases.some(a => a.toLowerCase() === cleanKey)) {
                if (this.modules.has(primaryKey)) {
                    return this.modules.get(primaryKey);
                }
            }
        }

        // 2. Check CatalogManager aliases
        if (window.CatalogManager && typeof window.CatalogManager.getModule === 'function') {
            const meta = window.CatalogManager.getModule(key);
            if (meta) {
                if (meta.id && this.modules.has(meta.id)) return this.modules.get(meta.id);
                if (meta.key && this.modules.has(meta.key)) return this.modules.get(meta.key);
                if (Array.isArray(meta.aliases)) {
                    for (const alias of meta.aliases) {
                        if (this.modules.has(alias)) return this.modules.get(alias);
                    }
                }
            }
        }

        // 3. Fallback fuzzy match (ends with or starts with)
        for (const [modKey, modInstance] of this.modules.entries()) {
            if (cleanKey.endsWith('/' + modKey) || cleanKey === modKey) {
                return modInstance;
            }
        }

        return null;
    }

    /**
     * Retrieve a registered module
     * @param {string} key 
     * @returns {Object|null}
     */
    get(key) {
        return this.resolveModule(key);
    }

    /**
     * Resolves metadata for module key
     * @param {string} moduleKey 
     * @returns {Object|null}
     */
    getModuleMeta(moduleKey) {
        if (!moduleKey) return null;
        if (window.CatalogManager && typeof window.CatalogManager.getModule === 'function') {
            const meta = window.CatalogManager.getModule(moduleKey);
            if (meta) return meta;
        }
        if (window.allModules && Array.isArray(window.allModules)) {
            const found = window.allModules.find(m => m.key === moduleKey || m.id === moduleKey);
            if (found) return found;
        }
        return { key: moduleKey, id: moduleKey, name: moduleKey, engine_status: 'WIP', tier: 'Tier 3' };
    }

    /**
     * Determines whether the module is currently WIP
     * @param {string} moduleKey 
     * @returns {boolean}
     */
    isWIP(moduleKey) {
        const resolved = this.resolveModule(moduleKey);
        // If a dedicated module pack is registered and active, it is NOT WIP
        if (resolved) return false;

        const meta = this.getModuleMeta(moduleKey);
        if (meta && (meta.is_wip === false || meta.status === 'Online')) return false;
        if (meta && meta.engine_status === 'WIP') return true;
        if (meta && meta.engine_status === 'VERIFIED') return false;
        return true;
    }

    /**
     * Cleans up input pane form to prevent leftover listeners and stale DOM
     * @param {HTMLElement} [container] 
     */
    cleanupForm(container = null) {
        const target = container || document.getElementById('dynamic-form') || document.getElementById('pane-input-form');
        if (!target) return;

        // Unmount member_forms if available
        if (window.MemberForms && typeof window.MemberForms.clearForm === 'function') {
            window.MemberForms.clearForm(target.id || 'dynamic-form');
        }

        // Deep wipe of form content and replace to strip stale listeners
        const formEl = document.getElementById('dynamic-form');
        if (formEl && formEl.parentNode) {
            const newForm = formEl.cloneNode(false);
            newForm.innerHTML = '';
            formEl.parentNode.replaceChild(newForm, formEl);
        } else if (target) {
            target.innerHTML = '';
        }
    }

    /**
     * Switch active member module with ultra-high speed (< 50ms)
     * @param {string} moduleKey 
     * @param {string} memberId 
     * @param {Object} [memberData] 
     */
    async switchModule(moduleKey, memberId, memberData = null) {
        const startTime = performance.now();

        // 1. Unmount current module if exists
        if (this.currentModule) {
            try {
                if (typeof this.currentModule.unmount === 'function') {
                    this.currentModule.unmount();
                }
            } catch (e) {
                console.error(`[ModuleDispatcher] Error unmounting module:`, e);
            }
        }

        this.currentMemberId = memberId;
        const targetModule = this.resolveModule(moduleKey);
        const moduleMeta = this.getModuleMeta(moduleKey);
        const isWip = this.isWIP(moduleKey);

        if (targetModule && !isWip) {
            this.currentModule = targetModule;
            try {
                // Ensure form container is clean before mounting
                this.cleanupForm();

                const mountContext = {
                    ...this.context,
                    canvas: document.getElementById('canvas-geometry') || document.getElementById('sectionCanvas'),
                    pmCanvas: document.getElementById('canvas-mechanics') || document.getElementById('pmChartCanvas'),
                    formContainer: document.getElementById('dynamic-form') || document.getElementById('pane-input-form'),
                    reportContainer: document.getElementById('result-container'),
                    memberId: memberId,
                    memberData: memberData || (window.ProjectStore ? window.ProjectStore.getActiveMember(moduleKey)?.inputs : null),
                    dispatcher: this
                };

                if (typeof targetModule.mount === 'function') {
                    await targetModule.mount(mountContext);
                } else {
                    // Fallback to ModulePack protocol methods
                    const data = memberData || (typeof targetModule.getDefaultData === 'function' ? targetModule.getDefaultData() : {});
                    if (typeof targetModule.renderForm === 'function' && mountContext.formContainer) {
                        targetModule.renderForm(mountContext.formContainer, data, window.EventBus);
                    }
                    if (typeof targetModule.renderGraphics === 'function') {
                        targetModule.renderGraphics(mountContext.canvas, mountContext.pmCanvas, data, null);
                    }
                    if (typeof targetModule.renderReport === 'function' && mountContext.reportContainer) {
                        targetModule.renderReport(mountContext.reportContainer, data, null, {});
                    }
                }
            } catch (e) {
                console.error(`[ModuleDispatcher] Error mounting module "${moduleKey}":`, e);
            }
        } else {
            // Fallback / WIP Guard for modules without custom packs or in WIP status
            this.currentModule = null;

            // 1. Completely unmount and clear pane-input-form
            this.cleanupForm();

            // 2. Render modern WIP informative card if WIP
            if (isWip) {
                const targetContainer = document.getElementById('dynamic-form') || document.getElementById('pane-input-form');
                if (targetContainer && window.WIPCardRenderer) {
                    window.WIPCardRenderer.render(targetContainer, moduleMeta);
                }
            }
        }

        // Protect Member Manager & Member List tag
        const tagEl = document.getElementById('active-member-tag');
        if (tagEl && memberId) {
            tagEl.textContent = memberId;
        }

        const switchDuration = performance.now() - startTime;
        console.log(`[ModuleDispatcher] Switched to "${moduleKey}" in ${switchDuration.toFixed(2)}ms (DoD < 50ms)`);

        // Broadcast module switched
        if (window.EventBus) {
            const switchedEvent = (window.APP_EVENTS && window.APP_EVENTS.DISPATCHER_SWITCHED) || 'dispatcher:switched';
            window.EventBus.emit(switchedEvent, {
                key: moduleKey,
                memberId: memberId,
                hasCustomModule: !!targetModule && !isWip,
                isWip: isWip,
                meta: moduleMeta,
                durationMs: switchDuration
            });
        }
    }

    /**
     * Dispatch 100ms real-time parameter update
     * @param {string} memberId 
     * @param {Object} patchData 
     */
    updateMember(memberId, patchData) {
        if (!memberId || !patchData) return;
        if (this.currentModule && typeof this.currentModule.onParamChange === 'function') {
            Object.keys(patchData).forEach(k => {
                this.currentModule.onParamChange({ key: k, value: patchData[k] });
            });
        }
    }

    /**
     * Render current module graphics directly
     */
    renderCurrentModuleGraphics(geomCanvas, mechCanvas, data, result) {
        if (this.currentModule && typeof this.currentModule.renderGraphics === 'function') {
            this.currentModule.renderGraphics(geomCanvas, mechCanvas, data, result);
        }
    }

    /**
     * Render current module report directly
     */
    renderCurrentModuleReport(container, data, result, options) {
        if (this.currentModule && typeof this.currentModule.renderReport === 'function') {
            this.currentModule.renderReport(container, data, result, options);
        }
    }

    /**
     * Get currently active module
     */
    getCurrentModule() {
        return this.currentModule;
    }

    /**
     * Get currently active member ID
     */
    getCurrentMemberId() {
        return this.currentMemberId;
    }
}

// Global Singleton Instance
window.ModuleDispatcher = new ModuleDispatcher();
