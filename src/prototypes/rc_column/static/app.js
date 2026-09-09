/**
 * Midas Design+ RC Column 1:1 Prototype Interactive Frontend Controller (app.js)
 * Conforms 100% to docs/202_rc_column_module_specification.md.
 * Features:
 * - 10-domain 48-parameter 1:1 real-time calculation
 * - Mixed rebar detailing (Corner vs Side bar diameter)
 * - 4 Internal tie bar patterns (TYPE_1 ~ TYPE_4)
 * - Excel clipboard TSV paste integration
 * - Real-time Canvas 3D P-Mx-My interaction surface viewer with interactive mouse rotation
 * - Rounded corner section rendering
 */

class RCColumnApp {
    constructor() {
        this.currentAxis = 'X'; // 'X', 'Y', or '3D'
        this.lastResult = null;
        this.rotX = 22.0;       // Pitch angle (degrees)
        this.rotZ = -45.0;      // Yaw angle (degrees)
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;

        this.loadCombinations = [
            { no: 1, name: "1.4D", Pu: 1800.0, Mux: 120.0, Muy: 80.0, Vux: 45.0, Vuy: 60.0 },
            { no: 2, name: "1.2D + 1.6L", Pu: 2500.0, Mux: 350.0, Muy: 150.0, Vux: 80.0, Vuy: 120.0 },
            { no: 3, name: "1.2D + 1.0L + 1.0E", Pu: 2100.0, Mux: 480.0, Muy: 320.0, Vux: 160.0, Vuy: 210.0 }
        ];

        this.initDOMElements();
        this.bindEvents();
        this.updateStateMachine();
        this.runCheck(); // Initial execution
    }

    initDOMElements() {
        // Form inputs
        this.selFck = document.getElementById('selFck');
        this.selFy = document.getElementById('selFy');
        this.selFys = document.getElementById('selFys');
        this.chkLcon = document.getElementById('chkLcon');
        this.numLambda = document.getElementById('numLambda');

        this.radShapes = document.getElementsByName('radShape');
        this.rectFields = document.getElementById('rectFields');
        this.circleFields = document.getElementById('circleFields');
        this.rectBarFields = document.getElementById('rectBarFields');
        this.circleBarFields = document.getElementById('circleBarFields');

        this.numWidth = document.getElementById('numWidth');
        this.numHeight = document.getElementById('numHeight');
        this.numCorner = document.getElementById('numCorner');
        this.numDiameter = document.getElementById('numDiameter');
        this.numCover = document.getElementById('numCover');
        this.numLux = document.getElementById('numLux');
        this.numLuy = document.getElementById('numLuy');
        this.numKx = document.getElementById('numKx');
        this.numKy = document.getElementById('numKy');

        this.numPu = document.getElementById('numPu');
        this.chkApply2Shear = document.getElementById('chkApply2Shear');
        this.numMux = document.getElementById('numMux');
        this.numMuy = document.getElementById('numMuy');
        this.numVux = document.getElementById('numVux');
        this.numVuy = document.getElementById('numVuy');

        this.numCmx = document.getElementById('numCmx');
        this.numCmy = document.getElementById('numCmy');
        this.numBetaD = document.getElementById('numBetaD');
        this.chk2ndOrder = document.getElementById('chk2ndOrder');

        this.numNx = document.getElementById('numNx');
        this.numNy = document.getElementById('numNy');
        this.numNcir = document.getElementById('numNcir');
        this.selBarDiam = document.getElementById('selBarDiam');

        // Rebar Mode & Per-Face Fields
        this.radRebarModes = document.getElementsByName('radRebarMode');
        this.perFaceBarFields = document.getElementById('perFaceBarFields');
        this.singleBarDiamField = document.getElementById('singleBarDiamField');
        this.diffBarCheckField = document.getElementById('diffBarCheckField');
        this.selPerFaceCornerDiam = document.getElementById('selPerFaceCornerDiam');
        this.numSideXBars = document.getElementById('numSideXBars');
        this.selSideXBarDiam = document.getElementById('selSideXBarDiam');
        this.numSideYBars = document.getElementById('numSideYBars');
        this.selSideYBarDiam = document.getElementById('selSideYBarDiam');
        this.lblClearSpacingStatus = document.getElementById('lblClearSpacingStatus');

        // Mixed Rebar
        this.chkUseDiffBar = document.getElementById('chkUseDiffBar');
        this.diffBarOptions = document.getElementById('diffBarOptions');
        this.selCornerBarDiam = document.getElementById('selCornerBarDiam');
        this.selSideBarDiam = document.getElementById('selSideBarDiam');

        // Tie bar & Pattern
        this.selTieType = document.getElementById('selTieType');
        this.selTieDiam = document.getElementById('selTieDiam');
        this.numTieSpacing = document.getElementById('numTieSpacing');
        this.chkUseEndTie = document.getElementById('chkUseEndTie');
        this.numEndTieSpacing = document.getElementById('numEndTieSpacing');
        this.numLegsX = document.getElementById('numLegsX');
        this.numLegsY = document.getElementById('numLegsY');
        this.selTiePattern = document.getElementById('selTiePattern');
        this.chkTiebar = document.getElementById('chkTiebar');
        this.radSplices = document.getElementsByName('radSplice');

        this.chkSeismic = document.getElementById('chkSeismic');
        this.seismicSubOptions = document.getElementById('seismicSubOptions');
        this.radFrames = document.getElementsByName('radFrame');
        this.chkPiloti = document.getElementById('chkPiloti');

        this.chkUserRho = document.getElementById('chkUserRho');
        this.userRhoOptions = document.getElementById('userRhoOptions');
        this.numMinRho = document.getElementById('numMinRho');
        this.numMaxRho = document.getElementById('numMaxRho');

        // Buttons
        this.btnCheck = document.getElementById('btnCheck');
        this.btnAutoDesign = document.getElementById('btnAutoDesign');
        this.btnOpenReport = document.getElementById('btnOpenReport');
        this.btnOpenLcomb = document.getElementById('btnOpenLcomb');
        this.tabAxisX = document.getElementById('tabAxisX');
        this.tabAxisY = document.getElementById('tabAxisY');
        this.tabAxis3D = document.getElementById('tabAxis3D');
        this.pm3dHint = document.getElementById('pm3dHint');

        // Canvases
        this.canvasSection = document.getElementById('canvasSection');
        this.canvasPM = document.getElementById('canvasPM');

        // Modals - Lcomb
        this.modalLcomb = document.getElementById('modalLcomb');
        this.btnCloseLcomb = document.getElementById('btnCloseLcomb');
        this.btnApplyLcomb = document.getElementById('btnApplyLcomb');
        this.btnAddLcomb = document.getElementById('btnAddLcomb');
        this.btnDelLcomb = document.getElementById('btnDelLcomb');
        this.btnResetLcomb = document.getElementById('btnResetLcomb');
        this.btnPasteExcel = document.getElementById('btnPasteExcel');
        this.tbodyLcomb = document.getElementById('tbodyLcomb');

        // Modals - Rebar Detail (IDD_RCS_COLUMN_RBAR_DLG)
        this.btnOpenRebarDetail = document.getElementById('btnOpenRebarDetail');
        this.modalRebarDetail = document.getElementById('modalRebarDetail');
        this.btnCloseRebarDetail = document.getElementById('btnCloseRebarDetail');
        this.btnApplyRebarDetail = document.getElementById('btnApplyRebarDetail');
        this.numModalCover = document.getElementById('numModalCover');
        this.numModalDagg = document.getElementById('numModalDagg');
        this.selModalHookType = document.getElementById('selModalHookType');
        this.numModalLo = document.getElementById('numModalLo');
        this.chkModalAutoLo = document.getElementById('chkModalAutoLo');

        // Modals - Pure White A4 Report
        this.modalReport = document.getElementById('modalReport');
        this.btnCloseReport = document.getElementById('btnCloseReport');
        this.btnCloseReport2 = document.getElementById('btnCloseReport2');
        this.btnPrintReport = document.getElementById('btnPrintReport');
        this.btnCopyReportHtml = document.getElementById('btnCopyReportHtml');
        this.btnZoomToggle = document.getElementById('btnZoomToggle');
        this.reportContainer = document.getElementById('reportContainer');
        this.reportSheet = document.getElementById('reportSheet');

        // Labels
        this.lblOverallStatus = document.getElementById('overallStatusBadge');
        this.lblP0 = document.getElementById('lblP0');
        this.lblPhiPnMax = document.getElementById('lblPhiPnMax');
        this.lblMc = document.getElementById('lblMc');
        this.lblPhiVn = document.getElementById('lblPhiVn');
        this.lblMaxDcr = document.getElementById('lblMaxDcr');
        this.lblCritName = document.getElementById('lblCritName');
        this.lblTotalBars = document.getElementById('lblTotalBars');
        this.lblRhoG = document.getElementById('lblRhoG');
        this.lblClearSpacing = document.getElementById('lblClearSpacing');
        this.lblLsTens = document.getElementById('lblLsTens');
        this.lblLscComp = document.getElementById('lblLscComp');
        this.lblLo = document.getElementById('lblLo');
        this.lblSoLimit = document.getElementById('lblSoLimit');
        this.lblAshReq = document.getElementById('lblAshReq');
    }

    bindEvents() {
        // 배근 모드 전환 (EQUAL vs PER_FACE)
        if (this.radRebarModes) {
            this.radRebarModes.forEach(r => r.addEventListener('change', () => {
                this.updateStateMachine();
                this.runCheck();
            }));
        }

        // 배근 상세 모달 이벤트
        if (this.btnOpenRebarDetail) {
            this.btnOpenRebarDetail.addEventListener('click', () => {
                if (this.numModalCover) this.numModalCover.value = this.numCover.value;
                if (this.modalRebarDetail) this.modalRebarDetail.style.display = 'flex';
            });
        }
        if (this.btnCloseRebarDetail) {
            this.btnCloseRebarDetail.addEventListener('click', () => {
                if (this.modalRebarDetail) this.modalRebarDetail.style.display = 'none';
            });
        }
        if (this.btnApplyRebarDetail) {
            this.btnApplyRebarDetail.addEventListener('click', () => {
                if (this.numModalCover) this.numCover.value = this.numModalCover.value;
                if (this.modalRebarDetail) this.modalRebarDetail.style.display = 'none';
                this.runCheck();
            });
        }

        // 리포트 툴바 이벤트 (인쇄, 복사, 줌)
        if (this.btnPrintReport) {
            this.btnPrintReport.addEventListener('click', () => window.print());
        }
        if (this.btnCopyReportHtml) {
            this.btnCopyReportHtml.addEventListener('click', () => {
                if (!this.reportSheet) return;
                const html = this.reportSheet.innerText;
                navigator.clipboard.writeText(html).then(() => {
                    alert('📋 구조계산서 내용이 클립보드에 복사되었습니다.');
                }).catch(() => {
                    alert('클립보드 복사에 실패했습니다.');
                });
            });
        }
        if (this.btnZoomToggle) {
            this.isZoomFit = false;
            this.btnZoomToggle.addEventListener('click', () => {
                this.isZoomFit = !this.isZoomFit;
                if (this.reportSheet) {
                    this.reportSheet.style.transform = this.isZoomFit ? 'scale(0.85)' : 'scale(1.0)';
                    this.reportSheet.style.transformOrigin = 'top center';
                    this.btnZoomToggle.innerText = this.isZoomFit ? '🔍 100%' : '🔍 화면 맞춤';
                }
            });
        }

        // 라디오 및 체크박스 상태 전이
        this.radShapes.forEach(r => r.addEventListener('change', () => {
            this.updateStateMachine();
            this.runCheck();
        }));

        this.chkLcon.addEventListener('change', () => this.updateStateMachine());
        this.chkUseEndTie.addEventListener('change', () => this.updateStateMachine());
        this.chkSeismic.addEventListener('change', () => this.updateStateMachine());
        this.chkUserRho.addEventListener('change', () => this.updateStateMachine());

        if (this.chkUseDiffBar) {
            this.chkUseDiffBar.addEventListener('change', () => {
                this.updateStateMachine();
                this.runCheck();
            });
        }

        // 즉각 재계산 이벤트
        const autoInputs = [
            this.selFck, this.selFy, this.selFys, this.numLambda,
            this.numWidth, this.numHeight, this.numCorner, this.numDiameter, this.numCover,
            this.numLux, this.numLuy, this.numKx, this.numKy,
            this.numPu, this.numMux, this.numMuy, this.numVux, this.numVuy,
            this.numNx, this.numNy, this.numNcir, this.selBarDiam,
            this.selPerFaceCornerDiam, this.numSideXBars, this.selSideXBarDiam,
            this.numSideYBars, this.selSideYBarDiam,
            this.selCornerBarDiam, this.selSideBarDiam,
            this.selTieType, this.selTieDiam, this.selTiePattern,
            this.numTieSpacing, this.numEndTieSpacing, this.numLegsX, this.numLegsY
        ].filter(Boolean);

        autoInputs.forEach(el => el.addEventListener('change', () => this.runCheck()));

        this.radSplices.forEach(r => r.addEventListener('change', () => this.runCheck()));
        this.radFrames.forEach(r => r.addEventListener('change', () => this.runCheck()));

        // 버튼 이벤트
        this.btnCheck.addEventListener('click', () => this.runCheck());
        this.btnAutoDesign.addEventListener('click', () => this.runAutoDesign());
        this.btnOpenReport.addEventListener('click', () => this.showReportModal());
        this.btnCloseReport.addEventListener('click', () => this.modalReport.style.display = 'none');
        this.btnCloseReport2.addEventListener('click', () => this.modalReport.style.display = 'none');

        // P-M 축 전환
        this.tabAxisX.addEventListener('click', () => {
            this.currentAxis = 'X';
            this.tabAxisX.classList.add('active');
            this.tabAxisY.classList.remove('active');
            this.tabAxis3D.classList.remove('active');
            this.pm3dHint.style.display = 'none';
            if (this.lastResult) this.renderPMCanvas(this.lastResult);
        });

        this.tabAxisY.addEventListener('click', () => {
            this.currentAxis = 'Y';
            this.tabAxisY.classList.add('active');
            this.tabAxisX.classList.remove('active');
            this.tabAxis3D.classList.remove('active');
            this.pm3dHint.style.display = 'none';
            if (this.lastResult) this.renderPMCanvas(this.lastResult);
        });

        if (this.tabAxis3D) {
            this.tabAxis3D.addEventListener('click', () => {
                this.currentAxis = '3D';
                this.tabAxis3D.classList.add('active');
                this.tabAxisX.classList.remove('active');
                this.tabAxisY.classList.remove('active');
                this.pm3dHint.style.display = 'block';
                if (this.lastResult) this.renderPMCanvas(this.lastResult);
            });
        }

        // 3D Canvas Mouse Rotate Controls
        this.canvasPM.addEventListener('mousedown', (e) => {
            if (this.currentAxis !== '3D') return;
            this.isDragging = true;
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isDragging || this.currentAxis !== '3D') return;
            const dx = e.clientX - this.lastMouseX;
            const dy = e.clientY - this.lastMouseY;
            this.rotZ += dx * 0.7;
            this.rotX = Math.max(-80, Math.min(80, this.rotX + dy * 0.5));
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            if (this.lastResult) this.renderPMCanvas(this.lastResult);
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        // 모달 이벤트
        this.btnOpenLcomb.addEventListener('click', () => {
            this.renderLcombTable();
            this.modalLcomb.style.display = 'flex';
        });
        this.btnCloseLcomb.addEventListener('click', () => this.modalLcomb.style.display = 'none');
        this.btnApplyLcomb.addEventListener('click', () => {
            this.collectLcombFromTable();
            this.modalLcomb.style.display = 'none';
            this.runCheck();
        });

        this.btnAddLcomb.addEventListener('click', () => {
            const nextNo = this.loadCombinations.length + 1;
            this.loadCombinations.push({
                no: nextNo, name: `LC${nextNo}`, Pu: 2000.0, Mux: 250.0, Muy: 150.0, Vux: 80.0, Vuy: 120.0
            });
            this.renderLcombTable();
        });

        this.btnDelLcomb.addEventListener('click', () => {
            const checked = document.querySelectorAll('.chk-lc:checked');
            if (checked.length === 0) return alert('삭제할 하중조합을 선택하세요.');
            const toDelete = Array.from(checked).map(c => parseInt(c.dataset.no));
            this.loadCombinations = this.loadCombinations.filter(lc => !toDelete.includes(lc.no));
            this.renderLcombTable();
        });

        this.btnResetLcomb.addEventListener('click', () => {
            this.loadCombinations = [
                { no: 1, name: "1.4D", Pu: 1800.0, Mux: 120.0, Muy: 80.0, Vux: 45.0, Vuy: 60.0 },
                { no: 2, name: "1.2D + 1.6L", Pu: 2500.0, Mux: 350.0, Muy: 150.0, Vux: 80.0, Vuy: 120.0 },
                { no: 3, name: "1.2D + 1.0L + 1.0E", Pu: 2100.0, Mux: 480.0, Muy: 320.0, Vux: 160.0, Vuy: 210.0 }
            ];
            this.renderLcombTable();
        });

        // 엑셀 붙여넣기 기능
        if (this.btnPasteExcel) {
            this.btnPasteExcel.addEventListener('click', () => this.handleExcelPaste());
        }

        // 모달 테이블 Ctrl+V 직접 붙여넣기 지원
        this.tbodyLcomb.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text');
            this.parseTSVLoadCombinations(text);
        });

        this.btnOpenReport.addEventListener('click', () => this.showReportModal());
        this.btnCloseReport.addEventListener('click', () => this.modalReport.style.display = 'none');
        this.btnCloseReport2.addEventListener('click', () => this.modalReport.style.display = 'none');
        this.btnCopyReport.addEventListener('click', () => {
            navigator.clipboard.writeText(this.preReportContent.innerText);
            alert('상세 리포트가 클립보드에 복사되었습니다.');
        });
    }

    async handleExcelPaste() {
        let text = "";
        try {
            if (navigator.clipboard && navigator.clipboard.readText) {
                text = await navigator.clipboard.readText();
            }
        } catch (err) {
            console.warn("Clipboard access denied or unsupported, fallback to prompt:", err);
        }

        if (!text || text.trim().length === 0) {
            text = prompt("엑셀에서 복사한 테이블 데이터를 아래에 붙여넣기(Ctrl+V) 하세요:\n(형식: 이름 [탭] Pu [탭] Mux [탭] Muy [탭] Vux [탭] Vuy)");
        }

        if (text && text.trim().length > 0) {
            this.parseTSVLoadCombinations(text);
        }
    }

    parseTSVLoadCombinations(text) {
        const lines = text.trim().split(/\r?\n/);
        const parsed = [];
        let curNo = 1;

        for (const line of lines) {
            const row = line.trim();
            if (!row) continue;
            // Split by tab or multiple spaces or comma
            const parts = row.split(/\t|,|\s{2,}/).map(s => s.trim()).filter(Boolean);
            if (parts.length < 3) continue; // At least name, Pu, Mux

            // Skip header if line contains non-numeric Pu
            const testNum = parseFloat(parts[1]);
            if (isNaN(testNum)) continue;

            const name = parts[0] || `LC${curNo}`;
            const Pu = parseFloat(parts[1]) || 0.0;
            const Mux = parseFloat(parts[2]) || 0.0;
            const Muy = parseFloat(parts[3]) || 0.0;
            const Vux = parseFloat(parts[4]) || 0.0;
            const Vuy = parseFloat(parts[5]) || 0.0;

            parsed.push({ no: curNo++, name, Pu, Mux, Muy, Vux, Vuy });
        }

        if (parsed.length > 0) {
            this.loadCombinations = parsed;
            this.renderLcombTable();
            alert(`성공: 엑셀 데이터 ${parsed.length}개 하중조합을 붙여넣었습니다.`);
        } else {
            alert('유효한 테이블 데이터를 찾을 수 없습니다. (형식: 명칭, Pu, Mux, Muy, Vux, Vuy)');
        }
    }

    updateStateMachine() {
        // 1. 형상 및 배근 모드 토글
        const shape = document.querySelector('input[name="radShape"]:checked').value;
        const rebarMode = document.querySelector('input[name="radRebarMode"]:checked')?.value || 'EQUAL';

        if (shape === 'RECT') {
            this.rectFields.style.display = 'block';
            this.circleFields.style.display = 'none';
            this.circleBarFields.style.display = 'none';

            if (rebarMode === 'PER_FACE') {
                this.rectBarFields.style.display = 'none';
                this.perFaceBarFields.style.display = 'block';
                this.singleBarDiamField.style.display = 'none';
                this.diffBarCheckField.style.display = 'none';
                this.diffBarOptions.style.display = 'none';
            } else {
                this.rectBarFields.style.display = 'block';
                this.perFaceBarFields.style.display = 'none';
                this.singleBarDiamField.style.display = 'block';
                this.diffBarCheckField.style.display = 'block';
                if (this.chkUseDiffBar && this.diffBarOptions) {
                    this.diffBarOptions.style.display = this.chkUseDiffBar.checked ? 'grid' : 'none';
                    this.selBarDiam.disabled = this.chkUseDiffBar.checked;
                }
            }
        } else {
            this.rectFields.style.display = 'none';
            this.circleFields.style.display = 'block';
            this.rectBarFields.style.display = 'none';
            this.perFaceBarFields.style.display = 'none';
            this.circleBarFields.style.display = 'block';
            this.singleBarDiamField.style.display = 'block';
            this.diffBarCheckField.style.display = 'none';
            this.diffBarOptions.style.display = 'none';
        }

        // 2. 경량콘크리트 토글
        this.numLambda.disabled = !this.chkLcon.checked;
        if (!this.chkLcon.checked) this.numLambda.value = "1.00";

        // 3. 단부 띠철근 토글
        this.numEndTieSpacing.disabled = !this.chkUseEndTie.checked;
        if (this.chkUseEndTie.checked && parseFloat(this.numEndTieSpacing.value) > parseFloat(this.numTieSpacing.value)) {
            this.numEndTieSpacing.value = Math.round(parseFloat(this.numTieSpacing.value) / 2);
        }

        // 4. 내진 토글
        if (this.chkSeismic.checked) {
            this.seismicSubOptions.style.opacity = '1.0';
            this.seismicSubOptions.style.pointerEvents = 'auto';
        } else {
            this.seismicSubOptions.style.opacity = '0.5';
            this.seismicSubOptions.style.pointerEvents = 'none';
        }

        // 5. 철근비 사용자 지정 토글
        this.userRhoOptions.style.display = this.chkUserRho.checked ? 'grid' : 'none';
    }

    collectInput() {
        const shape = document.querySelector('input[name="radShape"]:checked').value;
        const splice_type = document.querySelector('input[name="radSplice"]:checked').value;
        const frame_type = document.querySelector('input[name="radFrame"]:checked').value;
        const rebarMode = document.querySelector('input[name="radRebarMode"]:checked')?.value || 'EQUAL';

        let Nx = parseInt(this.numNx.value);
        let Ny = parseInt(this.numNy.value);
        let bar_diam = parseFloat(this.selBarDiam.value);
        let use_diff_bar = this.chkUseDiffBar ? this.chkUseDiffBar.checked : false;
        let corner_bar_diam = this.selCornerBarDiam ? parseFloat(this.selCornerBarDiam.value) : 25.0;
        let side_bar_diam = this.selSideBarDiam ? parseFloat(this.selSideBarDiam.value) : 22.0;
        let side_x_bars = parseInt(this.numSideXBars?.value || 2);
        let side_y_bars = parseInt(this.numSideYBars?.value || 2);

        if (shape === 'RECT' && rebarMode === 'PER_FACE') {
            Nx = side_x_bars + 2;
            Ny = side_y_bars + 2;
            corner_bar_diam = parseFloat(this.selPerFaceCornerDiam.value);
            side_bar_diam = parseFloat(this.selSideXBarDiam.value);
            bar_diam = corner_bar_diam;
            use_diff_bar = true;
        }

        return {
            fck: parseFloat(this.selFck.value),
            fy: parseFloat(this.selFy.value),
            fys: parseFloat(this.selFys.value),
            is_lcon: this.chkLcon.checked,
            lambda_factor: parseFloat(this.numLambda.value),
            shape: shape,
            b: parseFloat(this.numWidth.value),
            h: parseFloat(this.numHeight.value),
            r: parseFloat(this.numCorner.value),
            D: parseFloat(this.numDiameter.value),
            cc: parseFloat(this.numCover.value),
            Lux: parseFloat(this.numLux.value),
            Luy: parseFloat(this.numLuy.value),
            Kx: parseFloat(this.numKx.value),
            Ky: parseFloat(this.numKy.value),
            Cmx: parseFloat(this.numCmx.value),
            Cmy: parseFloat(this.numCmy.value),
            beta_d: parseFloat(this.numBetaD.value),
            chk_2nd: this.chk2ndOrder.checked,
            Pu: parseFloat(this.numPu.value),
            Mux: parseFloat(this.numMux.value),
            Muy: parseFloat(this.numMuy.value),
            Vux: parseFloat(this.numVux.value),
            Vuy: parseFloat(this.numVuy.value),
            apply_ax2sh: this.chkApply2Shear.checked,
            load_combinations: this.loadCombinations,
            Nx: Nx,
            Ny: Ny,
            Ncir: parseInt(this.numNcir.value),
            bar_diam: bar_diam,
            rebar_mode: rebarMode,
            use_diff_bar: use_diff_bar,
            corner_bar_diam: corner_bar_diam,
            side_bar_diam: side_bar_diam,
            side_x_bars: side_x_bars,
            side_y_bars: side_y_bars,
            d_agg: this.numModalDagg ? parseFloat(this.numModalDagg.value) : 25.0,
            tie_type: this.selTieType.value,
            tie_diam: parseFloat(this.selTieDiam.value),
            tie_pattern: this.selTiePattern ? this.selTiePattern.value : "TYPE_1",
            s_mid: parseFloat(this.numTieSpacing.value),
            use_end_tie: this.chkUseEndTie.checked,
            s_end: parseFloat(this.numEndTieSpacing.value),
            tie_legs_x: parseInt(this.numLegsX.value),
            tie_legs_y: parseInt(this.numLegsY.value),
            chk_tiebar: this.chkTiebar.checked,
            splice_type: splice_type,
            chk_seismic: this.chkSeismic.checked,
            frame_type: frame_type,
            chk_piloti: this.chkPiloti.checked,
            omega_0: 3.0,
            chk_user_rho: this.chkUserRho.checked,
            min_rho: parseFloat(this.numMinRho.value),
            max_rho: parseFloat(this.numMaxRho.value),
            chk_serv: false,
            k1: 0.6, k2: 0.8, k3: 0.7
        };
    }

    async runCheck() {
        const inp = this.collectInput();
        try {
            const resp = await fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inp)
            });
            if (!resp.ok) throw new Error(await resp.text());
            const data = await resp.json();
            this.lastResult = data;
            this.applyResultToUI(data);
        } catch (err) {
            console.error(err);
        }
    }

    async runAutoDesign() {
        const inp = this.collectInput();
        try {
            const resp = await fetch('/api/auto-design', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inp)
            });
            if (!resp.ok) throw new Error(await resp.text());
            const data = await resp.json();
            const opt = data.optimized_input;

            // UI 필드 업데이트
            this.numWidth.value = opt.b;
            this.numHeight.value = opt.h;
            this.numDiameter.value = opt.D;
            this.numNx.value = opt.Nx;
            this.numNy.value = opt.Ny;
            this.numNcir.value = opt.Ncir;
            this.selBarDiam.value = opt.bar_diam.toString();

            this.lastResult = data.result;
            this.applyResultToUI(data.result);
            alert(`자동 설계 완료!\n최적 단면: ${opt.b}x${opt.h}mm, 주철근: ${opt.Nx}x${opt.Ny}-D${opt.bar_diam}\n최대 DCR: ${data.result.max_dcr}`);
        } catch (err) {
            console.error(err);
            alert('자동설계 오류: ' + err.message);
        }
    }

    applyResultToUI(res) {
        // 배지 및 라벨 갱신
        this.lblOverallStatus.className = `status-badge ${res.overall_status === 'OK' ? 'ok' : 'ng'}`;
        this.lblOverallStatus.innerText = `판정: ${res.overall_status} (DCR ${res.max_dcr})`;

        this.lblTotalBars.innerText = res.total_bars;
        this.lblRhoG.innerText = (res.rho_g * 100).toFixed(2);
        this.lblClearSpacing.innerText = res.s_clear.toFixed(1);
        if (this.lblClearSpacingStatus) {
            this.lblClearSpacingStatus.innerText = res.is_sclear_ok ? 'OK' : 'NG';
            this.lblClearSpacingStatus.style.color = res.is_sclear_ok ? '#16a34a' : '#dc2626';
        }

        this.lblP0.innerText = res.P0.toFixed(1);
        this.lblPhiPnMax.innerText = res.phi_Pn_max.toFixed(1);
        this.lblMc.innerText = `${res.Mc_x.toFixed(1)} / ${res.Mc_y.toFixed(1)}`;
        this.lblPhiVn.innerText = `${res.phi_Vnx.toFixed(1)} / ${res.phi_Vny.toFixed(1)}`;
        this.lblMaxDcr.innerText = res.max_dcr.toFixed(3);
        this.lblCritName.innerText = res.critical_case.name;

        // 이음
        this.lblLsTens.innerText = res.splice.ls_tens > 0 ? res.splice.ls_tens.toFixed(1) : '-';
        this.lblLscComp.innerText = res.splice.lsc_comp > 0 ? res.splice.lsc_comp.toFixed(1) : '-';

        // 내진
        this.lblLo.innerText = res.seismic.lo.toFixed(1);
        this.lblSoLimit.innerText = res.seismic.so_limit.toFixed(1);
        this.lblAshReq.innerText = res.seismic.Ash_req.toFixed(1);

        // 캔버스 드로잉
        this.renderSectionCanvas(res.geometry);
        this.renderPMCanvas(res);
    }

    renderSectionCanvas(geom) {
        const cv = this.canvasSection;
        const ctx = cv.getContext('2d');
        const w = cv.width;
        const h = cv.height;

        ctx.clearRect(0, 0, w, h);

        // 스케일 계산
        const maxDim = Math.max(geom.b, geom.h) * 1.4;
        const scale = Math.min(w, h) / maxDim;
        const cx = w / 2;
        const cy = h / 2;

        // 콘크리트 외곽선 드로잉 (라운딩 반영)
        ctx.beginPath();
        if (geom.shape === 'RECT') {
            const pts = geom.outline;
            ctx.moveTo(cx + pts[0].x * scale, cy - pts[0].y * scale);
            for (let i = 1; i < pts.length; i++) {
                ctx.lineTo(cx + pts[i].x * scale, cy - pts[i].y * scale);
            }
            ctx.closePath();
        } else {
            ctx.arc(cx, cy, (geom.D / 2.0) * scale, 0, 2 * Math.PI);
        }
        ctx.fillStyle = '#e2e8f0';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#334155';
        ctx.stroke();

        // 띠철근 루프 드로잉 (4종 타이바 지원)
        geom.ties.forEach(tie => {
            ctx.beginPath();
            ctx.strokeStyle = tie.color || '#2563eb';
            ctx.lineWidth = tie.line_width || 1.8;
            const pts = tie.points;
            ctx.moveTo(cx + pts[0].x * scale, cy - pts[0].y * scale);
            for (let i = 1; i < pts.length; i++) {
                ctx.lineTo(cx + pts[i].x * scale, cy - pts[i].y * scale);
            }
            if (tie.closed) ctx.closePath();
            ctx.stroke();
        });

        // 주철근 드로잉 (코너/변 이종배근 색상 구분)
        geom.rebars.forEach(r => {
            ctx.beginPath();
            const rPx = Math.max(3, (r.diameter / 2.0) * scale);
            ctx.arc(cx + r.x * scale, cy - r.y * scale, rPx, 0, 2 * Math.PI);

            if (r.is_corner) {
                ctx.fillStyle = '#f59e0b'; // Gold/Amber for corner bars
                ctx.strokeStyle = '#b45309';
            } else {
                ctx.fillStyle = '#dc2626'; // Red for side bars
                ctx.strokeStyle = '#7f1d1d';
            }

            ctx.fill();
            ctx.lineWidth = 1.2;
            ctx.stroke();
        });

        // 치수 텍스트
        ctx.fillStyle = '#475569';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        if (geom.shape === 'RECT') {
            ctx.fillText(`${geom.b} mm`, cx, cy + (geom.h / 2) * scale + 18);
            ctx.save();
            ctx.translate(cx - (geom.b / 2) * scale - 14, cy);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText(`${geom.h} mm`, 0, 0);
            ctx.restore();
        } else {
            ctx.fillText(`D = ${geom.D} mm`, cx, cy + (geom.D / 2) * scale + 18);
        }
    }

    renderPMCanvas(res) {
        if (this.currentAxis === '3D') {
            this.renderPM3D(res);
            return;
        }

        const cv = this.canvasPM;
        const ctx = cv.getContext('2d');
        const w = cv.width;
        const h = cv.height;

        ctx.clearRect(0, 0, w, h);

        const curve = (this.currentAxis === 'X') ? res.curve_x : res.curve_y;
        if (!curve || curve.length === 0) return;

        // 스케일 산정
        const maxP = Math.max(...curve.map(p => p.phi_P)) * 1.15;
        const minP = Math.min(...curve.map(p => p.phi_P)) * 1.15;
        const maxM = Math.max(...curve.map(p => (this.currentAxis === 'X' ? p.phi_Mx : p.phi_My))) * 1.25;

        const margin = { left: 45, right: 25, top: 20, bottom: 30 };
        const plotW = w - margin.left - margin.right;
        const plotH = h - margin.top - margin.bottom;

        const pRange = maxP - minP || 1.0;
        const toX = m => margin.left + (m / maxM) * plotW;
        const toY = p => margin.top + ((maxP - p) / pRange) * plotH;

        // 격자선 및 축
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i <= 4; i++) {
            const mVal = (maxM * i / 4);
            const x = toX(mVal);
            ctx.moveTo(x, margin.top);
            ctx.lineTo(x, h - margin.bottom);
        }
        for (let j = 0; j <= 4; j++) {
            const pVal = minP + (pRange * j / 4);
            const y = toY(pVal);
            ctx.moveTo(margin.left, y);
            ctx.lineTo(w - margin.right, y);
        }
        ctx.stroke();

        // 0 축선
        const y0 = toY(0);
        ctx.strokeStyle = '#94a3b8';
        ctx.beginPath();
        ctx.moveTo(margin.left, y0);
        ctx.lineTo(w - margin.right, y0);
        ctx.stroke();

        // P-M 곡선 패스 드로잉
        ctx.beginPath();
        ctx.strokeStyle = '#2563eb';
        ctx.lineWidth = 2.5;

        curve.forEach((pt, idx) => {
            const m = (this.currentAxis === 'X') ? pt.phi_Mx : pt.phi_My;
            const px = toX(m);
            const py = toY(pt.phi_P);
            if (idx === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });
        ctx.stroke();

        // 설계 하중점 플롯 (다중 하중조합)
        res.comb_results.forEach(lc => {
            const m = (this.currentAxis === 'X') ? lc.Mux : lc.Muy;
            const px = toX(m);
            const py = toY(lc.Pu);

            ctx.beginPath();
            ctx.arc(px, py, 4, 0, 2 * Math.PI);
            ctx.fillStyle = (lc.status === 'OK') ? '#10b981' : '#ef4444';
            ctx.fill();
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 1;
            ctx.stroke();

            // 라벨
            ctx.fillStyle = '#0f172a';
            ctx.font = '10px sans-serif';
            ctx.fillText(lc.name, px + 6, py - 4);
        });

        // 축 라벨
        ctx.fillStyle = '#64748b';
        ctx.font = '10.5px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`M${this.currentAxis.toLowerCase()} (kN·m)`, w - margin.right, y0 - 6);
        ctx.textAlign = 'left';
        ctx.fillText('P (kN)', margin.left + 6, margin.top + 12);
    }

    renderPM3D(res) {
        const cv = this.canvasPM;
        const ctx = cv.getContext('2d');
        const w = cv.width;
        const h = cv.height;

        ctx.clearRect(0, 0, w, h);

        const curveX = res.curve_x;
        const curveY = res.curve_y;
        if (!curveX || !curveY) return;

        // 3D Projection Configuration
        const maxP = Math.max(...curveX.map(p => p.phi_P)) * 1.1;
        const maxMx = Math.max(...curveX.map(p => p.phi_Mx)) * 1.2;
        const maxMy = Math.max(...curveY.map(p => p.phi_My)) * 1.2;

        const radX = (this.rotX * Math.PI) / 180.0;
        const radZ = (this.rotZ * Math.PI) / 180.0;

        const cx = w / 2;
        const cy = h / 2 + 20;
        const scale3d = Math.min(w, h) * 0.38;

        // 3D Point to 2D Screen Projection
        const project = (mx, my, p) => {
            const normMx = mx / (maxMx || 1.0);
            const normMy = my / (maxMy || 1.0);
            const normP = (p / (maxP || 1.0)) * 1.6;

            // Rotate about Z-axis
            const x1 = normMx * Math.cos(radZ) - normMy * Math.sin(radZ);
            const y1 = normMx * Math.sin(radZ) + normMy * Math.cos(radZ);
            const z1 = normP;

            // Rotate about X-axis (pitch)
            const y2 = y1 * Math.cos(radX) - z1 * Math.sin(radX);
            const z2 = y1 * Math.sin(radX) + z1 * Math.cos(radX);

            return {
                x: cx + x1 * scale3d,
                y: cy - z2 * scale3d
            };
        };

        // 1. Draw 3D Axes
        ctx.lineWidth = 1.2;
        const origin = project(0, 0, 0);

        // P Axis (Vertical)
        const pAxis = project(0, 0, maxP);
        ctx.strokeStyle = '#64748b';
        ctx.beginPath();
        ctx.moveTo(origin.x, origin.y);
        ctx.lineTo(pAxis.x, pAxis.y);
        ctx.stroke();

        // Mx Axis
        const mxAxis = project(maxMx, 0, 0);
        ctx.strokeStyle = '#ef4444';
        ctx.beginPath();
        ctx.moveTo(origin.x, origin.y);
        ctx.lineTo(mxAxis.x, mxAxis.y);
        ctx.stroke();

        // My Axis
        const myAxis = project(0, maxMy, 0);
        ctx.strokeStyle = '#10b981';
        ctx.beginPath();
        ctx.moveTo(origin.x, origin.y);
        ctx.lineTo(myAxis.x, myAxis.y);
        ctx.stroke();

        // Axis Labels
        ctx.font = '11px sans-serif';
        ctx.fillStyle = '#64748b';
        ctx.fillText('P (kN)', pAxis.x + 4, pAxis.y - 4);
        ctx.fillStyle = '#ef4444';
        ctx.fillText('Mx', mxAxis.x + 6, mxAxis.y + 4);
        ctx.fillStyle = '#10b981';
        ctx.fillText('My', myAxis.x + 6, myAxis.y + 4);

        // 2. Wireframe 3D Surface Rings (Elliptical Slices along P levels)
        const numRings = 14;
        const ringStep = maxP / numRings;

        ctx.strokeStyle = 'rgba(37, 99, 235, 0.45)';
        ctx.lineWidth = 1.0;

        for (let k = 1; k <= numRings; k++) {
            const pVal = k * ringStep;
            const capMx = this.interpolateCapacity(curveX, pVal, 'X');
            const capMy = this.interpolateCapacity(curveY, pVal, 'Y');

            if (capMx <= 1.0 && capMy <= 1.0) continue;

            ctx.beginPath();
            for (let deg = 0; deg <= 360; deg += 15) {
                const rad = (deg * Math.PI) / 180.0;
                const curMx = Math.max(0, capMx * Math.cos(rad));
                const curMy = Math.max(0, capMy * Math.sin(rad));
                const pt = project(curMx, curMy, pVal);

                if (deg === 0) ctx.moveTo(pt.x, pt.y);
                else ctx.lineTo(pt.x, pt.y);
            }
            ctx.stroke();
        }

        // 3. Meridians (Longitudinal Wireframe Lines)
        const meridians = [0, 30, 60, 90, 180, 270];
        ctx.strokeStyle = 'rgba(37, 99, 235, 0.35)';

        meridians.forEach(deg => {
            ctx.beginPath();
            const rad = (deg * Math.PI) / 180.0;
            for (let k = 1; k <= numRings; k++) {
                const pVal = k * ringStep;
                const capMx = this.interpolateCapacity(curveX, pVal, 'X');
                const capMy = this.interpolateCapacity(curveY, pVal, 'Y');
                const curMx = Math.max(0, capMx * Math.cos(rad));
                const curMy = Math.max(0, capMy * Math.sin(rad));
                const pt = project(curMx, curMy, pVal);
                if (k === 1) ctx.moveTo(pt.x, pt.y);
                else ctx.lineTo(pt.x, pt.y);
            }
            ctx.stroke();
        });

        // 4. Plot Demand Load Combination Points in 3D Space
        res.comb_results.forEach(lc => {
            const pt = project(lc.Mux, lc.Muy, lc.Pu);

            // Drop line to base plane
            const basePt = project(lc.Mux, lc.Muy, 0);
            ctx.strokeStyle = 'rgba(100, 116, 139, 0.35)';
            ctx.setLineDash([2, 2]);
            ctx.beginPath();
            ctx.moveTo(pt.x, pt.y);
            ctx.lineTo(basePt.x, basePt.y);
            ctx.stroke();
            ctx.setLineDash([]);

            // Marker sphere
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 4.5, 0, 2 * Math.PI);
            ctx.fillStyle = (lc.status === 'OK') ? '#10b981' : '#ef4444';
            ctx.fill();
            ctx.strokeStyle = '#0f172a';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            // Label
            ctx.fillStyle = '#0f172a';
            ctx.font = 'bold 10px sans-serif';
            ctx.fillText(lc.name, pt.x + 6, pt.y - 3);
        });
    }

    interpolateCapacity(curve, targetP, axis) {
        if (!curve || curve.length === 0) return 0.0;
        const sorted = [...curve].sort((a, b) => b.phi_P - a.phi_P);
        if (targetP >= sorted[0].phi_P) return 0.0;
        if (targetP <= sorted[sorted.length - 1].phi_P) return 0.0;

        for (let i = 0; i < sorted.length - 1; i++) {
            const p1 = sorted[i].phi_P;
            const p2 = sorted[i + 1].phi_P;
            if (p1 >= targetP && targetP >= p2) {
                const m1 = (axis === 'X') ? sorted[i].phi_Mx : sorted[i].phi_My;
                const m2 = (axis === 'X') ? sorted[i + 1].phi_Mx : sorted[i + 1].phi_My;
                const frac = (p1 - p2) !== 0 ? (targetP - p2) / (p1 - p2) : 0;
                return Math.max(0, m2 + frac * (m1 - m2));
            }
        }
        return 0.0;
    }

    renderLcombTable() {
        this.tbodyLcomb.innerHTML = '';
        this.loadCombinations.forEach((lc, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><input type="checkbox" class="chk-lc" data-no="${lc.no}"></td>
                <td>${lc.no}</td>
                <td><input type="text" class="inp-lc-name" value="${lc.name}"></td>
                <td><input type="number" class="inp-lc-pu" value="${lc.Pu}"></td>
                <td><input type="number" class="inp-lc-mux" value="${lc.Mux}"></td>
                <td><input type="number" class="inp-lc-muy" value="${lc.Muy}"></td>
                <td><input type="number" class="inp-lc-vux" value="${lc.Vux}"></td>
                <td><input type="number" class="inp-lc-vuy" value="${lc.Vuy}"></td>
                <td>${this.lastResult ? (this.lastResult.comb_results[idx]?.dcr_pm || '-') : '-'}</td>
                <td><span class="badge-${this.lastResult ? this.lastResult.comb_results[idx]?.status : 'OK'}">${this.lastResult ? this.lastResult.comb_results[idx]?.status : 'OK'}</span></td>
            `;
            this.tbodyLcomb.appendChild(tr);
        });
    }

    collectLcombFromTable() {
        const rows = this.tbodyLcomb.querySelectorAll('tr');
        const newList = [];
        rows.forEach((r, idx) => {
            newList.push({
                no: idx + 1,
                name: r.querySelector('.inp-lc-name').value,
                Pu: parseFloat(r.querySelector('.inp-lc-pu').value),
                Mux: parseFloat(r.querySelector('.inp-lc-mux').value),
                Muy: parseFloat(r.querySelector('.inp-lc-muy').value),
                Vux: parseFloat(r.querySelector('.inp-lc-vux').value),
                Vuy: parseFloat(r.querySelector('.inp-lc-vuy').value)
            });
        });
        if (newList.length > 0) {
            this.loadCombinations = newList;
            this.numPu.value = newList[0].Pu;
            this.numMux.value = newList[0].Mux;
            this.numMuy.value = newList[0].Muy;
            this.numVux.value = newList[0].Vux;
            this.numVuy.value = newList[0].Vuy;
        }
    }

    showReportModal() {
        if (!this.lastResult) return alert('먼저 계산을 수행하세요.');
        const r = this.lastResult;
        const inp = this.collectInput();

        const kx = (tex) => {
            if (window.katex && typeof window.katex.renderToString === 'function') {
                try {
                    return window.katex.renderToString(tex, { throwOnError: false, displayMode: false });
                } catch (e) {
                    return `<span>${tex}</span>`;
                }
            }
            return `<code>${tex}</code>`;
        };

        const kxBlock = (tex) => {
            if (window.katex && typeof window.katex.renderToString === 'function') {
                try {
                    return window.katex.renderToString(tex, { throwOnError: false, displayMode: true });
                } catch (e) {
                    return `<div style="text-align:center;margin:6px 0;"><code>${tex}</code></div>`;
                }
            }
            return `<div style="text-align:center;margin:6px 0;"><code>${tex}</code></div>`;
        };

        const today = new Date().toISOString().split('T')[0];

        // 1. P-M Curve SVG 생성
        let pmSvg = '';
        if (r.curve_x && r.curve_x.length > 0) {
            const svgW = 320, svgH = 200, padL = 45, padR = 25, padT = 20, padB = 30;
            const pts = r.curve_x;
            const maxM = Math.max(...pts.map(p => p.phi_Mx), Math.abs(r.critical_case.Mux) * 1.25, 100);
            const maxP = Math.max(...pts.map(p => p.phi_P), r.critical_case.Pu * 1.2, 500);
            const minP = Math.min(...pts.map(p => p.phi_P), 0);

            const tx = (m) => padL + (m / (maxM || 1)) * (svgW - padL - padR);
            const ty = (p) => padT + ((maxP - p) / ((maxP - minP) || 1)) * (svgH - padT - padB);

            let pathD = '';
            pts.forEach((pt, i) => {
                const x = tx(pt.phi_Mx), y = ty(pt.phi_P);
                pathD += (i === 0 ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : ` L ${x.toFixed(1)} ${y.toFixed(1)}`);
            });

            const critX = tx(Math.abs(r.critical_case.Mux));
            const critY = ty(r.critical_case.Pu);

            pmSvg = `
                <svg width="${svgW}" height="${svgH}" style="background:#ffffff;border:1px solid #cbd5e1;border-radius:4px;">
                    <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${svgH - padB}" stroke="#475569" stroke-width="1.2"/>
                    <line x1="${padL}" y1="${ty(0)}" x2="${svgW - padR}" y2="${ty(0)}" stroke="#475569" stroke-width="1.2"/>
                    <text x="${padL - 4}" y="${padT + 10}" text-anchor="end" font-size="9" fill="#475569">φPn (kN)</text>
                    <text x="${svgW - padR}" y="${ty(0) - 4}" text-anchor="end" font-size="9" fill="#475569">φMn (kN·m)</text>
                    <path d="${pathD}" fill="rgba(37, 99, 235, 0.08)" stroke="#2563eb" stroke-width="2"/>
                    <circle cx="${critX.toFixed(1)}" cy="${critY.toFixed(1)}" r="4" fill="#dc2626" stroke="#ffffff" stroke-width="1.5"/>
                    <text x="${(critX + 6).toFixed(1)}" y="${(critY - 4).toFixed(1)}" font-size="9" font-weight="bold" fill="#dc2626">${r.critical_case.name}</text>
                </svg>
            `;
        }

        // A4 구조계산서 HTML 조립
        let html = `
            <!-- 표제부 (Header) -->
            <div class="sheet-doc-header">
                <div class="sheet-main-title">
                    <h1>구조계산서 (RC 기둥 설계 검토)</h1>
                    <div class="sub">Midas Design+ 1:1 Engine & KDS 기준 완전 부합 구조설계 검토서</div>
                </div>
                <div class="sheet-verdict-box">
                    <div class="sheet-verdict-badge ${r.overall_status === 'OK' ? 'ok' : 'ng'}">
                        ${r.overall_status === 'OK' ? '적 합 (OK)' : '부 적 합 (NG)'}
                    </div>
                    <div style="font-size:11px;color:#64748b;margin-top:3px;">최대 DCR = <strong>${r.max_dcr.toFixed(3)}</strong> (${r.critical_case.name})</div>
                </div>
            </div>

            <!-- 메타정보 그리드 -->
            <div class="sheet-meta-grid">
                <div class="meta-item"><span>프로젝트명</span><strong>AltDP 표준 부재 설계</strong></div>
                <div class="meta-item"><span>부재 번호</span><strong>C1 (RC Column)</strong></div>
                <div class="meta-item"><span>설계 기준</span><strong>KDS 14 20 00 / 41 17 00</strong></div>
                <div class="meta-item"><span>검토 일자</span><strong>${today}</strong></div>
            </div>

            <!-- Chapter 1. 설계 조건 및 재료 제원 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>1. 설계 조건 및 재료 제원 (Design Criteria & Materials)</span>
                    <span class="ref-code">KDS 14 20 10 / KDS 14 20 20</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>구분</th>
                                <th>기호</th>
                                <th>설계 수치</th>
                                <th>단위</th>
                                <th>비고</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="left">콘크리트 설계기준압축강도</td>
                                <td>${kx('f_{ck}')}</td>
                                <td><strong>${inp.fck}</strong></td>
                                <td>MPa</td>
                                <td>${inp.is_lcon ? '경량콘크리트 (λ=' + inp.lambda_factor + ')' : '보통콘크리트'}</td>
                            </tr>
                            <tr>
                                <td class="left">주철근 설계기준항복강도</td>
                                <td>${kx('f_y')}</td>
                                <td><strong>${inp.fy}</strong></td>
                                <td>MPa</td>
                                <td>탄성계수 ${kx('E_s = 200,000')} MPa</td>
                            </tr>
                            <tr>
                                <td class="left">띠철근 설계기준항복강도</td>
                                <td>${kx('f_{ys}')}</td>
                                <td><strong>${inp.fys}</strong></td>
                                <td>MPa</td>
                                <td>횡보강용 전단철근</td>
                            </tr>
                            <tr>
                                <td class="left">콘크리트 할선탄성계수</td>
                                <td>${kx('E_c')}</td>
                                <td><strong>${r.Ec || (8500 * Math.cbrt(inp.fck + 4)).toFixed(1)}</strong></td>
                                <td>MPa</td>
                                <td>${kx('E_c = 8500 \\sqrt[3]{f_{ck} + \\Delta f}')}</td>
                            </tr>
                            <tr>
                                <td class="left">등가 직사각형 응력블록 계수</td>
                                <td>${kx('\\beta_1')}</td>
                                <td><strong>${r.beta1 || (inp.fck <= 28 ? 0.85 : Math.max(0.65, 0.85 - 0.05 * (inp.fck - 28) / 7)).toFixed(3)}</strong></td>
                                <td>-</td>
                                <td>${kx('\\beta_1 = 0.85 - 0.05(f_{ck}-28)/7 \\ge 0.65')}</td>
                            </tr>
                            <tr>
                                <td class="left">단면 총단면적 / 모멘트관성</td>
                                <td>${kx('A_g, I_g')}</td>
                                <td><strong>${r.Ag.toFixed(1)}</strong></td>
                                <td>mm²</td>
                                <td>${inp.shape === 'RECT' ? `b=${inp.b}mm, h=${inp.h}mm, r=${inp.r}mm` : `D=${inp.D}mm`}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Chapter 2. 주철근 배근 및 순간격 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>2. 주철근 배근 및 순간격 검토 (Reinforcement & Spacing)</span>
                    <span class="ref-code">KDS 14 20 20 (4.1.2) / KDS 14 20 50</span>
                </div>
                <div class="sheet-section">
                    <div class="sheet-formula-box">
                        <div class="math-line">
                            ${kx('\\text{총 주철근량 } A_{st} = ' + r.Ast.toFixed(1) + '\\text{ mm}^2, \\quad \\text{철근비 } \\rho_g = \\frac{A_{st}}{A_g} = \\frac{' + r.Ast.toFixed(1) + '}{' + r.Ag.toFixed(1) + '} = ' + (r.rho_g * 100).toFixed(2) + '\\%')}
                        </div>
                        <div class="sub-step">
                            기준 허용 범위: ${kx('1.0\\% \\le \\rho_g \\le 4.0\\%')} (사용자 지정: ${kx(inp.min_rho * 100 + '\\% \\sim ' + inp.max_rho * 100 + '\\%')})
                        </div>
                    </div>
                    <div class="sheet-result-line">
                        <span>철근비 판정: <strong>ρ = ${(r.rho_g * 100).toFixed(2)}%</strong></span>
                        <span class="${r.is_rho_ok ? 'badge-pass' : 'badge-fail'}">${r.is_rho_ok ? 'OK (적합)' : 'NG (철근비 제한 초과)'}</span>
                    </div>

                    <div class="sheet-formula-box" style="margin-top:8px;">
                        <div class="math-line">
                            ${kx('\\text{주철근 순 순간격 } s_{clear} = ' + r.s_clear.toFixed(1) + '\\text{ mm} \\ge s_{\\min} = \\max(1.5 d_b, 25\\text{ mm}, 1.33 d_{agg}) = ' + (r.s_clear_min || 25.0) + '\\text{ mm}')}
                        </div>
                    </div>
                    <div class="sheet-result-line">
                        <span>순간격 판정: <strong>s_clear = ${r.s_clear.toFixed(1)} mm</strong> (한계: ${(r.s_clear_min || 25.0)} mm)</span>
                        <span class="${r.is_sclear_ok ? 'badge-pass' : 'badge-fail'}">${r.is_sclear_ok ? 'OK (배근 시공성 만족)' : 'NG (간격 협소)'}</span>
                    </div>
                </div>
            </div>

            <!-- Chapter 3. 순수 축압축 내력 및 최대 축하중 한계 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>3. 축하중 극한 용량 검토 (Pure Axial Capacity)</span>
                    <span class="ref-code">KDS 14 20 20 (4.1.2)</span>
                </div>
                <div class="sheet-section">
                    <div class="sheet-formula-box">
                        <div class="math-line">
                            ${kx('P_0 = 0.85 f_{ck} (A_g - A_{st}) + f_y A_{st}')}
                        </div>
                        <div class="sub-step">
                            ${kx('= 0.85 \\times ' + inp.fck + ' \\times (' + r.Ag.toFixed(0) + ' - ' + r.Ast.toFixed(0) + ') + ' + inp.fy + ' \\times ' + r.Ast.toFixed(0) + ' = ' + r.P0.toFixed(1) + '\\text{ kN}')}
                        </div>
                        <div class="math-line" style="margin-top:6px;">
                            ${kx('\\phi P_{n,\\max} = ' + (inp.tie_type === 'SPIRAL' ? '0.85 \\times 0.70' : '0.80 \\times 0.65') + ' \\times P_0 = ' + r.phi_Pn_max.toFixed(1) + '\\text{ kN}')}
                        </div>
                    </div>
                    <div class="sheet-result-line">
                        <span>최대 계수 축력 ${kx('P_u = ' + r.critical_case.Pu.toFixed(1) + '\\text{ kN}')} / 설계 허용 한계 ${kx('\\phi P_{n,\\max} = ' + r.phi_Pn_max.toFixed(1) + '\\text{ kN}')}</span>
                        <span class="${r.critical_case.Pu <= r.phi_Pn_max ? 'badge-pass' : 'badge-fail'}">
                            DCR = ${(r.critical_case.Pu / (r.phi_Pn_max || 1)).toFixed(3)} [${r.critical_case.Pu <= r.phi_Pn_max ? 'OK' : 'NG'}]
                        </span>
                    </div>
                </div>
            </div>

            <!-- Chapter 4. 장주 세장비 및 모멘트 확대 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>4. 장주 세장비 및 모멘트 확대 (Moment Magnification)</span>
                    <span class="ref-code">KDS 14 20 20 (4.3)</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>축 방향</th>
                                <th>세장비 (KL/r)</th>
                                <th>한계비</th>
                                <th>장주 여부</th>
                                <th>오일러 좌굴 (Pc)</th>
                                <th>확대계수 (δns)</th>
                                <th>설계모멘트 (Mc)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>X축 (강축)</td>
                                <td>${r.slender_ratio_x}</td>
                                <td>34.0</td>
                                <td><strong>${r.is_slender_x ? '장주 고려' : '단주'}</strong></td>
                                <td>${r.Pc_x} kN</td>
                                <td>${r.delta_ns_x}</td>
                                <td><strong>${r.Mc_x.toFixed(1)} kN·m</strong></td>
                            </tr>
                            <tr>
                                <td>Y축 (약축)</td>
                                <td>${r.slender_ratio_y}</td>
                                <td>34.0</td>
                                <td><strong>${r.is_slender_y ? '장주 고려' : '단주'}</strong></td>
                                <td>${r.Pc_y} kN</td>
                                <td>${r.delta_ns_y}</td>
                                <td><strong>${r.Mc_y.toFixed(1)} kN·m</strong></td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="sheet-formula-box">
                        <div class="math-line">
                            ${kx('E I = \\frac{0.40 E_c I_g}{1 + \\beta_{dns}}, \\quad P_c = \\frac{\\pi^2 E I}{(K L_u)^2}, \\quad \\delta_{ns} = \\frac{C_m}{1 - P_u / (0.75 P_c)} \\ge 1.0')}
                        </div>
                        <div class="sub-step">
                            최소 편심 모멘트: ${kx('e_{\\min} = 15 + 0.03 h, \\quad M_{2,\\min} = P_u e_{\\min}')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chapter 5. 이축 휨-압축 P-M 상관곡선 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>5. 이축 휨-압축 P-M 상관곡선 검토 (Bresler Interaction)</span>
                    <span class="ref-code">KDS 14 20 20 (4.1)</span>
                </div>
                <div class="sheet-section" style="display:flex;gap:16px;align-items:center;">
                    <div style="flex:1;">
                        <div class="sheet-formula-box">
                            <div class="math-line">
                                <strong>Bresler 역수 하중식:</strong>
                            </div>
                            <div class="math-line">
                                ${kx('\\frac{1}{P_n} = \\frac{1}{P_{nx}} + \\frac{1}{P_{ny}} - \\frac{1}{P_0} \\quad \\implies \\quad \\phi P_n \\ge P_u')}
                            </div>
                            <div class="sub-step">
                                200단계 파이버 수치적분 (콘크리트 극한변형률 ${kx('\\epsilon_{cu} = 0.0033')})
                            </div>
                        </div>
                        <div class="sheet-result-line" style="margin-top:6px;">
                            <span>임계 하중조합: <strong>${r.critical_case.name}</strong> (Pu=${r.critical_case.Pu} kN, Mux=${r.critical_case.Mux} kN·m)</span>
                            <span class="${r.critical_case.dcr_pm <= 1.0 ? 'badge-pass' : 'badge-fail'}">
                                DCR_PM = ${r.critical_case.dcr_pm.toFixed(3)} [${r.critical_case.dcr_pm <= 1.0 ? 'OK' : 'NG'}]
                            </span>
                        </div>
                    </div>
                    <div style="text-align:center;">
                        ${pmSvg}
                        <div style="font-size:10px;color:#64748b;margin-top:2px;">[X축 φPn - φMn 상관곡선 및 설계점]</div>
                    </div>
                </div>
            </div>

            <!-- Chapter 6. 전단 강도 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>6. 전단 강도 검토 (Shear Strength)</span>
                    <span class="ref-code">KDS 14 20 22 (4.2)</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>방향</th>
                                <th>계수전단력 (Vu)</th>
                                <th>콘크리트 (Vc)</th>
                                <th>띠철근 (Vs)</th>
                                <th>설계전단강도 (φVn)</th>
                                <th>DCR</th>
                                <th>판정</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>X방향</td>
                                <td>${r.critical_case.Vux} kN</td>
                                <td>${r.Vcx} kN</td>
                                <td>${r.Vsx} kN</td>
                                <td>${r.phi_Vnx} kN</td>
                                <td><strong>${r.critical_case.dcr_vx.toFixed(3)}</strong></td>
                                <td><span class="${r.critical_case.dcr_vx <= 1.0 ? 'badge-pass' : 'badge-fail'}">${r.critical_case.dcr_vx <= 1.0 ? 'OK' : 'NG'}</span></td>
                            </tr>
                            <tr>
                                <td>Y방향</td>
                                <td>${r.critical_case.Vuy} kN</td>
                                <td>${r.Vcy} kN</td>
                                <td>${r.Vsy} kN</td>
                                <td>${r.phi_Vny} kN</td>
                                <td><strong>${r.critical_case.dcr_vy.toFixed(3)}</strong></td>
                                <td><span class="${r.critical_case.dcr_vy <= 1.0 ? 'badge-pass' : 'badge-fail'}">${r.critical_case.dcr_vy <= 1.0 ? 'OK' : 'NG'}</span></td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="sheet-formula-box">
                        <div class="math-line">
                            ${kx('V_c = \\frac{1}{6} \\left(1 + \\frac{P_u}{14 A_g}\\right) \\lambda \\sqrt{f_{ck}} b_w d, \\quad V_s = \\frac{A_v f_{ys} d}{s}, \\quad \\phi V_n = 0.75 (V_c + V_s)')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chapter 7. 내진 상세 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>7. 내진 상세 검토 (Seismic Provisions)</span>
                    <span class="ref-code">KDS 14 20 80 / KDS 41 17 00</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>골조 시스템</th>
                                <th>소성힌지 단부길이 (lo)</th>
                                <th>단부 띠철근 간격 (so)</th>
                                <th>심부구속면적 (Ash)</th>
                                <th>필로티 적용</th>
                                <th>판정</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>${r.seismic.frame_type}</strong></td>
                                <td>${r.seismic.lo.toFixed(1)} mm</td>
                                <td>${r.seismic.so.toFixed(1)} mm (한계: ${r.seismic.so_limit.toFixed(1)})</td>
                                <td>소요: ${r.seismic.Ash_req.toFixed(1)} / 배근: ${r.seismic.Ash_prov_x.toFixed(1)} mm²</td>
                                <td>${r.seismic.piloti_status}</td>
                                <td><span class="${r.seismic.status === 'OK' ? 'badge-pass' : 'badge-fail'}">${r.seismic.status}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Chapter 8. 주철근 겹침이음 검토 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>8. 주철근 겹침이음 검토 (Lap Splice)</span>
                    <span class="ref-code">KDS 14 20 50</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>이음 방식</th>
                                <th>이음 등급</th>
                                <th>기본 인장정착길이 (ld)</th>
                                <th>인장 겹침이음길이 (ls)</th>
                                <th>압축 이음길이 (lsc)</th>
                                <th>상태</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>${r.splice.splice_type}</strong></td>
                                <td>${r.splice.splice_class}</td>
                                <td>${r.splice.ld.toFixed(1)} mm</td>
                                <td><strong>${r.splice.ls_tens.toFixed(1)} mm</strong></td>
                                <td>${r.splice.lsc_comp.toFixed(1)} mm</td>
                                <td><span class="badge-pass">${r.splice.status}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Chapter 9. 하중조합별 종합 검토 요약표 -->
            <div class="sheet-chapter">
                <div class="sheet-chapter-title">
                    <span>9. 하중조합별 전체 검토 요약 (Load Combinations Summary)</span>
                    <span class="ref-code">KDS 14 20 20 / 22</span>
                </div>
                <div class="sheet-section">
                    <table class="sheet-table">
                        <thead>
                            <tr>
                                <th>No</th>
                                <th>하중조합명</th>
                                <th>Pu (kN)</th>
                                <th>Mux (kN·m)</th>
                                <th>Muy (kN·m)</th>
                                <th>Vux (kN)</th>
                                <th>Vuy (kN)</th>
                                <th>DCR (P-M)</th>
                                <th>DCR (V)</th>
                                <th>판정</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${r.comb_results.map(lc => `
                                <tr class="${lc.no === r.critical_case.no ? 'critical' : ''}">
                                    <td>${lc.no}</td>
                                    <td class="left"><strong>${lc.name}</strong> ${lc.no === r.critical_case.no ? '<span style="color:#dc2626;font-size:9px;">[Crit]</span>' : ''}</td>
                                    <td>${lc.Pu.toFixed(1)}</td>
                                    <td>${lc.Mux.toFixed(1)}</td>
                                    <td>${lc.Muy.toFixed(1)}</td>
                                    <td>${lc.Vux.toFixed(1)}</td>
                                    <td>${lc.Vuy.toFixed(1)}</td>
                                    <td><strong>${lc.dcr_pm.toFixed(3)}</strong></td>
                                    <td>${Math.max(lc.dcr_vx, lc.dcr_vy).toFixed(3)}</td>
                                    <td><span class="${lc.status === 'OK' ? 'badge-pass' : 'badge-fail'}">${lc.status}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Chapter 10. 종합 판정 및 결론 -->
            <div class="sheet-chapter" style="margin-bottom:0;">
                <div class="sheet-chapter-title">
                    <span>10. 종합 엔지니어링 판정 (Engineering Conclusion & Approval)</span>
                </div>
                <div class="sheet-section">
                    <div style="background:#f8fafc;border:1.5px solid ${r.overall_status === 'OK' ? '#86efac' : '#fca5a5'};border-radius:6px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-size:13px;font-weight:700;color:${r.overall_status === 'OK' ? '#15803d' : '#b91c1c'};margin-bottom:4px;">
                                결론: 본 기둥 부재 단면은 KDS 국가건설기준에 의거하여 ${r.overall_status === 'OK' ? '모든 내력 및 사용성 한계를 만족(OK)합니다.' : '설계 내력을 초과(NG)하므로 단면 또는 철근 보강이 필요합니다.'}
                            </div>
                            <div style="font-size:11px;color:#475569;">
                                • 최대 안전율 여유도 (Max DCR): <strong>${r.max_dcr.toFixed(3)}</strong> (임계 하중조합: ${r.critical_case.name})<br>
                                • 주철근비 여유도: <strong>${(r.rho_g * 100).toFixed(2)}%</strong> (규정: 1.0% ~ 4.0%) | 순간격: <strong>${r.s_clear.toFixed(1)} mm</strong>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div class="sheet-verdict-badge ${r.overall_status === 'OK' ? 'ok' : 'ng'}">
                                ${r.overall_status === 'OK' ? 'FINAL VERDICT: PASS' : 'FINAL VERDICT: FAIL'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.reportSheet.innerHTML = html;
        this.modalReport.style.display = 'flex';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new RCColumnApp();
});
