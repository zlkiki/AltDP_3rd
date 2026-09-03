# app/engines/rc/slab/base.py
"""RC Slab (1·2방향 슬래브 휨/전단 및 최소 두께 검토) Engine - KDS 14 20 70 & PCA Method 2."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_alpha1, calc_eta

MODULE_INFO = {
    "id": "base",
    "name": "슬래브 (RC Slab)",
    "category": "rc",
    "group": "slab",
    "geomType": "rc_slab",
    "description": "KDS 14 20 및 PCA Method 2에 따른 1방향/2방향 슬래브 휨모멘트, 최소두께 및 배근 검토"
}

# PCA Method 2 Coeff Table (m = 1.0, 0.9, 0.8, 0.7, 0.6, 0.5)
PCA_CASE_COEFFS = {
    1: {  # All edges discontinuous (Simply supported)
        "caNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "cbNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "caPos": [0.036, 0.040, 0.045, 0.050, 0.059, 0.072],
        "cbPos": [0.036, 0.029, 0.022, 0.014, 0.008, 0.004]
    },
    2: {  # All edges continuous
        "caNeg": [0.045, 0.050, 0.055, 0.060, 0.066, 0.075],
        "cbNeg": [0.045, 0.041, 0.037, 0.031, 0.024, 0.017],
        "caPos": [0.018, 0.020, 0.023, 0.026, 0.030, 0.036],
        "cbPos": [0.018, 0.014, 0.011, 0.008, 0.005, 0.003]
    },
    3: {  # One long edge continuous
        "caNeg": [0.057, 0.061, 0.065, 0.068, 0.070, 0.072],
        "cbNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "caPos": [0.027, 0.030, 0.034, 0.038, 0.043, 0.052],
        "cbPos": [0.027, 0.022, 0.017, 0.011, 0.007, 0.004]
    },
    4: {  # One short edge continuous
        "caNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "cbNeg": [0.057, 0.055, 0.051, 0.044, 0.038, 0.029],
        "caPos": [0.027, 0.032, 0.039, 0.046, 0.055, 0.067],
        "cbPos": [0.027, 0.021, 0.015, 0.009, 0.005, 0.003]
    },
    5: {  # Two adjacent edges continuous
        "caNeg": [0.050, 0.055, 0.060, 0.066, 0.071, 0.076],
        "cbNeg": [0.050, 0.045, 0.040, 0.034, 0.027, 0.019],
        "caPos": [0.027, 0.030, 0.035, 0.040, 0.048, 0.058],
        "cbPos": [0.027, 0.022, 0.017, 0.011, 0.007, 0.004]
    },
    6: {  # Two long edges continuous
        "caNeg": [0.071, 0.075, 0.079, 0.080, 0.082, 0.083],
        "cbNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "caPos": [0.033, 0.038, 0.043, 0.049, 0.055, 0.061],
        "cbPos": [0.033, 0.025, 0.019, 0.012, 0.007, 0.004]
    },
    7: {  # Two short edges continuous
        "caNeg": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "cbNeg": [0.071, 0.067, 0.062, 0.057, 0.051, 0.044],
        "caPos": [0.033, 0.038, 0.047, 0.056, 0.068, 0.080],
        "cbPos": [0.033, 0.025, 0.019, 0.013, 0.008, 0.004]
    },
    8: {  # Three edges continuous (one short discontinuous)
        "caNeg": [0.055, 0.060, 0.066, 0.071, 0.077, 0.085],
        "cbNeg": [0.055, 0.050, 0.045, 0.038, 0.032, 0.024],
        "caPos": [0.022, 0.025, 0.029, 0.033, 0.039, 0.048],
        "cbPos": [0.022, 0.018, 0.014, 0.009, 0.006, 0.003]
    },
    9: {  # Three edges continuous (one long discontinuous)
        "caNeg": [0.058, 0.064, 0.070, 0.076, 0.082, 0.088],
        "cbNeg": [0.058, 0.052, 0.046, 0.039, 0.032, 0.024],
        "caPos": [0.022, 0.026, 0.032, 0.038, 0.046, 0.056],
        "cbPos": [0.022, 0.017, 0.013, 0.008, 0.005, 0.003]
    }
}


class SlabInputSchema(BaseModel):
    Lx: float = Field(4000.0, description="단변 스팬 (mm)")
    Ly: float = Field(6000.0, description="장변 스팬 (mm)")
    thickness: float = Field(200.0, description="슬래브 두께 (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(30.0, description="피복 두께 (mm)")
    case_no: int = Field(2, description="PCA 경계조건 케이스 (1~9)")
    
    DL: float = Field(5.0, description="고정하중 (kN/m²)")
    LL: float = Field(3.0, description="활하중 (kN/m²)")
    
    main_dia: int = Field(13, description="주철근 직경 (mm)")
    main_spacing: float = Field(200.0, description="주철근 간격 (mm)")
    temp_dia: int = Field(10, description="온도수축철근 직경 (mm)")
    temp_spacing: float = Field(250.0, description="온도수축철근 간격 (mm)")


def get_pca_coeff(case_no: int, m: float) -> Dict[str, float]:
    """Linear interpolation for PCA coefficients based on aspect ratio m = la/lb (0.5 ~ 1.0)"""
    m_clamped = max(min(m, 1.0), 0.5)
    m_vals = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
    coeffs = PCA_CASE_COEFFS.get(case_no, PCA_CASE_COEFFS[2])
    
    idx = 0
    for i in range(len(m_vals) - 1):
        if m_vals[i] >= m_clamped >= m_vals[i + 1]:
            idx = i
            break
            
    m1, m2 = m_vals[idx], m_vals[idx + 1]
    t = (m_clamped - m2) / (m1 - m2) if m1 != m2 else 1.0
    
    def interp(arr):
        return arr[idx + 1] + t * (arr[idx] - arr[idx + 1])
        
    return {
        "caNeg": interp(coeffs["caNeg"]),
        "cbNeg": interp(coeffs["cbNeg"]),
        "caPos": interp(coeffs["caPos"]),
        "cbPos": interp(coeffs["cbPos"])
    }


def compute_as_required(Mu_kNm_per_m: float, b_mm: float, d_mm: float, fck: float, fy: float) -> float:
    """Computes exact required rebar area As,req (mm²/m) using quadratic equilibrium formula."""
    phi = 0.85
    Mu_Nmm = abs(Mu_kNm_per_m) * 1e6
    a1 = calc_alpha1(fck) * calc_eta(fck)
    
    A = -(fy * fy) / (2.0 * a1 * fck * b_mm)
    B = fy * d_mm
    C = -(Mu_Nmm / phi)
    disc = B * B - 4.0 * A * C
    if disc < 0:
        return float("inf")
    As1 = (-B + math.sqrt(disc)) / (2.0 * A)
    As2 = (-B - math.sqrt(disc)) / (2.0 * A)
    cands = [v for v in [As1, As2] if v > 0 and math.isfinite(v)]
    return min(cands) if cands else float("inf")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    Lx = float(data.get("Lx", 4000.0))
    Ly = float(data.get("Ly", 6000.0))
    h = float(data.get("thickness", 200.0))
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 30.0))
    case_no = int(data.get("case_no", 2))
    
    DL = float(data.get("DL", 5.0))
    LL = float(data.get("LL", 3.0))
    
    main_dia = int(data.get("main_dia", 13))
    main_spacing = float(data.get("main_spacing", 200.0))
    temp_dia = int(data.get("temp_dia", 10))
    temp_spacing = float(data.get("temp_spacing", 250.0))
    
    wu = 1.2 * DL + 1.6 * LL  # kN/m²
    la = min(Lx, Ly) * 1e-3    # short span (m)
    lb = max(Lx, Ly) * 1e-3    # long span (m)
    m = la / lb if lb > 0 else 1.0
    is_one_way = m < 0.5
    
    b_strip = 1000.0
    d = h - cover - main_dia / 2.0
    
    if is_one_way:
        Mu_pos_a = wu * (la ** 2) / 10.0
        Mu_neg_a = wu * (la ** 2) / 12.0
        Mu_pos_b = 0.0
        Mu_neg_b = 0.0
        coeffs = {"caPos": 0.10, "caNeg": 0.083, "cbPos": 0.0, "cbNeg": 0.0}
    else:
        coeffs = get_pca_coeff(case_no, m)
        w_tot = wu * (la ** 2)
        Mu_pos_a = coeffs["caPos"] * w_tot
        Mu_neg_a = coeffs["caNeg"] * w_tot
        Mu_pos_b = coeffs["cbPos"] * w_tot
        Mu_neg_b = coeffs["cbNeg"] * w_tot
        
    As_main = (b_strip / main_spacing) * REBAR_AREA.get(main_dia, 126.7)
    As_temp = (b_strip / temp_spacing) * REBAR_AREA.get(temp_dia, 71.33)
    
    rho_min = 0.002 if fy <= 400.0 else max(0.002 * 400.0 / fy, 0.0014)
    As_min = rho_min * b_strip * h
    
    # Required rebar calculations
    As_req_pos_a = compute_as_required(Mu_pos_a, b_strip, d, fck, fy)
    As_req_neg_a = compute_as_required(Mu_neg_a, b_strip, d, fck, fy)
    
    # Flexural capacity for provided As_main
    a1_eta = calc_alpha1(fck) * calc_eta(fck)
    a = As_main * fy / (a1_eta * fck * b_strip)
    phi_flex = 0.85
    Mn = As_main * fy * (d - a / 2.0) * 1e-6
    phiMn = phi_flex * Mn
    dcr_flex = max(Mu_pos_a, Mu_neg_a) / phiMn if phiMn > 0 else 999.0
    
    h_min = Lx / 28.0 if is_one_way else (la * 1000.0 * (0.8 + fy / 1400.0) / 36.0)
    dcr_thickness = h_min / h if h > 0 else 999.0
    
    governing_dcr = max(dcr_flex, dcr_thickness)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "system": "1-Way Slab" if is_one_way else f"2-Way Slab (PCA Case {case_no}, m={m:.2f})",
        "m": round(m, 3), "wu": round(wu, 2), "h": h, "d": round(d, 1),
        "Lx": Lx, "Ly": Ly, "cover": cover, "fck": fck, "fy": fy,
        "pca_coeffs": coeffs,
        "moments": {
            "Mu_pos_short_kNm": round(Mu_pos_a, 2),
            "Mu_neg_short_kNm": round(Mu_neg_a, 2),
            "Mu_pos_long_kNm": round(Mu_pos_b, 2),
            "Mu_neg_long_kNm": round(Mu_neg_b, 2)
        },
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "Mu_max_kNm_m": round(max(Mu_pos_a, Mu_neg_a), 2),
            "phiMn_kNm_m": round(phiMn, 2),
            "As_prov_mm2_m": round(As_main, 1),
            "As_req_mm2_m": round(max(As_req_pos_a, As_req_neg_a), 1),
            "As_min_mm2_m": round(As_min, 1)
        },
        "thickness_check": {
            "h_provided_mm": h,
            "h_min_recommended_mm": round(h_min, 1),
            "dcr": round(dcr_thickness, 3)
        },
        "temperature_rebar": {
            "As_provided_mm2_m": round(As_temp, 1),
            "As_required_mm2_m": round(As_min, 1),
            "status": "OK" if As_temp >= As_min else "Shortage"
        },
        "section": {
            "thickness": h, "cover": cover, "d": round(d, 1),
            "main_rebar": f"D{main_dia}@{int(main_spacing)}",
            "temp_rebar": f"D{temp_dia}@{int(temp_spacing)}"
        }
    }
