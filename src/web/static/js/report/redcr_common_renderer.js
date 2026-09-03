// web/js/report/redcr_common_renderer.js
/**
 * 54종 단위부재 공통 범용 4대 영역 렌더러 (Universal 4-Pillar Layout Engine)
 * re-DCR sheetFormulas.js 기반으로 4대 영역(입력 요약 - 기준 수식 - 비주얼 단면 - 종합 검토표)을 자동 조립
 * [object Object] 방지 및 공학 수식/스마트 데이터 테이블 렌더링 지원
 */

window.RedcrCommonRenderer = {
    render(container, resultData, currentModulePath, inputParams) {
        if (!container || !resultData) return;
        
        const F = window.RedcrFormulas || {};
        const dcr = Number(resultData.governing_dcr) || Number(resultData.max_dcr) || Number(resultData.dcr) || 0.0;
        const isOk = (resultData.status === 'OK' || resultData.status === 'PASS') && dcr <= 1.0;


        let html = `
        <div class="four-pillar-container">
            <!-- [Panel A: 좌측 시각화 & 입력 요약] -->
            <div class="pillar-panel panel-left">
                <!-- ③ [영역 3] 비주얼 부재 표현 (공용 Vector SVG 1순위 연동) -->
                <div class="pillar-card card-visual">
                    <div class="card-header">
                        <span class="card-icon">📐</span>
                        <span class="card-title">단면 형상 및 배근 시각화</span>
                    </div>
                    <div class="card-body canvas-body" id="common-canvas-host">
                        ${this.generateSectionVisualHtml(resultData, currentModulePath, inputParams)}
                    </div>
                </div>

                <!-- ① [영역 1] 사용자 입력 요약 -->
                <div class="pillar-card card-inputs">
                    <div class="card-header">
                        <span class="card-icon">📥</span>
                        <span class="card-title">설계 입력 파라미터 요약</span>
                    </div>
                    <div class="card-body">
                        ${this.generateInputsHtml(resultData, inputParams)}
                    </div>
                </div>
            </div>

            <!-- [Panel B: 우측 종합 검토표 & KDS 수식 과정] -->
            <div class="pillar-panel panel-right">
                <!-- ④ [영역 4] 종합 검토 결과표 -->
                <div class="pillar-card card-summary">
                    <div class="card-header">
                        <span class="card-icon">📋</span>
                        <span class="card-title">한계상태별 안전성 종합 검토표</span>
                    </div>
                    <div class="card-body">
                        ${this.generateCheckTableHtml(resultData)}
                    </div>
                </div>

                <!-- 📈 [공학 다이어그램 카드군: P-M 상관곡선 / 지반 접지압 / 철근 정착이음] -->
                ${this.generateEngineeringDiagramsHtml(resultData)}

                <!-- ② [영역 2] 기준 기반 Step-by-Step 계산 과정 -->
                <div class="pillar-card card-steps">
                    <div class="card-header">
                        <span class="card-icon">📄</span>
                        <span class="card-title">KDS 기준 기반 상세 계산 근거 (Step-by-Step)</span>
                    </div>
                    <div class="card-body">
                        ${this.generateStepsHtml(resultData)}
                    </div>
                </div>
            </div>
        </div>`;

        container.innerHTML = html;

        // Vector SVG가 없을 때만 Canvas 2D Fallback 드로잉 실행
        setTimeout(() => {
            const cv = document.getElementById('pillar-section-canvas');
            if (cv && window.CanvasRenderer) {
                const geomType = (window.allModules && window.allModules.find(m => m.key === currentModulePath)?.geomType) || 'rc_rect';
                const isLightMode = true;
                const ctx = cv.getContext('2d');
                const W = cv.width;
                const H = cv.height;
                ctx.clearRect(0, 0, W, H);
                ctx.save();
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, W, H);
                const cx = W / 2;
                const cy = H / 2;
                const data = inputParams || resultData || {};
                
                if (geomType === 'rc_rect') window.CanvasRenderer.drawRcRect(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'rc_tsect') window.CanvasRenderer.drawRcTSect(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'steel_h') window.CanvasRenderer.drawSteelH(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'steel_box_pipe') window.CanvasRenderer.drawSteelBoxPipe(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'rc_footing') window.CanvasRenderer.drawRcFooting(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'rc_slab') window.CanvasRenderer.drawRcSlab(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'steel_baseplate') window.CanvasRenderer.drawSteelBaseplate(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'pc_double_tee') window.CanvasRenderer.drawPcDoubleTee(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'bracket') window.CanvasRenderer.drawBracketCorbel(ctx, cx, cy, data, W, H, isLightMode);
                else if (geomType === 'src_section') window.CanvasRenderer.drawSrcSection(ctx, cx, cy, data, W, H, isLightMode);
                else window.CanvasRenderer.drawRcRect(ctx, cx, cy, data, W, H, isLightMode);
                
                ctx.restore();
            }
        }, 40);
    },

    /** ③ 단면 형상 및 배근 시각화 SVG/Canvas 생성 (SSOT 공용화) */
    generateSectionVisualHtml(resultData, currentModulePath, inputParams) {
        const data = Object.assign({}, inputParams || {}, resultData || {});
        const geomType = (window.allModules && window.allModules.find(m => m.key === currentModulePath)?.geomType) || 'rc_rect';
        
        // 1. 공용 Vector SVG 렌더러 호출 (A4 순백색 모드)
        if (window.CanvasRenderer && typeof window.CanvasRenderer.dispatchVectorSVG === 'function') {
            const svg = window.CanvasRenderer.dispatchVectorSVG(geomType, data, 320, 220, { mode: 'report' });
            if (svg) {
                return `<div class="pillar-vector-wrap" style="width:100%;min-height:220px;display:flex;justify-content:center;align-items:center;background:#ffffff;border-radius:4px;overflow:hidden;">${svg}</div>`;
            }
        }
        
        // 2. 특수 부재 Fallback: Canvas 2D
        return `<canvas id="pillar-section-canvas" width="340" height="240"></canvas>`;
    },

    /** ① 사용자 입력 요약 HTML */
    generateInputsHtml(res, inputParams) {
        const F = window.RedcrFormulas;
        const rows = [];
        const src = inputParams || res.inputs || res;

        const labelMap = {
            fck: { label: '콘크리트 설계강도 (fck)', unit: 'MPa' },
            fy: { label: '주철근 항복강도 (fy)', unit: 'MPa' },
            fys: { label: '전단철근 항복강도 (fys)', unit: 'MPa' },
            fyt: { label: '전단철근 항복강도 (fyt)', unit: 'MPa' },
            b: { label: '단면 폭 (b)', unit: 'mm' },
            bw: { label: '복부 폭 (bw)', unit: 'mm' },
            h: { label: '단면 춤 (h)', unit: 'mm' },
            H: { label: '높이/춤 (H)', unit: 'mm' },
            B: { label: '폭/너비 (B)', unit: 'mm' },
            L: { label: '길이/스팬 (L)', unit: 'mm' },
            D: { label: '기둥/단면 직경 (D)', unit: 'mm' },
            tw: { label: '웨브 두께 (tw)', unit: 'mm' },
            tf: { label: '플랜지 두께 (tf)', unit: 'mm' },
            cover: { label: '피복 두께 (cover)', unit: 'mm' },
            Mu: { label: '소요 휨모멘트 (Mu)', unit: 'kN·m' },
            Mux: { label: 'X축 소요 휨모멘트 (Mux)', unit: 'kN·m' },
            Muy: { label: 'Y축 소요 휨모멘트 (Muy)', unit: 'kN·m' },
            Muz: { label: 'Z축 소요 휨모멘트 (Muz)', unit: 'kN·m' },
            Vu: { label: '소요 전단력 (Vu)', unit: 'kN' },
            Pu: { label: '소요 축력 (Pu)', unit: 'kN' },
            qa: { label: '허용 지내력 (qa)', unit: 'kN/m²' },
            P_serv: { label: '사용 축하중 (Pserv)', unit: 'kN' },
            Mx_serv: { label: '사용 모멘트 Mx', unit: 'kN·m' },
            My_serv: { label: '사용 모멘트 My', unit: 'kN·m' },
            Lb: { label: '비지지길이 (Lb)', unit: 'mm' },
            Cb: { label: '모멘트 구배계수 (Cb)', unit: '' },
            grade: { label: '강재 강종 (Grade)', unit: '' },
            steel_grade: { label: '강재 강종 (Grade)', unit: '' },
            rebar_grade: { label: '철근 강종 (Rebar Grade)', unit: '' },
            bar_dia: { label: '주철근 직경 (bar_dia)', unit: 'mm' },
            bar_spacing: { label: '배근 간격 (spacing)', unit: 'mm' },
            span: { label: '부재 순경간 (span)', unit: 'mm' },
            slab_thick: { label: '슬래브 두께 (t)', unit: 'mm' },
            num_piles: { label: '말뚝 개수 (num_piles)', unit: 'EA' },
            pile_cap_dia: { label: '말뚝 직경 (pile_dia)', unit: 'mm' }
        };

        Object.keys(src).forEach(k => {
            if (['status', 'governing_dcr', 'section', 'inputs', 'category', 'group', 'id'].includes(k)) return;
            const val = src[k];
            if (val === null || val === undefined || typeof val === 'object') return;
            
            if (labelMap[k]) {
                rows.push({ label: labelMap[k].label, value: val, unit: labelMap[k].unit });
            } else {
                const { valueStr, unitStr } = F.formatValueAndUnit(k, val);
                rows.push({ label: F.formatSymbol(k), value: valueStr, unit: unitStr });
            }
        });

        if (rows.length === 0) {
            return '<div style="color:#888;padding:8px;">입력된 파라미터 요약이 없습니다.</div>';
        }

        return F && F.inputBlock ? F.inputBlock('Design Inputs & Parameters', rows) : '<table class="inp-table">' + rows.map(r => `<tr><td>${r.label}</td><td>${r.value} ${r.unit}</td></tr>`).join('') + '</table>';
    },

    /** ④ 종합 검토 결과표 HTML (54개 모듈 한계상태 전수 자동 매핑) */
    generateCheckTableHtml(res) {
        const F = window.RedcrFormulas;
        const checkRows = [];

        // 1. 휨 검토 (Flexure)
        if (res.flexure || res.phi_Mn || res.Mn || res.Mu || res.phiMn_kNm) {
            const flex = res.flexure || res;
            const mu = flex.Mu || flex.Mu_kNm || res.Mu || 0;
            const phiMn = flex.phi_Mn || flex.phiMn_kNm || flex.phiMn || res.phi_Mn || (flex.dcr > 0 ? mu / flex.dcr : 1);
            const dcr = flex.dcr !== undefined ? Number(flex.dcr) : (phiMn > 0 ? (mu / phiMn) : 0);
            checkRows.push({
                label: '휨강도 검토 (Flexural Capacity)',
                formula: 'Mu ≤ φMn',
                demand: mu,
                capacity: phiMn,
                unit: 'kN·m',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 20 / KDS 14 31 10'
            });
        }

        // 2. 전단 검토 (Shear)
        if (res.shear || res.phi_Vn || res.Vn || res.Vu || res.phiVn_kN) {
            const sh = res.shear || res;
            const vu = sh.Vu || sh.Vu_kN || res.Vu || 0;
            const phiVn = sh.phi_Vn || sh.phiVn_kN || sh.phiVn || res.phi_Vn || (sh.dcr > 0 ? vu / sh.dcr : 1);
            const dcr = sh.dcr !== undefined ? Number(sh.dcr) : (phiVn > 0 ? (vu / phiVn) : 0);
            checkRows.push({
                label: '전단강도 검토 (Shear Capacity)',
                formula: 'Vu ≤ φVn',
                demand: vu,
                capacity: phiVn,
                unit: 'kN',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 22 / KDS 14 31 10'
            });
        }

        // 3. 1방향 보 전단 (One-way Shear)
        if (res.one_way_shear) {
            const ow = res.one_way_shear;
            const vu = ow.Vu_kN || ow.Vu || 0;
            const phiVc = ow.phiVc_kN || ow.phiVc || 1;
            const dcr = Number(ow.dcr || (phiVc > 0 ? vu / phiVc : 0));
            checkRows.push({
                label: '1방향 보전단 (One-way Shear)',
                formula: 'Vu ≤ φVc',
                demand: vu,
                capacity: phiVc,
                unit: 'kN',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 70 §4.2.2'
            });
        }

        // 4. 2방향 펀칭 전단 (Punching Shear)
        if (res.punching_shear) {
            const ps = res.punching_shear;
            const vu = ps.Vu_kN || ps.Vu || 0;
            const phiVc = ps.phiVc_kN || ps.phiVc || 1;
            const dcr = Number(ps.dcr || (phiVc > 0 ? vu / phiVc : 0));
            checkRows.push({
                label: '2방향 펀칭전단 (Punching Shear)',
                formula: 'Vu ≤ φVc,punch',
                demand: vu,
                capacity: phiVc,
                unit: 'kN',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 22 §4.5'
            });
        }

        // 5. 지반 지내력 (Soil Bearing Pressure)
        if (res.soil_bearing) {
            const sb = res.soil_bearing;
            const qmax = sb.q_max || sb.q_max_kPa || 0;
            const qa = sb.qa || sb.qa_kPa || 200;
            const dcr = Number(sb.dcr || (qa > 0 ? qmax / qa : 0));
            checkRows.push({
                label: '지반 접지압 (Soil Bearing)',
                formula: 'qmax ≤ qa',
                demand: qmax,
                capacity: qa,
                unit: 'kN/m²',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 70 §4.2.1'
            });
        }

        // 6. 축압축/좌굴 검토 (Axial Compression)
        if (res.axial_compression || res.axial) {
            const ax = res.axial_compression || res.axial;
            const pu = ax.Pu || ax.Pu_kN || res.Pu || 0;
            const phiPn = ax.phi_Pn || ax.phiPn_kN || ax.phiPn || 1;
            const dcr = Number(ax.dcr || (phiPn > 0 ? pu / phiPn : 0));
            checkRows.push({
                label: '축압축 좌굴강도 (Axial Capacity)',
                formula: 'Pu ≤ φPn',
                demand: pu,
                capacity: phiPn,
                unit: 'kN',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 31 10 §4.2'
            });
        }

        // 7. P-M-M 상관식 검토 (Biaxial Interaction)
        if (res.interaction || res.pm) {
            const pm = res.interaction || res.pm;
            const dcr = Number(pm.dcr || pm.governing_dcr || 0);
            checkRows.push({
                label: 'P-M 상관비 (Biaxial Interaction)',
                formula: 'Interaction Ratio ≤ 1.0',
                demand: dcr,
                capacity: 1.0,
                unit: 'ratio',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 20 / KDS 14 31 10'
            });
        }

        // 8. 볼트 / 접합부 / 베이스플레이트 (Connection & Fasteners)
        if (res.bolt_shear || res.bolt_tension || res.connection || res.baseplate) {
            const conn = res.bolt_shear || res.bolt_tension || res.connection || res.baseplate;
            const dcr = Number(conn.dcr || res.governing_dcr || 0);
            checkRows.push({
                label: '접합부 결합강도 (Connection Capacity)',
                formula: 'Ru ≤ φRn',
                demand: dcr,
                capacity: 1.0,
                unit: 'ratio',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 31 25'
            });
        }

        // 9. 사용성 / 처짐 / 진동 (Serviceability)
        if (res.deflection || res.vibration || res.serviceability) {
            const serv = res.deflection || res.vibration || res.serviceability;
            const dcr = Number(serv.dcr || 0);
            checkRows.push({
                label: '사용성 검토 (Serviceability / Defl)',
                formula: 'δ ≤ δallow',
                demand: serv.delta_max || serv.a_peak || dcr,
                capacity: serv.delta_allow || serv.a_allow || 1.0,
                unit: serv.delta_max ? 'mm' : 'ratio',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS 14 20 30 / KDS 14 31 10'
            });
        }

        // Fallback: 상세 항목이 없는 경우 Governing DCR 1줄 표시
        if (checkRows.length === 0) {
            const dcr = Number(res.governing_dcr || res.dcr || 0);
            checkRows.push({
                label: '단면 안전성 종합 검토 (Governing State)',
                formula: 'Demand / Capacity ≤ 1.0',
                demand: dcr,
                capacity: 1.0,
                unit: 'ratio',
                dc: dcr,
                pass: dcr <= 1.0,
                note: 'KDS Standard'
            });
        }

        return F && F.checkTable ? F.checkTable('한계상태 종합 판정표', checkRows) : '';
    },

    /** ② 기준 기반 Step-by-Step 계산 과정 HTML ([object Object] 원천 차단 및 스마트 표 변환) */
    generateStepsHtml(res) {
        const F = window.RedcrFormulas;
        const steps = [];
        const topPrimitives = [];

        const ignoredKeys = [
            'status', 'governing_dcr', 'max_dcr', 'dcr', 'section', 'inputs', 
            'visual_data', 'template', 'geomType', 'section_info', 'summary',
            'category', 'group', 'id', 'pmCurve', 'pm_points', 'splice_chart'
        ];

        Object.keys(res).forEach(key => {
            if (ignoredKeys.includes(key)) return;
            const val = res[key];


            // [Case 1] 배열 데이터 (capacity_table, pm_points, bar_details 등)
            if (Array.isArray(val)) {
                steps.push(F.dataTable(this.formatSectionTitle(key), val, 'KDS Standard'));
            }
            // [Case 2] 딕셔너리 객체 (flexure, shear, beam_details, visual_data 등)
            else if (typeof val === 'object' && val !== null) {
                const subSteps = [];
                const nestedTables = [];

                Object.keys(val).forEach(subKey => {
                    const subVal = val[subKey];

                    // 하위 서브값이 배열 또는 중첩 객체인 경우 -> 별도 데이터 테이블로 렌더링
                    if (Array.isArray(subVal) || (typeof subVal === 'object' && subVal !== null)) {
                        nestedTables.push(F.dataTable(this.formatSectionTitle(subKey), subVal, 'KDS Standard'));
                    }
                    // 원시값인 경우 -> 공학 수식 Step-by-Step 행 생성
                    else {
                        const { valueStr, unitStr } = F.formatValueAndUnit(subKey, subVal);
                        const sym = F.formatSymbol(subKey);
                        subSteps.push({
                            formula: sym,
                            result: `= ${valueStr} ${unitStr}`.trim(),
                            substitution: ''
                        });
                    }
                });

                if (subSteps.length > 0) {
                    steps.push(F.calcBlock(this.formatSectionTitle(key), subSteps, 'KDS Standard'));
                }
                if (nestedTables.length > 0) {
                    steps.push(...nestedTables);
                }
            }
            // [Case 3] 최상위 원시 값 (top-level primitive results)
            else {
                const { valueStr, unitStr } = F.formatValueAndUnit(key, val);
                const sym = F.formatSymbol(key);
                topPrimitives.push({
                    formula: sym,
                    result: `= ${valueStr} ${unitStr}`.trim(),
                    substitution: ''
                });
            }
        });

        // 최상위 원시값들이 있으면 상단에 요약 수식 블록 추가
        if (topPrimitives.length > 0) {
            steps.unshift(F.calcBlock('1. 설계 성능 요약 (Design Summary)', topPrimitives, 'KDS Standard'));
        }

        if (steps.length === 0) {
            return '<div style="color:#888;padding:8px;">상세 수식 단계가 제공되지 않았습니다.</div>';
        }

        return steps.join('\n');
    },

    generateEngineeringDiagramsHtml(resultData) {
        if (!resultData) return '';
        let html = '';
        
        // 1. P-M 곡선 카드
        html += this.generatePmCardHtml(resultData);
        
        // 2. 기초 지반 접지압 카드
        html += this.generateSoilPressureCardHtml(resultData);
        
        // 3. 철근 정착 및 이음 길이 비교 카드
        html += this.generateSpliceCardHtml(resultData);
        
        return html;
    },

    generateSoilPressureCardHtml(resultData) {
        if (!resultData) return '';
        const sb = resultData.soil_bearing || (resultData.qmax !== undefined ? {
            q_max: resultData.qmax,
            q_min: resultData.qmin || 0,
            qa: resultData.qa || 200
        } : null);
        
        if (!sb) return '';
        const qmax = Number(sb.q_max || sb.qmax || sb.q_max_kPa || 0);
        const qmin = Number(sb.q_min || sb.qmin || sb.q_min_kPa || 0);
        const qa = Number(sb.qa || sb.qa_kPa || 200);
        if (qmax <= 0 && qa <= 0) return '';
        
        const svg = window.RedcrFootingReport && typeof window.RedcrFootingReport.generateSoilPressureSVG === 'function'
            ? window.RedcrFootingReport.generateSoilPressureSVG(qmax, qmin, qa)
            : '';
            
        if (!svg) return '';
        
        return `
        <div class="pillar-card card-soil-diagram" style="margin-bottom:14px;">
            <div class="card-header">
                <span class="card-icon">📐</span>
                <span class="card-title">지반 접지압 분포도 (Soil Pressure Distribution)</span>
            </div>
            <div class="card-body" style="display:flex;justify-content:center;padding:12px;background:#fafafa;">
                ${svg}
            </div>
        </div>`;
    },

    generateSpliceCardHtml(resultData) {
        if (!resultData) return '';
        const items = resultData.splice_chart || (resultData.tension_development ? [
            { label: '인장 정착길이 (ld)', length_mm: resultData.tension_development.ld_tension_mm || 800, code: 'KDS 14 20 52 §4.1', color: '#1976d2' },
            { label: '인장 이음길이 (ls, B급)', length_mm: (resultData.tension_splice && resultData.tension_splice.splice_length_mm) || 1040, code: 'KDS 14 20 52 §4.5', color: '#dc2626' },
            { label: '압축 정착길이 (ldc)', length_mm: (resultData.compression_development && resultData.compression_development.ld_comp_mm) || 480, code: 'KDS 14 20 52 §4.2', color: '#059669' },
            { label: '표준 갈고리 정착길이 (ldh)', length_mm: (resultData.standard_hook && resultData.standard_hook.ldh_mm) || 360, code: 'KDS 14 20 52 §4.3', color: '#7c3aed' }
        ] : null);
        
        if (!items || items.length === 0) return '';
        
        const maxLen = Math.max(...items.map(i => i.length_mm), 1000) * 1.15;
        const W = 460, H = 180;
        const pad = { left: 160, right: 60, top: 15, bottom: 25 };
        const pw = W - pad.left - pad.right;
        const barH = 18, gap = 12;
        
        let svg = `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;display:block;margin:0 auto;">`;
        
        items.forEach((item, idx) => {
            const y = pad.top + idx * (barH + gap);
            const bw = (item.length_mm / maxLen) * pw;
            
            // 라벨
            svg += `<text x="${pad.left - 8}" y="${y + 13}" text-anchor="end" font-size="10" font-weight="600" fill="#334155" font-family="'Segoe UI', sans-serif">${item.label}</text>`;
            // 배경 트랙
            svg += `<rect x="${pad.left}" y="${y}" width="${pw}" height="${barH}" rx="3" fill="#f1f5f9"/>`;
            // 바
            svg += `<rect x="${pad.left}" y="${y}" width="${bw.toFixed(1)}" height="${barH}" rx="3" fill="${item.color}"/>`;
            // 수치
            svg += `<text x="${pad.left + bw + 6}" y="${y + 13}" font-size="10" font-weight="700" fill="${item.color}" font-family="Consolas, monospace">${item.length_mm} mm</text>`;
        });
        
        // 하단 기준선
        svg += `<line x1="${pad.left}" y1="${H - pad.bottom}" x2="${pad.left + pw}" y2="${H - pad.bottom}" stroke="#94a3b8" stroke-width="1"/>`;
        svg += `<text x="${pad.left + pw / 2}" y="${H - 8}" text-anchor="middle" font-size="9" font-weight="600" fill="#64748b" font-family="'Segoe UI', sans-serif">정착 및 이음 소요길이 비교 (KDS 14 20 52)</text>`;
        svg += '</svg>';
        
        return `
        <div class="pillar-card card-splice-diagram" style="margin-bottom:14px;">
            <div class="card-header">
                <span class="card-icon">📏</span>
                <span class="card-title">철근 정착 및 이음 소요길이 비교 다이어그램</span>
            </div>
            <div class="card-body" style="display:flex;justify-content:center;padding:12px;background:#fafafa;">
                ${svg}
            </div>
        </div>`;
    },

    generatePmCardHtml(resultData) {
        if (!resultData) return '';
        const pm = resultData.pm || (resultData.pmCurve || resultData.pm_points ? {
            combo: '1.2D + 1.6L (설계하중)',
            Pu: resultData.Pu || (resultData.Pu_kN ? resultData.Pu_kN * 1e3 : 1500000),
            Mu: resultData.Mu || (resultData.Mu_kNm ? resultData.Mu_kNm * 1e6 : (resultData.Mux_kNm ? resultData.Mux_kNm * 1e6 : 200000000)),
            Mrθ: resultData.Mu || (resultData.Mu_kNm ? resultData.Mu_kNm * 1e6 : (resultData.Mux_kNm ? resultData.Mux_kNm * 1e6 : 200000000)),
            phiPn0: resultData.phi_Pn_max || (resultData.phiPn0_kN ? resultData.phiPn0_kN * 1e3 : 4000000),
            phiMnθ: resultData.phi_Mn || (resultData.phiMn_kNm ? resultData.phiMn_kNm * 1e6 : 350000000),
            dcr: resultData.governing_dcr || resultData.dcr || 0.65,
            pmCurve: resultData.pmCurve || resultData.pm_points
        } : null);

        if (!pm || (!pm.pmCurve && !pm.pm_points)) return '';

        let svgHtml = '';
        if (window.RedcrColumnReport && typeof window.RedcrColumnReport.pmCurveSVG === 'function') {
            svgHtml = window.RedcrColumnReport.pmCurveSVG(pm);
        }

        if (!svgHtml) return '';

        return `
        <div class="pillar-card card-pm-diagram" style="margin-bottom:14px;">
            <div class="card-header">
                <span class="card-icon">📈</span>
                <span class="card-title">P-M 상관곡선 다이어그램 (P-M Interaction Diagram)</span>
            </div>
            <div class="card-body" style="display:flex;justify-content:center;padding:12px;background:#ffffff;">
                ${svgHtml}
            </div>
        </div>`;
    },

    formatSectionTitle(key) {
        const map = {
            flexure: '1. 휨 모멘트 성능 검토 (Flexural Capacity φMn)',
            shear: '2. 전단력 성능 검토 (Shear Capacity φVn)',
            soil_bearing: '3. 지반 접지압 및 지내력 검토 (Soil Bearing Pressure)',
            one_way_shear: '4. 1방향 보전단 검토 (One-way Shear)',
            punching_shear: '5. 2방향 펀칭 전단 검토 (Punching Shear)',
            axial_compression: '6. 축압축 좌굴강도 검토 (Axial Compression Pn)',
            axial_tension: '7. 축인장 파단강도 검토 (Axial Tension Tn)',
            interaction: '8. P-M 상관식 검토 (Biaxial Interaction)',
            pm: '8. P-M 상관식 검토 (Biaxial Interaction)',
            capacity_table: '단면 성능 및 배근 일람표 (Capacity Table)',
            bar_details: '철근별 응력 및 변형률 상세 (Rebar Stress & Strain)',
            pm_points: 'P-M 상관곡선 좌표점 (P-M Interaction Points)',
            beam_details: '부재별 설계 결과 일람표 (Beam Member Details)',
            visual_data: '단면 기하 형상 상세 (Visual Geometry Details)',
            bolt_shear: '볼트 전단강도 검토 (Bolt Shear Capacity)',
            bolt_tension: '볼트 인장강도 검토 (Bolt Tensile Capacity)',
            bearing: '볼트 지압강도 검토 (Bearing Capacity)',
            baseplate: '베이스플레이트 지압 및 휨 검토 (Baseplate Capacity)',
            deflection: '사용성 처짐 검토 (Deflection Check)',
            vibration: '바닥판 진동 사용성 검토 (Floor Vibration)',
            stiffness: '단면 강성 및 2차 모멘트 (Section Stiffness)'
        };
        return map[key] || (key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '));
    },

    /**
     * 54종 전 단위부재 공통 표준화 KDS A4 계산서 렌더러 (MIDAS Gen / re-DCR 일치 포맷)
     */
    renderA4Sheet(container, resultData, currentModulePath, inputParams) {
        if (!container || !resultData) return;
        const dcr = Number(resultData.governing_dcr) || Number(resultData.max_dcr) || Number(resultData.dcr) || 0.0;
        const isOk = (resultData.status === 'OK' || resultData.status === 'PASS') && dcr <= 1.0;
        const modName = (window.allModules && window.allModules.find(m => m.key === currentModulePath)?.name) || currentModulePath || '단위부재';

        // 제원 및 재료 정보 문자열 조립
        const src = inputParams || resultData.inputs || resultData;
        const geomParts = [];
        if (src.b && src.h) geomParts.push(`${src.b} × ${src.h} mm`);
        else if (src.bw && src.h) geomParts.push(`${src.bw} × ${src.h} mm`);
        else if (src.B && src.H) geomParts.push(`${src.B} × ${src.H} mm`);
        else if (src.D) geomParts.push(`D${src.D} mm`);
        else if (src.section_name) geomParts.push(src.section_name);
        
        const matParts = [];
        if (src.fck) matParts.push(`fck = ${src.fck} MPa`);
        if (src.fy) matParts.push(`fy = ${src.fy} MPa`);
        if (src.fyt) matParts.push(`fyt = ${src.fyt} MPa`);
        if (src.steel_grade || src.grade) matParts.push(`강재: ${src.steel_grade || src.grade}`);

        const specText = geomParts.length > 0 ? `${modName} (${geomParts.join(', ')})` : modName;
        const matText = matParts.length > 0 ? matParts.join(' · ') : 'KDS 표준 재료';

        let html = `
        <div class="a4-sheet-page pure-white-sheet">
            <!-- 보고서 대제목 (h1) -->
            <h1>${modName} Design Report</h1>

            <!-- 부재 규격 및 재료 요약 배너 -->
            <div class="rpt-spec-banner">
                <b>부재 규격:</b> ${specText} · <b>재료 강도:</b> ${matText}
            </div>

            <div class="a4-sheet-body">
                <!-- 1. 단면 제원 및 입력 파라미터 -->
                <h2>1. Member Section & Design Parameters</h2>
                <div class="sheet-content-block">
                    ${this.generateInputsHtml(resultData, inputParams)}
                </div>

                <!-- 2. 한계상태별 안전성 종합 검토표 -->
                <h2>2. Safety Verification Summary</h2>
                <div class="sheet-content-block">
                    ${this.generateCheckTableHtml(resultData)}
                </div>

                <!-- 3. 공학 다이어그램 (P-M / 접지압 / 정착이음) -->
                ${this.generateEngineeringDiagramsHtml(resultData)}

                <!-- 4. KDS 기준 수식 기반 상세 계산 과정 -->
                <h2>3. KDS Engineering Calculation Steps</h2>
                <div class="sheet-content-block">
                    ${this.generateStepsHtml(resultData)}
                </div>

                <!-- 5. 최종 종합 판정 -->
                <h2>4. Summary Verdict</h2>
                <div class="sheet-verdict-box ${isOk ? 'verdict-pass' : 'verdict-fail'}" style="margin-top:8px;">
                    <div class="verdict-icon">${isOk ? '✓' : '⚠'}</div>
                    <div class="verdict-content">
                        <div class="verdict-title">${isOk ? 'KDS 설계기준 만족 (STRUCTURAL INTEGRITY OK)' : 'KDS 설계기준 초과 (STRENGTH LIMIT EXCEEDED)'}</div>
                        <div class="verdict-desc">
                            ${isOk 
                                ? `본 부재 단면은 KDS 구조설계기준의 모든 한계상태(최대 DCR ${dcr.toFixed(3)} ≤ 1.0)를 만족하므로 구조적으로 안전합니다.` 
                                : `본 부재 단면의 최대 DCR은 ${dcr.toFixed(3)}로 한계상태(1.0)를 초과하였으므로 단면 증대 또는 배근 보강이 필요합니다.`}
                        </div>
                    </div>
                </div>
            </div>

            <div class="a4-sheet-footer" style="margin-top:24px;border-top:1px solid #e2e8f0;padding-top:8px;display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;">
                <span>AltDP 2nd Structural Member Designer — KDS Engineering Engine</span>
                <span>KDS 14 20 / KDS 14 31</span>
            </div>
        </div>`;

        container.innerHTML = html;
    }
};
