# app/engines/rc/beam/defl.py
"""RC Beam Deflection (Branson 유효단면2차모멘트 Ie 및 탄성/장기 처짐 산정) Engine - KDS 14 20 30."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA

MODULE_INFO = {
    "id": "defl",
    "name": "보 처짐 (Beam Deflection)",
    "category": "rc",
    "group": "beam",
    "geomType": "rc_rect",
    "description": "KDS 14 20 30에 따른 Branson 유효단면2차모멘트(Ie), 순간 탄성처짐 및 압축철근 지속하중계수(xi) 기반 장기 처짐 검토"
}


class BeamDeflInputSchema(BaseModel):
    b: float = Field(400.0, description="보 폭 b (mm)")
    h: float = Field(600.0, description="보 춤 h (mm)")
    L_span: float = Field(7000.0, description="보 스팬 L (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    bot_dia: int = Field(22, description="인장 주근 직경 (mm)")
    bot_num: int = Field(4, description="인장 주근 개수 (EA)")
    top_dia: int = Field(22, description="압축 주근 직경 (mm)")
    top_num: int = Field(2, description="압축 주근 개수 (EA)")
    
    M_dead: float = Field(80.0, description="고정하중 모멘트 (kN*m)")
    M_live: float = Field(60.0, description="활하중 모멘트 (kN*m)")
    sustained_live_ratio: float = Field(0.3, description="지속 활하중 비율 (0.0~1.0)")
    duration_months: int = Field(60, description="지속하중 재하기간 (개월, 60=5년 이상)")


def calculate(data: Any) -> Dict[str, Any]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = {}

    b = float(data.get("b", 400.0))
    h = float(data.get("h", 600.0))
    L = float(data.get("L_span", 7000.0))
    fck = float(data.get("fck", 24.0))
    cover = float(data.get("cover", 40.0))
    
    bot_dia = int(data.get("bot_dia", 22))
    bot_num = int(data.get("bot_num", 4))
    top_dia = int(data.get("top_dia", 22))
    top_num = int(data.get("top_num", 2))
    
    Md_kNm = float(data.get("M_dead", 80.0))
    Ml_kNm = float(data.get("M_live", 60.0))
    sustained_ratio = float(data.get("sustained_live_ratio", 0.3))
    duration_months = int(data.get("duration_months", 60))
    
    # 1. Modulus of Elasticity & Gross Moment of Inertia
    Ec = 8500.0 * ((fck + 4.0) ** (1.0 / 3.0))  # MPa
    Es = 200000.0
    n = Es / Ec
    
    Ig = b * (h ** 3) / 12.0  # mm⁴
    yt = h / 2.0
    
    # Cracking Moment Mcr (fr = 0.63 * sqrt(fck))
    fr = 0.63 * math.sqrt(fck)
    Mcr = (fr * Ig / yt) * 1e-6  # kN*m
    
    # 2. Cracked Section Moment of Inertia Icr
    d = h - cover - 10.0 - bot_dia / 2.0
    d_c = cover + 10.0 + top_dia / 2.0
    As = bot_num * REBAR_AREA.get(bot_dia, 387.1)
    As_prime = top_num * REBAR_AREA.get(top_dia, 387.1)
    
    # Quadratic for elastic cracked neutral axis kd
    A_quad = b / 2.0
    B_quad = (n - 1.0) * As_prime + n * As
    C_quad = -((n - 1.0) * As_prime * d_c + n * As * d)
    
    disc = B_quad ** 2 - 4.0 * A_quad * C_quad
    kd = (-B_quad + math.sqrt(max(0.0, disc))) / (2.0 * A_quad) if A_quad > 0 else d / 3.0
    
    Icr = (b * (kd ** 3) / 3.0) + (n - 1.0) * As_prime * ((kd - d_c) ** 2) + n * As * ((d - kd) ** 2)
    
    # 3. Branson Effective Moment of Inertia Ie
    Ma_total = Md_kNm + Ml_kNm
    if Ma_total <= Mcr:
        Ie = Ig
    else:
        mcr_ma3 = (Mcr / Ma_total) ** 3
        Ie = mcr_ma3 * Ig + (1.0 - mcr_ma3) * Icr
        Ie = min(Ie, Ig)
        
    # 4. Immediate Deflections (Simply supported uniform load delta = 5*M*L^2 / (48*E*I))
    coeff = 5.0 * (L ** 2) / (48.0 * Ec * Ie) if (Ec * Ie) > 0 else 0.0
    delta_dead = coeff * (Md_kNm * 1e6)
    delta_live = coeff * (Ml_kNm * 1e6)
    delta_immediate_total = delta_dead + delta_live
    
    # 5. Long-term Deflection Multiplier lambda_delta (KDS 14 20 30 §4.3)
    xi = 2.0 if duration_months >= 60 else (1.4 if duration_months >= 12 else (1.2 if duration_months >= 6 else 1.0))
    rho_prime = As_prime / (b * d) if (b * d) > 0 else 0.0
    lambda_delta = xi / (1.0 + 50.0 * rho_prime)
    
    M_sustained = Md_kNm + sustained_ratio * Ml_kNm
    delta_sustained_immediate = coeff * (M_sustained * 1e6)
    delta_creep_shrinkage = lambda_delta * delta_sustained_immediate
    
    delta_total_longterm = delta_dead + delta_live + delta_creep_shrinkage
    
    # 6. Allowable Limits (KDS 14 20 30 Table 4.3-1)
    allow_live_L360 = L / 360.0
    allow_total_L240 = L / 240.0
    
    dcr_live = delta_live / allow_live_L360 if allow_live_L360 > 0 else 0.0
    dcr_total = delta_total_longterm / allow_total_L240 if allow_total_L240 > 0 else 0.0
    governing_dcr = max(dcr_live, dcr_total)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "max_dcr": round(governing_dcr, 3),
        "deflection": {
            "title": "보 사용성 처짐 검토 (Deflection Serviceability Check)",
            "delta_dead_mm": round(delta_dead, 2),
            "delta_live_mm": round(delta_live, 2),
            "allow_live_mm": round(allow_live_L360, 2),
            "dcr_live": round(dcr_live, 3),
            "delta_longterm_mm": round(delta_total_longterm, 2),
            "allow_longterm_mm": round(allow_total_L240, 2),
            "dcr_longterm": round(dcr_total, 3),
            "dcr": round(governing_dcr, 3)
        },
        "details": {
            "section_properties": {
                "Ec_MPa": round(Ec, 1),
                "modular_ratio_n": round(n, 2),
                "Ig_mm4": round(Ig, 0),
                "fr_MPa": round(fr, 2),
                "Mcr_kNm": round(Mcr, 2),
                "kd_mm": round(kd, 1),
                "Icr_mm4": round(Icr, 0),
                "Ie_mm4": round(Ie, 0)
            },
            "creep_shrinkage": {
                "duration_months": duration_months,
                "time_factor_xi": xi,
                "comp_rebar_ratio_rho_prime": round(rho_prime, 5),
                "multiplier_lambda_delta": round(lambda_delta, 3)
            }
        },
        "summary": f"처짐 검토: 활하중 처짐={delta_live:.1f}mm (한계 {allow_live_L360:.1f}mm), 총 장기처짐={delta_total_longterm:.1f}mm (한계 {allow_total_L240:.1f}mm)",
        "visual_data": {
            "b": b,
            "h": h,
            "cover": cover,
            "bot_num": bot_num,
            "top_num": top_num
        }
    }
    if duration_months >= 60:
        xi = 2.0
    elif duration_months >= 12:
        xi = 1.4
    elif duration_months >= 6:
        xi = 1.2
    else:
        xi = 1.0
        
    rho_prime = As_prime / (b * d)
    lambda_delta = xi / (1.0 + 50.0 * rho_prime)
    
    delta_sustained = delta_dead + sustained_ratio * delta_live
    delta_creep_shrinkage = lambda_delta * delta_sustained
    delta_long_term_total = delta_live + delta_creep_shrinkage
    
    # Allowable deflection limit L / 240 or L / 480
    delta_allow = L / 240.0
    dcr_defl = delta_long_term_total / delta_allow if delta_allow > 0 else 999.0
    status = "OK" if dcr_defl <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(dcr_defl, 3),
        "deflection_summary": {
            "dcr": round(dcr_defl, 3),
            "delta_immediate_live_mm": round(delta_live, 2),
            "delta_long_term_total_mm": round(delta_long_term_total, 2),
            "delta_allowable_mm": round(delta_allow, 2),
            "allowable_criteria": "L / 240"
        },
        "section_properties": {
            "Mcr_kNm": round(Mcr, 1),
            "Ma_total_kNm": round(Ma_total, 1),
            "Ig_cm4": round(Ig * 1e-4, 0),
            "Icr_cm4": round(Icr * 1e-4, 0),
            "Ie_cm4": round(Ie * 1e-4, 0),
            "Ie_ratio_pct": round((Ie / Ig) * 100, 1)
        },
        "long_term_factor": {
            "xi": xi,
            "rho_prime_pct": round(rho_prime * 100, 2),
            "lambda_multiplier": round(lambda_delta, 2)
        }
    }
