/**
 * AltDP_3rd ModalManager
 * Manages modal lifecycles for Midas Design+ sub-dialogs
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.overlay = null;
        this._initDOM();
    }

    _initDOM() {
        let el = document.getElementById('app-modal-overlay');
        if (!el) {
            el = document.createElement('div');
            el.id = 'app-modal-overlay';
            el.className = 'app-modal-overlay';
            el.style.display = 'none';
            document.body.appendChild(el);
        }
        this.overlay = el;

        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });
    }

    /**
     * Open a modal dialog
     * @param {Object} config 
     * @param {string} config.title - Dialog Title
     * @param {string} config.dialogId - Original Dialog ID (e.g. IDD_RCS_DESIGN_LOAD)
     * @param {string|HTMLElement} config.content - Body content HTML or Node
     * @param {Function} [config.onConfirm] - Callback on OK
     * @param {Function} [config.onCancel] - Callback on Cancel
     * @param {string} [config.width] - Optional modal width
     */
    open(config) {
        if (!this.overlay) return;
        this.activeModal = config;

        const width = config.width || '520px';
        const dialogIdBadge = config.dialogId ? `<span class="dialog-id-tag">[${config.dialogId}]</span>` : '';

        this.overlay.innerHTML = `
            <div class="modal-dialog-box" style="max-width: ${width};">
                <div class="modal-header">
                    <div class="modal-title">
                        <span class="modal-icon">🗂️</span>
                        <span>${config.title}</span>
                        ${dialogIdBadge}
                    </div>
                    <button class="modal-close-btn" id="btn-modal-x" title="닫기">&times;</button>
                </div>
                <div class="modal-body" id="modal-body-content"></div>
                <div class="modal-footer">
                    <button class="modal-btn btn-cancel" id="btn-modal-cancel">취소</button>
                    <button class="modal-btn btn-confirm" id="btn-modal-ok">확인</button>
                </div>
            </div>
        `;

        const bodyContainer = this.overlay.querySelector('#modal-body-content');
        if (typeof config.content === 'string') {
            bodyContainer.innerHTML = config.content;
        } else if (config.content instanceof HTMLElement) {
            bodyContainer.appendChild(config.content);
        }

        // Event bindings
        this.overlay.querySelector('#btn-modal-x').onclick = () => this.close();
        this.overlay.querySelector('#btn-modal-cancel').onclick = () => {
            if (config.onCancel) config.onCancel();
            this.close();
        };
        this.overlay.querySelector('#btn-modal-ok').onclick = () => {
            if (config.onConfirm) {
                const proceed = config.onConfirm(this.overlay);
                if (proceed !== false) this.close();
            } else {
                this.close();
            }
        };

        this.overlay.style.display = 'flex';
    }

    close() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
            this.overlay.innerHTML = '';
        }
        this.activeModal = null;
    }
}

window.ModalManager = new ModalManager();
