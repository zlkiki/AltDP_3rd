"""
PC 하프 슬래브(Half PC Panel) + 현장타설(Topping) 합성 계면 수평전단마찰(Shear Friction) 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_slab_half_slab",
    "name": "하프 PC 슬래브 (Half PC Slab)",
    "category": "pc",
    "group": "slab",
    "submodule": "half_slab",
    "description": "KDS 14 20 60 프리캐스트 하프패널과 현장타설 토핑 콘크리트 계면 수평전단 및 합성 휨 설계",
    "geomType": "rc_slab",
    "template": "rc_slab"
}

class HalfSlabInput(BaseModel):
    span: float = Field(6000.0, description="슬래브 경간 (mm)")
    h_precast: float = Field(70.0, description="PC 하프패널 두께 (mm)")
    h_topping: float = Field(130.0, description="현장타설 토핑 두께 (mm)")
    fck_precast: float = Field(35.0, description="PC 패널 콘크리트 압축강도 (MPa)")
    fck_topping: float = Field(24.0, description="토핑 콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="철근/트러스 항복강도 (MPa)")
    Vu_interface: float = Field(85.0, description="계면 작용 계수 전단력 (kN/m)")
    Mu_serv: float = Field(65.0, description="합성 슬래브 계수 휨모멘트 (kN·m/m)")
    surface_roughened: bool = Field(True, description="계면 인위적 거칠기 처리 여부(Roughened, >=6mm)")
    truss_bar_dia: str = Field("D10", description="계면 연결 래티스/트러스 수직근 규격")
    truss_bar_spacing: float = Field(200.0, description="트러스 철근 배치 간격 (mm)")

def calculate(data: HalfSlabInput) -> Dict[str, Any]:
    h_tot = data.h_precast + data.h_topping
    Vu = data.Vu_interface * 1e3  # N/m
    Mu = data.Mu_serv * 1e6  # N·mm/m
    b = 1000.0  # 단위 폭 1m
    
    # 1. 계면 수평전단강도 Vnh (KDS 14 20 60 식)
    # Avf: 단위 m당 계면 전단보강근 단면적
    ab_truss = 71.33 if data.truss_bar_dia == "D10" else 126.7
    # 1m당 개수
    num_per_m = 1000.0 / data.truss_bar_spacing
    Avf = 2.0 * ab_truss * num_per_m  # 2leg mm2/m
    
    # 마찰계수 mu
    # 거칠게 마감된 경우 mu = 1.0, 그렇지 않은 경우 mu = 0.6
    mu = 1.0 if data.surface_roughened else 0.6
    phi_v = 0.75
    
    # 전단마찰 강도 Vnh = phi * (Avf * fy * mu) + 콘크리트 부착강도
    # 콘크리트 직접 부착 기여도 Vc_inter
    # 거친 표면: 0.55 MPa * b * d_v
    dv = h_tot - 30.0
    Vc_inter = (0.55 if data.surface_roughened else 0.0) * b * dv  # N
    Vn_inter = min(Vc_inter + Avf * data.fy * mu, 0.2 * data.fck_topping * b * dv)
    phi_Vnh = phi_v * Vn_inter
    
    dcr_interface_shear = Vu / phi_Vnh if phi_Vnh > 0 else 999.0
    
    # 2. 합성 슬래브 극한 휨모멘트 Mn
    # 하부 PC 주근 (D13@150 가정 -> As = 126.7 * 6.67 = 845 mm2/m)
    As_bot = 845.0
    d = h_tot - 30.0
    a = (As_bot * data.fy) / (0.85 * data.fck_topping * b)
    Mn = As_bot * data.fy * (d - a / 2.0)  # N·mm/m
    phi_b = 0.85
    phi_Mn = phi_b * Mn
    dcr_flexure = Mu / phi_Mn if phi_Mn > 0 else 999.0
    
    max_dcr = max(dcr_interface_shear, dcr_flexure)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_interface_shear": round(dcr_interface_shear, 3),
        "dcr_flexure": round(dcr_flexure, 3),
        "h_total_mm": round(h_tot, 1),
        "phi_Vnh_kN_per_m": round(phi_Vnh / 1000.0, 1),
        "phi_Mn_kNm_per_m": round(phi_Mn / 1e6, 1),
        "Avf_mm2_per_m": round(Avf, 1),
        "summary": f"하프 PC 슬래브: 계면전단 DCR={round(dcr_interface_shear,2)}, 합성휨 DCR={round(dcr_flexure,2)} ({status})",
        "visual_data": {
            "type": "rc_slab",
            "thk": h_tot,
            "span_x": data.span,
            "span_y": 6000.0,
            "rebar_top_x": "D10@200",
            "rebar_bot_x": "D13@150"
        }
    }
