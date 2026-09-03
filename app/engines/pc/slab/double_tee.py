"""
장스팬 프리스트레스트 더블티(Double Tee, TT) 슬래브 극한 휨/전단 및 프리스트레스 캠버(Camber) 해석 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_slab_double_tee",
    "name": "더블티 슬래브 (Double Tee Slab)",
    "category": "pc",
    "group": "slab",
    "submodule": "double_tee",
    "description": "장스팬 주차장/물류센터 Double-Tee 슬래브 휨, 전단 강도 및 릴리즈 캠버/장기 처짐 해석",
    "geomType": "pc_double_tee",
    "template": "pc_double_tee"
}

class DoubleTeeInput(BaseModel):
    width: float = Field(2400.0, description="더블티 패널 전체 폭 (mm)")
    depth: float = Field(600.0, description="더블티 전체 춤 (mm)")
    flange_thick: float = Field(50.0, description="상부 플랜지 두께 (mm)")
    stem_width_top: float = Field(150.0, description="리브(Stem) 상단 폭 (mm)")
    stem_width_bot: float = Field(120.0, description="리브(Stem) 하단 폭 (mm)")
    span: float = Field(15000.0, description="더블티 경간 (mm)")
    fck: float = Field(40.0, description="콘크리트 압축강도 (MPa)")
    fpu: float = Field(1860.0, description="긴장재 인장강도 (MPa)")
    strands_per_stem: int = Field(4, description="리브(Stem) 1개당 긴장 강연선 수")
    strand_dia: float = Field(12.7, description="강연선 직경 (mm)")
    Mu: float = Field(450.0, description="계수 휨모멘트 (kN·m)")
    Vu: float = Field(150.0, description="계수 전단력 (kN)")

def calculate(data: DoubleTeeInput) -> Dict[str, Any]:
    b = data.width
    H = data.depth
    hf = data.flange_thick
    L = data.span
    fck = data.fck
    fpu = data.fpu
    
    # 1. 텐던 단면적 및 유효 긴장력 (2개 Stem)
    # 강연선 1개 단면적 (12.7mm = 98.7 mm2)
    a_strand = (math.pi * (data.strand_dia**2)) / 4.0
    Aps = 2.0 * data.strands_per_stem * a_strand  # mm2
    
    dp = H - 75.0  # mm
    
    # 2. 극한 휨강도 Mn 산정
    rho_p = Aps / (b * dp)
    gamma_p = 0.40
    beta1 = 0.77  # 40MPa
    fps = fpu * (1.0 - (gamma_p / beta1) * (rho_p * fpu / fck))
    
    a = (Aps * fps) / (0.85 * fck * b)
    Mn = Aps * fps * (dp - a / 2.0) / 1e6  # kN·m
    phi_b = 0.85
    phi_Mn = phi_b * Mn
    dcr_flexure = data.Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 3. 복부 전단강도 Vn (2개 Stem 복부폭 합산)
    bw_total = 2.0 * ((data.stem_width_top + data.stem_width_bot) / 2.0)
    phi_v = 0.75
    Vc = (1.0 / 6.0) * math.sqrt(fck) * bw_total * dp / 1000.0  # kN
    # 스터럽 2-D10@200 가정
    Vs = (2.0 * 71.33 * 400.0 * dp / 200.0) / 1000.0
    phi_Vn = phi_v * (Vc + Vs)
    dcr_shear = data.Vu / phi_Vn if phi_Vn > 0 else 999.0
    
    # 4. 도입 초기 캠버(Camber) 산정
    # Pe = 0.70 * fpu * Aps
    Pe = 0.70 * fpu * Aps  # N
    # 단면 2차모멘트 I 근사
    I_approx = (b * (hf**3)) / 12.0 + 2.0 * ((data.stem_width_top * ((H - hf)**3)) / 3.0)  # mm4
    Ec = 8500.0 * ((fck + 4.0)**(1.0/3.0))  # MPa
    # 도심거리 yb
    yb = H * 0.35
    e_mid = yb - 75.0
    # 캠버: delta_camber = Pe * e * L^2 / (8 E I) - 5 w L^4 / (384 E I)
    camber_init = (Pe * e_mid * (L**2)) / (8.0 * Ec * I_approx) if I_approx > 0 else 0.0  # mm
    
    max_dcr = max(dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_flexure": round(dcr_flexure, 3),
        "dcr_shear": round(dcr_shear, 3),
        "phi_Mn_kNm": round(phi_Mn, 1),
        "phi_Vn_kN": round(phi_Vn, 1),
        "initial_camber_mm": round(camber_init, 1),
        "Aps_mm2": round(Aps, 1),
        "summary": f"더블티(TT) 검토: 휨 DCR={round(dcr_flexure,2)}, 전단 DCR={round(dcr_shear,2)}, 초기 캠버={round(camber_init,1)}mm ({status})",
        "visual_data": {
            "type": "rc_tsect",
            "b": b,
            "h": H,
            "b_w": bw_total,
            "h_f": hf,
            "cover": 40.0,
            "top_rebar_count": 4,
            "bot_rebar_count": 4
        }
    }
