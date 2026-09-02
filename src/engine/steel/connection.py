"""강구조 볼트 및 용접 접합부 설계 엔진 (KDS 14 31 25)

Ground Truth:
  - decompiled_src/core_routines/steel/steel__CHK_USBC_*.c (CSTLCodeCheck::CHK_USBC)
  - decompiled_src/core_routines/steel/steel__CHK_USWE_*.c (CSTLCodeCheck::CHK_USWE)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple


class BoltGrade(str, Enum):
    """고장력 볼트 등급"""
    F10T = "F10T"      # Fu = 1000 MPa
    TS10T = "TS10T"    # Fu = 1000 MPa (Torque-Shear)
    A325 = "A325"      # Fu = 825 MPa (d <= M24), 725 MPa (d > M24)
    A490 = "A490"      # Fu = 1035 MPa
    GRADE_8_8 = "8.8"  # Fu = 800 MPa
    GRADE_10_9 = "10.9"# Fu = 1000 MPa


class JointType(str, Enum):
    """접합 방식"""
    BEARING = "BEARING"       # 지압접합 (Bearing-Type)
    SLIP_CRITICAL = "SLIP"    # 마찰접합 (Slip-Critical)


class HoleType(str, Enum):
    """구멍 종류"""
    STANDARD = "STANDARD"          # 표준 구멍
    OVERSIZED = "OVERSIZED"        # 대형 구멍
    SHORT_SLOT = "SHORT_SLOT"      # 단슬롯
    LONG_SLOT = "LONG_SLOT"        # 장슬롯


class WeldType(str, Enum):
    """용접 종류"""
    FILLET = "FILLET"  # 필릿용접
    CJP = "CJP"        # 완전용입 그루브용접
    PJP = "PJP"        # 부분용입 그루브용접


# 볼트 표준 규격 DB (직경 d -> 공칭 단면적 mm², 설계볼트장력 T0 kN)
BOLT_DB: Dict[str, Dict[str, float]] = {
    "M16": {"d": 16.0, "area": 201.1, "T0_F10T": 100.0, "T0_A325": 85.0, "T0_A490": 107.0, "dh": 18.0},
    "M20": {"d": 20.0, "area": 314.2, "T0_F10T": 157.0, "T0_A325": 133.0, "T0_A490": 167.0, "dh": 22.0},
    "M22": {"d": 22.0, "area": 380.1, "T0_F10T": 195.0, "T0_A325": 165.0, "T0_A490": 205.0, "dh": 24.0},
    "M24": {"d": 24.0, "area": 452.4, "T0_F10T": 227.0, "T0_A325": 192.0, "T0_A490": 240.0, "dh": 26.0},
    "M27": {"d": 27.0, "area": 572.6, "T0_F10T": 295.0, "T0_A325": 246.0, "T0_A490": 310.0, "dh": 30.0},
    "M30": {"d": 30.0, "area": 706.9, "T0_F10T": 360.0, "T0_A325": 301.0, "T0_A490": 379.0, "dh": 33.0},
}


@dataclass
class BoltGroupInput:
    """볼트군 설계 입력 데이터"""
    bolt_size: str = "M20"               # 볼트 규격 (M16 ~ M30)
    grade: BoltGrade = BoltGrade.F10T    # 볼트 등급
    joint_type: JointType = JointType.BEARING  # 지압접합 or 마찰접합
    hole_type: HoleType = HoleType.STANDARD    # 구멍 종류
    num_bolts: int = 4                  # 총 볼트 개수
    num_shear_planes: int = 1            # 전단면 수 (1: 단일전단, 2: 이중전단)
    threads_included: bool = True       # 나사부 전단면 포함 여부
    
    # 지압 및 배치 기하조건 (mm)
    plate_thickness: float = 10.0       # 연결판/모재 두께 t
    plate_fu: float = 400.0             # 연결판 인장강도 Fu (MPa)
    plate_fy: float = 275.0             # 연결판 항복강도 Fy (MPa)
    edge_distance: float = 40.0         # 힘 방향 연단거리 Le (mm)
    pitch: float = 60.0                 # 힘 방향 볼트간격 s (mm)
    gauge: float = 70.0                 # 힘 직각방향 게이지 g (mm)
    rows: int = 2                       # 힘 방향 열(row) 수
    cols: int = 2                       # 힘 직각방향 행(col) 수
    
    # 마찰접합 파라미터
    slip_coefficient: float = 0.33      # 미끄럼계수 mu (Class A: 0.33, Class B: 0.50)
    du: float = 1.13                    # 볼트 조임력 계수
    
    # 소요 하중 (kN)
    Vu: float = 100.0                   # 계수 전단력 (kN)
    Tu: float = 0.0                     # 계수 인장력 (kN)
    
    # 사용성 변형 고려 여부 (True: 1.2Lc, False: 1.5Lc)
    deformation_considered: bool = True


@dataclass
class BlockShearInput:
    """블록전단파단 설계 입력 데이터 (KDS 14 31 25 4.1.3)"""
    Agv: float                          # 전단 총단면적 (mm²)
    Anv: float                          # 전단 순단면적 (mm²)
    Ant: float                          # 인장 순단면적 (mm²)
    Fu: float = 400.0                   # 인장강도 (MPa)
    Fy: float = 275.0                   # 항복강도 (MPa)
    Ubs: float = 1.0                    # 인장응력 균일도 계수 (1.0 또는 0.5)
    Pu: float = 100.0                   # 계수 인장력 (kN)


@dataclass
class WeldJointInput:
    """용접 접합부 설계 입력 데이터 (KDS 14 31 25 4.2)"""
    weld_type: WeldType = WeldType.FILLET  # 용접 종류
    leg_size: float = 6.0               # 필릿용접 다리길이 s (mm)
    length: float = 200.0               # 용접선 길이 Lw (mm)
    Fexx: float = 490.0                 # 용접봉 공칭인장강도 (MPa, E70XX/E49XX = 490 MPa)
    base_fu: float = 400.0              # 모재 인장강도 (MPa)
    base_thickness: float = 10.0        # 모재 두께 (mm)
    Vu: float = 100.0                   # 계수 전단력 (kN)


@dataclass
class BoltGroupResult:
    """볼트군 설계 결과"""
    phi_Rn_shear_single: float          # 단일 볼트 설계전단강도 (kN)
    phi_Rn_shear_total: float           # 볼트군 총 설계전단강도 (kN)
    phi_Rn_tension_single: float        # 단일 볼트 설계인장강도 (kN)
    phi_Rn_tension_total: float         # 볼트군 총 설계인장강도 (kN)
    phi_Rn_bearing_single: float        # 단일 볼트 구멍 설계지압강도 (kN)
    phi_Rn_bearing_total: float         # 볼트군 총 설계지압강도 (kN)
    phi_Rn_slip_total: float            # 볼트군 설계미끄럼강도 (kN, 마찰접합)
    dcr_shear: float                    # 전단 DCR
    dcr_tension: float                  # 인장 DCR
    dcr_bearing: float                  # 지압 DCR
    dcr_combined: float                 # 전단-인장 복합 DCR
    governing_dcr: float                # 지배 DCR
    is_safe: bool                       # 안전 여부 (DCR <= 1.0)
    messages: List[str] = field(default_factory=list)


@dataclass
class BlockShearResult:
    """블록전단 파단강도 결과"""
    Rn_rupture: float                   # 전단파단 + 인장파단 강도 (kN)
    Rn_yield: float                     # 전단항복 + 인장파단 상한치 (kN)
    phi_Rn: float                       # 설계 블록전단강도 (kN)
    dcr: float                          # 블록전단 DCR
    is_safe: bool                       # 안전 여부
    governing_mode: str                 # 지배 파괴모드


@dataclass
class WeldJointResult:
    """용접 접합부 설계 결과"""
    throat: float                       # 유효 목두께 (mm)
    effective_length: float             # 유효 용접길이 (mm)
    phi_Rn_weld: float                  # 용접부 설계강도 (kN)
    phi_Rn_base: float                  # 모재 전단 설계강도 (kN)
    phi_Rn: float                       # 최종 지배 설계강도 (kN)
    dcr: float                          # DCR
    is_safe: bool                       # 안전 여부


class SteelConnectionEngine:
    """KDS 14 31 25 강구조 접합부 설계 해석기"""

    # 강도감소계수 (LRFD)
    PHI_BOLT_SHEAR = 0.75
    PHI_BOLT_TENSION = 0.75
    PHI_BEARING = 0.75
    PHI_BLOCK_SHEAR = 0.75
    PHI_WELD = 0.75

    @classmethod
    def get_bolt_props(cls, size: str, grade: BoltGrade) -> Tuple[float, float, float, float]:
        """볼트 공칭 직경, 단면적, Fnt, Fnv 반환 (d, Ab, Fnt, Fnv, Fu)"""
        info = BOLT_DB.get(size, BOLT_DB["M20"])
        d = info["d"]
        ab = info["area"]

        # 볼트 재료 강도 (MPa)
        if grade in (BoltGrade.F10T, BoltGrade.TS10T, BoltGrade.GRADE_10_9):
            fu = 1000.0
            fnt = 0.75 * fu  # 750 MPa (KDS 기준 620~750 MPa)
            fnv_inc = 0.45 * fu  # 450 MPa
            fnv_exc = 0.563 * fu # 563 MPa
        elif grade == BoltGrade.A490:
            fu = 1035.0
            fnt = 0.75 * fu  # 776.25 MPa
            fnv_inc = 470.0
            fnv_exc = 580.0
        elif grade == BoltGrade.A325:
            fu = 825.0 if d <= 24.0 else 725.0
            fnt = 0.75 * fu
            fnv_inc = 372.0
            fnv_exc = 457.0
        else: # GRADE_8_8
            fu = 800.0
            fnt = 0.75 * fu  # 600 MPa
            fnv_inc = 0.45 * fu  # 360 MPa
            fnv_exc = 0.563 * fu # 450 MPa

        return d, ab, fnt, fnv_inc, fnv_exc, fu

    @classmethod
    def check_bolt_group(cls, inp: BoltGroupInput) -> BoltGroupResult:
        """볼트군 전단/인장/지압/마찰 종합 검토"""
        d, ab, fnt, fnv_inc, fnv_exc, fu = cls.get_bolt_props(inp.bolt_size, inp.grade)
        fnv = fnv_inc if inp.threads_included else fnv_exc
        n_bolts = inp.num_bolts
        n_sp = inp.num_shear_planes
        messages = []

        # 1. 지압접합 볼트 전단강도 (Single & Total)
        # Rn = Fnv * Ab * Ns
        rn_shear_single = fnv * ab * n_sp / 1000.0 # kN
        phi_rn_shear_single = cls.PHI_BOLT_SHEAR * rn_shear_single
        phi_rn_shear_total = phi_rn_shear_single * n_bolts

        # 2. 볼트 인장강도
        # Rn = Fnt * Ab
        rn_tension_single = fnt * ab / 1000.0 # kN
        phi_rn_tension_single = cls.PHI_BOLT_TENSION * rn_tension_single
        phi_rn_tension_total = phi_rn_tension_single * n_bolts

        # 3. 볼트 구멍 지압강도 (Bearing Strength)
        dh = BOLT_DB.get(inp.bolt_size, {}).get("dh", d + 2.0)
        # 내측 볼트와 단부 볼트의 순거리 Lc 계산
        lc_edge = max(0.1, inp.edge_distance - 0.5 * dh)
        lc_inner = max(0.1, inp.pitch - dh)

        t = inp.plate_thickness
        fu_p = inp.plate_fu

        if inp.deformation_considered:
            c1, c2 = 1.2, 2.4
        else:
            c1, c2 = 1.5, 3.0

        # 단부 볼트 및 내측 볼트 지압강도
        rn_bearing_edge = min(c1 * lc_edge * t * fu_p, c2 * d * t * fu_p) / 1000.0 # kN
        rn_bearing_inner = min(c1 * lc_inner * t * fu_p, c2 * d * t * fu_p) / 1000.0 # kN

        # 열/행 배치에 따른 가중 평균 (단부 볼트 개수 = cols, 내측 볼트 = n_bolts - cols)
        n_edge = min(inp.cols, n_bolts)
        n_inner = max(0, n_bolts - n_edge)
        rn_bearing_total = (n_edge * rn_bearing_edge) + (n_inner * rn_bearing_inner)
        phi_rn_bearing_single = cls.PHI_BEARING * min(rn_bearing_edge, rn_bearing_inner)
        phi_rn_bearing_total = cls.PHI_BEARING * rn_bearing_total

        # 4. 마찰접합 미끄럼 강도 (Slip-Critical)
        t0 = BOLT_DB.get(inp.bolt_size, {}).get(f"T0_{inp.grade.value}", 157.0)
        if inp.hole_type == HoleType.STANDARD:
            phi_slip = 1.0
            h_sc = 1.0
        elif inp.hole_type in (HoleType.OVERSIZED, HoleType.SHORT_SLOT):
            phi_slip = 0.85
            h_sc = 0.85
        else: # LONG_SLOT
            phi_slip = 0.70
            h_sc = 0.70

        # 인장력에 의한 미끄럼 저감계수
        if inp.Tu > 0 and n_bolts > 0:
            k_sc = max(0.0, 1.0 - inp.Tu / (inp.du * t0 * n_bolts))
        else:
            k_sc = 1.0

        # Rn = mu * Du * h_sc * T0 * Ns * n_bolts * k_sc
        rn_slip_total = inp.slip_coefficient * inp.du * h_sc * t0 * n_sp * n_bolts * k_sc
        phi_rn_slip_total = phi_slip * rn_slip_total

        # 5. 전단-인장 복합 작용 (Combined Shear and Tension, KDS 14 31 25 4.1.2)
        fv = (inp.Vu * 1000.0) / (n_bolts * ab) if n_bolts > 0 else 0.0 # 전단응력 MPa
        if fv > 0 and inp.Tu > 0:
            fnt_prime = 1.3 * fnt - (fnt / (cls.PHI_BOLT_SHEAR * fnv)) * fv
            fnt_prime = max(0.0, min(fnt, fnt_prime))
            phi_rn_tension_comb = cls.PHI_BOLT_TENSION * (fnt_prime * ab * n_bolts / 1000.0)
            dcr_combined = inp.Tu / max(1e-4, phi_rn_tension_comb)
        else:
            dcr_combined = max(
                inp.Vu / max(1e-4, phi_rn_shear_total),
                inp.Tu / max(1e-4, phi_rn_tension_total)
            )

        # DCR 산정
        dcr_shear = inp.Vu / max(1e-4, phi_rn_shear_total)
        dcr_tension = inp.Tu / max(1e-4, phi_rn_tension_total)
        dcr_bearing = inp.Vu / max(1e-4, phi_rn_bearing_total)
        
        if inp.joint_type == JointType.SLIP_CRITICAL:
            dcr_slip = inp.Vu / max(1e-4, phi_rn_slip_total)
            governing_dcr = max(dcr_slip, dcr_bearing, dcr_combined)
        else:
            governing_dcr = max(dcr_shear, dcr_bearing, dcr_combined)

        # 최소 연단거리 / 간격 규정 체크
        min_edge = 1.25 * d # 일반적인 최소 연단거리 가이드 (약 1.5d 권장)
        min_pitch = 2.67 * d
        if inp.edge_distance < min_edge:
            messages.append(f"연단거리 Le({inp.edge_distance:.1f}mm)가 최소기준({min_edge:.1f}mm) 미달")
        if inp.pitch < min_pitch:
            messages.append(f"볼트피치 s({inp.pitch:.1f}mm)가 최소기준({min_pitch:.1f}mm) 미달")

        return BoltGroupResult(
            phi_Rn_shear_single=round(phi_rn_shear_single, 2),
            phi_Rn_shear_total=round(phi_rn_shear_total, 2),
            phi_Rn_tension_single=round(phi_rn_tension_single, 2),
            phi_Rn_tension_total=round(phi_rn_tension_total, 2),
            phi_Rn_bearing_single=round(phi_rn_bearing_single, 2),
            phi_Rn_bearing_total=round(phi_rn_bearing_total, 2),
            phi_Rn_slip_total=round(phi_rn_slip_total, 2),
            dcr_shear=round(dcr_shear, 4),
            dcr_tension=round(dcr_tension, 4),
            dcr_bearing=round(dcr_bearing, 4),
            dcr_combined=round(dcr_combined, 4),
            governing_dcr=round(governing_dcr, 4),
            is_safe=(governing_dcr <= 1.0 and len(messages) == 0),
            messages=messages,
        )

    @classmethod
    def check_block_shear(cls, inp: BlockShearInput) -> BlockShearResult:
        """블록전단 파단강도 산정 (KDS 14 31 25 4.1.3)"""
        # Rn = 0.60 * Fu * Anv + Ubs * Fu * Ant <= 0.60 * Fy * Agv + Ubs * Fu * Ant
        term_tension = inp.Ubs * inp.Fu * inp.Ant
        rn_rupture = (0.60 * inp.Fu * inp.Anv + term_tension) / 1000.0 # kN
        rn_yield = (0.60 * inp.Fy * inp.Agv + term_tension) / 1000.0   # kN

        rn = min(rn_rupture, rn_yield)
        phi_rn = cls.PHI_BLOCK_SHEAR * rn
        dcr = inp.Pu / max(1e-4, phi_rn)

        gov_mode = "전단파단+인장파단" if rn_rupture <= rn_yield else "전단항복+인장파단"

        return BlockShearResult(
            Rn_rupture=round(rn_rupture, 2),
            Rn_yield=round(rn_yield, 2),
            phi_Rn=round(phi_rn, 2),
            dcr=round(dcr, 4),
            is_safe=(dcr <= 1.0),
            governing_mode=gov_mode
        )

    @classmethod
    def check_weld_joint(cls, inp: WeldJointInput) -> WeldJointResult:
        """용접 접합부 강도 산정 (KDS 14 31 25 4.2)"""
        # 1. 필릿용접 유효목두께 및 유효길이
        if inp.weld_type == WeldType.FILLET:
            throat = 0.707 * inp.leg_size
            eff_len = max(0.0, inp.length - 2.0 * inp.leg_size) if inp.length > 4.0 * inp.leg_size else inp.length
            # 용접부 공칭강도 Rn = 0.60 * Fexx * Aw
            aw = throat * eff_len # mm²
            rn_weld = 0.60 * inp.Fexx * aw / 1000.0 # kN
            phi_rn_weld = cls.PHI_WELD * rn_weld
            
            # 모재 전단파단강도 Rn = 0.60 * Fu * (t * Lw)
            rn_base = 0.60 * inp.base_fu * (inp.base_thickness * inp.length) / 1000.0
            phi_rn_base = cls.PHI_WELD * rn_base
        elif inp.weld_type == WeldType.CJP:
            throat = inp.base_thickness
            eff_len = inp.length
            # 완전용입은 모재와 동등
            phi_rn_weld = 0.90 * (inp.base_fu * throat * eff_len) / 1000.0
            phi_rn_base = phi_rn_weld
        else: # PJP
            throat = 0.75 * inp.leg_size
            eff_len = inp.length
            rn_weld = 0.60 * inp.Fexx * (throat * eff_len) / 1000.0
            phi_rn_weld = cls.PHI_WELD * rn_weld
            phi_rn_base = 0.75 * (0.60 * inp.base_fu * inp.base_thickness * eff_len) / 1000.0

        phi_rn = min(phi_rn_weld, phi_rn_base)
        dcr = inp.Vu / max(1e-4, phi_rn)

        return WeldJointResult(
            throat=round(throat, 2),
            effective_length=round(eff_len, 2),
            phi_Rn_weld=round(phi_rn_weld, 2),
            phi_Rn_base=round(phi_rn_base, 2),
            phi_Rn=round(phi_rn, 2),
            dcr=round(dcr, 4),
            is_safe=(dcr <= 1.0)
        )
