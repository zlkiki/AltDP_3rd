"""
RC 보 복부 원형/사각형 개구부(Web Opening) 비렌딜(Vierendeel) 전단 및 휨 검토 모듈
"""
import math
from pydantic import BaseModel, Field
from typing import Dict, Any

MODULE_INFO = {
    "id": "rc_beam_open",
    "name": "보 웨브 보강 (Web Opening RC Beam)",
    "category": "rc",
    "group": "beam",
    "submodule": "open",
    "description": "RC 보 복부 개구부 상·하현재 비렌딜(Vierendeel) 전단 및 보강근 검토",
    "geomType": "rc_rect",
    "template": "rc_rect"
}

class BeamOpenInput(BaseModel):
    b: float = Field(400.0, description="보 폭 (mm)", ge=0.0)
    h: float = Field(700.0, description="보 춤 (mm)", ge=0.0)
    fck: float = Field(24.0, description="콘크리트 압축강도 (MPa)", ge=0.0)
    fy: float = Field(400.0, description="주철근 항복강도 (MPa)", ge=0.0)
    fys: float = Field(400.0, description="전단보강근 항복강도 (MPa)", ge=0.0)
    Mu: float = Field(250.0, description="개구부 중심 계수 모멘트 (kN·m)", ge=0.0)
    Vu: float = Field(180.0, description="개구부 계수 전단력 (kN)", ge=0.0)
    open_shape: str = Field("circle", description="개구부 형태 (circle/rect)")
    open_size: float = Field(250.0, description="개구부 직경 또는 높이 (mm)", ge=0.0)
    open_width: float = Field(250.0, description="개구부 폭(직사각형인 경우) (mm)", ge=0.0)
    
    top_rebar_num: int = Field(4, description="상부 주근 개수 (EA)", ge=0)
    top_rebar_dia: int = Field(25, description="상부 주근 직경 (mm)", ge=0)
    bot_rebar_num: int = Field(4, description="하부 주근 개수 (EA)", ge=0)
    bot_rebar_dia: int = Field(25, description="하부 주근 직경 (mm)", ge=0)
    diag_rebar_num: int = Field(4, description="개구부 경사 보강근 개수 (EA)", ge=0)
    diag_rebar_dia: int = Field(16, description="개구부 경사 보강근 직경 (mm)", ge=0)

def calculate(data: Any) -> Dict[str, Any]:
    get_v = lambda k, default: data.get(k, default) if isinstance(data, dict) else getattr(data, k, default)
    
    b = float(get_v("b", 400.0))
    h = float(get_v("h", 700.0))
    fck = float(get_v("fck", 24.0))
    fy = float(get_v("fy", 400.0))
    fys = float(get_v("fys", 400.0))
    Mu = float(get_v("Mu", 250.0)) * 1e6
    Vu = float(get_v("Vu", 180.0)) * 1e3
    open_shape = str(get_v("open_shape", "circle"))
    open_size = float(get_v("open_size", 250.0))
    open_width = float(get_v("open_width", 250.0))
    
    # 철근 수량 및 직경 파싱 (문자열 호환성 포함)
    top_num = int(get_v("top_rebar_num", 4))
    top_dia = int(get_v("top_rebar_dia", 25))
    bot_num = int(get_v("bot_rebar_num", 4))
    bot_dia = int(get_v("bot_rebar_dia", 25))
    diag_num = int(get_v("diag_rebar_num", 4))
    diag_dia = int(get_v("diag_rebar_dia", 16))
    
    # 1. 개구부 상·하현재(Chord) 기하 분할
    ho = open_size
    ht = (h - ho) / 2.0  # 상현재 높이
    hb = (h - ho) / 2.0  # 하현재 높이
    dt = ht - 40.0
    db = hb - 40.0
    
    # 2. 비렌딜 전단 분배 (상현재 Vt, 하현재 Vb)
    Vt = Vu * 0.5
    Vb = Vu * 0.5
    
    # 3. 콘크리트 전단강도 저감 (개구부 주변)
    phi_v = 0.75
    Vct = 0.5 * (1.0 / 6.0) * math.sqrt(fck) * b * dt if dt > 0 else 0.0
    Vcb = 0.5 * (1.0 / 6.0) * math.sqrt(fck) * b * db if db > 0 else 0.0
    
    # 4. 경사 보강근(Diagonal Rebar) 기여도 Vd
    Asd = diag_num * (math.pi * diag_dia * diag_dia / 4.0)
    alpha = 45.0 * math.pi / 180.0
    Vd = phi_v * Asd * fys * math.sin(alpha)
    
    # 전단 내력 산정
    phi_Vnt = phi_v * Vct + Vd * 0.5
    phi_Vnb = phi_v * Vcb + Vd * 0.5
    
    dcr_vt = Vt / phi_Vnt if phi_Vnt > 0 else 999.0
    dcr_vb = Vb / phi_Vnb if phi_Vnb > 0 else 999.0
    
    # 5. 비렌딜 국부 모멘트 검토 (M_local = V_chord * (ho_width / 2))
    w_open = open_width if open_shape == "rect" else open_size
    Mt_local = Vt * (w_open / 2.0)
    phi_m = 0.85
    
    # 상현재 휨내력 근사치
    As_top_chord = (top_num / 2.0) * (math.pi * top_dia * top_dia / 4.0)
    phi_Mnt = phi_m * As_top_chord * fy * max(10.0, dt - 20.0)  # N*mm
    dcr_mt = Mt_local / phi_Mnt if phi_Mnt > 0 else 999.0
    
    max_dcr = max(dcr_vt, dcr_vb, dcr_mt)
    status = "OK" if max_dcr <= 1.0 else "NG"
    
    diag_str = f"{diag_num}-D{diag_dia}"
    top_str = f"{top_num}-D{top_dia}"
    bot_str = f"{bot_num}-D{bot_dia}"
    
    return {
        "status": status,
        "governing_dcr": round(max_dcr, 3),
        "max_dcr": round(max_dcr, 3),
        "dcr_shear_top": round(dcr_vt, 3),
        "dcr_shear_bot": round(dcr_vb, 3),
        "dcr_moment_top": round(dcr_mt, 3),
        "phi_Vn_total_kN": round((phi_Vnt + phi_Vnb) / 1000.0, 1),
        "Vd_kN": round(Vd / 1000.0, 1),
        "shear": {
            "title": "비렌딜 전단내력 검토 (Vierendeel Shear Capacity φVn)",
            "Vu_total_kN": round(Vu / 1000.0, 1),
            "Vt_top_kN": round(Vt / 1000.0, 1),
            "phi_Vnt_kN": round(phi_Vnt / 1000.0, 1),
            "dcr_top": round(dcr_vt, 3),
            "Vb_bot_kN": round(Vb / 1000.0, 1),
            "phi_Vnb_kN": round(phi_Vnb / 1000.0, 1),
            "dcr_bot": round(dcr_vb, 3),
            "dcr": round(max(dcr_vt, dcr_vb), 3)
        },
        "flexure": {
            "title": "현재 국부 휨모멘트 검토 (Local Chord Moment φMn)",
            "Mt_local_kNm": round(Mt_local / 1e6, 2),
            "phi_Mnt_kNm": round(phi_Mnt / 1e6, 2),
            "dcr": round(dcr_mt, 3)
        },
        "details": {
            "geometry": {
                "open_shape": open_shape,
                "open_size_mm": ho,
                "chord_height_ht_mm": round(ht, 1),
                "chord_height_hb_mm": round(hb, 1)
            },
            "reinforcement": {
                "top_rebar": top_str,
                "bot_rebar": bot_str,
                "diag_rebar": diag_str,
                "diag_area_Asd_mm2": round(Asd, 1),
                "diag_contribution_Vd_kN": round(Vd / 1000.0, 1)
            }
        },
        "summary": f"복부 개구부 Vierendeel 검토: DCR(전단)={round(max(dcr_vt, dcr_vb),2)}, DCR(국부휨)={round(dcr_mt,2)} ({status})",
        "visual_data": {
            "type": "rc_rect",
            "b": b,
            "h": h,
            "open_size": ho,
            "open_shape": open_shape,
            "cover": 40.0
        }
    }
