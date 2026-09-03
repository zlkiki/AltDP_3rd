// web/js/designer/auto_designer.js
/**
 * AltDP Member Designer - Auto Optimal Design Engine
 * Automatically searches for compliant parameters (All DCR <= 1.0)
 * - RC: Optimizes main rebar count/layer (Top/Bot) & stirrup spacing
 * - Steel: Searches KS H-beam DB for the lightest compliant section
 * - Connections: Optimizes plate thickness & bolt count
 */

const get_KS_H_BEAM_DB = () => (typeof window !== 'undefined' && window.KS_H_BEAM_DB) ? window.KS_H_BEAM_DB : [];
const get_KS_REBAR_DB = () => (typeof window !== 'undefined' && window.KS_REBAR_DB) ? window.KS_REBAR_DB : [];
const get_KS_BOLT_DB = () => (typeof window !== 'undefined' && window.KS_BOLT_DB) ? window.KS_BOLT_DB : [];

const AutoDesigner = {

    /**
     * Executes automatic optimization for the active module and inputs
     * @param {string} moduleKey e.g. 'rc/beam/base'
     * @param {Object} currentInputs Current form inputs
     * @param {Function} evaluateFn Async function (inputs) => Promise<result>
     * @returns {Promise<{ success: boolean, updatedInputs: Object, message: string }>}
     */
    async optimize(moduleKey, currentInputs, evaluateFn) {
        const [cat, grp, modId] = moduleKey.split('/');
        const inputs = { ...currentInputs };

        // 1. RC Beam & Column Optimization (Optimize rebar count and stirrup spacing)
        if (cat === 'rc' && (grp === 'beam' || grp === 'column')) {
            return await this.optimizeRcMember(moduleKey, inputs, evaluateFn);
        }

        // 2. RC Slab Optimization (Optimize main rebar spacing and thickness)
        if (cat === 'rc' && grp === 'slab') {
            return await this.optimizeRcSlab(moduleKey, inputs, evaluateFn);
        }

        // 3. RC Footing Optimization (Optimize B, L, H dimensions and bar spacing)
        if (cat === 'rc' && grp === 'footing') {
            return await this.optimizeRcFooting(moduleKey, inputs, evaluateFn);
        }

        // 4. Steel Member Optimization (Search lightest KS H-Beam section)
        if (cat === 'steel' && grp === 'member') {
            return await this.optimizeSteelMember(moduleKey, inputs, evaluateFn);
        }

        // 5. Steel Connection Optimization (Baseplate / Bolts)
        if (cat === 'steel' && grp === 'connection') {
            return await this.optimizeSteelConnection(moduleKey, inputs, evaluateFn);
        }

        // 6. Generic / Other modules
        return await this.genericOptimize(moduleKey, inputs, evaluateFn);
    },

    async optimizeRcSlab(moduleKey, inputs, evaluateFn) {
        const candidateSpacings = [250, 200, 150, 125, 100];
        const candidateThk = [150, 180, 200, 220, 250, 300];

        for (const thk of candidateThk) {
            for (const sp of candidateSpacings) {
                const testInputs = { ...inputs, thickness: thk, main_spacing: sp };
                try {
                    const res = await evaluateFn(testInputs);
                    const dcr = Number(res?.governing_dcr) || 0.0;
                    if (dcr > 0 && dcr <= 1.0 && (res.status === 'OK' || res.status === 'PASS')) {
                        return {
                            success: true,
                            updatedInputs: testInputs,
                            message: `[슬래브 최적설계] 두께: ${thk}mm, 주철근 간격: @${sp}mm (최대 DCR: ${dcr.toFixed(3)})`
                        };
                    }
                } catch (e) {}
            }
        }
        return await this.genericOptimize(moduleKey, inputs, evaluateFn);
    },

    async optimizeRcFooting(moduleKey, inputs, evaluateFn) {
        const sizeCandidates = [1800, 2000, 2200, 2500, 2800, 3000, 3500];
        const thkCandidates = [500, 600, 700, 800, 900, 1000];

        for (const sz of sizeCandidates) {
            for (const h of thkCandidates) {
                const testInputs = { ...inputs, B: sz, L: sz, H: h, bar_spacing: 150 };
                try {
                    const res = await evaluateFn(testInputs);
                    const dcr = Number(res?.governing_dcr) || 0.0;
                    if (dcr > 0 && dcr <= 1.0 && (res.status === 'OK' || res.status === 'PASS')) {
                        return {
                            success: true,
                            updatedInputs: testInputs,
                            message: `[독립기초 최적설계] 크기: ${sz}x${sz}mm, 두께: ${h}mm (최대 DCR: ${dcr.toFixed(3)})`
                        };
                    }
                } catch (e) {}
            }
        }
        return await this.genericOptimize(moduleKey, inputs, evaluateFn);
    },

    async optimizeRcMember(moduleKey, inputs, evaluateFn) {
        const candidateBars = [2, 3, 4, 5, 6, 8, 10];
        const candidateSpacing = [300, 250, 200, 150, 100, 75];

        let bestInputs = null;
        let lowestDcr = 999;
        let isCompliant = false;

        // Try increasing top/bot rebar bars
        for (const nb of candidateBars) {
            for (const sp of candidateSpacing) {
                const testInputs = { ...inputs };
                if (testInputs.top_bars !== undefined) testInputs.top_bars = nb;
                if (testInputs.bot_bars !== undefined) testInputs.bot_bars = nb;
                if (testInputs.rebar_count !== undefined) testInputs.rebar_count = Math.max(nb * 2, 4);
                if (testInputs.s !== undefined) testInputs.s = sp;
                if (testInputs.stirrup_spacing !== undefined) testInputs.stirrup_spacing = sp;

                try {
                    const res = await evaluateFn(testInputs);
                    const dcr = Number(res?.governing_dcr) || Number(res?.max_dcr) || 0.0;

                    if (dcr > 0 && dcr < lowestDcr) {
                        lowestDcr = dcr;
                        bestInputs = { ...testInputs };
                    }

                    if (dcr > 0 && dcr <= 1.0 && (res.status === 'OK' || res.status === 'PASS')) {
                        isCompliant = true;
                        return {
                            success: true,
                            updatedInputs: testInputs,
                            message: `[RC 최적설계 성공] 주철근: ${nb}개, 스터럽 간격: ${sp}mm (최대 DCR: ${dcr.toFixed(3)})`
                        };
                    }
                } catch (e) {
                    console.warn('Optimization evaluation step failed:', e);
                }
            }
        }

        if (bestInputs && lowestDcr < 999) {
            return {
                success: isCompliant,
                updatedInputs: bestInputs,
                message: isCompliant 
                    ? `[최적 설계 완료] 모든 한계상태 만족 (DCR: ${lowestDcr.toFixed(3)})`
                    : `[설계 제안] 배근량을 최대로 증대하였으나 DCR ${lowestDcr.toFixed(3)}로 단면 크기(b, h) 증대를 권장합니다.`
            };
        }

        return {
            success: false,
            updatedInputs: inputs,
            message: `자동 최적 배근 탐색에 실패하였습니다. 수동 조정을 권장합니다.`
        };
    },

    async optimizeSteelMember(moduleKey, inputs, evaluateFn) {
        const beamDb = get_KS_H_BEAM_DB();
        if (!beamDb || beamDb.length === 0) {
            return { success: false, updatedInputs: inputs, message: 'KS 강재 DB를 불러올 수 없습니다.' };
        }

        // Sort by weight ascending (lightest first for economic design)
        const sortedSections = [...beamDb].sort((a, b) => (a.weight || a.A) - (b.weight || b.A));


        for (const sec of sortedSections) {
            const testInputs = {
                ...inputs,
                section_name: sec.name,
                b: sec.bf,
                bf: sec.bf,
                h: sec.h,
                d: sec.h,
                tw: sec.tw,
                tf: sec.tf,
                r: sec.r || 13,
                A: sec.A,
                Ix: sec.Ix * 10000,
                Iy: sec.Iy * 10000,
                Zx: sec.Zx * 1000,
                Zy: sec.Zy * 1000
            };

            try {
                const res = await evaluateFn(testInputs);
                const dcr = Number(res?.governing_dcr) || 0.0;
                if (dcr > 0 && dcr <= 1.0 && (res.status === 'OK' || res.status === 'PASS')) {
                    return {
                        success: true,
                        updatedInputs: testInputs,
                        message: `[Steel 최적 단면 선정] ${sec.name} (중량: ${sec.weight}kg/m, DCR: ${dcr.toFixed(3)})`
                    };
                }
            } catch (e) {
                // Continue searching
            }
        }

        return {
            success: false,
            updatedInputs: inputs,
            message: `KS H형강 DB 내에서 만족하는 단면을 찾지 못했습니다. 상위 규격 또는 강재 강도 상향을 제안합니다.`
        };
    },

    async optimizeSteelConnection(moduleKey, inputs, evaluateFn) {
        const thicknessCandidates = [12, 16, 20, 25, 28, 32, 36, 40, 45, 50];
        const boltCountCandidates = [4, 6, 8, 10, 12];

        for (const t of thicknessCandidates) {
            for (const nb of boltCountCandidates) {
                const testInputs = { ...inputs };
                if (testInputs.tp !== undefined) testInputs.tp = t;
                if (testInputs.t_plate !== undefined) testInputs.t_plate = t;
                if (testInputs.bolt_count !== undefined) testInputs.bolt_count = nb;
                if (testInputs.n_bolts !== undefined) testInputs.n_bolts = nb;

                try {
                    const res = await evaluateFn(testInputs);
                    const dcr = Number(res?.governing_dcr) || 0.0;
                    if (dcr > 0 && dcr <= 1.0 && (res.status === 'OK' || res.status === 'PASS')) {
                        return {
                            success: true,
                            updatedInputs: testInputs,
                            message: `[접합부 최적설계] 플레이트 두께: ${t}mm, 볼트 수: ${nb}개 (DCR: ${dcr.toFixed(3)})`
                        };
                    }
                } catch (e) {}
            }
        }

        return {
            success: false,
            updatedInputs: inputs,
            message: `접합부 최적 규격을 찾지 못했습니다. 볼트 규격(M20➔M24) 변경이나 플레이트 폭 확장을 제안합니다.`
        };
    },

    async genericOptimize(moduleKey, inputs, evaluateFn) {
        return {
            success: false,
            updatedInputs: inputs,
            message: `해당 부재(${moduleKey})는 최적화 룰셋을 준비 중입니다. 입력값을 수동으로 조정하여 검토해 주세요.`
        };
    }
};

window.AutoDesigner = AutoDesigner;

if (typeof window !== 'undefined') {
    window.AutoDesigner = AutoDesigner;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AutoDesigner };
}