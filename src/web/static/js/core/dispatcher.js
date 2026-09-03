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

        const targetModule = this.modules.get(moduleKey);
        this.currentMemberId = memberId;

        if (targetModule) {
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
            // Fallback for modules not yet having a specialized pack
            console.warn(`[ModuleDispatcher] Module "${moduleKey}" has no custom pack. Falling back to default.`);
            this.currentModule = null;
        }

        // Broadcast module switched
        if (window.EventBus && window.APP_EVENTS) {
            window.EventBus.emit('dispatcher:switched', {
                key: moduleKey,
                memberId: memberId,
                hasCustomModule: !!targetModule
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
