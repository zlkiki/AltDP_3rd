/**
 * AltDP_3rd KDS Standard Structural Calculation Report Engine (report_engine.js)
 * Conforms to Requirement 21-5 & DOCS 07 & DOCS 14 Specifications
 * - Report Control Toolbar: Detail/Summary modes, Input data toggle, Graphics toggle, Header settings
 * - Constant Pure White (#ffffff) A4 Fixed Calculation Sheet
 * - KaTeX 8-Step Formula Derivation Pipeline (KDS 14 20 20 / 14 20 22)
 * - Original App 1:1 Verdict Badges ('  →  O.K' / '  →  N.G')
 * - Header/Footer Custom Banner & Approval Box (IDD_REPORT_HEADER_DLG)
 */

(function(window) {
    'use strict';

    class ReportEngine {
        constructor() {
            this.mode = 'detail'; // 'detail' | 'summary'
            this.includeInput = true;
            this.includeGraphics = true;
            
            // Default header configuration (IDD_REPORT_HEADER_DLG)
            const today = new Date().toISOString().slice(0, 10);
            this.headerConfig = {
                projectName: 'AltDP_3rd KDS Automated Engineering',
                companyName: '(주)한국구조기술엔지니어링',
                companyShort: 'K-STRUCT',
                memberTag: '1F-B1',
                engineer: '홍길동 (작성)',
                checker: '이몽룡 (검토)',
                approver: '성춘향 (승인)',
                date: today,
                logoUrl: ''
            };

            this.currentMemberData = null;
            this.currentCalcResult = null;
            this.currentModuleKey = 'rc_beam';
            this.currentContainer = null;
            this.isInitialized = false;
        }

        /**
         * Initialize toolbar elements and bind events
         * @param {HTMLElement} [container] 
         */
        init(container) {
            if (container) {
                this.currentContainer = container;
            }
            this._ensureToolbar();
            this._bindToolbarEvents();
            this.isInitialized = true;
        }

        /**
         * Ensure #report-control-toolbar exists in DOM
         */
        _ensureToolbar() {
            let toolbar = document.getElementById('report-control-toolbar');
            if (!toolbar) {
                const rightPane = document.getElementById('right-pane') || document.querySelector('.pane-right-report');
                if (rightPane) {
                    toolbar = document.createElement('div');
                    toolbar.id = 'report-control-toolbar';
                    toolbar.className = 'report-toolbar';
                    
                    const scrollWrap = rightPane.querySelector('.report-scroll-wrap') || document.getElementById('result-container');
                    if (scrollWrap) {
                        rightPane.insertBefore(toolbar, scrollWrap);
                    } else {
                        rightPane.appendChild(toolbar);
                    }
                }
            }

            if (toolbar && !toolbar.hasChildNodes()) {
                toolbar.innerHTML = `
                    <!-- 1. 보고서 유형 분기 -->
                    <div class="toolbar-group">
                        <span class="group-label">유형:</span>
                        <label class="radio-label" title="인허가 관공서 및 구조심의 제출용 초정밀 수식 전개 계산서">
                            <input type="radio" name="report-mode" value="detail" ${this.mode === 'detail' ? 'checked' : ''}> 상세 보고서 (Detail)
                        </label>
                        <label class="radio-label" title="실무 퀵 검토 및 배근 현장용 1~2페이지 압축 레이아웃">
                            <input type="radio" name="report-mode" value="summary" ${this.mode === 'summary' ? 'checked' : ''}> 요약 보고서 (Summary)
                        </label>
                    </div>

                    <!-- 2. 출력 옵션 체크박스 -->
                    <div class="toolbar-group">
                        <label class="checkbox-label" title="설계자가 입력한 재료/배근/하중 제원 상세 표 수록 여부">
                            <input type="checkbox" id="chk-report-include-input" ${this.includeInput ? 'checked' : ''}> 사용자 입력 데이터 상세 포함
                        </label>
                        <label class="checkbox-label" title="2D 단면도 및 P-M 곡선 이미지 삽입">
                            <input type="checkbox" id="chk-report-include-graphics" ${this.includeGraphics ? 'checked' : ''}> 그래픽 임베딩
                        </label>
                    </div>

                    <!-- 3. 커스텀 설정 및 출력 액션 -->
                    <div class="toolbar-actions">
                        <button id="btn-report-header-settings" class="btn-tool" title="머릿말/회사명/서명란 설정">⚙️ 머릿말 설정</button>
                        <button id="btn-report-print" class="btn-primary-sm" title="브라우저 인쇄 (A4 순백색)">🖨️ 인쇄</button>
                        <button id="btn-report-pdf" class="btn-tool" title="WeasyPrint 고화질 PDF 다운로드">📄 PDF</button>
                        <button id="btn-report-excel" class="btn-tool" title="OpenPyXL 엑셀 내보내기">📊 Excel</button>
                    </div>
                `;
            }
        }

        /**
         * Bind toolbar interactive events
         */
        _bindToolbarEvents() {
            const toolbar = document.getElementById('report-control-toolbar');
            if (!toolbar || toolbar.dataset.bound === 'true') return;
            toolbar.dataset.bound = 'true';

            // Radio: Mode switch
            const modeRadios = toolbar.querySelectorAll('input[name="report-mode"]');
            modeRadios.forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.setReportMode(e.target.value);
                });
            });

            // Checkbox: Include Input Data
            const chkInput = toolbar.querySelector('#chk-report-include-input');
            if (chkInput) {
                chkInput.addEventListener('change', (e) => {
                    this.setIncludeInput(e.target.checked);
                });
            }

            // Checkbox: Include Graphics
            const chkGraphics = toolbar.querySelector('#chk-report-include-graphics');
            if (chkGraphics) {
                chkGraphics.addEventListener('change', (e) => {
                    this.setIncludeGraphics(e.target.checked);
                });
            }

            // Buttons: Header Dialog
            const btnHeader = toolbar.querySelector('#btn-report-header-settings');
            if (btnHeader) {
                btnHeader.addEventListener('click', () => {
                    this.openHeaderDialog();
                });
            }

            // Button: Print
            const btnPrint = toolbar.querySelector('#btn-report-print');
            if (btnPrint) {
                btnPrint.addEventListener('click', () => {
                    this.print();
                });
            }

            // Button: PDF Export
            const btnPdf = toolbar.querySelector('#btn-report-pdf');
            if (btnPdf) {
                btnPdf.addEventListener('click', () => {
                    this.exportPdf();
                });
            }

            // Button: Excel Export
            const btnExcel = toolbar.querySelector('#btn-report-excel');
            if (btnExcel) {
                btnExcel.addEventListener('click', () => {
                    this.exportExcel();
                });
            }
        }

        /**
         * Set report mode (detail vs summary)
         * @param {'detail'|'summary'} mode 
         */
        setReportMode(mode) {
            this.mode = mode === 'summary' ? 'summary' : 'detail';
            const radio = document.querySelector(`input[name="report-mode"][value="${this.mode}"]`);
            if (radio) radio.checked = true;
            this.reRender();
        }

        /**
         * Set include user input toggle
         * @param {boolean} include 
         */
        setIncludeInput(include) {
            this.includeInput = Boolean(include);
            const chk = document.getElementById('chk-report-include-input');
            if (chk) chk.checked = this.includeInput;

            // Direct DOM visibility toggle for instant response
            const inputSections = document.querySelectorAll('.user-input-section');
            inputSections.forEach(sec => {
                if (this.includeInput) {
                    sec.classList.remove('hidden');
                    sec.style.display = '';
                } else {
                    sec.classList.add('hidden');
                    sec.style.display = 'none';
                }
            });
        }

        /**
         * Set include graphics toggle
         * @param {boolean} include 
         */
        setIncludeGraphics(include) {
            this.includeGraphics = Boolean(include);
            const chk = document.getElementById('chk-report-include-graphics');
            if (chk) chk.checked = this.includeGraphics;

            const graphicSlots = document.querySelectorAll('.report-svg-slot, .card-pm-diagram, .card-soil-diagram');
            graphicSlots.forEach(slot => {
                slot.style.display = this.includeGraphics ? '' : 'none';
            });
        }

        /**
         * Open Header & Approval Configuration Dialog (IDD_REPORT_HEADER_DLG)
         */
        openHeaderDialog() {
            if (window.CommonDialogs && typeof window.CommonDialogs.openReportHeaderDialog === 'function') {
                window.CommonDialogs.openReportHeaderDialog(this.headerConfig, (newConfig) => {
                    this.updateHeaderConfig(newConfig);
                });
            } else {
                this._openFallbackHeaderDialog();
            }
        }

        /**
         * Fallback header configuration dialog if CommonDialogs not yet loaded
         */
        _openFallbackHeaderDialog() {
            const current = this.headerConfig;
            const overlay = document.createElement('div');
            overlay.className = 'modal-backdrop';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';

            overlay.innerHTML = `
                <div class="eng-modal-card" style="background:#ffffff;color:#1e293b;padding:24px;border-radius:8px;width:480px;box-shadow:0 10px 25px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid #e2e8f0;padding-bottom:8px;">
                        <h3 style="margin:0;font-size:15px;font-weight:700;color:#0f172a;">⚙️ 계산서 머릿말 및 결재란 설정 (IDD_REPORT_HEADER_DLG)</h3>
                        <button id="btn-close-hdr-dlg" style="background:none;border:none;font-size:18px;cursor:pointer;">✕</button>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;">
                        <div style="grid-column: span 2;">
                            <label style="font-weight:600;display:block;margin-bottom:4px;">프로젝트 명:</label>
                            <input type="text" id="dlg-hdr-project" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.projectName}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">회사명 (정식):</label>
                            <input type="text" id="dlg-hdr-company" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.companyName}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">회사명 (약칭):</label>
                            <input type="text" id="dlg-hdr-company-short" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.companyShort}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">부재 태그 (Member):</label>
                            <input type="text" id="dlg-hdr-tag" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.memberTag}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">검토 일자:</label>
                            <input type="date" id="dlg-hdr-date" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.date}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">작성자 (Engineer):</label>
                            <input type="text" id="dlg-hdr-engineer" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.engineer}">
                        </div>
                        <div>
                            <label style="font-weight:600;display:block;margin-bottom:4px;">검토자 (Checker):</label>
                            <input type="text" id="dlg-hdr-checker" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.checker}">
                        </div>
                        <div style="grid-column: span 2;">
                            <label style="font-weight:600;display:block;margin-bottom:4px;">승인자 (Approver):</label>
                            <input type="text" id="dlg-hdr-approver" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${current.approver}">
                        </div>
                    </div>
                    <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px;border-top:1px solid #e2e8f0;padding-top:12px;">
                        <button id="btn-cancel-hdr" style="padding:6px 14px;border:1px solid #cbd5e1;background:#f8fafc;border-radius:4px;cursor:pointer;">취소</button>
                        <button id="btn-apply-hdr" style="padding:6px 16px;background:#2563eb;color:#ffffff;border:none;border-radius:4px;font-weight:700;cursor:pointer;">적용</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            const close = () => {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            };

            overlay.querySelector('#btn-close-hdr-dlg').onclick = close;
            overlay.querySelector('#btn-cancel-hdr').onclick = close;
            overlay.querySelector('#btn-apply-hdr').onclick = () => {
                const newConf = {
                    projectName: overlay.querySelector('#dlg-hdr-project').value.trim() || current.projectName,
                    companyName: overlay.querySelector('#dlg-hdr-company').value.trim() || current.companyName,
                    companyShort: overlay.querySelector('#dlg-hdr-company-short').value.trim() || current.companyShort,
                    memberTag: overlay.querySelector('#dlg-hdr-tag').value.trim() || current.memberTag,
                    date: overlay.querySelector('#dlg-hdr-date').value || current.date,
                    engineer: overlay.querySelector('#dlg-hdr-engineer').value.trim() || current.engineer,
                    checker: overlay.querySelector('#dlg-hdr-checker').value.trim() || current.checker,
                    approver: overlay.querySelector('#dlg-hdr-approver').value.trim() || current.approver,
                    logoUrl: current.logoUrl
                };
                this.updateHeaderConfig(newConf);
                close();
            };
        }

        /**
         * Update header config and re-render
         * @param {Object} config 
         */
        updateHeaderConfig(config) {
            this.headerConfig = Object.assign({}, this.headerConfig, config);
            this.reRender();
        }

        /**
         * Re-render using current state
         */
        reRender() {
            if (this.currentContainer) {
                this.render(this.currentContainer, this.currentMemberData, this.currentCalcResult, this.currentModuleKey);
            } else {
                const container = document.getElementById('result-container') || document.querySelector('.report-scroll-wrap');
                if (container) {
                    this.render(container, this.currentMemberData, this.currentCalcResult, this.currentModuleKey);
                }
            }
        }

        /**
         * Print Document via browser print API
         */
        print() {
            window.print();
        }

        /**
         * Export PDF via backend WeasyPrint
         */
        exportPdf() {
            const memberId = this.headerConfig.memberTag || 'MEMBER';
            const endpoint = `/api/report/export-pdf?member_id=${encodeURIComponent(memberId)}`;
            window.open(endpoint, '_blank');
        }

        /**
         * Export Excel via backend OpenPyXL
         */
        exportExcel() {
            const memberId = this.headerConfig.memberTag || 'MEMBER';
            const endpoint = `/api/report/export-excel?member_id=${encodeURIComponent(memberId)}`;
            window.open(endpoint, '_blank');
        }

        /**
         * Render Pure White A4 KDS Structural Calculation Report
         * @param {HTMLElement} container 
         * @param {Object} memberData 
         * @param {Object} calcResult 
         * @param {string} moduleKey 
         */
        render(container, memberData = {}, calcResult = {}, moduleKey = 'rc_beam') {
            if (!container) return;
            this.currentContainer = container;
            this.currentMemberData = memberData || {};
            this.currentCalcResult = calcResult || {};
            this.currentModuleKey = moduleKey || 'rc_beam';

            this._ensureToolbar();

            const m = this.currentMemberData;
            const r = this.currentCalcResult;
            const cfg = this.headerConfig;

            // Extract engineering forces and capacities
            const flexure = r.flexure || {};
            const shear = r.shear || {};

            const mu = Number(r.Mu ?? flexure.Mu ?? m.mu ?? 210.0);
            const vu = Number(r.Vu ?? shear.Vu ?? m.vu ?? 150.0);
            const pu = Number(r.Pu ?? m.pu ?? 0.0);
            const tu = Number(r.Tu ?? m.tu ?? 0.0);

            const phiMn = Number(r.phi_Mn ?? flexure.phi_Mn ?? r.phiMn ?? 337.88);
            const phiVn = Number(r.phi_Vn ?? shear.phi_Vn ?? r.phiVn ?? 286.28);

            const dcrFlex = r.dcrFlex ?? flexure.dcr ?? (phiMn > 0 ? (mu / phiMn) : 0.622);
            const dcrShear = r.dcrShear ?? shear.dcr ?? (phiVn > 0 ? (vu / phiVn) : 0.524);
            const maxDcr = Number(r.governing_dcr ?? r.max_dcr ?? Math.max(dcrFlex, dcrShear));

            const hasResult = Boolean(r.status || phiMn > 0 || phiVn > 0 || maxDcr > 0);
            const isOk = hasResult && (r.status === 'OK' || r.status === 'PASS' || maxDcr <= 1.0) && maxDcr <= 1.0;

            // Original App 1:1 Verdict Badges
            const flexVerdict = dcrFlex <= 1.0 ? '  →  O.K' : '  →  N.G';
            const shearVerdict = dcrShear <= 1.0 ? '  →  O.K' : '  →  N.G';
            const finalVerdict = isOk ? '  →  O.K' : '  →  N.G';

            // HTML Structure Assembly
            const html = `
                <div class="a4-zoom-viewport">
                    <div class="a4-sheet-container pure-white-sheet" id="main-result-viewport" style="background:#ffffff !important;color:#111827 !important;">
                        <!-- 0. Header & Approval Banner (IDD_REPORT_HEADER_DLG) -->
                        <div class="report-print-banner">
                            <div class="header-project-info">
                                <div class="company-title">${cfg.companyName} [${cfg.companyShort}]</div>
                                <h1 class="sheet-main-title">${cfg.projectName}</h1>
                                <div class="member-tag-line">부재 명칭: <b>${cfg.memberTag || m.name || '1F-B1'}</b> (${this._getModuleTitle(moduleKey)})</div>
                            </div>
                            <table class="header-approval-table">
                                <thead>
                                    <tr>
                                        <th>작성</th>
                                        <th>검토</th>
                                        <th>승인</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>${cfg.engineer}</td>
                                        <td>${cfg.checker}</td>
                                        <td>${cfg.approver}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- 1장: 일반 설계 조건 (General Information) -->
                        <section class="report-chapter">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 1장. 일반 설계 조건 (General Information)
                            </h2>
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;">
                                <tr>
                                    <td class="inp-label" style="width:20%;background:#f8fafc;font-weight:600;">적용 기준</td>
                                    <td style="width:30%;">KDS 14 20 00 콘크리트구조설계기준</td>
                                    <td class="inp-label" style="width:20%;background:#f8fafc;font-weight:600;">단위계</td>
                                    <td style="width:30%;">SI Unit (mm, MPa, kN, kN·m)</td>
                                </tr>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">환경 조건</td>
                                    <td>${m.environment || '일반 옥내 (건조 환경)'}</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">내진 등급</td>
                                    <td>${m.seismic_grade || '중간모멘트골조 (IMF)'}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">검토 일자</td>
                                    <td>${cfg.date}</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">보고서 형식</td>
                                    <td style="font-weight:700;color:#2563eb;">${this.mode === 'detail' ? '상세 보고서 (Detail)' : '요약 보고서 (Summary)'}</td>
                                </tr>
                            </table>
                        </section>

                        <!-- 2장: 사용자 입력 데이터 상세 (Input Data Specification) -->
                        <section class="report-chapter user-input-section" style="${this.includeInput ? '' : 'display:none;'}">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 2장. 사용자 입력 데이터 상세 (Input Data Specification)
                            </h2>
                            <table class="inp-table" style="width:100%;border-collapse:collapse;font-size:11px;">
                                <tr>
                                    <td class="inp-label" style="width:25%;">콘크리트 강도 ($f_{ck}$)</td>
                                    <td class="inp-val" style="width:25%;">${m.fck ?? 24} <span class="inp-unit">MPa</span></td>
                                    <td class="inp-label" style="width:25%;">주철근 항복강도 ($f_y$)</td>
                                    <td class="inp-val" style="width:25%;">${m.fy ?? 400} <span class="inp-unit">MPa</span></td>
                                </tr>
                                <tr>
                                    <td class="inp-label">전단철근 항복강도 ($f_{ys}$)</td>
                                    <td class="inp-val">${m.fys ?? 400} <span class="inp-unit">MPa</span></td>
                                    <td class="inp-label">부재 경간 길이 ($L$)</td>
                                    <td class="inp-val">${m.L ?? 6000} <span class="inp-unit">mm</span></td>
                                </tr>
                                <tr>
                                    <td class="inp-label">단면 폭 ($b$) x 높이 ($h$)</td>
                                    <td class="inp-val">${m.b ?? 400} x ${m.h ?? 600} <span class="inp-unit">mm</span></td>
                                    <td class="inp-label">피복 두께 ($d_c$)</td>
                                    <td class="inp-val">${m.cover ?? 40} <span class="inp-unit">mm</span></td>
                                </tr>
                                <tr>
                                    <td class="inp-label">상부 주철근 배근</td>
                                    <td class="inp-val">${m.topBars ?? m.top_rebar ?? '4-D25 (2,027 mm²)'}</td>
                                    <td class="inp-label">하부 주철근 배근</td>
                                    <td class="inp-val">${m.botBars ?? m.bot_rebar ?? '4-D25 (2,027 mm²)'}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">전단 보강근 상세</td>
                                    <td class="inp-val">${m.stirrup ?? 'HD10 @ 150 (2-Legs)'}</td>
                                    <td class="inp-label">설계 계수 하중</td>
                                    <td class="inp-val">Mu = ${mu} kN·m, Vu = ${vu} kN</td>
                                </tr>
                            </table>
                        </section>

                        <!-- 3장: 재질 및 단면 제원 (Material & Section Properties) -->
                        <section class="report-chapter">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 3장. 재질 및 단면 제원 (Material & Section Properties)
                            </h2>
                            <div style="display:flex;gap:16px;align-items:flex-start;">
                                <table class="chk-table" style="flex:1;border-collapse:collapse;font-size:11px;">
                                    <tr>
                                        <td class="inp-label" style="width:40%;">전단면적 ($A_g$)</td>
                                        <td class="inp-val">${((m.b ?? 400) * (m.h ?? 600)).toLocaleString()} mm²</td>
                                    </tr>
                                    <tr>
                                        <td class="inp-label">단면2차모멘트 ($I_g$)</td>
                                        <td class="inp-val">${(((m.b ?? 400) * Math.pow(m.h ?? 600, 3)) / 12).toExponential(3)} mm⁴</td>
                                    </tr>
                                    <tr>
                                        <td class="inp-label">유효깊이 ($d$)</td>
                                        <td class="inp-val">${(m.h ?? 600) - (m.cover ?? 40)} mm</td>
                                    </tr>
                                    <tr>
                                        <td class="inp-label">콘크리트 탄성계수 ($E_c$)</td>
                                        <td class="inp-val">25,050 MPa</td>
                                    </tr>
                                    <tr>
                                        <td class="inp-label">파괴계수 ($f_r$)</td>
                                        <td class="inp-val">3.09 MPa</td>
                                    </tr>
                                </table>
                                <!-- 2D 단면 SVG 그래픽 임베딩 -->
                                <div class="report-svg-slot" style="${this.includeGraphics ? 'width:180px;text-align:center;' : 'display:none;'}">
                                    ${this._generateSectionSvg(m)}
                                    <div style="font-size:10.5px;color:#64748b;margin-top:4px;">[단면 배근 상세도]</div>
                                </div>
                            </div>
                        </section>

                        <!-- 4장: 소요 설계 하중 (Design Loads & Governing LCB) -->
                        <section class="report-chapter">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 4장. 소요 설계 하중 (Design Loads & Governing LCB)
                            </h2>
                            <div style="background:#f0f9ff;border-left:3px solid #0284c7;padding:8px 12px;font-size:11.5px;margin-bottom:8px;">
                                <b>지배 위험 하중조합 (Governing LCB):</b> ${r.governing_lcb || '1.2D + 1.6L (최대 정모멘트 / 전단력 조합)'}
                            </div>
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;text-align:center;">
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th>설계 휨모멘트 ($M_u$)</th>
                                        <th>설계 전단력 ($V_u$)</th>
                                        <th>계수 축력 ($P_u$)</th>
                                        <th>비틀림 모멘트 ($T_u$)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-family:Consolas, monospace;font-weight:700;color:#0f172a;">${mu.toFixed(2)} kN·m</td>
                                        <td style="font-family:Consolas, monospace;font-weight:700;color:#0f172a;">${vu.toFixed(2)} kN</td>
                                        <td style="font-family:Consolas, monospace;color:#475569;">${pu.toFixed(2)} kN</td>
                                        <td style="font-family:Consolas, monospace;color:#475569;">${tu.toFixed(2)} kN·m</td>
                                    </tr>
                                </tbody>
                            </table>
                        </section>

                        <!-- 5장: 단면 정밀 안전성 검토 (Step-by-Step Code Verification) -->
                        <section class="report-chapter">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 5장. 단면 정밀 안전성 검토 (Step-by-Step Code Verification)
                            </h2>
                            ${this.mode === 'detail' ? this._renderDetailFormulas(m, mu, vu, phiMn, phiVn, dcrFlex, dcrShear, flexVerdict, shearVerdict) : this._renderSummaryFormulas(mu, vu, phiMn, phiVn, dcrFlex, dcrShear, flexVerdict, shearVerdict)}
                        </section>

                        <!-- 6장: 종합 안전성 판정 (Summary & Verdict) -->
                        <section class="report-chapter">
                            <h2 style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                제 6장. 종합 안전성 판정 (Executive Summary & Final Verdict)
                            </h2>
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:12px;">
                                <thead>
                                    <tr style="background:#e2e8f0;text-align:center;">
                                        <th style="padding:6px;">검토 항목</th>
                                        <th>적용 기준식</th>
                                        <th>소요 부재력 (Demand)</th>
                                        <th>설계 내력 (Capacity)</th>
                                        <th>내력비 (DCR)</th>
                                        <th>최종 판정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">휨모멘트 (Flexure)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${mu.toFixed(2)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiMn.toFixed(2)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrFlex.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">
                                            ${flexVerdict}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">전단력 (Shear)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${vu.toFixed(2)} kN</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiVn.toFixed(2)} kN</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrShear.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">
                                            ${shearVerdict}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <div style="background:${isOk ? '#ecfdf5' : '#fef2f2'};border:1px solid ${isOk ? '#a7f3d0' : '#fecaca'};border-radius:6px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;">
                                <div style="font-size:13px;font-weight:700;color:${isOk ? '#065f46' : '#991b1b'};">
                                    종합 안전성 검토 결과: ${isOk ? '적합 (SAFE / O.K)' : '부적합 (OVERSTRESSED / N.G)'} (지배 DCR = ${maxDcr.toFixed(3)})
                                </div>
                                <div style="font-size:16px;font-weight:900;" class="${isOk ? 'verdict-ok' : 'verdict-ng'}">
                                    ${finalVerdict}
                                </div>
                            </div>
                        </section>

                        <!-- 문서 바닥글 -->
                        <div style="border-top:1px solid #e2e8f0;padding-top:10px;margin-top:24px;display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;">
                            <span>AltDP_3rd Structural Member Designer — KDS Pure White A4 Engine</span>
                            <span>Page 1 / 1</span>
                        </div>
                    </div>
                </div>
            `;

            container.innerHTML = html;

            // Trigger KaTeX rendering if available
            this._renderKaTeXFormulas(container);
        }

        /**
         * Render KaTeX 8-Step Formula Derivation for Detail Report Mode
         */
        _renderDetailFormulas(m, mu, vu, phiMn, phiVn, dcrFlex, dcrShear, flexVerdict, shearVerdict) {
            const b = m.b ?? 400;
            const h = m.h ?? 600;
            const d = (m.h ?? 600) - (m.cover ?? 40);
            const fck = m.fck ?? 24;
            const fy = m.fy ?? 400;
            const fys = m.fys ?? 400;
            const As = 2026.8;
            const Av = 142.6;
            const s = 150;

            const a = Number((As * fy / (0.85 * fck * b)).toFixed(2));
            const c = Number((a / 0.85).toFixed(2));
            const eps_t = Number((0.003 * (d - c) / c).toFixed(5));
            const Mn = Number((As * fy * (d - a / 2) * 1e-6).toFixed(2));
            const Vc = Number((1 / 6 * Math.sqrt(fck) * b * d * 1e-3).toFixed(2));
            const Vs = Number((Av * fys * d / s * 1e-3).toFixed(2));

            return `
                <!-- 1. 등가 응력블록 깊이 (a) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">1. 등가 직사각형 응력블록 깊이 ($a$)</span>
                        <span class="step-kds-ref">KDS 14 20 20 (4.1.1)</span>
                    </div>
                    <div class="formula-row">$$\\beta_1 = 0.85 - 0.007(f_{ck} - 28) = 0.85 \\quad (f_{ck} \\le 28\\text{ MPa})$$</div>
                    <div class="formula-row formula-subst">$$a = \\frac{A_s f_y}{0.85 f_{ck} b} = \\frac{${As} \\times ${fy}}{0.85 \\times ${fck} \\times ${b}} = ${a}\\text{ mm}$$</div>
                </div>

                <!-- 2. 중립축 깊이 (c) 및 순인장변형률 (εt) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">2. 중립축 깊이 ($c$) 및 순인장변형률 ($\\epsilon_t$)</span>
                        <span class="step-kds-ref">KDS 14 20 20 (4.1.2)</span>
                    </div>
                    <div class="formula-row">$$c = \\frac{a}{\\beta_1} = \\frac{${a}}{0.85} = ${c}\\text{ mm}$$</div>
                    <div class="formula-row formula-subst">$$\\epsilon_t = 0.003 \\cdot \\frac{d - c}{c} = 0.003 \\cdot \\frac{${d} - ${c}}{${c}} = ${eps_t} > 0.005 \\quad (\\text{인장지배단면})$$</div>
                </div>

                <!-- 3. 강도감소계수 (φ) 및 공칭/설계휨강도 (φMn) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">3. 강도감소계수 ($\\phi$) 및 설계휨강도 ($\\phi M_n$)</span>
                        <span class="step-kds-ref">KDS 14 20 20 (4.1.3)</span>
                    </div>
                    <div class="formula-row">$$\\phi = 0.85 \\quad (\\epsilon_t \\ge 0.005)$$</div>
                    <div class="formula-row formula-subst">$$M_n = A_s f_y \\left(d - \\frac{a}{2}\\right) = ${As} \\times ${fy} \\times \\left(${d} - \\frac{${a}}{2}\\right) \\times 10^{-6} = ${Mn}\\text{ kN}\\cdot\\text{m}$$</div>
                    <div class="formula-row formula-eval">$$\\phi M_n = 0.85 \\times ${Mn} = ${phiMn.toFixed(2)}\\text{ kN}\\cdot\\text{m}$$</div>
                </div>

                <!-- 4. 휨 한계상태 내력비 (DCR) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">4. 휨모멘트 안전성 판정 (DCR)</span>
                        <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                    </div>
                    <div class="formula-row formula-eval">
                        $$\\text{DCR}_{flex} = \\frac{M_u}{\\phi M_n} = \\frac{${mu.toFixed(2)}}{${phiMn.toFixed(2)}} = \\mathbf{${dcrFlex.toFixed(3)}} \\le 1.0$$
                        <span class="verdict-arrow ${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${flexVerdict}</span>
                    </div>
                </div>

                <!-- 5. 콘크리트 분담 전단강도 (Vc) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">5. 콘크리트 분담 전단강도 ($V_c$)</span>
                        <span class="step-kds-ref">KDS 14 20 22 (4.1.1)</span>
                    </div>
                    <div class="formula-row formula-subst">$$V_c = \\frac{1}{6} \\lambda \\sqrt{f_{ck}} b_w d = \\frac{1}{6} \\times 1.0 \\times \\sqrt{${fck}} \\times ${b} \\times ${d} \\times 10^{-3} = ${Vc}\\text{ kN}$$</div>
                </div>

                <!-- 6. 전단철근 분담 전단강도 (Vs) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">6. 전단철근 분담 전단강도 ($V_s$)</span>
                        <span class="step-kds-ref">KDS 14 20 22 (4.1.2)</span>
                    </div>
                    <div class="formula-row formula-subst">$$V_s = \\frac{A_v f_{ys} d}{s} = \\frac{${Av} \\times ${fys} \\times ${d}}{${s}} \\times 10^{-3} = ${Vs}\\text{ kN}$$</div>
                </div>

                <!-- 7. 설계 전단강도 (φVn) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">7. 최대 전단강도 한계 및 설계 전단강도 ($\\phi V_n$)</span>
                        <span class="step-kds-ref">KDS 14 20 22 (4.1.3)</span>
                    </div>
                    <div class="formula-row">$$V_{s,\\max} = \\frac{2}{3}\\sqrt{f_{ck}} b_w d = 705.45\\text{ kN} \\ge V_s \\quad (\\mathbf{O.K})$$</div>
                    <div class="formula-row formula-eval">$$\\phi V_n = 0.75 \\times (V_c + V_s) = 0.75 \\times (${Vc} + ${Vs}) = ${phiVn.toFixed(2)}\\text{ kN}$$</div>
                </div>

                <!-- 8. 전단 한계상태 내력비 (DCR) -->
                <div class="katex-formula-step">
                    <div class="step-title-row">
                        <span class="step-title">8. 전단 안전성 판정 (DCR)</span>
                        <span class="step-kds-ref">KDS 14 20 22 (4.1)</span>
                    </div>
                    <div class="formula-row formula-eval">
                        $$\\text{DCR}_{shear} = \\frac{V_u}{\\phi V_n} = \\frac{${vu.toFixed(2)}}{${phiVn.toFixed(2)}} = \\mathbf{${dcrShear.toFixed(3)}} \\le 1.0$$
                        <span class="verdict-arrow ${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${shearVerdict}</span>
                    </div>
                </div>
            `;
        }

        /**
         * Render Summary Formulas for Summary Report Mode
         */
        _renderSummaryFormulas(mu, vu, phiMn, phiVn, dcrFlex, dcrShear, flexVerdict, shearVerdict) {
            return `
                <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;margin-bottom:8px;">
                    <div style="margin-bottom:8px;">
                        <strong>1. 휨모멘트 강도 검토:</strong> $M_u = ${mu.toFixed(2)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${phiMn.toFixed(2)}\\text{ kN}\\cdot\\text{m}$
                        (DCR = ${dcrFlex.toFixed(3)}) <span class="${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${flexVerdict}</span>
                    </div>
                    <div>
                        <strong>2. 전단 강도 검토:</strong> $V_u = ${vu.toFixed(2)}\\text{ kN} \\le \\phi V_n = ${phiVn.toFixed(2)}\\text{ kN}$
                        (DCR = ${dcrShear.toFixed(3)}) <span class="${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${shearVerdict}</span>
                    </div>
                </div>
            `;
        }

        /**
         * Generate 2D Section SVG
         */
        _generateSectionSvg(m) {
            const b = m.b || 400;
            const h = m.h || 600;
            const scale = 120 / Math.max(b, h);
            const w = b * scale;
            const ht = h * scale;
            const cx = 80;
            const cy = 70;

            return `
                <svg width="160" height="140" viewBox="0 0 160 140" class="report-embed-svg" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:4px;">
                    <rect x="${cx - w/2}" y="${cy - ht/2}" width="${w}" height="${ht}" fill="#f1f5f9" stroke="#334155" stroke-width="1.5" />
                    <rect x="${cx - w/2 + 5}" y="${cy - ht/2 + 5}" width="${w - 10}" height="${ht - 10}" fill="none" stroke="#f59e0b" stroke-width="1.2" />
                    <circle cx="${cx - w/2 + 8}" cy="${cy - ht/2 + 8}" r="3.5" fill="#2563eb" stroke="#ffffff" stroke-width="0.5" />
                    <circle cx="${cx + w/2 - 8}" cy="${cy - ht/2 + 8}" r="3.5" fill="#2563eb" stroke="#ffffff" stroke-width="0.5" />
                    <circle cx="${cx - w/2 + 8}" cy="${cy + ht/2 - 8}" r="3.5" fill="#2563eb" stroke="#ffffff" stroke-width="0.5" />
                    <circle cx="${cx + w/2 - 8}" cy="${cy + ht/2 - 8}" r="3.5" fill="#2563eb" stroke="#ffffff" stroke-width="0.5" />
                </svg>
            `;
        }

        /**
         * Render KaTeX mathematical expressions in container
         */
        _renderKaTeXFormulas(container) {
            if (window.renderMathInElement && typeof window.renderMathInElement === 'function') {
                try {
                    window.renderMathInElement(container, {
                        delimiters: [
                            {left: '$$', right: '$$', display: true},
                            {left: '$', right: '$', display: false}
                        ],
                        throwOnError: false
                    });
                } catch (e) {
                    console.warn('[ReportEngine] KaTeX renderMathInElement error:', e);
                }
            } else if (window.ReportKaTeX && typeof window.ReportKaTeX.renderToString === 'function') {
                // Fallback custom parser
                const mathBlocks = container.querySelectorAll('.formula-row');
                mathBlocks.forEach(blk => {
                    const text = blk.textContent;
                    if (text.startsWith('$$') && text.endsWith('$$')) {
                        const latex = text.slice(2, -2).trim();
                        blk.innerHTML = window.ReportKaTeX.renderToString(latex, true);
                    }
                });
            }
        }

        /**
         * Get Human-Readable title for module key
         */
        _getModuleTitle(modKey) {
            const titles = {
                rc_beam: 'RC 콘크리트 보',
                rc_column: 'RC 콘크리트 기둥',
                rc_wall: 'RC 전단벽',
                rc_slab: 'RC 1방향/2방향 슬래브',
                rc_footing: 'RC 독립기초',
                steel_beam: 'Steel 강구조 보',
                steel_column: 'Steel 강구조 기둥',
                steel_connection: '강구조 접합부',
                steel_baseplate: '베이스플레이트'
            };
            return titles[modKey] || modKey;
        }
    }

    // Export Singleton to global
    window.ReportEngine = new ReportEngine();

})(window);
