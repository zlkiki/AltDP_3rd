/**
 * AltDP_3rd RC Beam Pure White A4 7-Chapter 8-Step KaTeX Structural Calculation Report
 * Conforms to Requirement 22-4, 22-4-1-2, 22-4-1-4, 22-5-3 & DOCS 07 & DOCS 14 Specifications
 * - Standard Class: RCBeamReportGenerator
 * - Global Function: window.renderRCBeamReport(reportEngine, container, memberData, calcResult)
 * - Chapter 1: 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry) - 단면 치수, 재료 강도, 2D 횡단면 배근 상세도
 * - Appendix 1: 사용자 입력 데이터 상세 (User Input Data Specification) - 선택 토글
 * - Chapter 2: 설계 부재력 및 하중조합 (Design Factored Loads & Combinations) - 지배 LCB 및 3-Station 부재력
 * - Chapter 3: 단면 연성 및 최소철근량 검토 (Ductility Limit & Minimum Reinforcement Check) [★신설] - KDS 14 20 20: 2022
 * - Chapter 4: 휨모멘트 강도 검토 (Flexural Strength Check) - 3-Station 4단계 강도 검토 (0하중 동적 생략)
 * - Chapter 5: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check) - 3-Station 전단 & 비틀림 (0하중 동적 생략)
 * - Chapter 6: 사용성 한계상태 검토 (Serviceability Check) - Branson Ie 가중평균, 처짐, 3-Station 균열 s_max, 직접 균열폭
 * - Chapter 7: 종합 안전성 판정 (Executive Summary & Final Verdict) - 전 항목 DCR 전수 표기 및 최종 판정
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
            const solveFlexure = (stationTag, AsTens, AsComp, MuDemand, isNegativeBending, stationRes = null) => {
                const isFlangeComp = (!isNegativeBending) && isTBeam && (bf > b);
                const bComp = isFlangeComp ? bf : b;

                // 유효깊이 산정
                const dEst = Number((isNegativeBending ? (h - coverTop - 10 - 25 / 2) : (h - cover - 10 - 25 / 2)).toFixed(1));
                const dtEst = dEst;
                const dPrimeEst = Number((isNegativeBending ? (cover + 10 + 22 / 2) : (coverTop + 10 + 22 / 2)).toFixed(1));

                let d = Number(stationRes?.d ?? dEst);
                let dt = Number(stationRes?.dt ?? dtEst);
                let dPrime = Number(stationRes?.d_prime ?? dPrimeEst);

                let a = Number(stationRes?.a ?? 0);
                let c = Number(stationRes?.c ?? 0);
                if (!a || !c) {
                    const T = AsTens * fy;
                    const Cs = AsComp * fy;
                    a = Number(((T - Cs) / (alpha1 * fck * bComp)).toFixed(1));
                    if (a <= 0) a = Number((T / (alpha1 * fck * bComp)).toFixed(1));
                    c = Number((a / beta1).toFixed(1));
                }

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
                const dcrMin = Number((phiMn > 0 ? (phiMnMin / phiMn) : 9.999).toFixed(3));
                const isDuctilityOk = (epsT >= epsTMin) && ((c / dt) <= cDtLimit);
                const dcrEps = Number((epsT > 0 ? (epsTMin / epsT) : 9.999).toFixed(3));

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
                    dcrMin,
                    isDuctilityOk,
                    dcrEps,
                    verdict: isSafe ? '  →  O.K' : '  →  N.G',
                    minVerdict: isMinOk ? '  →  O.K' : '  →  N.G',
                    ductilityVerdict: isDuctilityOk ? '  →  O.K' : '  →  N.G'
                };
            };

            // 3개 위치별 계산 인스턴스 생성
            const endIFlex = solveFlexure('End-I (단부-I)', endITop.totalArea, endIBot.totalArea, endIMuNeg, true, r.end_i?.neg_flexure || r);
            const centerMFlex = solveFlexure('Center-M (중앙부-M)', centerBot.totalArea, centerTop.totalArea, centerMuPos, false, r.center_m?.pos_flexure || r);
            const endJFlex = solveFlexure('End-J (단부-J)', endJTop.totalArea, endJBot.totalArea, endJMuNeg, true, r.end_j?.neg_flexure || (arrangeType !== 'THREE_STATIONS' ? endIFlex : r));

            // =========================================================================
            // 3. 3-Station 위치별 전단강도 및 최소 전단철근 산정 엔진 (KDS 14 20 22)
            // =========================================================================
            const solveShear = (stationTag, VuDemand, Av, sSpacing, dVal, shearRes = null) => {
                const Vc = Number(shearRes?.Vc ?? (1.0 / 6.0 * 1.0 * Math.sqrt(fck) * b * dVal * 1e-3).toFixed(1));
                const Vs = Number(shearRes?.Vs ?? (Av * fyt * dVal / sSpacing * 1e-3).toFixed(1));
                const VsMax = Number(shearRes?.Vs_max ?? (2.0 / 3.0 * Math.sqrt(fck) * b * dVal * 1e-3).toFixed(1));
                const phiShear = 0.75;
                const phiVn = Number(shearRes?.phi_Vn ?? (phiShear * (Vc + Vs)).toFixed(1));
                const dcr = Number((phiVn > 0 ? (VuDemand / phiVn) : 0.0).toFixed(3));
                const isSafe = (VuDemand <= 0) || (dcr <= 1.0);

                // 최소 전단철근량 Av_min (KDS 14 20 22 식 4.3-1)
                const AvMinCalc = Math.max(0.0625 * Math.sqrt(fck) * (b * sSpacing) / fyt, 0.35 * (b * sSpacing) / fyt);
                const AvMin = Number(shearRes?.Av_min ?? AvMinCalc.toFixed(1));
                const dcrAvMin = Number(shearRes?.dcr_Av_min ?? (Av > 0 ? (AvMin / Av) : 9.999).toFixed(3));

                // 최대 전단철근 배근간격 s_max (KDS 14 20 22 4.3.4)
                let sMaxEst = Math.min(dVal / 2.0, 600.0);
                if (VuDemand > 0 && Vs > (1.0 / 3.0 * Math.sqrt(fck) * b * dVal * 1e-3)) {
                    sMaxEst = Math.min(dVal / 4.0, 300.0);
                }
                const sMax = Number(shearRes?.s_max ?? sMaxEst.toFixed(1));
                const dcrSpacing = Number(shearRes?.dcr_spacing ?? (sMax > 0 ? (sSpacing / sMax) : 9.999).toFixed(3));

                const isMinShearOk = Boolean(shearRes?.is_min_shear_ok ?? ((Av >= AvMin - 1e-4) && (sSpacing <= sMax * 1.001)));
                const isSpacingOk = sSpacing <= sMax * 1.001;

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
                    AvMin,
                    AvProv: Av,
                    sSpacing,
                    sMax,
                    dcrAvMin,
                    dcrSpacing,
                    isMinShearOk,
                    isSpacingOk,
                    verdict: isSafe ? '  →  O.K' : '  →  N.G',
                    minVerdict: isMinShearOk ? '  →  O.K' : '  →  N.G',
                    spacingVerdict: isSpacingOk ? '  →  O.K' : '  →  N.G'
                };
            };

            const endIShear = solveShear('End-I (단부-I)', endIVu, AvProvEnd, endIS, endIFlex.d, r.end_i?.shear || r);
            const centerMShear = solveShear('Center-M (중앙부-M)', centerVu, AvProvCenter, centerS, centerMFlex.d, r.center_m?.shear || r);
            const endJShear = solveShear('End-J (단부-J)', endJVu, AvProvEnd, endJS, endJFlex.d, r.end_j?.shear || (arrangeType !== 'THREE_STATIONS' ? endIShear : r));

            const governingShear = (endIShear.VuDemand >= endJShear.VuDemand) ? endIShear : endJShear;

            // =========================================================================
            // 4. 비틀림 및 최소 비틀림철근 산정 (KDS 14 20 22 제4.3 & 4.5절)
            // =========================================================================
            const Acp = b * h;
            const pcp = 2 * (b + h);
            const Tth = Number((r.Tth ?? (0.0625 * 1.0 * Math.sqrt(fck) * (Math.pow(Acp, 2) / pcp) * 1e-6)).toFixed(1));
            const phiTth = Number((0.75 * Tth).toFixed(1));
            const tu = Math.max(endITu, centerTu, endJTu);
            const isZeroTorsion = (tu <= 0.0);
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
            const vuStress = (governingShear.VuDemand * 1e3) / (b * (governingShear.dVal || endIFlex.d));
            const tuStress = (tu * 1e6 * ph) / (1.7 * Math.pow(Aoh, 2));
            const torsionCombinedStress = Number(Math.sqrt(Math.pow(vuStress, 2) + Math.pow(tuStress, 2)).toFixed(2));
            const torsionAllowStress = Number((0.75 * ((governingShear.Vc * 1e3) / (b * endIFlex.d) + (2.0 / 3.0) * Math.sqrt(fck))).toFixed(2));
            const dcrTorsionStress = Number((torsionAllowStress > 0 ? (torsionCombinedStress / torsionAllowStress) : 0.5).toFixed(3));
            const isTorsionStressOk = torsionCombinedStress <= torsionAllowStress;

            // KDS 14 20 22 4.5.4 최소 비틀림 철근량 및 간격 산정
            const Av2AtMin = Number((r.torsion?.Av_2At_min ?? Math.max(0.0625 * Math.sqrt(fck) * (b * endIS) / fyt, 0.35 * (b * endIS) / fyt)).toFixed(1));
            const sMaxTorsion = Number((r.torsion?.s_max_torsion ?? Math.min(ph / 8.0, 300.0)).toFixed(1));
            const isTorsionStirrupOk = (AvProvEnd >= Av2AtMin - 1e-4) && (endIS <= sMaxTorsion * 1.001);

            const AlCalc = Number((r.torsion?.Al_calc ?? (At / endIS * ph * (fyt / fy))).toFixed(1));
            const atOverSForMin = Math.max(At / endIS, 0.175 * b / fyt);
            const AlMin = Number((r.torsion?.Al_min ?? Math.max((0.42 * Math.sqrt(fck) * Acp / fy) - (atOverSForMin * ph * (fyt / fy)), 0.0)).toFixed(1));
            const AlReq = Number((r.torsion?.Al_req ?? Math.max(AlCalc, AlMin)).toFixed(1));

            const sideRebarCount = Number(m.rebar?.torsion_side_count || 4);
            const sideRebarDia = m.rebar?.torsion_side_bar || 'D13';
            const AlProv = Number((sideRebarCount * (REBAR_AREAS[sideRebarDia] || 126.7)).toFixed(1));
            const dcrAl = Number((r.torsion?.dcr_Al ?? (AlProv > 0 ? (AlReq / AlProv) : 9.999)).toFixed(3));
            const isAlOk = AlProv >= AlReq;

            // =========================================================================
            // 5. 사용성 한계상태 검토 수치 (KDS 14 20 30) - Branson Ie 가중평균 & 3-Station 균열
            // =========================================================================
            const calcCrackedSection = (bSec, hSec, dSec, dpSec, AsTens, AsComp) => {
                const nMod = 200000.0 / Ec;
                const Akd = 0.5 * bSec;
                const Bkd = nMod * AsTens + Math.max(0.0, (nMod - 1.0) * AsComp);
                const Ckd = -(nMod * AsTens * dSec + Math.max(0.0, (nMod - 1.0) * AsComp * dpSec));
                const disc = Math.max(0.0, Math.pow(Bkd, 2) - 4.0 * Akd * Ckd);
                const kdVal = Number(((-Bkd + Math.sqrt(disc)) / (2.0 * Akd)).toFixed(1));
                let IcrVal = (bSec * Math.pow(kdVal, 3)) / 3.0 + nMod * AsTens * Math.pow(dSec - kdVal, 2);
                if (AsComp > 0 && kdVal > dpSec) {
                    IcrVal += (nMod - 1.0) * AsComp * Math.pow(kdVal - dpSec, 2);
                }
                return { kd: kdVal, Icr: Math.round(IcrVal) };
            };

            // 1) 중앙부-M 균열단면
            const crM = calcCrackedSection(b, h, centerMFlex.d, centerMFlex.dPrime, centerBot.totalArea, centerTop.totalArea);
            const IcrM = Number((r.serviceability?.I_cr ? r.serviceability.I_cr * 1e4 : crM.Icr).toFixed(0));
            const mcrRatioM = Math.min(1.0, Mcr / Math.max(centerMa, 1.0));
            const mcr3M = Math.pow(mcrRatioM, 3);
            const IeM = Number((r.serviceability?.Ie_mid ? r.serviceability.Ie_mid * 1e4 : (mcr3M * Ig + (1.0 - mcr3M) * IcrM)).toFixed(0));

            // 2) 단부-I 균열단면
            const crI = calcCrackedSection(b, h, endIFlex.d, endIFlex.dPrime, endITop.totalArea, endIBot.totalArea);
            const IcrI = crI.Icr;
            const endIMa = Number(endILoads.Ma || Math.max(endIMuNeg * 0.65, 80.0));
            const mcrRatioI = Math.min(1.0, Mcr / Math.max(endIMa, 1.0));
            const mcr3I = Math.pow(mcrRatioI, 3);
            const IeI = Number((r.serviceability?.Ie_end_i ? r.serviceability.Ie_end_i * 1e4 : (mcr3I * Ig + (1.0 - mcr3I) * IcrI)).toFixed(0));

            // 3) 단부-J 균열단면
            const crJ = (arrangeType === 'THREE_STATIONS')
                ? calcCrackedSection(b, h, endJFlex.d, endJFlex.dPrime, endJTop.totalArea, endJBot.totalArea)
                : crI;
            const IcrJ = crJ.Icr;
            const endJMa = Number(endJLoads.Ma || (arrangeType === 'THREE_STATIONS' ? Math.max(endJMuNeg * 0.65, 80.0) : endIMa));
            const mcrRatioJ = Math.min(1.0, Mcr / Math.max(endJMa, 1.0));
            const mcr3J = Math.pow(mcrRatioJ, 3);
            const IeJ = Number((r.serviceability?.Ie_end_j ? r.serviceability.Ie_end_j * 1e4 : (mcr3J * Ig + (1.0 - mcr3J) * IcrJ)).toFixed(0));

            // 지점조건 및 가중평균 Ie (KDS 14 20 30 제4.2.1절)
            const supportCond = m.support || m.section?.support || 'CONTINUOUS_BOTH';
            let IeAvg = IeM;
            let supportCondText = '양단 연속보 (Both Ends Continuous)';
            let IeFormulaText = '0.70 I_{e,m} + 0.15(I_{e,i} + I_{e,j})';
            if (supportCond === 'SIMPLE') {
                IeAvg = IeM;
                supportCondText = '단순 지지보 (Simply Supported)';
                IeFormulaText = 'I_{e,m}';
            } else if (supportCond === 'CONTINUOUS_ONE') {
                const IeCont = Math.max(IeI, IeJ);
                IeAvg = Number((0.85 * IeM + 0.15 * IeCont).toFixed(0));
                supportCondText = '1단 연속보 (One End Continuous)';
                IeFormulaText = '0.85 I_{e,m} + 0.15 I_{e,cont}';
            } else if (supportCond === 'CANTILEVER') {
                IeAvg = IeI;
                supportCondText = '캔틸레버보 (Cantilever)';
                IeFormulaText = 'I_{e,i}';
            } else {
                IeAvg = Number((0.70 * IeM + 0.15 * (IeI + IeJ)).toFixed(0));
            }
            if (r.serviceability?.Ie_avg && r.serviceability.Ie_avg > 0) {
                IeAvg = Number((r.serviceability.Ie_avg * 1e4).toFixed(0));
            }

            // 처짐량 계산
            const deltaImmediate = Number((r.serviceability?.delta_immediate ?? r.delta_elastic ?? r.delta_immediate ?? 6.2).toFixed(1));
            const rhoPrime = centerTop.totalArea / (b * centerMFlex.d);
            const lambdaDelta = Number((r.serviceability?.lambda_delta ?? (2.0 / (1.0 + 50.0 * rhoPrime))).toFixed(2));
            const deltaSus = 3.8;
            const deltaLong = Number((r.serviceability?.delta_long_term ?? r.delta_long ?? (lambdaDelta * deltaSus)).toFixed(1));
            const deltaTotal = Number((r.serviceability?.delta_total ?? r.delta_total ?? (deltaImmediate + deltaLong)).toFixed(1));
            const deltaAllow = Number((r.serviceability?.delta_allow ?? r.delta_allowable ?? (L / 240.0)).toFixed(1));
            const dcrDefl = Number((r.serviceability?.dcr_defl ?? r.deflection_dcr ?? (deltaTotal / deltaAllow)).toFixed(3));
            const deflVerdict = dcrDefl <= 1.0 ? '  →  O.K' : '  →  N.G';

            // KDS 14 20 30 제4.2.3절 3-Station 균열방지 철근간격 제한 (s <= s_max)
            const calcStationCrackSpacing = (stationTag, rebarPos, bSec, dSec, kdSec, AsTens, MaDemand, ccVal, stirrupD, l1Count, l1Dia, isZero) => {
                const jdSec = Number((dSec - kdSec / 3.0).toFixed(1));
                let fs = 0.0;
                if (isZero || MaDemand <= 0.0) {
                    fs = Number((0.60 * fy).toFixed(1));
                } else {
                    fs = Number(Math.min((Math.abs(MaDemand) * 1e6) / (AsTens * jdSec), 0.60 * fy).toFixed(1));
                    if (fs <= 0) fs = Number((0.60 * fy).toFixed(1));
                }
                const kcr = 210.0;
                const sMaxCalculated = Number((375.0 * (kcr / fs) - 2.5 * ccVal).toFixed(1));
                const sMaxUpper = Number((300.0 * (kcr / fs)).toFixed(1));
                const sMax = Number(Math.min(sMaxCalculated, sMaxUpper).toFixed(1));

                const dbNum = parseInt(l1Dia.replace('D', ''), 10) || 25;
                const nBars = Math.max(l1Count, 2);
                const sActual = Number(((bSec - 2 * ccVal - 2 * stirrupD - dbNum) / (nBars - 1)).toFixed(1));
                const dcr = Number((sActual / sMax).toFixed(3));
                const isOk = sActual <= sMax;
                return {
                    stationTag,
                    rebarPos,
                    cc: ccVal,
                    kd: kdSec,
                    jd: jdSec,
                    fs,
                    kcr,
                    sMaxCalculated,
                    sMaxUpper,
                    sMax,
                    sActual,
                    dcr,
                    isOk,
                    verdict: isOk ? '  →  O.K' : '  →  N.G'
                };
            };

            const crackI = calcStationCrackSpacing(
                'End-I (단부-I)', '상부 인장철근 (Top Tension)',
                b, endIFlex.d, crI.kd, endITop.totalArea, endIMa, coverTop, stirrupDiaNum, endITop.l1.count, endITop.l1.dia, (endIMuNeg <= 0)
            );
            const crackM = calcStationCrackSpacing(
                'Center-M (중앙부-M)', '하부 인장철근 (Bottom Tension)',
                b, centerMFlex.d, crM.kd, centerBot.totalArea, centerMa, cover, stirrupDiaNum, centerBot.l1.count, centerBot.l1.dia, (centerMuPos <= 0)
            );
            const crackJ = (arrangeType === 'THREE_STATIONS')
                ? calcStationCrackSpacing('End-J (단부-J)', '상부 인장철근 (Top Tension)', b, endJFlex.d, crJ.kd, endJTop.totalArea, endJMa, coverTop, stirrupDiaNum, endJTop.l1.count, endJTop.l1.dia, (endJMuNeg <= 0))
                : crackI;

            // 직접 균열폭 검토
            const fsDirect = Number((0.6 * fy).toFixed(0));
            const Es = 200000;
            const dc = cover;
            const crackWidth = Number((r.serviceability?.crack_width ?? r.crack_width ?? 0.22).toFixed(2));
            const crackAllow = Number((r.serviceability?.crack_allow ?? r.crack_allowable ?? 0.30).toFixed(2));
            const dcrCrack = Number((r.serviceability?.dcr_crack ?? r.crack_dcr ?? (crackWidth / crackAllow)).toFixed(3));
            const crackVerdict = dcrCrack <= 1.0 ? '  →  O.K' : '  →  N.G';

            // =========================================================================
            // 6. 종합 안전성 판정 (Executive Summary & Final Verdict)
            // =========================================================================
            const governingDcr = Number(Math.max(
                endIFlex.dcr, centerMFlex.dcr, endJFlex.dcr,
                endIFlex.dcrMin, centerMFlex.dcrMin, endJFlex.dcrMin,
                endIFlex.dcrEps, centerMFlex.dcrEps, endJFlex.dcrEps,
                endIShear.dcr, centerMShear.dcr, endJShear.dcr,
                governingShear.dcrAvMin, governingShear.dcrSpacing,
                (isZeroTorsion ? 0.0 : dcrTorsion),
                (isTorsionRequired ? dcrAl : 0.0),
                dcrDefl,
                crackI.dcr, crackM.dcr, crackJ.dcr,
                dcrCrack
            ).toFixed(3));
            const isOverallSafe = governingDcr <= 1.0;
            const overallVerdict = isOverallSafe ? '  →  O.K' : '  →  N.G';

            // 그래픽 렌더링 헬퍼
            const graphicContent = (engine._generateSectionGraphic && typeof engine._generateSectionGraphic === 'function')
                ? engine._generateSectionGraphic(m, r, 'rc_beam')
                : '';

            // =========================================================================
            // 7. HTML 조립 시작 (A4 Sheet 7-Chapter Template)
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

                            <!-- 2D 단면 배근 상세 그래픽 임베딩 -->
                            <div class="report-svg-slot report-graphic-slot" style="${includeGraphics ? 'width:100%;text-align:center;margin-top:4px;' : 'display:none;'}">
                                ${graphicContent}
                                <div style="font-size:10.5px;color:#64748b;margin-top:5px;font-weight:500;">
                                    [RC 보 3-Station 횡단면 배근 상세도: End-I (${b}×${h}) / Center-M (${b}×${h}) / End-J (${b}×${h}) mm]
                                </div>
                            </div>
                        </section>

                        <!-- 부록 1: 사용자 입력 데이터 상세 표 (체크박스 토글 옵션) -->
                        <section class="report-appendix user-input-section" data-chapter-key="input" style="${includeInput ? '' : 'display:none;'}">
                            <h2 class="appendix-heading" style="font-size:14px;color:#1a3a5c;background:#f1f5f9;padding:6px 12px;border-left:4px solid #64748b;margin:16px 0 10px;font-weight:700;">
                                <span class="appendix-num">부록 1</span>. <span class="appendix-title">사용자 입력 데이터 상세 (User Input Data Specification)</span>
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

                        <!-- 제 3장: 단면 연성 및 최소철근량 검토 (Ductility Limit & Minimum Reinforcement Check) [★신설] -->
                        <section class="report-chapter" data-chapter-key="ductility">
                            <h2 class="chapter-heading" data-title-detail="단면 연성 및 최소철근량 검토 (Ductility Limit & Minimum Reinforcement Check)" data-title-summary="단면 연성 및 최소철근량 검토 요약 (Ductility & Min Rebar Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 3장</span>. <span class="chapter-title">단면 연성 및 최소철근량 검토 (Ductility Limit & Minimum Reinforcement Check)</span>
                            </h2>

                            <!-- 3.1 3-Station 연성 및 최소철근량 총괄 요약표 -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                3.1 3-Station 연성 및 최소철근량 검토 총괄 요약표 (KDS 14 20 20)
                            </div>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;text-align:center;margin-bottom:12px;">
                                <colgroup>
                                    <col style="width:16%;">
                                    <col style="width:20%;">
                                    <col style="width:18%;">
                                    <col style="width:14%;">
                                    <col style="width:18%;">
                                    <col style="width:14%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th style="padding:6px;">검토 위치 (Station)</th>
                                        <th>지배 모멘트 / 인장철근</th>
                                        <th>중립축 및 변형률 ($c, \\epsilon_t$)</th>
                                        <th>순인장변형률 DCR</th>
                                        <th>최소 휨강도 ($\\phi M_n \\ge 1.2 M_{cr}$)</th>
                                        <th>최소철근량 DCR</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-I (End-I)</td>
                                        <td>부모멘트 ($M_u^-$)<br><span style="font-size:10px;color:#64748b;">상부: ${endITop.text}</span></td>
                                        <td>$c = ${endIFlex.c.toFixed(1)}$ mm<br>$\\epsilon_t = ${endIFlex.epsT.toFixed(4)}$</td>
                                        <td style="font-weight:700;" class="${endIFlex.isDuctilityOk ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.dcrEps.toFixed(3)} ${endIFlex.ductilityVerdict}</td>
                                        <td>${endIFlex.phiMn.toFixed(1)} kN·m $\\ge$ ${phiMnMin.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;" class="${endIFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.dcrMin.toFixed(3)} ${endIFlex.minVerdict}</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부-M (Center-M)</td>
                                        <td>정모멘트 ($M_u^+$)<br><span style="font-size:10px;color:#64748b;">하부: ${centerBot.text}</span></td>
                                        <td>$c = ${centerMFlex.c.toFixed(1)}$ mm<br>$\\epsilon_t = ${centerMFlex.epsT.toFixed(4)}$</td>
                                        <td style="font-weight:700;" class="${centerMFlex.isDuctilityOk ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.dcrEps.toFixed(3)} ${centerMFlex.ductilityVerdict}</td>
                                        <td>${centerMFlex.phiMn.toFixed(1)} kN·m $\\ge$ ${phiMnMin.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;" class="${centerMFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.dcrMin.toFixed(3)} ${centerMFlex.minVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-J (End-J)</td>
                                        <td>부모멘트 ($M_u^-$)<br><span style="font-size:10px;color:#64748b;">상부: ${endJTop.text}</span></td>
                                        <td>$c = ${endJFlex.c.toFixed(1)}$ mm<br>$\\epsilon_t = ${endJFlex.epsT.toFixed(4)}$</td>
                                        <td style="font-weight:700;" class="${endJFlex.isDuctilityOk ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.dcrEps.toFixed(3)} ${endJFlex.ductilityVerdict}</td>
                                        <td>${endJFlex.phiMn.toFixed(1)} kN·m $\\ge$ ${phiMnMin.toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;" class="${endJFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.dcrMin.toFixed(3)} ${endJFlex.minVerdict}</td>
                                    </tr>
                                </tbody>
                            </table>

                            ${mode === 'detail' ? `
                            <!-- 최소철근량 만족 검토 및 연성파괴 유도 기준 상세 KaTeX 전개 -->
                            ${arrangeType === 'ONE_SECTION' ? `
                            <!-- 3.2 중앙부 (Center-M) 전단면 동일 최소철근량 및 연성 검토 -->
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">3.2 중앙부 (Center-M) 최소철근량 만족 및 연성파괴 유도 순인장변형률 검토 [전단면 동일 배근, 하부 인장]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1 & 4.2.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\phi M_n \\ge 1.2 M_{cr} \\quad \\left(\\text{단, } A_s \\ge \\frac{4}{3} A_{s,req} \\text{ 만족 시 적용 예외}\\right)$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\begin{aligned}
                                    f_r &= 0.63 \\lambda \\sqrt{f_{ck}} = 0.63 \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} = \\mathbf{${fr.toFixed(2)}\\text{ MPa}} \\\\
                                    I_g &= \\frac{b_w h^3}{12} = \\frac{${b} \\times ${h}^3}{12} = \\mathbf{${Ig.toLocaleString()}\\text{ mm}^4}, \\quad M_{cr} = \\frac{f_r I_g}{y_t} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_n = \\mathbf{${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\ge 1.2 M_{cr} (${phiMnMin.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\quad (\\text{DCR} = ${centerMFlex.dcrMin.toFixed(3)}) \\quad \\rightarrow \\quad ${centerMFlex.isMinOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    $$\\epsilon_t \\ge \\epsilon_{t,\\min} = \\begin{cases} 0.0040 & (f_y \\le 400\\text{ MPa}) \\\\ 2.0\\,\\epsilon_y & (f_y > 400\\text{ MPa}) \\end{cases}, \\quad \\epsilon_t = \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right), \\quad \\frac{c}{d_t} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} = \\frac{\\epsilon_{cu}}{\\epsilon_{cu} + \\epsilon_{t,\\min}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\begin{aligned}
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${centerMFlex.dt.toFixed(1)} - ${centerMFlex.c.toFixed(1)}}{${centerMFlex.c.toFixed(1)}}\\right) = \\mathbf{${centerMFlex.epsT.toFixed(4)}} \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}) \\\\
                                    \\frac{c}{d_t} &= \\frac{${centerMFlex.c.toFixed(1)}}{${centerMFlex.dt.toFixed(1)}} = \\mathbf{${(centerMFlex.c / centerMFlex.dt).toFixed(3)}} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)})
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{\\epsilon_t} = \\frac{\\epsilon_{t,\\min}}{\\epsilon_t} = \\mathbf{${centerMFlex.dcrEps.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${centerMFlex.isDuctilityOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                            </div>
                            ` : `
                            <!-- 3.2 단부-I (End-I) 최소철근량 및 연성 검토 (부모멘트, 상부인장) -->
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">3.2 단부-I (End-I) 최소철근량 만족 및 연성파괴 유도 순인장변형률 검토 [부모멘트 작용, 상부 인장철근 $A_s = ${endITop.totalArea.toFixed(1)}$ mm²]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1 & 4.2.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\phi M_n \\ge 1.2 M_{cr} \\quad \\left(f_r = 0.63 \\lambda \\sqrt{f_{ck}} = \\mathbf{${fr.toFixed(2)}\\text{ MPa}}, \\quad I_g = \\frac{b_w h^3}{12} = \\mathbf{${Ig.toLocaleString()}\\text{ mm}^4}, \\quad M_{cr} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}\\right)$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_{n,I} = \\mathbf{${endIFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\ge 1.2 M_{cr} (${phiMnMin.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\quad (\\text{DCR} = ${endIFlex.dcrMin.toFixed(3)}) \\quad \\rightarrow \\quad ${endIFlex.isMinOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    $$\\epsilon_t \\ge \\epsilon_{t,\\min}, \\quad \\epsilon_t = \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right), \\quad \\frac{c}{d_t} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} = \\frac{\\epsilon_{cu}}{\\epsilon_{cu} + \\epsilon_{t,\\min}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\begin{aligned}
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${endIFlex.dt.toFixed(1)} - ${endIFlex.c.toFixed(1)}}{${endIFlex.c.toFixed(1)}}\\right) = \\mathbf{${endIFlex.epsT.toFixed(4)}} \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}) \\\\
                                    \\frac{c}{d_t} &= \\frac{${endIFlex.c.toFixed(1)}}{${endIFlex.dt.toFixed(1)}} = \\mathbf{${(endIFlex.c / endIFlex.dt).toFixed(3)}} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)})
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{\\epsilon_t,I} = \\frac{\\epsilon_{t,\\min}}{\\epsilon_t} = \\mathbf{${endIFlex.dcrEps.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${endIFlex.isDuctilityOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                            </div>

                            <!-- 3.3 중앙부-M (Center-M) 최소철근량 및 연성 검토 (정모멘트, 하부인장) -->
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">3.3 중앙부-M (Center-M) 최소철근량 만족 및 연성파괴 유도 순인장변형률 검토 [정모멘트 작용, 하부 인장철근 $A_s = ${centerBot.totalArea.toFixed(1)}$ mm²]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1 & 4.2.2)</span>
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_{n,M} = \\mathbf{${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\ge 1.2 M_{cr} (${phiMnMin.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\quad (\\text{DCR} = ${centerMFlex.dcrMin.toFixed(3)}) \\quad \\rightarrow \\quad ${centerMFlex.isMinOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                                <div class="formula-row formula-subst" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    $$\\begin{aligned}
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${centerMFlex.dt.toFixed(1)} - ${centerMFlex.c.toFixed(1)}}{${centerMFlex.c.toFixed(1)}}\\right) = \\mathbf{${centerMFlex.epsT.toFixed(4)}} \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}) \\\\
                                    \\frac{c}{d_t} &= \\frac{${centerMFlex.c.toFixed(1)}}{${centerMFlex.dt.toFixed(1)}} = \\mathbf{${(centerMFlex.c / centerMFlex.dt).toFixed(3)}} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)})
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{\\epsilon_t,M} = \\frac{\\epsilon_{t,\\min}}{\\epsilon_t} = \\mathbf{${centerMFlex.dcrEps.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${centerMFlex.isDuctilityOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                            </div>

                            <!-- 3.4 단부-J (End-J) 최소철근량 및 연성 검토 -->
                            ${arrangeType === 'THREE_STATIONS' ? `
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span class="step-title">3.4 단부-J (End-J) 최소철근량 만족 및 연성파괴 유도 순인장변형률 검토 [독립 3단면, 상부 인장철근 $A_s = ${endJTop.totalArea.toFixed(1)}$ mm²]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1 & 4.2.2)</span>
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_{n,J} = \\mathbf{${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\ge 1.2 M_{cr} (${phiMnMin.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\quad (\\text{DCR} = ${endJFlex.dcrMin.toFixed(3)}) \\quad \\rightarrow \\quad ${endJFlex.isMinOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                                <div class="formula-row formula-subst" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    $$\\begin{aligned}
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${endJFlex.dt.toFixed(1)} - ${endJFlex.c.toFixed(1)}}{${endJFlex.c.toFixed(1)}}\\right) = \\mathbf{${endJFlex.epsT.toFixed(4)}} \\ge \\epsilon_{t,\\min} (${epsTMin.toFixed(4)}) \\\\
                                    \\frac{c}{d_t} &= \\frac{${endJFlex.c.toFixed(1)}}{${endJFlex.dt.toFixed(1)}} = \\mathbf{${(endJFlex.c / endJFlex.dt).toFixed(3)}} \\le \\left(\\frac{c}{d_t}\\right)_{\\lim} (${cDtLimit.toFixed(3)})
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{\\epsilon_t,J} = \\frac{\\epsilon_{t,\\min}}{\\epsilon_t} = \\mathbf{${endJFlex.dcrEps.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${endJFlex.isDuctilityOk ? '\\text{O.K}' : '\\text{N.G}'}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 12px;border-radius:4px;margin-top:10px;font-size:11px;">
                                <span style="font-weight:600;color:#1e3a8a;">3.4 단부-J (End-J) 최소철근량 만족 및 연성파괴 유도 검토:</span> 단부-I과 대칭 동일 배근 및 단면 ($\\\\phi M_n = ${endJFlex.phiMn.toFixed(1)}\\\\text{ kN}\\\\cdot\\\\text{m} \\\\ge 1.2 M_{cr}$, $\\\\epsilon_t = ${endJFlex.epsT.toFixed(4)}$) <span class="${endJFlex.isMinOk && endJFlex.isDuctilityOk ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.isMinOk && endJFlex.isDuctilityOk ? '  →  O.K' : '  →  N.G'}</span>
                            </div>
                            `}
                            `}
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>단부-I 최소철근량 만족 및 연성:</strong> $\\phi M_n = ${endIFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\ge 1.2 M_{cr}$, $\\epsilon_t = ${endIFlex.epsT.toFixed(4)}$ (DCR = ${endIFlex.dcrMin.toFixed(3)}) <span class="${endIFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${endIFlex.minVerdict}</span></div>
                                <div style="margin-bottom:6px;"><strong>중앙부-M 최소철근량 만족 및 연성:</strong> $\\phi M_n = ${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\ge 1.2 M_{cr}$, $\\epsilon_t = ${centerMFlex.epsT.toFixed(4)}$ (DCR = ${centerMFlex.dcrMin.toFixed(3)}) <span class="${centerMFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.minVerdict}</span></div>
                                <div><strong>단부-J 최소철근량 만족 및 연성:</strong> $\\phi M_n = ${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\ge 1.2 M_{cr}$, $\\epsilon_t = ${endJFlex.epsT.toFixed(4)}$ (DCR = ${endJFlex.dcrMin.toFixed(3)}) <span class="${endJFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.minVerdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 4장: 휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Positive & Negative Bending) -->
                        <section class="report-chapter" data-chapter-key="flexure">
                            <h2 class="chapter-heading" data-title-detail="휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Positive & Negative Bending)" data-title-summary="휨모멘트 강도 검토 요약 (Flexural Strength Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 4장</span>. <span class="chapter-title">휨모멘트 강도 검토 (Flexural Strength Check - 3-Station Positive & Negative Bending)</span>
                            </h2>

                            <!-- 4.1 3-Station 위치별 휨설계 강도 총괄 요약표 -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                4.1 3-Station 위치별 휨설계 강도 총괄 요약표
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
                            <!-- 4.2 단부-I (End-I) 부모멘트 (Mu-) 검토 -->
                            ${endIFlex.MuDemand <= 0 ? `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
                                <strong>4.2 단부-I 휨모멘트 검토:</strong> 작용 부모멘트 없음 ($M_u^- = 0.0\\text{ kN}\\cdot\\text{m}$) — 강도 검토 생략
                            </div>
                            ` : `
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">4.2 단부-I (End-I) 부모멘트 ($M_u^-$) 4단계 강도 검토 [상부 인장 배근, 복부폭 $b_w$ 직사각형 보]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    A_s &= ${endITop.totalArea.toFixed(1)}\\text{ mm}^2\\text{ (상부)}, \\quad A_s' = ${endIBot.totalArea.toFixed(1)}\\text{ mm}^2\\text{ (하부)}, \\quad \\beta_1 = ${beta1.toFixed(3)} \\\\
                                    a &= \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_w} = \\frac{${endITop.totalArea.toFixed(1)} \\times ${fy.toFixed(0)} - ${endIBot.totalArea.toFixed(1)} \\times ${fy.toFixed(0)}}{0.85 \\times ${fck.toFixed(1)} \\times ${b}} = \\mathbf{${endIFlex.a.toFixed(1)}\\text{ mm}} \\\\
                                    c &= \\frac{a}{\\beta_1} = \\frac{${endIFlex.a.toFixed(1)}}{${beta1.toFixed(3)}} = \\mathbf{${endIFlex.c.toFixed(1)}\\text{ mm}} \\\\
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${endIFlex.dt.toFixed(1)} - ${endIFlex.c.toFixed(1)}}{${endIFlex.c.toFixed(1)}}\\right) = \\mathbf{${endIFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad (\\phi = ${endIFlex.phi.toFixed(2)}) \\\\
                                    M_n &= \\left[A_s f_y \\left(d - \\frac{a}{2}\\right) + A_s' f_s' \\left(\\frac{a}{2} - d'\\right)\\right] \\times 10^{-6} = \\mathbf{${endIFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                    \\phi M_n &= ${endIFlex.phi.toFixed(2)} \\times ${endIFlex.Mn.toFixed(1)} = \\mathbf{${endIFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                    \\text{DCR}_{flex,I} &= \\frac{M_u^-}{\\phi M_n} = \\frac{${endIFlex.MuDemand.toFixed(1)}}{${endIFlex.phiMn.toFixed(1)}} = \\mathbf{${endIFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${endIFlex.isSafe ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>
                            `}

                            <!-- 4.3 중앙부 (Center-M) 정모멘트 (Mu+) 검토 -->
                            ${centerMFlex.MuDemand <= 0 ? `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
                                <strong>4.3 중앙부-M 휨모멘트 검토:</strong> 작용 정모멘트 없음 ($M_u^+ = 0.0\\text{ kN}\\cdot\\text{m}$) — 강도 검토 생략
                            </div>
                            ` : `
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">4.3 중앙부 (Center-M) 정모멘트 ($M_u^+$) 4단계 강도 검토 [하부 인장 배근, ${isTBeam ? `T형 유효폭 $b_e = ${bf}$ mm 압축` : `복부폭 $b = ${b}$ mm 직사각형 보`}]</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    A_s &= ${centerBot.totalArea.toFixed(1)}\\text{ mm}^2\\text{ (하부)}, \\quad A_s' = ${centerTop.totalArea.toFixed(1)}\\text{ mm}^2\\text{ (상부)} \\\\
                                    ${isTBeam ? `a &= \\mathbf{${centerMFlex.a.toFixed(1)}\\text{ mm}} \\le h_f (${hf}\\text{ mm}) \\quad \\longrightarrow \\quad \\text{유효폭 } b_e (${bf}\\text{ mm}) \\text{ 직사각형 보 거동} \\\\` : ''}
                                    a &= \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_e} = \\frac{${centerBot.totalArea.toFixed(1)} \\times ${fy.toFixed(0)} - ${centerTop.totalArea.toFixed(1)} \\times ${fy.toFixed(0)}}{0.85 \\times ${fck.toFixed(1)} \\times ${centerMFlex.bComp}} = \\mathbf{${centerMFlex.a.toFixed(1)}\\text{ mm}} \\\\
                                    c &= \\frac{a}{\\beta_1} = \\frac{${centerMFlex.a.toFixed(1)}}{${beta1.toFixed(3)}} = \\mathbf{${centerMFlex.c.toFixed(1)}\\text{ mm}} \\\\
                                    \\epsilon_t &= \\epsilon_{cu} \\left(\\frac{d_t - c}{c}\\right) = ${ecu.toFixed(4)} \\times \\left(\\frac{${centerMFlex.dt.toFixed(1)} - ${centerMFlex.c.toFixed(1)}}{${centerMFlex.c.toFixed(1)}}\\right) = \\mathbf{${centerMFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad (\\phi = ${centerMFlex.phi.toFixed(2)}) \\\\
                                    M_n &= \\left[A_s f_y \\left(d - \\frac{a}{2}\\right) + A_s' f_s' \\left(\\frac{a}{2} - d'\\right)\\right] \\times 10^{-6} = \\mathbf{${centerMFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                    \\phi M_n &= ${centerMFlex.phi.toFixed(2)} \\times ${centerMFlex.Mn.toFixed(1)} = \\mathbf{${centerMFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                    \\text{DCR}_{flex,M} &= \\frac{M_u^+}{\\phi M_n} = \\frac{${centerMFlex.MuDemand.toFixed(1)}}{${centerMFlex.phiMn.toFixed(1)}} = \\mathbf{${centerMFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${centerMFlex.isSafe ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>
                            `}

                            <!-- 4.4 단부-J (End-J) 부모멘트 (Mu-) 검토 -->
                            ${arrangeType === 'THREE_STATIONS' ? (
                                endJFlex.MuDemand <= 0 ? `
                                <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
                                    <strong>4.4 단부-J 휨모멘트 검토:</strong> 작용 부모멘트 없음 ($M_u^- = 0.0\\text{ kN}\\cdot\\text{m}$) — 강도 검토 생략
                                </div>
                                ` : `
                                <div class="katex-formula-step" style="margin-top:12px;">
                                    <div class="step-title-row">
                                        <span class="step-title">4.4 단부-J (End-J) 부모멘트 ($M_u^-$) 4단계 강도 검토 [독립 3단면 비대칭 배근, 상부 인장]</span>
                                        <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                    </div>
                                    <div class="formula-row">
                                        $$\\begin{aligned}
                                        A_s &= ${endJTop.totalArea.toFixed(1)}\\text{ mm}^2, \\quad A_s' = ${endJBot.totalArea.toFixed(1)}\\text{ mm}^2 \\\\
                                        a &= \\mathbf{${endJFlex.a.toFixed(1)}\\text{ mm}}, \\quad c = \\mathbf{${endJFlex.c.toFixed(1)}\\text{ mm}}, \\quad \\epsilon_t = \\mathbf{${endJFlex.epsT.toFixed(4)}} \\ge 0.005 \\quad (\\phi = ${endJFlex.phi.toFixed(2)}) \\\\
                                        M_n &= \\mathbf{${endJFlex.Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}, \\quad \\phi M_n = \\mathbf{${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                        \\text{DCR}_{flex,J} &= \\frac{M_u^-}{\\phi M_n} = \\frac{${endJFlex.MuDemand.toFixed(1)}}{${endJFlex.phiMn.toFixed(1)}} = \\mathbf{${endJFlex.dcr.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${endJFlex.isSafe ? '\\text{O.K}' : '\\text{N.G}'}
                                        \\end{aligned}$$
                                    </div>
                                </div>
                                `
                            ) : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;">
                                <strong>4.4 단부-J (End-J) 부모멘트 검토:</strong> 단부-I과 대칭 동일 단면 ($M_u^- = ${endJFlex.MuDemand.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${endJFlex.phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$, DCR = ${endJFlex.dcr.toFixed(3)}) <span class="${endJFlex.isSafe ? 'verdict-ok' : 'verdict-ng'}">${endJFlex.verdict}</span>
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

                        <!-- 제 5장: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check) -->
                        <section class="report-chapter" data-chapter-key="shear">
                            <h2 class="chapter-heading" data-title-detail="전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)" data-title-summary="전단 및 비틀림 강도 검토 요약 (Shear & Torsion Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 5장</span>. <span class="chapter-title">전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)</span>
                            </h2>

                            <!-- 5.1 3-Station 전단력 및 전단강도 총괄 요약표 -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                5.1 3-Station 전단력 및 전단강도 총괄 요약표
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
                                        <th>설계전단강도 ($\phi V_n$)</th>
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

                            <!-- 5.1-B 3-Station 최소 전단철근량 및 배근간격 검토 총괄 요약표 (KDS 14 20 22) -->
                            <div style="font-weight:700;color:#1e3a8a;margin:10px 0 6px;font-size:12.5px;">
                                5.1.B 3-Station 최소 전단철근량 ($A_{v,\min}$) 및 최대 배근간격 ($s_{\max}$) 총괄 요약표
                            </div>
                            <table class="chk-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:11px;text-align:center;margin-bottom:12px;">
                                <colgroup>
                                    <col style="width:18%;">
                                    <col style="width:20%;">
                                    <col style="width:16%;">
                                    <col style="width:15%;">
                                    <col style="width:16%;">
                                    <col style="width:15%;">
                                </colgroup>
                                <thead>
                                    <tr style="background:#e2e8f0;">
                                        <th style="padding:6px;">검토 위치 (Station)</th>
                                        <th>배근 스터럽 ($A_{v,prov}, s$)</th>
                                        <th>최소 철근량 ($A_{v,\min}$)</th>
                                        <th>최소철근 DCR</th>
                                        <th>최대 허용간격 ($s_{\max}$)</th>
                                        <th>간격 DCR / 판정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-I (End-I)</td>
                                        <td>${stirrupDia} @ ${endIS} mm (${endIShear.AvProv.toFixed(1)} mm²)</td>
                                        <td>${endIShear.AvMin.toFixed(1)} mm²</td>
                                        <td style="font-weight:700;" class="${endIShear.isMinShearOk ? 'verdict-ok' : 'verdict-ng'}">${endIShear.dcrAvMin.toFixed(3)}</td>
                                        <td>${endIShear.sMax.toFixed(1)} mm</td>
                                        <td style="font-weight:800;" class="${endIShear.isSpacingOk ? 'verdict-ok' : 'verdict-ng'}">${endIShear.dcrSpacing.toFixed(3)} ${endIShear.spacingVerdict}</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부-M (Center-M)</td>
                                        <td>${centerRebarRaw.stirrup_dia || stirrupDia} @ ${centerS} mm (${centerMShear.AvProv.toFixed(1)} mm²)</td>
                                        <td>${centerMShear.AvMin.toFixed(1)} mm²</td>
                                        <td style="font-weight:700;" class="${centerMShear.isMinShearOk ? 'verdict-ok' : 'verdict-ng'}">${centerMShear.dcrAvMin.toFixed(3)}</td>
                                        <td>${centerMShear.sMax.toFixed(1)} mm</td>
                                        <td style="font-weight:800;" class="${centerMShear.isSpacingOk ? 'verdict-ok' : 'verdict-ng'}">${centerMShear.dcrSpacing.toFixed(3)} ${centerMShear.spacingVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부-J (End-J)</td>
                                        <td>${stirrupDia} @ ${endJS} mm (${endJShear.AvProv.toFixed(1)} mm²)</td>
                                        <td>${endJShear.AvMin.toFixed(1)} mm²</td>
                                        <td style="font-weight:700;" class="${endJShear.isMinShearOk ? 'verdict-ok' : 'verdict-ng'}">${endJShear.dcrAvMin.toFixed(3)}</td>
                                        <td>${endJShear.sMax.toFixed(1)} mm</td>
                                        <td style="font-weight:800;" class="${endJShear.isSpacingOk ? 'verdict-ok' : 'verdict-ng'}">${endJShear.dcrSpacing.toFixed(3)} ${endJShear.spacingVerdict}</td>
                                    </tr>
                                </tbody>
                            </table>

                            ${mode === 'detail' ? `
                            <!-- 5.2 최대 계수전단력 지배 단부 전단강도 KaTeX 전개 (0하중 동적 생략 지원) -->
                            ${governingShear.VuDemand <= 0 ? `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
                                <strong>5.2 전단강도 검토:</strong> 작용 계수전단력 없음 ($V_u = 0.0\\text{ kN}$) — 전단강도 상세 검토 생략
                            </div>
                            ` : `
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.2 최대 계수전단력 지배 단부 [${governingShear.stationTag}] 전단강도 산정 (KDS 14 20 22)</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    V_c &= \\frac{1}{6} \\lambda \\sqrt{f_{ck}} b_w d = \\frac{1}{6} \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} \\times ${b} \\times ${endIFlex.d.toFixed(1)} \\times 10^{-3} = \\mathbf{${governingShear.Vc.toFixed(1)}\\text{ kN}} \\\\
                                    V_s &= \\frac{A_v f_{yt} d}{s} = \\frac{${AvProvEnd.toFixed(1)} \\times ${fyt.toFixed(0)} \\times ${endIFlex.d.toFixed(1)}}{${endIS}} \\times 10^{-3} = \\mathbf{${governingShear.Vs.toFixed(1)}\\text{ kN}} \\le V_{s,\\max} (${governingShear.VsMax.toFixed(1)}\\text{ kN}) \\\\
                                    \\phi V_n &= \\phi (V_c + V_s) = 0.75 \\times (${governingShear.Vc.toFixed(1)} + ${governingShear.Vs.toFixed(1)}) = \\mathbf{${governingShear.phiVn.toFixed(1)}\\text{ kN}} \\\\
                                    \\text{DCR}_{shear} &= \\frac{${governingShear.VuDemand.toFixed(1)}}{${governingShear.phiVn.toFixed(1)}} = \\mathbf{${governingShear.dcr.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${governingShear.isSafe ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>
                            `}

                            <!-- 5.3 최소 전단철근량 및 최대 배근간격 검토 (상시 필수 출력, Vu <= 0이어도 생략 불가) -->
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">5.3 최소 전단철근량 ($A_{v,\\min}$) 및 최대 배근간격 ($s_{\\max}$) 검토 [지배 단부, 상시 필수 규정]</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.3.3 & 4.3.4)</span>
                                </div>
                                <div class="formula-row" style="font-size:11px;color:#475569;margin-bottom:6px;">
                                    ※ KDS 14 20 22 제4.3.3(1)에 따라 보 전체 높이 $h > 250\\text{ mm}$인 일반 구조용 보는 작용 전단력 크기와 무관하게 취성파괴 방지를 위한 법정 최소 전단철근량 및 최대 배근간격을 반드시 만족해야 합니다.
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    A_{v,\\min} &= \\max\\left(0.0625 \\sqrt{f_{ck}} \\frac{b_w s}{f_{yt}}, \\, 0.35 \\frac{b_w s}{f_{yt}}\\right) \\\\
                                    &= \\max\\left(0.0625 \\times \\sqrt{${fck.toFixed(1)}} \\times \\frac{${b} \\times ${governingShear.sSpacing}}{${fyt.toFixed(0)}}, \\, 0.35 \\times \\frac{${b} \\times ${governingShear.sSpacing}}{${fyt.toFixed(0)}}\\right) = \\mathbf{${governingShear.AvMin.toFixed(1)}\\text{ mm}^2} \\le A_{v,prov} (${governingShear.AvProv.toFixed(1)}\\text{ mm}^2) \\\\
                                    \\text{DCR}_{Av,\\min} &= \\frac{A_{v,\\min}}{A_{v,prov}} = \\frac{${governingShear.AvMin.toFixed(1)}}{${governingShear.AvProv.toFixed(1)}} = \\mathbf{${governingShear.dcrAvMin.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${governingShear.isMinShearOk ? '\\text{O.K}' : '\\text{N.G}'} \\\\
                                    s_{\\max} &= \\min\\left(\\frac{d}{2}, \\, 600\\text{ mm}\\right) = \\min\\left(${endIFlex.d.toFixed(1)} / 2, \\, 600\\right) = \\mathbf{${governingShear.sMax.toFixed(1)}\\text{ mm}} \\ge s (${governingShear.sSpacing}\\text{ mm}) \\\\
                                    \\text{DCR}_{spacing} &= \\frac{s}{s_{\\max}} = \\frac{${governingShear.sSpacing}}{${governingShear.sMax.toFixed(1)}} = \\mathbf{${governingShear.dcrSpacing.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${governingShear.isSpacingOk ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>

                            <!-- 5.4 비틀림 임계 검토 및 상호작용 (0하중 동적 생략 및 최소비틀림철근 KaTeX 지원) -->
                            ${isZeroTorsion ? `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:10px 14px;border-radius:4px;margin-top:10px;font-size:11.5px;color:#475569;">
                                <strong>5.4 비틀림 모멘트 검토:</strong> 설계 비틀림 모멘트 없음 ($T_u = 0.0\\text{ kN}\\cdot\\text{m}$) — 비틀림 상세 설계 생략 (부재 횡방향 최소 배근은 5.3절 전단 최소철근 배근으로 갈음)
                            </div>
                            ` : `
                            <div class="katex-formula-step" style="margin-top:12px;">
                                <div class="step-title-row">
                                    <span class="step-title">5.4 비틀림모멘트 한계 검토 및 전단-비틀림 상호작용 (Torsion Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.3 & 4.5)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    T_{th} &= 0.0625 \\lambda \\sqrt{f_{ck}} \\left(\\frac{A_{cp}^2}{p_{cp}}\\right) = 0.0625 \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} \\times \\left(\\frac{${Acp}^2}{${pcp}}\\right) \\times 10^{-6} = \\mathbf{${Tth.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\\\
                                    \\phi T_{th} &= 0.75 \\times ${Tth.toFixed(1)} = \\mathbf{${phiTth.toFixed(1)}\\text{ kN}\\cdot\\text{m}} \\quad \\longrightarrow \\quad T_u = ${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m} ${isTorsionRequired ? '>' : '\\le'} \\phi T_{th} \\quad (${isTorsionRequired ? '비틀림 설계 필요' : '비틀림 무시 가능'})
                                    \\end{aligned}$$
                                </div>
                                ${!isTorsionRequired ? `
                                <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:8px 12px;border-radius:4px;margin-top:8px;font-size:11px;color:#475569;">
                                    $T_u (${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m}) \\le \\phi T_{th} (${phiTth.toFixed(1)}\\text{ kN}\\cdot\\text{m})$이므로 비틀림모멘트의 영향을 무시할 수 있으며, 전단-비틀림 결합응력 및 추가 종방향 철근 상세 설계를 생략합니다. (부재 횡방향 최소 배근은 5.3절 전단 최소철근 배근으로 갈음)
                                </div>
                                ` : `
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    $$\\begin{aligned}
                                    \\tau_{comb} &= \\sqrt{\\left(\\frac{V_u}{b_w d}\\right)^2 + \\left(\\frac{T_u p_h}{1.7 A_{oh}^2}\\right)^2} = \\sqrt{\\left(\\frac{${governingShear.VuDemand.toFixed(1)} \\times 10^3}{${b} \\times ${endIFlex.d.toFixed(1)}}\\right)^2 + \\left(\\frac{${tu.toFixed(1)} \\times 10^6 \\times ${ph}}{1.7 \\times ${Aoh}^2}\\right)^2} = \\mathbf{${torsionCombinedStress}\\text{ MPa}} \\\\
                                    \\tau_{allow} &= \\phi \\left(\\frac{V_c}{b_w d} + \\frac{2}{3} \\sqrt{f_{ck}}\\right) = \\mathbf{${torsionAllowStress}\\text{ MPa}} \\quad (\\text{DCR} = ${dcrTorsionStress.toFixed(3)}) \\quad \\rightarrow \\quad ${isTorsionStressOk ? '\\text{O.K}' : '\\text{N.G}'} \\\\
                                    (A_v + 2A_t)_{\\min} &= \\max\\left(0.0625 \\sqrt{f_{ck}} \\frac{b_w s}{f_{yt}}, \\, 0.35 \\frac{b_w s}{f_{yt}}\\right) = \\mathbf{${Av2AtMin.toFixed(1)}\\text{ mm}^2} \\le A_{v,prov} (${AvProvEnd.toFixed(1)}\\text{ mm}^2) \\\\
                                    A_{l,\\min} &= \\frac{0.42 \\sqrt{f_{ck}} A_{cp}}{f_y} - \\left(\\frac{A_t}{s}\\right) p_h \\left(\\frac{f_{yt}}{f_y}\\right) = \\mathbf{${AlMin.toFixed(1)}\\text{ mm}^2} \\quad \\left(\\frac{A_t}{s} \\ge \\frac{0.175 b_w}{f_{yt}}\\right) \\\\
                                    A_{l,req} &= \\max(A_{l,\\text{calc}}, \\, A_{l,\\min}) = \\max(${AlCalc.toFixed(1)}, \\, ${AlMin.toFixed(1)}) = \\mathbf{${AlReq.toFixed(1)}\\text{ mm}^2} \\le A_{l,prov} (${AlProv.toFixed(1)}\\text{ mm}^2) \\\\
                                    \\text{DCR}_{Al} &= \\frac{A_{l,req}}{A_{l,prov}} = \\frac{${AlReq.toFixed(1)}}{${AlProv.toFixed(1)}} = \\mathbf{${dcrAl.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${isAlOk ? '\\text{O.K}' : '\\text{N.G}'} \\\\
                                    s &\\le \\min\\left(\\frac{p_h}{8}, \\, 300\\text{ mm}\\right) = \\mathbf{${sMaxTorsion.toFixed(1)}\\text{ mm}} \\ge s (${endIS}\\text{ mm})
                                    \\end{aligned}$$
                                </div>
                                `}
                            </div>
                            `}
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>전단 강도 검토:</strong> ${governingShear.VuDemand <= 0 ? '작용 계수전단력 없음 ($V_u = 0$)' : `$V_u = ${governingShear.VuDemand.toFixed(1)}\\text{ kN} \\le \\phi V_n = ${governingShear.phiVn.toFixed(1)}\\text{ kN}$ (DCR = ${governingShear.dcr.toFixed(3)})`} <span class="${governingShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${governingShear.verdict}</span></div>
                                <div style="margin-bottom:6px;"><strong>최소 전단철근 및 간격:</strong> $A_{v,prov} (${governingShear.AvProv.toFixed(1)}\\text{ mm}^2) \\ge A_{v,\\min} (${governingShear.AvMin.toFixed(1)}\\text{ mm}^2)$, $s (${governingShear.sSpacing}\\text{ mm}) \\le s_{\\max} (${governingShear.sMax.toFixed(1)}\\text{ mm})$ <span class="${governingShear.isMinShearOk && governingShear.isSpacingOk ? 'verdict-ok' : 'verdict-ng'}">${governingShear.isMinShearOk && governingShear.isSpacingOk ? '  →  O.K' : '  →  N.G'}</span></div>
                                <div><strong>비틀림 강도 검토:</strong> ${isZeroTorsion ? '설계 비틀림 없음 ($T_u = 0$)' : `$T_u = ${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi T_n = ${phiTn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${dcrTorsion.toFixed(3)})`} <span class="${dcrTorsion <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${torsionVerdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 6장: 사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width) -->
                        <section class="report-chapter" data-chapter-key="serviceability">
                            <h2 class="chapter-heading" data-title-detail="사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)" data-title-summary="사용성 한계상태 검토 요약 (Serviceability Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 6장</span>. <span class="chapter-title">사용성 한계상태 검토 (Serviceability Check - Deflection & Crack Width)</span>
                            </h2>
                            ${mode === 'detail' ? `
                            <!-- 6.1 Branson 유효단면2차모멘트 Ie 가중평균 산정 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">6.1 Branson 유효단면2차모멘트 ($I_e$) 가중평균 산정 [${supportCondText}]</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.1)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    M_{cr} &= \\frac{f_r I_g}{y_t} = \\frac{${fr.toFixed(2)} \\times ${Ig.toLocaleString()}}{${yt}} \\times 10^{-6} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}, \\quad I_g = \\mathbf{${Ig.toExponential(2)}\\text{ mm}^4} \\\\
                                    I_{e,m} &= \\left(\\frac{M_{cr}}{M_{a,m}}\\right)^3 I_g + \\left[1 - \\left(\\frac{M_{cr}}{M_{a,m}}\\right)^3\\right] I_{cr,m} = \\mathbf{${Number(IeM).toExponential(2)}\\text{ mm}^4} \\\\
                                    I_{e,i} &= \\mathbf{${Number(IeI).toExponential(2)}\\text{ mm}^4}, \\quad I_{e,j} = \\mathbf{${Number(IeJ).toExponential(2)}\\text{ mm}^4} \\\\
                                    I_{e,avg} &= ${IeFormulaText} = \\mathbf{${Number(IeAvg).toExponential(2)}\\text{ mm}^4} \\le I_g \\\\
                                    \\lambda_\\Delta &= \\frac{\\xi}{1 + 50\\rho'} = \\frac{2.0}{1 + 50 \\times ${rhoPrime.toFixed(4)}} = \\mathbf{${lambdaDelta.toFixed(2)}}
                                    \\end{aligned}$$
                                </div>
                            </div>

                            <!-- 6.2 단기 및 장기 처짐량 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">6.2 단기 및 장기 처짐량 검토 (Deflection Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    \\Delta_{long} &= \\lambda_\\Delta \\times \\Delta_{sus} = ${lambdaDelta.toFixed(2)} \\times ${deltaSus.toFixed(1)} = \\mathbf{${deltaLong.toFixed(1)}\\text{ mm}} \\\\
                                    \\Delta_{total} &= \\Delta_{immediate} + \\Delta_{long} = ${deltaImmediate.toFixed(1)} + ${deltaLong.toFixed(1)} = \\mathbf{${deltaTotal.toFixed(1)}\\text{ mm}} \\\\
                                    \\Delta_{allow} &= \\frac{L}{240} = \\frac{${L}}{240} = \\mathbf{${deltaAllow.toFixed(1)}\\text{ mm}} \\\\
                                    \\text{DCR}_{defl} &= \\frac{\\Delta_{total}}{\\Delta_{allow}} = \\frac{${deltaTotal.toFixed(1)}}{${deltaAllow.toFixed(1)}} = \\mathbf{${dcrDefl.toFixed(3)}} \\le 1.000 \\quad \\rightarrow \\quad ${dcrDefl <= 1.0 ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>

                            <!-- 6.3 KDS 14 20 30 제4.2.3절 균열방지 철근간격 제한 (s <= s_max) 3-Station 개별 전개 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">6.3 균열방지 휨철근 간격 제한 검토 ($s \\le s_{\\max}$, KDS 14 20 30 식 4.2-4)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.3)</span>
                                </div>
                                <div class="formula-row">
                                    $$kd = \\frac{-B_{kd} + \\sqrt{B_{kd}^2 - 4 A_{kd} C_{kd}}}{2 A_{kd}}, \\quad jd = d - \\frac{kd}{3}, \\quad f_s = \\frac{M_a \\times 10^6}{A_s \\cdot jd} \\le 0.6 f_y$$
                                    $$s_{\\max} = 375 \\left(\\frac{k_{cr}}{f_s}\\right) - 2.5 c_c \\le 300 \\left(\\frac{k_{cr}}{f_s}\\right) \\quad (k_{cr} = 210)$$
                                </div>
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    <strong>6.3.1 단부-I [상부 인장]:</strong>
                                    $$\\begin{aligned}
                                    f_{s,i} &= \\frac{${Math.abs(endIMa).toFixed(1)} \\times 10^6}{${endITop.totalArea.toFixed(1)} \\times ${crackI.jd.toFixed(1)}} = \\mathbf{${crackI.fs.toFixed(1)}\\text{ MPa}} \\le 0.6 f_y (${(0.6 * fy).toFixed(1)}\\text{ MPa}) \\\\
                                    s_{\\max,i} &= 375 \\left(\\frac{${crackI.kcr}}{${crackI.fs.toFixed(1)}}\\right) - 2.5 \\times ${crackI.cc} = \\mathbf{${crackI.sMax.toFixed(1)}\\text{ mm}} \\\\
                                    s_{actual,i} &= \\mathbf{${crackI.sActual.toFixed(1)}\\text{ mm}} \\le s_{\\max,i} \\quad (\\text{DCR} = ${crackI.dcr.toFixed(3)}) \\quad \\rightarrow \\quad ${crackI.isOk ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    <strong>6.3.2 중앙부-M [하부 인장]:</strong>
                                    $$\\begin{aligned}
                                    f_{s,m} &= \\frac{${Math.abs(centerMa).toFixed(1)} \\times 10^6}{${centerBot.totalArea.toFixed(1)} \\times ${crackM.jd.toFixed(1)}} = \\mathbf{${crackM.fs.toFixed(1)}\\text{ MPa}} \\le 0.6 f_y (${(0.6 * fy).toFixed(1)}\\text{ MPa}) \\\\
                                    s_{\\max,m} &= 375 \\left(\\frac{${crackM.kcr}}{${crackM.fs.toFixed(1)}}\\right) - 2.5 \\times ${crackM.cc} = \\mathbf{${crackM.sMax.toFixed(1)}\\text{ mm}} \\\\
                                    s_{actual,m} &= \\mathbf{${crackM.sActual.toFixed(1)}\\text{ mm}} \\le s_{\\max,m} \\quad (\\text{DCR} = ${crackM.dcr.toFixed(3)}) \\quad \\rightarrow \\quad ${crackM.isOk ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                                ${arrangeType === 'THREE_STATIONS' ? `
                                <div class="formula-row" style="margin-top:6px;border-top:1px dashed #e2e8f0;padding-top:6px;">
                                    <strong>6.3.3 단부-J [상부 인장]:</strong>
                                    $$\\begin{aligned}
                                    f_{s,j} &= \\frac{${Math.abs(endJMa).toFixed(1)} \\times 10^6}{${endJTop.totalArea.toFixed(1)} \\times ${crackJ.jd.toFixed(1)}} = \\mathbf{${crackJ.fs.toFixed(1)}\\text{ MPa}} \\le 0.6 f_y (${(0.6 * fy).toFixed(1)}\\text{ MPa}) \\\\
                                    s_{\\max,j} &= 375 \\left(\\frac{${crackJ.kcr}}{${crackJ.fs.toFixed(1)}}\\right) - 2.5 \\times ${crackJ.cc} = \\mathbf{${crackJ.sMax.toFixed(1)}\\text{ mm}} \\\\
                                    s_{actual,j} &= \\mathbf{${crackJ.sActual.toFixed(1)}\\text{ mm}} \\le s_{\\max,j} \\quad (\\text{DCR} = ${crackJ.dcr.toFixed(3)}) \\quad \\rightarrow \\quad ${crackJ.isOk ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                                ` : `
                                <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:8px 12px;border-radius:4px;margin-top:6px;font-size:11px;">
                                    <strong>6.3.3 단부-J [상부 인장]:</strong> 단부-I 대칭 동일 간격 ($s_{actual,j} = ${crackJ.sActual.toFixed(1)}\\text{ mm} \\le s_{\\max,j} = ${crackJ.sMax.toFixed(1)}\\text{ mm}$, DCR = ${crackJ.dcr.toFixed(3)}) <span class="${crackJ.isOk ? 'verdict-ok' : 'verdict-ng'}">${crackJ.verdict}</span>
                                </div>
                                `}
                            </div>

                            <!-- 6.4 직접 균열폭 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">6.4 직접 균열폭 검토 (Direct Crack Width Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.1.2)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\begin{aligned}
                                    w &= 1.08 \\beta \\left(\\frac{f_s}{E_s}\\right) \\sqrt[3]{d_c s} = 1.08 \\times 1.2 \\times \\left(\\frac{${fsDirect}}{${Es.toLocaleString()}}\\right) \\times \\sqrt[3]{${dc} \\times ${crackM.sActual}} = \\mathbf{${crackWidth.toFixed(2)}\\text{ mm}} \\\\
                                    w &\\le w_{lim} = \\mathbf{${crackAllow.toFixed(2)}\\text{ mm}} \\quad (\\text{DCR} = ${dcrCrack.toFixed(3)}) \\quad \\rightarrow \\quad ${dcrCrack <= 1.0 ? '\\text{O.K}' : '\\text{N.G}'}
                                    \\end{aligned}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>처짐 검토:</strong> $\\Delta_{total} = ${deltaTotal.toFixed(1)}\\text{ mm} \\le \\Delta_{allow} = ${deltaAllow.toFixed(1)}\\text{ mm}$ (DCR = ${dcrDefl.toFixed(3)}) <span class="${dcrDefl <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${deflVerdict}</span></div>
                                <div style="margin-bottom:6px;"><strong>균열 철근간격 검토:</strong> $s_{actual} \\le s_{\\max}$ (최대 DCR = ${Math.max(crackI.dcr, crackM.dcr, crackJ.dcr).toFixed(3)}) <span class="${crackI.isOk && crackM.isOk && crackJ.isOk ? 'verdict-ok' : 'verdict-ng'}">${crackI.isOk && crackM.isOk && crackJ.isOk ? '  →  O.K' : '  →  N.G'}</span></div>
                                <div><strong>직접 균열폭 검토:</strong> $w = ${crackWidth.toFixed(2)}\\text{ mm} \\le w_{lim} = ${crackAllow.toFixed(2)}\\text{ mm}$ (DCR = ${dcrCrack.toFixed(3)}) <span class="${dcrCrack <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${crackVerdict}</span></div>
                            </div>
                            `}
                        </section>

                        <!-- 제 7장: 종합 안전성 판정 (Executive Summary & Final Verdict) -->
                        <section class="report-chapter" data-chapter-key="verdict">
                            <h2 class="chapter-heading" data-title-detail="종합 안전성 판정 (Executive Summary & Final Verdict)" data-title-summary="종합 안전성 판정 (Executive Summary & Final Verdict)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 7장</span>. <span class="chapter-title">종합 안전성 판정 (Executive Summary & Final Verdict)</span>
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
                                        <th>소요 부재력 / 실제치</th>
                                        <th>설계 내력 / 허용치</th>
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
                                        <td style="font-weight:600;padding:6px;">최소 철근량 (Min Rebar)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.2.2)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">1.2 Mcr (${phiMnMin.toFixed(1)} kN·m)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">\\phi Mn (${centerMFlex.phiMn.toFixed(1)} kN·m)</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${centerMFlex.dcrMin.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${centerMFlex.isMinOk ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.minVerdict}</td>
                                    </tr>
                                    <tr style="background:#f8fafc;">
                                        <td style="font-weight:600;padding:6px;">단면 연성 (Ductility)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1.2)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">\\epsilon_{t,\\min} (${epsTMin.toFixed(4)})</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">\\epsilon_t (${centerMFlex.epsT.toFixed(4)})</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${centerMFlex.dcrEps.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${centerMFlex.isDuctilityOk ? 'verdict-ok' : 'verdict-ng'}">${centerMFlex.ductilityVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">설계 전단력 ($V_u$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.VuDemand.toFixed(1)} kN</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.phiVn.toFixed(1)} kN</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${governingShear.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${governingShear.isSafe ? 'verdict-ok' : 'verdict-ng'}">${governingShear.verdict}</td>
                                    </tr>
                                    <tr style="background:#f8fafc;">
                                        <td style="font-weight:600;padding:6px;">최소 전단철근량 ($A_{v,\\min}$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.3.3)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.AvMin.toFixed(1)} mm²</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.AvProv.toFixed(1)} mm²</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${governingShear.dcrAvMin.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${governingShear.isMinShearOk ? 'verdict-ok' : 'verdict-ng'}">${governingShear.minVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">전단철근 최대간격 ($s_{\\max}$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.3.4)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.sSpacing} mm</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${governingShear.sMax.toFixed(1)} mm</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${governingShear.dcrSpacing.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${governingShear.isSpacingOk ? 'verdict-ok' : 'verdict-ng'}">${governingShear.spacingVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">설계 비틀림 ($T_u$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.3)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${tu.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiTn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${isZeroTorsion ? '0.000' : dcrTorsion.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrTorsion <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${isZeroTorsion ? '  →  O.K' : torsionVerdict}</td>
                                    </tr>
                                    ${isTorsionRequired ? `
                                    <tr style="background:#f8fafc;">
                                        <td style="font-weight:600;padding:6px;">최소 비틀림 종방향철근 ($A_l$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.5.4)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${AlReq.toFixed(1)} mm²</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${AlProv.toFixed(1)} mm²</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrAl.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${isAlOk ? 'verdict-ok' : 'verdict-ng'}">${isAlOk ? '  →  O.K' : '  →  N.G'}</td>
                                    </tr>
                                    ` : ''}
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">총 처짐량 (Deflection)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 30 (4.2)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${deltaTotal.toFixed(1)} mm</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${deltaAllow.toFixed(1)} mm</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrDefl.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrDefl <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${deflVerdict}</td>
                                    </tr>
                                    <tr style="background:#f8fafc;">
                                        <td style="font-weight:600;padding:6px;">균열 철근간격 ($s \\le s_{\\max}$)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 30 (4.2.3)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${crackM.sActual.toFixed(1)} mm (중앙부)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${crackM.sMax.toFixed(1)} mm</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${crackM.dcr.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${crackM.isOk ? 'verdict-ok' : 'verdict-ng'}">${crackM.verdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">직접 균열폭 (Crack Width)</td>
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
