# RC 보 (RC Beam) 설계 모듈 종합 명세서 (201_rc_beam_module_specification.md)

본 문서는 AltDP_3rd 시스템의 플래그십 단위부재인 **RC 보 (`rc_beam` / 원본 C++ `CHK_BBBE`) 모듈**에 대한 전용 기술 명세서(Module SSOT)입니다. 원본 데스크톱 바이너리 역공학 자산, KDS 기준 계산 엔진, 전용 파라메트릭 Web UI/UX 인터페이스, 2D 벡터 그래픽 뷰포트 및 KDS 순백색 A4 구조계산서 전개 체계를 총체적으로 집대성합니다.

---

## 1. 개요 및 원본 데스크톱 역공학 분석 (Ground Truth)

### 1.1. C++ 핵심 루틴 및 심볼 (`decompiled_src/core_routines/rc/`)
* **핵심 연산 루틴**: `rc__CHK_BBBE_CRCSCodeCheck__QEAA_NI_Z.c`, `rc__CHK_BBBE_CRCSCodeCheck__QEAA_NAEBV__CArray_II___Z.c`
* **드로잉 엔진**: `DPLUS_VDraw.dll` 내 `CODABeamBase` (횡단면 배근 및 길이방향 BMD/SFD/배근포락선 생성)
* **주요 연산 체계**:
  * 휨모멘트 강도 ($\phi M_n$): 등가직사각형 응력블록 깊이 $a = \frac{A_s f_y}{0.85 f_{ck} b}$, 공칭모멘트 $M_n = A_s f_y (d - a/2)$, 현행 KDS 최외단 인장변형률 $\epsilon_t$ 연동 $\phi(0.65 \sim 0.85)$.
  * 전단강도 ($V_c, V_s$): 콘크리트 $V_c = \frac{1}{6}\lambda\sqrt{f_{ck}} b_w d$, 전단철근 $V_s = \frac{A_v f_{yt} d}{s}$, 상한 $V_{n,\max} \le V_c + 0.66\sqrt{f_{ck}} b_w d$.
  * 사용성 처짐 ($I_e$): Branson 공식 $I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \le I_g$.

### 1.2. 원본 MFC 다이얼로그 리소스 매핑 (`DLG_DPLUS_RCS.ini`)
`IDD_RCS_BEAM_PMODE_DLG`, `IDD_RCS_DEFL_DLG`, `IDD_RCS_BEAM_SECT_DLG`, `IDD_RCS_BEAM_BEFF_DLG`를 역공학 분석하여 도출된 6대 입력 도메인입니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 원본앱 RC 보 6대 핵심 입력 도메인 (IDD_RCS_BEAM_PMODE_DLG 역공학)                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 재료 물성치 : fck, fy(주철근), fys(스터럽), 경량콘크리트 계수(λ)                    │
│ 2. 단면 형상   : 폭(b), 높이(h), 상/하부 순피복, 사각형 vs T형보 (슬래브 두께 hf, 유효폭 bf)│
│ 3. 배근 유형   : Type 1(전단면 단일), Type 2(양단부-중앙부 대칭), Type 3(각단부-중앙부 3단면)│
│ 4. 배근 옵션   : 열마다 다른 철근 사용 여부, 상-하부 동일 철근 적용 여부, 표피철근(Skin Bar)│
│ 5. 철근 이음   : 이음하지 않음(0%), 반수 이음(50%), 전수 이음(100%)                      │
│ 6. 구조 성능   : 내진상세(SMF/IMF/OMF/필로티), 처짐(하중방식/모멘트방식), 균열(건조/기타환경)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. RC 보 전용 Web UI/UX 상세 명세 (Pane 2 & Pane 3)

### 2.1. 4대 서브탭 구성 (`src/web/static/js/components/form_rc_beam.js`)
1. **[단면 / 재료 탭]**: 단면 형상(직사각형/T형), 단면 치수($b, h, L$), 슬래브 두께($h_f$), 유효 플랜지폭($b_e$), KS 표준 강종($f_{ck}, f_y, f_{yt}$), 피복두께.
2. **[철근 배근 탭]**: 배근 유형 라디오, 단부-I / 중앙부-M / 단부-J 상하부 다단 주철근, 스터럽 직경/간격/다리수, 표피/비틀림 철근.
3. **[부재력 / 하중 탭]**: 3-Station별 계수 정/부 휨모멘트($M_u^+, M_u^-$), 계수 전단력($V_u$), 계수 비틀림($T_u$).
4. **[사용성 / 처짐 탭]**: 사용하중 모멘트($M_a$), 지속하중 모멘트($M_{sus}$), 허용 처짐비($L/240$), 노출 환경(건조/습윤), 내진 등급.

### 2.2. 배근 유형(Arrange Type) 3대 라디오 옵션 시스템
* **`ONE_SECTION` (배근 유형-1: 전단면)**:
  - 단일 단면 배근. 임의 위치 수정 시 End-I, Center-M, End-J 3개 위치에 동일 값이 실시간 일괄 복사 동기화.
* **`SYMMETRIC_ENDS` (배근 유형-2: 양단부와 중앙부, 기본값 Default)**:
  - 실무 표준 배근. 단부-I 수정 시 단부-J 셀이 실시간 양방향 자동 동기화되며, 단부-J 행은 시각적으로 `[단부-I 대칭 연동]` 태그 표출 및 비활성화(디밍) 처리.
* **`THREE_STATIONS` (배근 유형-3: 각단부와 중앙부)**:
  - End-I, Center-M, End-J 3개 위치 모든 셀이 독립적으로 활성화되어 비대칭 골조 보 배근 완벽 지원.

### 2.3. 주철근 복합 분리입력 컨트롤 (Composite Input Control)
단일 텍스트박스(`4-D25` 직접 타이핑)의 오탈자를 원천 방지하는 3분할 인라인 복합 컨트롤:
* **구조**: `[개수 텍스트박스] + [-] 고정 라벨 + [호칭경 셀렉트 콤보박스]`
* **1단 주근 (상/하부 1단)**: 스터럽 코너 정착 및 유효 휨내력 확보를 위한 **최소 2개 제약(`min="2"`)** 적용.
* **2단 주근 (상/하부 2단)**: 추가 보강단이므로 **0개 이상 허용(`min="0"`)**, `0` 입력 시 셀 디밍 및 미배치 처리.
* **호칭경 콤보박스**: KS D 3504 표준 9종(`D10`, `D13`, `D16`, `D19`, `D22`, `D25`, `D29`, `D32`, `D35`) 드롭다운 지원.

### 2.4. 배근 유형 연동 부재력(Forces) 테이블 동적 동기화 (Disabled Sync)
* `ONE_SECTION`: 중앙부(Center-M) 행만 활성화, End-I/End-J 행은 `disabled` 처리.
* `SYMMETRIC_ENDS`: End-I 및 Center-M 행 활성화, End-J 행은 `disabled` 처리되고 End-I의 입력 필드(`Mu_neg`, `Mu_pos`, `Vu`, `Tu`) 수정 시 End-J에 실시간 대칭 복제 동기화.
* `THREE_STATIONS`: End-I, Center-M, End-J 3개 행 모두 활성화되어 독립 부재력 입력 허용.

### 2.5. 3-Station × 4-Layer 총 12개 포인트 철근 순간격(Clear Spacing) 검토
단부-I, 중앙부-M, 단부-J 3개 위치 × 상/하부 1, 2단 총 12개 포인트의 순간격을 실시간 연산:
* **수평 순간격**: $s_{clear} = \frac{b_w - 2(c_c + d_{stirrup}) - n \cdot d_b}{n - 1} \quad (n \ge 2)$
* **수직 순간격**: $s_{vert} \ge \max(25\text{ mm}, d_b)$
* **규준 요구치**: $s_{req} = \max(25\text{ mm}, d_b, 1.33 d_{agg})$
* **대표 거버닝 뱃지**: 12개 포인트 중 최소 순간격을 갖는 위치를 뱃지로 표출 (예: `최소 순간격: 32.5mm [M-하부1단] (O.K)`).
* **상세 팝오버**: 클릭 시 12개 위치별 $s_{clear}$ 및 O.K/N.G 상태 전수 그리드 툴팁 제공.

### 2.6. RC 보 전용 2단 적층 그래픽 뷰포트 (Pane 3)
* **1단 (상단: 단면 배근도)**:
  - 단부(End-I, J) 및 중앙(Center-M) 단면의 정밀 횡단면 (외곽선 해칭, 콘크리트 피복선, 135° 내진 갈고리 스터럽, 다단 주철근 점, 치수선 $b \times h$, 호버 툴팁).
  - **표피/비틀림 철근 널 병합(`?? 0`) 패치**: 0개 입력 시 렌더링을 완전히 스킵.
* **2단 (하단: 부재력도 및 길이방향 배근도)**:
  - 3-Station에 걸친 계수 휨모멘트도(BMD) 및 전단력도(SFD) 곡선과 상/하부 주철근 배근 포락선(Envelope) 시각화.

---

## 3. RC 보 KDS 설계 엔진 아키텍처 (`src/engine/rc/beam.py`)

1,811줄 규모의 완성형 엔지니어링 엔진으로 다음 KDS 기준을 완벽 구현합니다:

### 3.1. KDS 14 20 10 휨/연성 해석
* **단근 및 복근 직사각형/T형 보 완전 대응**.
* **콘크리트 압축강도별 응력블록 깊이비 ($\beta_1$)**:
  $$\beta_1 = \begin{cases} 0.80 & (f_{ck} \le 28\text{ MPa}) \\ 0.80 - \frac{0.05(f_{ck}-28)}{7} & (28 < f_{ck} < 56) \\ 0.60 & (f_{ck} \ge 56\text{ MPa}) \end{cases}$$
* **최외단 인장변형률 $\epsilon_t = 0.0033 \frac{d_t - c}{c}$ 산정에 따른 강도감소계수 ($\phi$) 구간 선형 보간**:
  $$\phi = \begin{cases} 0.65 & (\epsilon_t \le \epsilon_{ty}) \\ 0.65 + 0.20 \frac{\epsilon_t - \epsilon_{ty}}{0.005 - \epsilon_{ty}} & (\epsilon_{ty} < \epsilon_t < 0.005) \\ 0.85 & (\epsilon_t \ge 0.005) \end{cases}$$
* **최소철근비 및 연성 한계**:
  $$\rho_{\min} = \max\left(\frac{0.25\sqrt{f_{ck}}}{f_y}, \frac{1.4}{f_y}\right), \quad \epsilon_t \ge 0.004 \quad \left(\frac{c}{d_t} \le 0.452\right)$$

### 3.2. KDS 14 20 22 전단 및 비틀림 해석
* **콘크리트 및 전단철근 전단강도**:
  $$V_c = \frac{1}{6}\lambda\sqrt{f_{ck}} b_w d, \quad V_s = \frac{A_v f_{yt} d}{s}, \quad V_n \le V_c + 0.66\sqrt{f_{ck}} b_w d$$
* **비틀림 해석**:
  $$T_{cr} = \frac{1}{3}\lambda\sqrt{f_{ck}}\left(\frac{A_{cp}^2}{p_{cp}}\right), \quad T_{th} = 0.25 \phi T_{cr}$$
  $$A_l = \left(\frac{A_t}{s}\right) p_h \left(\frac{f_{yt}}{f_y}\right) \cot^2\theta, \quad A_{l,\min} = \frac{0.42\sqrt{f_{ck}} A_{cp}}{f_y} - \left(\frac{A_t}{s}\right) p_h \left(\frac{f_{yt}}{f_y}\right)$$
* **휨-전단-비틀림 상호작용 검토**:
  $$\sqrt{\left(\frac{V_u}{b_w d}\right)^2 + \left(\frac{T_u p_h}{1.7 A_{oh}^2}\right)^2} \le \phi \left(\frac{V_c}{b_w d} + 0.66\sqrt{f_{ck}}\right)$$

### 3.3. KDS 14 20 30 사용성 한계상태 (처짐 및 균열)
* **Branson 유효단면2차모멘트 ($I_e$)**:
  $$I_e = \left(\frac{M_{cr}}{M_a}\right)^3 I_g + \left[1 - \left(\frac{M_{cr}}{M_a}\right)^3\right] I_{cr} \le I_g$$
* **장기처짐 증분계수**:
  $$\lambda_\Delta = \frac{\xi}{1 + 50\rho'} \quad (\xi = 2.0, \ 5\text{년 이상})$$
* **KDS 14 20 30 제4.2.3절 건조/습윤 인장철근 최대 순간격 ($s_{\max}$)**:
  $$s_{\max} = 375\left(\frac{k_{cr}}{f_s}\right) - 2.5 c_c \le 300\left(\frac{k_{cr}}{f_s}\right) \quad (k_{cr}=280 \text{ 건조}, 210 \text{ 습윤})$$

### 3.4. 0 하중 및 0 전단 시 방어 로직
외력이 0이더라도 KDS 최소철근비, 최소전단철근($A_{v,\min}$), 최소비틀림철근 검토를 강제 수행하여 DCR 및 판정을 엄밀히 도출.

---

## 4. RC 보 KDS 표준 구조계산서 상세 서식 (Pane 4)

### 4.1. 요약 보고서 (Summary Report)
```markdown
# [RC 보 1F-B1] KDS 구조계산서 (요약 보고서)

## 1. 일반 설계 조건 및 사용 재료
- 프로젝트: AltDP_3rd Engineering | 부재명: 1F-B1 | 검토일자: 2026-09-09
- 적용 기준: KDS 14 20 00 | 단위계: SI Unit (kN, mm, MPa)
- 재료 특성: fck = 24.0 MPa, fy = 400.0 MPa, fyt = 400.0 MPa, Es = 200,000 MPa, β1 = 0.85

## 2. 단면 제원 및 배근 상세 (2D SVG 단면도 포함)
- 단면 크기: b = 400 mm, h = 600 mm, d = 536.0 mm, dt = 547.0 mm, 순피복 = 40 mm
- 상단 배근: 1단 3-D22 + 2단 2-D22 (As,top = 1,935.5 mm²)
- 하단 배근: 1단 4-D25 (As,bot = 2,026.8 mm²)
- 전단 배근: 2-D10 @ 150 mm (Av = 142.6 mm²)

## 3. 한계상태별 안전성 검토 결과 종합표 (DCR Summary)
| 검토 단면 (Station) | 검토 항목 (Limit State) | 계수 소요력 (Demand) | 설계 내력 (Capacity) | DCR | 판정 |
|---|---|---|---|---|---|
| **Center-M (중앙부)** | 정모멘트 휨강도 (φMn+) | 210.00 kN·m | 337.88 kN·m | **0.622** | **PASS** 🟢 |
| **End-I (좌측단부)** | 부모멘트 휨강도 (φMn-) | 185.00 kN·m | 324.50 kN·m | **0.570** | **PASS** 🟢 |
| **End-I (좌측단부)** | 전단강도 (φVn) | 150.00 kN | 286.28 kN | **0.524** | **PASS** 🟢 |
| **Center-M (중앙부)** | Branson 총 처짐 (Δtot) | 10.0 mm | 24.0 mm (L/250) | **0.417** | **PASS** 🟢 |
| **Center-M (중앙부)** | KDS 직접 균열폭 (w) | 0.16 mm | 0.30 mm | **0.533** | **PASS** 🟢 |

- **최대 지배 DCR**: **0.622** (중앙부 정모멘트 휨)
- **종합 안전성 판정**: **OK (만족 / SAFE)** 🟢
```

### 4.2. 상세 보고서 KDS 정밀 7대장 체계 (Detail Report)

```markdown
# [부재명: 1F-B1] KDS 구조계산서 (상세 보고서)

## 제 1장. 부재 형상 및 비주얼 단면 배근도 (Section Geometry & Layout)
- 부재 명칭: 1F-B1 (경간 L = 6,000 mm, 순경간 Ln = 5,600 mm)
- 단면 제원: b = 400 mm, h = 600 mm, d = 536.0 mm, dt = 547.0 mm
- 철근 순간격 검토: sclear = 42.5 mm ≥ max(db=25.4, dagg=25, 25mm) = 25.4 mm (PASS)

## 제 2장. 사용 재료 및 설계 기준 계수 (Materials & Design Parameters)
- 콘크리트 압축강도: fck = 24.0 MPa (KDS 14 20 10)
- 주철근 / 전단철근 항복강도: fy = 400.0 MPa, fyt = 400.0 MPa (SD400)
- 탄성계수: Ec = 25,815 MPa, Es = 200,000 MPa, β1 = 0.85

## 제 3장. 배근율 및 연성/단면 제한 검토 (Reinforcement Limits & Ductility)
1. 최소 철근비 및 소요 면적:
   ρ_min = max(0.25√24 / 400, 1.4 / 400) = 0.00350
   As,min = 750.4 mm² ≤ As,prov = 2,026.8 mm² (PASS)
2. 연성 한계 검토:
   c / dt ≤ (c / dt)_lim = 0.452 (εt ≥ 0.004)

## 제 4장. 공칭 및 설계 휨강도 상세 산정 (Flexural Capacity)
1. 등가직사각형 응력블록 깊이: a = (As · fy) / (0.85 · fck · b) = 99.35 mm
2. 중립축 깊이: c = a / β1 = 116.89 mm
3. 최외단 인장변형률: εt = 0.0033 · (dt - c) / c = 0.01214 ≥ 0.005 (인장지배, φ = 0.85)
4. 공칭 휨강도: Mn = As · fy · (d - a/2) = 394.68 kN·m
5. 설계 휨강도: φMn = 0.85 · Mn = 335.48 kN·m
6. 휨 DCR: Mu / φMn = 210.00 / 335.48 = 0.626 ≤ 1.0 (PASS)

## 제 5장. 공칭 및 설계 전단/비틀림 강도 산정 (Shear & Torsion Capacity)
1. 콘크리트 분담 전단강도: Vc = (1/6) · λ · √fck · bw · d = 175.06 kN
2. 전단철근 분담 전단강도: Vs = (Av · fyt · d) / s = 203.82 kN
3. 최대 전단강도 상한: Vs ≤ 0.66√fck · bw · d = 690.23 kN (PASS)
4. 설계 전단강도: φVn = 0.75 · (Vc + Vs) = 284.16 kN
5. 전단 DCR: Vu / φVn = 150.00 / 284.16 = 0.528 ≤ 1.0 (PASS)
6. 최소 전단철근 및 간격: Av ≥ Av,min = 45.93 mm² (PASS), s = 150 mm ≤ s_max = 268.0 mm (PASS)

## 제 6장. 사용성 한계상태 검토 (처짐 및 균열 - KDS 14 20 30)
1. Branson 유효단면2차모멘트: Ie = 3.592 × 10⁹ mm⁴ ≤ Ig = 7.200 × 10⁹ mm⁴
2. 즉시/장기처짐: Δi = 4.9 mm, λΔ = 1.379, Δtot = 10.2 mm ≤ Δallow = L/250 = 24.0 mm (PASS)
3. 균열방지 철근간격: s_actual = 98.0 mm ≤ s_max = 293.8 mm (PASS)

## 제 7장. 종합 안전성 검토 판정표 (Executive DCR Summary)
- 최대 지배 DCR: 0.626 (중앙부 정모멘트 휨)
- 최종 판정: ALL OK 🟢
```

---

## 5. 차세대 플랫폼(AltDP-Core) 정렬 계획

RC 보 모듈은 현재 안정적으로 동작하고 있으나, 차세대 공통 아키텍처와의 일관성을 위해 다음 정렬 작업이 예정되어 있습니다:
1. **Tracer AST 전면 도입**:
   - `src/engine/rc/beam.py`의 계산서 생성 로직을 `src/core/tracer.py` AST 트리 생성 파이프라인으로 전환.
2. **2D Geometry AST 연동**:
   - 프론트엔드 직접 드로잉에서 `src/core/geometry.py` 월드좌표 AST 수신 렌더링으로 단일화.
