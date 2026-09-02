"""강구조 주각부 베이스플레이트 및 앵커볼트 설계 엔진 (KDS 14 31 25 4.5 / KDS 14 20 54)

Ground Truth:
  - decompiled_src/core_routines/steel/steel__CHK_USBP_*.c (CSTLCodeCheck::CHK_USBP)
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple


class AnchorType(str, Enum):
    """앵커볼트 시공 형식"""
    CAST_IN_HEADED = "CAST_IN_HEADED"  # 선설치 헤드볼트 (kc = 12.5)
    POST_INSTALLED = "POST_INSTALLED"  # 후설치 앵커 (kc = 10.0)


@dataclass
class AnchorBoltInput:
    """앵커볼트 설계 입력"""
    anchor_type: AnchorType = AnchorType.CAST_IN_HEADED
    diameter: float = 24.0             # 앵커 공칭 직경 da (mm)
    num_anchors: int = 4               # 총 앵커 개수
    num_tension_anchors: int = 2       # 인장 측 앵커 개수
    hef: float = 250.0                 # 유효 매입 깊이 (mm)
    edge_distance: float = 150.0       # 콘크리트 연단거리 c_a1 (mm)
    spacing: float = 150.0             # 앵커 간격 s_a (mm)
    futa: float = 400.0                # 앵커볼트 인장강도 (MPa, SS400=400, SM355=490 등)


@dataclass
class BasePlateInput:
    """주각부 베이스플레이트 입력 데이터"""
    # 기둥 단면 (mm) & 재료 (MPa)
    col_d: float = 400.0               # 기둥 춤 dc (mm)
    col_bf: float = 400.0              # 기둥 플랜지 폭 bfc (mm)
    col_tf: float = 20.0               # 기둥 플랜지 두께 tfc (mm)
    col_tw: float = 13.0               # 기둥 웨브 두께 twc (mm)
    col_fy: float = 275.0              # 기둥 강재 항복강도 (MPa)
    
    # 베이스플레이트 치수 (mm) & 재료 (MPa)
    B: float = 600.0                   # 베이스플레이트 폭 (mm, 플랜지 직각)
    N: float = 600.0                   # 베이스플레이트 길이 (mm, 플랜지 평행)
    tp: float = 35.0                   # 베이스플레이트 두께 (mm)
    plate_fy: float = 275.0            # 플레이트 강재 항복강도 (MPa)
    
    # 콘크리트 기초 (mm, MPa)
    fck: float = 27.0                  # 콘크리트 설계기준압축강도 (MPa)
    pedestal_B: float = 800.0          # 기초/패디스탈 폭 B2 (mm)
    pedestal_N: float = 800.0          # 기초/패디스탈 길이 N2 (mm)
    
    # 앵커볼트
    anchor: AnchorBoltInput = field(default_factory=AnchorBoltInput)
    anchor_edge_dist_plate: float = 60.0 # 베이스플레이트 연단에서 앵커 중심까지 거리 (mm)
    
    # 계수 하중
    Pu: float = 600.0                  # 계수 축압축력 (kN, 압축 +)
    Mu: float = 150.0                  # 계수 휨모멘트 (kN·m)
    Vu: float = 80.0                   # 계수 전단력 (kN)


@dataclass
class BasePlateResult:
    """주각부 베이스플레이트 및 앵커 설계 결과"""
    # 콘크리트 지압
    phi_Pp: float                      # 콘크리트 설계지압강도 (kN)
    fp_max_allow: float                # 최대 허용 지압응력 (MPa)
    fp_actual: float                   # 실제 최대 지압응력 (MPa)
    dcr_bearing: float                 # 콘크리트 지압 DCR
    eccentricity_case: str             # 편심 상태 ("소편심(전단면압축)", "중편심(부분압축)", "대편심(앵커인장)")
    
    # 플레이트 두께 및 캔틸레버 모멘트
    cantilever_l: float                # 캔틸레버 유효 굽힘암 l (mm)
    req_plate_tp: float                # 소요 베이스플레이트 두께 tp,req (mm)
    dcr_plate: float                   # 플레이트 휨 DCR
    
    # 앵커볼트 한계상태
    Tu_anchor_total: float             # 총 소요 앵커 인장력 (kN)
    phi_Nsa: float                     # 앵커 강재 설계인장강도 (kN)
    phi_Ncb: float                     # 콘크리트 콘파칭 설계강도 (kN)
    phi_Vsa: float                     # 앵커 강재 설계전단강도 (kN)
    phi_Vcp: float                     # 콘크리트 프라이아웃 설계전단강도 (kN)
    dcr_anchor_tension: float          # 앵커 인장 DCR
    dcr_anchor_shear: float            # 앵커 전단 DCR
    dcr_anchor_combined: float         # 앵커 인장-전단 상호작용 DCR
    
    # 종합
    governing_dcr: float
    is_safe: bool
    messages: List[str] = field(default_factory=list)


class SteelBasePlateEngine:
    """KDS 14 31 25 4.5 / KDS 14 20 54 주각부 및 앵커 해석 솔버"""

    PHI_CONCRETE_BEARING = 0.65
    PHI_PLATE_FLEXURE = 0.90
    PHI_ANCHOR_STEEL_TENSION = 0.75
    PHI_ANCHOR_STEEL_SHEAR = 0.65
    PHI_ANCHOR_CONCRETE = 0.70

    @classmethod
    def check_base_plate(cls, inp: BasePlateInput) -> BasePlateResult:
        """베이스플레이트 지압응력, 두께 산정, 앵커볼트 종합 검토"""
        messages = []
        
        # 1. 콘크리트 기초 지압강도 Pp 및 fp_max
        A1 = inp.B * inp.N # mm²
        A2 = inp.pedestal_B * inp.pedestal_N # mm²
        geo_factor = math.sqrt(max(1.0, A2 / max(1.0, A1)))
        geo_factor = min(2.0, geo_factor) # 최대 2.0 배 제한

        fp_max_allow = cls.PHI_CONCRETE_BEARING * (0.85 * inp.fck) * geo_factor # MPa
        phi_Pp = fp_max_allow * A1 / 1000.0 # kN

        # 2. 편심 e 및 지압응력 분포 판정
        Pu_n = max(1.0, inp.Pu * 1000.0) # N
        Mu_nmm = abs(inp.Mu) * 1e6        # N*mm
        e = Mu_nmm / Pu_n                 # mm

        # 앵커 중심 위치 d_prime (압축 연단에서 인장측 앵커까지 거리)
        d_prime = inp.N - inp.anchor_edge_dist_plate

        # 지압응력 및 앵커 인장력 산정
        if e <= inp.N / 6.0:
            ecc_case = "소편심(전단면압축)"
            fp_actual = (Pu_n / A1) * (1.0 + 6.0 * e / inp.N)
            Tu_anchor = 0.0
        elif e <= (inp.N / 2.0 - Pu_n / (2.0 * fp_max_allow * inp.B)):
            ecc_case = "중편심(부분압축)"
            Yc = 3.0 * (inp.N / 2.0 - e)
            fp_actual = (2.0 * Pu_n) / (3.0 * inp.B * max(1.0, (inp.N / 2.0 - e)))
            Tu_anchor = 0.0
        else:
            ecc_case = "대편심(앵커인장)"
            # 대편심 시 2차 방정식 풀이: f = fp_max_allow 가정 하 압축대 길이 Yc 및 Tu 산출
            # q_max = fp_max_allow * B (N/mm)
            # Yc^2 - 2*d_prime*Yc + 2*(Pu*(d_prime - N/2) + Mu)/(fp_max*B) = 0
            q_max = fp_max_allow * inp.B
            term_c = (2.0 * (Pu_n * (d_prime - inp.N / 2.0) + Mu_nmm)) / max(1.0, q_max)
            discriminant = max(0.0, (2.0 * d_prime)**2 - 4.0 * term_c)
            Yc = (2.0 * d_prime - math.sqrt(discriminant)) / 2.0
            Yc = max(10.0, min(inp.N, Yc))
            
            # C = 0.5 * fp_max_allow * B * Yc
            # Tu = C - Pu
            C_force = 0.5 * fp_max_allow * inp.B * Yc # N
            Tu_anchor = max(0.0, (C_force - Pu_n) / 1000.0) # kN
            fp_actual = fp_max_allow

        dcr_bearing = fp_actual / max(1e-4, fp_max_allow)

        # 3. 캔틸레버 모멘트 암 l 및 소요 베이스플레이트 두께 tp,req
        m = (inp.N - 0.95 * inp.col_d) / 2.0
        n = (inp.B - 0.80 * inp.col_bf) / 2.0
        n_prime = math.sqrt(inp.col_d * inp.col_bf) / 4.0

        ratio_geom = (4.0 * inp.col_d * inp.col_bf) / ((inp.col_d + inp.col_bf)**2)
        X_term = ratio_geom * (inp.Pu / max(1e-4, phi_Pp))
        X_term = min(1.0, max(0.0, X_term))
        lambda_val = (2.0 * math.sqrt(X_term)) / (1.0 + math.sqrt(max(0.0, 1.0 - X_term)))
        lambda_val = min(1.0, max(0.0, lambda_val))

        cantilever_l = max(m, n, lambda_val * n_prime)
        cantilever_l = max(10.0, cantilever_l)

        # tp,req = l * sqrt( 2 * fp_actual / (0.90 * plate_fy) )
        tp_req = cantilever_l * math.sqrt((2.0 * fp_actual) / (cls.PHI_PLATE_FLEXURE * inp.plate_fy))
        dcr_plate = (tp_req / max(1.0, inp.tp)) ** 2

        # 4. 앵커볼트 강도 검토 (KDS 14 20 54)
        anc = inp.anchor
        da = anc.diameter
        area_bolt = (math.pi * da**2) / 4.0
        n_ta = max(1, anc.num_tension_anchors)
        n_total = max(1, anc.num_anchors)

        # 4.1 앵커 강재 인장강도 phi_Nsa
        phi_Nsa = cls.PHI_ANCHOR_STEEL_TENSION * (n_ta * area_bolt * anc.futa) / 1000.0 # kN
        
        # 4.2 콘크리트 콘파칭강도 phi_Ncb
        kc = 12.5 if anc.anchor_type == AnchorType.CAST_IN_HEADED else 10.0
        Nb = kc * 1.0 * math.sqrt(inp.fck) * (anc.hef ** 1.5) # N
        Anc0 = 9.0 * (anc.hef ** 2)
        # 단일/그룹 앵커 유효면적 Anc 추정
        Anc = min(Anc0 * n_ta, (anc.spacing + 3.0 * anc.hef) * (3.0 * anc.hef))
        psi_ed_N = min(1.0, max(0.7, anc.edge_distance / (1.5 * anc.hef)))
        phi_Ncb = cls.PHI_ANCHOR_CONCRETE * (Anc / max(1.0, Anc0)) * psi_ed_N * Nb / 1000.0 # kN

        phi_Nn = min(phi_Nsa, phi_Ncb)
        dcr_anchor_tension = Tu_anchor / max(1e-4, phi_Nn)

        # 4.3 앵커 강재 전단강도 phi_Vsa
        phi_Vsa = cls.PHI_ANCHOR_STEEL_SHEAR * (0.60 * n_total * area_bolt * anc.futa) / 1000.0 # kN

        # 4.4 콘크리트 프라이아웃강도 phi_Vcp
        kcp = 2.0 if anc.hef >= 65.0 else 1.0
        phi_Vcp = cls.PHI_ANCHOR_CONCRETE * (kcp * (phi_Ncb / cls.PHI_ANCHOR_CONCRETE)) # kN

        phi_Vn = min(phi_Vsa, phi_Vcp)
        dcr_anchor_shear = abs(inp.Vu) / max(1e-4, phi_Vn)

        # 4.5 인장-전단 상호작용
        dcr_anchor_combined = (dcr_anchor_tension ** 1.67) + (dcr_anchor_shear ** 1.67)

        # 종합 판정
        all_dcrs = [dcr_bearing, dcr_plate, dcr_anchor_tension, dcr_anchor_shear, dcr_anchor_combined]
        governing_dcr = max(all_dcrs)

        if inp.tp < tp_req:
            messages.append(f"베이스플레이트 두께 tp({inp.tp}mm)가 소요두께({tp_req:.1f}mm) 미달")
        if dcr_bearing > 1.0:
            messages.append("콘크리트 기초 지압강도 초과 (플레이트 면적 또는 콘크리트 강도 증대 필요)")
        if dcr_anchor_combined > 1.0:
            messages.append("앵커볼트 복합응력 초과 (앵커 직경/매입깊이/수량 증대 필요)")

        return BasePlateResult(
            phi_Pp=round(phi_Pp, 2),
            fp_max_allow=round(fp_max_allow, 2),
            fp_actual=round(fp_actual, 2),
            dcr_bearing=round(dcr_bearing, 4),
            eccentricity_case=ecc_case,
            cantilever_l=round(cantilever_l, 2),
            req_plate_tp=round(tp_req, 2),
            dcr_plate=round(dcr_plate, 4),
            Tu_anchor_total=round(Tu_anchor, 2),
            phi_Nsa=round(phi_Nsa, 2),
            phi_Ncb=round(phi_Ncb, 2),
            phi_Vsa=round(phi_Vsa, 2),
            phi_Vcp=round(phi_Vcp, 2),
            dcr_anchor_tension=round(dcr_anchor_tension, 4),
            dcr_anchor_shear=round(dcr_anchor_shear, 4),
            dcr_anchor_combined=round(dcr_anchor_combined, 4),
            governing_dcr=round(governing_dcr, 4),
            is_safe=(governing_dcr <= 1.0),
            messages=messages
        )
