# app/engines/rc/beam/tsect.py
"""RC T-Beam / L-Beam (T형 및 L형 단면 보 유효플랜지폭 be 산정 및 휨 검토) Engine - KDS 14 20 20."""
import math
from typing import Dict, Any
from pydantic import BaseModel, Field

from app.engines.common.kds_concrete import REBAR_FY, REBAR_AREA, calc_beta1, calc_eta, get_eps_cu

MODULE_INFO = {
    "id": "tsect",
    "name": "T/L형 보 (T-Beam)",
    "category": "rc",
    "group": "beam",
    "geomType": "rc_tsect",
    "description": "KDS 14 20에 따른 T형/L형 보의 유효 플랜지 폭(be) 자동 산정 및 플랜지 압축/웨브 압축 휨강도 검토"
}


class BeamTsectInputSchema(BaseModel):
    shape: str = Field("T_shape", description="단면 형태 (T_shape, L_shape)")
    bw: float = Field(400.0, description="웨브 폭 bw (mm)")
    h: float = Field(700.0, description="전체 춤 h (mm)")
    hf: float = Field(150.0, description="플랜지(슬래브) 두께 hf (mm)")
    L_span: float = Field(8000.0, description="보 스팬 L (mm)")
    sw: float = Field(3000.0, description="인접 보 순간격 sw (mm)")
    
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    rebar_grade: str = Field("SD400", description="철근 강종")
    cover: float = Field(40.0, description="피복 두께 (mm)")
    
    bot_dia: int = Field(25, description="하부 인장주근 직경 (mm)")
    bot_num: int = Field(5, description="하부 인장주근 개수 (EA)")
    
    Mu: float = Field(480.0, description="소요 휨모멘트 Mu (kN*m)")
    Vu: float = Field(180.0, description="소요 전단력 Vu (kN)")


def calculate(data: Dict[str, Any]) -> Dict[str, Any]:
    shape = str(data.get("shape", "T_shape"))
    bw = float(data.get("bw", 400.0))
    h = float(data.get("h", 700.0))
    hf = float(data.get("hf", 150.0))
    L = float(data.get("L_span", 8000.0))
    sw = float(data.get("sw", 3000.0))
    
    fck = float(data.get("fck", 24.0))
    rebar_grade = str(data.get("rebar_grade", "SD400"))
    fy = REBAR_FY.get(rebar_grade, 400.0)
    cover = float(data.get("cover", 40.0))
    
    bot_dia = int(data.get("bot_dia", 25))
    bot_num = int(data.get("bot_num", 5))
    
    Mu_kNm = float(data.get("Mu", 480.0))
    Vu_kN = float(data.get("Vu", 180.0))
    
    # 1. Effective Flange Width be (KDS 14 20 20 §4.1.4)
    if shape == "T_shape":
        be1 = L / 4.0
        be2 = bw + 16.0 * hf
        be3 = bw + sw
        be = min(be1, be2, be3)
    else:  # L_shape
        be1 = bw + L / 12.0
        be2 = bw + 6.0 * hf
        be3 = bw + sw / 2.0
        be = min(be1, be2, be3)
        
    d = h - cover - 10.0 - bot_dia / 2.0
    As = bot_num * REBAR_AREA.get(bot_dia, 506.7)
    
    # 2. T-Beam Flexural Capacity
    beta1 = calc_beta1(fck)
    eta = calc_eta(fck)
    sb = eta * 0.85 * fck
    ecu = get_eps_cu(fck)
    
    # Check if depth of stress block a <= hf (Rectangular behavior)
    a_rect = As * fy / (sb * be)
    
    if a_rect <= hf:
        # Acts like rectangular beam of width be
        a = a_rect
        c = a / beta1
        Mn = As * fy * (d - a / 2.0)
        action_type = "Rectangular Flange Behavior (a <= hf)"
    else:
        # True T-beam action (stress block enters web)
        A_flange_overhang = (be - bw) * hf
        C_flange = sb * A_flange_overhang
        Asf = C_flange / fy
        Asw = As - Asf
        
        a_web = Asw * fy / (sb * bw)
        a = a_web
        c = a / beta1
        
        M_flange = C_flange * (d - hf / 2.0)
        M_web = sb * bw * a * (d - a / 2.0)
        Mn = M_flange + M_web
        action_type = "True T-Beam Web Behavior (a > hf)"
        
    eps_t = ecu * (d - c) / c if c > 0 else 0.005
    phi_flex = 0.85 if eps_t >= 0.005 else (0.65 + 0.20 * (eps_t - 0.002) / 0.003 if eps_t > 0.002 else 0.65)
    
    phiMn_kNm = phi_flex * Mn * 1e-6
    dcr_flex = abs(Mu_kNm) / phiMn_kNm if phiMn_kNm > 0 else 999.0
    
    # 3. Shear Capacity
    Vc = (1.0 / 6.0) * math.sqrt(fck) * bw * d * 1e-3
    Vs = (2 * REBAR_AREA.get(10, 71.3) * min(fy, 500.0) * d / 150.0) * 1e-3  # D10@150
    phi_v = 0.75
    phiVn_kN = phi_v * (Vc + Vs)
    dcr_shear = abs(Vu_kN) / phiVn_kN if phiVn_kN > 0 else 999.0
    
    governing_dcr = max(dcr_flex, dcr_shear)
    status = "OK" if governing_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(governing_dcr, 3),
        "effective_flange": {
            "be_effective_mm": round(be, 0),
            "controlling_limit": "L/4" if be == L/4.0 else ("bw+16hf" if be == (bw+16*hf) else "bw+sw"),
            "action_type": action_type
        },
        "flexure": {
            "dcr": round(dcr_flex, 3),
            "phiMn_kNm": round(phiMn_kNm, 1),
            "Mu_kNm": Mu_kNm,
            "a_depth_mm": round(a, 1),
            "hf_flange_depth_mm": hf
        },
        "shear": {
            "dcr": round(dcr_shear, 3),
            "phiVn_kN": round(phiVn_kN, 1),
            "Vu_kN": Vu_kN
        },
        "section": {
            "shape": shape, "bw": bw, "be": round(be, 0), "h": h, "hf": hf,
            "rebar": f"{bot_num}-D{bot_dia}"
        }
    }
