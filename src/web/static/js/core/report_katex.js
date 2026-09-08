/**
 * AltDP_3rd KaTeX Formula Renderer & Formatter (report_katex.js)
 * Conforms to Requirement 21-5 & DOCS 14 Structural Calculation Math Specifications
 * - High-Fidelity KaTeX vector math rendering
 * - Automatic inline ($...$) and block ($$...$$) equation parsing across document trees
 * - Zero-failure offline / fallback math engine for standalone intranet environments
 */

(function(window) {
    'use strict';

    const ReportKaTeX = {
        /**
         * Render LaTeX string into HTML string
         * @param {string} latex 
         * @param {boolean} displayMode 
         * @returns {string} HTML string
         */
        renderToString(latex, displayMode = false) {
            if (!latex) return '';
            const cleanLatex = latex.trim();

            if (window.katex && typeof window.katex.renderToString === 'function') {
                try {
                    return window.katex.renderToString(cleanLatex, {
                        displayMode: displayMode,
                        throwOnError: false
                    });
                } catch (e) {
                    console.warn('[ReportKaTeX] KaTeX rendering error, falling back:', e);
                }
            }

            // Fallback: High quality semantic math HTML
            return this.formatMathFallback(cleanLatex, displayMode);
        },

        /**
         * Render all mathematical formulas ($...$ and $$...$$) inside a DOM element
         * @param {HTMLElement} element 
         */
        renderElement(element) {
            if (!element) return;

            // 1. If official KaTeX auto-render extension is loaded
            if (window.renderMathInElement && typeof window.renderMathInElement === 'function') {
                try {
                    window.renderMathInElement(element, {
                        delimiters: [
                            { left: '$$', right: '$$', display: true },
                            { left: '$', right: '$', display: false }
                        ],
                        throwOnError: false
                    });
                    return;
                } catch (err) {
                    console.warn('[ReportKaTeX] renderMathInElement failed, using internal parser:', err);
                }
            }

            // 2. Internal recursive text parser (handles both KaTeX present & offline fallback)
            this._parseAndRenderMathInTree(element);
        },

        /**
         * Parse and replace $...$ and $$...$$ directly in DOM text nodes
         * @param {HTMLElement} root 
         */
        _parseAndRenderMathInTree(root) {
            const mathRegex = /(\$\$[\s\S]+?\$\$|\$[^\$\n]+?\$)/g;
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
                acceptNode(node) {
                    // Skip script, style, or already rendered elements
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    const tag = parent.tagName.toLowerCase();
                    if (tag === 'script' || tag === 'style' || tag === 'code' || tag === 'pre') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    if (parent.classList.contains('katex') || parent.classList.contains('math-rendered')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return mathRegex.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
                }
            });

            const nodesToReplace = [];
            let currentNode;
            while ((currentNode = walker.nextNode())) {
                nodesToReplace.push(currentNode);
            }

            nodesToReplace.forEach(textNode => {
                const text = textNode.nodeValue;
                const frag = document.createDocumentFragment();
                let lastIdx = 0;
                let match;
                mathRegex.lastIndex = 0;

                while ((match = mathRegex.exec(text)) !== null) {
                    const matchStart = match.index;
                    const matchedStr = match[0];

                    // Text preceding math
                    if (matchStart > lastIdx) {
                        frag.appendChild(document.createTextNode(text.substring(lastIdx, matchStart)));
                    }

                    const isBlock = matchedStr.startsWith('$$') && matchedStr.endsWith('$$');
                    const latex = isBlock ? matchedStr.slice(2, -2).trim() : matchedStr.slice(1, -1).trim();

                    const span = document.createElement('span');
                    span.className = isBlock ? 'math-block-rendered math-rendered' : 'math-inline-rendered math-rendered';
                    span.innerHTML = this.renderToString(latex, isBlock);
                    frag.appendChild(span);

                    lastIdx = matchStart + matchedStr.length;
                }

                if (lastIdx < text.length) {
                    frag.appendChild(document.createTextNode(text.substring(lastIdx)));
                }

                if (textNode.parentNode) {
                    textNode.parentNode.replaceChild(frag, textNode);
                }
            });
        },

        /**
         * Offline semantic math HTML generator for zero-CDN/intranet resilience
         * @param {string} latex 
         * @param {boolean} displayMode 
         * @returns {string} Clean HTML
         */
        formatMathFallback(latex, displayMode = false) {
            let s = latex;

            // 1. Common engineering fraction: \frac{A}{B}
            s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, (match, num, den) => {
                return `<span class="math-frac"><span class="math-num">${num}</span><span class="math-bar">/</span><span class="math-den">${den}</span></span>`;
            });

            // 2. Greek Letters
            s = s.replace(/\\beta/g, 'β')
                 .replace(/\\epsilon/g, 'ε')
                 .replace(/\\phi/g, 'φ')
                 .replace(/\\lambda/g, 'λ')
                 .replace(/\\alpha/g, 'α')
                 .replace(/\\gamma/g, 'γ')
                 .replace(/\\theta/g, 'θ')
                 .replace(/\\sigma/g, 'σ')
                 .replace(/\\Delta/g, 'Δ');

            // 3. Mathematical operators & relations
            s = s.replace(/\\le/g, '≤')
                 .replace(/\\ge/g, '≥')
                 .replace(/\\ne/g, '≠')
                 .replace(/\\times/g, '×')
                 .replace(/\\cdot/g, '·')
                 .replace(/\\pm/g, '±')
                 .replace(/\\quad/g, '&nbsp;&nbsp;')
                 .replace(/\\qquad/g, '&nbsp;&nbsp;&nbsp;&nbsp;');

            // 4. Text and formatting macros
            s = s.replace(/\\text\{([^{}]+)\}/g, '$1')
                 .replace(/\\mathbf\{([^{}]+)\}/g, '<b>$1</b>')
                 .replace(/\\mathit\{([^{}]+)\}/g, '<i>$1</i>')
                 .replace(/\\left\(/g, '(')
                 .replace(/\\right\)/g, ')')
                 .replace(/\\left\[/g, '[')
                 .replace(/\\right\]/g, ']');

            // 5. Square root
            s = s.replace(/\\sqrt\{([^{}]+)\}/g, '√($1)');

            // 6. Subscripts: _{...} or _X
            s = s.replace(/_\{([^{}]+)\}/g, '<sub>$1</sub>')
                 .replace(/_([a-zA-Z0-9])/g, '<sub>$1</sub>');

            // 7. Superscripts: ^{...} or ^X
            s = s.replace(/\^\{([^{}]+)\}/g, '<sup>$1</sup>')
                 .replace(/\^([a-zA-Z0-9])/g, '<sup>$1</sup>');

            const modeClass = displayMode ? 'math-display-fallback' : 'math-inline-fallback';
            return `<span class="${modeClass}" style="font-family:'Times New Roman', Cambria, Georgia, serif;${displayMode ? 'display:block;text-align:center;margin:6px 0;' : ''}">${s}</span>`;
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

})(window);
