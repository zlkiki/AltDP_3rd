/**
 * AltDP_3rd ModuleDispatcher & ModuleRegistry
 * Coordinates switching of 2열(Canvas), 3열(Input Form), and 4열(KDS Report)
 */
class ModuleDispatcher {
    constructor() {
        this.modules = new Map();
        this.currentModule = null;
        this.currentMemberId = null;
        this.context = null;
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
            if (payload && payload.type) {
                this.switchModule(payload.type, payload.memberId, payload.data);
            }
        });

        window.EventBus.on(window.APP_EVENTS.PARAM_CHANGED, (payload) => {
            if (this.currentModule && typeof this.currentModule.onParamChange === 'function') {
                this.currentModule.onParamChange(payload);
            }
        });
    }

    /**
     * Register a specialized member module
     * @param {string} key 
     * @param {Object} moduleInstance 
     */
    register(key, moduleInstance) {
        if (!key || !moduleInstance) return;
        this.modules.set(key, moduleInstance);
        console.log(`[ModuleDispatcher] Registered module: ${key}`);
    }

    /**
     * Retrieve a registered module
     * @param {string} key 
     * @returns {Object|null}
     */
    get(key) {
        return this.modules.get(key) || null;
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
        const meta = this.getModuleMeta(moduleKey);
        if (meta && meta.engine_status === 'WIP') return true;
        // If it does not have a specialized pack and has no properties schema, consider it WIP
        if (!this.modules.has(moduleKey)) {
            if (meta && meta.engine_status === 'VERIFIED') return false;
            return true;
        }
        return false;
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
     * Switch active member module
     * @param {string} moduleKey 
     * @param {string} memberId 
     * @param {Object} [memberData] 
     */
    async switchModule(moduleKey, memberId, memberData = null) {
        // Unmount current module if exists
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
        const targetModule = this.modules.get(moduleKey);
        const moduleMeta = this.getModuleMeta(moduleKey);
        const isWip = this.isWIP(moduleKey);

        if (targetModule && !isWip) {
            this.currentModule = targetModule;
            try {
                if (typeof targetModule.mount === 'function') {
                    await targetModule.mount({
                        ...this.context,
                        memberId: memberId,
                        memberData: memberData,
                        dispatcher: this
                    });
                }
            } catch (e) {
                console.error(`[ModuleDispatcher] Error mounting module "${moduleKey}":`, e);
            }
        } else {
            // Fallback / WIP Guard for modules without custom packs or in WIP status
            console.log(`[ModuleDispatcher] Module "${moduleKey}" handled as WIP/Fallback.`);
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

        // Broadcast module switched
        if (window.EventBus && window.APP_EVENTS) {
            window.EventBus.emit('dispatcher:switched', {
                key: moduleKey,
                memberId: memberId,
                hasCustomModule: !!targetModule && !isWip,
                isWip: isWip,
                meta: moduleMeta
            });
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
