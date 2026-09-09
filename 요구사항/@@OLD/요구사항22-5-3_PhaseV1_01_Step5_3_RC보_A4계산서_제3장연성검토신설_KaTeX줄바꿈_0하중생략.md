# 요구사항 22-5-3: Phase V1-01 Step 5-3 RC 보 A4 계산서 제 3장 연성검토 신설, KaTeX 줄바꿈, DCR 전수화 및 0하중 동적 생략 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 순백색 A4 구조계산서의 **(1) 최소철근량 및 순인장변형률 제한 표기 위치를 제 2장(하중조합) 뒤로 이동하여 [제 3장. 단면 연성 및 최소철근량 검토] 독립 챕터 신설 및 7대 장구분 확립**, **(2) 배근 유형(1/2/3)에 따른 단부(상부인장) 및 중앙부(하부인장) 3-Station 개별 KaTeX 수식 전개**, **(3) KaTeX `aligned` 줄바꿈 적용으로 A4 우측 여백 오버플로우 0건 방지**, **(4) 부가설명 한글 태그 삭제 및 `  →  O.K` 엔지니어링 판정 간결화**, **(5) 계산서 전 항목 DCR 전수 표기**, **(6) 0하중($T_u=0, M_u=0$ 등) 입력 시 불필요한 상세 검토 동적 생략 및 1줄 요약**, 그리고 **(7) KDS 14 20 30 제4.2.3절 균열방지 철근간격 제한($s \le s_{\max}$) 및 Branson $I_e$ 가중평균 수식 블록 신설**을 완수하기 위한 계산서 렌더러 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/rc_beam_report.js` (RC보 전용 A4 계산서 생성기)
  - `src/web/static/js/core/report_common_renderer.js` (계산서 공통 렌더링 유틸리티)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - KaTeX 8단계 수식 유도, `aligned` 환경 포맷팅, 인쇄 A4 레이아웃 무결성
* **연동 SSOT**: [`docs/14`](../docs/14_structural_calculation_report_specification.md), [`docs/07 PART 4`](../docs/07_web_application_ui_ux_specification.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)

---

## 2. 세부 개편 사양 명세

### 2.1. 계산서 7대 장구분 체계 확립 및 제 3장 연성검토 신설
전체 A4 구조계산서 구성을 아래와 같이 표준화하여 역학적 흐름을 완성합니다:

```
제 1장. 설계 기본 정보 및 단면 제원 (단면 치수, 재료 강도, 2D 횡단면 배근 상세도)
제 2장. 설계 부재력 및 하중조합 (지배 하중조합 및 3-Station 설계 부재력 총괄표)
제 3장. 단면 연성 및 최소철근량 검토 (KDS 14 20 20: 2022 3단계 수식 전개) [★신설]
제 4장. 휨모멘트 강도 검토 (3-Station 정/부모멘트 설계휨강도 phi_Mn 검토)
제 5장. 전단 및 비틀림 강도 검토 (3-Station 전단 강도 및 비틀림 검토)
제 6장. 사용성 한계상태 검토 (처짐 가중평균 및 균열방지 철근간격 s_max 검토)
제 7장. 종합 안전성 판정 (전체 항목 DCR 및 최종 O.K / N.G 판정표)
```

---

### 2.2. 배근 유형별 3-Station 역학 분리 개별 KaTeX 수식 전개
* **`ONE_SECTION` (전단면 동일)**:
  - 중앙부 단면 1개에 대해 최소철근량($\phi M_n \ge 1.2 M_{cr}$) 및 순인장변형률($\epsilon_t \ge \epsilon_{t,\min}$) 전개.
* **`SYMMETRIC_ENDS` (양단부 대칭 및 중앙부)**:
  - **단부 (End-I/J)**: 부모멘트 작용, 상부 인장철근($A_{s,\text{top}}$), 유효깊이 $d_{\text{top}}$ 기준 개별 수식 전개.
  - **중앙부 (Center-M)**: 정모멘트 작용, 하부 인장철근($A_{s,\text{bot}}$), 유효깊이 $d_{\text{bot}}$ 기준 개별 수식 전개.
* **`THREE_STATIONS` (각단부와 중앙부)**:
  - **단부-I**, **중앙부-M**, **단부-J** 3개 위치 각각의 실제 인장철근량과 유효깊이를 적용하여 3개 섹션 전수 개별 수식 전개.

---

### 2.3. KaTeX `aligned` 환경 적용으로 오버플로우 0건 방지
기호식, 수치대입, 판정이 한 줄로 길게 이어져 A4 용지(약 680px)를 벗어나는 문제를 해결하기 위해 등호(`=`) 기준으로 줄바꿈:

```latex
\begin{aligned}
\epsilon_t &= \epsilon_{cu} \left(\frac{d_t - c}{c}\right) \\
&= 0.0033 \times \left(\frac{540.0 - 112.5}{112.5}\right) = \mathbf{0.0125} \ge \epsilon_{t,\min} (0.0040) \quad \rightarrow \quad \text{O.K}
\end{aligned}
```

```latex
\begin{aligned}
\phi M_n &= 0.85 \times \left[A_s f_y \left(d - \frac{a}{2}\right)\right] \\
&= 0.85 \times \left[1532.4 \times 400 \times \left(540.0 - \frac{72.1}{2}\right)\right] \times 10^{-6} \\
&= \mathbf{262.5}\text{ kN}\cdot\text{m} \ge 1.2 M_{cr} (118.8\text{ kN}\cdot\text{m}) \quad \rightarrow \quad \text{O.K}
\end{aligned}
```

---

### 2.4. 부가설명 텍스트 태그 정리 및 판정 표기 간결화
* `[최소철근량만족O.K]`, `[연성파괴유도O.K]`, `[단면파괴방지O.K]` 등 불필요한 한글 브래킷 문구를 전면 제거.
* 우측 끝에 엔지니어링 표준 판정 형식(`  →  O.K` 또는 `  →  N.G`)과 DCR 수치로 깔끔하게 정리.

---

### 2.5. 계산서 전 항목 DCR(Demand Capacity Ratio) 전수 표기
계산서 내 모든 검토 항목에 DCR을 100% 명시:
1. 최소철근량 검토: $\text{DCR} = \frac{1.2 M_{cr}}{\phi M_n}$
2. 순인장변형률 검토: $\text{DCR} = \frac{\epsilon_{t,\min}}{\epsilon_t}$
3. 휨모멘트 검토: $\text{DCR} = \frac{M_u}{\phi M_n}$ (3-Station 각각)
4. 전단 강도 검토: $\text{DCR} = \frac{V_u}{\phi V_n}$ (3-Station 각각)
5. 비틀림 강도 검토: $\text{DCR} = \frac{T_u}{\phi T_n}$ 및 전단-비틀림 결합응력비
6. 처짐 검토: $\text{DCR} = \frac{\Delta_{total}}{\Delta_{allow}}$
7. 균열방지 철근 배근 간격: $\text{DCR} = \frac{s}{s_{\max}}$
8. 직접 균열폭: $\text{DCR} = \frac{w}{w_{lim}}$

---

### 2.6. 검토하중 0($T_u=0, M_u=0$) 동적 생략 및 1줄 요약
* **비틀림 모멘트 $T_u \le 0.0$ kN·m (또는 $T_u \le \phi T_{th}$)**:
  - 비틀림 4.3절의 장황한 KaTeX 수식 블록(임계비틀림, 결합응력, 종방향 철근)을 전면 생략.
  - *"설계 비틀림 모멘트 없음 ($T_u = 0.0\text{ kN}\cdot\text{m}$) - 비틀림 설계 생략"* 1줄 안내 박스로 간결히 표출.
* **휨모멘트 $M_u \le 0.0$ kN·m**:
  - 해당 위치의 휨모멘트 상세 전개식을 생략하고, *"작용 모멘트 없음 ($M_u = 0.0\text{ kN}\cdot\text{m}$) - 강도 검토 생략"* 표출.

---

### 2.7. 사용성 제 6장 수식 보강 (Branson $I_e$ 가중평균 & 3-Station 균열 $s_{\max}$)
* **Branson $I_e$ 가중평균**:
  - 단순보/양단연속/1단연속/캔틸레버 지점조건 공식 및 대입 결과 KaTeX 출력.
  - 장기처짐 배수 $\lambda_\Delta = \frac{\xi}{1 + 50\rho'}$ 산출식 명시.
* **KDS 14 20 30 제4.2.3절 균열방지 철근간격 제한 ($s \le s_{\max}$) 3-Station 개별 KaTeX 전개**:
  - **직접 산출된 인장철근 실 응력 $f_s$ 대입**:
    $$kd = \frac{-B_{kd} + \sqrt{B_{kd}^2 - 4 A_{kd} C_{kd}}}{2 A_{kd}}, \quad jd = d - \frac{kd}{3}, \quad f_s = \frac{M_s \times 10^6}{A_s \cdot jd}$$
  - **식 (4.2-4) 3-Station 위치별 KaTeX 수식 전개**:
    $$s_{\max} = 375 \left(\frac{k_{cr}}{f_s}\right) - 2.5 c_c \le 300 \left(\frac{k_{cr}}{f_s}\right)$$
    - **단부-I (End-I)**: 부모멘트 작용 $\rightarrow$ 상부 인장철근($A_{s,\text{top}}$) 기준 $f_{s,I}$, $s_{\max,I}$ 산출 및 실제 간격 $s_{I,\text{top}}$ 대조 ($\text{DCR} = s_{I,\text{top}} / s_{\max,I}$)
    - **중앙부-M (Center-M)**: 정모멘트 작용 $\rightarrow$ 하부 인장철근($A_{s,\text{bot}}$) 기준 $f_{s,M}$, $s_{\max,M}$ 산출 및 실제 간격 $s_{M,\text{bot}}$ 대조 ($\text{DCR} = s_{M,\text{bot}} / s_{\max,M}$)
    - **단부-J (End-J)**: 부모멘트 작용 $\rightarrow$ 상부 인장철근($A_{s,\text{top}}$) 기준 $f_{s,J}$, $s_{\max,J}$ 산출 및 실제 간격 $s_{J,\text{top}}$ 대조 ($\text{DCR} = s_{J,\text{top}} / s_{\max,J}$)
  - 배근 유형(단일/대칭/3단면)에 따라 해당되는 인장 단면별로 분리 전개 표출.

---

## 3. 완료 검증 기준 (Definition of Done)

- [ ] 순백색 A4 계산서에 제 3장(단면 연성 및 최소철근량 검토)이 독립 장으로 정상 렌더링될 것.
- [ ] 3-Station 개별 위치별 최소철근량 및 순인장변형률 수식이 배근 유형에 따라 분리 출력될 것.
- [ ] KaTeX 수식에 `aligned` 줄바꿈이 적용되어 우측 오버플로우가 0건일 것.
- [ ] 장황한 한글 브래킷 태그가 전면 삭제되고 `  →  O.K` 판정 및 DCR이 전수 표기될 것.
- [ ] $T_u = 0$, $M_u = 0$ 시 불필요한 장황 수식이 1줄 요약으로 동적 생략될 것.
- [ ] 제 6장에 Branson $I_e$ 가중평균 수식 블록이 KaTeX로 무결하게 출력될 것.
- [ ] 제 6장 균열방지 철근간격 제한($s \le s_{\max}$) 검토 시, 직접 산출된 $f_s$를 적용하여 3-Station 각 단면별 인장철근(단부: 상부, 중앙부: 하부)의 $s_{\max}$ 및 DCR이 분리 출력될 것.
