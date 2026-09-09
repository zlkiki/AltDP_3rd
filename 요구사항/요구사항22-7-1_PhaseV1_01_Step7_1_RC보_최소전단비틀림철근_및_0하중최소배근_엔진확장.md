# 요구사항 22-7-1: Phase V1-01 Step 7-1 RC 보 최소전단·비틀림철근 산정식 및 0하중 최소배근 엔진 확장 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 설계 엔진(`src/engine/rc/beam.py`)의 **(1) KDS 14 20 22 제4.3.3절 최소 전단철근량($A_{v,\min}$) 및 제4.3.4절 최대 배근간격($s_{\max}$) 정밀 산출**, **(2) 계수전단력 0 ($V_u \le 0$)일 때 전단강도 0플래그(`is_zero_shear`) 부여 및 최소 전단철근 검토 상시 수행**, **(3) KDS 14 20 22 제4.5.4절 최소 횡방향 폐쇄스터럽($(A_v + 2A_t)_{\min}$) 및 최소 종방향 비틀림철근량($A_{l,\min}$) 산출과 소요량 보정($A_{l,req} = \max(A_{l,\text{calc}}, A_{l,\min})$) 버그 치유**, 그리고 **(4) 계수휨모멘트 0 ($M_u \le 0$)일 때 현행 KDS 신 기준 최소 휨철근 검토($\phi M_n \ge 1.2 M_{cr}$) 및 연성 검토($\epsilon_t \ge \epsilon_{t,\min}$) 무결성 보장**을 완수하기 위한 백엔드 계산 엔진 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/engine/rc/beam.py` (KDS 계산 엔진 및 Pydantic 스키마)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트 스위트)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KDS 14 20 20 / 22 기준 공식 수치 해석, Pydantic 스키마 확장, 엄밀한 TDD (오차 $\le 0.10\%$)
* **연동 SSOT**:
  - **KDS 14 20 20 : 2022** (제4.2.2절 식 4.2-1 $\phi M_n \ge 1.2 M_{cr}$)
  - **KDS 14 20 22 : 2022** (제4.3.3절 식 4.3-1 $A_{v,\min}$, 제4.3.4절 $s_{\max}$, 제4.5.4절 식 4.5-6 $(A_v + 2A_t)_{\min}$, 식 4.5-7 $A_{l,\min}$)
  - [`docs/10`](../docs/10_agent_development_protocols.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)

---

## 2. 세부 엔지니어링 구현 사양

### 2.1. `ShearResult` Pydantic 스키마 확장 및 산출 로직 개편
* **스키마 필드 확장**:
  ```python
  class ShearResult(BaseModel):
      Vu: float
      Vc: float
      Vs: float
      Vn: float
      phi_Vn: float
      phi: float = 0.75
      s_max: float                # 규준 최대 허용 배근간격 (mm)
      Av_min: float               # 최소 전단철근량 (mm2)
      Av_prov: float              # 실제 배치된 전단철근량 (mm2)
      dcr: float                  # Vu / phi_Vn (Vu <= 0 시 0.0)
      dcr_Av_min: float = 0.0     # Av_min / Av_prov
      dcr_spacing: float = 0.0    # s / s_max
      is_min_shear_ok: bool = True# Av_prov >= Av_min 및 s <= s_max 만족 여부
      status: str                 # "OK" | "NG"
      is_zero_shear: bool = False # 계수전단력 0 이하 여부
  ```
* **수식 산정 및 판정 알고리즘 (`calculate_rc_beam_shear`)**:
  1. **최소 전단철근량 $A_{v,\min}$** (KDS 14 20 22 식 4.3-1):
     $$A_{v,\min} = \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right)$$
  2. **최대 배근간격 $s_{\max}$** (KDS 14 20 22 제4.3.4절):
     $$s_{\max} = \begin{cases} \min\left(\frac{d}{2}, \, 600.0\right) & \left(V_s \le \frac{1}{3}\sqrt{f_{ck}} b_w d\right) \\ \min\left(\frac{d}{4}, \, 300.0\right) & \left(V_s > \frac{1}{3}\sqrt{f_{ck}} b_w d\right) \end{cases}$$
     - $V_u \le 0$일 때는 $V_s = 0$이므로 $s_{\max} = \min(d/2, 600.0\text{ mm})$ 적용.
  3. **내력비 및 판정**:
     - $\text{dcr}_{Av,\min} = A_{v,\min} / A_{v,prov}$ ($A_{v,prov} > 0$ 시)
     - $\text{dcr}_{spacing} = s / s_{\max}$ ($s_{\max} > 0$ 시)
     - `is_min_shear_ok = (Av_prov >= Av_min - 1e-4) and (s <= s_max * 1.001)`
     - `is_zero_shear = (Vu <= 0.0)`
     - `status = "OK"` if `(dcr <= 1.0 and is_min_shear_ok)` else `"NG"`

---

### 2.2. `TorsionResult` Pydantic 스키마 확장 및 소요량 보정 버그 완치
* **스키마 필드 확장**:
  ```python
  class TorsionResult(BaseModel):
      Tu: float
      Tth: float
      Tcr: float
      Tn: float
      phi_Tn: float
      phi: float = 0.75
      cross_section_check: str
      Al_calc: float = 0.0        # 순수 비틀림 계산 소요 종방향 철근량 (mm2)
      Al_min: float = 0.0         # 최소 종방향 비틀림 철근량 (mm2)
      Al_req: float               # max(Al_calc, Al_min) 최종 소요량 (mm2)
      Al_prov: float              # 실제 배치된 측면 철근량 (mm2)
      Av_2At_min: float = 0.0     # 최소 횡방향 폐쇄스터럽 철근량 (mm2)
      s_max_torsion: float = 0.0  # 비틀림 스터럽 최대 간격 min(ph/8, 300) (mm)
      dcr: float
      dcr_Al: float = 0.0         # Al_req / Al_prov
      status: str
      is_zero_torsion: bool = False
  ```
* **수식 산정 및 판정 알고리즘 (`calculate_rc_beam_torsion`)**:
  1. **최소 횡방향 폐쇄스터럽** (KDS 14 20 22 식 4.5-6):
     $$(A_v + 2A_t)_{\min} = \max\left(0.0625 \sqrt{f_{ck}} \frac{b_w s}{f_{yt}}, \, 0.35 \frac{b_w s}{f_{yt}}\right)$$
  2. **최소 종방향 비틀림 철근량** (KDS 14 20 22 식 4.5-7):
     $$A_{l,\min} = \max\left(\frac{0.42 \sqrt{f_{ck}} A_{cp}}{f_y} - \left(\frac{A_t}{s}\right) p_h \frac{f_{yt}}{f_y}, \, 0.0\right)$$
     (단, 위 수식 대입 시 $\frac{A_t}{s} \ge \frac{0.175 b_w}{f_{yt}}$ 한계 적용)
  3. **최종 소요량 보정 (버그 완치)**:
     $$A_{l,req} = \max(A_{l,\text{calc}}, \, A_{l,\min})$$
  4. **비틀림 최대 간격**:
     $$s_{\max,torsion} = \min\left(\frac{p_h}{8}, \, 300.0\right)$$

---

### 2.3. 계수하중 0일 때의 최소 배근 의무화 보장 (`beam.py`)
1. **휨 ($M_u \le 0$)**:
   - `is_zero_flexure = True`
   - `phi_Mn >= phi_Mn_min` ($1.2 M_{cr}$) 검토는 $M_u \le 0$이어도 정상 수행 및 `is_min_flexure_ok` 반환.
   - `epsilon_t >= epsilon_t_min` 연성 검토 역시 $M_u \le 0$이어도 정상 수행 및 `is_ductility_ok` 반환.
2. **전단 ($V_u \le 0$)**:
   - `is_zero_shear = True`, `dcr = 0.0`
   - $A_{v,\min}$ 및 $s_{\max}$ 검토는 정상 수행하며, `is_min_shear_ok`가 False이면 `status = "NG"` 판정.
3. **비틀림 ($T_u \le \phi T_{th}$)**:
   - `is_zero_torsion = True`
   - 비틀림 전용 추가 배근은 0으로 처리되나, 부재 최소 전단철근 배근으로 갈음.

---

## 3. 단위 테스트 검증 계획 (`tests/engine/test_rc_beam.py`)

1. **`test_rc_beam_shear_min_rebar`**:
   - 일반 직사각형 보 ($400 \times 600$, D10@150 2-legs)에 대해 $A_{v,\min}$ 및 $s_{\max}$ 수식 수치 정밀 대조 ($\le 0.10\%$ 오차).
   - 스터럽 간격 $s > s_{\max}$ 또는 $A_{v,prov} < A_{v,\min}$ 시 `is_min_shear_ok == False` 및 `status == "NG"` 검증.
2. **`test_rc_beam_shear_zero_load_mandatory_min`**:
   - $V_u = 0.0\text{ kN}$ 입력 시 `is_zero_shear == True`, `dcr == 0.0` 검증.
   - $V_u = 0$이어도 $A_{v,\min} > 0$ 및 $s_{\max} > 0$이 정상 계산되고 최소배근 검토가 수행됨을 검증.
3. **`test_rc_beam_torsion_Al_min_governing`**:
   - $T_u > \phi T_{th}$이나 계산된 $A_{l,\text{calc}}$가 매우 작은 경우, $A_{l,\min}$이 지배하여 $A_{l,req} == A_{l,\min}$으로 보정됨을 검증.
4. **기존 391개 회귀 테스트 100% PASS 확인**.

---

## 4. 완료 검증 기준 (Definition of Done)

- [x] `ShearResult`에 `dcr_Av_min`, `dcr_spacing`, `is_min_shear_ok` 필드가 정상 추가될 것.
- [x] $V_u \le 0$일 때 `is_zero_shear = True`가 설정되고, $A_{v,\min}$과 $s_{\max}$가 정상 산출될 것.
- [x] `TorsionResult`에 $A_{l,req} = \max(A_{l,\text{calc}}, A_{l,\min})$ 보정이 적용되어 과소평가 버그가 완치될 것.
- [x] $M_u \le 0$이어도 신 기준 휨 최소철근량($\phi M_n \ge 1.2 M_{cr}$) 및 연성 한계($\epsilon_t \ge \epsilon_{t,\min}$)가 정상 평가될 것.
- [x] `pytest tests/engine/test_rc_beam.py` 100% 통과 및 오차 $\le 0.10\%$ 입증.
