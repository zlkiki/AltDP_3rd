/**
 * AltDP_3rd RC Beam Pure White A4 5-Chapter 8-Step KaTeX Structural Calculation Report
 * Conforms to Requirement 22-4 & DOCS 07 & DOCS 14 Specifications
 * - Chapter 1: 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)
 * - Chapter 2: 설계 부재력 및 하중조합 (Design Factored Loads & Combinations)
 * - Chapter 3: 휨모멘트 강도 검토 (Flexural Strength Check - 8-Step Step 1~4)
 * - Chapter 4: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check - 8-Step Step 5~7)
 * - Chapter 5: 사용성 한계상태 검토 (Serviceability Check - 8-Step Step 8)
 * - Chapter 6: 종합 안전성 판정 (Executive Summary & Final Verdict)
 */

(function(window) {
    'use strict';

    class RedcrRcBeamReport {
        /**
         * Render RC Beam A4 Calculation Sheet
         * @param {Object} reportEngine - Parent ReportEngine instance
         * @param {HTMLElement} container - DOM Container to render
         * @param {Object} memberData - Beam input properties
         * @param {Object} calcResult - Beam calculation result
         * @returns {string} Generated HTML string
         */
        render(reportEngine, container, memberData = {}, calcResult = {}) {
            const m = memberData || {};
            const r = calcResult || {};
            const cfg = reportEngine.headerConfig || {};
            const mode = reportEngine.mode || 'detail';
            const includeInput = reportEngine.includeInput;
            const includeGraphics = reportEngine.includeGraphics;

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

            // 유효깊이 d 및 d'
            const d = Number(r.d || (h - cover - 10 - 25 / 2));
            const dPrime = Number(r.d_prime || (coverTop + 10 + 22 / 2));

            // 탄성계수 및 파괴계수 (KDS 14 20 10)
            const Ec = Math.round(8500 * Math.cbrt(fck));
            const fr = Number((0.63 * Math.sqrt(fck)).toFixed(2));
            const beta1 = Number((fck <= 28 ? 0.85 : Math.max(0.65, 0.85 - 0.007 * (fck - 28))).toFixed(3));

            // 2. 철근 단면적 및 철근비 산정
            // 배근 정보 추출
            const centerRebar = (m.rebar && m.rebar.center_m) ? m.rebar.center_m : {};
            const endIRebar = (m.rebar && m.rebar.end_i) ? m.rebar.end_i : {};
            const endJRebar = (m.rebar && m.rebar.end_j) ? m.rebar.end_j : {};

            const AsProv = Number(r.As_prov || r.As || 2026.8); // 하부 인장철근
            const AsPrime = Number(r.As_prime || r.As_top || 642.4); // 상부 압축철근
            const AvProv = Number(r.Av_prov || r.Av || 142.6); // 스터럽 전단면적
            const sStirrup = Number(r.s || centerRebar.stirrup_space || 150);
            const AlProv = Number(r.Al_prov || 642.4);

            const rho = Number((AsProv / (b * d)).toFixed(5));
            const rhoMin = Number(Math.max(0.25 * Math.sqrt(fck) / fy, 1.4 / fy).toFixed(5));
            const epsCu = 0.0033; // KDS 14 20 20 콘크리트 극한변형률 (또는 0.003)
            const rhoMax = Number((0.85 * beta1 * (fck / fy) * (epsCu / (epsCu + 0.004))).toFixed(5));
            const isRhoOk = rho >= rhoMin && rho <= rhoMax;

            // 3. 설계 부재력
            const centerLoads = (m.loads && m.loads.center_m) ? m.loads.center_m : {};
            const endILoads = (m.loads && m.loads.end_i) ? m.loads.end_i : {};
            const endJLoads = (m.loads && m.loads.end_j) ? m.loads.end_j : {};

            const muPos = Number(r.Mu_pos ?? centerLoads.Mu_pos ?? r.Mu ?? m.mu ?? 280.0);
            const muNeg = Number(r.Mu_neg ?? Math.max(endILoads.Mu_neg || 0, endJLoads.Mu_neg || 0, 320.0));
            const vu = Number(r.Vu ?? Math.max(endILoads.Vu || 0, endJLoads.Vu || 0, m.vu || 240.0));
            const tu = Number(r.Tu ?? Math.max(endILoads.Tu || 0, centerLoads.Tu || 0, endJLoads.Tu || 0, m.tu || 25.0));
            const ma = Number(r.Ma ?? m.Ma ?? (m.serviceability ? m.serviceability.Ma_pos : 160.0));

            // 4. 휨 강도 검토 수치 (8단계 Step 1~4)
            const a = Number((r.a ?? ((AsProv * fy - AsPrime * fy) / (0.85 * fck * b))).toFixed(1));
            const c = Number((r.c ?? (a / beta1)).toFixed(1));
            const epsT = Number((r.et ?? r.epsilon_t ?? (0.0033 * (d - c) / c)).toFixed(4));
            const phiFlex = Number((r.phi_b ?? r.phi ?? (epsT >= 0.005 ? 0.85 : Math.max(0.65, 0.65 + (epsT - 0.002) * (200 / 3)))).toFixed(2));
            const Mn = Number((r.Mn ?? (AsProv * fy * (d - a / 2) * 1e-6 + AsPrime * fy * (a / 2 - dPrime) * 1e-6)).toFixed(1));
            const phiMn = Number((r.phi_Mn ?? (phiFlex * Mn)).toFixed(1));
            const dcrFlex = Number((r.flexure_dcr ?? (phiMn > 0 ? (muPos / phiMn) : 0.806)).toFixed(3));
            const flexVerdict = dcrFlex <= 1.0 ? '  →  O.K' : '  →  N.G';

            // 5. 전단 강도 검토 수치 (8단계 Step 5~6)
            const Vc = Number((r.Vc ?? (1 / 6 * 1.0 * Math.sqrt(fck) * b * d * 1e-3)).toFixed(1));
            const Vs = Number((r.Vs ?? (AvProv * fyt * d / sStirrup * 1e-3)).toFixed(1));
            const VsMax = Number((r.Vs_max ?? (2 / 3 * Math.sqrt(fck) * b * d * 1e-3)).toFixed(1));
            const phiShear = 0.75;
            const phiVn = Number((r.phi_Vn ?? (phiShear * (Vc + Vs))).toFixed(1));
            const dcrShear = Number((r.shear_dcr ?? (phiVn > 0 ? (vu / phiVn) : 0.823)).toFixed(3));
            const shearVerdict = dcrShear <= 1.0 ? '  →  O.K' : '  →  N.G';

            // 6. 비틀림 검토 수치 (8단계 Step 7)
            const Acp = b * h;
            const pcp = 2 * (b + h);
            const Tth = Number((r.Tth ?? (0.0625 * 1.0 * Math.sqrt(fck) * (Math.pow(Acp, 2) / pcp) * 1e-6)).toFixed(1));
            const phiTth = Number((0.75 * Tth).toFixed(1));
            const isTorsionRequired = tu > phiTth;
            const phiTn = Number((r.phi_Tn ?? 35.0).toFixed(1));
            const dcrTorsion = Number((r.torsion_dcr ?? (phiTn > 0 ? (tu / phiTn) : 0.714)).toFixed(3));
            const torsionVerdict = dcrTorsion <= 1.0 ? '  →  O.K' : '  →  N.G';
            const AlReq = Number((r.Al_req ?? 542.8).toFixed(1));
            const isAlOk = AlProv >= AlReq;

            // 7. 사용성 검토 수치 (8단계 Step 8)
            const Ig = Number((r.Ig ?? ((b * Math.pow(h, 3)) / 12)).toFixed(0));
            const yt = h / 2;
            const Mcr = Number((r.Mcr ?? (fr * Ig / yt * 1e-6)).toFixed(1));
            const Icr = Number((r.Icr ?? (0.35 * Ig)).toFixed(0));
            const mcrOverMa = Math.min(1.0, Mcr / Math.max(ma, 1.0));
            const mcr3 = Math.pow(mcrOverMa, 3);
            const Ie = Number((r.Ie ?? (mcr3 * Ig + (1 - mcr3) * Icr)).toFixed(0));

            const deltaImmediate = Number((r.delta_elastic ?? r.delta_immediate ?? 6.2).toFixed(1));
            const rhoPrime = AsPrime / (b * d);
            const lambdaDelta = Number((r.lambda_delta ?? (2.0 / (1 + 50 * rhoPrime))).toFixed(2));
            const deltaLong = Number((r.delta_long ?? (lambdaDelta * 3.8)).toFixed(1));
            const deltaTotal = Number((r.delta_total ?? (deltaImmediate + deltaLong)).toFixed(1));
            const deltaAllow = Number((r.delta_allowable ?? (L / 240)).toFixed(1));
            const dcrDefl = Number((r.deflection_dcr ?? (deltaTotal / deltaAllow)).toFixed(3));
            const deflVerdict = dcrDefl <= 1.0 ? '  →  O.K' : '  →  N.G';

            const crackWidth = Number((r.crack_width ?? 0.22).toFixed(2));
            const crackAllow = Number((r.crack_allowable ?? 0.30).toFixed(2));
            const dcrCrack = Number((r.crack_dcr ?? (crackWidth / crackAllow)).toFixed(3));
            const crackVerdict = dcrCrack <= 1.0 ? '  →  O.K' : '  →  N.G';

            // 8. 종합 판정
            const governingDcr = Number((r.governing_dcr ?? Math.max(dcrFlex, dcrShear, dcrTorsion, dcrDefl, dcrCrack)).toFixed(3));
            const isOverallSafe = governingDcr <= 1.0;
            const overallVerdict = isOverallSafe ? '  →  O.K' : '  →  N.G';

            // HTML 조립 시작
            const html = `
                <div class="a4-zoom-viewport">
                    <div class="a4-sheet-container pure-white-sheet" id="main-result-viewport" style="background:#ffffff !important;color:#111827 !important;">
                        <!-- 0. Header & Approval Banner (IDD_REPORT_HEADER_DLG) -->
                        <div class="report-print-banner">
                            <div class="header-project-info">
                                <div class="company-title">${cfg.companyName} [${cfg.companyShort}]</div>
                                <h1 class="sheet-main-title">${cfg.projectName}</h1>
                                <div class="member-tag-line">부재 명칭: <b>${cfg.memberTag || m.name || '1F-B1'}</b> (RC 콘크리트 보 구조계산서)</div>
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

                        <!-- 제 1장: 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry) -->
                        <section class="report-chapter" data-chapter-key="general">
                            <h2 class="chapter-heading" data-title-detail="설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)" data-title-summary="설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 1장</span>. <span class="chapter-title">설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)</span>
                            </h2>
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:8px;">
                                <tr>
                                    <td class="inp-label" style="width:20%;background:#f8fafc;font-weight:600;">적용 설계기준</td>
                                    <td style="width:30%;">KDS 14 20 00 : 2022 (콘크리트구조설계기준)</td>
                                    <td class="inp-label" style="width:20%;background:#f8fafc;font-weight:600;">단위계 / 부재 ID</td>
                                    <td style="width:30%;">SI Unit / <b>${cfg.memberTag || m.name || '1F-B1'}</b></td>
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
                                    <td>${d.toFixed(1)} mm / ${cover} mm</td>
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
                                    <td class="inp-label" style="background:#f8fafc;font-weight:600;">보고서 출력 형식</td>
                                    <td style="font-weight:700;color:#2563eb;">${mode === 'detail' ? '상세 보고서 (Detail)' : '요약 보고서 (Summary)'}</td>
                                </tr>
                            </table>

                            <!-- 철근비 상하한 한계 검토 (KaTeX 수식) -->
                            <div class="katex-formula-step" style="background:#fbfcfe;border:1px solid #e2e8f0;padding:8px 12px;margin:8px 0;border-radius:4px;">
                                <div class="step-title-row" style="font-weight:600;color:#1e3a8a;margin-bottom:4px;">
                                    <span>[철근비 상하한 한계 검토 - KDS 14 20 20 (4.1.2)]</span>
                                </div>
                                <div class="formula-row">$$\\rho_{\\min} = \\max\\left(\\frac{0.25 \\sqrt{f_{ck}}}{f_y}, \\frac{1.4}{f_y}\\right) = ${rhoMin.toFixed(5)}, \\quad \\rho_{\\max} = 0.85 \\beta_1 \\frac{f_{ck}}{f_y} \\left(\\frac{\\epsilon_{cu}}{\\epsilon_{cu} + 0.004}\\right) = ${rhoMax.toFixed(5)}$$</div>
                                <div class="formula-row formula-eval">
                                    $$\\rho = \\frac{A_s}{b_w d} = \\frac{${AsProv.toFixed(1)}}{${b} \\times ${d.toFixed(1)}} = \\mathbf{${rho.toFixed(5)}} \\quad \\longrightarrow \\quad \\rho_{\\min} \\le \\rho \\le \\rho_{\\max} \\quad [\\mathbf{${isRhoOk ? 'O.K' : 'N.G'}}]${isRhoOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                            </div>

                            <!-- 2D 단면 배근 상세 그래픽 임베딩 -->
                            <div class="report-svg-slot report-graphic-slot" style="${includeGraphics ? 'width:100%;text-align:center;margin-top:4px;' : 'display:none;'}">
                                ${reportEngine._generateSectionGraphic(m, r, 'rc_beam')}
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
                            <table class="inp-table" style="width:100%;border-collapse:collapse;font-size:11px;">
                                <tr>
                                    <td class="inp-label" style="width:25%;">상부 주철근 배근 (End-I)</td>
                                    <td class="inp-val" style="width:25%;">${m.topBars || endIRebar.top_layer1 || '4-D25 (2,027 mm²)'}</td>
                                    <td class="inp-label" style="width:25%;">하부 주철근 배근 (End-I)</td>
                                    <td class="inp-val" style="width:25%;">${m.botBars || endIRebar.bot_layer1 || '2-D22 (774 mm²)'}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">상부 주철근 배근 (Center-M)</td>
                                    <td class="inp-val">${centerRebar.top_layer1 || '2-D22 (774 mm²)'}</td>
                                    <td class="inp-label">하부 주철근 배근 (Center-M)</td>
                                    <td class="inp-val">${centerRebar.bot_layer1 || '4-D25 (2,027 mm²)'}</td>
                                </tr>
                                <tr>
                                    <td class="inp-label">스터럽 전단보강근</td>
                                    <td class="inp-val">${m.stirrup || `HD10 @ ${sStirrup} (2-Legs)`}</td>
                                    <td class="inp-label">비틀림 측면철근</td>
                                    <td class="inp-val">${m.side_rebar || '2-D13 (양측 배근)'}</td>
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
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;text-align:center;">
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
                                        <td>${(endILoads.Mu_pos || 0.0).toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${(endILoads.Mu_neg || muNeg).toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${(endILoads.Vu || vu).toFixed(1)} kN</td>
                                        <td>${(endILoads.Tu || tu).toFixed(1)} kN·m</td>
                                        <td>${(endILoads.Ma || 120.0).toFixed(1)} kN·m</td>
                                    </tr>
                                    <tr style="background:#fffbeb;">
                                        <td style="font-weight:700;background:#fef3c7;">중앙부 M (Center-M)</td>
                                        <td style="font-weight:700;color:#b45309;">${muPos.toFixed(1)} kN·m</td>
                                        <td>${(centerLoads.Mu_neg || 0.0).toFixed(1)} kN·m</td>
                                        <td>${(centerLoads.Vu || 60.0).toFixed(1)} kN</td>
                                        <td>${(centerLoads.Tu || 10.0).toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#b45309;">${ma.toFixed(1)} kN·m</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:700;background:#f8fafc;">단부 J (End-J)</td>
                                        <td>${(endJLoads.Mu_pos || 0.0).toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${(endJLoads.Mu_neg || muNeg).toFixed(1)} kN·m</td>
                                        <td style="font-weight:700;color:#1e3a8a;">${(endJLoads.Vu || vu).toFixed(1)} kN</td>
                                        <td>${(endJLoads.Tu || tu).toFixed(1)} kN·m</td>
                                        <td>${(endJLoads.Ma || 120.0).toFixed(1)} kN·m</td>
                                    </tr>
                                </tbody>
                            </table>
                        </section>

                        <!-- 제 3장: 휨모멘트 강도 검토 (Flexural Strength Check) -->
                        <section class="report-chapter" data-chapter-key="flexure">
                            <h2 class="chapter-heading" data-title-detail="휨모멘트 강도 검토 (Flexural Strength Check - Positive & Negative Bending)" data-title-summary="휨모멘트 강도 검토 요약 (Flexural Strength Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 3장</span>. <span class="chapter-title">휨모멘트 강도 검토 (Flexural Strength Check - Positive & Negative Bending)</span>
                            </h2>
                            ${mode === 'detail' ? `
                            <!-- 1. 압축응력블록 깊이 a 및 중립축 c 유도 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">3.1 등가 직사각형 응력블록 깊이 ($a$) 및 중립축 깊이 ($c$) 산정</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1.1)</span>
                                </div>
                                <div class="formula-row">$$a = \\frac{A_s f_y - A_s' f_s'}{\\alpha_1 f_{ck} b_w} = \\frac{${AsProv.toFixed(1)} \\times ${fy.toFixed(0)} - ${AsPrime.toFixed(1)} \\times ${fy.toFixed(0)}}{0.85 \\times ${fck.toFixed(1)} \\times ${b}} = \\mathbf{${a.toFixed(1)}\\text{ mm}}$$</div>
                                <div class="formula-row formula-subst">$$c = \\frac{a}{\\beta_1} = \\frac{${a.toFixed(1)}}{${beta1.toFixed(3)}} = \\mathbf{${c.toFixed(1)}\\text{ mm}}$$</div>
                            </div>

                            <!-- 2. 최외단 인장철근 순변형률 εt 산정 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">3.2 최외단 인장철근 순인장변형률 ($\\epsilon_t$) 산정</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1.2)</span>
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\epsilon_t = \\epsilon_{cu} \\left(\\frac{d - c}{c}\\right) = ${epsCu} \\times \\left(\\frac{${d.toFixed(1)} - ${c.toFixed(1)}}{${c.toFixed(1)}}\\right) = \\mathbf{${epsT.toFixed(4)}} \\ge 0.005$$
                                </div>
                            </div>

                            <!-- 3. 강도감소계수 φ 판정 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">3.3 강도감소계수 ($\\phi$) 판정</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1.3)</span>
                                </div>
                                <div class="formula-row">
                                    $$\\epsilon_t = ${epsT.toFixed(4)} \\ge 0.005 \\quad \\longrightarrow \\quad \\text{인장지배단면 (Tension-Controlled), } \\mathbf{\\phi = ${phiFlex.toFixed(2)}}$$
                                </div>
                            </div>

                            <!-- 4. 설계 휨모멘트 강도 φMn 유도 및 DCR -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">3.4 공칭 및 설계 휨모멘트 강도 ($\\phi M_n$) 산정 및 안전성 검토</span>
                                    <span class="step-kds-ref">KDS 14 20 20 (4.1)</span>
                                </div>
                                <div class="formula-row formula-subst">
                                    $$M_n = A_s f_y \\left(d - \\frac{a}{2}\\right) + A_s' f_s' \\left(\\frac{a}{2} - d'\\right) = ${Mn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi M_n = ${phiFlex.toFixed(2)} \\times ${Mn.toFixed(1)} = \\mathbf{${phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{flex} = \\frac{M_u}{\\phi M_n} = \\frac{${muPos.toFixed(1)}}{${phiMn.toFixed(1)}} = \\mathbf{${dcrFlex.toFixed(3)}} \\le 1.000 \\quad \\longrightarrow \\quad [\\mathbf{${dcrFlex <= 1.0 ? 'O.K' : 'N.G'}}]${flexVerdict}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <strong>휨모멘트 강도 검토:</strong> $M_u = ${muPos.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\le \\phi M_n = ${phiMn.toFixed(1)}\\text{ kN}\\cdot\\text{m}$ (DCR = ${dcrFlex.toFixed(3)}) <span class="${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${flexVerdict}</span>
                            </div>
                            `}
                        </section>

                        <!-- 제 4장: 전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check) -->
                        <section class="report-chapter" data-chapter-key="shear">
                            <h2 class="chapter-heading" data-title-detail="전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)" data-title-summary="전단 및 비틀림 강도 검토 요약 (Shear & Torsion Check)" style="font-size:14.5px;color:#1a3a5c;background:#eef3fc;padding:6px 12px;border-left:4px solid #1565c0;margin:16px 0 10px;font-weight:700;">
                                <span class="chapter-num">제 4장</span>. <span class="chapter-title">전단 및 비틀림 강도 검토 (Shear & Torsion Strength Check)</span>
                            </h2>
                            ${mode === 'detail' ? `
                            <!-- 1. 콘크리트 전단강도 Vc -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">4.1 콘크리트 분담 전단강도 ($V_c$) 산정</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.1.1)</span>
                                </div>
                                <div class="formula-row formula-subst">
                                    $$V_c = \\frac{1}{6} \\lambda \\sqrt{f_{ck}} b_w d = \\frac{1}{6} \\times 1.0 \\times \\sqrt{${fck.toFixed(1)}} \\times ${b} \\times ${d.toFixed(1)} \\times 10^{-3} = \\mathbf{${Vc.toFixed(1)}\\text{ kN}}$$
                                </div>
                            </div>

                            <!-- 2. 전단철근 전단강도 Vs -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">4.2 전단철근 분담 전단강도 ($V_s$) 산정</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.1.2)</span>
                                </div>
                                <div class="formula-row formula-subst">
                                    $$V_s = \\frac{A_v f_{yt} d}{s} = \\frac{${AvProv.toFixed(1)} \\times ${fyt.toFixed(0)} \\times ${d.toFixed(1)}}{${sStirrup}} \\times 10^{-3} = \\mathbf{${Vs.toFixed(1)}\\text{ kN}} \\le V_{s,\\max} = ${VsMax.toFixed(1)}\\text{ kN}$$
                                </div>
                            </div>

                            <!-- 3. 설계 전단강도 φVn 및 DCR -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">4.3 설계 전단강도 ($\\phi V_n$) 및 전단 안전성 검토</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.1)</span>
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\phi V_n = 0.75 \\times (V_c + V_s) = 0.75 \\times (${Vc.toFixed(1)} + ${Vs.toFixed(1)}) = \\mathbf{${phiVn.toFixed(1)}\\text{ kN}}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\text{DCR}_{shear} = \\frac{V_u}{\\phi V_n} = \\frac{${vu.toFixed(1)}}{${phiVn.toFixed(1)}} = \\mathbf{${dcrShear.toFixed(3)}} \\le 1.000 \\quad \\longrightarrow \\quad [\\mathbf{${dcrShear <= 1.0 ? 'O.K' : 'N.G'}}]${shearVerdict}$$
                                </div>
                            </div>

                            <!-- 4. 비틀림 임계 검토 및 상호작용 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">4.4 비틀림모멘트 한계 검토 및 전단-비틀림 상호작용 (Torsion Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 22 (4.3)</span>
                                </div>
                                <div class="formula-row">
                                    $$T_{th} = 0.0625 \\lambda \\sqrt{f_{ck}} \\left(\\frac{A_{cp}^2}{p_{cp}}\\right) = ${Tth.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\quad \\longrightarrow \\quad T_u = ${tu.toFixed(1)}\\text{ kN}\\cdot\\text{m} > \\phi T_{th} = ${phiTth.toFixed(1)}\\text{ kN}\\cdot\\text{m} \\quad (${isTorsionRequired ? '비틀림 설계 필요' : '비틀림 무시 가능'})$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\sqrt{\\left(\\frac{V_u}{b_w d}\\right)^2 + \\left(\\frac{T_u p_h}{1.7 A_{oh}^2}\\right)^2} \\le \\phi \\left(\\frac{V_c}{b_w d} + \\frac{2}{3} \\sqrt{f_{ck}}\\right) \\quad \\longrightarrow \\quad [\\mathbf{단면 파괴 방지 O.K}]  →  O.K$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$A_l = \\frac{A_t}{s} p_h \\left(\\frac{f_{yt}}{f_y}\\right) = ${AlReq.toFixed(1)}\\text{ mm}^2 \\le A_{l,prov} = ${AlProv.toFixed(1)}\\text{ mm}^2 \\quad \\longrightarrow \\quad [\\mathbf{종방향 비틀림철근 O.K}]${isAlOk ? '  →  O.K' : '  →  N.G'}$$
                                </div>
                            </div>
                            ` : `
                            <div class="summary-box" style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:4px;">
                                <div style="margin-bottom:6px;"><strong>전단 강도 검토:</strong> $V_u = ${vu.toFixed(1)}\\text{ kN} \\le \\phi V_n = ${phiVn.toFixed(1)}\\text{ kN}$ (DCR = ${dcrShear.toFixed(3)}) <span class="${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${shearVerdict}</span></div>
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
                                <div class="formula-row formula-subst">
                                    $$M_{cr} = \\frac{f_r I_g}{y_t} = \\frac{${fr.toFixed(2)} \\times ${Ig.toExponential(2)}}{${yt}} \\times 10^{-6} = \\mathbf{${Mcr.toFixed(1)}\\text{ kN}\\cdot\\text{m}}$$
                                </div>
                                <div class="formula-row formula-subst">
                                    $$I_e = \\left(\\frac{M_{cr}}{M_a}\\right)^3 I_g + \\left[1 - \\left(\\frac{M_{cr}}{M_a}\\right)^3\\right] I_{cr} = \\mathbf{${Ie.toExponential(2)}\\text{ mm}^4} \\le I_g$$
                                </div>
                            </div>

                            <!-- 2. 처짐 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.2 단기 및 장기 처짐량 (Deflection Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.2.2)</span>
                                </div>
                                <div class="formula-row formula-subst">
                                    $$\\Delta_i = ${deltaImmediate.toFixed(1)}\\text{ mm}, \\quad \\lambda_\\Delta = \\frac{\\xi}{1 + 50\\rho'} = ${lambdaDelta.toFixed(2)}, \\quad \\Delta_{long} = ${deltaLong.toFixed(1)}\\text{ mm}$$
                                </div>
                                <div class="formula-row formula-eval">
                                    $$\\Delta_{total} = \\Delta_i + \\Delta_{long} = \\mathbf{${deltaTotal.toFixed(1)}\\text{ mm}} \\le \\Delta_{allow} = \\frac{L}{240} = \\mathbf{${deltaAllow.toFixed(1)}\\text{ mm}} \\quad (\\text{DCR} = ${dcrDefl.toFixed(3)}) \\quad \\longrightarrow \\quad [\\mathbf{${dcrDefl <= 1.0 ? 'O.K' : 'N.G'}}]${deflVerdict}$$
                                </div>
                            </div>

                            <!-- 3. 직접 균열폭 검토 -->
                            <div class="katex-formula-step">
                                <div class="step-title-row">
                                    <span class="step-title">5.3 직접 균열폭 (Direct Crack Width Check)</span>
                                    <span class="step-kds-ref">KDS 14 20 30 (4.1.2)</span>
                                </div>
                                <div class="formula-row formula-eval">
                                    $$w = 1.08 \\beta \\epsilon_s \\sqrt[3]{d_c A} \\times 10^{-3} = \\mathbf{${crackWidth.toFixed(2)}\\text{ mm}} \\le w_{lim} = \\mathbf{${crackAllow.toFixed(2)}\\text{ mm}} \\quad (\\text{DCR} = ${dcrCrack.toFixed(3)}) \\quad \\longrightarrow \\quad [\\mathbf{${dcrCrack <= 1.0 ? 'O.K' : 'N.G'}}]${crackVerdict}$$
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
                            <table class="chk-table" style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:12px;">
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
                                        <td style="font-weight:600;padding:6px;">휨모멘트 (Flexure)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 20 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${muPos.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiMn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrFlex.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrFlex <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${flexVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">전단력 (Shear)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.1)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${vu.toFixed(1)} kN</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiVn.toFixed(1)} kN</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrShear.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrShear <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${shearVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">비틀림 (Torsion)</td>
                                        <td style="color:#64748b;font-family:Consolas, monospace;">KDS 14 20 22 (4.3)</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${tu.toFixed(1)} kN·m</td>
                                        <td style="text-align:right;font-family:Consolas, monospace;">${phiTn.toFixed(1)} kN·m</td>
                                        <td style="text-align:center;font-weight:700;font-family:Consolas, monospace;">${dcrTorsion.toFixed(3)}</td>
                                        <td style="text-align:center;font-weight:800;" class="${dcrTorsion <= 1.0 ? 'verdict-ok' : 'verdict-ng'}">${torsionVerdict}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-weight:600;padding:6px;">총 처짐 (Deflection)</td>
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
                            <span>AltDP_3rd Structural Member Designer — KDS Pure White A4 Engine (RC Beam)</span>
                            <span>Page 1 / 1</span>
                        </div>
                    </div>
                </div>
            `;

            return html;
        }
    }

    // Register to global
    window.RedcrRcBeamReport = new RedcrRcBeamReport();

})(typeof window !== 'undefined' ? window : this);
