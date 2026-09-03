// web/js/report/redcr/reportUnitTransform.js
/**
 * AltDP Member Designer - Universal Canonical Report Localizer
 * 
 * Converts standard Canonical SI calculation sheets (mm, m, kN, kN·m, MPa, kPa, etc.)
 * to the currently active display unit system (SI, SI_M, MKS, US) safely across HTML structures.
 */

(function () {
    const NUM = '([+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?)';
    const MULT_OP = '(?:\\s*(?:[×x*X]|&times;)\\s*)';

    function formatUnitNumber(value, digits = 2) {
        if (!Number.isFinite(value)) return '—';
        if (Object.is(value, -0) || value === 0) return '0';
        const abs = Math.abs(value);
        if (abs >= 1e9 || (abs < 10 ** -digits && abs > 0)) {
            return value.toExponential(digits);
        }
        const fixed = value.toFixed(digits);
        return parseFloat(fixed).toString() === fixed ? fixed : Number(fixed).toString();
    }

    /**
     * Localizes a canonical HTML calculation sheet to the target Unit System.
     * @param {string} html Raw calculation sheet HTML in canonical units
     * @param {string|object} sysIdOrObj Unit system ID ('SI', 'SI_M', 'MKS', 'US') or UnitManager system object
     * @returns {string} Localized HTML
     */
    function localizeCanonicalReportHtml(html, sysIdOrObj) {
        if (!html || typeof html !== 'string') return html || '';
        
        let sys = null;
        if (window.UnitManager) {
            if (typeof sysIdOrObj === 'string') {
                sys = window.UnitManager.getPresets().find(p => p.id === sysIdOrObj) || window.UnitManager.getCurrentSystem();
            } else if (sysIdOrObj && sysIdOrObj.id) {
                sys = sysIdOrObj;
            } else {
                sys = window.UnitManager.getCurrentSystem();
            }
        }

        // If SI, canonical is native, return unchanged
        if (!sys || sys.id === 'SI') {
            return html;
        }

        const forceLabel = sys.force;
        const lengthLabel = sys.length;
        const momentLabel = `${sys.momentForce}·${sys.momentLength}`;
        const stressLabel = sys.id === 'MKS' ? 'kgf/cm²' : (sys.id === 'US' ? 'ksi' : (sys.id === 'SI_M' ? 'kPa' : 'MPa'));
        const areaLoadLabel = `${sys.areaLoadForce}/${sys.areaLoadLength}²`;
        const lineLoadLabel = `${sys.force}/${sys.length}`;
        const lengthMLabel = sys.length === 'in' ? 'ft' : 'm';

        // Helper conversions from canonical SI
        const cvForce = (kN) => window.UnitManager.fromCanonical(kN, 'force');
        const cvLength = (mm) => window.UnitManager.fromCanonical(mm, 'length');
        const cvLengthM = (m) => window.UnitManager.fromCanonical(m, 'length_m');
        const cvMoment = (kNm) => window.UnitManager.fromCanonical(kNm, 'moment');
        const cvStress = (MPa) => window.UnitManager.fromCanonical(MPa, 'stress');
        const cvAreaLoad = (kNm2) => window.UnitManager.fromCanonical(kNm2, 'areaLoad');
        const cvArea = (mm2) => window.UnitManager.fromCanonical(mm2, 'area');

        // Token placeholder management
        let tokenId = 0;
        const tokenMap = new Map();
        const hold = (replacement) => {
            const key = `___ALTD_UNIT_TOKEN_${tokenId++}___`;
            tokenMap.set(key, replacement);
            return key;
        };

        let result = html;

        // 1. Convert cross-cell dimension patterns (2D / 3D section sizes: 600 × 600 mm, 400 × 600 × 300 mm)
        const dim2CellRegex = new RegExp(`(<td[^>]*>\\s*)${NUM}${MULT_OP}${NUM}(\\s*</td>\\s*<td[^>]*>\\s*)(?:mm|cm|m|in)(\\s*</td>)`, 'gi');
        result = result.replace(dim2CellRegex, (_m, td1, n1, n2, td2, td3) => {
            const v1 = formatUnitNumber(cvLength(Number(n1)), 1);
            const v2 = formatUnitNumber(cvLength(Number(n2)), 1);
            return hold(`${td1}${v1} × ${v2}${td2}${lengthLabel}${td3}`);
        });

        const dim3CellRegex = new RegExp(`(<td[^>]*>\\s*)${NUM}${MULT_OP}${NUM}${MULT_OP}${NUM}(\\s*</td>\\s*<td[^>]*>\\s*)(?:mm|cm|m|in)(\\s*</td>)`, 'gi');
        result = result.replace(dim3CellRegex, (_m, td1, n1, n2, n3, td2, td3) => {
            const v1 = formatUnitNumber(cvLength(Number(n1)), 1);
            const v2 = formatUnitNumber(cvLength(Number(n2)), 1);
            const v3 = formatUnitNumber(cvLength(Number(n3)), 1);
            return hold(`${td1}${v1} × ${v2} × ${v3}${td2}${lengthLabel}${td3}`);
        });

        // 2. Single-value cross-cell patterns (<td class="inp-val">400</td><td class="inp-unit">mm</td>)
        const cellUnitConfigs = [
            { pattern: 'kN/m(?:&sup2;|²)', convert: cvAreaLoad, label: areaLoadLabel, digits: 2 },
            { pattern: 'kN(?:·m|&middot;m)', convert: cvMoment, label: momentLabel, digits: 2 },
            { pattern: 'N/mm(?:&sup2;|²)', convert: cvStress, label: stressLabel, digits: 2 },
            { pattern: 'MPa', convert: cvStress, label: stressLabel, digits: 2 },
            { pattern: 'kPa', convert: v => cvAreaLoad(v / 1000), label: areaLoadLabel, digits: 2 },
            { pattern: 'kN', convert: cvForce, label: forceLabel, digits: 2 },
            { pattern: 'mm(?:&sup2;|²)', convert: cvArea, label: `${lengthLabel}²`, digits: 1 },
            { pattern: 'mm', convert: cvLength, label: lengthLabel, digits: 1 },
            { pattern: 'm', convert: cvLengthM, label: lengthMLabel, digits: 2 }
        ];

        cellUnitConfigs.forEach(({ pattern, convert, label, digits }) => {
            const regex = new RegExp(`(<td[^>]*>\\s*)${NUM}(\\s*</td>\\s*<td[^>]*>\\s*)${pattern}(\\s*</td>)`, 'gi');
            result = result.replace(regex, (_match, td1, numStr, td2, td3) => {
                const num = Number(numStr);
                if (isNaN(num)) return _match;
                const converted = convert(num);
                return hold(`${td1}${formatUnitNumber(converted, digits)}${td2}${label}${td3}`);
            });
        });

        // 3. Tag-wrapped numbers before units: <b>NUMBER</b> UNIT or <span>NUMBER</span> UNIT
        cellUnitConfigs.forEach(({ pattern, convert, label, digits }) => {
            const regex = new RegExp(`(<(?:b|span|strong)[^>]*>\\s*)${NUM}(\\s*</(?:b|span|strong)>\\s*)${pattern}`, 'gi');
            result = result.replace(regex, (_match, tagOpen, numStr, tagClose) => {
                const num = Number(numStr);
                if (isNaN(num)) return _match;
                const converted = convert(num);
                return hold(`${tagOpen}${formatUnitNumber(converted, digits)}${tagClose} ${label}`);
            });
        });

        // 4. In-text composite dimensions: "600 × 600 mm", "b = 600 mm", "h = 600 mm"
        const dim2TextRegex = new RegExp(`\\b${NUM}${MULT_OP}${NUM}\\s*mm\\b`, 'gi');
        result = result.replace(dim2TextRegex, (_m, n1, n2) => {
            const v1 = formatUnitNumber(cvLength(Number(n1)), 1);
            const v2 = formatUnitNumber(cvLength(Number(n2)), 1);
            return hold(`${v1} × ${v2} ${lengthLabel}`);
        });

        // 5. In-text single NUMBER UNIT nodes (safely excluding style/script/html tags)
        const protectTagsRegex = /(<style\b[^>]*>[\s\S]*?<\/style>|<script\b[^>]*>[\s\S]*?<\/script>|<[^>]+>)/gi;
        result = result.split(protectTagsRegex).map((part, index) => {
            if (index % 2 === 1) return part; // Keep HTML tags unmodified

            let text = part;
            cellUnitConfigs.forEach(({ pattern, convert, label, digits }) => {
                const regex = new RegExp(`${NUM}\\s*${pattern}`, 'gi');
                text = text.replace(regex, (_match, numStr) => {
                    const num = Number(numStr);
                    if (isNaN(num)) return _match;
                    const converted = convert(num);
                    return hold(`${formatUnitNumber(converted, digits)} ${label}`);
                });
            });

            // Replace remaining bare unit labels in text
            text = text.replace(/kN\/m(?:&sup2;|²)/gi, areaLoadLabel);
            text = text.replace(/kN(?:·m|&middot;m)/gi, momentLabel);
            text = text.replace(/N\/mm(?:&sup2;|²)/gi, stressLabel);
            text = text.replace(/\bMPa\b/gi, stressLabel);
            text = text.replace(/\bkPa\b/gi, areaLoadLabel);
            text = text.replace(/\bkN\b/gi, forceLabel);
            text = text.replace(/mm(?:&sup2;|²)/gi, `${lengthLabel}²`);
            text = text.replace(/\bmm\b/gi, lengthLabel);

            return text;
        }).join('');

        // Restore all hold tokens
        for (const [token, value] of tokenMap) {
            result = result.replaceAll(token, value);
        }

        return result;
    }

    // Expose globally
    window.RedcrReportUnitTransform = {
        localizeCanonicalReportHtml,
        formatUnitNumber
    };
    window.localizeCanonicalReportHtml = localizeCanonicalReportHtml;
})();
