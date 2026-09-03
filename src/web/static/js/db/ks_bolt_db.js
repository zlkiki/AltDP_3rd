// web/js/db/ks_bolt_db.js
/**
 * KS Standard Bolts Single Source of Truth (SSOT) Database
 * Ref: KS B 1010, KS B 0233, KS B 1016, KDS 14 31 25.
 */

(function () {
    // 1. KS Bolt Diameter & Geometric Properties (M16 ~ M36)
    const KS_BOLT_DIA_DB = [
        { size: 'M16', dia: 16, nominalArea: 201.1, tensileArea: 157.0, holeDia: 18, edgeDistMin: 28, pitchMin: 48, name: 'M16 (Ø16mm, 홀 18mm)' },
        { size: 'M20', dia: 20, nominalArea: 314.2, tensileArea: 245.0, holeDia: 22, edgeDistMin: 34, pitchMin: 60, name: 'M20 (Ø20mm, 홀 22mm)' },
        { size: 'M22', dia: 22, nominalArea: 380.1, tensileArea: 303.0, holeDia: 24, edgeDistMin: 38, pitchMin: 66, name: 'M22 (Ø22mm, 홀 24mm)' },
        { size: 'M24', dia: 24, nominalArea: 452.4, tensileArea: 353.0, holeDia: 27, edgeDistMin: 42, pitchMin: 72, name: 'M24 (Ø24mm, 홀 27mm)' },
        { size: 'M27', dia: 27, nominalArea: 572.6, tensileArea: 459.0, holeDia: 30, edgeDistMin: 48, pitchMin: 81, name: 'M27 (Ø27mm, 홀 30mm)' },
        { size: 'M30', dia: 30, nominalArea: 706.9, tensileArea: 561.0, holeDia: 33, edgeDistMin: 52, pitchMin: 90, name: 'M30 (Ø30mm, 홀 33mm)' },
        { size: 'M36', dia: 36, nominalArea: 1017.9, tensileArea: 817.0, holeDia: 39, edgeDistMin: 64, pitchMin: 108, name: 'M36 (Ø36mm, 홀 39mm)' }
    ];

    // 2. KS High-Strength Bolt Grades (F8T, F10T, F13T, S10T, A325, A490)
    const KS_HIGH_BOLT_GRADE_DB = [
        {
            grade: 'F10T',
            name: 'F10T (KS B 1010 표준 고력볼트 Fy=900, Fu=1000)',
            Fy: 900,
            Fu: 1000,
            pretension_Tb: { 16: 100.0, 20: 165.0, 22: 205.0, 24: 240.0, 27: 310.0, 30: 380.0, 36: 550.0 }
        },
        {
            grade: 'S10T',
            name: 'S10T (토크셔 T/S 볼트 Fy=900, Fu=1000)',
            Fy: 900,
            Fu: 1000,
            pretension_Tb: { 16: 100.0, 20: 165.0, 22: 205.0, 24: 240.0, 27: 310.0, 30: 380.0, 36: 550.0 }
        },
        {
            grade: 'F13T',
            name: 'F13T (KS B 1010 초고력볼트 Fy=1170, Fu=1300)',
            Fy: 1170,
            Fu: 1300,
            pretension_Tb: { 20: 215.0, 22: 265.0, 24: 310.0, 27: 400.0, 30: 495.0 }
        },
        {
            grade: 'F8T',
            name: 'F8T (KS B 1010 8T 고력볼트 Fy=640, Fu=800)',
            Fy: 640,
            Fu: 800,
            pretension_Tb: { 16: 80.0, 20: 130.0, 22: 165.0, 24: 190.0, 27: 250.0, 30: 305.0, 36: 440.0 }
        },
        {
            grade: 'A325',
            name: 'ASTM A325 (고력볼트 Fy=630, Fu=830)',
            Fy: 630,
            Fu: 830,
            pretension_Tb: { 16: 85.0, 20: 142.0, 22: 176.0, 24: 205.0, 27: 267.0, 30: 326.0 }
        },
        {
            grade: 'A490',
            name: 'ASTM A490 (초고력볼트 Fy=895, Fu=1035)',
            Fy: 895,
            Fu: 1035,
            pretension_Tb: { 16: 107.0, 20: 179.0, 22: 221.0, 24: 257.0, 27: 334.0, 30: 408.0 }
        }
    ];

    // 3. KS Ordinary Hex Bolt Grades (4.6, 4.8, 8.8, 10.9)
    const KS_ORDINARY_BOLT_GRADE_DB = [
        { grade: '4.6', name: '강도구분 4.6 (일반 육각볼트 Fy=240, Fu=400)', Fy: 240, Fu: 400 },
        { grade: '4.8', name: '강도구분 4.8 (일반 육각볼트 Fy=320, Fu=400)', Fy: 320, Fu: 400 },
        { grade: '8.8', name: '강도구분 8.8 (중강도 구조용볼트 Fy=640, Fu=800)', Fy: 640, Fu: 800 },
        { grade: '10.9', name: '강도구분 10.9 (고강도 볼트 Fy=900, Fu=1000)', Fy: 900, Fu: 1000 }
    ];

    // 4. KS Anchor Bolt Grades (SS275, SM355, SS400, Gr.55, Gr.105)
    const KS_ANCHOR_BOLT_GRADE_DB = [
        { grade: 'SS275', name: 'SS275 (일반구조용 앵커볼트 Fy=275, Fu=410)', Fy: 275, Fu: 410 },
        { grade: 'SM355', name: 'SM355 (고강도 구조용 앵커볼트 Fy=355, Fu=490)', Fy: 355, Fu: 490 },
        { grade: 'SS400', name: 'SS400 (구규격 일반 앵커볼트 Fy=235, Fu=400)', Fy: 235, Fu: 400 },
        { grade: 'Gr.55', name: 'ASTM F1554 Gr.55 (고강도 앵커볼트 Fy=380, Fu=517)', Fy: 380, Fu: 517 },
        { grade: 'Gr.105', name: 'ASTM F1554 Gr.105 (초고강도 앵커볼트 Fy=724, Fu=862)', Fy: 724, Fu: 862 }
    ];

    // Unified Bolt Grade List for Selection
    const KS_ALL_BOLT_GRADE_DB = [
        ...KS_HIGH_BOLT_GRADE_DB,
        ...KS_ORDINARY_BOLT_GRADE_DB,
        ...KS_ANCHOR_BOLT_GRADE_DB
    ];

    // Helper functions
    function getBoltDiaInfo(val) {
        if (!val) return null;
        const s = String(val).trim().toUpperCase();
        return KS_BOLT_DIA_DB.find(b => b.size === s || b.size === `M${s}` || String(b.dia) === s || String(parseInt(s, 10)) === b.size.substring(1)) || null;
    }

    function getBoltGradeInfo(val) {
        if (!val) return null;
        const s = String(val).trim().toUpperCase();
        return KS_ALL_BOLT_GRADE_DB.find(g => g.grade.toUpperCase() === s) || null;
    }

    // Window Global Exports
    window.KS_BOLT_DIA_DB = KS_BOLT_DIA_DB;
    window.KS_HIGH_BOLT_GRADE_DB = KS_HIGH_BOLT_GRADE_DB;
    window.KS_ORDINARY_BOLT_GRADE_DB = KS_ORDINARY_BOLT_GRADE_DB;
    window.KS_ANCHOR_BOLT_GRADE_DB = KS_ANCHOR_BOLT_GRADE_DB;
    window.KS_ALL_BOLT_GRADE_DB = KS_ALL_BOLT_GRADE_DB;
    window.getBoltDiaInfo = getBoltDiaInfo;
    window.getBoltGradeInfo = getBoltGradeInfo;

    // Legacy Compatibility
    window.KS_BOLT_DB = KS_BOLT_DIA_DB;
})();
