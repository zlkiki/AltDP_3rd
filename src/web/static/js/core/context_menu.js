/**
 * AltDP_3rd Tree Context Menu Handler
 * Provides right-click operations: Add, Duplicate, Delete, Rename, Sort
 */
class ContextMenu {
    constructor() {
        this.menuEl = null;
        this.activeContext = null;
        this._initDOM();
    }

    _initDOM() {
        let el = document.getElementById('tree-context-menu');
        if (!el) {
            el = document.createElement('div');
            el.id = 'tree-context-menu';
            el.className = 'app-context-menu';
            el.style.display = 'none';
            document.body.appendChild(el);
        }
        this.menuEl = el;

        document.addEventListener('click', (e) => {
            if (this.menuEl && !this.menuEl.contains(e.target)) {
                this.hide();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hide();
        });
    }

    /**
     * Show context menu at (x, y)
     * @param {number} x 
     * @param {number} y 
     * @param {Object} context 
     */
    show(x, y, context) {
        this.activeContext = context;
        if (!this.menuEl) return;

        this.menuEl.innerHTML = `
            <div class="menu-item" data-action="add">
                <span class="menu-icon">➕</span> 부재 추가
            </div>
            <div class="menu-item" data-action="dup">
                <span class="menu-icon">📋</span> 부재 복제
            </div>
            <div class="menu-item" data-action="rename">
                <span class="menu-icon">✏️</span> 이름 변경
            </div>
            <div class="menu-divider"></div>
            <div class="menu-item" data-action="sort_asc">
                <span class="menu-icon">🔤</span> 오름차순 정렬
            </div>
            <div class="menu-item" data-action="sort_desc">
                <span class="menu-icon">🔡</span> 내림차순 정렬
            </div>
            <div class="menu-divider"></div>
            <div class="menu-item menu-danger" data-action="delete">
                <span class="menu-icon">🗑️</span> 부재 삭제
            </div>
        `;

        this.menuEl.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = item.dataset.action;
                this._handleAction(action);
                this.hide();
            });
        });

        // Boundary adjust
        const menuWidth = 160;
        const menuHeight = 220;
        const posX = (x + menuWidth > window.innerWidth) ? (window.innerWidth - menuWidth - 10) : x;
        const posY = (y + menuHeight > window.innerHeight) ? (window.innerHeight - menuHeight - 10) : y;

        this.menuEl.style.left = `${posX}px`;
        this.menuEl.style.top = `${posY}px`;
        this.menuEl.style.display = 'block';
    }

    hide() {
        if (this.menuEl) {
            this.menuEl.style.display = 'none';
        }
        this.activeContext = null;
    }

    _handleAction(action) {
        if (!this.activeContext) return;
        const { moduleId } = this.activeContext;

        if (action === 'add') {
            if (window.EventBus && window.APP_EVENTS) {
                window.EventBus.emit(window.APP_EVENTS.MEMBER_ADDED, { type: moduleId });
            }
        } else if (action === 'dup') {
            if (window.EventBus && window.APP_EVENTS) {
                window.EventBus.emit(window.APP_EVENTS.MEMBER_DUPLICATED, { type: moduleId });
            }
        } else if (action === 'delete') {
            if (confirm('선택한 부재를 삭제하시겠습니까?')) {
                if (window.EventBus && window.APP_EVENTS) {
                    window.EventBus.emit(window.APP_EVENTS.MEMBER_DELETED, { type: moduleId });
                }
            }
        } else if (action === 'rename') {
            const newName = prompt('새 부재명을 입력하십시오:');
            if (newName && window.EventBus) {
                window.EventBus.emit('member:renamed', { type: moduleId, newName });
            }
        } else if (action === 'sort_asc' || action === 'sort_desc') {
            if (window.EventBus) {
                window.EventBus.emit('tree:sort', { order: action === 'sort_asc' ? 'asc' : 'desc' });
            }
        }
    }
}

// Global Singleton Instance
window.ContextMenu = new ContextMenu();
