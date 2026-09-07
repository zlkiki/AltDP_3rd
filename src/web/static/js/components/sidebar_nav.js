/**
 * AltDP_3rd SidebarNav Component (요구사항 21-2 Phase 21-2)
 * 스마트 계층형 모듈 탐색기 사이드바 및 즐겨찾기 시스템
 * 
 * - 8대 카테고리 Pills 탭 필터
 * - 즐겨찾기 (Favorites ⭐) 영속화 ('AltDP_favorites')
 * - 3단계 계층 WorkTree (Level 1 대분류 -> Level 2 모듈 -> Level 3 부재)
 * - DCR 2단계 텍스트 표기 (녹색 OK / 빨간색 NG) 및 NG 클릭 시 계산서 자동 스크롤
 * - 스마트 자동 숨김 (Auto-Hide 3초 타이머) & 고정핀 (📌) 인터랙션
 * - Ctrl + B 단축키 토글 지원
 */

class SidebarNav {
    constructor() {
        this.container = null;
        this.pillsContainer = null;
        this.pinBtn = null;
        this.searchInput = null;
        this.sidebarEl = null;

        // 상태
        this.currentCategory = 'all';
        this.currentSearchQuery = '';
        this.currentTreeLevel = Number(localStorage.getItem('altdp_tree_level') || 2);
        this.isPinned = localStorage.getItem('AltDP_sidebar_pinned') !== 'false'; // default true
        this.autoHideTimer = null;

        // 즐겨찾기 모듈 목록 (사용자가 명시적으로 등록한 모듈만 영속화, 기본값 빈 배열 [])
        const savedFavs = localStorage.getItem('AltDP_favorites') || localStorage.getItem('altdp_pinned_modules');
        try {
            this.favorites = savedFavs ? JSON.parse(savedFavs) : [];
            if (!Array.isArray(this.favorites)) this.favorites = [];
        } catch (_) {
            this.favorites = [];
        }

        // 트리 접힘 상태
        this.collapsedGroups = JSON.parse(localStorage.getItem('altdp_collapsed_groups') || '[]');
        this.collapsedModules = JSON.parse(localStorage.getItem('altdp_collapsed_modules') || '[]');

        // 8대 카테고리 정의
        this.CATEGORIES = [
            { id: 'all', name: '전체', title: '전체 모듈 전개 (61종)' },
            { id: 'fav', name: '⭐ 즐겨찾기', title: '⭐ 즐겨찾기 고정 모듈' },
            { id: 'rc', name: 'RC 콘크리트', title: 'RC 콘크리트 구조' },
            { id: 'steel', name: 'STEEL 강구조', title: 'STEEL 강구조' },
            { id: 'src_pc', name: 'SRC / PC', title: 'SRC 합성 / PC 프리캐스트' },
            { id: 'alu', name: 'ALU 알루미늄', title: 'ALU 알루미늄 구조' },
            { id: 'rfm', name: 'RFM 보강', title: 'RFM 보수보강' },
            { id: 'found_special', name: '기초 / 특수', title: '기초 / 특수 구조' }
        ];
    }

    /**
     * 컴포넌트 초기화
     */
    init(options = {}) {
        this.container = document.getElementById(options.containerId || 'module-accordion');
        this.pillsContainer = document.getElementById(options.pillsContainerId || 'sidebar-cat-pills');
        this.pinBtn = document.getElementById(options.pinBtnId || 'btn-pin-sidebar');
        this.searchInput = document.getElementById(options.searchInputId || 'quick-search');
        this.sidebarEl = document.getElementById(options.sidebarId || 'sidebar-nav') || document.querySelector('.sidebar');

        this._setupCategoryPills();
        this._setupPinAndAutoHide();
        this._setupTreeLevelButtons();
        this._setupSearch();
        this._setupShortcuts();

        // 초기 렌더링
        this.render();
    }

    /**
     * 카테고리 Pills 탭 이벤트 바인딩
     */
    _setupCategoryPills() {
        if (!this.pillsContainer) return;
        const pills = this.pillsContainer.querySelectorAll('.pill-btn');
        pills.forEach(btn => {
            btn.addEventListener('click', () => {
                pills.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.setCategory(btn.dataset.cat || 'all');
            });
        });
    }

    setCategory(catId) {
        this.currentCategory = catId;
        this.render();
    }

    /**
     * 고정핀(📌) 및 마우스 이탈 시 3초 자동 숨김(Auto-Hide) 인터랙션
     */
    _setupPinAndAutoHide() {
        if (this.pinBtn) {
            this._updatePinBtnUI();
            this.pinBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePin();
            });
        }

        if (this.sidebarEl) {
            // 마우스 진입 시 자동 숨김 타이머 취소 및 즉시 전개
            this.sidebarEl.addEventListener('mouseenter', () => {
                if (this.autoHideTimer) {
                    clearTimeout(this.autoHideTimer);
                    this.autoHideTimer = null;
                }
                if (this.sidebarEl.classList.contains('auto-hidden')) {
                    this.sidebarEl.classList.remove('auto-hidden');
                }
            });

            // 마우스 이탈 시 고정핀 OFF 상태이면 3초 후 자동 축소
            this.sidebarEl.addEventListener('mouseleave', () => {
                if (this.isPinned) return; // 고정 ON이면 숨기지 않음
                if (this.autoHideTimer) clearTimeout(this.autoHideTimer);
                this.autoHideTimer = setTimeout(() => {
                    if (!this.isPinned && this.sidebarEl) {
                        this.sidebarEl.classList.add('auto-hidden');
                    }
                }, 3000);
            });
        }
    }

    togglePin() {
        this.isPinned = !this.isPinned;
        localStorage.setItem('AltDP_sidebar_pinned', String(this.isPinned));
        this._updatePinBtnUI();

        if (this.sidebarEl) {
            if (this.isPinned) {
                if (this.autoHideTimer) clearTimeout(this.autoHideTimer);
                this.sidebarEl.classList.remove('auto-hidden');
            } else {
                // 고정 해제 즉시 타이머 가동하지 않고, 마우스 이탈 시 가동
            }
        }

        if (window.ProjectStore && typeof window.ProjectStore.setSidebarPinned === 'function') {
            window.ProjectStore.setSidebarPinned(this.isPinned);
        }
    }

    _updatePinBtnUI() {
        if (!this.pinBtn) return;
        this.pinBtn.classList.toggle('pinned', this.isPinned);
        this.pinBtn.classList.toggle('unpinned', !this.isPinned);
        this.pinBtn.title = this.isPinned ? "사이드바 상시 고정됨 (클릭 시 자동숨김 모드 전환)" : "사이드바 자동숨김 활성화 (클릭 시 상시 고정)";
    }

    /**
     * 트리 레벨 (Level 1, Level 2, Level 3) 버튼 이벤트 바인딩
     */
    _setupTreeLevelButtons() {
        [1, 2, 3].forEach(lv => {
            const btn = document.getElementById(`btn-tree-lv${lv}`);
            if (btn) {
                btn.addEventListener('click', () => this.setTreeLevel(lv));
            }
        });
    }

    setTreeLevel(level) {
        this.currentTreeLevel = level;
        localStorage.setItem('altdp_tree_level', String(level));

        const modules = window.allModules || [];
        const allGroups = [...new Set(modules.map(m => m.group)), '_pinned'];
        const allModKeys = modules.map(m => m.key);

        if (level === 1) {
            // Level 1: 대분류만 (모든 그룹 접음, 모든 모듈 부재 접음)
            this.collapsedGroups = [...allGroups];
            this.collapsedModules = [...allModKeys];
        } else if (level === 2) {
            // Level 2: 단위 모듈까지 (그룹 펼침, 모듈 부재 접음)
            this.collapsedGroups = [];
            this.collapsedModules = [...allModKeys];
        } else if (level === 3) {
            // Level 3: 개별 등록 부재까지 전체 전개 (그룹 펼침, 모듈 펼침)
            this.collapsedGroups = [];
            this.collapsedModules = [];
        }

        localStorage.setItem('altdp_collapsed_groups', JSON.stringify(this.collapsedGroups));
        localStorage.setItem('altdp_collapsed_modules', JSON.stringify(this.collapsedModules));

        this.render();
    }

    /**
     * 검색 필터 연동
     */
    _setupSearch() {
        if (!this.searchInput) return;
        this.searchInput.addEventListener('input', (e) => {
            this.currentSearchQuery = e.target.value.toLowerCase().trim();
            this.render();
        });
    }

    /**
     * Ctrl + B 단축키 토글 지원
     */
    _setupShortcuts() {
        window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                e.preventDefault();
                if (window.LayoutResizer && typeof window.LayoutResizer.toggleSidebar === 'function') {
                    window.LayoutResizer.toggleSidebar();
                } else if (window.ProjectStore && typeof window.ProjectStore.toggleSidebar === 'function') {
                    window.ProjectStore.toggleSidebar();
                }
            }
        });
    }

    /**
     * 모듈 키 정규화 (alias -> canonical key)
     */
    _canonicalKey(key) {
        if (!key) return '';
        const allMods = window.allModules || [];
        const found = allMods.find(m => m.key === key || (m.aliases && m.aliases.includes(key)));
        return found ? found.key : key;
    }

    /**
     * 즐겨찾기 토글 및 영속화
     */
    toggleFavorite(moduleKey, e) {
        if (e) e.stopPropagation();
        const cKey = this._canonicalKey(moduleKey);
        const idx = this.favorites.findIndex(k => this._canonicalKey(k) === cKey);
        if (idx >= 0) {
            this.favorites.splice(idx, 1);
        } else {
            this.favorites.push(cKey);
        }

        localStorage.setItem('AltDP_favorites', JSON.stringify(this.favorites));
        localStorage.setItem('altdp_pinned_modules', JSON.stringify(this.favorites)); // 호환성
        this.render();
    }

    isFavorite(moduleKey) {
        if (!moduleKey || !this.favorites || this.favorites.length === 0) return false;
        const cKey = this._canonicalKey(moduleKey);
        return this.favorites.some(k => this._canonicalKey(k) === cKey);
    }

    /**
     * 그룹 및 모듈 접기/펼치기 토글
     */
    toggleGroup(grp, e) {
        if (e) e.stopPropagation();
        if (this.collapsedGroups.includes(grp)) {
            this.collapsedGroups = this.collapsedGroups.filter(g => g !== grp);
        } else {
            this.collapsedGroups.push(grp);
        }
        localStorage.setItem('altdp_collapsed_groups', JSON.stringify(this.collapsedGroups));
        this.render();
    }

    toggleModule(modKey, e) {
        if (e) e.stopPropagation();
        if (this.collapsedModules.includes(modKey)) {
            this.collapsedModules = this.collapsedModules.filter(k => k !== modKey);
        } else {
            this.collapsedModules.push(modKey);
        }
        localStorage.setItem('altdp_collapsed_modules', JSON.stringify(this.collapsedModules));
        this.render();
    }

    /**
     * 모듈이 지정된 카테고리 필터에 부합하는지 판정
     */
    matchesCategory(mod, cat) {
        if (cat === 'all') return true;
        if (cat === 'fav') return this.isFavorite(mod.key);

        const mCat = (mod.category || '').toLowerCase();
        const mGrp = (mod.group || '').toLowerCase();
        const mDom = (mod.domain || '').toUpperCase();
        const mKey = (mod.key || '').toLowerCase();

        if (cat === 'rc') {
            return (mCat === 'rc' || mDom === 'RC') && !['footing', 'foundation'].includes(mGrp);
        }
        if (cat === 'steel') {
            return mCat === 'steel' || mDom === 'STEEL';
        }
        if (cat === 'src_pc') {
            return mCat === 'src' || mDom === 'SRC' || mCat === 'pc' || mDom === 'PC' || mKey.includes('cft');
        }
        if (cat === 'alu') {
            return mCat === 'alu' || mDom === 'ALU';
        }
        if (cat === 'rfm') {
            return mCat === 'rfm' || mDom === 'RFM';
        }
        if (cat === 'found_special') {
            return (
                ['footing', 'foundation', 'special', 'retaining_wall'].includes(mGrp) ||
                mKey.includes('footing') ||
                mKey.includes('foundation') ||
                mKey.includes('retaining') ||
                mKey.includes('buttress') ||
                mKey.includes('anchor') ||
                mKey.includes('stair') ||
                mKey.includes('corbel')
            );
        }
        return true;
    }

    /**
     * 메인 사이드바 트리 렌더러
     */
    render(modules = null, filterQuery = null) {
        if (!this.container) {
            this.container = document.getElementById('module-accordion');
            if (!this.container) return;
        }

        const allMods = modules || window.allModules || [];
        const query = (filterQuery !== null ? filterQuery : this.currentSearchQuery).toLowerCase();

        this.container.innerHTML = '';

        // 트리 레벨 버튼 활성화 상태 동기화
        [1, 2, 3].forEach(lv => {
            const btn = document.getElementById(`btn-tree-lv${lv}`);
            if (btn) btn.classList.toggle('active', lv === this.currentTreeLevel);
        });

        const currentModKey = window.ProjectStore ? window.ProjectStore.getState().activeContext.moduleKey : 'rc/beam/base';
        const activeMemberId = window.ProjectStore ? window.ProjectStore.getActiveMember(currentModKey)?.id : null;

        // Level 3: 개별 등록 부재 렌더러 빌더
        const buildMemberTree = (modKey) => {
            const modData = window.ProjectStore ? window.ProjectStore.state.modules[modKey] : null;
            if (!modData || !modData.members || modData.members.length === 0) return null;

            const members = modData.members;
            const isCollapsed = this.collapsedModules.includes(modKey);
            const subList = document.createElement('div');
            subList.className = `member-tree-list ${isCollapsed ? 'collapsed' : ''}`;

            members.forEach(m => {
                const isMemActive = (modKey === currentModKey && m.id === activeMemberId);
                const item = document.createElement('div');
                item.className = `member-tree-item ${isMemActive ? 'active' : ''}`;

                // DCR 2단계 글자 표기 (배경 칩 제거, 녹색 OK / 빨간색 NG 글자)
                let dcrHtml = '';
                let isPass = true;
                if (m.result) {
                    const dcr = Number(m.result.governing_dcr) || Number(m.result.max_dcr) || Number(m.result.dcr) || 0.0;
                    isPass = (m.result.status === 'OK' || m.result.status === 'PASS') && dcr <= 1.0;
                    const verdict = isPass ? 'OK' : 'NG';
                    const textClass = isPass ? 'pass' : 'fail';
                    dcrHtml = `<span class="tree-dcr-text ${textClass}" title="DCR: ${dcr.toFixed(3)} (${verdict}) - 클릭 시 부재 전환 및 계산서 위치 이동">${verdict} ${dcr.toFixed(3)}</span>`;
                }

                item.innerHTML = `
                    <span class="tree-member-name" title="${m.name}">${m.name}</span>
                    ${dcrHtml}
                `;

                // 부재 클릭 시 이벤트
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (typeof window.selectMemberInModule === 'function') {
                        window.selectMemberInModule(modKey, m.id);
                    } else if (window.ProjectStore) {
                        window.ProjectStore.setActiveMember(modKey, m.id);
                    }

                    // 불합격(NG) 부재인 경우 우측 계산서의 NG 판정 수식 위치로 자동 스크롤 연동
                    if (!isPass) {
                        setTimeout(() => {
                            this.scrollToReportNG();
                        }, 120);
                    }
                });

                subList.appendChild(item);
            });

            return { subList, isCollapsed, count: members.length };
        };

        // 1. [⭐ 즐겨찾기] 상시 고정 섹션 (검색어가 없고, 카테고리가 fav 또는 all일 때)
        if (!query && (this.currentCategory === 'all' || this.currentCategory === 'fav') && this.favorites.length > 0) {
            const isPinCollapsed = this.collapsedGroups.includes('_pinned');
            const pinWrap = document.createElement('div');
            pinWrap.className = `group-section pinned-section ${isPinCollapsed ? 'collapsed' : ''}`;

            const pinHeader = document.createElement('div');
            pinHeader.className = 'group-header';
            pinHeader.innerHTML = `
                <div class="group-header-left">
                    <span class="group-arrow">${isPinCollapsed ? '▶' : '▼'}</span>
                    <span>⭐ 즐겨찾기 (${this.favorites.length})</span>
                </div>
            `;
            pinHeader.addEventListener('click', (e) => this.toggleGroup('_pinned', e));

            const pinList = document.createElement('div');
            pinList.className = 'module-list';

            this.favorites.forEach(fKey => {
                const mod = allMods.find(m => m.key === fKey || (m.aliases && m.aliases.includes(fKey)));
                if (mod) {
                    const node = this._createModuleTreeNode(mod, currentModKey, buildMemberTree);
                    pinList.appendChild(node);
                }
            });

            pinWrap.appendChild(pinHeader);
            pinWrap.appendChild(pinList);
            this.container.appendChild(pinWrap);
        }

        // 즐겨찾기 전용 탭(fav)인 경우 상시 섹션만 표시 후 리턴
        if (this.currentCategory === 'fav') {
            if (this.favorites.length === 0) {
                const emptyMsg = document.createElement('div');
                emptyMsg.style.cssText = 'padding: 20px; text-align: center; color: var(--text-muted); font-size: 12px;';
                emptyMsg.innerHTML = '⭐ 등록된 즐겨찾기 모듈이 없습니다.<br>모듈 우측의 별표(☆)를 클릭하여 즐겨찾기를 등록하세요.';
                this.container.appendChild(emptyMsg);
            }
            return;
        }

        // 2. 카테고리 및 검색어 필터링
        let filtered = allMods;
        if (query) {
            filtered = allMods.filter(m =>
                m.name.toLowerCase().includes(query) ||
                m.key.toLowerCase().includes(query) ||
                (m.description && m.description.toLowerCase().includes(query))
            );
        } else if (this.currentCategory !== 'all') {
            filtered = allMods.filter(m => this.matchesCategory(m, this.currentCategory));
        }

        // 3. Level 1 (대분류/그룹)별 모듈 묶기
        const groups = {};
        filtered.forEach(m => {
            const grpKey = m.group || 'misc';
            if (!groups[grpKey]) groups[grpKey] = [];
            groups[grpKey].push(m);
        });

        Object.keys(groups).forEach(grp => {
            const isCollapsed = !query && this.collapsedGroups.includes(grp);
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
            header.addEventListener('click', (e) => this.toggleGroup(grp, e));

            const list = document.createElement('div');
            list.className = 'module-list';

            groups[grp].forEach(mod => {
                const node = this._createModuleTreeNode(mod, currentModKey, buildMemberTree);
                list.appendChild(node);
            });

            groupWrap.appendChild(header);
            groupWrap.appendChild(list);
            this.container.appendChild(groupWrap);
        });

        if (filtered.length === 0) {
            const emptyMsg = document.createElement('div');
            emptyMsg.style.cssText = 'padding: 20px; text-align: center; color: var(--text-muted); font-size: 12px;';
            emptyMsg.innerHTML = '🔍 일치하는 모듈이 없습니다.';
            this.container.appendChild(emptyMsg);
        }
    }

    /**
     * Level 2: 단위 모듈 트리 노드 생성
     */
    _createModuleTreeNode(mod, currentModKey, buildMemberTree) {
        const modWrap = document.createElement('div');
        modWrap.className = 'module-tree-node';

        const isPinned = this.isFavorite(mod.key);
        const isModActive = mod.key === currentModKey;
        const treeData = buildMemberTree(mod.key);

        const item = document.createElement('div');
        item.className = `module-item ${isModActive ? 'active' : ''}`;

        const arrowHtml = treeData 
            ? `<span class="mod-tree-arrow" title="부재 목록 접기/펼치기">${treeData.isCollapsed ? '▶' : '▼'}</span>`
            : '<span class="mod-tree-spacer"></span>';
        const countBadge = treeData && treeData.count > 0 ? `<span class="mod-mem-count">(${treeData.count})</span>` : '';

        item.innerHTML = `
            <div class="mod-item-left">
                ${arrowHtml}
                <span class="mod-icon">${mod.engine_status === 'VERIFIED' ? '🔹' : '⚙️'}</span>
                <span class="mod-name" title="${mod.name} (${mod.standard || ''})">${mod.name}</span>
                ${countBadge}
            </div>
            <button class="fav-star-btn ${isPinned ? 'active' : ''}" title="${isPinned ? '즐겨찾기 해제' : '즐겨찾기 추가'}">
                ${isPinned ? '★' : '☆'}
            </button>
        `;

        // 모듈 선택 클릭 이벤트
        item.addEventListener('click', (e) => {
            if (e.target.closest('.fav-star-btn')) return;
            if (e.target.closest('.mod-tree-arrow')) {
                this.toggleModule(mod.key, e);
                return;
            }
            if (typeof window.selectModule === 'function') {
                window.selectModule(mod.key);
            }
        });

        // 즐겨찾기(⭐) 클릭 이벤트
        const starBtn = item.querySelector('.fav-star-btn');
        starBtn.addEventListener('click', (e) => this.toggleFavorite(mod.key, e));

        modWrap.appendChild(item);
        if (treeData && treeData.subList) {
            modWrap.appendChild(treeData.subList);
        }

        return modWrap;
    }

    /**
     * 불합격(NG) 부재 클릭 시 우측 4열 계산서의 NG 판정 수식 위치로 자동 스크롤 연동
     */
    scrollToReportNG() {
        const reportContainer = document.getElementById('result-container');
        if (!reportContainer) return;

        // 계산서 내부의 NG 뱃지나 판정 수식 요소 검색
        const ngEl = reportContainer.querySelector('.badge-ng, .verdict-ng, .status-ng, .sheet-ng, [data-verdict="NG"], [data-verdict="FAIL"]') ||
                     reportContainer.querySelector('.text-danger, .dcr-fail, .fail-row');

        if (ngEl) {
            ngEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // 하이라이트 애니메이션
            ngEl.style.transition = 'box-shadow 0.3s ease';
            ngEl.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.8)';
            setTimeout(() => {
                ngEl.style.boxShadow = '';
            }, 1500);
        }
    }
}

// 전역 싱글톤 인스턴스 등록
window.SidebarNav = new SidebarNav();
