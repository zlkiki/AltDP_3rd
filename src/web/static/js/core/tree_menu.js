/**
 * AltDP_3rd TreeMenu Component (1열 WorkTree 1:1 이식)
 * Implements 6 top-level categories and strictly ordered original module lists
 */
class TreeMenu {
    constructor() {
        this.container = null;
        this.activeCategory = 'rc';
        this.activeModule = 'rc_beam';
        this.activeMemberId = null;
        this.currentLevel = 3;

        // 원본 6대 탭 및 모듈 순서 완벽 고정
        this.ORIGINAL_CATEGORIES = [
            { id: 'rc', name: '콘크리트(RCS)', icon: '🧱' },
            { id: 'steel', name: '철골(STEEL)', icon: '🏗️' },
            { id: 'src', name: '합성부재(SRC)', icon: '🏛️' },
            { id: 'alu', name: '알루미늄(ALU)', icon: '📐' },
            { id: 'rfm', name: '보강(RFM)', icon: '🛡️' },
            { id: 'option', name: '설정/하중(Option)', icon: '⚙️' }
        ];

        this.ORIGINAL_MODULE_ORDER = {
            rc: [
                { id: 'rc_slab', name: '슬래브', icon: '▦', defaultDim: 't=200' },
                { id: 'rc_beam', name: '보', icon: '▬', defaultDim: '400x600' },
                { id: 'rc_column', name: '기둥', icon: '▮', defaultDim: '500x500' },
                { id: 'gen_column', name: '임의 형상 기둥', icon: '⬟', defaultDim: 'Gen-Sec' },
                { id: 'rc_wall', name: '전단벽', icon: '❚', defaultDim: 't=250' },
                { id: 'combined_wall', name: '이형 벽체', icon: '⫽', defaultDim: 'L/T-Shape' },
                { id: 'basement_wall', name: '지하외벽', icon: '☷', defaultDim: 't=300' },
                { id: 'retaining_wall', name: '옹벽', icon: '⧘', defaultDim: 'H=4.5m' },
                { id: 'anchor_bolt', name: '앵커볼트', icon: '⤋', defaultDim: '4-M24' },
                { id: 'buttress', name: '버트레스', icon: '▲', defaultDim: 't=400' },
                { id: 'rc_stair', name: '계단', icon: '∦', defaultDim: 't=150' },
                { id: 'corbel', name: '코벨 / 브라켓', icon: '⌐', defaultDim: '300x500' },
                { id: 'rc_footing', name: '기초 (독립/복합/줄)', icon: '⨅', defaultDim: '2000x2000' }
            ],
            steel: [
                { id: 'steel_beam', name: '보 / 기둥', icon: '工', defaultDim: 'H-400x200' },
                { id: 'steel_baseplate', name: '주각부', icon: '⌸', defaultDim: 'PL-500x500' },
                { id: 'steel_bolt_conn', name: '볼트 접합부', icon: '⁑', defaultDim: 'F10T M22' },
                { id: 'steel_moment_bolt', name: '모멘트 볼트 접합부', icon: '⩕', defaultDim: 'Split-T' },
                { id: 'steel_crane_girder', name: '크레인 주행보', icon: '☲', defaultDim: 'CR-50t' },
                { id: 'steel_purlin_girt', name: '중도리 / 띠장', icon: '∷', defaultDim: 'C-150x75' },
                { id: 'steel_web_opening', name: '웨브 개공보', icon: '◯', defaultDim: 'Do=250' },
                { id: 'steel_welding', name: '용접', icon: '⧓', defaultDim: 'Fillet 8mm' },
                { id: 'steel_embed_plate', name: '임베디드 플레이트', icon: '⊞', defaultDim: 'PL-300x300' },
                { id: 'steel_stair', name: '계단', icon: '∦', defaultDim: 'Channel' },
                { id: 'steel_corrugated_beam', name: '파형웨브보', icon: '≋', defaultDim: 'CW-600' }
            ],
            src: [
                { id: 'src_beam', name: '합성보', icon: '☵', defaultDim: 'SRC 400x600' },
                { id: 'src_base_plate', name: 'SRC 주각부', icon: '⌹', defaultDim: 'PL-600x600' },
                { id: 'src_column', name: 'SRC 기둥', icon: '⛶', defaultDim: 'SRC 600x600' },
                { id: 'cft_column', name: 'CFT 기둥', icon: '▣', defaultDim: 'CFT □-500' }
            ],
            alu: [
                { id: 'alu_beam_column', name: '알루미늄 보/기둥', icon: '🪟', defaultDim: 'ALU-150x75' },
                { id: 'alu_gen_beam_column', name: '임의형상 보/기둥', icon: '📐', defaultDim: 'ALU-Gen' }
            ],
            rfm: [
                { id: 'rfm_slab', name: 'RC 슬래브 보강', icon: '▤', defaultDim: 'CFRP 1-Ply' },
                { id: 'rfm_beam', name: 'RC 보 보강', icon: '☲', defaultDim: 'Steel-PL 4.5t' },
                { id: 'rfm_column', name: 'RC 기둥 탄소/강판 보강', icon: '▩', defaultDim: 'CFRP Wrap' }
            ],
            option: [
                { id: 'opt_code_mat', name: '설계기준/재료설정', icon: '📜', defaultDim: 'KDS 2022' },
                { id: 'opt_load_comb', name: '하중/하중조합', icon: '⚖️', defaultDim: '1.2D+1.6L' },
                { id: 'opt_sec_db', name: '단면 형강 DB 관리', icon: '🗄️', defaultDim: 'KS D 3503' }
            ]
        };
    }

    init(containerId, pillsContainerId) {
        this.container = document.getElementById(containerId);
        this.pillsContainer = document.getElementById(pillsContainerId);
        if (!this.container) return;

        this._renderCategoryPills();
        this._renderTree();
        this._setupEvents();
    }

    _renderCategoryPills() {
        if (!this.pillsContainer) return;
        this.pillsContainer.innerHTML = '';
        this.ORIGINAL_CATEGORIES.forEach(cat => {
            const btn = document.createElement('button');
            btn.className = `pill-btn ${cat.id === this.activeCategory ? 'active' : ''}`;
            btn.dataset.cat = cat.id;
            btn.innerHTML = `${cat.icon} ${cat.name.split('(')[0]}`;
            btn.title = cat.name;
            btn.addEventListener('click', () => {
                this.setCategory(cat.id);
            });
            this.pillsContainer.appendChild(btn);
        });
    }

    setCategory(catId) {
        if (!this.ORIGINAL_MODULE_ORDER[catId]) return;
        this.activeCategory = catId;
        if (this.pillsContainer) {
            this.pillsContainer.querySelectorAll('.pill-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.cat === catId);
            });
        }
        const modules = this.ORIGINAL_MODULE_ORDER[catId];
        if (modules && modules.length > 0) {
            this.selectModule(modules[0].id);
        }
        this._renderTree();
    }

    selectModule(moduleId) {
        this.activeModule = moduleId;
        this._renderTree();

        if (window.EventBus && window.APP_EVENTS) {
            window.EventBus.emit(window.APP_EVENTS.MEMBER_SELECTED, {
                type: moduleId,
                memberId: this.activeMemberId || `${moduleId.toUpperCase()}-1`
            });
        }
    }

    setLevel(level) {
        this.currentLevel = Math.max(1, Math.min(3, level));
        this._renderTree();
    }

    _renderTree() {
        if (!this.container) return;
        const modules = this.ORIGINAL_MODULE_ORDER[this.activeCategory] || [];
        
        let html = `<div class="tree-menu-root level-${this.currentLevel}">`;
        
        modules.forEach(mod => {
            const isSelected = mod.id === this.activeModule;
            html += `
            <div class="tree-node module-node ${isSelected ? 'selected' : ''}" data-mod-id="${mod.id}">
                <div class="tree-node-content">
                    <span class="tree-node-icon">${mod.icon}</span>
                    <span class="tree-node-title">${mod.name}</span>
                    <span class="tree-node-dim">${mod.defaultDim}</span>
                    <span class="tree-node-badge badge-ok">0.72</span>
                </div>
            </div>`;
        });
        
        html += '</div>';
        this.container.innerHTML = html;

        // Node click and context menu handlers
        this.container.querySelectorAll('.module-node').forEach(node => {
            node.addEventListener('click', () => {
                const modId = node.dataset.modId;
                this.selectModule(modId);
            });

            node.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                const modId = node.dataset.modId;
                if (window.ContextMenu) {
                    window.ContextMenu.show(e.clientX, e.clientY, {
                        type: 'tree_node',
                        moduleId: modId,
                        category: this.activeCategory
                    });
                }
            });
        });
    }

    _setupEvents() {
        // Level button support
        ['btn-tree-lv1', 'btn-tree-lv2', 'btn-tree-lv3'].forEach((btnId, idx) => {
            const el = document.getElementById(btnId);
            if (el) {
                el.addEventListener('click', () => this.setLevel(idx + 1));
            }
        });
    }
}

// Global Singleton Instance
window.TreeMenu = new TreeMenu();
