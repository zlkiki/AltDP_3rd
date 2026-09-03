/**
 * AltDP_3rd KaTeX Formula Renderer & Formatter (report_katex.js)
 * Formats mathematical formulas for KDS structural calculations
 */
const ReportKaTeX = {
    /**
     * Render LaTeX string into HTML
     * @param {string} latex 
     * @param {boolean} displayMode 
     * @returns {string} HTML string
     */
    renderToString(latex, displayMode = false) {
        if (window.katex && typeof window.katex.renderToString === 'function') {
            try {
                return window.katex.renderToString(latex, {
                    displayMode: displayMode,
                    throwOnError: false
                });
            } catch (e) {
                console.warn('[ReportKaTeX] Rendering error:', e);
            }
        }
        // Fallback: Clean mathematical styling
        const modeClass = displayMode ? 'math-display' : 'math-inline';
        return `<span class="${modeClass}"><code>${latex}</code></span>`;
    },

    /**
     * Helper for standard KDS flexural equation
     */
    formulaPhiMn(phi, As, fy, d, a) {
        const latex = `\\phi M_n = \\phi A_s f_y \\left( d - \\frac{a}{2} \\right) = ${phi} \\times ${As} \\times ${fy} \\left( ${d} - \\frac{${a}}{2} \\right)`;
        return this.renderToString(latex, true);
    },

    /**
     * Helper for standard KDS shear equation
     */
    formulaPhiVn(phi, Vc, Vs) {
        const latex = `\\phi V_n = \\phi (V_c + V_s) = ${phi} \\times (${Vc} + ${Vs})`;
        return this.renderToString(latex, true);
    }
};

window.ReportKaTeX = ReportKaTeX;
