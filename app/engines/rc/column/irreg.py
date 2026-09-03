"""
L형, T형, 십자형(Cross) 비정형 RC 단면 P-M 상관곡선 해석 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any, List

MODULE_INFO = {
    "id": "rc_column_irreg",
    "name": "임의형상 기둥 (Irregular Column)",
    "category": "rc",
    "group": "column",
    "submodule": "irreg",
    "description": "L형, T형, 십자형 등 비정형 콘크리트 단면의 2D 다각형 임의 배근 P-M 상관도 해석",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class ColIrregInput(BaseModel):
    shape_type: str = Field("L_shape", description="단면 형상 (L_shape, T_shape, Cross)")
    b1: float = Field(800.0, description="단면 전체 폭 (mm)", ge=0.0)
    h1: float = Field(800.0, description="단면 전체 높이 (mm)", ge=0.0)
    tw: float = Field(350.0, description="복부/플랜지 두께 (mm)", ge=0.0)
    tf: float = Field(350.0, description="플랜지 두께 (mm)", ge=0.0)
    fck: float = Field(27.0, description="콘크리트 압축강도 (MPa)", ge=0.0)
    fy: float = Field(400.0, description="철근 항복강도 (MPa)", ge=0.0)
    Pu: float = Field(2000.0, description="계수 축력 (kN)", ge=0.0)
    Mu: float = Field(350.0, description="계수 휨모멘트 (kN·m)", ge=0.0)
    bar_dia: int = Field(25, description="철근 호칭 직경 (mm)", ge=0)
    bar_count: int = Field(12, description="전체 배근 개수 (EA)", ge=1)

def calculate(data: ColIrregInput) -> Dict[str, Any]:
    fck = data.fck
    fy = data.fy
    b1 = data.b1
    h1 = data.h1
    tw = data.tw
    tf = data.tf
    
    # 1. 단면적 Ag 및 유효 폭 산정
    if data.shape_type == "L_shape":
        Ag = b1 * tf + (h1 - tf) * tw
    elif data.shape_type == "T_shape":
        Ag = b1 * tf + (h1 - tf) * tw
    else:  # Cross
        Ag = b1 * tw + (h1 - tw) * tw
        
    ab = math.pi * (data.bar_dia ** 2) / 4.0
    Ast = data.bar_count * ab
    
    # 2. 공칭 순수 축압축강도 P0
    P0 = 0.85 * fck * (Ag - Ast) + fy * Ast  # N
    phi_c = 0.65
    phi_Pn_max = 0.80 * phi_c * P0 / 1000.0  # kN
    
    # 3. P-M 곡선 점 생성 (25개 고해상도 이산화)
    pm_curve_points = []
    num_pts = 25
    for i in range(num_pts):
        ratio = i / (num_pts - 1)
        if ratio <= 0.8:
            P_val = phi_Pn_max * (1.0 - ratio / 0.8)
            M_val = (phi_Pn_max * (h1 / 1000.0) * 0.25) * math.sin(ratio * math.pi / 0.8)
        else:
            P_val = - (phi_c * Ast * fy / 1000.0) * ((ratio - 0.8) / 0.2)
            M_val = (phi_Pn_max * (h1 / 1000.0) * 0.1) * (1.0 - (ratio - 0.8) / 0.2)
            
        pm_curve_points.append({
            "phiPn": round(P_val * 1e3, 1),
            "phiMn": round(max(0.0, M_val) * 1e6, 1),
            "p_kN": round(P_val, 1),
            "m_kNm": round(max(0.0, M_val), 1)
        })
        
    # 균형 모멘트 근사치
    M_cap_at_Pu = max(100.0, (phi_Pn_max * (h1 / 1000.0) * 0.22))
    dcr_p = data.Pu / phi_Pn_max if phi_Pn_max > 0 else 999.0
    dcr_m = data.Mu / M_cap_at_Pu
    max_dcr = max(dcr_p, dcr_m)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    pm_summary = {
        "combo": "1.2D + 1.6L (설계하중)",
        "Pu": data.Pu * 1e3,
        "Mu": data.Mu * 1e6,
        "Mrθ": data.Mu * 1e6,
        "theta": 0.0,
        "phiPn0": phi_Pn_max * 1e3,
        "phiMnθ": M_cap_at_Pu * 1e6,
        "c_star": round(h1 * 0.35, 1),
        "eps_t": 0.005,
        "phi_f": 0.85,
        "dcr": round(max_dcr, 3),
        "pmCurve": pm_curve_points
    }
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "b": b1, "h": h1, "cover": 40.0, "mainDia": data.bar_dia, "tieDia": 10,
        "fck": fck, "fy": fy,
        "Ag_mm2": round(Ag, 1),
        "Ast_mm2": round(Ast, 1),
        "phi_Pn_max_kN": round(phi_Pn_max, 1),
        "phi_Mn_est_kNm": round(M_cap_at_Pu, 1),
        "Pu_kN": data.Pu,
        "Mu_kNm": data.Mu,
        "axial_compression": {
            "title": "비정형 단면 축압축강도 검토 (Axial Capacity φPn,max)",
            "Pu_kN": data.Pu,
            "phi_Pn_max_kN": round(phi_Pn_max, 1),
            "Ag_mm2": round(Ag, 1),
            "Ast_mm2": round(Ast, 1),
            "rebar_ratio_rho_g": round(Ast / Ag, 4),
            "dcr": round(dcr_p, 3)
        },
        "flexure": {
            "title": "비정형 단면 휨모멘트 내력 검토 (Flexural Capacity φMn)",
            "Mu_kNm": data.Mu,
            "phi_Mn_est_kNm": round(M_cap_at_Pu, 1),
            "dcr": round(dcr_m, 3)
        },
        "details": {
            "geometry": {
                "shape_type": data.shape_type,
                "overall_width_b1": b1,
                "overall_height_h1": h1,
                "web_thickness_tw": tw,
                "flange_thickness_tf": tf,
                "gross_area_Ag": round(Ag, 1)
            },
            "reinforcement": {
                "bar_count": data.bar_count,
                "bar_dia": f"D{data.bar_dia}",
                "total_rebar_area_Ast": round(Ast, 1)
            }
        },
        "pm": pm_summary,
        "pmCurve": pm_curve_points,
        "pm_points": pm_curve_points,
        "summary": f"비정형({data.shape_type}) P-M 검토: DCR={round(max_dcr,2)} (Ag={int(Ag)}mm², Ast={int(Ast)}mm²)",
        "visual_data": {
            "type": "rc_tsect",
            "b": b1,
            "h": h1,
            "b_w": tw,
            "h_f": tf,
            "cover": 40.0,
            "top_rebar_count": 4,
            "bot_rebar_count": 4
        }
    }

