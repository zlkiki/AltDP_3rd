"""
ACI 360R / Westergaard Winkler 지반 탄성 지지 바닥 슬래브(Slab On Grade, SOG) 지게차 휠하중 휨응력 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_slab_sog",
    "name": "지반지지 슬래브 (SOG)",
    "category": "rc",
    "group": "slab",
    "submodule": "sog",
    "description": "ACI 360R / Westergaard 탄성 지반 반력계수(k) 기반 지게차 휠하중 및 랙 지주 하중 휨/지압 검토",
    "geomType": "rc_slab",
    "template": "rc_slab"
}

class SlabOnGradeInput(BaseModel):
    slab_thick: float = Field(200.0, description="슬래브 두께 h (mm)")
    subgrade_k: float = Field(0.05, description="지반 반력계수 k (N/mm³ or MPa/mm)")
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)")
    wheel_load: float = Field(60.0, description="지게차 1개 휠 하중 P (kN)")
    contact_radius: float = Field(120.0, description="휠 타이어 등가 접지반경 a (mm)")
    joint_spacing: float = Field(5000.0, description="수축 줄눈(Control Joint) 간격 (mm)")
    rebar_dia: str = Field("D13", description="수축/온도 보강근 규격")
    rebar_spacing: float = Field(250.0, description="보강근 배치 간격 (mm)")

def calculate(data: SlabOnGradeInput) -> Dict[str, Any]:
    h = data.slab_thick
    k = data.subgrade_k
    fck = data.fck
    P = data.wheel_load * 1000.0  # N
    a = data.contact_radius
    
    # 1. 콘크리트 탄성계수 및 상대강성반경 l (Radius of Relative Stiffness)
    Ec = 8500.0 * ((fck + 4.0)**(1.0/3.0))  # MPa
    nu = 0.15  # 포아송비
    # l = [ E * h^3 / (12 * (1 - nu^2) * k) ]^(1/4)
    l_stiff = ((Ec * (h**3)) / (12.0 * (1.0 - nu**2) * k))**(0.25)  # mm
    
    # 2. Westergaard 휠하중 위치별 휨응력
    # 1) 슬래브 내부(Interior) 하중:
    # sigma_i = 0.275 * (1 + nu) * (P / h^2) * [ log10( (E*h^3) / (k*b_eq^4) ) - 0.54 ]
    # 등가 반경 b_eq = sqrt(1.6 * a^2 + h^2) - 0.675 * h (만약 a < 1.724 * h)
    if a < 1.724 * h:
        b_eq = math.sqrt(1.6 * (a**2) + (h**2)) - 0.675 * h
    else:
        b_eq = a
        
    term_log = math.log10((Ec * (h**3)) / (k * (b_eq**4)))
    sigma_interior = (0.275 * (1.0 + nu) * (P / (h**2))) * (term_log - 0.54)  # MPa
    
    # 2) 모서리(Corner) 하중:
    # sigma_c = (3 * P / h^2) * [ 1 - ( (a * sqrt(2)) / l )^0.6 ]
    sigma_corner = (3.0 * P / (h**2)) * (1.0 - ((a * math.sqrt(2.0)) / l_stiff)**0.6)  # MPa
    
    # 3) 가장자리(Edge) 하중:
    # sigma_e = 0.529 * (1 + 0.54 * nu) * (P / h^2) * [ log10( (E*h^3) / (k*b_eq^4) ) - 0.71 ]
    sigma_edge = (0.529 * (1.0 + 0.54 * nu) * (P / (h**2))) * (term_log - 0.71)  # MPa
    
    sigma_max = max(sigma_interior, sigma_corner, sigma_edge)
    
    # 3. 콘크리트 파괴계수(휨인장강도 fr) 및 허용 휨응력
    fr = 0.63 * math.sqrt(fck)  # MPa
    # 안전율 Fs = 1.7
    f_allow = fr / 1.7
    dcr_flexure = sigma_max / f_allow if f_allow > 0 else 999.0
    
    # 4. 수축/온도 균열 제어 최소 철근비 (0.15%)
    rho_min = 0.0015
    As_min_req = rho_min * 1000.0 * h  # mm2/m
    ab = 126.7 if data.rebar_dia == "D13" else 71.33
    As_prov = ab * (1000.0 / data.rebar_spacing)
    dcr_rebar = As_min_req / As_prov if As_prov > 0 else 999.0
    
    max_dcr = max(dcr_flexure, dcr_rebar)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "max_dcr": round(max_dcr, 3),
        "dcr_stress": round(dcr_flexure, 3),
        "dcr_rebar": round(dcr_rebar, 3),
        "sigma_interior_MPa": round(sigma_interior, 2),
        "sigma_corner_MPa": round(sigma_corner, 2),
        "sigma_edge_MPa": round(sigma_edge, 2),
        "f_allow_MPa": round(f_allow, 2),
        "radius_l_mm": round(l_stiff, 1),
        "As_prov_mm2_per_m": round(As_prov, 1),
        "summary": f"SOG 바닥슬래브: 최대휨응력={round(sigma_max,2)}MPa(허용 {round(f_allow,2)}MPa, DCR={round(dcr_flexure,2)}), 상대강성반경 l={round(l_stiff,0)}mm ({status})",
        "visual_data": {
            "type": "rc_slab",
            "thk": h,
            "span_x": data.joint_spacing,
            "span_y": data.joint_spacing,
            "rebar_top_x": f"{data.rebar_dia}@{int(data.rebar_spacing)}",
            "rebar_bot_x": "None"
        }
    }
