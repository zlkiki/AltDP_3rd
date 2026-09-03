"""
RC 경사 계단 슬래브(Stair Slab) 등가 수평투영 하중, 휨/전단 및 꺾임부(Knee Joint) 배근 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "misc_special_stair",
    "name": "계단 (RC Stair)",
    "category": "misc",
    "group": "special",
    "submodule": "stair",
    "description": "KDS 14 20 70 경사 계단 단(Riser/Tread) 등가 자중, 수평투영 휨/전단 및 꺾임부 대각 철근 설계",
    "geomType": "rc_slab",
    "template": "rc_slab"
}

class StairInput(BaseModel):
    span_horiz: float = Field(3600.0, description="계단 수평 투영 경간 L (mm)")
    slab_thick: float = Field(150.0, description="계단판 슬래브 두께 t (mm)")
    tread_R: float = Field(175.0, description="챌판 높이 R (Riser) (mm)")
    tread_T: float = Field(280.0, description="디딤판 너비 T (Tread) (mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근 항복강도 (MPa)")
    live_load: float = Field(3.0, description="활하중 (kN/m²)")
    finish_load: float = Field(1.0, description="마감 하중 (kN/m²)")
    rebar_dia: Any = Field("D13", description="하부 주철근 규격 (D10, D13, D16)")
    rebar_spacing: float = Field(150.0, description="하부 주철근 간격 (mm)")

def calculate(data: StairInput) -> Dict[str, Any]:
    L = data.span_horiz / 1000.0  # m
    t = data.slab_thick  # mm
    R = data.tread_R
    T = data.tread_T
    fck = data.fck
    fy = data.fy
    
    # 1. 경사각 theta 및 경사 슬래브 등가 자중
    tan_theta = R / T
    theta_rad = math.atan(tan_theta)
    cos_theta = math.cos(theta_rad)
    
    # 단위 수평 투영 면적(1m x 1m) 당 계단 자중
    # 슬래브 자중 w_slab = (t/1000) / cos(theta) * 24.0
    w_slab = ((t / 1000.0) / cos_theta) * 24.0  # kN/m2
    # 디딤단 평균 자중 w_step = 0.5 * (R/1000) * 24.0
    w_step = 0.5 * (R / 1000.0) * 24.0  # kN/m2
    
    w_dl = w_slab + w_step + data.finish_load  # kN/m2
    w_ll = data.live_load  # kN/m2
    w_u = 1.2 * w_dl + 1.6 * w_ll  # kN/m (폭 1m 기준)
    
    # 2. 계수 휨모멘트 및 전단력 (단순지지 가정: Mu = wu * L^2 / 8)
    Mu = (w_u * (L**2)) / 8.0  # kN·m/m
    Vu = (w_u * L) / 2.0  # kN/m
    
    # 3. 휨 내력 phi_Mn
    d = t - 30.0  # mm
    r_str = str(data.rebar_dia).strip().upper()
    ab_map = {"D10": 71.33, "D13": 126.7, "D16": 198.6, "D19": 286.5, "D22": 387.1, "10": 71.33, "13": 126.7, "16": 198.6}
    ab = ab_map.get(r_str, 126.7)
    spacing = max(50.0, float(data.rebar_spacing))
    As = ab * (1000.0 / spacing)  # mm2/m
    
    a = (As * fy) / (0.85 * fck * 1000.0)
    phi_b = 0.85
    phi_Mn = phi_b * As * fy * (d - a / 2.0) / 1e6  # kN·m/m
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    # 4. 전단 내력 phi_Vc
    phi_v = 0.75
    phi_Vc = phi_v * (1.0 / 6.0) * math.sqrt(fck) * 1000.0 * d / 1000.0  # kN/m
    dcr_shear = Vu / phi_Vc if phi_Vc > 0 else 999.0
    
    # 5. 꺾임부(Knee Joint) 외측 할렬 방지 대각 보강근 As_knee
    # As_knee = 0.5 * As (인장력 절곡 성분 저항)
    As_knee = 0.5 * As
    
    max_dcr = max(dcr_flexure, dcr_shear)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "flexure": {
            "title": "계단판 휨모멘트 내력 검토 (Stair Flexural Capacity φMn)",
            "Mu_kNm_per_m": round(Mu, 1),
            "phi_Mn_kNm_per_m": round(phi_Mn, 1),
            "As_provided_mm2": round(As, 1),
            "dcr": round(dcr_flexure, 3),
            "phi": phi_b
        },
        "shear": {
            "title": "계단판 1방향 전단강도 검토 (Stair Shear Capacity φVc)",
            "Vu_kN_per_m": round(Vu, 1),
            "phi_Vc_kN_per_m": round(phi_Vc, 1),
            "dcr": round(dcr_shear, 3),
            "phi": phi_v
        },
        "details": {
            "stair_geometry": {
                "slope_deg": round(math.degrees(theta_rad), 1),
                "riser_R_mm": R,
                "tread_T_mm": T,
                "slab_thickness_t_mm": t,
                "effective_depth_d_mm": round(d, 1)
            },
            "loads_and_knee": {
                "equivalent_dead_load_kN_m2": round(w_dl, 2),
                "factored_load_wu_kN_m2": round(w_u, 2),
                "knee_joint_rebar_As_mm2": round(As_knee, 1)
            }
        },
        "summary": f"계단 슬래브 검토: 경사 {round(math.degrees(theta_rad),1)}°, 휨 DCR={round(dcr_flexure,2)}, 전단 DCR={round(dcr_shear,2)} ({status})",
        "visual_data": {
            "type": "rc_slab",
            "t": t,
            "span_x": data.span_horiz,
            "rebar_bot": f"{data.rebar_dia}@{int(data.rebar_spacing)}"
        }
    }
