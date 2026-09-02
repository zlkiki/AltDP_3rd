"""강구조 엔드플레이트 모멘트 접합부 설계 엔진 (KDS 14 31 25 4.4.3)

Ground Truth:
  - decompiled_src/core_routines/steel/steel__CHK_USEP_*.c (CSTLCodeCheck::CHK_USEP)
  - decompiled_src/core_routines/steel/steel__CHK_USWB_*.c (CSTLCodeCheck::CHK_USWB)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional
from src.engine.steel.connection import BoltGrade, SteelConnectionEngine, BOLT_DB


class EndPlateType(str, Enum):
    """엔드플레이트 접합부 형식"""
    FLUSH = "FLUSH"                                  # 플러시 (비확장형)
    EXTENDED_4BOLT_UNSTIFFENED = "EXT_4B_UNSTIFF"    # 4볼트 비보강 확장형
    EXTENDED_4BOLT_STIFFENED = "EXT_4B_STIFF"        # 4볼트 거셋보강 확장형
    EXTENDED_8BOLT_STIFFENED = "EXT_8B_STIFF"        # 8볼트 보강 확장형


@dataclass
class EndPlateInput:
    """엔드플레이트 접합부 입력 데이터"""
    plate_type: EndPlateType = EndPlateType.EXTENDED_4BOLT_UNSTIFFENED
    
    # 보(Beam) 단면 치수 (mm) & 재료 (MPa)
    beam_d: float = 500.0              # 보 춤 db (mm)
    beam_bf: float = 200.0             # 보 플랜지 폭 bfb (mm)
    beam_tf: float = 16.0              # 보 플랜지 두께 tfb (mm)
    beam_tw: float = 10.0              # 보 웨브 두께 twb (mm)
    beam_fy: float = 275.0             # 보 강재 항복강도 Fyb (MPa)
    beam_fu: float = 400.0             # 보 강재 인장강도 Fub (MPa)
    
    # 기둥(Column) 단면 치수 (mm) & 재료 (MPa)
    col_d: float = 350.0               # 기둥 춤 dc (mm)
    col_bf: float = 350.0              # 기둥 플랜지 폭 bfc (mm)
    col_tf: float = 19.0               # 기둥 플랜지 두께 tfc (mm)
    col_tw: float = 12.0               # 기둥 웨브 두께 twc (mm)
    col_k: float = 32.0                # 기둥 k치수 (mm)
    col_fy: float = 275.0              # 기둥 강재 항복강도 Fyc (MPa)
    
    # 엔드플레이트 기하 치수 (mm) & 재료
    bp: float = 220.0                  # 엔드플레이트 폭 (mm)
    tp: float = 25.0                   # 엔드플레이트 두께 (mm)
    plate_fy: float = 275.0            # 플레이트 항복강도 Fyp (MPa)
    plate_fu: float = 400.0            # 플레이트 인장강도 Fup (MPa)
    pf: float = 50.0                   # 플랜지 내외측 볼트 피치 pf (mm)
    pext: float = 50.0                 # 외측 연단거리 pext (mm)
    g: float = 100.0                   # 볼트 게이지 g (mm)
    
    # 볼트 규격 및 개수
    bolt_size: str = "M24"             # 볼트 직경 (M20, M22, M24 등)
    bolt_grade: BoltGrade = BoltGrade.F10T
    num_tension_bolts: int = 4         # 인장 플랜지 측 볼트 수 (Ext 4-Bolt: 4개)
    num_shear_bolts: int = 4           # 웨브 전단 볼트 수
    
    # 설계 하중
    Mu: float = 250.0                  # 계수 휨모멘트 (kN·m)
    Vu: float = 120.0                  # 계수 전단력 (kN)
    Pu: float = 0.0                    # 계수 축력 (kN, 인장 +, 압축 -)


@dataclass
class EndPlateResult:
    """엔드플레이트 접합부 설계 검토 결과"""
    Tf: float                          # 플랜지 인장력 (kN)
    T_bolt_req: float                  # 단일 볼트 소요 인장력 (kN)
    phi_Rn_bolt: float                 # 단일 볼트 설계인장강도 (kN)
    dcr_bolt_tension: float            # 볼트 인장 DCR
    
    # 항복선 및 플레이트 휨
    yield_line_Y: float                # 항복선 파라미터 Y (mm)
    req_plate_tp: float                # 소요 플레이트 두께 tp,req (mm)
    dcr_plate_bending: float           # 플레이트 휨 DCR
    
    # 기둥 한계상태 강도 (kN)
    phi_Rn_col_flange_bending: float   # 기둥 플랜지 휨강도 (kN)
    phi_Rn_col_web_yielding: float     # 기둥 웨브 국부항복강도 (kN)
    phi_Rn_col_web_crippling: float    # 기둥 웨브 압괴강도 (kN)
    phi_Vn_col_panel_zone: float       # 기둥 패널존 전단강도 (kN)
    
    # DCR 종합
    dcr_col_flange_bending: float
    dcr_col_web_yielding: float
    dcr_col_web_crippling: float
    dcr_col_panel_zone: float
    dcr_shear: float
    governing_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class SteelEndPlateEngine:
    """KDS 14 31 25 4.4.3 엔드플레이트 모멘트 접합부 설계 솔버"""

    PHI_FLEXURE = 0.90
    PHI_TENSION = 0.75
    PHI_SHEAR = 0.90
    GAMMA_R = 1.10  # 연결부 초강도 계수

    @classmethod
    def calculate_yield_line_Y(cls, inp: EndPlateInput) -> float:
        """항복선 파라미터 Y (mm) 산정"""
        bp = inp.bp
        g = inp.g
        pf = inp.pf
        pext = inp.pext
        h1 = inp.beam_d - inp.beam_tf # 인장 플랜지-압축 플랜지 중심간 거리
        h0 = h1 + pf + pext           # 최외단 볼트-압축 플랜지 중심간 거리

        s = 0.5 * math.sqrt(bp * g)

        if inp.plate_type == EndPlateType.EXTENDED_4BOLT_UNSTIFFENED:
            # AISC / KDS 4볼트 비보강 확장형 수식
            # Y = (bp/2) * [ h1*(1/pf + 1/s) + h0*(1/pext) ] + (2/g) * [ h1*(pf + s) ]
            term1 = (bp / 2.0) * (h1 / pf + h1 / max(1.0, s) + h0 / max(1.0, pext))
            term2 = (2.0 / max(1.0, g)) * (h1 * (pf + s))
            Y = term1 + term2
        elif inp.plate_type == EndPlateType.EXTENDED_4BOLT_STIFFENED:
            # 보강 리브 추가 시 유효 항복선 증대 (~1.25x)
            term1 = (bp / 2.0) * (h1 / pf + h1 / max(1.0, s) + h0 / max(1.0, pext))
            term2 = (2.0 / max(1.0, g)) * (h1 * (pf + s))
            Y = (term1 + term2) * 1.25
        elif inp.plate_type == EndPlateType.EXTENDED_8BOLT_STIFFENED:
            # 8볼트 확장형 (내외측 2열)
            term1 = (bp / 2.0) * (h1 / pf + h1 / max(1.0, s) + h0 / max(1.0, pext)) * 1.8
            term2 = (2.0 / max(1.0, g)) * (h1 * (pf + s)) * 1.8
            Y = term1 + term2
        else: # FLUSH
            # 플러시형: 내측 볼트만 기여
            Y = (bp / 2.0) * (h1 / pf + h1 / max(1.0, s)) + (2.0 / max(1.0, g)) * (h1 * (pf + s))

        return max(100.0, Y)

    @classmethod
    def check_end_plate(cls, inp: EndPlateInput) -> EndPlateResult:
        """엔드플레이트 모멘트 접합부 전수 설계 검토"""
        messages = []
        d_eff = max(10.0, inp.beam_d - inp.beam_tf)

        # 1. 보 플랜지 소요 인장력 Tf (kN)
        # Tf = Mu / (db - tfb) + Pu / 2
        Tf = (abs(inp.Mu) * 1000.0) / d_eff + (inp.Pu / 2.0)
        Tf = max(0.0, Tf)

        # 2. 볼트 인장력 및 강도 검토
        d, ab, fnt, _, _, fu = SteelConnectionEngine.get_bolt_props(inp.bolt_size, inp.bolt_grade)
        n_bt = max(1, inp.num_tension_bolts)
        T_bolt_req = Tf / n_bt # 볼트 1개당 인장력 (지레작용 미포함 기준)

        # 볼트 설계인장강도 phi_Rn
        phi_Rn_bolt = cls.PHI_TENSION * (fnt * ab) / 1000.0 # kN
        dcr_bolt_tension = T_bolt_req / max(1e-4, phi_Rn_bolt)

        # 3. 항복선 이론에 따른 소요 엔드플레이트 두께 tp,req
        Y = cls.calculate_yield_line_Y(inp)
        # tp,req = sqrt( 1.11 * gamma_r * Mu * 1e6 / (phi * Fyp * Y) )
        mu_nmm = abs(inp.Mu) * 1e6 # N*mm
        tp_req_sq = (1.11 * cls.GAMMA_R * mu_nmm) / (cls.PHI_FLEXURE * inp.plate_fy * Y)
        tp_req = math.sqrt(max(0.0, tp_req_sq))

        dcr_plate_bending = (tp_req / max(1.0, inp.tp)) ** 2

        # 4. 기둥 플랜지 휨 (Column Flange Bending)
        # phi_Rn = 0.90 * (6.25 * Fyc * tfc^2)
        phi_Rn_col_flange_bending = cls.PHI_FLEXURE * (6.25 * inp.col_fy * (inp.col_tf ** 2)) / 1000.0 # kN
        dcr_col_flange_bending = Tf / max(1e-4, phi_Rn_col_flange_bending)

        # 5. 기둥 웨브 국부항복 (Column Web Local Yielding)
        # phi_Rn = 1.0 * Fyc * twc * (5k + N)
        N_bearing = inp.beam_tf + 2.0 * inp.tp # 지압길이 N
        phi_Rn_col_web_yielding = 1.0 * (inp.col_fy * inp.col_tw * (5.0 * inp.col_k + N_bearing)) / 1000.0 # kN
        dcr_col_web_yielding = Tf / max(1e-4, phi_Rn_col_web_yielding)

        # 6. 기둥 웨브 압괴 (Column Web Crippling)
        # phi_Rn = 0.75 * 0.80 * twc^2 * sqrt( E * Fyc * tfc / twc )
        E_mod = 205000.0 # MPa
        term_crip = math.sqrt((E_mod * inp.col_fy * inp.col_tf) / max(1.0, inp.col_tw))
        phi_Rn_col_web_crippling = 0.75 * (0.80 * (inp.col_tw ** 2) * term_crip) / 1000.0 # kN
        dcr_col_web_crippling = Tf / max(1e-4, phi_Rn_col_web_crippling)

        # 7. 기둥 패널존 전단 (Column Panel Zone Shear)
        # phi_Vn = 0.90 * 0.60 * Fyc * dc * twc * [ 1 + (3 bfc tfc^2)/(db dc twc) ]
        factor_pz = 1.0 + (3.0 * inp.col_bf * (inp.col_tf ** 2)) / max(1.0, inp.beam_d * inp.col_d * inp.col_tw)
        phi_Vn_col_panel_zone = cls.PHI_SHEAR * (0.60 * inp.col_fy * inp.col_d * inp.col_tw * factor_pz) / 1000.0 # kN
        # 패널존 소요전단력 Vpz = Tf - Vcol (간략히 Tf 기준)
        dcr_col_panel_zone = Tf / max(1e-4, phi_Vn_col_panel_zone)

        # 8. 전단 볼트 DCR
        n_sv = max(1, inp.num_shear_bolts)
        _, _, _, fnv_inc, _, _ = SteelConnectionEngine.get_bolt_props(inp.bolt_size, inp.bolt_grade)
        phi_Vn_shear_bolts = cls.PHI_TENSION * (fnv_inc * ab * n_sv) / 1000.0 # kN
        dcr_shear = abs(inp.Vu) / max(1e-4, phi_Vn_shear_bolts)

        # 종합 DCR
        all_dcrs = [
            dcr_bolt_tension,
            dcr_plate_bending,
            dcr_col_flange_bending,
            dcr_col_web_yielding,
            dcr_col_web_crippling,
            dcr_col_panel_zone,
            dcr_shear
        ]
        governing_dcr = max(all_dcrs)

        if inp.tp < tp_req:
            messages.append(f"엔드플레이트 두께 tp({inp.tp}mm)가 소요두께({tp_req:.1f}mm) 미달")
        if dcr_col_flange_bending > 1.0:
            messages.append("기둥 플랜지 국부휨 보강(연속판 Stiffener) 필요")
        if dcr_col_web_yielding > 1.0 or dcr_col_web_crippling > 1.0:
            messages.append("기둥 웨브 보강(더블러 플레이트 Doubler Plate) 필요")

        return EndPlateResult(
            Tf=round(Tf, 2),
            T_bolt_req=round(T_bolt_req, 2),
            phi_Rn_bolt=round(phi_Rn_bolt, 2),
            dcr_bolt_tension=round(dcr_bolt_tension, 4),
            yield_line_Y=round(Y, 1),
            req_plate_tp=round(tp_req, 2),
            dcr_plate_bending=round(dcr_plate_bending, 4),
            phi_Rn_col_flange_bending=round(phi_Rn_col_flange_bending, 2),
            phi_Rn_col_web_yielding=round(phi_Rn_col_web_yielding, 2),
            phi_Rn_col_web_crippling=round(phi_Rn_col_web_crippling, 2),
            phi_Vn_col_panel_zone=round(phi_Vn_col_panel_zone, 2),
            dcr_col_flange_bending=round(dcr_col_flange_bending, 4),
            dcr_col_web_yielding=round(dcr_col_web_yielding, 4),
            dcr_col_web_crippling=round(dcr_col_web_crippling, 4),
            dcr_col_panel_zone=round(dcr_col_panel_zone, 4),
            dcr_shear=round(dcr_shear, 4),
            governing_dcr=round(governing_dcr, 4),
            is_safe=(governing_dcr <= 1.0),
            messages=messages
        )
