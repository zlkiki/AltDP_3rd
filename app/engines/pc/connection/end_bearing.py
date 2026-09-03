"""
포스트텐션/PC 부재 단부 텐던 정착구역(Anchorage Zone) 국부 지압 및 할렬(Bursting) 철근 설계 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "pc_connection_end_bearing",
    "name": "PC 단부 지압·정착구 (End Bearing & Anchor)",
    "category": "pc",
    "group": "connection",
    "submodule": "end_bearing",
    "description": "KDS 14 20 60 포스트텐션 정착판 국부 지압 응력 및 일반구역(General Zone) 할렬 인장철근(Bursting Rebar) 설계",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class EndBearingInput(BaseModel):
    b_member: float = Field(500.0, description="부재 단면 폭 (mm)")
    h_member: float = Field(800.0, description="부재 단면 높이 (mm)")
    fci: float = Field(28.0, description="긴장 시 콘크리트 압축강도 (MPa)")
    fy: float = Field(400.0, description="할렬 철근 항복강도 (MPa)")
    P_jacking: float = Field(1200.0, description="최대 인장 긴장력 Pj (kN)")
    anchor_b: float = Field(220.0, description="정착판 폭 (mm)")
    anchor_h: float = Field(220.0, description="정착판 높이 (mm)")
    rebar_dia: str = Field("D13", description="할렬 보강근 규격")

def calculate(data: EndBearingInput) -> Dict[str, Any]:
    b = data.b_member
    h = data.h_member
    fci = data.fci
    fy = data.fy
    Pj = data.P_jacking * 1e3  # N
    a_b = data.anchor_b
    a_h = data.anchor_h
    
    # 1. 국부구역(Local Zone) 지압강도 검토
    A1 = a_b * a_h  # 정착판 지압면적
    # 최대 유효 면적 A2 (정착판과 상사형)
    ratio_b = b / a_b
    ratio_h = h / a_h
    scale = min(ratio_b, ratio_h, 2.0)
    A2 = A1 * (scale**2)
    
    # 허용 지압응력 f_b_allow = 0.7 * phi * fci * sqrt(A2/A1) (최대 1.5 * phi * fci)
    phi_bearing = 0.65
    f_b_allow = min(0.7 * phi_bearing * fci * math.sqrt(A2 / A1), 1.5 * phi_bearing * fci)
    # 실제 지압응력 fb = Pj / A1
    fb_act = Pj / A1
    dcr_bearing = fb_act / f_b_allow if f_b_allow > 0 else 999.0
    
    # 2. 일반구역(General Zone) 할렬력(Bursting Force) F_bst 산정 (KDS 식)
    # F_bst = 0.25 * Pj * (1 - a_h / h)
    F_bst = 0.25 * Pj * (1.0 - a_h / h)  # N
    
    # 3. 필요 할렬 철근량 As_bst
    phi_s = 0.85
    As_bst_req = F_bst / (phi_s * fy)  # mm2
    
    ab_burst = 126.7 if data.rebar_dia == "D13" else 201.1
    # 2Leg 폐쇄형 스터럽 가정
    n_ties = math.ceil(As_bst_req / (2.0 * ab_burst))
    As_bst_prov = n_ties * 2.0 * ab_burst
    dcr_bursting = As_bst_req / As_bst_prov if As_bst_prov > 0 else 999.0
    
    # 4. 파열력 발생 구간 (단부로부터 0.2h ~ 1.0h 구간에 균등 배치)
    zone_start = 0.2 * h
    zone_end = 1.0 * h
    
    max_dcr = max(dcr_bearing, dcr_bursting)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "soil_bearing": {
            "title": "국부 지압응력 검토 (Local Zone Bearing Capacity)",
            "fb_act_MPa": round(fb_act, 1),
            "fb_allow_MPa": round(f_b_allow, 1),
            "dcr": round(dcr_bearing, 3),
            "phi": phi_bearing
        },
        "flexure": {
            "title": "일반구역 할렬력 및 파열 철근 검토 (Bursting Force & Rebar)",
            "F_bursting_kN": round(F_bst / 1000.0, 1),
            "As_burst_req_mm2": round(As_bst_req, 1),
            "As_burst_prov_mm2": round(As_bst_prov, 1),
            "dcr": round(dcr_bursting, 3),
            "phi": phi_s
        },
        "details": {
            "bearing_geometry": {
                "anchor_plate_b_mm": a_b,
                "anchor_plate_h_mm": a_h,
                "bearing_area_A1_mm2": round(A1, 0),
                "effective_area_A2_mm2": round(A2, 0),
                "confinement_ratio_sqrt_A2_A1": round(math.sqrt(A2 / A1), 2)
            },
            "bursting_zone": {
                "bursting_force_Fbst_kN": round(F_bst / 1000.0, 1),
                "zone_start_mm": round(zone_start, 0),
                "zone_end_mm": round(zone_end, 0),
                "tie_arrangement": f"{n_ties}-폐쇄형 {data.rebar_dia}"
            }
        },
        "summary": f"정착구역 검토: 국부지압 DCR={round(dcr_bearing,2)}, 할렬력={round(F_bst/1000,1)}kN (필요철근 {n_ties}-2Leg {data.rebar_dia}) ({status})",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "cover": 40.0
        }
    }
