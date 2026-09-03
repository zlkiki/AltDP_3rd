// web/js/db/rebar_db.js
/**
 * KS D 3504 Deformed Rebar & Structural Bolt Standard Database
 */

const KS_REBAR_DB = [
    { name: 'D10', dia: 9.53, area: 71.33, perimeter: 30.0, weight: 0.560 },
    { name: 'D13', dia: 12.7, area: 126.7, perimeter: 40.0, weight: 0.995 },
    { name: 'D16', dia: 15.9, area: 198.6, perimeter: 50.0, weight: 1.560 },
    { name: 'D19', dia: 19.1, area: 286.5, perimeter: 60.0, weight: 2.250 },
    { name: 'D22', dia: 22.2, area: 387.1, perimeter: 70.0, weight: 3.040 },
    { name: 'D25', dia: 25.4, area: 506.7, perimeter: 80.0, weight: 3.980 },
    { name: 'D29', dia: 28.6, area: 642.4, perimeter: 90.0, weight: 5.040 },
    { name: 'D32', dia: 31.8, area: 794.2, perimeter: 100.0, weight: 6.230 },
    { name: 'D35', dia: 34.9, area: 956.6, perimeter: 110.0, weight: 7.510 },
    { name: 'D38', dia: 38.1, area: 1140.0, perimeter: 120.0, weight: 8.950 },
    { name: 'D41', dia: 41.3, area: 1340.0, perimeter: 130.0, weight: 10.36 },
    { name: 'D43', dia: 43.0, area: 1452.0, perimeter: 135.0, weight: 11.40 },
    { name: 'D51', dia: 50.8, area: 2027.0, perimeter: 160.0, weight: 15.91 },
    { name: 'D57', dia: 57.3, area: 2580.0, perimeter: 180.0, weight: 20.25 }
];

const KS_BOLT_DB = [
    { name: 'M16 (F10T)', size: 'M16', grade: 'F10T', dia: 16, holeDia: 18, nominalArea: 201, tensileArea: 157, designShear: 55.4, designTens: 89.5 },
    { name: 'M20 (F10T)', size: 'M20', grade: 'F10T', dia: 20, holeDia: 22, nominalArea: 314, tensileArea: 245, designShear: 86.5, designTens: 139.7 },
    { name: 'M22 (F10T)', size: 'M22', grade: 'F10T', dia: 22, holeDia: 24, nominalArea: 380, tensileArea: 303, designShear: 107.0, designTens: 172.7 },
    { name: 'M24 (F10T)', size: 'M24', grade: 'F10T', dia: 24, holeDia: 27, nominalArea: 452, tensileArea: 353, designShear: 124.6, designTens: 201.2 },
    { name: 'M30 (F10T)', size: 'M30', grade: 'F10T', dia: 30, holeDia: 33, nominalArea: 707, tensileArea: 561, designShear: 198.0, designTens: 319.8 },
    { name: 'M20 (F13T)', size: 'M20', grade: 'F13T', dia: 20, holeDia: 22, nominalArea: 314, tensileArea: 245, designShear: 112.5, designTens: 181.6 },
    { name: 'M22 (F13T)', size: 'M22', grade: 'F13T', dia: 22, holeDia: 24, nominalArea: 380, tensileArea: 303, designShear: 139.1, designTens: 224.5 },
    { name: 'M24 (F13T)', size: 'M24', grade: 'F13T', dia: 24, holeDia: 27, nominalArea: 452, tensileArea: 353, designShear: 162.0, designTens: 261.6 }
];

function getRebarInfo(val) {
    if (!val) return null;
    const s = String(val).trim().toUpperCase();
    return KS_REBAR_DB.find(r => r.name === s || r.name === `D${s}` || String(r.dia) === s || String(parseInt(s, 10)) === r.name.substring(1)) || null;
}

function getBoltInfo(val) {
    if (!val) return null;
    const s = String(val).trim().toUpperCase();
    return KS_BOLT_DB.find(b => b.name.toUpperCase().includes(s) || b.size === s) || null;
}

window.KS_REBAR_DB = KS_REBAR_DB;
window.KS_BOLT_DB = KS_BOLT_DB;
window.getRebarInfo = getRebarInfo;
window.getBoltInfo = getBoltInfo;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { KS_REBAR_DB, KS_BOLT_DB, getRebarInfo, getBoltInfo };
}