// web/js/components/layout_resizer.js
/**
 * 4-Pane Workspace Layout & 4 Independent Resizers Engine (SSOT)
 * 
 * Complies with:
 * - Requirements 21-1 (Phase 21-1)
 * - DOCS 07 Section 1, 2, 5 (Web Application UI/UX Specification)
 * 
 * 4 Independent Resizers:
 * 1. resizer-sidebar-h: Sidebar Width (200px <= W_sb <= 480px, default: 280px)
 * 2. resizer-left-h: Left-Sub Pane Width (20% <= W_sub <= 50% of workspace, default: 380px)
 * 3. resizer-left-v: Pane 1 Member List Height (80px <= H_memb <= 400px, default: 160px)
 * 4. resizer-main-h: Center Graphic <-> Right Report Ratio (25% <= W_center <= 75%, default: 50:50)
 * 
 * Key Features:
 * - PointerLock / Global Dragging (iframe/canvas overlay resilience)
 * - Double persistence: localStorage ('AltDP_layout_ratios') + ProjectStore
 * - One-click Reset (#btn-reset-layout) to golden ratio defaults (< 0.05s)
 * - Responsive window resize clamping & canvas redraw triggers
 */

(function () {
    const STORAGE_KEY = 'AltDP_layout_ratios';

    // Standard Golden Ratio & Geometric Baseline (Requirement 21-1 Sec 2.2)
    const DEFAULT_LAYOUT = {
        sidebarWidth: 280,      // 200px <= W <= 480px
        leftSubWidth: 380,      // 20% <= W <= 50% of workspace
        memberHeight: 160,      // 80px <= H <= 400px
        centerRightRatio: 0.50, // 25% <= ratio <= 75% (50:50)
        viewportStackRatio: 0.50, // 15% <= ratio <= 85% (상단:하단 50:50)
        sidebarCollapsed: false,
        sidebarPinned: true
    };

    class LayoutResizer {
        constructor() {
            this.defaultLayout = { ...DEFAULT_LAYOUT };
            this.currentLayout = this.loadPersistedLayout();

            this.activeResizer = null;
            this.startX = 0;
            this.startY = 0;

            this.startSidebarWidth = 0;
            this.startLeftSubWidth = 0;
            this.startMemberHeight = 0;
            this.startCenterWidth = 0;
            this.startRightWidth = 0;
            this.workspaceWidth = 0;

            this.autoHideTimer = null;
            this._mouseEnteredAfterOpen = false;
            this._smartEventsBound = false;

            this.onPointerMove = this.onPointerMove.bind(this);
            this.onPointerUp = this.onPointerUp.bind(this);
        }

        /**
         * Load layout from localStorage or fallback to default
         */
        loadPersistedLayout() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {
                    const parsed = JSON.parse(saved);
                    return { ...DEFAULT_LAYOUT, ...parsed };
                }
            } catch (err) {
                console.warn("[LayoutResizer] Failed to parse localStorage layout:", err);
            }
            return { ...DEFAULT_LAYOUT };
        }

        /**
         * Save current layout state to localStorage
         */
        savePersistedLayout(layout = this.currentLayout) {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(layout));
                return true;
            } catch (err) {
                console.error("[LayoutResizer] Failed to save layout to localStorage:", err);
                return false;
            }
        }

        // ==========================================
        // DOM Element Accessors (Standard + Legacy Fallback)
        // ==========================================
        getWorkspace() {
            return document.getElementById('main-workspace') || document.getElementById('workspace-body');
        }

        getSidebar() {
            return document.getElementById('sidebar-nav') || document.getElementById('sidebar-navigator');
        }

        getLeftSub() {
            return document.getElementById('left-sub-pane') || document.getElementById('pane-left-sub');
        }

        getMemberList() {
            return document.getElementById('pane-member-list');
        }

        getInputForm() {
            return document.getElementById('pane-input-form');
        }

        getCenterPane() {
            return document.getElementById('center-pane') || document.getElementById('pane-graphic-view');
        }

        getRightPane() {
            return document.getElementById('right-pane') || document.getElementById('pane-right-report');
        }

        getGeomCard() {
            return document.getElementById('viewport-card-geometry');
        }

        getMechCard() {
            return document.getElementById('viewport-card-mechanics');
        }

        // ==========================================
        // Initialization & Event Binding
        // ==========================================
        init() {
            if (this.isInitialized) {
                // Already initialized, re-apply layout and return to prevent duplicate listeners
                this.applyLayout(this.currentLayout);
                return;
            }
            this.isInitialized = true;

            this.bindResizerEvents();
            this.bindTopControls();
            this.bindSidebarSmartEvents();

            // Apply persisted layout immediately
            this.applyLayout(this.currentLayout);

            // Subscribe to ProjectStore if present
            if (window.ProjectStore) {
                window.ProjectStore.subscribe((event, payload, state) => {
                    if (event === 'LAYOUT_RESET' || event === 'STORE_RESET') {
                        this.resetLayout();
                    } else if (event === 'SIDEBAR_TOGGLED' || event === 'SIDEBAR_PIN_CHANGED' || event === 'SIDEBAR_COLLAPSED_CHANGED') {
                        this.applySidebarState(state.layout || this.currentLayout);
                    }
                });
            }

            // Window resize handler with clamping guard
            window.addEventListener('resize', () => {
                this.clampOnWindowResize();
                this.triggerCanvasRedraw();
            });
        }

        bindResizerEvents() {
            if (this._resizersBound) return;
            this._resizersBound = true;

            const sidebarH = document.getElementById('resizer-sidebar-h');
            const leftH = document.getElementById('resizer-left-h');
            const leftV = document.getElementById('resizer-left-v');
            const mainH = document.getElementById('resizer-main-h');
            const centerV = document.getElementById('resizer-center-v');
            const centerV1 = document.getElementById('resizer-center-v1');
            const centerV2 = document.getElementById('resizer-center-v2');

            const attachStart = (el, type) => {
                if (!el) return;
                // Pointer events for robust global tracking
                el.addEventListener('pointerdown', (e) => this.onPointerDown(e, type));
                el.addEventListener('mousedown', (e) => this.onPointerDown(e, type));
            };

            attachStart(sidebarH, 'sidebar-h');
            attachStart(leftH, 'left-h');
            attachStart(leftV, 'left-v');
            attachStart(mainH, 'main-h');
            attachStart(centerV, 'center-v');
            attachStart(centerV1, 'center-v1');
            attachStart(centerV2, 'center-v2');
        }

        bindTopControls() {
            if (this._topControlsBound) return;
            this._topControlsBound = true;

            // Sidebar toggle button (Ctrl+B or header button)
            const toggleBtn = document.getElementById('btn-toggle-sidebar');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toggleSidebar();
                });
            }

            // Keyboard shortcut Ctrl+B
            window.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                    e.preventDefault();
                    this.toggleSidebar();
                }
            });

            // Reset layout button
            const resetBtn = document.getElementById('btn-reset-layout');
            if (resetBtn) {
                resetBtn.addEventListener('click', () => this.resetLayout());
            }

            // Save layout buttons (#btn-save-layout & legacy #btn-save-default)
            const bindSaveBtn = (btn) => {
                if (!btn) return;
                btn.addEventListener('click', () => {
                    this.savePersistedLayout(this.currentLayout);
                    if (window.ProjectStore && typeof window.ProjectStore.saveCurrentAsDefault === 'function') {
                        const curTheme = window.ThemeManager ? window.ThemeManager.getTheme() : 'dark';
                        window.ProjectStore.saveCurrentAsDefault(curTheme);
                    }
                    const origText = btn.innerText;
                    btn.innerText = '✅ 저장됨';
                    btn.style.color = '#10b981';
                    setTimeout(() => {
                        btn.innerText = origText;
                        btn.style.color = '';
                    }, 2000);
                });
            };

            bindSaveBtn(document.getElementById('btn-save-layout'));
            bindSaveBtn(document.getElementById('btn-save-default'));

            // Pin toggle button in sidebar header
            const pinBtn = document.getElementById('btn-pin-sidebar');
            if (pinBtn) {
                pinBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.togglePin();
                });
            }
        }

        togglePin() {
            this.currentLayout.sidebarPinned = !this.currentLayout.sidebarPinned;
            this.savePersistedLayout(this.currentLayout);
            this.applySidebarState(this.currentLayout);
            if (window.ProjectStore && typeof window.ProjectStore.setSidebarPinned === 'function') {
                window.ProjectStore.setSidebarPinned(this.currentLayout.sidebarPinned);
            }
            if (window.SidebarNav) {
                window.SidebarNav.isPinned = this.currentLayout.sidebarPinned;
                if (typeof window.SidebarNav._updatePinBtnUI === 'function') {
                    window.SidebarNav._updatePinBtnUI();
                }
            }
            if (window.showToast) {
                window.showToast(this.currentLayout.sidebarPinned ? "📌 사이드바가 상시 고정되었습니다." : "📍 사이드바 자동 숨김 모드 활성화 (마우스 이탈 시 접힘)", "info");
            }
        }

        bindSidebarSmartEvents() {
            if (this._smartEventsBound) return;
            this._smartEventsBound = true;
            const sidebar = this.getSidebar();
            if (!sidebar) return;

            // When mouse enters sidebar, cancel auto-hide timer and expand if collapsed
            sidebar.addEventListener('mouseenter', () => {
                if (this.autoHideTimer) {
                    clearTimeout(this.autoHideTimer);
                    this.autoHideTimer = null;
                }
                if (window.SidebarNav && window.SidebarNav.autoHideTimer) {
                    clearTimeout(window.SidebarNav.autoHideTimer);
                    window.SidebarNav.autoHideTimer = null;
                }
                this._mouseEnteredAfterOpen = true;
                if (!this.currentLayout.sidebarPinned && this.currentLayout.sidebarCollapsed) {
                    this.currentLayout.sidebarCollapsed = false;
                    this.applySidebarState(this.currentLayout);
                }
            });

            // When mouse leaves sidebar, start 3s countdown to auto-hide if not pinned
            sidebar.addEventListener('mouseleave', () => {
                if (!this.currentLayout.sidebarPinned) {
                    if (!this._mouseEnteredAfterOpen) return;
                    if (this.autoHideTimer) clearTimeout(this.autoHideTimer);
                    this.autoHideTimer = setTimeout(() => {
                        this.currentLayout.sidebarCollapsed = true;
                        this.applySidebarState(this.currentLayout);
                    }, 3000);
                }
            });
        }

        // ==========================================
        // Dragging Lifecycle & PointerLock Engine
        // ==========================================
        onPointerDown(e, type) {
            e.preventDefault();
            this.activeResizer = type;
            this.startX = e.clientX;
            this.startY = e.clientY;

            const ws = this.getWorkspace();
            const sidebar = this.getSidebar();
            const leftSub = this.getLeftSub();
            const memberList = this.getMemberList();
            const centerPane = this.getCenterPane();
            const rightPane = this.getRightPane();
            const geomCard = this.getGeomCard();
            const mechCard = this.getMechCard();

            if (ws) this.workspaceWidth = ws.getBoundingClientRect().width;
            if (sidebar) this.startSidebarWidth = sidebar.getBoundingClientRect().width;
            if (leftSub) this.startLeftSubWidth = leftSub.getBoundingClientRect().width;
            if (memberList) this.startMemberHeight = memberList.getBoundingClientRect().height;
            if (centerPane) this.startCenterWidth = centerPane.getBoundingClientRect().width;
            if (rightPane) this.startRightWidth = rightPane.getBoundingClientRect().width;
            if (geomCard) this.startGeomHeight = geomCard.getBoundingClientRect().height;
            if (mechCard) this.startMechHeight = mechCard.getBoundingClientRect().height;

            const card1 = document.getElementById('viewport-card-1') || geomCard;
            const card2 = document.getElementById('viewport-card-2') || mechCard;
            const card3 = document.getElementById('viewport-card-3');
            if (card1) this.startCard1Height = card1.getBoundingClientRect().height;
            if (card2) this.startCard2Height = card2.getBoundingClientRect().height;
            if (card3) this.startCard3Height = card3.getBoundingClientRect().height;

            const isRowResize = (type === 'left-v' || type === 'center-v' || type === 'center-v1' || type === 'center-v2');
            document.body.classList.add(isRowResize ? 'resizing-row' : 'resizing-col');

            window.addEventListener('pointermove', this.onPointerMove, { passive: false });
            window.addEventListener('pointerup', this.onPointerUp);
            window.addEventListener('mousemove', this.onPointerMove, { passive: false });
            window.addEventListener('mouseup', this.onPointerUp);
        }

        onPointerMove(e) {
            if (!this.activeResizer) return;
            e.preventDefault();

            const deltaX = e.clientX - this.startX;
            const deltaY = e.clientY - this.startY;

            if (this.activeResizer === 'sidebar-h') {
                // Resizer 1: Sidebar-Horizontal (200px <= W <= 480px)
                const newW = Math.max(200, Math.min(480, Math.round(this.startSidebarWidth + deltaX)));
                this.currentLayout.sidebarWidth = newW;
                const sidebar = this.getSidebar();
                if (sidebar && !this.currentLayout.sidebarCollapsed) {
                    sidebar.style.width = `${newW}px`;
                    sidebar.style.minWidth = `${newW}px`;
                    sidebar.style.flex = `0 0 ${newW}px`;
                }
            } else if (this.activeResizer === 'left-h') {
                // Resizer 3: Left-Horizontal (Left-Sub Width: 20% <= W <= 50% of workspace, min 320px for form usability)
                const ws = this.getWorkspace();
                const totalW = ws ? ws.getBoundingClientRect().width : (this.workspaceWidth || 1200);
                const minW = Math.max(320, Math.round(totalW * 0.20));
                const maxW = Math.round(totalW * 0.50);
                const newW = Math.max(minW, Math.min(maxW, Math.round(this.startLeftSubWidth + deltaX)));

                this.currentLayout.leftSubWidth = newW;
                const leftSub = this.getLeftSub();
                if (leftSub) {
                    leftSub.style.width = `${newW}px`;
                    leftSub.style.minWidth = `${minW}px`;
                    leftSub.style.flex = `0 0 ${newW}px`;
                }
            } else if (this.activeResizer === 'left-v') {
                // Resizer 2: Left-Vertical (Member List Height: 80px <= H <= 400px)
                const newH = Math.max(80, Math.min(400, Math.round(this.startMemberHeight + deltaY)));
                this.currentLayout.memberHeight = newH;
                const memberList = this.getMemberList();
                if (memberList) {
                    memberList.style.height = `${newH}px`;
                    memberList.style.minHeight = '80px';
                    memberList.style.flex = `0 0 ${newH}px`;
                }
            } else if (this.activeResizer === 'main-h') {
                // Resizer 4: Main-Horizontal (Center <-> Right Ratio: 25% <= ratio <= 75%)
                const totalCR = this.startCenterWidth + this.startRightWidth;
                if (totalCR > 50) {
                    const minCenterW = Math.round(totalCR * 0.25);
                    const maxCenterW = Math.round(totalCR * 0.75);
                    const newCenterW = Math.max(minCenterW, Math.min(maxCenterW, Math.round(this.startCenterWidth + deltaX)));
                    const ratio = Number((newCenterW / totalCR).toFixed(3));

                    this.currentLayout.centerRightRatio = ratio;
                    const centerPane = this.getCenterPane();
                    const rightPane = this.getRightPane();
                    if (centerPane && rightPane) {
                        centerPane.style.flex = `${ratio} 1 0%`;
                        rightPane.style.flex = `${(1 - ratio).toFixed(3)} 1 0%`;
                    }
                }
            } else if (this.activeResizer === 'center-v') {
                // Resizer 5: Center-Vertical (Pane 3 상하 2단 분할: 15% <= ratio <= 85%)
                const totalH = this.startGeomHeight + this.startMechHeight;
                if (totalH > 100) {
                    const minGeomH = Math.max(80, Math.round(totalH * 0.15));
                    const maxGeomH = Math.round(totalH * 0.85);
                    const newGeomH = Math.max(minGeomH, Math.min(maxGeomH, Math.round(this.startGeomHeight + deltaY)));
                    const ratio = Number((newGeomH / totalH).toFixed(3));

                    this.currentLayout.viewportStackRatio = ratio;
                    const geomCard = this.getGeomCard();
                    const mechCard = this.getMechCard();
                    if (geomCard && mechCard) {
                        geomCard.style.flex = `${ratio} 1 0%`;
                        mechCard.style.flex = `${(1 - ratio).toFixed(3)} 1 0%`;
                    }
                }
            } else if (this.activeResizer === 'center-v1') {
                const card1 = document.getElementById('viewport-card-1') || this.getGeomCard();
                if (card1) {
                    const newH = Math.max(100, Math.round(this.startCard1Height + deltaY));
                    card1.style.height = `${newH}px`;
                    card1.style.flex = `0 0 ${newH}px`;
                }
            } else if (this.activeResizer === 'center-v2') {
                const card2 = document.getElementById('viewport-card-2') || this.getMechCard();
                if (card2) {
                    const newH = Math.max(100, Math.round(this.startCard2Height + deltaY));
                    card2.style.height = `${newH}px`;
                    card2.style.flex = `0 0 ${newH}px`;
                }
            }

            this.triggerCanvasRedraw();
        }

        onPointerUp() {
            if (!this.activeResizer) return;

            document.body.classList.remove('resizing-col', 'resizing-row');
            window.removeEventListener('pointermove', this.onPointerMove);
            window.removeEventListener('pointerup', this.onPointerUp);
            window.removeEventListener('mousemove', this.onPointerMove);
            window.removeEventListener('mouseup', this.onPointerUp);

            this.activeResizer = null;

            // Commit to localStorage
            this.savePersistedLayout(this.currentLayout);

            // Sync with ProjectStore if available
            if (window.ProjectStore && typeof window.ProjectStore.setLayout === 'function') {
                window.ProjectStore.setLayout({
                    sidebarWidth: this.currentLayout.sidebarWidth,
                    leftSubWidth: this.currentLayout.leftSubWidth,
                    memberHeight: this.currentLayout.memberHeight,
                    centerRightRatio: this.currentLayout.centerRightRatio,
                    sidebarPinned: this.currentLayout.sidebarPinned,
                    sidebarCollapsed: this.currentLayout.sidebarCollapsed
                });
            }

            this.triggerCanvasRedraw();
        }

        // ==========================================
        // Layout Application & Clamping
        // ==========================================
        applyLayout(layout) {
            if (!layout) return;
            const {
                sidebarWidth = DEFAULT_LAYOUT.sidebarWidth,
                leftSubWidth = DEFAULT_LAYOUT.leftSubWidth,
                memberHeight = DEFAULT_LAYOUT.memberHeight,
                centerRightRatio = DEFAULT_LAYOUT.centerRightRatio,
                viewportStackRatio = DEFAULT_LAYOUT.viewportStackRatio,
                sidebarCollapsed = false,
                sidebarPinned = true
            } = layout;

            this.currentLayout = {
                sidebarWidth: Math.max(200, Math.min(480, sidebarWidth)),
                leftSubWidth: Math.max(240, leftSubWidth),
                memberHeight: Math.max(80, Math.min(400, memberHeight)),
                centerRightRatio: Math.max(0.25, Math.min(0.75, centerRightRatio)),
                viewportStackRatio: Math.max(0.15, Math.min(0.85, viewportStackRatio !== undefined ? viewportStackRatio : 0.50)),
                sidebarCollapsed: Boolean(sidebarCollapsed),
                sidebarPinned: sidebarPinned !== false
            };

            const sidebar = this.getSidebar();
            const leftSub = this.getLeftSub();
            const memberList = this.getMemberList();
            const centerPane = this.getCenterPane();
            const rightPane = this.getRightPane();
            const geomCard = this.getGeomCard();
            const mechCard = this.getMechCard();

            if (sidebar) {
                sidebar.style.width = `${this.currentLayout.sidebarWidth}px`;
                sidebar.style.minWidth = `${this.currentLayout.sidebarWidth}px`;
                sidebar.style.flex = `0 0 ${this.currentLayout.sidebarWidth}px`;
            }

            if (leftSub) {
                leftSub.style.width = `${this.currentLayout.leftSubWidth}px`;
                leftSub.style.flex = `0 0 ${this.currentLayout.leftSubWidth}px`;
            }

            if (memberList) {
                memberList.style.height = `${this.currentLayout.memberHeight}px`;
                memberList.style.flex = `0 0 ${this.currentLayout.memberHeight}px`;
            }

            if (centerPane && rightPane) {
                const ratio = this.currentLayout.centerRightRatio;
                centerPane.style.flex = `${ratio} 1 0%`;
                rightPane.style.flex = `${(1 - ratio).toFixed(3)} 1 0%`;
            }

            if (geomCard && mechCard) {
                const vRatio = this.currentLayout.viewportStackRatio;
                geomCard.style.flex = `${vRatio} 1 0%`;
                mechCard.style.flex = `${(1 - vRatio).toFixed(3)} 1 0%`;
            }

            this.applySidebarState(this.currentLayout);
            this.triggerCanvasRedraw();
        }

        applySidebarState(layout) {
            const sidebar = this.getSidebar();
            const toggleBtn = document.getElementById('btn-toggle-sidebar');
            const pinBtn = document.getElementById('btn-pin-sidebar');
            if (!sidebar) return;

            const isPinned = layout.sidebarPinned !== false;
            if (pinBtn) {
                pinBtn.classList.toggle('pinned', isPinned);
                pinBtn.classList.toggle('unpinned', !isPinned);
                pinBtn.innerText = '📌';
                pinBtn.title = isPinned 
                    ? '📌 사이드바 고정됨 (상시 표시 - 클릭 시 자동 숨김 모드로 전환)' 
                    : '📍 사이드바 자동 숨김 모드 (3초 무조작 시 자동 숨김 - 클릭 시 고정)';
            }

            const resizerSidebar = document.getElementById('resizer-sidebar-h');
            if (layout.sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                sidebar.classList.remove('auto-hidden');
                sidebar.style.width = '0px';
                sidebar.style.minWidth = '0px';
                sidebar.style.maxWidth = '0px';
                sidebar.style.flex = '0 0 0px';
                sidebar.style.display = 'none';
                if (resizerSidebar) resizerSidebar.style.display = 'none';
                if (toggleBtn) toggleBtn.innerHTML = '▶';
            } else {
                sidebar.classList.remove('collapsed');
                sidebar.classList.remove('auto-hidden');
                sidebar.style.display = 'flex';
                sidebar.style.width = `${this.currentLayout.sidebarWidth}px`;
                sidebar.style.minWidth = `${this.currentLayout.sidebarWidth}px`;
                sidebar.style.maxWidth = '';
                sidebar.style.flex = `0 0 ${this.currentLayout.sidebarWidth}px`;
                if (resizerSidebar) resizerSidebar.style.display = 'block';
                if (toggleBtn) toggleBtn.innerHTML = '◀';
            }
        }

        toggleSidebar() {
            const sidebar = this.getSidebar();
            let isCurrentlyHidden = false;
            if (sidebar) {
                isCurrentlyHidden = sidebar.classList.contains('collapsed') || 
                                    sidebar.classList.contains('auto-hidden') || 
                                    sidebar.style.display === 'none' ||
                                    sidebar.offsetWidth === 0;
            } else {
                isCurrentlyHidden = Boolean(this.currentLayout.sidebarCollapsed);
            }

            // Clear any pending auto-hide timer immediately
            if (this.autoHideTimer) {
                clearTimeout(this.autoHideTimer);
                this.autoHideTimer = null;
            }
            if (window.SidebarNav && window.SidebarNav.autoHideTimer) {
                clearTimeout(window.SidebarNav.autoHideTimer);
                window.SidebarNav.autoHideTimer = null;
            }

            // If it was hidden, new state is open (collapsed = false).
            // If it was visible, new state is closed (collapsed = true).
            const willOpen = isCurrentlyHidden;
            this.currentLayout.sidebarCollapsed = !willOpen;
            if (willOpen) {
                // When opening via button, don't auto-hide until user hovers into sidebar and then leaves
                this._mouseEnteredAfterOpen = false;
            }

            this.savePersistedLayout(this.currentLayout);
            this.applySidebarState(this.currentLayout);
            if (window.ProjectStore && typeof window.ProjectStore.setSidebarCollapsed === 'function') {
                window.ProjectStore.setSidebarCollapsed(this.currentLayout.sidebarCollapsed);
            }
            this.triggerCanvasRedraw();
        }

        resetLayout() {
            this.currentLayout = { ...DEFAULT_LAYOUT };
            this.savePersistedLayout(this.currentLayout);
            this.applyLayout(this.currentLayout);
            if (window.ProjectStore && typeof window.ProjectStore.setLayout === 'function') {
                window.ProjectStore.setLayout({ ...DEFAULT_LAYOUT });
            }
        }

        clampOnWindowResize() {
            const ws = this.getWorkspace();
            if (!ws) return;
            const totalW = ws.getBoundingClientRect().width;
            const maxLeftSub = Math.round(totalW * 0.50);
            if (this.currentLayout.leftSubWidth > maxLeftSub) {
                this.currentLayout.leftSubWidth = Math.max(240, maxLeftSub);
                const leftSub = this.getLeftSub();
                if (leftSub) {
                    leftSub.style.width = `${this.currentLayout.leftSubWidth}px`;
                    leftSub.style.flex = `0 0 ${this.currentLayout.leftSubWidth}px`;
                }
            }
        }

        triggerCanvasRedraw() {
            if (window.CanvasRenderer && typeof window.CanvasRenderer.redrawCurrent === 'function') {
                window.CanvasRenderer.redrawCurrent();
            }
            if (window.GraphicViewport && typeof window.GraphicViewport.redrawAll === 'function') {
                window.GraphicViewport.redrawAll();
            }
        }
    }

    // Global Singleton Export
    window.LayoutResizer = new LayoutResizer();

    // Auto-init upon DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window.LayoutResizer.init());
    } else {
        window.LayoutResizer.init();
    }
})();
