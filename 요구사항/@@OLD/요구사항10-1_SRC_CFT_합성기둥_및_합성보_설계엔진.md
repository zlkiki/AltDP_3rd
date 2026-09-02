# 요구사항 10-1: SRC/CFT 합성기둥 및 합성보 설계 엔진

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* 철골-콘크리트 합성구조(Composite Structures)는 초고층 및 대형 구조물의 하중 지지 성능과 연성을 극대화하기 위해 널리 사용됩니다.
* KDS 14 31 30(강-콘크리트 합성구조 설계기준)에 기반하여 **매입형(Encased SRC) 및 충전형(Filled CFT 원형/각형) 합성기둥**과 **합성보(Composite Beam)** 설계 엔진(`src/engine/src_composite/`)을 구축합니다.
* 합성기둥의 소성단면 압축강도($P_{no}$) 및 유효휨강성($EI_{eff}$)을 기반으로 탄성/비탄성 좌굴하중과 설계 압축강도($\phi_c P_n$)를 산출합니다.
* 합성보의 유효 플랜지 폭($b_{eff}$), 헤디드 스터드(Headed Stud) 전단연결재 공칭강도($Q_n$) 및 수량, 소성중립축(PNA) 위치에 따른 정모멘트 설계휨강도($\phi_b M_n$)를 산정합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스 및 심볼**:
  - `decompiled_src/DPLUS_SRC.dll_symbols.txt` (`CSRCCodeCheck`, `CSRCSectProp`, `CSRCColumn`, `CSRCBeam`)
* **KDS 기준서**:
  - KDS 14 31 30 강-콘크리트 합성구조 설계기준 (4.1 합성기둥, 4.2 합성보)
* **대상 소스**:
  - [`src/engine/src_composite/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/__init__.py)
  - [`src/engine/src_composite/composite_column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/composite_column.py)
  - [`src/engine/src_composite/composite_beam.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/composite_beam.py)
  - [`tests/engine/test_composite.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_composite.py)

---

## 2. 상세 공학 공식 및 설계 규정 (KDS 14 31 30)

### 2.1. 합성기둥 단면 제한조건 및 소성 압축강도 ($P_{no}$)
* **단면 제한사항**:
  - 강재 단면적 비율: $A_s / A_g \ge 1.0\%$
  - CFT 각형강관 폭두께비: $b/t \le 2.26 \sqrt{E/F_y}$ (조밀), $b/t \le 3.00 \sqrt{E/F_y}$ (비조밀)
  - CFT 원형강관 외경두께비: $D/t \le 0.15 E/F_y$
  - SRC 매입형: 주철근비 $A_{sr}/A_g \ge 0.4\%$, 콘크리트 피복두께 $\ge 40\text{mm}$, 띠철근 간격 $\le \min(16 d_b, 48 d_t, 0.5 b)$
* **소성단면 압축강도 ($P_{no}$)**:
  - **매입형 (Encased SRC)**:
    $$P_{no} = F_y A_s + F_{ysr} A_{sr} + 0.85 f_{ck} A_c$$
  - **충전형 각형 (Rectangular CFT)**:
    $$P_{no} = F_y A_s + F_{ysr} A_{sr} + 0.85 f_{ck} A_c$$
  - **충전형 원형 (Circular CFT)** (구속효과 반영):
    $$P_{no} = F_y A_s + F_{ysr} A_{sr} + 0.95 f_{ck} A_c$$

### 2.2. 유효 휨강성 ($EI_{eff}$) 및 설계 압축좌굴강도 ($\phi_c P_n$)
* **유효 휨강성 ($EI_{eff}$)**:
  $$EI_{eff} = E_s I_s + E_s I_{sr} + C_1 E_c I_c$$
  $$C_1 = 0.1 + 2\left(\frac{A_s}{A_s + A_c}\right) \le 0.3$$
* **탄성 오일러 좌굴하중 ($P_e$)**:
  $$P_e = \frac{\pi^2 EI_{eff}}{(KL)^2}$$
* **임계 압축강도 ($P_n$) 및 설계강도 ($\phi_c P_n, \; \phi_c = 0.75$)**:
  $$\frac{P_{no}}{P_e} \le 2.25 \implies P_n = P_{no} \left[ 0.658^{P_{no} / P_e} \right]$$
  $$\frac{P_{no}}{P_e} > 2.25 \implies P_n = 0.877 P_e$$
  $$\phi_c P_n = 0.75 P_n$$

### 2.3. 합성보 및 스터드 전단연결재 설계 (KDS 14 31 30 4.2)
* **슬래브 유효폭 ($b_{eff}$)**:
  $$b_{eff} = \min\left(\frac{L}{4}, \; s_{beam}, \; b_w + 16 h_f\right)$$
* **헤디드 스터드 1본당 공칭 전단강도 ($Q_n$)**:
  $$Q_n = 0.5 A_{sa} \sqrt{f_{ck} E_c} \le R_g R_p A_{sa} F_u$$
  - $A_{sa} = \frac{\pi d_{stud}^2}{4}$
  - $R_g$: 데크플레이트 리브 방향 계수 (1.0 평판슬래브, 0.85/0.7 리브 수직배치)
  - $R_p$: 스터드 위치 계수 (0.75/0.6)
* **소성 휨강도 ($M_n$)**:
  - 압축측 콘크리트 슬래브 압축력 $C_c = 0.85 f_{ck} b_{eff} a$
  - 강재 인장력 $T_s = A_s F_y$
  - 전단연결재 총전단력 $V' = \sum Q_n$ (완전합성: $V' \ge \min(C_c, T_s)$)
  - 소성중립축(PNA) 판정 후 모멘트 팔길이 기반 $\phi_b M_n = 0.90 M_n$ 산출.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/src_composite/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/__init__.py) | [NEW] | SRC 합성 모듈 패키지 진입점 |
| [`src/engine/src_composite/composite_column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/composite_column.py) | [NEW] | CFT(원형/각형), SRC 매입형 소성강도($P_{no}$), $EI_{eff}$, 좌굴강도, 축하중 DCR 산정 |
| [`src/engine/src_composite/composite_beam.py`](file:///f:/PyProject/AltDP_3rd/src/engine/src_composite/composite_beam.py) | [NEW] | 합성보 유효폭, 스터드볼트 전단강도($Q_n$), 소성중립축 휨강도($M_n$) 산정 |
| [`tests/engine/test_composite.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_composite.py) | [NEW] | CFT/SRC 기둥 및 합성보 KDS 14 31 30 공학 단위 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] `SRCSectionType`, `CFTColumnInput`, `SRCColumnInput`, `CompositeBeamInput` Pydantic/Dataclass 스키마 구축
- [x] CFT 각형 및 원형 기둥의 폭두께비/경두께비 조밀성 및 단면 제한치 판정 로직 구현
- [x] 매입형(SRC) 및 충전형(CFT) 소성단면 압축강도($P_{no}$) 산정식 정확도 구현 (구속효과 0.95/0.85)
- [x] 유효 휨강성($EI_{eff}$) 계수 $C_1 = 0.1 + 2(A_s/(A_s+A_c)) \le 0.3$ 및 탄성/비탄성 좌굴강도($\phi_c P_n$) 구현
- [x] 합성보 슬래브 유효폭($b_{eff}$) 및 데크플레이트 계수($R_g, R_p$) 반영 헤디드 스터드 전단강도($Q_n$) 구현
- [x] 합성보 완전합성 및 부분합성 소성중립축(PNA) 기반 설계휨강도($\phi_b M_n$) 구현
- [x] `pytest tests/engine/test_composite.py` 100% 통과 (오차 0.1% 미만)
