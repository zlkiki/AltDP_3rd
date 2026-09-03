/**
 * AltDP_3rd Common Sub-Dialogs (common_dialogs.js)
 * Implements Midas Design+ sub-dialog templates
 */
const CommonDialogs = {
    /**
     * 1. Design Load Combination Dialog (IDD_RCS_DESIGN_LOAD)
     */
    openLoadCombination(current = {}, onApply) {
        const d = current.deadLoad ?? 50;
        const l = current.liveLoad ?? 30;
        const e = current.seismicLoad ?? 0;
        const w = current.windLoad ?? 0;

        const html = `
            <div class="eng-dialog-grid">
                <div class="dialog-field-group">
                    <label>고정하중 (D, Dead Load):</label>
                    <input type="number" id="dlg-load-d" value="${d}" class="form-input">
                    <span class="unit-tag">kN·m</span>
                </div>
                <div class="dialog-field-group">
                    <label>활하중 (L, Live Load):</label>
                    <input type="number" id="dlg-load-l" value="${l}" class="form-input">
                    <span class="unit-tag">kN·m</span>
                </div>
                <div class="dialog-field-group">
                    <label>지진하중 (E, Earthquake):</label>
                    <input type="number" id="dlg-load-e" value="${e}" class="form-input">
                    <span class="unit-tag">kN·m</span>
                </div>
                <div class="dialog-field-group">
                    <label>풍하중 (W, Wind Load):</label>
                    <input type="number" id="dlg-load-w" value="${w}" class="form-input">
                    <span class="unit-tag">kN·m</span>
                </div>
            </div>
            <div class="dialog-calc-preview">
                <div class="preview-title">⚡ KDS 자동 하중조합 결과</div>
                <div id="dlg-lcb-preview" class="preview-result">LCB 2: 1.2D + 1.6L = ${(1.2 * d + 1.6 * l).toFixed(1)} kN·m</div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: '설계 하중 및 하중조합 설정',
            dialogId: 'IDD_RCS_DESIGN_LOAD',
            content: html,
            onConfirm: (modalEl) => {
                const valD = parseFloat(modalEl.querySelector('#dlg-load-d').value) || 0;
                const valL = parseFloat(modalEl.querySelector('#dlg-load-l').value) || 0;
                const valE = parseFloat(modalEl.querySelector('#dlg-load-e').value) || 0;
                const valW = parseFloat(modalEl.querySelector('#dlg-load-w').value) || 0;

                const lcb1 = 1.4 * valD;
                const lcb2 = 1.2 * valD + 1.6 * valL;
                const lcb3 = 1.2 * valD + 1.0 * valL + 1.0 * valE;
                const governing = Math.max(lcb1, lcb2, lcb3);

                if (onApply) {
                    onApply({
                        deadLoad: valD,
                        liveLoad: valL,
                        seismicLoad: valE,
                        windLoad: valW,
                        governingMu: governing
                    });
                }
            }
        });
    },

    /**
     * 2. KS Steel Section DB Selector (IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG)
     */
    openSectionDb(currentSec = 'H-400x200x8x13', onApply) {
        const sections = [
            { name: 'H-300x150x6.5x9', h: 300, b: 150, tw: 6.5, tf: 9, A: 46.78, Ix: 7210 },
            { name: 'H-350x175x7x11', h: 350, b: 175, tw: 7, tf: 11, A: 63.14, Ix: 13600 },
            { name: 'H-400x200x8x13', h: 400, b: 200, tw: 8, tf: 13, A: 84.10, Ix: 23700 },
            { name: 'H-450x200x9x14', h: 450, b: 200, tw: 9, tf: 14, A: 96.76, Ix: 33500 },
            { name: 'H-500x200x10x16', h: 500, b: 200, tw: 10, tf: 16, A: 114.2, Ix: 47800 },
            { name: '□-200x200x6.0', h: 200, b: 200, tw: 6.0, tf: 6.0, A: 45.12, Ix: 2790 },
            { name: '□-300x300x9.0', h: 300, b: 300, tw: 9.0, tf: 9.0, A: 102.1, Ix: 14300 }
        ];

        let listHtml = '';
        sections.forEach(s => {
            const isSel = s.name === currentSec;
            listHtml += `
                <tr class="sec-row ${isSel ? 'selected' : ''}" data-name="${s.name}" data-json='${JSON.stringify(s)}'>
                    <td><strong>${s.name}</strong></td>
                    <td>${s.h}</td>
                    <td>${s.b}</td>
                    <td>${s.tw}</td>
                    <td>${s.tf}</td>
                    <td>${s.Ix}</td>
                </tr>
            `;
        });

        const html = `
            <div class="sec-db-modal-wrap">
                <div class="search-row">
                    <input type="text" id="dlg-sec-filter" placeholder="규격 필터링 검색 (예: 400)..." class="form-input">
                </div>
                <div class="sec-table-container">
                    <table class="sec-table" id="dlg-sec-table">
                        <thead>
                            <tr><th>형강명</th><th>H (mm)</th><th>B (mm)</th><th>t1 (mm)</th><th>t2 (mm)</th><th>Ix (cm⁴)</th></tr>
                        </thead>
                        <tbody>${listHtml}</tbody>
                    </table>
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: 'KS 표준 철골 형강 단면 DB 선택기',
            dialogId: 'IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG',
            width: '600px',
            content: html,
            onConfirm: (modalEl) => {
                const selRow = modalEl.querySelector('.sec-row.selected');
                if (selRow && onApply) {
                    const secData = JSON.parse(selRow.dataset.json);
                    onApply(secData);
                }
            }
        });

        // Row click selection
        setTimeout(() => {
            const table = document.getElementById('dlg-sec-table');
            if (table) {
                table.querySelectorAll('.sec-row').forEach(row => {
                    row.onclick = () => {
                        table.querySelectorAll('.sec-row').forEach(r => r.classList.remove('selected'));
                        row.classList.add('selected');
                    };
                });
            }
        }, 50);
    },

    /**
     * 3. Beam Section Details (T-Flange) (IDD_RCS_BEAM_SECT_DLG)
     */
    openBeamSectionDetail(current = {}, onApply) {
        const be = current.flangeWidth ?? 1000;
        const hf = current.slabThickness ?? 150;

        const html = `
            <div class="eng-dialog-grid">
                <div class="dialog-field-group">
                    <label>T형 플랜지 유효폭 (be):</label>
                    <input type="number" id="dlg-flange-be" value="${be}" class="form-input">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>슬래브 두께 (hf):</label>
                    <input type="number" id="dlg-slab-hf" value="${hf}" class="form-input">
                    <span class="unit-tag">mm</span>
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: '보 단면 상세 형상 및 T-플랜지 설정',
            dialogId: 'IDD_RCS_BEAM_SECT_DLG',
            content: html,
            onConfirm: (modalEl) => {
                const valBe = parseFloat(modalEl.querySelector('#dlg-flange-be').value) || be;
                const valHf = parseFloat(modalEl.querySelector('#dlg-slab-hf').value) || hf;
                if (onApply) onApply({ flangeWidth: valBe, slabThickness: valHf });
            }
        });
    }
};

window.CommonDialogs = CommonDialogs;
