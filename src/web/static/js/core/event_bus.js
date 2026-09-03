/**
 * AltDP_3rd Central Event Bus (SSOT Event Architecture)
 * Handles cross-pane communication between 1열(Tree), 2열(Canvas), 3열(Form), 4열(Report)
 */
class EventBus {
    constructor() {
        this.listeners = new Map();
    }

    /**
     * Subscribe to an event
     * @param {string} event 
     * @param {Function} callback 
     * @returns {Function} Unsubscribe function
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
        return () => this.off(event, callback);
    }

    /**
     * Unsubscribe from an event
     * @param {string} event 
     * @param {Function} callback 
     */
    off(event, callback) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).delete(callback);
        }
    }

    /**
     * Emit event with payload
     * @param {string} event 
     * @param {*} data 
     */
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(cb => {
                try {
                    cb(data);
                } catch (err) {
                    console.error(`[EventBus] Error in listener for event "${event}":`, err);
                }
            });
        }
    }

    /**
     * Clear all listeners for an event or all events
     * @param {string} [event] 
     */
    clear(event) {
        if (event) {
            this.listeners.delete(event);
        } else {
            this.listeners.clear();
        }
    }
}

// Global Singleton Instance
window.EventBus = new EventBus();

// Standard Event Constants
window.APP_EVENTS = {
    MEMBER_SELECTED: 'member:selected',
    MEMBER_ADDED: 'member:added',
    MEMBER_DELETED: 'member:deleted',
    MEMBER_DUPLICATED: 'member:duplicated',
    PARAM_CHANGED: 'param:changed',
    CALCULATION_DONE: 'calc:done',
    CANVAS_REDRAW: 'canvas:redraw',
    UNIT_CHANGED: 'unit:changed',
    REPORT_MODE_CHANGED: 'report:mode_changed'
};
