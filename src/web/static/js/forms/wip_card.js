/**
 * AltDP_3rd WIP Member Card & Toast Notification Component (Phase 20-3)
 * Docs: docs/07 제1절/제3절, docs/13, 요구사항 20-3
 * 
 * Provides:
 * 1. WIPCardRenderer: Renders modern glassmorphism informative card for WIP/Tier modules.
 * 2. ToastManager / showToast: Bottom-right non-blocking toast notifications for 3-button pipeline guard.
 */

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        const exports = factory();
        root.WIPCardRenderer = exports.WIPCardRenderer;
        root.ToastManager = exports.ToastManager;
        root.showToast = exports.showToast;
    }
}(typeof self !== 'undefined' ? self : this, function () {

    // =========================================================================
    // 1. WIP Card Renderer
    // =========================================================================
    const WIPCardRenderer = {
        /**
         * Resolves planned 1:1 subtabs based on module domain/group/name
         * @param {Object} meta 
         * @returns {string[]}
         */
        getSubtabsForModule(meta = {}) {
            const key = (meta.key || meta.id || '').toLowerCase();
            const group = (meta.group || '').toLowerCase();
            const category = (meta.category || '').toLowerCase();

            if (key.includes('basement_wall')) {
                return ['재질 및 단면', '배근 상세', '설계 하중', '토압/수압 조건'];
            }
            if (group === 'wall' || key.includes('wall')) {
                return ['단면 및 콘크리트', '수직/수평 배근', '경계요소 상세', '설계 전단/모멘트'];
            }
            if (group === 'footing' || key.includes('footing') || key.includes('mat')) {
                return ['기초 제원 및 지반', '상·하부 배근 상세', '기둥 지압 및 하중', '지지력 및 침하 검토'];
            }
            if (group === 'slab' || key.includes('slab')) {
                return ['슬래브 제원/경간', '상·하부 주근/배력근', '설계 하중 및 경계', '처짐/균열 사용성'];
            }
            if (key.includes('baseplate')) {
                return ['베이스플레이트 제원', '앵커볼트/전단키', '설계 축력/모멘트', '기초 콘크리트 지압'];
            }
            if (group === 'connection' || key.includes('connection') || key.includes('joint')) {
                return ['모재 및 연결재', '고장력볼트/용접', '설계 단면력', '기하학적 한계 상태'];
            }
            if (category === 'steel' || group === 'steel') {
                return ['강재 및 단면 규격', '비지지 길이 (Lb)', '설계 휨/전단/축력', '국부 및 횡좌굴 검토'];
            }
            if (category === 'src' || key.includes('src') || key.includes('composite')) {
                return ['콘크리트/강재 제원', '매입 형강 규격', '주철근 및 띠철근', '합성 P-M 상관도'];
            }
            if (category === 'rfm' || key.includes('retrofit')) {
                return ['기존 부재 상태', '보강재(CFRP/강판)', '설계 하중 증분', '계면 부착 응력'];
            }
            if (category === 'alu' || key.includes('alu')) {
                return ['알루미늄 단면 제원', '합금 재료 물성', '설계 하중', '좌굴 및 처짐 사용성'];
            }

            // General Default 4 Subtabs
            return ['재질 및 단면', '배근 및 상세', '설계 하중 조건', 'KDS 기준 검토 옵션'];
        },

        /**
         * Resolves visual styling metadata for each tier
         * @param {string} tier 
         */
        getTierStyle(tier = '') {
            const t = (tier || '').toUpperCase();
            if (t.includes('1')) {
                return {
                    label: 'Tier 1 핵심 플래그십',
                    badgeBg: 'rgba(59, 130, 246, 0.15)',
                    badgeColor: '#60a5fa',
                    borderColor: 'rgba(59, 130, 246, 0.35)',
                    icon: '⭐'
                };
            }
            if (t.includes('2')) {
                return {
                    label: 'Tier 2 실무 주요 부재',
                    badgeBg: 'rgba(16, 185, 129, 0.15)',
                    badgeColor: '#34d399',
                    borderColor: 'rgba(16, 185, 129, 0.35)',
                    icon: '🔷'
                };
            }
            return {
                label: 'Tier 3 특수/상세 모듈',
                badgeBg: 'rgba(245, 158, 11, 0.15)',
                badgeColor: '#fbbf24',
                borderColor: 'rgba(245, 158, 11, 0.35)',
                icon: '🔶'
            };
        },

        /**
         * Renders the WIP informative card inside container
         * @param {HTMLElement|string} container 
         * @param {Object} moduleMeta 
         */
        render(container, moduleMeta = {}) {
            const el = typeof container === 'string' ? document.getElementById(container) : container;
            if (!el) return;

            const name = moduleMeta.name || moduleMeta.id || '미확인 부재';
            const midasDlg = moduleMeta.midas_dlg || 'IDD_RCS_MEMBER_DLG';
            const standard = moduleMeta.standard || 'KDS 14 20 00 / 14 31 00';
            const tier = moduleMeta.tier || 'Tier 2';
            const tierStyle = this.getTierStyle(tier);
            const subtabs = this.getSubtabsForModule(moduleMeta);

            const subtabPillsHtml = subtabs.map(tab => `
                <div class="wip-subtab-pill" style="
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 10px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 6px;
                    font-size: 11px;
                    color: var(--text-secondary, #94a3b8);
                ">
                    <span style="color: var(--color-primary, #38bdf8); font-size: 10px;">▪</span>
                    <span>${tab}</span>
                </div>
            `).join('');

            el.innerHTML = `
                <div class="wip-card-wrapper" style="
                    margin: 8px;
                    padding: 16px;
                    background: rgba(15, 23, 42, 0.65);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    border: 1px solid ${tierStyle.borderColor};
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
                    display: flex;
                    flex-direction: column;
                    gap: 14px;
                    animation: wipCardFadeIn 0.25s ease-out;
                ">
                    <!-- Header with Tier Badge & Status -->
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            gap: 5px;
                            padding: 3px 8px;
                            background: ${tierStyle.badgeBg};
                            color: ${tierStyle.badgeColor};
                            border: 1px solid ${tierStyle.borderColor};
                            border-radius: 6px;
                            font-size: 11px;
                            font-weight: 600;
                            letter-spacing: 0.3px;
                        ">
                            ${tierStyle.icon} ${tierStyle.label}
                        </span>
                        <span style="
                            padding: 2px 7px;
                            background: rgba(239, 68, 68, 0.12);
                            color: #f87171;
                            border: 1px solid rgba(239, 68, 68, 0.25);
                            border-radius: 4px;
                            font-size: 10px;
                            font-weight: 600;
                            text-transform: uppercase;
                        ">
                            WIP (엔진 준비 중)
                        </span>
                    </div>

                    <!-- Member Title & Midas DLG Code -->
                    <div>
                        <div style="
                            font-size: 14px;
                            font-weight: 700;
                            color: var(--text-primary, #f1f5f9);
                            margin-bottom: 4px;
                        ">
                            ${name}
                        </div>
                        <div style="
                            display: inline-flex;
                            align-items: center;
                            gap: 5px;
                            font-family: 'Fira Code', monospace, Consolas;
                            font-size: 10.5px;
                            color: #94a3b8;
                            background: rgba(0, 0, 0, 0.35);
                            padding: 2px 6px;
                            border-radius: 4px;
                            border: 1px solid rgba(255, 255, 255, 0.06);
                        ">
                            <span style="color: #64748b;">DLG:</span>
                            <span style="color: #cbd5e1;">${midasDlg}</span>
                        </div>
                    </div>

                    <!-- Applicable KDS Standard -->
                    <div style="
                        padding: 8px 10px;
                        background: rgba(255, 255, 255, 0.03);
                        border-left: 3px solid var(--color-primary, #38bdf8);
                        border-radius: 0 6px 6px 0;
                    ">
                        <div style="font-size: 10px; color: #64748b; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.5px;">적용 국가건설기준 (KDS)</div>
                        <div style="font-size: 12px; font-weight: 600; color: #e2e8f0;">
                            📘 ${standard}
                        </div>
                    </div>

                    <!-- Planned Subtabs -->
                    <div>
                        <div style="
                            font-size: 10.5px;
                            font-weight: 600;
                            color: var(--text-secondary, #94a3b8);
                            margin-bottom: 6px;
                            display: flex;
                            align-items: center;
                            gap: 4px;
                        ">
                            <span>📋 지원 예정 원본앱 1:1 서브탭</span>
                        </div>
                        <div style="
                            display: flex;
                            flex-wrap: wrap;
                            gap: 6px;
                        ">
                            ${subtabPillsHtml}
                        </div>
                    </div>

                    <!-- Roadmap Notification Banner -->
                    <div style="
                        padding: 10px 12px;
                        background: rgba(56, 189, 248, 0.08);
                        border: 1px dashed rgba(56, 189, 248, 0.25);
                        border-radius: 8px;
                        display: flex;
                        align-items: flex-start;
                        gap: 8px;
                    ">
                        <span style="font-size: 14px; line-height: 1;">🚀</span>
                        <div style="font-size: 11px; line-height: 1.5; color: #bae6fd;">
                            본 부재는 <strong>KDS 수식</strong> 및 <strong>원본앱 1:1 서브탭 전용 폼</strong> 개발 준비 중입니다. 
                            <span style="color: #7dd3fc; display: block; font-size: 10px; margin-top: 2px;">
                                상단 [적용/검토/설계] 액션 실행 시 가드 알림이 제공됩니다.
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }
    };

    // =========================================================================
    // 2. Toast Notification Manager
    // =========================================================================
    const ToastManager = {
        container: null,

        _getOrCreateContainer() {
            if (this.container && document.body.contains(this.container)) {
                return this.container;
            }
            let el = document.getElementById('altdp-toast-container');
            if (!el) {
                el = document.createElement('div');
                el.id = 'altdp-toast-container';
                el.style.position = 'fixed';
                el.style.bottom = '24px';
                el.style.right = '24px';
                el.style.display = 'flex';
                el.style.flexDirection = 'column';
                el.style.gap = '10px';
                el.style.zIndex = '99999';
                el.style.pointerEvents = 'none';
                document.body.appendChild(el);
            }
            this.container = el;
            return el;
        },

        /**
         * Show toast notification in bottom right
         * @param {string} message 
         * @param {'warning'|'info'|'success'|'error'} type 
         * @param {number} durationMs 
         */
        show(message, type = 'warning', durationMs = 3200) {
            const container = this._getOrCreateContainer();

            const toast = document.createElement('div');
            toast.className = `altdp-toast toast-${type}`;
            toast.style.pointerEvents = 'auto';
            toast.style.minWidth = '280px';
            toast.style.maxWidth = '420px';
            toast.style.padding = '12px 16px';
            toast.style.borderRadius = '10px';
            toast.style.fontSize = '12px';
            toast.style.fontWeight = '500';
            toast.style.lineHeight = '1.45';
            toast.style.display = 'flex';
            toast.style.alignItems = 'center';
            toast.style.justifyContent = 'space-between';
            toast.style.gap = '10px';
            toast.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.4)';
            toast.style.backdropFilter = 'blur(12px)';
            toast.style.webkitBackdropFilter = 'blur(12px)';
            toast.style.transform = 'translateY(20px)';
            toast.style.opacity = '0';
            toast.style.transition = 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)';

            let icon = 'ℹ️';
            let bg = 'rgba(15, 23, 42, 0.9)';
            let border = '1px solid rgba(255, 255, 255, 0.15)';
            let color = '#f1f5f9';

            if (type === 'warning') {
                icon = '⚠️';
                bg = 'rgba(30, 25, 15, 0.95)';
                border = '1px solid rgba(245, 158, 11, 0.45)';
                color = '#fef3c7';
            } else if (type === 'error') {
                icon = '🚨';
                bg = 'rgba(35, 15, 15, 0.95)';
                border = '1px solid rgba(239, 68, 68, 0.45)';
                color = '#fee2e2';
            } else if (type === 'success') {
                icon = '✅';
                bg = 'rgba(15, 30, 20, 0.95)';
                border = '1px solid rgba(16, 185, 129, 0.45)';
                color = '#d1fae5';
            }

            toast.style.background = bg;
            toast.style.border = border;
            toast.style.color = color;

            toast.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                    <span style="font-size: 15px; flex-shrink: 0;">${icon}</span>
                    <span>${message}</span>
                </div>
                <button type="button" class="toast-close-btn" style="
                    background: transparent;
                    border: none;
                    color: inherit;
                    opacity: 0.6;
                    cursor: pointer;
                    font-size: 14px;
                    line-height: 1;
                    padding: 2px 4px;
                    border-radius: 4px;
                    transition: opacity 0.15s ease;
                " title="닫기">&times;</button>
            `;

            const closeBtn = toast.querySelector('.toast-close-btn');
            const removeToast = () => {
                toast.style.transform = 'translateY(15px)';
                toast.style.opacity = '0';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 250);
            };

            if (closeBtn) {
                closeBtn.addEventListener('click', removeToast);
                closeBtn.addEventListener('mouseenter', () => { closeBtn.style.opacity = '1'; });
                closeBtn.addEventListener('mouseleave', () => { closeBtn.style.opacity = '0.6'; });
            }

            container.appendChild(toast);

            // Animate in
            requestAnimationFrame(() => {
                toast.style.transform = 'translateY(0)';
                toast.style.opacity = '1';
            });

            // Auto dismiss
            if (durationMs > 0) {
                setTimeout(removeToast, durationMs);
            }

            return toast;
        }
    };

    function showToast(message, type = 'warning', durationMs = 3200) {
        return ToastManager.show(message, type, durationMs);
    }

    return {
        WIPCardRenderer,
        ToastManager,
        showToast
    };
}));
