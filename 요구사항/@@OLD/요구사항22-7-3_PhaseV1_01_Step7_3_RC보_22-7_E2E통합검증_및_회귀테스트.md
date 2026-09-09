# 요구사항 22-7-3: Phase V1-01 Step 7-3 RC 보 22-7 E2E 통합 검증, 0하중 인터랙션 및 회귀 테스트 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)**의 Step 7-1(백엔드 최소배근 엔진) 및 Step 7-2(A4 계산서 0전단 생략 및 최소배근 KaTeX) 구현 사항을 바탕으로, **(1) 4-Pane 워크스페이스(부재목록-입력폼-캔버스-계산서) 100ms 실시간 동기화 검증**, **(2) $V_u=0$, $M_u=0$, $T_u=0$ 등 0하중 복합 시나리오에서의 동적 생략 및 최소 배근량(휨 $\phi M_n \ge 1.2 M_{cr}$, 전단 $A_{v,prov} \ge A_{v,\min}$, 간격 $s \le s_{\max}$) 상시 표출 브라우저 E2E 육안 검증**, **(3) 브라우저 개발자 도구 콘솔 에러 0건 입증**, 그리고 **(4) 전체 단위/통합 테스트 회귀 무결성(391+ tests 100% PASS)**을 최종 검수하기 위한 통합 검증 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 및 테스트 파일**:
  - `src/web/static/js/components/form_rc_beam.js`
  - `src/web/static/js/report/rc_beam_report.js`
  - `tests/engine/test_rc_beam.py`
  - `tests/api/test_rc.py`
  - `tests/ui/test_phase22_4_rc_beam_report.py`
* **권장 AI 모델**: ⚙️ **Medium** - DOM UI 검증, E2E 이벤트 연결 및 전체 회귀 테스트 실행
* **연동 SSOT**: [`docs/07 PART 4`](../docs/07_web_application_ui_ux_specification.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)

---

## 2. 4-Pane E2E 통합 검증 시나리오

### 2.1. [시나리오 1] 일반 설계 하중 정상 검토
* **입력 제원**:
  - 단면: $400 \times 600\text{ mm}$, 콘크리트 $f_{ck} = 27\text{ MPa}$, 주철근 $f_y = 400\text{ MPa}$, 스터럽 $f_{yt} = 400\text{ MPa}$
  - 배근: End-I 상부 4-D25 / 하부 2-D22, Center-M 상부 2-D22 / 하부 4-D25+2-D25, 스터럽 D10@150 (2-legs), 측면 4-D13
  - 하중: End-I $M_u^- = 240\text{ kN}\cdot\text{m}, V_u = 180\text{ kN}, T_u = 15\text{ kN}\cdot\text{m}$
* **검증 항목**:
  - 제 3장: $\phi M_n \ge 1.2 M_{cr}$ 및 $\epsilon_t \ge 0.0040$ KaTeX 정상 출력.
  - 제 5장 5.2절: $V_u = 180\text{ kN}$ 전단강도 상세 수식 정상 출력.
  - 제 5장 5.3절: $A_{v,\min} = 52.5\text{ mm}^2 \le A_{v,prov} = 142.7\text{ mm}^2$ 및 $s = 150 \le s_{\max} = 270\text{ mm}$ KaTeX 정상 출력.
  - 제 5장 5.4절: $T_u = 15 > \phi T_{th}$이므로 $(A_v + 2A_t)_{\min}$ 및 $A_{l,\min}$ KaTeX 정상 출력.

---

### 2.2. [시나리오 2] 전단력 0 ($V_u = 0.0\text{ kN}$) 입력 검증
* **입력 조작**:
  - Pane 2 하중 탭에서 End-I, Center-M, End-J의 $V_u$를 모두 `0.0`으로 변경.
* **검증 항목**:
  - 제 5장 5.2절: 상세 전단강도 식이 사라지고, *"작용 계수전단력 없음 ($V_u = 0.0\text{ kN}$) — 전단강도 상세 검토 생략"* 1줄 요약 박스가 표출될 것.
  - **제 5장 5.3절: 최소 전단철근량($A_{v,\min}$) 및 최대 허용간격($s_{\max}$) 검토는 그대로 유지되어 온전하게 출력될 것**.

---

### 2.3. [시나리오 3] 전체 하중 0 ($M_u = 0, V_u = 0, T_u = 0$) 무하중 검증
* **입력 조작**:
  - Pane 2 하중 탭에서 모든 $M_u, V_u, T_u$를 `0.0`으로 변경.
* **검증 항목**:
  - 제 4장: 휨모멘트 강도 검토 1줄 요약 생략 표출.
  - 제 5장 5.2절: 전단강도 상세 검토 1줄 요약 생략 표출.
  - 제 5장 5.4절: 비틀림 설계 1줄 요약 생략 표출.
  - **제 3장: 신 기준 휨 최소철근량($\phi M_n \ge 1.2 M_{cr}$) 및 순인장변형률($\epsilon_t \ge \epsilon_{t,\min}$) 검토 상시 100% 표출**.
  - **제 5장 5.3절: 최소 전단철근량($A_{v,prov} \ge A_{v,\min}$) 및 최대 배근간격($s \le s_{\max}$) 검토 상시 100% 표출**.

---

### 2.4. [시나리오 4] 최소 배근 규정 위반(NG) 경계값 검증
* **입력 조작**:
  - 스터럽 간격을 규준 최대치($d/2 = 270\text{ mm}$)를 초과하는 `350 mm`로 입력.
* **검증 항목**:
  - 제 5장 5.3절에서 $\text{DCR}_{spacing} = 350 / 270 = 1.296 > 1.000$으로 계산되어 `  →  N.G` 빨간색 경고 표출.
  - 제 7장 종합 판정표에서 최종 부재 판정이 `N.G`로 전환될 것.

---

## 3. 전체 회귀 테스트 실행 계획

```bash
# 1. RC 보 엔진 단위 테스트
pytest tests/engine/test_rc_beam.py -v

# 2. RC API 라우트 테스트
pytest tests/api/test_rc.py -v

# 3. 계산서 렌더러 테스트
pytest tests/ui/test_phase22_4_rc_beam_report.py -v

# 4. 시스템 전체 회귀 테스트 (391+ tests)
pytest
```

---

## 4. 완료 검증 기준 (Definition of Done)

- [ ] 브라우저 4-Pane 워크스페이스에서 0하중 시나리오(시나리오 1~4)가 100% 정상 작동할 것.
- [ ] 브라우저 개발자 도구 콘솔에 에러(Error)가 0건일 것.
- [ ] 스터럽 간격 초과 시 즉각 `N.G` 판정으로 연동될 것.
- [ ] 전체 회귀 테스트(`pytest`) 391개 이상 100% 통과 (0 Failures).
- [ ] [`요구사항/PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md)에 완료 상태가 동기화될 것.
