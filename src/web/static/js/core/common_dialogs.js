/**
 * AltDP_3rd Common Sub-Dialogs (common_dialogs.js)
 * Implements Parametric Engineering Sub-Dialog Templates (Req 21-3 & DOCS 07)
 * 1. IDD_RCS_BEAM_BEFF_DLG (IDD_RCS_BEAM_SECT_DLG): T형/L형 보 플랜지 유효폭(beff) 자동 산정 모달
 * 2. IDD_RCS_COLUMN_SWAY_DLG: 기둥 장주 모멘트확대계수(δns, δs) 산정 모달
 * 3. IDD_STEEL_SECTION_DB_DLG (IDD_STL_BEAMCOL_SMODE_INPUT_SECT1_DLG): KS 표준 철골 형강 단면 DB 선택기
 * 4. IDD_LOAD_COMBINATION_DLG (IDD_RCS_DESIGN_LOAD): KDS 41 10 15 기본 하중조합 생성기
 */

const CommonDialogs = {
    /**
     * 1. T형/L형 보 플랜지 유효폭(beff) 자동 산정 모달 (IDD_RCS_BEAM_BEFF_DLG / IDD_RCS_BEAM_SECT_DLG)
     * KDS 14 20 10 제4.3.1조 기준
     */
    openBeamBeffDialog(current = {}, onApply) {
        const bw = current.bw ?? current.b ?? 400;
        const hf = current.hf ?? current.slab_thick ?? 150;
        const ln = current.ln ?? current.l_clear ?? 6000;
        const s = current.s ?? current.beam_spacing ?? 3000;
        const flangeType = current.flangeType || 'T'; // 'T' or 'L'

        const calcBeff = (type, w, h, span, spacing) => {
            if (type === 'T') {
                // T형 보: min(Ln/4, bw + 16*hf, S)
                const c1 = span / 4;
                const c2 = w + 16 * h;
                const c3 = spacing;
                return { beff: Math.round(Math.min(c1, c2, c3)), c1, c2, c3, type: 'T' };
            } else {
                // L형(편측) 보: min(bw + Ln/12, bw + 6*hf, bw + S/2)
                const c1 = w + span / 12;
                const c2 = w + 6 * h;
                const c3 = w + spacing / 2;
                return { beff: Math.round(Math.min(c1, c2, c3)), c1, c2, c3, type: 'L' };
            }
        };

        const initial = calcBeff(flangeType, bw, hf, ln, s);

        const html = `
            <div class="eng-dialog-grid">
                <div class="dialog-field-group" style="grid-column: span 2;">
                    <label>플랜지 형식:</label>
                    <div style="display: flex; gap: 16px; margin-top: 4px;">
                        <label style="display: inline-flex; align-items: center; gap: 4px; cursor: pointer;">
                            <input type="radio" name="dlg-beff-type" value="T" ${flangeType === 'T' ? 'checked' : ''}> 대칭 T형 보 (양측 슬래브)
                        </label>
                        <label style="display: inline-flex; align-items: center; gap: 4px; cursor: pointer;">
                            <input type="radio" name="dlg-beff-type" value="L" ${flangeType === 'L' ? 'checked' : ''}> 편측 L형 보 (단부 테두리보)
                        </label>
                    </div>
                </div>
                <div class="dialog-field-group">
                    <label>복부 폭 (bw):</label>
                    <input type="number" id="dlg-beff-bw" value="${bw}" class="form-input" min="100">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>슬래브 두께 (hf):</label>
                    <input type="number" id="dlg-beff-hf" value="${hf}" class="form-input" min="50">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>보 순경간 (Ln):</label>
                    <input type="number" id="dlg-beff-ln" value="${ln}" class="form-input" min="1000">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>보 중심간격 (S):</label>
                    <input type="number" id="dlg-beff-s" value="${s}" class="form-input" min="1000">
                    <span class="unit-tag">mm</span>
                </div>
            </div>
            <div class="dialog-calc-preview" style="margin-top: 12px;">
                <div class="preview-title">⚡ KDS 14 20 10 플랜지 유효폭 산정 결과</div>
                <div id="dlg-beff-preview" class="preview-result" style="font-size: 13px; font-weight: 700; color: #38bdf8;">
                    유효폭 beff = ${initial.beff} mm
                </div>
                <div id="dlg-beff-formula" style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                    규준 제한치: min(${Math.round(initial.c1)}, ${Math.round(initial.c2)}, ${Math.round(initial.c3)}) mm
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: 'T형/L형 보 플랜지 유효폭(beff) 자동 산정',
            dialogId: 'IDD_RCS_BEAM_BEFF_DLG',
            width: '540px',
            content: html,
            onConfirm: (modalEl) => {
                const type = modalEl.querySelector('input[name="dlg-beff-type"]:checked').value;
                const valBw = parseFloat(modalEl.querySelector('#dlg-beff-bw').value) || bw;
                const valHf = parseFloat(modalEl.querySelector('#dlg-beff-hf').value) || hf;
                const valLn = parseFloat(modalEl.querySelector('#dlg-beff-ln').value) || ln;
                const valS = parseFloat(modalEl.querySelector('#dlg-beff-s').value) || s;
                const res = calcBeff(type, valBw, valHf, valLn, valS);

                if (onApply) {
                    onApply({
                        beff: res.beff,
                        bw: valBw,
                        hf: valHf,
                        ln: valLn,
                        s: valS,
                        flangeType: type
                    });
                }
            }
        });

        // Dynamic update on input
        setTimeout(() => {
            const modalEl = document.getElementById('app-modal-overlay');
            if (!modalEl) return;
            const updatePreview = () => {
                const typeEl = modalEl.querySelector('input[name="dlg-beff-type"]:checked');
                const type = typeEl ? typeEl.value : 'T';
                const valBw = parseFloat(modalEl.querySelector('#dlg-beff-bw')?.value) || bw;
                const valHf = parseFloat(modalEl.querySelector('#dlg-beff-hf')?.value) || hf;
                const valLn = parseFloat(modalEl.querySelector('#dlg-beff-ln')?.value) || ln;
                const valS = parseFloat(modalEl.querySelector('#dlg-beff-s')?.value) || s;
                const res = calcBeff(type, valBw, valHf, valLn, valS);

                const prevEl = modalEl.querySelector('#dlg-beff-preview');
                const formEl = modalEl.querySelector('#dlg-beff-formula');
                if (prevEl) prevEl.innerText = `유효폭 beff = ${res.beff} mm`;
                if (formEl) formEl.innerText = `규준 제한치: min(${Math.round(res.c1)}, ${Math.round(res.c2)}, ${Math.round(res.c3)}) mm`;
            };

            modalEl.querySelectorAll('input').forEach(inp => {
                inp.addEventListener('input', updatePreview);
                inp.addEventListener('change', updatePreview);
            });
        }, 50);
    },

    /**
     * 2. 기둥 장주 모멘트확대계수(δns, δs) 산정 모달 (IDD_RCS_COLUMN_SWAY_DLG)
     * KDS 14 20 20 제4.2.3조 기준
     */
    openColumnSwayDialog(current = {}, onApply) {
        const lu = current.lu ?? current.unbraced_len ?? 3500;
        const k = current.k ?? 1.0;
        const h = current.h ?? current.col_h ?? 500;
        const b = current.b ?? current.col_b ?? 500;
        const pu = current.pu ?? 1500;
        const fck = current.fck ?? 24;
        const m1_m2 = current.m1_m2 ?? 0.5; // M1/M2 (-1.0 to 1.0)
        const frameType = current.frameType || 'nonsway'; // 'nonsway' or 'sway'

        const calcSway = (ft, valLu, valK, valH, valB, valPu, valFck, valMratio) => {
            const r = 0.3 * valH; // 단면 2차 반경 근사치
            const kl_r = (valK * valLu) / r;
            const ec = 8500 * Math.cbrt(valFck + 8); // MPa
            const ig = (valB * Math.pow(valH, 3)) / 12; // mm4
            const betaD = 0.6; // 지속하중비 기본값
            const ei = (0.4 * ec * ig) / (1 + betaD); // N*mm2
            const pcN = (Math.PI * Math.PI * ei) / Math.pow(valK * valLu, 2);
            const pc = pcN / 1000; // kN

            let delta = 1.0;
            let cm = 1.0;
            if (ft === 'nonsway') {
                cm = Math.max(0.4, 0.6 + 0.4 * valMratio);
                const denom = 1 - valPu / (0.75 * pc);
                delta = denom > 0.05 ? cm / denom : 9.99;
                delta = Math.max(1.0, delta);
            } else {
                const denom = 1 - valPu / (0.75 * pc);
                delta = denom > 0.05 ? 1.0 / denom : 9.99;
                delta = Math.max(1.0, delta);
            }

            return {
                kl_r: Number(kl_r.toFixed(1)),
                pc: Math.round(pc),
                cm: Number(cm.toFixed(2)),
                delta: Number(delta.toFixed(3)),
                isSlender: ft === 'nonsway' ? kl_r > 22 : kl_r > 22
            };
        };

        const initial = calcSway(frameType, lu, k, h, b, pu, fck, m1_m2);

        const html = `
            <div class="eng-dialog-grid">
                <div class="dialog-field-group" style="grid-column: span 2;">
                    <label>골조 횡구속 형태:</label>
                    <div style="display: flex; gap: 16px; margin-top: 4px;">
                        <label style="display: inline-flex; align-items: center; gap: 4px; cursor: pointer;">
                            <input type="radio" name="dlg-sway-frame" value="nonsway" ${frameType === 'nonsway' ? 'checked' : ''}> 비횡구속 골조 (Non-sway, δns)
                        </label>
                        <label style="display: inline-flex; align-items: center; gap: 4px; cursor: pointer;">
                            <input type="radio" name="dlg-sway-frame" value="sway" ${frameType === 'sway' ? 'checked' : ''}> 횡구속 골조 (Sway, δs)
                        </label>
                    </div>
                </div>
                <div class="dialog-field-group">
                    <label>비지지 길이 (lu):</label>
                    <input type="number" id="dlg-sway-lu" value="${lu}" class="form-input" min="500">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>유효좌굴길이계수 (k):</label>
                    <input type="number" id="dlg-sway-k" value="${k}" class="form-input" step="0.05" min="0.5">
                    <span class="unit-tag">-</span>
                </div>
                <div class="dialog-field-group">
                    <label>기둥 춤 (h):</label>
                    <input type="number" id="dlg-sway-h" value="${h}" class="form-input" min="150">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>기둥 폭 (b):</label>
                    <input type="number" id="dlg-sway-b" value="${b}" class="form-input" min="150">
                    <span class="unit-tag">mm</span>
                </div>
                <div class="dialog-field-group">
                    <label>계수 축력 (Pu):</label>
                    <input type="number" id="dlg-sway-pu" value="${pu}" class="form-input" min="0">
                    <span class="unit-tag">kN</span>
                </div>
                <div class="dialog-field-group">
                    <label>단부 모멘트비 (M1/M2):</label>
                    <input type="number" id="dlg-sway-mratio" value="${m1_m2}" class="form-input" step="0.1" min="-1" max="1">
                    <span class="unit-tag">-</span>
                </div>
            </div>
            <div class="dialog-calc-preview" style="margin-top: 12px;">
                <div class="preview-title">⚡ KDS 14 20 20 장주 효과 및 확대계수 산정</div>
                <div id="dlg-sway-preview" class="preview-result" style="font-size: 13px; font-weight: 700; color: #38bdf8;">
                    장주비 klu/r = ${initial.kl_r} → 확대계수 δ = ${initial.delta}
                </div>
                <div id="dlg-sway-sub" style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                    오일러 좌굴하중 Pc = ${initial.pc} kN | Cm = ${initial.cm} | ${initial.isSlender ? '⚠️ 장주효과 고려대상 (klu/r > 22)' : '✅ 단주 영역'}
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: '기둥 장주 모멘트확대계수(δns, δs) 자동 산정',
            dialogId: 'IDD_RCS_COLUMN_SWAY_DLG',
            width: '560px',
            content: html,
            onConfirm: (modalEl) => {
                const ft = modalEl.querySelector('input[name="dlg-sway-frame"]:checked').value;
                const valLu = parseFloat(modalEl.querySelector('#dlg-sway-lu').value) || lu;
                const valK = parseFloat(modalEl.querySelector('#dlg-sway-k').value) || k;
                const valH = parseFloat(modalEl.querySelector('#dlg-sway-h').value) || h;
                const valB = parseFloat(modalEl.querySelector('#dlg-sway-b').value) || b;
                const valPu = parseFloat(modalEl.querySelector('#dlg-sway-pu').value) || pu;
                const valMr = parseFloat(modalEl.querySelector('#dlg-sway-mratio').value) || m1_m2;
                const res = calcSway(ft, valLu, valK, valH, valB, valPu, fck, valMr);

                if (onApply) {
                    onApply({
                        delta: res.delta,
                        kl_r: res.kl_r,
                        pc: res.pc,
                        frameType: ft,
                        lu: valLu,
                        k: valK
                    });
                }
            }
        });

        setTimeout(() => {
            const modalEl = document.getElementById('app-modal-overlay');
            if (!modalEl) return;
            const updatePreview = () => {
                const ftEl = modalEl.querySelector('input[name="dlg-sway-frame"]:checked');
                const ft = ftEl ? ftEl.value : 'nonsway';
                const valLu = parseFloat(modalEl.querySelector('#dlg-sway-lu')?.value) || lu;
                const valK = parseFloat(modalEl.querySelector('#dlg-sway-k')?.value) || k;
                const valH = parseFloat(modalEl.querySelector('#dlg-sway-h')?.value) || h;
                const valB = parseFloat(modalEl.querySelector('#dlg-sway-b')?.value) || b;
                const valPu = parseFloat(modalEl.querySelector('#dlg-sway-pu')?.value) || pu;
                const valMr = parseFloat(modalEl.querySelector('#dlg-sway-mratio')?.value) || m1_m2;
                const res = calcSway(ft, valLu, valK, valH, valB, valPu, fck, valMr);

                const prevEl = modalEl.querySelector('#dlg-sway-preview');
                const subEl = modalEl.querySelector('#dlg-sway-sub');
                if (prevEl) prevEl.innerText = `장주비 klu/r = ${res.kl_r} → 확대계수 δ = ${res.delta}`;
                if (subEl) subEl.innerText = `오일러 좌굴하중 Pc = ${res.pc} kN | Cm = ${res.cm} | ${res.isSlender ? '⚠️ 장주효과 고려대상 (klu/r > 22)' : '✅ 단주 영역'}`;
            };

            modalEl.querySelectorAll('input').forEach(inp => {
                inp.addEventListener('input', updatePreview);
                inp.addEventListener('change', updatePreview);
            });
        }, 50);
    },

    /**
     * 3. KS 표준 철골 형강 단면 DB 선택기 (IDD_STEEL_SECTION_DB_DLG)
     */
    openSectionDb(currentSec = 'H-400×200×8×13', onApply) {
        const hBeamList = window.KS_H_BEAM_DB || [
            { name: 'H-300×150×6.5×9', h: 300, bf: 150, tw: 6.5, tf: 9, A: 4678, Ix: 7192, Iy: 508, weight: 36.7 },
            { name: 'H-350×175×7×11', h: 350, bf: 175, tw: 7, tf: 11, A: 6314, Ix: 13534, Iy: 986, weight: 49.6 },
            { name: 'H-400×200×8×13', h: 400, bf: 200, tw: 8, tf: 13, A: 8412, Ix: 23663, Iy: 1739, weight: 66.0 },
            { name: 'H-450×200×9×14', h: 450, bf: 200, tw: 9, tf: 14, A: 9676, Ix: 33384, Iy: 1875, weight: 76.0 },
            { name: 'H-500×200×10×16', h: 500, bf: 200, tw: 10, tf: 16, A: 11423, Ix: 47744, Iy: 2146, weight: 89.7 }
        ];

        const boxList = window.KS_BOX_DB || [
            { name: '□200×200×8.0', h: 200, b: 200, bf: 200, tw: 8.0, tf: 8.0, A: 5888, Ix: 3510, weight: 46.2 },
            { name: '□250×250×9.0', h: 250, b: 250, bf: 250, tw: 9.0, tf: 9.0, A: 8352, Ix: 8090, weight: 65.6 },
            { name: '□300×300×12.0', h: 300, b: 300, bf: 300, tw: 12.0, tf: 12.0, A: 13248, Ix: 18000, weight: 104.0 }
        ];

        const pipeList = window.KS_PIPE_DB || [
            { name: 'D216.3×6.0', h: 216.3, bf: 216.3, tw: 6.0, tf: 6.0, A: 3964, Ix: 2174, weight: 31.1 },
            { name: 'D267.4×6.6', h: 267.4, bf: 267.4, tw: 6.6, tf: 6.6, A: 5406, Ix: 4543, weight: 42.4 }
        ];

        let activeCategory = 'H'; // 'H', 'BOX', 'PIPE'
        let currentList = hBeamList;

        const renderRows = (list) => {
            return list.map(s => {
                const isSel = s.name === currentSec;
                const b = s.bf ?? s.b ?? 0;
                return `
                    <tr class="sec-row ${isSel ? 'selected' : ''}" data-name="${s.name}" data-json='${JSON.stringify(s)}'>
                        <td><strong>${s.name}</strong></td>
                        <td>${s.h}</td>
                        <td>${b}</td>
                        <td>${s.tw}</td>
                        <td>${s.tf}</td>
                        <td>${s.Ix}</td>
                        <td>${s.weight ?? '-'}</td>
                    </tr>
                `;
            }).join('');
        };

        const html = `
            <div class="sec-db-modal-wrap">
                <div style="display: flex; gap: 8px; margin-bottom: 8px; align-items: center;">
                    <div style="display: flex; gap: 4px;">
                        <button type="button" class="mini-btn ${activeCategory === 'H' ? 'active' : ''}" id="dlg-cat-h">H형강</button>
                        <button type="button" class="mini-btn ${activeCategory === 'BOX' ? 'active' : ''}" id="dlg-cat-box">각관(BOX)</button>
                        <button type="button" class="mini-btn ${activeCategory === 'PIPE' ? 'active' : ''}" id="dlg-cat-pipe">원형강관</button>
                    </div>
                    <input type="text" id="dlg-sec-filter" placeholder="규격 검색 (예: 400, 250)..." class="form-input" style="flex: 1;">
                </div>
                <div class="sec-table-container" style="max-height: 320px; overflow-y: auto; border: 1px solid var(--border); border-radius: 4px;">
                    <table class="sec-table" id="dlg-sec-table" style="width: 100%; font-size: 11px;">
                        <thead>
                            <tr>
                                <th>형강명</th>
                                <th>H (mm)</th>
                                <th>B (mm)</th>
                                <th>tw (mm)</th>
                                <th>tf (mm)</th>
                                <th>Ix (cm⁴)</th>
                                <th>중량 (kg/m)</th>
                            </tr>
                        </thead>
                        <tbody id="dlg-sec-tbody">${renderRows(currentList)}</tbody>
                    </table>
                </div>
                <div id="dlg-sec-preview-bar" style="margin-top: 8px; font-size: 11px; color: var(--text-muted);">
                    선택 단면: <span id="dlg-sec-sel-text" style="font-weight: 700; color: #38bdf8;">${currentSec}</span>
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: 'KS 표준 철골 형강 단면 DB 선택기',
            dialogId: 'IDD_STEEL_SECTION_DB_DLG',
            width: '640px',
            content: html,
            onConfirm: (modalEl) => {
                const selRow = modalEl.querySelector('.sec-row.selected');
                if (selRow && onApply) {
                    const secData = JSON.parse(selRow.dataset.json);
                    onApply(secData);
                }
            }
        });

        setTimeout(() => {
            const modalEl = document.getElementById('app-modal-overlay');
            if (!modalEl) return;

            const tbody = modalEl.querySelector('#dlg-sec-tbody');
            const filterInput = modalEl.querySelector('#dlg-sec-filter');
            const selText = modalEl.querySelector('#dlg-sec-sel-text');

            const bindRowEvents = () => {
                tbody.querySelectorAll('.sec-row').forEach(row => {
                    row.onclick = () => {
                        tbody.querySelectorAll('.sec-row').forEach(r => r.classList.remove('selected'));
                        row.classList.add('selected');
                        if (selText) selText.innerText = row.dataset.name;
                    };
                    row.ondblclick = () => {
                        row.classList.add('selected');
                        const okBtn = modalEl.querySelector('#btn-modal-ok');
                        if (okBtn) okBtn.click();
                    };
                });
            };

            const updateList = () => {
                const q = (filterInput.value || '').trim().toLowerCase();
                const filtered = currentList.filter(s => s.name.toLowerCase().includes(q));
                tbody.innerHTML = renderRows(filtered);
                bindRowEvents();
            };

            modalEl.querySelector('#dlg-cat-h').onclick = () => {
                activeCategory = 'H';
                currentList = hBeamList;
                modalEl.querySelectorAll('#dlg-cat-h, #dlg-cat-box, #dlg-cat-pipe').forEach(b => b.classList.remove('active'));
                modalEl.querySelector('#dlg-cat-h').classList.add('active');
                updateList();
            };

            modalEl.querySelector('#dlg-cat-box').onclick = () => {
                activeCategory = 'BOX';
                currentList = boxList;
                modalEl.querySelectorAll('#dlg-cat-h, #dlg-cat-box, #dlg-cat-pipe').forEach(b => b.classList.remove('active'));
                modalEl.querySelector('#dlg-cat-box').classList.add('active');
                updateList();
            };

            modalEl.querySelector('#dlg-cat-pipe').onclick = () => {
                activeCategory = 'PIPE';
                currentList = pipeList;
                modalEl.querySelectorAll('#dlg-cat-h, #dlg-cat-box, #dlg-cat-pipe').forEach(b => b.classList.remove('active'));
                modalEl.querySelector('#dlg-cat-pipe').classList.add('active');
                updateList();
            };

            filterInput.oninput = updateList;
            bindRowEvents();
        }, 50);
    },

    /**
     * 4. KDS 41 10 15 기본 하중조합 생성기 (IDD_LOAD_COMBINATION_DLG)
     */
    openLoadCombination(current = {}, onApply) {
        const d = current.deadLoad ?? current.d ?? 50;
        const l = current.liveLoad ?? current.l ?? 30;
        const w = current.windLoad ?? current.w ?? 0;
        const e = current.seismicLoad ?? current.e ?? 0;

        const calcLcb = (valD, valL, valW, valE) => {
            const lcb1 = 1.4 * valD;
            const lcb2 = 1.2 * valD + 1.6 * valL;
            const lcb3 = 1.2 * valD + 1.0 * valL + 1.0 * valW;
            const lcb4 = 1.2 * valD + 1.0 * valL + 1.0 * valE;
            const lcb5 = 0.9 * valD + 1.0 * valW;
            const lcb6 = 0.9 * valD + 1.0 * valE;

            const list = [
                { name: 'LCB 1 (1.4D)', val: lcb1 },
                { name: 'LCB 2 (1.2D + 1.6L)', val: lcb2 },
                { name: 'LCB 3 (1.2D + 1.0L + 1.0W)', val: lcb3 },
                { name: 'LCB 4 (1.2D + 1.0L + 1.0E)', val: lcb4 },
                { name: 'LCB 5 (0.9D + 1.0W)', val: lcb5 },
                { name: 'LCB 6 (0.9D + 1.0E)', val: lcb6 }
            ];

            let governing = list[0];
            list.forEach(item => {
                if (item.val > governing.val) governing = item;
            });

            return { governing, list };
        };

        const initial = calcLcb(d, l, w, e);

        const html = `
            <div class="eng-dialog-grid">
                <div class="dialog-field-group">
                    <label>고정하중 (D, Dead Load):</label>
                    <input type="number" id="dlg-load-d" value="${d}" class="form-input">
                    <span class="unit-tag">kN·m / kN</span>
                </div>
                <div class="dialog-field-group">
                    <label>활하중 (L, Live Load):</label>
                    <input type="number" id="dlg-load-l" value="${l}" class="form-input">
                    <span class="unit-tag">kN·m / kN</span>
                </div>
                <div class="dialog-field-group">
                    <label>풍하중 (W, Wind Load):</label>
                    <input type="number" id="dlg-load-w" value="${w}" class="form-input">
                    <span class="unit-tag">kN·m / kN</span>
                </div>
                <div class="dialog-field-group">
                    <label>지진하중 (E, Earthquake):</label>
                    <input type="number" id="dlg-load-e" value="${e}" class="form-input">
                    <span class="unit-tag">kN·m / kN</span>
                </div>
            </div>
            <div class="dialog-calc-preview" style="margin-top: 12px;">
                <div class="preview-title">⚡ KDS 41 10 15 극한하중조합 일괄 산출</div>
                <div id="dlg-lcb-preview" class="preview-result" style="font-size: 13px; font-weight: 700; color: #38bdf8;">
                    지배조합: ${initial.governing.name} = ${initial.governing.val.toFixed(1)} kN·m
                </div>
                <div id="dlg-lcb-list" style="font-size: 11px; color: var(--text-muted); margin-top: 6px; display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                    ${initial.list.map(it => `<div>${it.name}: <strong>${it.val.toFixed(1)}</strong></div>`).join('')}
                </div>
            </div>
        `;

        if (!window.ModalManager) return;
        window.ModalManager.open({
            title: 'KDS 41 10 15 기본 하중조합 생성기',
            dialogId: 'IDD_LOAD_COMBINATION_DLG',
            width: '540px',
            content: html,
            onConfirm: (modalEl) => {
                const valD = parseFloat(modalEl.querySelector('#dlg-load-d').value) || 0;
                const valL = parseFloat(modalEl.querySelector('#dlg-load-l').value) || 0;
                const valW = parseFloat(modalEl.querySelector('#dlg-load-w').value) || 0;
                const valE = parseFloat(modalEl.querySelector('#dlg-load-e').value) || 0;
                const res = calcLcb(valD, valL, valW, valE);

                if (onApply) {
                    onApply({
                        deadLoad: valD,
                        liveLoad: valL,
                        windLoad: valW,
                        seismicLoad: valE,
                        governingMu: Number(res.governing.val.toFixed(1)),
                        governingVu: Number((res.governing.val * 0.45).toFixed(1)), // 전단력 환산 참조치
                        governingLcbName: res.governing.name
                    });
                }
            }
        });

        setTimeout(() => {
            const modalEl = document.getElementById('app-modal-overlay');
            if (!modalEl) return;
            const updatePreview = () => {
                const valD = parseFloat(modalEl.querySelector('#dlg-load-d')?.value) || 0;
                const valL = parseFloat(modalEl.querySelector('#dlg-load-l')?.value) || 0;
                const valW = parseFloat(modalEl.querySelector('#dlg-load-w')?.value) || 0;
                const valE = parseFloat(modalEl.querySelector('#dlg-load-e')?.value) || 0;
                const res = calcLcb(valD, valL, valW, valE);

                const prevEl = modalEl.querySelector('#dlg-lcb-preview');
                const listEl = modalEl.querySelector('#dlg-lcb-list');
                if (prevEl) prevEl.innerText = `지배조합: ${res.governing.name} = ${res.governing.val.toFixed(1)} kN·m`;
                if (listEl) {
                    listEl.innerHTML = res.list.map(it => `<div>${it.name}: <strong>${it.val.toFixed(1)}</strong></div>`).join('');
                }
            };

            modalEl.querySelectorAll('input').forEach(inp => {
                inp.addEventListener('input', updatePreview);
            });
        }, 50);
    },

    /**
     * 레거시 호환용 보 단면 플랜지 모달 (IDD_RCS_BEAM_SECT_DLG)
     */
    openBeamSectionDetail(current = {}, onApply) {
        return this.openBeamBeffDialog(current, onApply);
    },

    /**
     * 5. 계산서 머릿말 및 결재란 설정 모달 (IDD_REPORT_HEADER_DLG) - Phase 21-5
     */
    openReportHeaderDialog(current = {}, onApply) {
        const today = new Date().toISOString().slice(0, 10);
        const projectName = current.projectName || 'AltDP_3rd KDS Automated Engineering';
        const companyName = current.companyName || '(주)한국구조기술엔지니어링';
        const companyShort = current.companyShort || 'K-STRUCT';
        const memberTag = current.memberTag || '1F-B1';
        const date = current.date || today;
        const engineer = current.engineer || '홍길동 (작성)';
        const checker = current.checker || '이몽룡 (검토)';
        const approver = current.approver || '성춘향 (승인)';

        const html = `
            <div class="eng-dialog-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;">
                <div class="dialog-field-group" style="grid-column: span 2;">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">프로젝트 명칭 (Project Name):</label>
                    <input type="text" id="dlg-hdr-project" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${projectName}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">회사명 (정식):</label>
                    <input type="text" id="dlg-hdr-company" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${companyName}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">회사 약칭 (Short Name):</label>
                    <input type="text" id="dlg-hdr-company-short" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${companyShort}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">부재 태그 (Member ID):</label>
                    <input type="text" id="dlg-hdr-tag" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${memberTag}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">검토 일자 (Date):</label>
                    <input type="date" id="dlg-hdr-date" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${date}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">작성자 (Engineer):</label>
                    <input type="text" id="dlg-hdr-engineer" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${engineer}">
                </div>
                <div class="dialog-field-group">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">검토자 (Checker):</label>
                    <input type="text" id="dlg-hdr-checker" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${checker}">
                </div>
                <div class="dialog-field-group" style="grid-column: span 2;">
                    <label style="font-weight:600;display:block;margin-bottom:4px;">승인자 (Approver):</label>
                    <input type="text" id="dlg-hdr-approver" class="form-input" style="width:100%;box-sizing:border-box;padding:6px;border:1px solid #cbd5e1;border-radius:4px;" value="${approver}">
                </div>
            </div>
        `;

        const applyAction = (modalEl) => {
            const result = {
                projectName: modalEl.querySelector('#dlg-hdr-project')?.value.trim() || projectName,
                companyName: modalEl.querySelector('#dlg-hdr-company')?.value.trim() || companyName,
                companyShort: modalEl.querySelector('#dlg-hdr-company-short')?.value.trim() || companyShort,
                memberTag: modalEl.querySelector('#dlg-hdr-tag')?.value.trim() || memberTag,
                date: modalEl.querySelector('#dlg-hdr-date')?.value || date,
                engineer: modalEl.querySelector('#dlg-hdr-engineer')?.value.trim() || engineer,
                checker: modalEl.querySelector('#dlg-hdr-checker')?.value.trim() || checker,
                approver: modalEl.querySelector('#dlg-hdr-approver')?.value.trim() || approver,
                logoUrl: current.logoUrl || ''
            };
            if (typeof onApply === 'function') {
                onApply(result);
            }
        };

        if (window.ModalManager && typeof window.ModalManager.openModal === 'function') {
            window.ModalManager.openModal({
                title: '⚙️ 계산서 머릿말 및 결재란 설정 (IDD_REPORT_HEADER_DLG)',
                bodyHtml: html,
                width: 520,
                onApply: applyAction
            });
        } else {
            // ModalManager 없을 경우 fallback
            const overlay = document.createElement('div');
            overlay.className = 'modal-backdrop';
            overlay.id = 'app-modal-overlay';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
            overlay.innerHTML = `
                <div class="eng-modal-card" style="background:#ffffff;color:#1e293b;padding:24px;border-radius:8px;width:520px;box-shadow:0 10px 25px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid #e2e8f0;padding-bottom:8px;">
                        <h3 style="margin:0;font-size:15px;font-weight:700;color:#0f172a;">⚙️ 계산서 머릿말 및 결재란 설정 (IDD_REPORT_HEADER_DLG)</h3>
                        <button id="btn-close-hdr-fallback" style="background:none;border:none;font-size:18px;cursor:pointer;">✕</button>
                    </div>
                    ${html}
                    <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px;border-top:1px solid #e2e8f0;padding-top:12px;">
                        <button id="btn-cancel-hdr-fallback" style="padding:6px 14px;border:1px solid #cbd5e1;background:#f8fafc;border-radius:4px;cursor:pointer;">취소</button>
                        <button id="btn-apply-hdr-fallback" style="padding:6px 16px;background:#2563eb;color:#ffffff;border:none;border-radius:4px;font-weight:700;cursor:pointer;">적용</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
            const close = () => {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            };
            overlay.querySelector('#btn-close-hdr-fallback').onclick = close;
            overlay.querySelector('#btn-cancel-hdr-fallback').onclick = close;
            overlay.querySelector('#btn-apply-hdr-fallback').onclick = () => {
                applyAction(overlay);
                close;
            };
        }
    }
};

window.CommonDialogs = CommonDialogs;

