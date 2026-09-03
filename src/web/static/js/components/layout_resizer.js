// web/js/components/layout_resizer.js
/**
 * 4-Split Draggable Resizer & Workspace Layout Controller
 * - Independent panel resizing (Prevents unintended coupled movement)
 * - Smart Sidebar: Auto-hides after 3s inactivity / mouseleave when unpinned
 * - Pin toggle with mouse hover tooltip
 */

(function () {
    class LayoutResizer {
        constructor() {
            this.activeResizer = null;
            this.startX = 0;
            this.startY = 0;
            this.startLeftWidth = 0;
            this.startRightWidth = 0;
            this.startSubWidth = 0;
            this.startGraphicWidth = 0;
            this.startMemberHeight = 0;
            this.startInputHeight = 0;
            this.autoHideTimer = null;

            this.onMouseMove = this.onMouseMove.bind(this);
            this.onMouseUp = this.onMouseUp.bind(this);
        }

        init() {
            this.bindResizerEvents();
            this.bindTopControls();
            this.bindSidebarSmartEvents();
            
            // Subscribe to store layout changes & hydrate
            if (window.ProjectStore) {
                window.ProjectStore.subscribe((event, payload, state) => {
                    if (event === 'LAYOUT_CHANGED' || event === 'LAYOUT_RESET' || event === 'HYDRATE_ALL' || event === 'STORE_RESET') {
                        this.applyLayout(state.layout);
                    }
                    if (event === 'SIDEBAR_TOGGLED' || event === 'SIDEBAR_PIN_CHANGED' || event === 'SIDEBAR_COLLAPSED_CHANGED') {
                        this.applySidebarState(state.layout);
                    }
                });

                // Apply initial layout
                this.applyLayout(window.ProjectStore.getLayout());
                this.applySidebarState(window.ProjectStore.getLayout());
            }

            // Window resize handler
            window.addEventListener('resize', () => {
                this.triggerCanvasRedraw();
            });
        }

        bindResizerEvents() {
            const sidebarH = document.getElementById('resizer-sidebar-h');
            const mainH = document.getElementById('resizer-main-h');
            const leftH = document.getElementById('resizer-left-h');
            const leftV = document.getElementById('resizer-left-v');

            if (sidebarH) {
                sidebarH.addEventListener('mousedown', (e) => this.onMouseDown(e, 'sidebar-h'));
            }
            if (mainH) {
                mainH.addEventListener('mousedown', (e) => this.onMouseDown(e, 'main-h'));
            }
            if (leftH) {
                leftH.addEventListener('mousedown', (e) => this.onMouseDown(e, 'left-h'));
            }
            if (leftV) {
                leftV.addEventListener('mousedown', (e) => this.onMouseDown(e, 'left-v'));
            }
        }

        bindTopControls() {
            // Sidebar toggle button
            const toggleBtn = document.getElementById('btn-toggle-sidebar');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => {
                    if (window.ProjectStore) {
                        window.ProjectStore.toggleSidebar();
                    }
                });
            }

            // Reset layout button
            const resetBtn = document.getElementById('btn-reset-layout');
            if (resetBtn) {
                resetBtn.addEventListener('click', () => {
                    if (window.ProjectStore) {
                        window.ProjectStore.resetLayout();
                    }
                });
            }

            // Save as default layout and theme button
            const saveDefaultBtn = document.getElementById('btn-save-default');
            if (saveDefaultBtn) {
                saveDefaultBtn.addEventListener('click', () => {
                    if (window.ProjectStore) {
                        const curTheme = window.ThemeManager ? window.ThemeManager.getTheme() : 'dark';
                        const ok = window.ProjectStore.saveCurrentAsDefault(curTheme);
                        if (ok) {
                            const originalText = saveDefaultBtn.innerText;
                            saveDefaultBtn.innerText = '✅ 기본값 저장됨';
                            saveDefaultBtn.style.color = '#10b981';
                            setTimeout(() => {
                                saveDefaultBtn.innerText = originalText;
                                saveDefaultBtn.style.color = '';
                            }, 2000);
                        }
                    }
                });
            }

            // Pin toggle button in sidebar header
            const pinBtn = document.getElementById('btn-pin-sidebar');
            if (pinBtn) {
                pinBtn.addEventListener('click', () => {
                    if (window.ProjectStore) {
                        const currentPinned = window.ProjectStore.getLayout().sidebarPinned !== false;
                        window.ProjectStore.setSidebarPinned(!currentPinned);
                    }
                });
            }
        }

        bindSidebarSmartEvents() {
            const sidebar = document.getElementById('sidebar-navigator');
            if (!sidebar) return;

            // When mouse enters sidebar, cancel auto-hide timer and expand if collapsed
            sidebar.addEventListener('mouseenter', () => {
                if (this.autoHideTimer) {
                    clearTimeout(this.autoHideTimer);
                    this.autoHideTimer = null;
                }
                const layout = window.ProjectStore ? window.ProjectStore.getLayout() : {};
                if (!layout.sidebarPinned && layout.sidebarCollapsed) {
                    if (window.ProjectStore) {
                        window.ProjectStore.setSidebarCollapsed(false);
                    }
                }
            });

            // When mouse leaves sidebar, start 3s countdown to auto-hide if not pinned
            sidebar.addEventListener('mouseleave', () => {
                const layout = window.ProjectStore ? window.ProjectStore.getLayout() : {};
                if (!layout.sidebarPinned) {
                    if (this.autoHideTimer) clearTimeout(this.autoHideTimer);
                    this.autoHideTimer = setTimeout(() => {
                        if (window.ProjectStore) {
                            window.ProjectStore.setSidebarCollapsed(true);
                        }
                    }, 3000);
                }
            });
        }

        onMouseDown(e, type) {
            e.preventDefault();
            this.activeResizer = type;
            this.startX = e.clientX;
            this.startY = e.clientY;

            const sidebar = document.getElementById('sidebar-navigator');
            const paneLeftMain = document.getElementById('pane-left-main');
            const paneRightReport = document.getElementById('pane-right-report');
            const paneLeftSub = document.getElementById('pane-left-sub');
            const paneGraphicView = document.getElementById('pane-graphic-view');
            const paneMemberList = document.getElementById('pane-member-list');
            const paneInputForm = document.getElementById('pane-input-form');

            if (sidebar) {
                this.startSidebarWidth = sidebar.getBoundingClientRect().width;
            }
            if (paneLeftMain && paneRightReport) {
                this.startLeftWidth = paneLeftMain.getBoundingClientRect().width;
                this.startRightWidth = paneRightReport.getBoundingClientRect().width;
            }
            if (paneLeftSub && paneGraphicView) {
                this.startSubWidth = paneLeftSub.getBoundingClientRect().width;
                this.startGraphicWidth = paneGraphicView.getBoundingClientRect().width;
            }
            if (paneMemberList && paneInputForm) {
                this.startMemberHeight = paneMemberList.getBoundingClientRect().height;
                this.startInputHeight = paneInputForm.getBoundingClientRect().height;
            }

            document.body.classList.add(type === 'left-v' ? 'resizing-row' : 'resizing-col');
            window.addEventListener('mousemove', this.onMouseMove);
            window.addEventListener('mouseup', this.onMouseUp);
        }

        onMouseMove(e) {
            if (!this.activeResizer) return;

            const deltaX = e.clientX - this.startX;
            const deltaY = e.clientY - this.startY;

            if (this.activeResizer === 'sidebar-h') {
                const sidebar = document.getElementById('sidebar-navigator');
                if (sidebar) {
                    const newW = Math.max(180, Math.min(500, this.startSidebarWidth + deltaX));
                    sidebar.style.width = `${newW}px`;
                    sidebar.style.minWidth = `${newW}px`;
                }
            } else if (this.activeResizer === 'main-h') {
                const totalW = this.startLeftWidth + this.startRightWidth;
                const newLeftW = Math.max(320, Math.min(totalW - 320, this.startLeftWidth + deltaX));
                const ratio = newLeftW / totalW;

                const paneLeftMain = document.getElementById('pane-left-main');
                const paneRightReport = document.getElementById('pane-right-report');
                if (paneLeftMain && paneRightReport) {
                    paneLeftMain.style.flex = `${ratio} 1 0%`;
                    paneRightReport.style.flex = `${1 - ratio} 1 0%`;
                }
            } else if (this.activeResizer === 'left-h') {
                const totalW = this.startSubWidth + this.startGraphicWidth;
                const newSubW = Math.max(220, Math.min(totalW - 200, this.startSubWidth + deltaX));
                const ratio = newSubW / totalW;

                const paneLeftSub = document.getElementById('pane-left-sub');
                const paneGraphicView = document.getElementById('pane-graphic-view');
                if (paneLeftSub && paneGraphicView) {
                    paneLeftSub.style.flex = `${ratio} 1 0%`;
                    paneGraphicView.style.flex = `${1 - ratio} 1 0%`;
                }
            } else if (this.activeResizer === 'left-v') {
                const totalH = this.startMemberHeight + this.startInputHeight;
                const newMemberH = Math.max(100, Math.min(totalH - 120, this.startMemberHeight + deltaY));
                const ratio = newMemberH / totalH;

                const paneMemberList = document.getElementById('pane-member-list');
                const paneInputForm = document.getElementById('pane-input-form');
                if (paneMemberList && paneInputForm) {
                    paneMemberList.style.flex = `${ratio} 1 0%`;
                    paneInputForm.style.flex = `${1 - ratio} 1 0%`;
                }
            }

            this.triggerCanvasRedraw();
        }

        onMouseUp() {
            if (!this.activeResizer) return;

            document.body.classList.remove('resizing-col', 'resizing-row');
            window.removeEventListener('mousemove', this.onMouseMove);
            window.removeEventListener('mouseup', this.onMouseUp);

            // Compute and commit ratios to ProjectStore
            if (window.ProjectStore) {
                const paneLeftMain = document.getElementById('pane-left-main');
                const paneRightReport = document.getElementById('pane-right-report');
                const paneLeftSub = document.getElementById('pane-left-sub');
                const paneGraphicView = document.getElementById('pane-graphic-view');
                const paneMemberList = document.getElementById('pane-member-list');
                const paneInputForm = document.getElementById('pane-input-form');

                let sidebarWidth = 250;
                let mainSplitRatio = 0.60;
                let leftSplitHRatio = 0.50;
                let leftSplitVRatio = 0.35;

                const sidebar = document.getElementById('sidebar-navigator');
                if (sidebar && !sidebar.classList.contains('collapsed')) {
                    sidebarWidth = Math.round(sidebar.getBoundingClientRect().width);
                }
                if (paneLeftMain && paneRightReport) {
                    const w1 = paneLeftMain.getBoundingClientRect().width;
                    const w2 = paneRightReport.getBoundingClientRect().width;
                    if (w1 + w2 > 0) mainSplitRatio = w1 / (w1 + w2);
                }
                if (paneLeftSub && paneGraphicView) {
                    const w1 = paneLeftSub.getBoundingClientRect().width;
                    const w2 = paneGraphicView.getBoundingClientRect().width;
                    if (w1 + w2 > 0) leftSplitHRatio = w1 / (w1 + w2);
                }
                if (paneMemberList && paneInputForm) {
                    const h1 = paneMemberList.getBoundingClientRect().height;
                    const h2 = paneInputForm.getBoundingClientRect().height;
                    if (h1 + h2 > 0) leftSplitVRatio = h1 / (h1 + h2);
                }

                window.ProjectStore.setLayout({
                    sidebarWidth: sidebarWidth,
                    mainSplitRatio: Number(mainSplitRatio.toFixed(3)),
                    leftSplitHRatio: Number(leftSplitHRatio.toFixed(3)),
                    leftSplitVRatio: Number(leftSplitVRatio.toFixed(3))
                });
            }

            this.activeResizer = null;
            this.triggerCanvasRedraw();
        }

        applyLayout(layout) {
            if (!layout) return;
            const { sidebarWidth = 250, mainSplitRatio = 0.60, leftSplitHRatio = 0.50, leftSplitVRatio = 0.35 } = layout;

            const sidebar = document.getElementById('sidebar-navigator');
            const paneLeftMain = document.getElementById('pane-left-main');
            const paneRightReport = document.getElementById('pane-right-report');
            const paneLeftSub = document.getElementById('pane-left-sub');
            const paneGraphicView = document.getElementById('pane-graphic-view');
            const paneMemberList = document.getElementById('pane-member-list');
            const paneInputForm = document.getElementById('pane-input-form');

            if (sidebar && !sidebar.classList.contains('collapsed') && sidebarWidth >= 180) {
                sidebar.style.width = `${sidebarWidth}px`;
                sidebar.style.minWidth = `${sidebarWidth}px`;
            }
            if (paneLeftMain && paneRightReport) {
                paneLeftMain.style.flex = `${mainSplitRatio} 1 0%`;
                paneRightReport.style.flex = `${1 - mainSplitRatio} 1 0%`;
            }
            if (paneLeftSub && paneGraphicView) {
                paneLeftSub.style.flex = `${leftSplitHRatio} 1 0%`;
                paneGraphicView.style.flex = `${1 - leftSplitHRatio} 1 0%`;
            }
            if (paneMemberList && paneInputForm) {
                paneMemberList.style.flex = `${leftSplitVRatio} 1 0%`;
                paneInputForm.style.flex = `${1 - leftSplitVRatio} 1 0%`;
            }

            this.triggerCanvasRedraw();
        }

        applySidebarState(layout) {
            const sidebar = document.getElementById('sidebar-navigator');
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

            if (layout.sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                if (toggleBtn) toggleBtn.innerHTML = '▶';
            } else {
                sidebar.classList.remove('collapsed');
                if (toggleBtn) toggleBtn.innerHTML = '◀';
            }
        }

        triggerCanvasRedraw() {
            if (window.CanvasRenderer && typeof window.CanvasRenderer.redrawCurrent === 'function') {
                window.CanvasRenderer.redrawCurrent();
            }
        }
    }

    // Global Export
    window.LayoutResizer = new LayoutResizer();
})();
