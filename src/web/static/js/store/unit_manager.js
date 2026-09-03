// web/js/store/unit_manager.js
/**
 * AltDP Member Designer - Universal Dimensional Analysis Unit Manager
 * Ported & adapted from re-DCR unitSystem.js
 * Supports real-time bidirectional conversion between SI, SI-M, MKS, and US Imperial units.
 */

(function () {
    const FORCE_IN_N = {
        N: 1,
        kN: 1000,
        tonf: 9806.65,
        kgf: 9.80665,
        kip: 4448.2216152605,
        lb: 4.4482216152605
    };

    const LENGTH_IN_MM = {
        mm: 1,
        cm: 10,
        m: 1000,
        in: 25.4,
        ft: 304.8
    };

    const PRESETS = {
        'SI': {
            id: 'SI',
            name: 'SI (kN, mm, MPa)',
            desc: '한국 KDS 표준 실무 (기본값)',
            force: 'kN',
            length: 'mm',
            momentForce: 'kN',
            momentLength: 'm',
            stressForce: 'N',
            stressLength: 'mm', // N/mm² = MPa
            areaLoadForce: 'kN',
            areaLoadLength: 'm', // kN/m²
            digits: { length: 1, length_m: 2, force: 1, moment: 2, stress: 1, areaLoad: 2, area: 1 }
        },
        'SI_M': {
            id: 'SI_M',
            name: 'SI-Meter (kN, m, kPa)',
            desc: '토목 및 대형 구조 해석',
            force: 'kN',
            length: 'm',
            momentForce: 'kN',
            momentLength: 'm',
            stressForce: 'kN',
            stressLength: 'm', // kPa
            areaLoadForce: 'kN',
            areaLoadLength: 'm',
            digits: { length: 3, length_m: 3, force: 1, moment: 2, stress: 1, areaLoad: 2, area: 3 }
        },
        'MKS': {
            id: 'MKS',
            name: 'MKS (tonf, m, kgf/cm²)',
            desc: '기존 건축물 안전진단 / 구도면',
            force: 'tonf',
            length: 'm',
            momentForce: 'tonf',
            momentLength: 'm',
            stressForce: 'kgf',
            stressLength: 'cm', // kgf/cm²
            areaLoadForce: 'tonf',
            areaLoadLength: 'm',
            digits: { length: 3, length_m: 2, force: 2, moment: 2, stress: 1, areaLoad: 2, area: 3 }
        },
        'US': {
            id: 'US',
            name: 'US Customary (kip, in, ksi)',
            desc: '해외 프로젝트 / ACI / AISC',
            force: 'kip',
            length: 'in',
            momentForce: 'kip',
            momentLength: 'ft', // kip·ft
            stressForce: 'kip',
            stressLength: 'in', // ksi
            areaLoadForce: 'kip',
            areaLoadLength: 'ft', // ksf
            digits: { length: 2, length_m: 2, force: 2, moment: 2, stress: 2, areaLoad: 2, area: 2 }
        }
    };

    class UnitManager {
        constructor() {
            let saved = 'SI';
            try {
                if (typeof localStorage !== 'undefined') {
                    saved = localStorage.getItem('altdp_unit_system') || 'SI';
                }
            } catch (e) {
                saved = 'SI';
            }
            this.currentSystemId = PRESETS[saved] ? saved : 'SI';
            this.listeners = [];
        }

        getPresets() {
            return Object.values(PRESETS);
        }

        getCurrentSystem() {
            return PRESETS[this.currentSystemId] || PRESETS['SI'];
        }

        setUnitSystem(sysId) {
            if (!PRESETS[sysId] || this.currentSystemId === sysId) return;
            const prev = this.currentSystemId;
            this.currentSystemId = sysId;
            try {
                if (typeof localStorage !== 'undefined') {
                    localStorage.setItem('altdp_unit_system', sysId);
                }
            } catch (e) {}
            this.notify(prev, sysId);
        }

        subscribe(callback) {
            this.listeners.push(callback);
            return () => {
                this.listeners = this.listeners.filter(cb => cb !== callback);
            };
        }

        notify(prevSys, nextSys) {
            this.listeners.forEach(cb => {
                try {
                    cb(nextSys, prevSys);
                } catch (e) {
                    console.error('[UnitManager] Listener error:', e);
                }
            });
        }

        /**
         * Converts a canonical SI value to a specific unit system.
         */
        fromCanonicalSys(value, quantityType, sysId) {
            if (value === null || value === undefined || isNaN(value)) return value;
            const sys = PRESETS[sysId] || PRESETS['SI'];
            const num = Number(value);
            if (sys.id === 'SI') return num;

            switch (quantityType) {
                case 'force': // kN -> tonf, kip
                    return num * (1000 / FORCE_IN_N[sys.force]);
                case 'length': // mm -> m, cm, in
                    return num / LENGTH_IN_MM[sys.length];
                case 'length_m': // m -> m, ft
                    return (num * 1000) / LENGTH_IN_MM[sys.length === 'in' ? 'ft' : sys.length];
                case 'moment': // kN·m -> tonf·m, kip·ft
                    const forceScaleM = 1000 / FORCE_IN_N[sys.momentForce];
                    const lengthScaleM = 1000 / LENGTH_IN_MM[sys.momentLength];
                    return num * forceScaleM * lengthScaleM;
                case 'stress': // MPa (N/mm²) -> kgf/cm², ksi, kPa
                    const forceScaleS = 1 / FORCE_IN_N[sys.stressForce];
                    const lengthScaleS = 1 / (LENGTH_IN_MM[sys.stressLength] ** 2);
                    return num * (forceScaleS / lengthScaleS);
                case 'areaLoad': // kN/m² -> tonf/m², ksf
                    const forceScaleA = 1000 / FORCE_IN_N[sys.areaLoadForce];
                    const lengthScaleA = 1000 / LENGTH_IN_MM[sys.areaLoadLength];
                    return num * forceScaleA / (lengthScaleA ** 2);
                case 'area': // mm² -> m², in²
                    return num / (LENGTH_IN_MM[sys.length] ** 2);
                default:
                    return num;
            }
        }

        /**
         * Converts a value from a specific unit system back to canonical SI.
         */
        toCanonicalSys(value, quantityType, sysId) {
            if (value === null || value === undefined || isNaN(value)) return value;
            const sys = PRESETS[sysId] || PRESETS['SI'];
            const num = Number(value);
            if (sys.id === 'SI') return num;

            switch (quantityType) {
                case 'force':
                    return num * (FORCE_IN_N[sys.force] / 1000);
                case 'length':
                    return num * LENGTH_IN_MM[sys.length];
                case 'length_m':
                    return (num * LENGTH_IN_MM[sys.length === 'in' ? 'ft' : sys.length]) / 1000;
                case 'moment':
                    const forceScaleM = FORCE_IN_N[sys.momentForce] / 1000;
                    const lengthScaleM = LENGTH_IN_MM[sys.momentLength] / 1000;
                    return num * forceScaleM * lengthScaleM;
                case 'stress':
                    const forceScaleS = FORCE_IN_N[sys.stressForce];
                    const lengthScaleS = LENGTH_IN_MM[sys.stressLength] ** 2;
                    return num * (forceScaleS / lengthScaleS);
                case 'areaLoad':
                    const forceScaleA = FORCE_IN_N[sys.areaLoadForce] / 1000;
                    const lengthScaleA = (LENGTH_IN_MM[sys.areaLoadLength] / 1000) ** 2;
                    return num * (forceScaleA / lengthScaleA);
                case 'area':
                    return num * (LENGTH_IN_MM[sys.length] ** 2);
                default:
                    return num;
            }
        }

        /**
         * Converts a value from canonical SI to the currently active display unit system.
         */
        fromCanonical(value, quantityType) {
            return this.fromCanonicalSys(value, quantityType, this.currentSystemId);
        }

        /**
         * Converts a value from the currently active display unit system back to canonical SI.
         */
        toCanonical(value, quantityType) {
            return this.toCanonicalSys(value, quantityType, this.currentSystemId);
        }

        /**
         * Rebase a draft input text from prev unit system to next unit system.
         */
        rebaseUnitDraftText(text, prevSysId, nextSysId, quantityType) {
            if (!text || String(text).trim() === '' || !quantityType) return text;
            const val = Number(text);
            if (!Number.isFinite(val)) return text;
            
            // prevSys -> Canonical SI -> nextSys
            const canonical = this.toCanonicalSys(val, quantityType, prevSysId);
            const converted = this.fromCanonicalSys(canonical, quantityType, nextSysId);
            
            const digits = PRESETS[nextSysId]?.digits?.[quantityType] ?? 2;
            const fixed = Number(converted.toFixed(digits));
            return String(fixed);
        }

        /**
         * Returns readable unit string for the current active unit system.
         */
        getUnitString(quantityType) {
            const sys = this.getCurrentSystem();
            switch (quantityType) {
                case 'force': return sys.force;
                case 'length': return sys.length;
                case 'length_m': return sys.length === 'in' ? 'ft' : 'm';
                case 'moment': return `${sys.momentForce}·${sys.momentLength}`;
                case 'stress': return sys.id === 'SI' ? 'MPa' : (sys.id === 'MKS' ? 'kgf/cm²' : (sys.id === 'US' ? 'ksi' : 'kPa'));
                case 'areaLoad': return `${sys.areaLoadForce}/${sys.areaLoadLength}²`;
                case 'area': return `${sys.length}²`;
                default: return '';
            }
        }

        getFieldQuantityType(fieldName) {
            return window.FormGenerator ? window.FormGenerator.getFieldQuantityType(fieldName) : null;
        }
    }

    window.UnitManager = new UnitManager();
})();
