# 요구사항 22-4-1-4: Phase V1-01 Step 4-4 RC 보 A4 구조계산서 3-Station(I/M/J 정·부모멘트) 개별 KaTeX 계산근거 출력 및 E2E 무결점 통합 검증 명세서

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** A4 5대 장구분 구조계산서에서 **(1) 제 1장의 구버전 철근비 공식 완전 삭제 및 현행 KDS 14 20 20: 2022 ($\phi M_n \ge 1.2 M_{cr}$, $\epsilon_t \ge \epsilon_{t,\min}$) 3단계 KaTeX 수식 전개 반영**, **(2) 제 3장 휨모멘트 강도 검토에서 기존 중앙부 1개 단면 출력 한계를 극복하고 단부-I (부모멘트), 중앙부-M (정모멘트), 단부-J (부모멘트) 3개 위치별 역학 거동에 따른 개별 KaTeX 계산근거 완전 출력**, **(3) 제 4장 전단 검토의 3-Station 요약 및 지배 단부 KaTeX 3단계 전개**, 그리고 **(4) 전체 단위/통합 테스트 스위트 확충 및 349+ 회귀 테스트 100% 무결점 통과 검증**을 완수하기 위한 종합 완결 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/rc_beam_report.js` (신규 표준 파일명: A4 계산서 3-Station KaTeX 렌더링 전면 개편)
  - `tests/ui/test_phase22_4_rc_beam_report.py` (계산서 UI 및 수식 검증 테스트 스위트)
  - `tests/engine/test_rc_beam.py` (엔진 단위 테스트 연동)
  - `요구사항/PROJECT_PROGRESS.md` (프로젝트 마스터 진행 상태 및 외부 기억 동기화)
* **권장 AI 모델**: 🧠 **High (Thinking 모드 권장)** - 엄밀한 KaTeX LaTeX 수식 조립, 3-Station 공학 역학 대조 및 회귀 테스트 검증

---

## 2. A4 계산서 3-Station 개별 계산근거 출력 규격

### 2.1. 제 1장: 최소 철근량 및 연성 한계 KDS 14 20 20: 2022 3단계 KaTeX 전개
* 구버전 철근비 ($\rho_{\min}, \rho_{\max}$) 수식을 완전 삭제하고 아래 3단계 KaTeX 블록을 렌더링합니다:

```latex
% 1. 최소 철근량 검토 (KDS 14 20 20 4.2.2)
\phi M_n \ge 1.2 M_{cr} \quad \left(\text{단, } A_s \ge \frac{4}{3} A_{s,req} \text{ 만족 시 적용 예외}\right)
f_r = 0.63 \lambda \sqrt{f_{ck}}, \quad I_g = \frac{b h^3}{12}, \quad M_{cr} = \frac{f_r I_g}{y_t}
\phi M_n \ge 1.2 M_{cr} \quad \longrightarrow \quad [\mathbf{최소철근량 만족 O.K}]

% 2. 연성 한계 및 순인장변형률 검토 (KDS 14 20 20 4.1.2)
\epsilon_t \ge \epsilon_{t,\min} = \begin{cases} 0.0040 & (f_y \le 400\text{ MPa}) \\ 2.0\,\epsilon_y & (f_y > 400\text{ MPa}) \end{cases}, \quad \frac{c}{d_t} \le \left(\frac{c}{d_t}\right)_{\lim}
\epsilon_t = \epsilon_{cu} \left(\frac{d_t - c}{c}\right) \ge \epsilon_{t,\min} \quad \longrightarrow \quad [\mathbf{연성파괴 유도 O.K}]
```

### 2.2. 제 3장: 휨모멘트 강도 검토 3-Station 구조화 및 개별 수식 전개

```
[제 3장. 휨모멘트 강도 검토 (Flexural Strength Check)]
  │
  ├─ 3.1 3-Station 위치별 휨설계 강도 총괄 요약표
  │     (End-I 부모멘트, Center-M 정모멘트, End-J 부모멘트 대비 Mu, phi_Mn, DCR, 판정)
  │
  ├─ 3.2 단부-I (End-I) 부모멘트 (Mu-) 검토 [상부 인장 배근 / 복부폭 bw 직사각형 보]
  │     - Step 1: 등가 응력블록 깊이 a 및 중립축 c 산정 (상부 As_top 인장)
  │     - Step 2: 순인장변형률 et 및 강도감소계수 phi 산정
  │     - Step 3: 공칭휨강도 Mn 및 설계휨강도 phi_Mn 산정
  │     - Step 4: 소요 휨강도 대비 안전성 판정 (Mu- / phi_Mn <= 1.0)
  │
  ├─ 3.3 중앙부 (Center-M) 정모멘트 (Mu+) 검토 [하부 인장 배근 / T형 유효폭 bf 압축]
  │     - Step 1: 플랜지 압축 T형 거동 검토 및 응력블록 a, c 산정 (하부 As_bot 인장)
  │     - Step 2: 순인장변형률 et 및 강도감소계수 phi 산정
  │     - Step 3: 정모멘트 설계휨강도 phi_Mn 산정
  │     - Step 4: 소요 휨강도 대비 안전성 판정 (Mu+ / phi_Mn <= 1.0)
  │
  └─ 3.4 단부-J (End-J) 부모멘트 (Mu-) 검토
        - 배근 유형-2 (대칭) 시: "단부-I과 대칭 동일 단면 (Mu = ... kN·m, phi_Mn = ... kN·m, O.K)" 요약 표기
        - 배근 유형-3 (비대칭) 시: 단부-I과 동일한 KaTeX 4단계 완전 전개 출력
```

### 2.3. 제 4장: 전단 및 비틀림 강도 검토
- 3-Station 전단력 요약표 ($V_u, V_c, V_s, \phi V_n, \text{DCR}$) 표출.
- 최대 계수전단력이 작용하는 지배 단부(Governing Station)에 대한 콘크리트 전단강도 $V_c$, 전단철근 강도 $V_s$, 설계전단강도 $\phi V_n$ KaTeX 3단계 전개.

---

## 3. 단위 테스트 스위트 확충 및 검증 명세

### 3.1. `tests/ui/test_phase22_4_rc_beam_report.py` 확충
1. `test_rc_beam_report_3station_flexure_sections`:
   - 계산서 렌더링 결과에 `단부-I`, `중앙부`, `단부-J` 전용 휨 검토 섹션이 포함되어 있는지 검증.
2. `test_rc_beam_report_kds_min_rebar_katex`:
   - `\phi M_n \ge 1.2 M_{cr}` 및 `M_{cr}` 수식이 KaTeX로 정상 조립되어 있는지 검증.
3. `test_rc_beam_report_ductility_strain_limit_katex`:
   - `\epsilon_{t,\min}` 및 `c/d_t` 수식이 정상 포함되어 있는지 검증.
4. `test_rc_beam_report_no_legacy_rho_terms`:
   - 계산서 본문에 구버전 `\rho_{\min}`, `\rho_{\max}` 문자열이 완전히 배제되었는지 정규식 검증.

---

## 4. 완료 검증 기준 (DoD)

- [x] A4 계산서 제 1장에 $\phi M_n \ge 1.2 M_{cr}$ 및 $\epsilon_t \ge \epsilon_{t,\min}$ 수식이 KaTeX로 정확히 렌더링될 것.
- [x] A4 계산서 제 3장에서 단부-I(부모멘트), 중앙부-M(정모멘트), 단부-J(부모멘트)의 계산근거가 위치별 역학 특성에 맞추어 명확히 분리 출력될 것.
- [x] 계산서 전체에서 구버전 철근비 $\rho_{\min}, \rho_{\max}$ 수식이 1건도 나타나지 않을 것.
- [x] `tests/ui/test_phase22_4_rc_beam_report.py` 테스트 슈트가 100% 무결점 통과할 것.
- [x] `pytest` 전체 349+ 회귀 테스트가 에러 0건으로 100% 통과할 것.
- [x] `요구사항/PROJECT_PROGRESS.md`에 본 작업 완료 상태와 다음 작업(Phase 22-5)이 정확히 동기화될 것.
