// web/js/report/redcr/common/formatHelpers.js
/**
 * AltDP Member Designer - Report Common Format Helpers
 * Zero-Build Vanilla JavaScript & Browser Global Namespace
 */

(function () {
    /** 일반 숫자 포매팅 — 소수 d자리. +Infinity → 'INF', NaN/기타 비정상 → '—' */
    function nf(v, d = 3) {
        if (v === Number.POSITIVE_INFINITY) return 'INF';
        if (v === Number.NEGATIVE_INFINITY) return '-INF';
        if (v === null || v === undefined || !Number.isFinite(Number(v))) return '—';
        return Number(v).toFixed(d);
    }

    /** HTML escape */
    function esc(s) {
        if (s === null || s === undefined) return '';
        return String(s).replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    /** OK/NG 태그 */
    function okNg(pass) {
        if (pass === true || pass === 'OK' || pass === 'PASS')
            return '<span class="pass">OK ✓</span>';
        if (pass === false || pass === 'NG' || pass === 'FAIL')
            return '<span class="fail">NG ✗</span>';
        return '<span style="color:#888">—</span>';
    }

    /** DCR 색상 반환 */
    function dcrColor(dcr) {
        const val = Number(dcr);
        if (!Number.isFinite(val)) return '#888888';
        if (val <= 0.85) return '#1a7a4a'; // safe green
        if (val <= 1.0) return '#b26a00';  // warning orange
        return '#b00020';                  // exceed red
    }

    /** 단위 포함 숫자 포맷 */
    function nfu(v, unit, d = 2) {
        return `${nf(v, d)} ${unit}`;
    }

    const FormatHelpers = {
        nf,
        esc,
        okNg,
        dcrColor,
        nfu
    };

    if (typeof window !== 'undefined') {
        window.RedcrCommon = window.RedcrCommon || {};
        window.RedcrCommon.formatHelpers = FormatHelpers;
        // 편리한 단축 별칭
        window.RedcrFormat = FormatHelpers;
    }
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = FormatHelpers;
    }
})();
