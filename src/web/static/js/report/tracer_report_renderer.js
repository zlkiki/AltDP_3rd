/**
 * AltDP-Core Platform Universal Calculation Tracer Report Renderer (tracer_report_renderer.js)
 * Conforms to Requirement 23 & 29 specifications and docs/07, docs/14 pure white A4 standards.
 * Dynamically converts CalculationTracer JSON AST into KaTeX-typeset 5-Chapter structural reports.
 * Completely eliminates report template hardcoding and escape backslash defects.
 */

(function(window) {
    'use strict';

    class TracerReportRenderer {
        /**
         * Render a CalculationTracer AST into the given DOM container.
         * @param {HTMLElement} container - DOM target container
         * @param {Object} tracerAST - Serialized CalculationTracer JSON AST
         * @param {Object} [options] - Additional display options
         */
        static render(container, tracerAST, options = {}) {
            if (!container) return;
            if (!tracerAST) {
                container.innerHTML = `
                    <div style="padding:40px;text-align:center;color:#64748b;font-family:'Pretendard', sans-serif;">
                        <div style="font-size:32px;margin-bottom:12px;">📑</div>
                        <div style="font-size:14px;font-weight:600;">계산서 생성 대기 중</div>
                        <div style="font-size:12px;margin-top:4px;">[⚡ 검토] 버튼을 클릭하여 KDS 구조계산서를 산출하십시오.</div>
                    </div>`;
                return;
            }

            const html = this.buildHtml(tracerAST, options);
            container.innerHTML = html;

            // Trigger KaTeX typeset
            if (window.ReportKaTeX && typeof window.ReportKaTeX.renderContainer === 'function') {
                window.ReportKaTeX.renderContainer(container);
            } else if (window.renderMathInElement && typeof window.renderMathInElement === 'function') {
                window.renderMathInElement(container, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false }
                    ],
                    throwOnError: false
                });
            }
        }

        /**
         * Render latex string to html using available KaTeX engine.
         */
        static renderMath(latex, displayMode = false) {
            if (!latex) return '';
            if (window.ReportKaTeX && typeof window.ReportKaTeX.renderMath === 'function') {
                return window.ReportKaTeX.renderMath(latex, displayMode);
            }
            if (window.katex && typeof window.katex.renderToString === 'function') {
                try {
                    return window.katex.renderToString(latex, { displayMode, throwOnError: false });
                } catch (e) {
                    return `<span class="raw-math">${latex}</span>`;
                }
            }
            return `<span class="raw-math">${latex}</span>`;
        }

        /**
         * Build HTML string from Tracer JSON AST.
         */
        static buildHtml(ast, options = {}) {
            const summary = ast.summary || {};
            const isSafe = summary.is_safe !== false && (summary.status === 'OK' || summary.status === 'PASS');
            const maxDcr = typeof summary.max_dcr === 'number' ? summary.max_dcr.toFixed(3) : '0.000';
            const memberName = ast.member_name || '부재';
            const title = ast.title || `${memberName} 구조계산서`;
            const standard = ast.standard || 'KDS 14 20 00';
            const dateStr = options.date || new Date().toISOString().slice(0, 10);
            const chapters = ast.chapters || [];

            let html = `
            <div class="a4-sheet-page pure-white-sheet altdp-tracer-report" style="background:#ffffff;padding:36px 44px;color:#0f172a;box-sizing:border-box;font-family:'Pretendard', 'Segoe UI', sans-serif;max-width:210mm;margin:0 auto;box-shadow:0 4px 16px rgba(0,0,0,0.06);border-radius:4px;">
                
                <!-- Action Toolbar (Print / Export) -->
                <div class="report-toolbar no-print" style="display:flex;justify-content:flex-end;gap:8px;margin-bottom:16px;border-bottom:1px dashed #e2e8f0;padding-bottom:10px;">
                    <button type="button" onclick="window.print()" style="background:#f8fafc;border:1px solid #cbd5e1;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:600;cursor:pointer;color:#334155;display:inline-flex;align-items:center;gap:4px;">
                        <span>🖨️</span> A4 인쇄 / PDF
                    </button>
                </div>

                <!-- Header Banner -->
                <div style="border-bottom:2px solid #0f172a;padding-bottom:12px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:flex-end;">
                    <div>
                        <div style="font-size:10.5px;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;">KDS STRUCTURAL CALCULATION REPORT (ALTD-CORE PLATFORM)</div>
                        <h1 style="margin:4px 0 0;font-size:20px;font-weight:800;color:#0f172a;">${title}</h1>
                    </div>
                    <div style="text-align:right;font-size:11px;color:#64748b;line-height:1.5;">
                        <div><b>검토부재:</b> <span style="color:#0f172a;font-weight:700;">${memberName}</span></div>
                        <div><b>적용기준:</b> ${standard}</div>
                        <div><b>검토일자:</b> ${dateStr}</div>
                    </div>
                </div>

                <!-- Executive Verdict Card -->
                <div style="background:${isSafe ? '#f0fdf4' : '#fef2f2'};border:1px solid ${isSafe ? '#bbf7d0' : '#fecaca'};padding:12px 16px;border-radius:6px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:11px;font-weight:700;color:${isSafe ? '#166534' : '#991b1b'};text-transform:uppercase;">구조 안전성 종합 판정 (STRUCTURAL INTEGRITY VERDICT)</div>
                        <div style="font-size:13px;font-weight:800;color:${isSafe ? '#15803d' : '#b91c1c'};margin-top:2px;">
                            ${isSafe ? 'KDS 설계기준 전체 만족 (CODE COMPLIANT - ALL CRITERIA SATISFIED)' : 'KDS 설계기준 초과/부적합 (EXCEEDS CODE LIMIT - CAPACITY DEFICIENT)'}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="display:inline-block;padding:4px 12px;border-radius:9999px;font-size:12px;font-weight:800;background:${isSafe ? '#16a34a' : '#dc2626'};color:#ffffff;">
                            ${isSafe ? 'OK' : 'NG'} (최대 DCR = ${maxDcr})
                        </span>
                    </div>
                </div>
            `;

            // Render Chapters
            chapters.forEach((chap, idx) => {
                html += `
                <section style="margin-bottom:24px;page-break-inside:avoid;">
                    <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1.5px solid #1e3a8a;padding-bottom:6px;margin-bottom:12px;">
                        <h2 style="font-size:13.5px;font-weight:700;color:#1e3a8a;margin:0;">
                            ${chap.title}
                        </h2>
                        <span style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.5px;">SECTION ${idx + 1}</span>
                    </div>`;

                // Calculation Steps Table
                if (chap.steps && chap.steps.length > 0) {
                    html += `
                    <div style="margin-bottom:14px;">
                        <table style="width:100%;border-collapse:collapse;font-size:11px;margin-bottom:8px;">
                            <thead>
                                <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-size:10.5px;text-align:left;">
                                    <th style="padding:6px 8px;width:24%;">검토 항목 및 기준조항</th>
                                    <th style="padding:6px 8px;width:38%;">수식 원형 (KDS Formula)</th>
                                    <th style="padding:6px 8px;width:38%;">변수 대입 및 산출 결과 (Result)</th>
                                </tr>
                            </thead>
                            <tbody>`;

                    chap.steps.forEach(st => {
                        const formulaMath = this.renderMath(st.formula, false);
                        let subStr = '';
                        if (typeof st.substitutions === 'object' && st.substitutions !== null) {
                            subStr = Object.entries(st.substitutions)
                                .map(([k, v]) => `${k} = ${v}`)
                                .join(', ');
                        } else {
                            subStr = String(st.substitutions || '');
                        }

                        html += `
                                <tr style="border-bottom:1px solid #f1f5f9;vertical-align:top;">
                                    <td style="padding:7px 8px;">
                                        <div style="font-weight:700;color:#0f172a;">${st.section}</div>
                                        ${st.standard_ref ? `<div style="font-size:9.5px;color:#64748b;margin-top:2px;">[${st.standard_ref}]</div>` : ''}
                                        ${st.description ? `<div style="font-size:9.5px;color:#94a3b8;margin-top:2px;">${st.description}</div>` : ''}
                                    </td>
                                    <td style="padding:7px 8px;font-family:KaTeX_Math, 'Times New Roman', serif;">
                                        <div class="katex-formula-step">${formulaMath}</div>
                                    </td>
                                    <td style="padding:7px 8px;">
                                        ${subStr ? `<div style="font-size:9.5px;color:#64748b;margin-bottom:3px;line-height:1.3;">${subStr}</div>` : ''}
                                        <div style="font-size:12px;font-weight:800;color:#1e3a8a;">
                                            = ${st.result} <span style="font-size:10px;font-weight:600;color:#475569;">${st.unit || ''}</span>
                                        </div>
                                    </td>
                                </tr>`;
                    });

                    html += `
                            </tbody>
                        </table>
                    </div>`;
                }

                // Evaluations Table (DCR & Verdict)
                if (chap.evaluations && chap.evaluations.length > 0) {
                    html += `
                    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:8px 12px;margin-bottom:12px;">
                        <div style="font-size:10.5px;font-weight:700;color:#334155;margin-bottom:6px;">적합성 및 강도비(DCR) 검토</div>
                        <table style="width:100%;border-collapse:collapse;font-size:11px;">
                            <tbody>`;

                    chap.evaluations.forEach(ev => {
                        const evSafe = ev.status === 'OK' && ev.dcr <= 1.0001;
                        const eqMath = this.renderMath(ev.equation, false);

                        html += `
                                <tr style="border-bottom:1px solid #e2e8f0;line-height:1.5;">
                                    <td style="padding:5px 6px;width:30%;font-weight:600;color:#1e293b;">
                                        ${ev.title}
                                        ${ev.standard_ref ? `<span style="font-size:9.5px;color:#64748b;font-weight:normal;margin-left:4px;">[${ev.standard_ref}]</span>` : ''}
                                    </td>
                                    <td style="padding:5px 6px;width:35%;">
                                        <span style="font-family:KaTeX_Math, serif;">${eqMath}</span> : 
                                        <b>${ev.left_val}</b> vs <b>${ev.right_val}</b> ${ev.unit}
                                    </td>
                                    <td style="padding:5px 6px;width:20%;font-weight:700;color:${evSafe ? '#166534' : '#991b1b'};">
                                        DCR = ${Number(ev.dcr).toFixed(3)}
                                    </td>
                                    <td style="padding:5px 6px;width:15%;text-align:right;">
                                        <span style="padding:2px 8px;border-radius:4px;font-size:10px;font-weight:800;background:${evSafe ? '#dcfce7' : '#fee2e2'};color:${evSafe ? '#15803d' : '#b91c1c'};">
                                            ${ev.status}
                                        </span>
                                    </td>
                                </tr>`;
                    });

                    html += `
                            </tbody>
                        </table>
                    </div>`;
                }

                // Notes
                if (chap.notes && chap.notes.length > 0) {
                    html += `
                    <div style="font-size:10px;color:#64748b;background:#ffffff;border-left:3px solid #94a3b8;padding:4px 8px;margin-top:6px;">
                        ${chap.notes.map(n => `<div>ℹ️ ${n}</div>`).join('')}
                    </div>`;
                }

                html += `</section>`;
            });

            // Summary Table
            const allEvals = ast.all_evaluations || [];
            if (allEvals.length > 0) {
                html += `
                <section style="margin-top:28px;border-top:1.5px solid #0f172a;padding-top:14px;page-break-inside:avoid;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <h2 style="font-size:13.5px;font-weight:800;color:#0f172a;margin:0;">
                            종합 검토 결과 요약 (Executive Summary Table)
                        </h2>
                        <span style="font-size:10.5px;font-weight:600;color:#475569;">
                            총 ${allEvals.length}개 설계조건 전수 검증
                        </span>
                    </div>
                    <table style="width:100%;border-collapse:collapse;font-size:11px;border:1px solid #cbd5e1;">
                        <thead>
                            <tr style="background:#f1f5f9;border-bottom:1px solid #cbd5e1;text-align:center;font-size:10.5px;color:#334155;">
                                <th style="padding:6px;border:1px solid #cbd5e1;width:8%;">No.</th>
                                <th style="padding:6px;border:1px solid #cbd5e1;text-align:left;width:32%;">검토 항목</th>
                                <th style="padding:6px;border:1px solid #cbd5e1;width:25%;">소요값 (Demand)</th>
                                <th style="padding:6px;border:1px solid #cbd5e1;width:20%;">설계내력 (Capacity)</th>
                                <th style="padding:6px;border:1px solid #cbd5e1;width:15%;">DCR / 판정</th>
                            </tr>
                        </thead>
                        <tbody>`;

                allEvals.forEach((ev, i) => {
                    const evSafe = ev.status === 'OK' && ev.dcr <= 1.0001;
                    html += `
                            <tr style="border-bottom:1px solid #e2e8f0;text-align:center;">
                                <td style="padding:6px;border:1px solid #cbd5e1;color:#64748b;">${i + 1}</td>
                                <td style="padding:6px;border:1px solid #cbd5e1;text-align:left;font-weight:600;color:#0f172a;">${ev.title}</td>
                                <td style="padding:6px;border:1px solid #cbd5e1;">${ev.left_val} <span style="font-size:9.5px;color:#64748b;">${ev.unit}</span></td>
                                <td style="padding:6px;border:1px solid #cbd5e1;">${ev.right_val} <span style="font-size:9.5px;color:#64748b;">${ev.unit}</span></td>
                                <td style="padding:6px;border:1px solid #cbd5e1;font-weight:800;color:${evSafe ? '#166534' : '#991b1b'};">
                                    ${Number(ev.dcr).toFixed(3)}
                                    <span style="margin-left:4px;padding:1px 5px;border-radius:3px;font-size:9px;background:${evSafe ? '#dcfce7' : '#fee2e2'};color:${evSafe ? '#15803d' : '#b91c1c'};">${ev.status}</span>
                                </td>
                            </tr>`;
                });

                html += `
                        </tbody>
                    </table>
                </section>`;
            }

            // Footer
            html += `
                <div style="margin-top:32px;padding-top:12px;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;font-size:10px;color:#94a3b8;">
                    <div>AltDP_3rd Structural Engineering Automation System • Powered by AltDP-Core CalculationTracer</div>
                    <div>Page 1 of 1</div>
                </div>
            </div>`;

            return html;
        }
    }

    window.TracerReportRenderer = TracerReportRenderer;
})(window);
