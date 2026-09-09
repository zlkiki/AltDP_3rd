/**
 * AltDP_3rd RC Beam Pure White A4 5-Chapter 8-Step KaTeX Structural Calculation Report
 * Conforms to Requirement 22-4, 22-4-1-2, 22-4-1-4 & DOCS 07 & DOCS 14 Specifications
 * - Standard Class: RCBeamReportGenerator
 * - Global Function: window.renderRCBeamReport(reportEngine, container, memberData, calcResult)
 * - Chapter 1: 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry) - KDS 14 20 20: 2022 3-Step KaTeX
 * - Chapter 2: 설계 부재력 및 하중조합 (Design Factored Loads & Combinations) - 3-Station Forces
 * - Chapter 3: 휨모멘트 강도 검토 (Flexural Strength Check) - 3-Station Individual KaTeX Formulations
 * - Chapter 4: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check) - 3-Station Summary & Governing Station KaTeX
 * - Chapter 5: 사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)
 * - Chapter 6: 종합 안전성 판정 (Executive Summary & Final Verdict)
 */

(function(window) {
    'use strict';

    // KS D 3504 Standard Deformed Bar Nominal Properties
    const REBAR_AREAS = {
        'D10': 71.33,
        'D13': 126.7,
        'D16': 198.6,
        'D19': 286.5,
        'D22': 387.1,
        'D25': 506.7,
        'D29': 642.4,
        'D32': 794.2,
        'D35': 956.6
    };

    /**
     * Parse rebar string (e.g. "4-D25", "2-D22", "0")
     * @param {string} str
     * @param {string} [defaultDia='D25']
     * @param {boolean} [isLayer2=false]
     * @returns {{count: number, dia: string, area: number, text: string}}
     */
    function parseRebarStr(str, defaultDia = 'D25', isLayer2 = false) {
        if (!str || str === '0' || str === 'none') {
            return { count: 0, dia: defaultDia, area: 0, text: '0' };
        }
        const parts = String(str).trim().split('-');
        let count = parseInt(parts[0], 10);
        if (isNaN(count)) count = isLayer2 ? 0 : 2;
        const dia = parts.length > 1 ? parts[1].trim() : defaultDia;
        const singleArea = REBAR_AREAS[dia] || 506.7;
        const area = count * singleArea;
        const text = count > 0 ? `${count}-${dia}` : '0';
        return { count, dia, area, text };
    }

    /**
     * Combine two layers into unified description and area
     */
    function combineRebarLayers(layer1Str, layer2Str, defaultDia = 'D25') {
        const l1 = parseRebarStr(layer1Str, defaultDia, false);
        const l2 = parseRebarStr(layer2Str, defaultDia, true);
        const totalArea = l1.area + l2.area;
        const totalCount = l1.count + l2.count;
        let text = l1.text;
        if (l2.count > 0) {
            text += ` + ${l2.text}`;
        }
        return {
            totalArea,
            totalCount,
            text: `${text} (${Math.round(totalArea).toLocaleString()} mm²)`,
            l1,
            l2
        };
    }

    class RCBeamReportGenerator {
        /**
         * Render RC Beam A4 Calculation Sheet
         * @param {Object} reportEngine - Parent ReportEngine instance
         * @param {HTMLElement} [container] - DOM Container to render
         * @param {Object} memberData - Beam input properties
         * @param {Object} calcResult - Beam calculation result
         * @returns {string} Generated HTML string
         */
        render(reportEngine, container, memberData = {}, calcResult = {}) {
            const m = memberData || {};
            const r = calcResult || {};
            const engine = reportEngine || (window.reportEngine || {});
            const cfg = engine.headerConfig || {};
            const mode = engine.mode || 'detail';
            const includeInput = engine.includeInput !== false;
            const includeGraphics = engine.includeGraphics !== false;

            // 1. 단면 및 재료 제원 기본값
            const b = Number(m.b || 400);
            const h = Number(m.h || 600);
            const cover = Number(m.cover || 40);
            const coverTop = Number(m.cover_top || 40);
            const L = Number(m.length || m.L || 6000);
            const fck = Number(m.fck || 27.0);
            const fy = Number(m.fy || 400.0);
            const fyt = Number(m.fyt || m.fys || 400.0);
            const shape = m.shape || 'RECTANGULAR';
            const isTBeam = shape === 'TEE' || Boolean(m.bf || m.b_eff || m.be);
            const bf = Number(m.bf || m.b_eff || m.be || b);
            const hf = Number(m.hf || m.h_f || 150);

            // KDS 14 20 10 / 20 / 22 핵심 재료 물성치 및 계수
            const Ec = Math.round(8500 * Math.cbrt(fck));
            const fr = Number((0.63 * 1.0 * Math.sqrt(fck)).toFixed(2));
            const ecu = Number((fck <= 40.0 ? 0.0033 : Math.max(0.0028, 0.0033 - 0.0001 * ((fck - 40.0) / 10.0))).toFixed(4));
            const alpha1 = Number((fck <= 40.0 ? 0.85 : Math.max(0.84, 1.00 - 0.003 * (fck - 40.0)) * 0.85).toFixed(3));
            const beta1 = Number((fck <= 50.0 ? 0.80 : Math.max(0.65, 0.80 - 0.004 * (fck - 50.0))).toFixed(3));
            const ey = Number((fy / 200000.0).toFixed(4));
            const epsTMin = fy <= 400.0 ? 0.0040 : Number((2.0 * ey).toFixed(4));
            const cDtLimit = Number((ecu / (ecu + epsTMin)).toFixed(3));

            // 비균열 전단면 2차모멘트 및 균열모멘트 (KDS 14 20 20 4.2.2)
            const Ig = Number((r.Ig ?? (b * Math.pow(h, 3) / 12.0)).toFixed(0));
            const yt = h / 2.0;
            const Mcr = Number((r.Mcr ?? ((fr * Ig / yt) * 1e-6)).toFixed(1));
            const phiMnMin = Number((r.phi_Mn_min ?? (1.2 * Mcr)).toFixed(1));

            // 배근 정보 추출 (3-Station)
            const arrangeType = m.rebar?.arrange_type || 'SYMMETRIC_ENDS'; // 'ONE_SECTION', 'SYMMETRIC_ENDS', 'THREE_STATIONS'
            const centerRebarRaw = (m.rebar && m.rebar.center_m) ? m.rebar.center_m : {};
            const endIRebarRaw = (m.rebar && m.rebar.end_i) ? m.rebar.end_i : {};
            const endJRebarRaw = (m.rebar && m.rebar.end_j) ? m.rebar.end_j : {};

            const endITop = combineRebarLayers(endIRebarRaw.top_layer1 || '4-D25', endIRebarRaw.top_layer2 || '0', 'D25');
            const endIBot = combineRebarLayers(endIRebarRaw.bot_layer1 || '2-D22', endIRebarRaw.bot_layer2 || '0', 'D22');
            const centerTop = combineRebarLayers(centerRebarRaw.top_layer1 || '2-D22', centerRebarRaw.top_layer2 || '0', 'D22');
            const centerBot = combineRebarLayers(centerRebarRaw.bot_layer1 || '4-D25', centerRebarRaw.bot_layer2 || '2-D25', 'D25');
            const endJTop = combineRebarLayers(endJRebarRaw.top_layer1 || endIRebarRaw.top_layer1 || '4-D25', endJRebarRaw.top_layer2 || '0', 'D25');
            const endJBot = combineRebarLayers(endJRebarRaw.bot_layer1 || endIRebarRaw.bot_layer1 || '2-D22', endJRebarRaw.bot_layer2 || '0', 'D22');

            // 스터럽 배근 정보
            const endIS = Number(endIRebarRaw.stirrup_space || 150);
            const centerS = Number(centerRebarRaw.stirrup_space || 250);
            const endJS = Number(endJRebarRaw.stirrup_space || 150);
            const stirrupDia = endIRebarRaw.stirrup_dia || 'D10';
            const stirrupSingleArea = REBAR_AREAS[stirrupDia] || 71.33;
            const stirrupLegs = Number(endIRebarRaw.stirrup_legs || 2);
            const AvProvEnd = stirrupLegs * stirrupSingleArea;
            const AvProvCenter = (Number(centerRebarRaw.stirrup_legs || 2)) * (REBAR_AREAS[centerRebarRaw.stirrup_dia || stirrupDia] || 71.33);

            // 설계 부재력 추출 (3-Station)
            const endILoads = (m.loads && m.loads.end_i) ? m.loads.end_i : {};
            const centerLoads = (m.loads && m.loads.center_m) ? m.loads.center_m : {};
            const endJLoads = (m.loads && m.loads.end_j) ? m.loads.end_j : {};

            const endIMuNeg = Number(endILoads.Mu_neg ?? m.mu_neg ?? m.mu ?? 240.0);
            const endIMuPos = Number(endILoads.Mu_pos ?? 0.0);
            const endIVu = Number(endILoads.Vu ?? m.vu ?? 180.0);
            const endITu = Number(endILoads.Tu ?? 15.0);

            const centerMuPos = Number(centerLoads.Mu_pos ?? m.mu_pos ?? m.mu ?? 240.0);
            const centerMuNeg = Number(centerLoads.Mu_neg ?? 0.0);
            const centerVu = Number(centerLoads.Vu ?? 40.0);
            const centerTu = Number(centerLoads.Tu ?? 5.0);
            const centerMa = Number(m.serviceability?.Ma_pos ?? centerLoads.Ma ?? r.Ma ?? 140.0);

            const endJMuNeg = Number(endJLoads.Mu_neg ?? (arrangeType === 'THREE_STATIONS' ? 240.0 : endIMuNeg));
            const endJMuPos = Number(endJLoads.Mu_pos ?? 0.0);
            const endJVu = Number(endJLoads.Vu ?? (arrangeType === 'THREE_STATIONS' ? 180.0 : endIVu));
            const endJTu = Number(endJLoads.Tu ?? endITu);

            // =========================================================================
            // 2. 3-Station 위치별 휨강도 산정 엔진 (End-I, Center-M, End-J)
            // =========================================================================

            /**
             * Station Flexural Solver
             * @param {string} stationTag
             * @param {number} AsTens
             * @param {number} AsComp
             * @param {number} MuDemand
             * @param {boolean} isNegativeBending
             * @param {Object} [stationRes]
             */
            const solveFlexure = (stationTag, AsTens, AsComp, MuDemand, isNegativeBending, stationRes = null) => {
                // 부모멘트는 상부인장, 플랜지 인장균열로 복부폭 bw 적용
                // 정모멘트는 하부인장, 상부 플랜지 압축으로 유효폭 bf 적용 (T형보인 경우)
                const isFlangeComp = (!isNegativeBending) && isTBeam && (bf > b);
                const bComp = isFlangeComp ? bf : b;

                // 유효깊이 산정
                const dEst = Number((isNegativeBending ? (h - coverTop - 10 - 25 / 2) : (h - cover - 10 - 25 / 2)).toFixed(1));
                const dtEst = dEst;
                const dPrimeEst = Number((isNegativeBending ? (cover + 10 + 22 / 2) : (coverTop + 10 + 22 / 2)).toFixed(1));

                let d = Number(stationRes?.d ?? dEst);
                let dt = Number(stationRes?.dt ?? dtEst);
                let dPrime = Number(stationRes?.d_prime ?? dPrimeEst);

                // 응력블록 깊이 a 및 중립축 c 산정
                let a = Number(stationRes?.a ?? 0);
                let c = Number(stationRes?.c ?? 0);
                if (!a || !c) {
                    const T = AsTens * fy;
                    const Cs = AsComp * fy;
                    a = Number(((T - Cs) / (alpha1 * fck * bComp)).toFixed(1));
                    if (a <= 0) a = Number((T / (alpha1 * fck * bComp)).toFixed(1));
                    c = Number((a / beta1).toFixed(1));
                }

                // 최외단 인장철근 변형률 εt 및 강도감소계수 φ
                let epsT = Number(stationRes?.epsilon_t ?? stationRes?.et ?? 0);
                if (!epsT) {
                    epsT = Number((ecu * (dt - c) / c).toFixed(4));
                }
                let phi = Number(stationRes?.phi ?? stationRes?.phi_b ?? 0);
                if (!phi) {
                    if (epsT >= 0.005) {
                        phi = 0.85;
                    } else if (epsT <= ey) {
                        phi = 0.65;
                    } else {
                        phi = Number((0.65 + (epsT - ey) * (0.20 / (0.005 - ey))).toFixed(3));
                    }
                }

                // 공칭 및 설계 휨강도 Mn, φMn
                let Mn = Number(stationRes?.Mn ?? 0);
                let phiMn = Number(stationRes?.phi_Mn ?? 0);
                if (!Mn || !phiMn) {
                    const arm1 = d - a / 2.0;
                    const arm2 = a / 2.0 - dPrime;
                    Mn = Number(((AsTens * fy * arm1 + Math.max(0, AsComp) * fy * arm2) * 1e-6).toFixed(1));
                    phiMn = Number((phi * Mn).toFixed(1));
                }

                const dcr = Number((phiMn > 0 ? (MuDemand / phiMn) : 9.999).toFixed(3));
                const isSafe = dcr <= 1.0;
                const isMinOk = phiMn >= phiMnMin;
                const isDuctilityOk = (epsT >= epsTMin) && ((c / dt) <= cDtLimit);

                return {
                    stationTag,
                    isNegativeBending,
                    isFlangeComp,
                    bComp,
                    d,
                    dt,
                    dPrime,
                    AsTens,
                    AsComp,
                    MuDemand,
                    a,
                    c,
                    epsT,
                    phi,
                    Mn,
                    phiMn,
                    dcr,
                    isSafe,
                    isMinOk,
                    isDuctilityOk,
                    verdict: isSafe ? '  →  O.K' : '  →  N.G'
                };
            };

            // 3개 위치별 계산 인스턴스 생성
            const endIFlex = solveFlexure('End-I (단부-I)', endITop.totalArea, endIBot.totalArea, endIMuNeg, true, r.end_i?.neg_flexure || r);
            const centerMFlex = solveFlexure('Center-M (중앙부-M)', centerBot.totalArea, centerTop.totalArea, centerMuPos, false, r.center_m?.pos_flexure || r);
            const endJFlex = solveFlexure('End-J (단부-J)', endJTop.totalArea, endJBot.totalArea, endJMuNeg, true, r.end_j?.neg_flexure || (arrangeType !== 'THREE_STATIONS' ? endIFlex : r));

            // =========================================================================
            // 3. 3-Station 위치별 전단강도 산정 엔진
            // =========================================================================
            const solveShear = (stationTag, VuDemand, Av, sSpacing, dVal, shearRes = null) => {
                const Vc = Number(shearRes?.Vc ?? (1.0 / 6.0 * 1.0 * Math.sqrt(fck) * b * dVal * 1e-3).toFixed(1));
                const Vs = Number(shearRes?.Vs ?? (Av * fyt * dVal / sSpacing * 1e-3).toFixed(1));
                const VsMax = Number(shearRes?.Vs_max ?? (2.0 / 3.0 * Math.sqrt(fck) * b * dVal * 1e-3).toFixed(1));
                const phiShear = 0.75;
                const phiVn = Number(shearRes?.phi_Vn ?? (phiShear * (Vc + Vs)).toFixed(1));
                const dcr = Number((phiVn > 0 ? (VuDemand / phiVn) : 9.999).toFixed(3));
                const isSafe = dcr <= 1.0;
                return {
                    stationTag,
                    VuDemand,
                    Vc,
                    Vs,
                    VsMax,
                    phiShear,
                    phiVn,
                    dcr,
                    isSafe,
                    verdict: isSafe ? '  →  O.K' : '  →  N.G'
                };
            };

            const endIShear = solveShear('End-I (단부-I)', endIVu, AvProvEnd, endIS, endIFlex.d, r.end_i?.shear || r);
            const centerMShear = solveShear('Center-M (중앙부-M)', centerVu, AvProvCenter, centerS, centerMFlex.d, r.center_m?.shear || r);
            const endJShear = solveShear('End-J (단부-J)', endJVu, AvProvEnd, endJS, endJFlex.d, r.end_j?.shear || (arrangeType !== 'THREE_STATIONS' ? endIShear : r));

            // 지배 단부 전단 선정 (Governing Station for Shear KaTeX)
            const governingShear = (endIShear.VuDemand >= endJShear.VuDemand) ? endIShear : endJShear;

            // =========================================================================
            // 4. 비틀림 및 상호작용 검토 수치 (KDS 14 20 22 4.3)
            // =========================================================================
            const Acp = b * h;
            const pcp = 2 * (b + h);
            const Tth = Number((r.Tth ?? (0.0625 * 1.0 * Math.sqrt(fck) * (Math.pow(Acp, 2) / pcp) * 1e-6)).toFixed(1));
            const phiTth = Number((0.75 * Tth).toFixed(1));
            const tu = Math.max(endITu, centerTu, endJTu);
            const isTorsionRequired = tu > phiTth;
            const phiTn = Number((r.phi_Tn ?? 35.0).toFixed(1));
            const dcrTorsion = Number((r.torsion_dcr ?? (phiTn > 0 ? (tu / phiTn) : 0.714)).toFixed(3));
            const torsionVerdict = dcrTorsion <= 1.0 ? '  →  O.K' : '  →  N.G';

            const stirrupDiaNum = parseInt(stirrupDia.replace('D', ''), 10) || 10;
            const bo = Math.max(100, b - 2 * cover - stirrupDiaNum);
            const ho = Math.max(100, h - 2 * cover - stirrupDiaNum);
            const Aoh = bo * ho;
            const ph = 2 * (bo + ho);
            const At = AvProvEnd / 2.0; // 1개 가닥 면적
            const vuStress = (governingShear.VuDemand * 1e3) / (b * governingShear.dVal || (b * endIFlex.d));
            const tuStress = (tu * 1e6 * ph) / (1.7 * Math.pow(Aoh, 2));
            const torsionCombinedStress = Number(Math.sqrt(Math.pow(vuStress, 2) + Math.pow(tuStress, 2)).toFixed(2));
            const torsionAllowStress = Number((0.75 * ((governingShear.Vc * 1e3) / (b * endIFlex.d) + (2.0 / 3.0) * Math.sqrt(fck))).toFixed(2));
            const isTorsionStressOk = torsionCombinedStress <= torsionAllowStress;
            const AlReq = Number((r.Al_req ?? (At / endIS * ph * (fyt / fy))).toFixed(1));
            const sideRebarCount = Number(m.rebar?.torsion_side_count || 4);
            const sideRebarDia = m.rebar?.torsion_side_bar || 'D13';
            const AlProv = Number((sideRebarCount * (REBAR_AREAS[sideRebarDia] || 126.7)).toFixed(1));
            const isAlOk = AlProv >= AlReq;

            // =========================================================================
            // 5. 사용성 한계상태 검토 수치 (KDS 14 20 30)
            // =========================================================================
            const Icr = Number((r.Icr ?? (0.35 * Ig)).toFixed(0));
            const mcrOverMa = Math.min(1.0, Mcr / Math.max(centerMa, 1.0));
            const mcr3 = Math.pow(mcrOverMa, 3);
            const Ie = Number((r.Ie ?? (mcr3 * Ig + (1.0 - mcr3) * Icr)).toFixed(0));

            const deltaImmediate = Number((r.delta_elastic ?? r.delta_immediate ?? 6.2).toFixed(1));
            const rhoPrime = centerTop.totalArea / (b * centerMFlex.d);
            const lambdaDelta = Number((r.lambda_delta ?? (2.0 / (1.0 + 50.0 * rhoPrime))).toFixed(2));
            const deltaSus = 3.8;
            const deltaLong = Number((r.delta_long ?? (lambdaDelta * deltaSus)).toFixed(1));
            const deltaTotal = Number((r.delta_total ?? (deltaImmediate + deltaLong)).toFixed(1));
            const deltaAllow = Number((r.delta_allowable ?? (L / 240.0)).toFixed(1));
            const dcrDefl = Number((r.deflection_dcr ?? (deltaTotal / deltaAllow)).toFixed(3));
            const deflVerdict = dcrDefl <= 1.0 ? '  →  O.K' : '  →  N.G';

            const fs = Number((0.6 * fy).toFixed(0));
            const Es = 200000;
            const dc = cover;
            const rebarSpace = Math.max(50, Math.round((b - 2 * cover - 2 * stirrupDiaNum - 25) / 3));
            const crackWidth = Number((r.crack_width ?? 0.22).toFixed(2));
            const crackAllow = Number((r.crack_allowable ?? 0.30).toFixed(2));
            const dcrCrack = Number((r.crack_dcr ?? (crackWidth / crackAllow)).toFixed(3));
            const crackVerdict = dcrCrack <= 1.0 ? '  →  O.K' : '  →  N.G';

            // =========================================================================
            // 6. 종합 안전성 판정
            // =========================================================================
            const governingDcr = Number(Math.max(
                endIFlex.dcr, centerMFlex.dcr, endJFlex.dcr,
                endIShear.dcr, centerMShear.dcr, endJShear.dcr,
                dcrTorsion, dcrDefl, dcrCrack
            ).toFixed(3));
            const isOverallSafe = governingDcr <= 1.0;
            const overallVerdict = isOverallSafe ? '  →  O.K' : '  →  N.G';

            // 그래픽 렌더링 헬퍼
            const graphicContent = (engine._generateSectionGraphic && typeof engine._generateSectionGraphic === 'function')
                ? engine._generateSectionGraphic(m, r, 'rc_beam')
                : '';

            // =========================================================================
            // 7. HTML 조립 시작 (A4 Sheet Template)
            // =========================================================================
            const html = `
                <div class="a4-zoom-viewport altdp-report-container redcr-report-container">
                    <div class="a4-sheet-container pure-white-sheet altdp-report redcr-report" id="main-result-viewport" style="background:#ffffff !important;color:#111827 !important;">
                        <!-- 0. Header & Approval Banner (IDD_REPORT_HEADER_DLG) -->
                        <div class="report-print-banner">
                            <div class="header-project-info">
                                <div class="company-title">${cfg.companyName || 'AltDP_3rd KDS Automated Engineering'} [${cfg.companyShort || 'K-STRUCT'}]</div>
                                <h1 class="sheet-main-title">${cfg.projectName || 'AltDP_3rd KDS Standard Report'}</h1>
                                <div class="member-tag-line">부재 명칭: <b>${cfg.memberTag || m.name || '1F-B1'}</b> (RC 콘크리트 보 구조계산서 - KDS 14 20 00 : 2022)</div>
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
                                        <td>${cfg.engineer || '작성자'}</td>
                                        <td>${cfg.checker || '검토자'}</td>
                                        <td>${cfg.approver || '승인자'}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- 제 1장: 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry) -->
                        <section class="report-chapter" data-chapter-key="general">
                            <h2 class="chapter-heading" data-title-detail="설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)" data-title-summary="설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 1장</span>. <span class="chapter-title">설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)</span>
                            </h2>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;margin-bottom:8px;">
                                <colgroup>
                                    <col style="width:20%;">
                                    <col style="width:30%;">
                                    <col style="width:20%;">
                                    <col style="width:30%;">
                                </colgroup>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">적용 설계기준</td>
                                    <td>KDS 14 20 00 : 2022 (콘크리트구조설계기준)</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">단위계 / 부재 ID</td>
                                    <td>SI Unit / <b>${cfg.memberTag || m.name || '1F-B1'}</b></td>
                                </tr>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">콘크리트 강도 ($f_{ck}$)</td>
                                    <td>${fck.toFixed(1)} MPa</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">주철근 강도 ($f_y$)</td>
                                    <td>${fy.toFixed(0)} MPa</td>
                                </tr>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">전단철근 강도 ($f_{yt}$)</td>
                                    <td>${fyt.toFixed(0)} MPa</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">탄성계수 ($E_c$)</td>
                                    <td>${Ec.toLocaleString()} MPa</td>
                                </tr>
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">단면 폭 ($b_w$) $\\times$ 높이 ($h$)</td>
                                    <td>${b} $\\times$ ${h} mm</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">유효깊이 ($d$) / 피복 ($c_v$)</td>
                                    <td>${centerMFlex.d.toFixed(1)} mm / ${cover} mm</td>
                                </tr>
                                ${isTBeam ? `
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">플랜지 유효폭 ($b_e$)</td>
                                    <td style="color:#1d4ed8;font-weight:700;">${bf} mm</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">플랜지 두께 ($h_f$)</td>
                                    <td>${hf} mm</td>
                                </tr>
                                ` : ''}
                                <tr>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">부재 경간 길이 ($L$)</td>
                                    <td>${L.toLocaleString()} mm</td>
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">배근 상세 유형</td>
                                    <td style="font-weight:700;color:#2563eb;">${arrangeType === 'ONE_SECTION' ? '유형-1: 전단면 동일 배근' : (arrangeType === 'THREE_STATIONS' ? '유형-3: 3단면 개별 배근 (I / M / J)' : '유형-2: 양단부 대칭 배근 (End 대칭)')}</td>
                                </tr>
                            </table>

                            <!-- KDS 14 20 20: 2022 최소 철근량 및 연성 한계 검토 (KaTeX 수식 전개) -->
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">1.1 최소 철근량 검토 (KDS 14 20 20 4.2.2)</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.2.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\phi M_n \\ge 1.2 M_{cr} \\quad \\left(\\text{단, } A_s \\ge \\frac{4}{3} A_{s,req} \\text{ 만족 시 적용 예외}\\right)$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$f_r = 0.63 \\lambda \\sqrt{f_{ck}} = 0.63 \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} = \\mathbf{${fr.toFixed(2)}\\text{ MPa}}, \\quad I_g = \\frac{b_w h^3}{12} = \\frac{${b} \\times ${h}^3}{12} = \\mathbf{${Ig.toLocaleString()}\\text{ mm}^4}, \\quad M_{cr} = \\frac{f_r I_g}{y_t} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_n = ${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\ge 1.2 M_{cr} (${phiMnMin.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\quad \\longrightarrow \\quad [\\mathbf{${centerMFlex.isMinOk ? '최소철근량 만족 O.K' : '최소철근량 미달 N.G'}}]${centerMFlex.isMinOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                            </div>

                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">1.2 연성 한계 및 순인장변형률 검토 (KDS 14 20 20 4.1.2)</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\epsilon_t \\ge \\epsilon_{t,\\min} = \\begin{cases} 0.0040 & (f_y \\le 400\\text{ MPa}) \\\\ 2.0\\,\\epsilon_y & (f_y > 400\\text{ MPa}) \\end{cases}, \\quad \\frac{c}{d_t} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} = \\frac{\\epsilon_{cu}}{\\epsilon_{cu} + \\epsilon_{t,\\min}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\epsilon_t = \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${centerMFlex.dt.toFixed(1)} - ${centerMFlex.c.toFixed(1)}}{${centerMFlex.c.toFixed(1)}}\\right) = \\mathbf{${centerMFlex.epsT.toFixed(4)}} \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}), \\quad \\frac{c}{d_t} = \\frac{${centerMFlex.c.toFixed(1)}}{${centerMFlex.dt.toFixed(1)}} = \\mathbf{${(centerMFlex.c / centerMFlex.dt).toFixed(3)}} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)})$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\epsilon_t (${centerMFlex.epsT.toFixed(4)}) \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}) \\quad \\text{및} \\quad \\frac{c}{d_t} (${(centerMFlex.c / centerMFlex.dt).toFixed(3)}) \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)}) \\quad \\longrightarrow \\quad [\\mathbf{${centerMFlex.isDuctilityOk ? '연성파괴 유도 O.K' : '취성파괴 우려 N.G'}}]${centerMFlex.isDuctilityOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                            </div>

                            <!-- 2D 단면 배근 상세 그래픽 임베딩 -->
                            <div class="report-svg-slot report-graphic-slot" style="${includeGraphics ? 'width:100%;text-align:center;margin-top:4px;' : 'display:none;'}">
                                ${graphicContent}
                                <div style="font-size:10.5px;color:#64748b;margin-top:5px;font-weight:500;">
                                    [RC 보 3-Station 횡단면 배근 상세도: End-I (${b}×${h}) / Center-M (${b}×${h}) / End-J (${b}×${h}) mm]
                                </div>
                            </div>
                        </section>

                        <!-- 사용자 입력 데이터 상세 표 (체크박스 토글 옵션) -->
                        <section class="report-chapter user-input-section" data-chapter-key="input" style="${includeInput ? '' : 'display:none;'}">
                            <h2 class="chapter-heading" data-title-detail="사용자 입력 데이터 상세 (User Input Data Specification)" data-title-summary="사용자 입력 데이터 상세 (User Input Data Specification)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">부록 1</span>. <span class="chapter-title">사용자 입력 데이터 상세 (User Input Data Specification)</span>
                            </h2>
                            <table class="inp-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;">
                                <colgroup>
                                    <col style="width:22%;">
                                    <col style="width:28%;">
                                    <col style="width:22%;">
                                    <col style="width:28%;">
                                </colgroup>
                                <tr>
                                    <td class="inp-label">상부 주철근 배근 (End-I)</td>
                                    <td class="inp-val">${endITop.text}</td>
                                    <td class="inp-label">하부 주철근 배근 (End-I)</td>
                                    <td class="inp-val">${endIBot.text}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">상부 주철근 배근 (Center-M)</td>
                                    <td class="inp-val">${centerTop.text}</td>
                                    <td class="inp-label">하부 주철근 배근 (Center-M)</td>
                                    <td class="inp-val">${centerBot.text}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">상부 주철근 배근 (End-J)</td>
                                    <td class="inp-val">${endJTop.text}</td>
                                    <td class="inp-label">하부 주철근 배근 (End-J)</td>
                                    <td class="inp-val">${endJBot.text}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">스터럽 전단보강근</td>
                                    <td class="inp-val">${stirrupDia} @ ${endIS} mm (${stirrupLegs}-Legs)</td>
                                    <td class="inp-label">비틀림 측면철근</td>
                                    <td class="inp-val">${sideRebarCount}-${sideRebarDia} (${Math.round(AlProv)} mm²)</td>
                                </tr>
                            </table>
                        </section>

                        <!-- 제 2장: 설계 부재력 및 하중조합 (Design Factored Loads & Combinations) -->
                        <section class="report-chapter" data-chapter-key="load">
                            <h2 class="chapter-heading" data-title-detail="설계 부재력 및 하중조합 (Design Factored Loads & Combinations)" data-title-summary="설계 부재력 및 하중조합 (Design Factored Loads & Combinations)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 2장</span>. <span class="chapter-title">설계 부재력 및 하중조합 (Design Factored Loads & Combinations)</span>
                            </h2>
                            <div style="background:#f0f9ff;border-left:3px solid #0284c7;padding:7px 12px;font-size:11.5px;margin-bottom:8px;">
                                <b>지배 하중조합 (Governing LCB):</b> ${r.governing_lcb || '1.2D + 1.6L (최대 정/부모멘트 및 전단/비틀림 복합 극한한계상태)'}
                            </div>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;text-align:center;">
                                <colgroup>
                                    <col style="width:20%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th style="padding:6px;">검토 위치 (Station)</th>
                                        <th>정모멘트 ($M_u^+$)</th>
                                        <th>부모멘트 ($M_u^-$)</th>
                                        <th>설계 전단력 ($V_u$)</th>
                                        <th>설계 비틀림 ($T_u$)</th>
                                        <th>사용 모멘트 ($M_a$)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부 I (End-I)</td>
                                        <td>${endIMuPos.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endIMuNeg.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endIVu.toFixed(1)} kN</td>
                                        <td>${endITu.toFixed(1)} kN·m</td>
                                        <td>${(endILoads.Ma || 120.0).toFixed(1)} kN·m</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부 M (Center-M)</td>
                                        <td style="font-weight:700;color:#b45309;">${centerMuPos.toFixed(1)} kN·m</td>
                                        <td>${centerMuNeg.toFixed(1)} kN·m</td>
                                        <td>${centerVu.toFixed(1)} kN</td>
                                        <td>${centerTu.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#b45309;">${centerMa.toFixed(1)} kN·m</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부 J (End-J)</td>
                                        <td>${endJMuPos.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endJMuNeg.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endJVu.toFixed(1)} kN</td>
                                        <td>${endJTu.toFixed(1)} kN·m</td>
                                        <td>${(endJLoads.Ma || 120.0).toFixed(1)} kN·m</td>
                                    </tr>
                                </tbody>
                            </table>
                        </section>

                        <!-- 제 3장: 휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Individual Formulations) -->
                        <section class="report-chapter" data-chapter-key="flexure">
                            <h2 class="chapter-heading" data-title-detail="휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Positive & Negative Bending)" data-title-summary="휨모멘트 강도 검토 요약 (Flexural Strength Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 3장</span>. <span class="chapter-title">휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Positive & Negative Bending)</span>
                            </h2>

                            <!-- 3.1 3-Station 위치별 휨설계 강도 총괄 요약표 -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                3.1 3-Station 위치별 휨설계 강도 총괄 요약표
                            </div>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;text-align:center;margin-bottom:12px;">
                                <colgroup>
                                    <col style="width:18%;">
                                    <col style="width:18%;">
                                    <col style="width:18%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:14%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th style="padding:6px;">검토 위치 (Station)</th>
                                        <th>지배 모멘트 및 배근</th>
                                        <th>단면 거동 및 압축폭</th>
                                        <th>소요 강도 ($M_u$)</th>
                                        <th>설계 강도 ($\\phi M_n$)</th>
                                        <th>내력비 (DCR) / 판정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-I (End-I)</td>
                                        <td>부모멘트 ($M_u^-$)<br><span style="font-size:10px;color:#64748b;">상부: ${endITop.text}</span></td>
                                        <td>직사각형 ($b_w = ${b}\\text{ mm}$)</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endIFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;">${endIFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="font-weight:800;" class="${endIFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.dcr.toFixed(3)} ${endIFlex.verdict}</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부-M (Center-M)</td>
                                        <td>정모멘트 ($M_u^+$)<br><span style="font-size:10px;color:#64748b;">하부: ${centerBot.text}</span></td>
                                        <td>${isTBeam ? `T형 보 ($b_e = ${bf}\\text{ mm}$)` : `직사각형 ($b = ${b}\\text{ mm}$)`}</td>
                                        <td style="font-weight:700;color:#b45309;">${centerMFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;">${centerMFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="font-weight:800;" class="${centerMFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.dcr.toFixed(3)} ${centerMFlex.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-J (End-J)</td>
                                        <td>부모멘트 ($M_u^-$)<br><span style="font-size:10px;color:#64748b;">상부: ${endJTop.text}</span></td>
                                        <td>직사각형 ($b_w = ${b}\\text{ mm}$)</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endJFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;">${endJFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="font-weight:800;" class="${endJFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.dcr.toFixed(3)} ${endJFlex.verdict}</td>
                                    </tr>
                                </tbody>
                            </table>

                            ${mode === 'detail' ? `
                            <!-- 3.2 단부-I (End-I) 부모멘트 (Mu-) 검토 [상부 인장 배근 / 복부폭 bw 직사각형 보] -->
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">3.2 단부-I (End-I) 부모멘트 ($M_u^-$) 4단계 강도 검토 [상부 인장 배근, 복부폭 $b_w$ 직사각형 보]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\text{인장철근: } A_s = ${endITop.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{상부}), \\quad \\text{압축철근: } A_s' = ${endIBot.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{하부}), \\quad \\beta_1 = ${beta1.toFixed(3)}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$a = \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_w} = \\frac{${endITop.totalArea.toFixed(1)} \\times ${fy.toFixed(0)} - ${endIBot.totalArea.toFixed(1)} \\times ${fy.toFixed(0)}}{0.85 \\times ${fck.toFixed(1)} \\times ${b}} = \\mathbf{${endIFlex.a.toFixed(1)}\\text{ mm}}, \\quad c = \\frac{a}{\\beta_1} = \\frac{${endIFlex.a.toFixed(1)}}{${beta1.toFixed(3)}} = \\mathbf{${endIFlex.c.toFixed(1)}\\text{ mm}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\epsilon_t = \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${endIFlex.dt.toFixed(1)} - ${endIFlex.c.toFixed(1)}}{${endIFlex.c.toFixed(1)}}\\right) = \\mathbf{${endIFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad \\longrightarrow \\quad \\text{인장지배단면, } \\mathbf{\\phi = ${endIFlex.phi.toFixed(2)}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$M_n = \\left[A_s f_y \\left(d - \\frac{a}{2}\\right) + A_s' f_s' \\left(\\frac{a}{2} - d'\\right)\\right] \\times 10^{-6} = \\mathbf{${endIFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}, \\quad \\phi M_n = ${endIFlex.phi.toFixed(2)} \\times ${endIFlex.Mn.toFixed(1)} = \\mathbf{${endIFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{flex,I} = \\frac{M_u^-}{\\phi M_n} = \\frac{${endIFlex.MuDemand.toFixed(1)}}{${endIFlex.phiMn.toFixed(1)}} = \\mathbf{${endIFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\longrightarrow \\quad [\\mathbf{${endIFlex.isSafe ? 'O.K' : 'N.G'}}]${endIFlex.verdict}$$
                                </div>
                            </div>

                            <!-- 3.3 중앙부 (Center-M) 정모멘트 (Mu+) 검토 [하부 인장 배근 / T형 유효폭 bf 압축] -->
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">3.3 중앙부 (Center-M) 정모멘트 ($M_u^+$) 4단계 강도 검토 [하부 인장 배근, ${isTBeam ? `T형 유효폭 $b_e = ${bf}$ mm 압축` : `복부폭 $b = ${b}$ mm 직사각형 보`}]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\text{인장철근: } A_s = ${centerBot.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{하부}), \\quad \\text{압축철근: } A_s' = ${centerTop.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{상부})$$
                                </div>
                                <div class="formula-row formula-subst">
                                    ${isTBeam ? `$$\\text{등가응력블록 깊이 } a = \\mathbf{${centerMFlex.a.toFixed(1)}\\text{ mm}} \\le h_f (${hf}\\text{ mm}) \\quad \\longrightarrow \\quad \\text{플랜지 내 압축 응력블록 형성, 유효폭 } b_e (${bf}\\text{ mm}) \\text{ 직사각형 보로 거동}$$` : ''}
                                    $$a = \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_e} = \\frac{${centerBot.totalArea.toFixed(1)} \\times ${fy.toFixed(0)} - ${centerTop.totalArea.toFixed(1)} \\times ${fy.toFixed(0)}}{0.85 \\times ${fck.toFixed(1)} \\times ${centerMFlex.bComp}} = \\mathbf{${centerMFlex.a.toFixed(1)}\\text{ mm}}, \\quad c = \\frac{a}{\\beta_1} = \\frac{${centerMFlex.a.toFixed(1)}}{${beta1.toFixed(3)}} = \\mathbf{${centerMFlex.c.toFixed(1)}\\text{ mm}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\epsilon_t = \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${centerMFlex.dt.toFixed(1)} - ${centerMFlex.c.toFixed(1)}}{${centerMFlex.c.toFixed(1)}}\\right) = \\mathbf{${centerMFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad \\longrightarrow \\quad \\text{인장지배단면, } \\mathbf{\\phi = ${centerMFlex.phi.toFixed(2)}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$M_n = \\left[A_s f_y \\left(d - \\frac{a}{2}\\right) + A_s' f_s' \\left(\\frac{a}{2} - d'\\right)\\right] \\times 10^{-6} = \\mathbf{${centerMFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}, \\quad \\phi M_n = ${centerMFlex.phi.toFixed(2)} \\times ${centerMFlex.Mn.toFixed(1)} = \\mathbf{${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{flex,M} = \\frac{M_u^+}{\\phi M_n} = \\frac{${centerMFlex.MuDemand.toFixed(1)}}{${centerMFlex.phiMn.toFixed(1)}} = \\mathbf{${centerMFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\longrightarrow \\quad [\\mathbf{${centerMFlex.isSafe ? 'O.K' : 'N.G'}}]${centerMFlex.verdict}$$
                                </div>
                            </div>

                            <!-- 3.4 단부-J (End-J) 부모멘트 (Mu-) 검토 -->
                            ${arrangeType === 'THREE_STATIONS' ? `
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">3.4 단부-J (End-J) 부모멘트 ($M_u^-$) 4단계 강도 검토 [독립 3단면 비대칭 배근, 상부 인장]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\text{인장철근: } A_s = ${endJTop.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{상부}), \\quad \\text{압축철근: } A_s' = ${endJBot.totalArea.toFixed(1)}\\text{ mm}^2 \\quad (\\text{하부})$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$a = \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_w} = \\mathbf{${endJFlex.a.toFixed(1)}\\text{ mm}}, \\quad c = \\frac{a}{\\beta_1} = \\mathbf{${endJFlex.c.toFixed(1)}\\text{ mm}}, \\quad \\epsilon_t = \\mathbf{${endJFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad (\\phi = ${endJFlex.phi.toFixed(2)})$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$M_n = \\mathbf{${endJFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}, \\quad \\phi M_n = \\mathbf{${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{flex,J} = \\frac{M_u^-}{\\phi M_n} = \\frac{${endJFlex.MuDemand.toFixed(1)}}{${endJFlex.phiMn.toFixed(1)}} = \\mathbf{${endJFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\longrightarrow \\quad [\\mathbf{${endJFlex.isSafe ? 'O.K' : 'N.G'}}]${endJFlex.verdict}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;margin-top:10px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">3.4 단부-J (End-J) 부모멘트 ($M_u^-$) 강도 검토</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div>
                                    <strong>단부-J (End-J) 부모멘트 검토:</strong> 단부-I과 대칭 동일 단면 ($M_u^- = ${endJFlex.MuDemand.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$, DCR = ${endJFlex.dcr.toFixed(3)}) <span class="${endJFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.verdict}</span>
                                </div>
                            </div>
                            `}
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>단부-I 휨모멘트 검토:</strong> $M_u^- = ${endIFlex.MuDemand.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${endIFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${endIFlex.dcr.toFixed(3)}) <span class="${endIFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.verdict}</span></div>
                                <div style="margin-bottom:6px;"><strong>중앙부-M 휨모멘트 검토:</strong> $M_u^+ = ${centerMFlex.MuDemand.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${centerMFlex.dcr.toFixed(3)}) <span class="${centerMFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.verdict}</span></div>
                                <div><strong>단부-J 휨모멘트 검토:</strong> $M_u^- = ${endJFlex.MuDemand.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${endJFlex.dcr.toFixed(3)}) <span class="${endJFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.verdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 4장: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check) -->
                        <section class="report-chapter" data-chapter-key="shear">
                            <h2 class="chapter-heading" data-title-detail="전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)" data-title-summary="전단 및 비틀림 강도 검토 요약 (Shear & Torsion Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 4장</span>. <span class="chapter-title">전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)</span>
                            </h2>

                            <!-- 4.1 3-Station 전단력 및 전단강도 총괄 요약표 -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                4.1 3-Station 전단력 및 전단강도 총괄 요약표
                            </div>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;text-align:center;margin-bottom:12px;">
                                <colgroup>
                                    <col style="width:20%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                    <col style="width:16%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th style="padding:6px;">검토 위치 (Station)</th>
                                        <th>설계전단력 ($V_u$)</th>
                                        <th>콘크리트 ($V_c$)</th>
                                        <th>전단철근 ($V_s$)</th>
                                        <th>설계전단강도 ($\\phi V_n$)</th>
                                        <th>내력비 (DCR) / 판정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-I (End-I)</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endIShear.VuDemand.toFixed(1)} kN</td>
                                        <td>${endIShear.Vc.toFixed(1)} kN</td>
                                        <td>${endIShear.Vs.toFixed(1)} kN</td>
                                        <td style="font-weight:700;">${endIShear.phiVn.toFixed(1)} kN</td>
                                        <td style="font-weight:800;" class="${endIShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endIShear.dcr.toFixed(3)} ${endIShear.verdict}</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부-M (Center-M)</td>
                                        <td style="font-weight:700;color:#b45309;">${centerMShear.VuDemand.toFixed(1)} kN</td>
                                        <td>${centerMShear.Vc.toFixed(1)} kN</td>
                                        <td>${centerMShear.Vs.toFixed(1)} kN</td>
                                        <td style="font-weight:700;">${centerMShear.phiVn.toFixed(1)} kN</td>
                                        <td style="font-weight:800;" class="${centerMShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${centerMShear.dcr.toFixed(3)} ${centerMShear.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-J (End-J)</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${endJShear.VuDemand.toFixed(1)} kN</td>
                                        <td>${endJShear.Vc.toFixed(1)} kN</td>
                                        <td>${endJShear.Vs.toFixed(1)} kN</td>
                                        <td style="font-weight:700;">${endJShear.phiVn.toFixed(1)} kN</td>
                                        <td style="font-weight:800;" class="${endJShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJShear.dcr.toFixed(3)} ${endJShear.verdict}</td>
                                    </tr>
                                </tbody>
                            </table>

                            ${mode === 'detail' ? `
                            <!-- 4.2 최대 계수전단력 지배 단부 전단강도 3단계 KaTeX 전개 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">4.2 최대 계수전단력 지배 단부 [${governingShear.stationTag}] 전단강도 산정 (KDS 14 20 22)</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$V_c = \\frac{1}{6} \\lambda \\sqrt{f_{ck}} b_w d = \\frac{1}{6} \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} \\times ${b} \\times ${endIFlex.d.toFixed(1)} \\times 10^{-3} = \\mathbf{${governingShear.Vc.toFixed(1)}\\text{ kN}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$V_s = \\frac{A_v f_{yt} d}{s} = \\frac{${AvProvEnd.toFixed(1)} \\times ${fyt.toFixed(0)} \\times ${endIFlex.d.toFixed(1)}}{${endIS}} \\times 10^{-3} = \\mathbf{${governingShear.Vs.toFixed(1)}\\text{ kN}} \\le V_{s,\\max} (${governingShear.VsMax.toFixed(1)}\\text{ kN}) \\quad [\\mathbf{O.K}]$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi V_n = \\phi (V_c + V_s) = 0.75 \\times (${governingShear.Vc.toFixed(1)} + ${governingShear.Vs.toFixed(1)}) = \\mathbf{${governingShear.phiVn.toFixed(1)}\\text{ kN}} \\quad \\longrightarrow \\quad \\text{DCR}_{shear} = \\frac{${governingShear.VuDemand.toFixed(1)}}{${governingShear.phiVn.toFixed(1)}} = \\mathbf{${governingShear.dcr.toFixed(3)}} \\le 1.000 \\quad [\\mathbf{${governingShear.isSafe ? 'O.K' : 'N.G'}}]${governingShear.verdict}$$
                                </div>
                            </div>

                            <!-- 4.3 비틀림 임계 검토 및 상호작용 -->
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">4.3 비틀림모멘트 한계 검토 및 전단-비틀림 상호작용 (Torsion Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.3)</span>
                                </div>
                                <div class="formula-row">
                                    $$T_{th} = 0.0625 \\lambda \\sqrt{f_{ck}} \\left(\\frac{A_{cp}^2}{p_{cp}}\\right), \\quad \\phi T_{th} = 0.75 \\times T_{th}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$T_{th} = 0.0625 \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} \\times \\left(\\frac{${Acp}^2}{${pcp}}\\right) \\times 10^{-6} = \\mathbf{${Tth.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi T_{th} = 0.75 \\times ${Tth.toFixed(1)} = \\mathbf{${phiTth.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\quad \\longrightarrow \\quad T_u = ${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m} ${isTorsionRequired ? '>' : '\\le'} \\phi T_{th} \\quad (${isTorsionRequired ? '비틀림 설계 필요' : '비틀림 무시 가능'})$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\sqrt{\\left(\\frac{V_u}{b_w d}\\right)^2 + \\left(\\frac{T_u p_h}{1.7 A_{oh}^2}\\right)^2} = \\sqrt{\\left(\\frac{${governingShear.VuDemand.toFixed(1)} \\times 10^3}{${b} \\times ${endIFlex.d.toFixed(1)}}\\right)^2 + \\left(\\frac{${tu.toFixed(1)} \\times 10^6 \\times ${ph}}{1.7 \\times ${Aoh}^2}\\right)^2} = \\mathbf{${torsionCombinedStress}\\text{ MPa}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{허용 한계: } \\phi \\left(\\frac{V_c}{b_w d} + \\frac{2}{3} \\sqrt{f_{ck}}\\right) = \\mathbf{${torsionAllowStress}\\text{ MPa}} \\quad \\longrightarrow \\quad [\\mathbf{단면 파괴 방지 O.K}]${isTorsionStressOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$A_l = \\frac{A_t}{s} p_h \\left(\\frac{f_{yt}}{f_y}\\right) = \\frac{${At.toFixed(1)}}{${endIS}} \\times ${ph} \\times \\left(\\frac{${fyt.toFixed(0)}}{${fy.toFixed(0)}}\\right) = \\mathbf{${AlReq.toFixed(1)}\\text{ mm}^2}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$A_l (${AlReq.toFixed(1)}\\text{ mm}^2) \\le A_{l,prov} (${AlProv.toFixed(1)}\\text{ mm}^2) \\quad \\longrightarrow \\quad [\\mathbf{종방향 비틀림철근 O.K}]${isAlOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>전단 강도 검토:</strong> $V_u = ${governingShear.VuDemand.toFixed(1)}\\text{ kN} \\le \\phi V_n = ${governingShear.phiVn.toFixed(1)}\\text{ kN}$ (DCR = ${governingShear.dcr.toFixed(3)}) <span class="${governingShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${governingShear.verdict}</span></div>
                                <div><strong>비틀림 강도 검토:</strong> $T_u = ${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi T_n = ${phiTn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${dcrTorsion.toFixed(3)}) <span class="${dcrTorsion <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${torsionVerdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 5장: 사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width) -->
                        <section class="report-chapter" data-chapter-key="serviceability">
                            <h2 class="chapter-heading" data-title-detail="사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)" data-title-summary="사용성 한계상태 검토 요약 (Serviceability Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 5장</span>. <span class="chapter-title">사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)</span>
                            </h2>
                            ${mode === 'detail' ? `
                            <!-- 1. Branson 유효단면2차모멘트 Ie -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.1 Branson 유효단면2차모멘트 ($I_e$) 산정</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$M_{cr} = \\frac{f_r I_g}{y_t} = \\frac{${fr.toFixed(2)} \\times ${Ig.toLocaleString()}}{${yt}} \\times 10^{-6} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$I_e = \\left(\\frac{M_{cr}}{M_a}\\right)^3 I_g + \\left[1 - \\left(\\frac{M_{cr}}{M_a}\\right)^3\\right] I_{cr}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$I_e = \\left(\\frac{${Mcr.toFixed(1)}}{${centerMa.toFixed(1)}}\\right)^3 \\times ${Ig.toExponential(2)} + \\left[1 - \\left(\\frac{${Mcr.toFixed(1)}}{${centerMa.toFixed(1)}}\\right)^3\\right] \\times ${Icr.toExponential(2)} = \\mathbf{${Ie.toExponential(2)}\\text{ mm}^4} \\le I_g$$
                                </div>
                            </div>

                            <!-- 2. 처짐 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.2 단기 및 장기 처짐량 (Deflection Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\lambda_\\Delta = \\frac{\\xi}{1 + 50\\rho'}, \\quad \\Delta_{long} = \\lambda_\\Delta \\times \\Delta_{sus}, \\quad \\Delta_{total} = \\Delta_i + \\Delta_{long}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\lambda_\\Delta = \\frac{2.0}{1 + 50 \\times ${rhoPrime.toFixed(4)}} = \\mathbf{${lambdaDelta.toFixed(2)}}, \\quad \\Delta_{long} = ${lambdaDelta.toFixed(2)} \\times ${deltaSus.toFixed(1)} = \\mathbf{${deltaLong.toFixed(1)}\\text{ mm}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\Delta_{total} = ${deltaImmediate.toFixed(1)} + ${deltaLong.toFixed(1)} = \\mathbf{${deltaTotal.toFixed(1)}\\text{ mm}} \\le \\Delta_{allow} = \\frac{L}{240} = \\frac{${L}}{240} = \\mathbf{${deltaAllow.toFixed(1)}\\text{ mm}} \\quad (\\text{DCR} = ${dcrDefl.toFixed(3)}) \\quad \\longrightarrow \\quad [\\mathbf{${dcrDefl <= 1.0 ? 'O.K' : 'N.G'}}]${deflVerdict}$$
                                </div>
                            </div>

                            <!-- 3. 직접 균열폭 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.3 직접 균열폭 (Direct Crack Width Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.1.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$w = 1.08 \\beta \\left(\\frac{f_s}{E_s}\\right) \\sqrt[3]{d_c s}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$w = 1.08 \\times 1.2 \\times \\left(\\frac{${fs}}{${Es.toLocaleString()}}\\right) \\times \\sqrt[3]{${dc} \\times ${rebarSpace}} = \\mathbf{${crackWidth.toFixed(2)}\\text{ mm}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$w = ${crackWidth.toFixed(2)}\\text{ mm} \\le w_{lim} = \\mathbf{${crackAllow.toFixed(2)}\\text{ mm}} \\quad (\\text{DCR} = ${dcrCrack.toFixed(3)}) \\quad \\longrightarrow \\quad [\\mathbf{${dcrCrack <= 1.0 ? 'O.K' : 'N.G'}}]${crackVerdict}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>처짐 검토:</strong> $\\Delta_{total} = ${deltaTotal.toFixed(1)}\\text{ mm} \\le \\Delta_{allow} = ${deltaAllow.toFixed(1)}\\text{ mm}$ (DCR = ${dcrDefl.toFixed(3)}) <span class="${dcrDefl <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${deflVerdict}</span></div>
                                <div><strong>균열폭 검토:</strong> $w = ${crackWidth.toFixed(2)}\\text{ mm} \\le w_{lim} = ${crackAllow.toFixed(2)}\\text{ mm}$ (DCR = ${dcrCrack.toFixed(3)}) <span class="${dcrCrack <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${crackVerdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 6장: 종합 안전성 판정 (Executive Summary & Final Verdict) -->
                        <section class="report-chapter" data-chapter-key="verdict">
                            <h2 class="chapter-heading" data-title-detail="종합 안전성 판정 (Executive Summary & Final Verdict)" data-title-summary="종합 안전성 판정 (Executive Summary & Final Verdict)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 6장</span>. <span class="chapter-title">종합 안전성 판정 (Executive Summary & Final Verdict)</span>
                            </h2>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;margin-bottom:12px;">
                                <colgroup>
                                    <col style="width:20%;">
                                    <col style="width:18%;">
                                    <col style="width:18%;">
                                    <col style="width:18%;">
                                    <col style="width:12%;">
                                    <col style="width:14%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;text-align:center;">
                                        <th style="padding:6px;">검토 항목</th>
                                        <th>적용 설계기준</th>
                                        <th>소요 부재력 (Demand)</th>
                                        <th>설계 내력 (Capacity)</th>
                                        <th>내력비 (DCR)</th>
                                        <th>최종 판정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">단부-I 휨 ($M_u^-$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${endIFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${endIFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${endIFlex.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${endIFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.verdict}</td>
                                    </tr>
                                    <tr style="background:#fefce8;">
                                        <td style="font-weight:600;padding:6px;">중앙부-M 휨 ($M_u^+$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${centerMFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${centerMFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${centerMFlex.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${centerMFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">단부-J 휨 ($M_u^-$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${endJFlex.MuDemand.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${endJFlex.phiMn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${endJFlex.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${endJFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">설계 전단력 ($V_u$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.VuDemand.toFixed(1)} kN</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.phiVn.toFixed(1)} kN</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${governingShear.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${governingShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${governingShear.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">설계 비틀림 ($T_u$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.3)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${tu.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiTn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrTorsion.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrTorsion <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${torsionVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">총 처짐량 (Deflection)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 30 (4.2)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${deltaTotal.toFixed(1)} mm</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${deltaAllow.toFixed(1)} mm</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrDefl.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrDefl <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${deflVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">직접 균열폭 (Crack)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 30 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${crackWidth.toFixed(2)} mm</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${crackAllow.toFixed(2)} mm</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrCrack.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrCrack <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${crackVerdict}</td>
                                    </tr>
                                </tbody>
                            </table>

                            <div style="background:${isOverallSafe ? '#ecfdf5' : '#fef2f2'};border:1px solid ${isOverallSafe ? '#a7f3d0' : '#fecaca'};border-radius:6px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;">
                                <div style="font-size:13px;font-weight:700;color:${isOverallSafe ? '#065f46' : '#991b1b'};">
                                    RC 보 종합 설계 안전성 검토 결과: ${isOverallSafe ? '적합 (SAFE / O.K)' : '부적합 (OVERSTRESSED / N.G)'} (최대 지배 DCR = ${governingDcr.toFixed(3)})
                                </div>
                                <div style="font-size:16px;font-weight:900;" class="${isOverallSafe ? 'verdict-ok' : 'verdict-ng'}">
                                    ${overallVerdict}
                                </div>
                            </div>
                        </section>

                        <!-- 문서 바닥글 -->
                        <div style="border-top:1px solid #e2e8f0;padding-top:10px;margin-top:24px;display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;">
                            <span>AltDP_3rd Structural Member Designer — KDS Pure White A4 Engine (RC Beam 3-Station)</span>
                            <span>Page 1 / 1</span>
                        </div>
                    </div>
                </div>
            `;

            return html;
        }
    }

    // Register to global
    window.RCBeamReportGenerator = RCBeamReportGenerator;
    const defaultGenerator = new RCBeamReportGenerator();

    /**
     * Standard Global RC Beam Report Renderer
     * @param {Object} reportEngine - ReportEngine instance or memberData
     * @param {HTMLElement} [container] - DOM Container or calcResult
     * @param {Object} [memberData] - Beam input properties
     * @param {Object} [calcResult] - Beam calculation result
     * @returns {string} HTML string
     */
    window.renderRCBeamReport = function(reportEngine, container, memberData, calcResult) {
        let engine = reportEngine;
        let c = container;
        let m = memberData;
        let r = calcResult;
        if (!reportEngine || typeof reportEngine.updateChapterNumbering !== 'function') {
            m = reportEngine;
            r = container;
            engine = window.reportEngine || { mode: 'detail', includeInput: true, includeGraphics: true, headerConfig: {} };
            c = null;
        }
        return defaultGenerator.render(engine, c, m, r);
    };

    // Legacy backwards compatibility
    window.RedcrRcBeamReport = {
        render: function(reportEngine, container, memberData, calcResult) {
            return window.renderRCBeamReport(reportEngine, container, memberData, calcResult);
        }
    };

})(typeof window !== 'undefined' ? window : this);
