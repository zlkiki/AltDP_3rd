# 요구사항 10-3: CFRP 및 강판 보수보강 설계 엔진

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* 노후화된 콘크리트 구조물의 내하력 증진과 사용성 개선을 위해 탄소섬유판/시트(CFRP Plate/Sheet) 및 강판(Steel Plate)을 부착하는 보수·보강(Retrofit) 공법이 널리 적용됩니다.
* KDS 14 20 90(기존 콘크리트구조물의 보수·보강 설계기준) 및 ACI 440.2R에 따라 **RC 보/기둥의 CFRP 및 강판 부착에 따른 휨·전단 내력 증진도 산정 및 계면 부착파괴(Debonding) 방지 검토** 엔진(`src/engine/rfm/retrofit_design.py`)을 구축합니다.
* 보강 전 기존 부재의 하중 이력에 따른 초기 변형률($\epsilon_{bi}$)을 반영합니다.
* CFRP의 조기 탈락(Debonding) 방지를 위한 유효 인장변형률($\epsilon_{fe}$) 한계치 및 보강재 환경감소계수($C_E$), 보강재 강도저감계수($\psi_f$)를 정확히 산출합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스 및 심볼**:
  - `decompiled_src/DPLUS_RFM.dll_symbols.txt` (`CRFMCodeCheck`, `CCFRPDesign`, `CSteelPlateDesign`, `CRFMSection`)
* **KDS 기준서**:
  - KDS 14 20 90 기존 콘크리트구조물의 보수·보강 설계기준
* **대상 소스**:
  - [`src/engine/rfm/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rfm/__init__.py)
  - [`src/engine/rfm/retrofit_design.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rfm/retrofit_design.py)
  - [`tests/engine/test_rfm.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_rfm.py)

---

## 2. 상세 공학 공식 및 설계 규정 (KDS 14 20 90)

### 2.1. 보강 재료 물성 및 환경감소계수 ($C_E$)
* **CFRP 설계인장강도 및 파단변형률**:
  $$f_{fu}^* = C_E f_{fu}, \quad \epsilon_{fu}^* = C_E \epsilon_{fu}$$
  - $C_E$: 환경노출계수 (실내 0.95, 옥외 0.85, 부식환경 0.75)
* **강판 보강재 물성**:
  - 항복강도 $f_{ys}$, 탄성계수 $E_s = 200,000\text{MPa}$, 두께 $t_s$

### 2.2. CFRP 휨 보강 설계 및 계면 탈락 검토
* **초기 인장측 변형률 ($\epsilon_{bi}$)**:
  $$\epsilon_{bi} = \frac{M_{DL} (h - k d)}{I_{cr} E_c}$$
* **계면 부착파괴(Debonding) 방지 CFRP 유효변형률 ($\epsilon_{fe}$)**:
  $$\epsilon_{fe} = \min\left(0.004, \; \kappa_m \epsilon_{fu}^*\right)$$
  - CFRP 판 부착 시: $\kappa_m = \frac{1}{60 \epsilon_{fu}^*} \left(1 - \frac{n E_f t_f}{360,000}\right) \le 0.90$
* **보강 후 설계 휨모멘트강도 ($\phi M_n$)**:
  $$\phi M_n = \phi \left[ M_{n,RC} + \psi_f A_f f_{fe} \left(d_f - \frac{\beta_1 c}{2}\right) \right]$$
  - $\psi_f = 0.85$ (CFRP 휨보강 강도감소계수)
  - $f_{fe} = E_f \epsilon_{fe}$

### 2.3. CFRP 및 강판 전단 보강 설계
* **CFRP U형/완전감싸기(Full Wrapping) 전단기여분 ($V_f$)**:
  $$V_f = \frac{A_{fv} f_{fe} (\sin\alpha + \cos\alpha) d_{fv}}{s_f}$$
  - 유효변형률: 완전감싸기 시 $\epsilon_{fe} = 0.004 \le 0.75 \epsilon_{fu}^*$, U형 감싸기 시 $\epsilon_{fe} = \kappa_v \epsilon_{fu}^* \le 0.004$
  - 부착감소계수: $\kappa_v = \frac{k_1 k_2 L_e}{11,900 \epsilon_{fu}^*} \le 0.75$
* **강판 전단 보강 기여분 ($V_{sp}$)**:
  $$V_{sp} = 2 \cdot t_{sp} \cdot d_{sp} \cdot (0.6 f_{ys})$$
* **총 설계 전단강도 ($\phi V_n$)**:
  $$\phi V_n = \phi (V_c + V_s + \psi_f V_f) \quad (\psi_f = 0.85 \text{ U-wrap}, \; 0.95 \text{ Full wrap})$$

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/rfm/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rfm/__init__.py) | [NEW] | 보수보강 모듈 패키지 진입점 |
| [`src/engine/rfm/retrofit_design.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rfm/retrofit_design.py) | [NEW] | CFRP/강판 휨보강(Debonding 검토), 전단보강, 내력 증진비 산정 엔진 |
| [`tests/engine/test_rfm.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_rfm.py) | [NEW] | CFRP/강판 보강 KDS 14 20 90 공학 단위 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] `RetrofitType`, `CFRPProp`, `SteelPlateProp`, `RetrofitBeamInput`, `RetrofitResult` 데이터 구조 정의
- [x] 환경감소계수($C_E$) 및 기존 하중에 의한 초기변형률($\epsilon_{bi}$) 산출 로직 구현
- [x] 계면 부착파괴(Debonding) 방지를 위한 CFRP 유효인장변형률($\epsilon_{fe} \le 0.004$) 산출
- [x] CFRP 및 강판 휨보강 강도($\phi M_n$) 및 기존 대비 내력 증진비($\ge 1.0$) 산출
- [x] CFRP U형/완전감싸기 및 강판 부착 전단보강강도($\phi V_n$) 산정 엔진 구현
- [x] 보강 한계상태(비보강 상태에서 사용하중 지지 여부 등) 안전성 판정
- [x] `pytest tests/engine/test_rfm.py` 100% 통과 (오차 0.1% 미만)
