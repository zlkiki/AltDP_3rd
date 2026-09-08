// web/js/app.js
/**
 * AltDP Member Designer - Master App Orchestrator
 * Integrates ProjectStore, LayoutResizer, MemberManager, FormGenerator, Visual, AutoDesigner, and ResultRenderer
 */

let allModules = [];
let currentCategoryFilter = 'all';
let currentSchema = null;
let debounceTimer = null;
let pinnedModules = JSON.parse(localStorage.getItem('AltDP_favorites') || localStorage.getItem('altdp_pinned_modules') || '[]');

async function initApp() {
    // 1. Initialize Components (Fail-safe isolation)
    try { if (window.ThemeManager) window.ThemeManager.init(); } catch (e) { console.error('[init] ThemeManager failed:', e); }
    try { if (window.LayoutResizer) window.LayoutResizer.init(); } catch (e) { console.error('[init] LayoutResizer failed:', e); }
    try { if (window.MemberManager) window.MemberManager.init(); } catch (e) { console.error('[init] MemberManager failed:', e); }
    try { if (window.GraphicViewport) window.GraphicViewport.init(); } catch (e) { console.error('[init] GraphicViewport failed:', e); }
    try { if (window.ReportEngine) window.ReportEngine.init(); } catch (e) { console.error('[init] ReportEngine failed:', e); }
    try { if (window.ZoomController) window.ZoomController.init(); } catch (e) { console.error('[init] ZoomController failed:', e); }
    try {
        if (window.ModuleDispatcher) {
            window.ModuleDispatcher.init({
                canvas: document.getElementById('canvas-geometry') || document.getElementById('sectionCanvas'),
                pmCanvas: document.getElementById('canvas-mechanics') || document.getElementById('pmChartCanvas'),
                formContainer: document.getElementById('dynamic-form'),
                reportContainer: document.getElementById('result-container')
            });
        }
    } catch (e) { console.error('[init] ModuleDispatcher failed:', e); }
    try {
        if (window.SidebarNav) {
            window.SidebarNav.init({
                containerId: 'module-accordion',
                pillsContainerId: 'sidebar-cat-pills',
                pinBtnId: 'btn-pin-sidebar',
                searchInputId: 'quick-search',
                sidebarId: 'sidebar-nav'
            });
        } else if (window.TreeMenu) {
            window.TreeMenu.init('module-accordion', 'sidebar-cat-pills');
        }
    } catch (e) { console.error('[init] SidebarNav failed:', e); }

    // 2. Setup Controls
    try { setupUnitSelector(); } catch (e) { console.error('[init] setupUnitSelector failed:', e); }
    try { setupSidebarCategoryPills(); } catch (e) { console.error('[init] setupSidebarCategoryPills failed:', e); }
    try { setupTreeLevelButtons(); } catch (e) { console.error('[init] setupTreeLevelButtons failed:', e); }
    try { setupSearch(); } catch (e) { console.error('[init] setupSearch failed:', e); }
    try { setupProjectIO(); } catch (e) { console.error('[init] setupProjectIO failed:', e); }
    try { setupGlobalShortcuts(); } catch (e) { console.error('[init] setupGlobalShortcuts failed:', e); }

    // 3. Subscribe to Store Hydration & Member Events
    if (window.ProjectStore) {
        window.ProjectStore.subscribe((event, payload, state) => {
            if (event === 'HYDRATE_ALL') {
                if (window.LayoutResizer && state.layout) {
                    window.LayoutResizer.applyLayout(state.layout);
                }
                const activeMod = state.activeContext?.moduleKey || 'rc/beam/base';
                selectModule(activeMod);
            } else if (
                event === 'MEMBER_ADDED' || 
                event === 'MEMBER_DELETED' || 
                event === 'MEMBER_DUPLICATED' || 
                event === 'MEMBER_SELECTED' || 
                event === 'MEMBER_UPDATED' || 
                event === 'MEMBER_RESULT_UPDATED' || 
                event === 'MEMBER_INPUTS_UPDATED' || 
                event === 'MEMBER_RENAMED' || 
                event === 'MODULE_CHANGED' || 
                event === 'CALCULATION_DONE'
            ) {
                renderSidebar();
                // Real-time GraphicViewport Sync
                if (window.GraphicViewport) {
                    if (event === 'MEMBER_SELECTED' && payload?.member) {
                        window.GraphicViewport.setMember(payload.member.moduleKey, payload.member.inputs);
                        if (payload.member.results) {
                            window.GraphicViewport.setCalculationResult(payload.member.results);
                        }
                    } else if (event === 'CALCULATION_DONE' && (payload?.results || payload?.result)) {
                        window.GraphicViewport.setCalculationResult(payload.results || payload.result);
                    } else if ((event === 'MEMBER_INPUTS_UPDATED' || event === 'MEMBER_UPDATED') && payload?.inputs) {
                        window.GraphicViewport.updateMemberData(payload.inputs);
                    }
                }
            }
        });
    }

    // 4. Load Backend Modules
    await loadModules();
}

function setupUnitSelector() {
    const sel = document.getElementById('unit-system-select');
    if (!sel || !window.UnitManager) return;

    // Set initial value from UnitManager
    const curSys = window.UnitManager.getCurrentSystem();
    sel.value = curSys.id;

    sel.addEventListener('change', () => {
        const nextSys = sel.value;
        window.UnitManager.setUnitSystem(nextSys);
    });

    // Re-render all 4 quadrants on unit system change
    window.UnitManager.subscribe((nextSys, prevSys) => {
        // 1. Rebase Dynamic Form Inputs & Unit Badges
        const formEl = document.getElementById('dynamic-form');
        if (formEl && window.FormGenerator) {
            window.FormGenerator.rebaseFormInputs(formEl, prevSys, nextSys);
        }

        // 2. Redraw 2D Canvas with updated dimensions & units
        if (window.CanvasRenderer) {
            window.CanvasRenderer.redrawCurrent();
        }

        // 3. Re-render Report & A4 Sheet with localization
        if (window.ProjectStore) {
            const modKey = window.ProjectStore.getState().activeContext.moduleKey;
            const activeMember = window.ProjectStore.getActiveMember(modKey);
            const resultContainer = document.getElementById('result-container');
            if (activeMember && activeMember.result && resultContainer) {
                if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
                    window.ReportEngine.render(resultContainer, activeMember.inputs, activeMember.result, modKey);
                } else if (window.ResultRenderer) {
                    window.ResultRenderer.render(resultContainer, activeMember.result, modKey, activeMember.inputs);
                }
            }
        }

        // 4. Update Member Manager Table summaries
        if (window.MemberManager) {
            window.MemberManager.renderMemberList();
        }
    });
}

function setupSidebarCategoryPills() {
    const pills = document.querySelectorAll('.sidebar-category-pills .pill-btn');
    pills.forEach(btn => {
        btn.addEventListener('click', () => {
            pills.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategoryFilter = btn.dataset.cat;
            renderSidebar();
        });
    });
}

function setupSearch() {
    const searchInput = document.getElementById('quick-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        renderSidebar(query);
    });
}

function setupGlobalShortcuts() {
    window.addEventListener('keydown', (e) => {
        // Ctrl + K -> Focus search
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('quick-search');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        // Ctrl + B is handled centrally in LayoutResizer.bindTopControls()
        // Ctrl + S -> Export project
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
            e.preventDefault();
            if (window.ProjectStore) {
                window.ProjectStore.exportProject();
            }
        }
    });
}

function setupProjectIO() {
    const btnExport = document.getElementById('btn-export-project');
    const btnImport = document.getElementById('btn-import-project');
    const fileImporter = document.getElementById('file-importer');

    if (btnExport) {
        btnExport.addEventListener('click', () => {
            if (window.ProjectStore) {
                window.ProjectStore.exportProject();
            }
        });
    }

    if (btnImport && fileImporter) {
        btnImport.addEventListener('click', () => {
            fileImporter.value = '';
            fileImporter.click();
        });

        fileImporter.addEventListener('change', (e) => {
            const file = e.target.files?.[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                const content = event.target?.result;
                if (content && window.ProjectStore) {
                    const res = window.ProjectStore.importProject(content);
                    if (res.success) {
                        alert("프로젝트가 성공적으로 불러와졌습니다.");
                    } else {
                        alert("프로젝트 불러오기 실패: " + res.error);
                    }
                }
            };
            reader.readAsText(file);
        });
    }
}

async function loadModules() {
    try {
        const res = await fetch('/api/modules');
        const data = await res.json();
        allModules = data.modules || [];
        window.allModules = allModules;
        renderSidebar();

        // Initial default module selection
        selectModule('rc/beam/base');
    } catch (err) {
        console.error('Failed to load modules:', err);
    }
}

function setupTreeLevelButtons() {
    const btnLv1 = document.getElementById('btn-tree-lv1');
    const btnLv2 = document.getElementById('btn-tree-lv2');
    const btnLv3 = document.getElementById('btn-tree-lv3');

    if (btnLv1) btnLv1.addEventListener('click', () => setTreeLevel(1));
    if (btnLv2) btnLv2.addEventListener('click', () => setTreeLevel(2));
    if (btnLv3) btnLv3.addEventListener('click', () => setTreeLevel(3));
}

let collapsedGroups = JSON.parse(localStorage.getItem('altdp_collapsed_groups') || '[]');
let collapsedModules = JSON.parse(localStorage.getItem('altdp_collapsed_modules') || '[]');
let currentTreeLevel = Number(localStorage.getItem('altdp_tree_level') || 2);

function setTreeLevel(level) {
    currentTreeLevel = level;
    localStorage.setItem('altdp_tree_level', level);

    const allGroups = [...new Set(allModules.map(m => m.group)), '_pinned'];
    const allModKeys = allModules.map(m => m.key);

    if (level === 1) {
        // Level 1: 대분류(그룹) 접기 + 모듈 부재 접기
        collapsedGroups = [...allGroups];
        collapsedModules = [...allModKeys];
    } else if (level === 2) {
        // Level 2: 대분류(그룹) 펼치기 + 모듈 부재 접기
        collapsedGroups = [];
        collapsedModules = [...allModKeys];
    } else if (level === 3) {
        // Level 3: 그룹 펼치기 + 모든 모듈의 부재 하위 트리까지 전체 전개
        collapsedGroups = [];
        collapsedModules = [];
    }

    localStorage.setItem('altdp_collapsed_groups', JSON.stringify(collapsedGroups));
    localStorage.setItem('altdp_collapsed_modules', JSON.stringify(collapsedModules));

    // 버튼 활성 상태 업데이트
    [1, 2, 3].forEach(lv => {
        const btn = document.getElementById(`btn-tree-lv${lv}`);
        if (btn) btn.classList.toggle('active', lv === level);
    });

    renderSidebar();
}

function toggleGroupCollapse(grp, e) {
    if (e) e.stopPropagation();
    if (collapsedGroups.includes(grp)) {
        collapsedGroups = collapsedGroups.filter(g => g !== grp);
    } else {
        collapsedGroups.push(grp);
    }
    localStorage.setItem('altdp_collapsed_groups', JSON.stringify(collapsedGroups));
    renderSidebar();
}

function toggleModuleCollapse(modKey, e) {
    if (e) e.stopPropagation();
    if (collapsedModules.includes(modKey)) {
        collapsedModules = collapsedModules.filter(k => k !== modKey);
    } else {
        collapsedModules.push(modKey);
    }
    localStorage.setItem('altdp_collapsed_modules', JSON.stringify(collapsedModules));
    renderSidebar();
}

function togglePin(key, e) {
    if (e) e.stopPropagation();
    if (pinnedModules.includes(key)) {
        pinnedModules = pinnedModules.filter(k => k !== key);
    } else {
        pinnedModules.push(key);
    }
    localStorage.setItem('altdp_pinned_modules', JSON.stringify(pinnedModules));
    renderSidebar();
}

/**
 * 부재 하위 트리 항목 클릭 시 모듈 전환 및 해당 부재 즉시 활성화
 */
async function selectMemberInModule(modKey, memberId) {
    if (!window.ProjectStore) return;
    await selectModule(modKey, memberId);
}

window.selectMemberInModule = selectMemberInModule;
window.selectModule = selectModule;

function renderSidebar(filterQuery = '') {
    if (window.SidebarNav && typeof window.SidebarNav.render === 'function') {
        window.SidebarNav.render(allModules, filterQuery);
        return;
    }

    const container = document.getElementById('module-accordion');
    if (!container) return;
    container.innerHTML = '';

    // 레벨 버튼 활성 클래스 동기화
    [1, 2, 3].forEach(lv => {
        const btn = document.getElementById(`btn-tree-lv${lv}`);
        if (btn) btn.classList.toggle('active', lv === currentTreeLevel);
    });

    const currentModKey = window.ProjectStore ? window.ProjectStore.getState().activeContext.moduleKey : 'rc/beam/base';
    const activeMemberId = window.ProjectStore ? window.ProjectStore.getActiveMember(currentModKey)?.id : null;

    // Helper: 모듈별 부재 하위 트리 생성 (한번도 열리지 않은 모듈은 하위 부재 없음)
    const buildMemberTreeElement = (modKey) => {
        const modData = window.ProjectStore ? window.ProjectStore.state.modules[modKey] : null;
        if (!modData || !modData.members || modData.members.length === 0) return null;

        const members = modData.members;
        const isCollapsed = collapsedModules.includes(modKey);
        const subList = document.createElement('div');
        subList.className = `member-tree-list ${isCollapsed ? 'collapsed' : ''}`;

        members.forEach(m => {
            const isMemActive = (modKey === currentModKey && m.id === activeMemberId);
            const item = document.createElement('div');
            item.className = `member-tree-item ${isMemActive ? 'active' : ''}`;
            
            // DCR 상태 표기 (칩/배경색 제거, 2단계 녹색 OK / 빨간색 NG 글자로만 표기)
            let dcrText = '';
            if (m.result) {
                const dcr = Number(m.result.governing_dcr) || Number(m.result.max_dcr) || Number(m.result.dcr) || 0.0;
                const isPass = (m.result.status === 'OK' || m.result.status === 'PASS') && dcr <= 1.0;
                const verdict = isPass ? 'OK' : 'NG';
                dcrText = `<span class="tree-dcr-text ${isPass ? 'pass' : 'fail'}">${dcr.toFixed(2)} ${verdict}</span>`;
            }

            item.innerHTML = `
                <span class="tree-member-name" title="${m.name}">${m.name}</span>
                ${dcrText}
            `;
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                selectMemberInModule(modKey, m.id);
            });
            subList.appendChild(item);
        });

        return { subList, isCollapsed, count: members.length };
    };

    // 1. Pinned section
    if (!filterQuery && currentCategoryFilter === 'all' && pinnedModules.length > 0) {
        const pinWrap = document.createElement('div');
        const isPinCollapsed = collapsedGroups.includes('_pinned');
        pinWrap.className = `group-section pinned-section ${isPinCollapsed ? 'collapsed' : ''}`;

        const pinHeader = document.createElement('div');
        pinHeader.className = 'group-header';
        pinHeader.innerHTML = `
            <div class="group-header-left">
                <span class="group-arrow">${isPinCollapsed ? '▶' : '▼'}</span>
                <span>⭐ 즐겨찾기 고정</span>
            </div>
            <span class="group-count">(${pinnedModules.length})</span>
        `;
        pinHeader.addEventListener('click', (e) => toggleGroupCollapse('_pinned', e));

        const pinList = document.createElement('div');
        pinList.className = 'module-list';

        pinnedModules.forEach(pkey => {
            const mod = allModules.find(m => m.key === pkey);
            if (mod) {
                const modWrap = document.createElement('div');
                modWrap.className = 'module-tree-node';

                const isModActive = mod.key === currentModKey;
                const treeData = buildMemberTreeElement(mod.key);

                const item = document.createElement('div');
                item.className = `module-item ${isModActive ? 'active' : ''}`;
                
                const arrowHtml = treeData 
                    ? `<span class="mod-tree-arrow" title="부재 목록 접기/펼치기">${treeData.isCollapsed ? '▶' : '▼'}</span>`
                    : '<span class="mod-tree-spacer"></span>';
                const countBadge = treeData && treeData.count > 0 ? `<span class="mod-mem-count">(${treeData.count})</span>` : '';

                item.innerHTML = `
                    <div class="mod-item-left">
                        ${arrowHtml}
                        <span class="mod-icon">⭐</span>
                        <span class="mod-name">${mod.name}</span>
                        ${countBadge}
                    </div>
                    <span class="pin-toggle active" title="고정 해제">★</span>
                `;

                item.addEventListener('click', (e) => {
                    if (e.target.closest('.pin-toggle')) return;
                    if (e.target.closest('.mod-tree-arrow')) {
                        toggleModuleCollapse(mod.key, e);
                        return;
                    }
                    selectModule(mod.key);
                });

                const pinBtn = item.querySelector('.pin-toggle');
                pinBtn.addEventListener('click', (e) => togglePin(mod.key, e));

                modWrap.appendChild(item);
                if (treeData && treeData.subList) {
                    modWrap.appendChild(treeData.subList);
                }
                pinList.appendChild(modWrap);
            }
        });

        pinWrap.appendChild(pinHeader);
        pinWrap.appendChild(pinList);
        container.appendChild(pinWrap);
    }

    // 2. Filter modules
    let filtered = allModules;
    if (filterQuery) {
        filtered = allModules.filter(m =>
            m.name.toLowerCase().includes(filterQuery) ||
            m.key.toLowerCase().includes(filterQuery) ||
            (m.description && m.description.toLowerCase().includes(filterQuery))
        );
    } else if (currentCategoryFilter !== 'all') {
        filtered = allModules.filter(m => m.category === currentCategoryFilter);
    }

    // Group by group
    const groups = {};
    filtered.forEach(m => {
        if (!groups[m.group]) groups[m.group] = [];
        groups[m.group].push(m);
    });

    Object.keys(groups).forEach(grp => {
        const isCollapsed = !filterQuery && collapsedGroups.includes(grp);
        const groupWrap = document.createElement('div');
        groupWrap.className = `group-section ${isCollapsed ? 'collapsed' : ''}`;

        const header = document.createElement('div');
        header.className = 'group-header';
        header.innerHTML = `
            <div class="group-header-left">
                <span class="group-arrow">${isCollapsed ? '▶' : '▼'}</span>
                <span>📁 ${grp.toUpperCase()}</span>
            </div>
            <span class="group-count">(${groups[grp].length})</span>
        `;
        header.addEventListener('click', (e) => toggleGroupCollapse(grp, e));

        const list = document.createElement('div');
        list.className = 'module-list';

        groups[grp].forEach(mod => {
            const modWrap = document.createElement('div');
            modWrap.className = 'module-tree-node';

            const isPinned = pinnedModules.includes(mod.key);
            const isModActive = mod.key === currentModKey;
            const treeData = buildMemberTreeElement(mod.key);

            const item = document.createElement('div');
            item.className = `module-item ${isModActive ? 'active' : ''}`;

            const arrowHtml = treeData 
                ? `<span class="mod-tree-arrow" title="부재 목록 접기/펼치기">${treeData.isCollapsed ? '▶' : '▼'}</span>`
                : '<span class="mod-tree-spacer"></span>';
            const countBadge = treeData && treeData.count > 0 ? `<span class="mod-mem-count">(${treeData.count})</span>` : '';

            item.innerHTML = `
                <div class="mod-item-left">
                    ${arrowHtml}
                    <span class="mod-name">${mod.name}</span>
                    ${countBadge}
                </div>
                <span class="pin-toggle ${isPinned ? 'active' : ''}" title="${isPinned ? '고정 해제' : '상단 고정'}">${isPinned ? '★' : '☆'}</span>
            `;

            item.addEventListener('click', (e) => {
                if (e.target.closest('.pin-toggle')) return;
                if (e.target.closest('.mod-tree-arrow')) {
                    toggleModuleCollapse(mod.key, e);
                    return;
                }
                selectModule(mod.key);
            });

            const pinBtn = item.querySelector('.pin-toggle');
            pinBtn.addEventListener('click', (e) => togglePin(mod.key, e));

            modWrap.appendChild(item);
            if (treeData && treeData.subList) {
                modWrap.appendChild(treeData.subList);
            }
            list.appendChild(modWrap);
        });

        groupWrap.appendChild(header);
        groupWrap.appendChild(list);
        container.appendChild(groupWrap);
    });
}

/**
 * Determines whether the given module key is currently in WIP status
 * @param {string} moduleKey 
 * @returns {boolean}
 */
function isModuleWIP(moduleKey) {
    if (!moduleKey) return false;
    if (window.CatalogManager && typeof window.CatalogManager.getModule === 'function') {
        const m = window.CatalogManager.getModule(moduleKey);
        if (m && m.engine_status === 'WIP') return true;
    }
    if (window.allModules && Array.isArray(window.allModules)) {
        const m = window.allModules.find(item => item.key === moduleKey || item.id === moduleKey);
        if (m && m.engine_status === 'WIP') return true;
    }
    return false;
}
window.isModuleWIP = isModuleWIP;

async function selectModule(key, targetMemberId = null) {
    if (!key) return;
    try {
        if (window.ProjectStore) {
            window.ProjectStore.setActiveModule(key);
            if (targetMemberId) {
                window.ProjectStore.selectMember(key, targetMemberId);
            }
        }

        renderSidebar();

        const parts = key.split('/');
        const cat = parts[0] || 'rc';
        const grp = parts[1] || 'beam';
        const modId = parts[2] || 'base';

        const hasCustomModule = window.ModuleDispatcher && Boolean(window.ModuleDispatcher.resolveModule(key));
        const isWip = !hasCustomModule && isModuleWIP(key);
        let modMeta = null;
        if (window.CatalogManager && typeof window.CatalogManager.getModule === 'function') {
            modMeta = window.CatalogManager.getModule(key);
        }
        if (!modMeta && window.allModules) {
            modMeta = window.allModules.find(m => m.key === key || m.id === key);
        }

        let currentSchema = {};
        try {
            const res = await fetch(`/api/schema/${cat}/${grp}/${modId}`);
            if (res.ok) {
                const data = await res.json();
                currentSchema = data.schema || {};
                if (!modMeta && data.info) {
                    modMeta = data.info;
                }
            } else {
                console.warn(`[App] Schema not found for ${key} (${res.status}), treating as WIP.`);
            }
        } catch (fetchErr) {
            console.warn(`[App] Schema fetch error for ${key}:`, fetchErr);
        }

        // Update Breadcrumb Banner
        const catMap = { rc: 'RC 콘크리트', steel: 'Steel 강구조', pc: 'PC 구조', misc: '기타·상세', src: 'SRC 합성', alu: '알루미늄', rfm: '보수보강' };
        const catName = catMap[cat] || cat.toUpperCase();
        const bannerEl = document.getElementById('stage-breadcrumb-banner');
        if (bannerEl) {
            const modTitle = (modMeta && modMeta.name) || key;
            bannerEl.innerHTML = `
                <span class="bc-cat-tag">${cat.toUpperCase()}</span>
                <span class="bc-sep">›</span>
                <span class="bc-grp-tag">${grp.toUpperCase()}</span>
                <span class="bc-sep">›</span>
                <span class="bc-mod-tag" id="stage-breadcrumb">${modTitle} (${key})</span>
            `;
            bannerEl.title = `${catName} > ${grp} > ${modTitle} (${key})`;
        }

        // Extract default inputs from schema properties
        const defaultInputs = {};
        const props = (currentSchema && currentSchema.properties) || {};
        Object.keys(props).forEach(pk => {
            if (props[pk] && props[pk].default !== undefined) {
                defaultInputs[pk] = props[pk].default;
            }
        });

        // Ensure module exists in store
        if (window.ProjectStore) {
            window.ProjectStore.ensureModule(key, defaultInputs);
            if (targetMemberId) {
                window.ProjectStore.selectMember(key, targetMemberId);
            }
        }

        const formEl = document.getElementById('dynamic-form');

        // Check if module is WIP or has empty schema properties (only for modules without dedicated pack)
        const hasNoProps = !props || Object.keys(props).length === 0;
        if (!hasCustomModule && (isWip || hasNoProps)) {
            // Unmount and cleanly wipe existing form DOM & event listeners
            if (window.ModuleDispatcher && typeof window.ModuleDispatcher.cleanupForm === 'function') {
                window.ModuleDispatcher.cleanupForm(formEl);
            } else if (formEl) {
                formEl.innerHTML = '';
            }

            // Render WIP Informative Card in Left-Sub Form container
            if (window.WIPCardRenderer && formEl) {
                window.WIPCardRenderer.render(formEl, modMeta || { key, name: key, tier: 'Tier 3', engine_status: 'WIP' });
            }

            // Dispatch module switch
            if (window.ModuleDispatcher) {
                window.ModuleDispatcher.switchModule(key, targetMemberId || 'M-1');
            }

            // Render 2D VDraw Canvas WIP Placeholder with dark engineering grid & geometry symbol
            const canvas = document.getElementById('sectionCanvas');
            const pmCanvas = document.getElementById('pmChartCanvas');
            if (pmCanvas) pmCanvas.style.display = 'none';
            if (canvas) {
                canvas.style.display = 'block';
                if (window.Renderer2D && typeof window.Renderer2D.renderWIPCanvas === 'function') {
                    window.Renderer2D.renderWIPCanvas(canvas, modMeta || { key, name: key, tier: 'Tier 3' });
                } else {
                    const ctx = canvas.getContext('2d');
                    if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
                }
            }
            const caption = document.getElementById('canvas-caption');
            if (caption) {
                caption.textContent = `2D VDraw (WIP: ${(modMeta && modMeta.name) || key})`;
            }

            // Render pure white (#ffffff) A4 KDS standard calculation sheet via ReportEngine
            const resultContainer = document.getElementById('result-container');
            if (resultContainer) {
                if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
                    window.ReportEngine.render(resultContainer, {}, { status: 'NOT_YET_IMPLEMENTED', code: 'WIP_MODULE' }, key);
                } else if (window.ResultRenderer && typeof window.ResultRenderer.render === 'function') {
                    window.ResultRenderer.render(
                        resultContainer, 
                        { status: 'NOT_YET_IMPLEMENTED', code: 'WIP_MODULE' }, 
                        key, 
                        {}
                    );
                }
            }

            // Render member list in top panel to keep list interaction safe
            if (window.MemberManager) {
                window.MemberManager.renderMemberList();
            }

            renderSidebar();
            return;
        }

        // Render dynamic form with [Apply], [Check] & [Design] actions
        if (window.FormGenerator && typeof window.FormGenerator.renderForm === 'function') {
            window.FormGenerator.renderForm(
                currentSchema, 
                formEl, 
                onFormChange, 
                () => triggerCalculate(), 
                () => triggerAutoDesign(),
                key,
                () => triggerApply()
            );
        }

        // Notify dispatcher for custom module packs
        if (window.ModuleDispatcher) {
            window.ModuleDispatcher.switchModule(key, targetMemberId || 'M-1');
        }

        // Populate active member inputs into form (do not auto-trigger calculate on module change)
        syncActiveMemberToForm(false);

        // Render member list in top panel
        if (window.MemberManager) {
            window.MemberManager.renderMemberList();
        }

        renderSidebar();
    } catch (err) {
        console.error('Failed in selectModule:', err);
    }
}

/**
 * Syncs the currently active member's inputs from ProjectStore into the dynamic form
 */
window.syncActiveMemberToForm = function (doCalculate = false) {
    if (!window.ProjectStore) return;
    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
    const activeMember = window.ProjectStore.getActiveMember(modKey);
    const formEl = document.getElementById('dynamic-form');

    if (activeMember && activeMember.inputs && formEl && window.FormGenerator) {
        window.FormGenerator.setFormData(formEl, activeMember.inputs);
    }

    // Always update 2D Canvas immediately
    updateCanvasOnly();

    // Trigger calculation or display existing calculation results immediately
    if (doCalculate) {
        triggerCalculate();
    } else {
        const resultContainer = document.getElementById('result-container');
        if (resultContainer) {
            const inputs = activeMember ? activeMember.inputs : {};
            const result = activeMember ? activeMember.result : null;
            if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
                window.ReportEngine.render(resultContainer, inputs, result, modKey);
            } else if (window.ResultRenderer) {
                window.ResultRenderer.render(resultContainer, result, modKey, inputs);
            }
        }
    }
};

/**
 * Real-time update for Canvas only (Do NOT trigger backend calculation until [검토]/[설계] is clicked)
 */
function onFormChange(changedFieldName) {
    if (debounceTimer) {
        clearTimeout(debounceTimer);
    }
    debounceTimer = setTimeout(() => {
        if (window.ProjectStore) {
            const modKey = window.ProjectStore.getState().activeContext.moduleKey;
            const activeMember = window.ProjectStore.getActiveMember(modKey);
            const formEl = document.getElementById('dynamic-form');
            if (activeMember && formEl && window.FormGenerator) {
                const formData = window.FormGenerator.getFormData(formEl);
                window.ProjectStore.updateMemberInputs(modKey, activeMember.id, formData);
            }
        }
        // Redraw 2D Canvas & Vector SVG (Real-time visual feedback)
        updateCanvasOnly();
    }, 50); // 50ms smooth responsiveness for visual feedback
}

function updateCanvasOnly() {
    if (!window.ProjectStore) return;
    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
    if (!modKey) return;

    const formEl = document.getElementById('dynamic-form');
    const formData = window.FormGenerator ? window.FormGenerator.getFormData(formEl) : {};
    const modMeta = allModules.find(m => m.key === modKey) || {};

    // 1. Remove legacy vector-svg-overlay if present to ensure 1단 Canvas is never covered
    const oldOverlay = document.getElementById('vector-svg-overlay');
    if (oldOverlay && oldOverlay.parentNode) {
        oldOverlay.parentNode.removeChild(oldOverlay);
    }

    const isRCBeam = modKey === 'rc/beam/base' || modKey === 'rc_beam' || modKey.includes('beam');
    if (!isRCBeam) {
        const canvas = document.getElementById('sectionCanvas');
        if (canvas && window.CanvasRenderer) {
            window.CanvasRenderer.draw(canvas, modMeta.geomType || 'rc_rect', formData, modKey);
        }
    }

    // Direct 100ms reactive synchronization with GraphicViewport & ModuleDispatcher
    if (window.GraphicViewport && typeof window.GraphicViewport.updateMemberData === 'function') {
        window.GraphicViewport.updateMemberData(formData);
    }
    if (window.ModuleDispatcher && typeof window.ModuleDispatcher.updateMember === 'function') {
        const activeMember = window.ProjectStore.getActiveMember(modKey);
        if (activeMember) {
            window.ModuleDispatcher.updateMember(activeMember.id, formData);
        }
    }
}

window.onFormChange = onFormChange;
window.updateCanvasOnly = updateCanvasOnly;

/**
 * [적용 (Apply)] Action:
 * Saves form inputs into memory (ProjectStore) immediately, updates Canvas & Member List without calling backend API.
 */
function triggerApply() {
    if (!window.ProjectStore) return;
    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
    if (!modKey) return;

    // Safety guard for WIP modules
    if (isModuleWIP(modKey)) {
        const msg = "⚠️ 해당 부재는 원본앱 1:1 전용 서브탭 폼 및 KDS 연산 탑재 준비 중입니다.";
        if (window.showToast) {
            window.showToast(msg, 'warning');
        } else {
            alert(msg);
        }
        return;
    }

    const activeMember = window.ProjectStore.getActiveMember(modKey);
    const formEl = document.getElementById('dynamic-form');
    if (!activeMember || !formEl || !window.FormGenerator) return;

    const formData = window.FormGenerator.getFormData(formEl);
    window.ProjectStore.updateMemberInputs(modKey, activeMember.id, formData);

    // Update 2D Canvas and Member List Table
    updateCanvasOnly();
    if (window.MemberManager) {
        window.MemberManager.renderMemberList();
    }
    renderSidebar();
}

/**
 * Explicit KDS Calculation on [검토] button click
 * Always executes triggerApply() first to guarantee latest form state.
 */
async function triggerCalculate() {
    if (!window.ProjectStore) return;
    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
    if (!modKey) return;

    // Safety guard for WIP modules
    if (isModuleWIP(modKey)) {
        const msg = "⚠️ 해당 부재는 원본앱 1:1 전용 서브탭 폼 및 KDS 연산 탑재 준비 중입니다.";
        if (window.showToast) {
            window.showToast(msg, 'warning');
        } else {
            alert(msg);
        }
        return;
    }

    // 1. Always execute [적용] first to sync memory
    triggerApply();

    const activeMember = window.ProjectStore.getActiveMember(modKey);
    const formEl = document.getElementById('dynamic-form');
    const formData = window.FormGenerator ? window.FormGenerator.getFormData(formEl) : {};

    const [cat, grp, modId] = modKey.split('/');
    const modMeta = allModules.find(m => m.key === modKey) || {};

    // 1. Draw 2D Canvas
    updateCanvasOnly();

    // 2. Call Backend Design Engine
    try {
        const res = await fetch(`/api/design/${cat}/${grp}/${modId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await res.json();
        if (data.success) {
            // Update Store Member Result
            if (activeMember) {
                window.ProjectStore.updateMemberResult(modKey, activeMember.id, data.result);
            }

            // Render Result & Report Sheets (Always Pure White Background via ReportEngine)
            const resultContainer = document.getElementById('result-container');
            if (resultContainer) {
                if (window.ReportEngine && typeof window.ReportEngine.render === 'function') {
                    window.ReportEngine.render(resultContainer, formData, data.result, modKey);
                } else if (window.ResultRenderer) {
                    window.ResultRenderer.render(resultContainer, data.result, modKey, formData);
                }
            }

            // Immediately update Member List Table & Explorer Sidebar
            if (window.MemberManager) {
                window.MemberManager.renderMemberList();
            }
            renderSidebar();
        } else {
            alert("검토 실패: " + (data.error || "입력 파라미터를 확인해 주세요."));
        }
    } catch (err) {
        console.error('Calculation call failed:', err);
    }
}

/**
 * Automatic Optimal Design on [설계] button click
 */
async function triggerAutoDesign() {
    if (!window.ProjectStore || !window.AutoDesigner) return;
    const modKey = window.ProjectStore.getState().activeContext.moduleKey;
    if (!modKey) return;

    // Safety guard for WIP modules
    if (isModuleWIP(modKey)) {
        const msg = "⚠️ 해당 부재는 원본앱 1:1 전용 서브탭 폼 및 KDS 연산 탑재 준비 중입니다.";
        if (window.showToast) {
            window.showToast(msg, 'warning');
        } else {
            alert(msg);
        }
        return;
    }

    // 1. Always execute [적용] first to sync memory
    triggerApply();

    const [cat, grp, modId] = modKey.split('/');
    const formEl = document.getElementById('dynamic-form');
    const formData = window.FormGenerator ? window.FormGenerator.getFormData(formEl) : {};

    const evaluateFn = async (testInputs) => {
        const res = await fetch(`/api/design/${cat}/${grp}/${modId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testInputs)
        });
        const data = await res.json();
        return data.success ? data.result : null;
    };

    const optResult = await window.AutoDesigner.optimize(modKey, formData, evaluateFn);

    if (optResult && optResult.updatedInputs) {
        // Update Form Inputs
        if (window.FormGenerator) {
            window.FormGenerator.setFormData(formEl, optResult.updatedInputs);
        }

        // Update Store
        const activeMember = window.ProjectStore.getActiveMember(modKey);
        if (activeMember) {
            window.ProjectStore.updateMemberInputs(modKey, activeMember.id, optResult.updatedInputs);
        }

        // Trigger KDS Calculation & Report update
        await triggerCalculate();

        // Brief User with message
        if (optResult.message) {
            alert(optResult.message);
        }
    }
}

window.triggerCalculate = triggerCalculate;
window.triggerAutoDesign = triggerAutoDesign;
window.addEventListener('DOMContentLoaded', initApp);


// =========================================================================
// Legacy API & Direct Engine Calling Compatibility Layer (AltDP_3rd Bridge)
// =========================================================================
function calculateRcBeam(data) {
    return fetch('/api/rc/beam', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

function calculateRcColumn(data) {
    return fetch('/api/rc/column', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

function calculateRcWall(data) {
    return fetch('/api/rc/wall', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

function calculateSteelBeam(data) {
    return fetch('/api/steel/beam', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

function calculateCftColumn(data) {
    return fetch('/api/special/cft', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

function calculateRetrofit(data) {
    return fetch('/api/special/retrofit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(res => res.json());
}

// Ensure btnThemeToggle click delegation & Phase 19-5 Advanced Feature Bindings
document.addEventListener('DOMContentLoaded', () => {
    const btnThemeToggle = document.getElementById('btnThemeToggle');
    const actualToggle = document.getElementById('btn-theme-toggle');
    if (btnThemeToggle && actualToggle) {
        btnThemeToggle.addEventListener('click', () => actualToggle.click());
    }

    // 1. 2D CAD DXF Export Button
    const btnDxf = document.getElementById('btn-open-dxf');
    if (btnDxf) {
        btnDxf.addEventListener('click', async () => {
            if (btnDxf.disabled) {
                if (window.showToast) window.showToast('⚠️ CAD 도면 기능은 추후 고도화 예정입니다.', 'info');
                return;
            }
            const state = window.ProjectStore ? window.ProjectStore.getState() : null;
            const currentMem = state?.activeContext?.memberId && state?.members ? state.members[state.activeContext.memberId] : null;
            const b = currentMem?.inputs?.b || 400.0;
            const h = currentMem?.inputs?.h || 600.0;
            const memType = (state?.activeContext?.moduleKey || '').includes('column') ? 'COLUMN' : 'BEAM';
            const name = currentMem?.name || 'M-1';

            try {
                const resp = await fetch(`/api/v1/project/cad/export-dxf?member_type=${memType}&name=${encodeURIComponent(name)}&b=${b}&h=${h}`, {
                    method: 'POST'
                });
                if (!resp.ok) throw new Error('CAD DXF 내보내기 실패');
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${name}_Rebar_Detail.dxf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } catch (err) {
                alert(`CAD DXF 다운로드 중 오류: ${err.message}`);
            }
        });
    }

    // 2. Quantity Takeoff Export Button
    const btnQuantity = document.getElementById('btn-open-quantity');
    if (btnQuantity) {
        btnQuantity.addEventListener('click', () => {
            if (btnQuantity.disabled) {
                if (window.showToast) window.showToast('⚠️ 물량 산출 기능은 추후 고도화 예정입니다.', 'info');
                return;
            }
            window.location.href = '/api/v1/project/quantity/export-excel';
        });
    }

    // 3. 3D P-M Curve Toggle Button
    const btnTogglePm = document.getElementById('btn-toggle-pm');
    if (btnTogglePm) {
        let isPmView = false;
        btnTogglePm.addEventListener('click', () => {
            const secCanvas = document.getElementById('sectionCanvas');
            const pmCanvas = document.getElementById('pmChartCanvas');
            if (!secCanvas || !pmCanvas) return;

            // WIP Guard: Prevent runtime chart errors on WIP modules
            const currentModMeta = window.allModules && window.allModules.find(m => m.key === currentModuleKey);
            const isWip = currentModMeta && (currentModMeta.engine_status === 'WIP' || currentModMeta.hasFullParams === false);
            if (isWip) {
                const toastFn = (window.ToastManager && window.ToastManager.showToast) || (typeof showToast === 'function' ? showToast : null);
                if (toastFn) {
                    toastFn('⚠️ 본 부재는 3D P-M 상관곡선 그래픽 준비 중 (WIP) 상태입니다.', 'warning');
                }
                return;
            }

            isPmView = !isPmView;
            if (isPmView) {
                secCanvas.style.display = 'none';
                pmCanvas.style.display = 'block';
                btnTogglePm.textContent = '📐 2D 단면';
                // Render sample or calculated P-M if renderer available
                if (window.PMChartRenderer) {
                    const pmRenderer = new window.PMChartRenderer('pmChartCanvas');
                    pmRenderer.render({
                        phi_Pn: [3000, 2500, 1800, 1000, 0, -500],
                        phi_Mn: [0, 150, 320, 280, 120, 0],
                        Pu: 1200,
                        Mu: 220
                    });
                }
            } else {
                pmCanvas.style.display = 'none';
                secCanvas.style.display = 'block';
                btnTogglePm.textContent = '📈 3D P-M';
                if (window.CanvasRenderer) window.CanvasRenderer.redrawCurrent();
            }
        });
    }

    // 4. 3D Frame .mgt Import Button
    const btnGen = document.getElementById('btn-import-gen');
    const genInput = document.getElementById('gen-file-importer');
    if (btnGen && genInput) {
        btnGen.addEventListener('click', () => {
            if (btnGen.disabled) {
                if (window.showToast) window.showToast('⚠️ Gen 가져오기 기능은 추후 고도화 예정입니다.', 'info');
                return;
            }
            genInput.click();
        });
        genInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const formData = new FormData();
            formData.append('file', file);
            try {
                const resp = await fetch('/api/v1/interop/mgt/upload', {
                    method: 'POST',
                    body: formData
                });
                const resData = await resp.json();
                if (resp.ok) {
                    alert(`3D 골조 모델 임포트 완료!\n절점: ${resData.total_nodes}개, 요소: ${resData.total_elements}개, 층: ${resData.total_stories}개`);
                } else {
                    alert(`3D 골조 임포트 실패: ${resData.detail || '오류'}`);
                }
            } catch (err) {
                alert(`3D 골조 모델 로드 에러: ${err.message}`);
            }
            genInput.value = '';
        });
    }
});
