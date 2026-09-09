# 요구사항 22-5-2: Phase V1-01 Step 5-2 RC 보 12포인트 순간격 검토, 부재력 disabled 동기화, Sticky 플로팅바 & 캔버스 버그 패치 명세서

---

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 프론트엔드 UI/UX 및 2D 캔버스 그래픽스의 **(1) 2D VDraw 캔버스 표피철근 0개 지정 시 비틀림 철근 2개가 강제로 그려지는 버그 픽스**, **(2) 단부-I, 중앙부-M, 단부-J 3개 위치 × 상/하부 1, 2단 총 12개 포인트 전 철근 순간격 실시간 전수 검토 엔진 및 UI 뱃지/상세 팝오버 표출**, **(3) 배근 유형(`arrange_type`) 변경 시 부재력 테이블의 행/셀 동적 `disabled` 및 대칭값 자동 복제**, **(4) 서브탭 바 및 3버튼 액션 바 상단 Sticky 플로팅 고정 및 32px 컴팩트 엔지니어링 버튼 스타일링**을 완수하기 위한 프론트엔드 전용 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/components/form_rc_beam.js` (12포인트 순간격 계산 엔진, 부재력 disabled/대칭 복제, 플로팅 바 구조화)
  - `src/web/static/js/visual/vector_rc_beam.js` (표피/비틀림 철근 널 병합 `?? 0` 패치 및 0개 시 렌더링 스킵)
  - `src/web/static/css/style.css` (상단 Sticky 플로팅 바, 32px 컴팩트 버튼, 순간격 뱃지/팝오버 스타일)
* **권장 AI 모델**: ⚙️ **Medium (DOM/UI 조작 및 그래픽스)**
* **연동 SSOT**: [`docs/07 PART 4`](../docs/07_web_application_ui_ux_specification.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)

---

## 2. 세부 구현 사양 명세

### 2.1. 2D VDraw 캔버스 표피철근 0개 오표기 버그 수정 (`vector_rc_beam.js`)
* **현황 및 원인**: 라인 105 부근에서 `const torsionSideCount = Number(r.torsion_side_count || data.torsion_side_count || 2);` 와 같이 OR(`||`) 연산자를 사용하여, 사용자가 `0`을 입력해도 Falsy로 평가되어 기본값 2가 대입됨.
* **수정 조치**:
  1. 널 병합 연산자(`??`) 적용:
     ```javascript
     const torsionSideCount = Number(r.torsion_side_count ?? data.torsion_side_count ?? 0);
     ```
  2. `torsionSideCount === 0`일 경우 측면 비틀림 철근 그리기 루프 및 인터랙티브 호버 툴팁 생성을 전면 스킵.

---

### 2.2. 3-Station × 4-Layer 총 12개 포인트 전 철근 순간격 실시간 전수 검토 (`form_rc_beam.js`)
1. **검토 대상 (총 12개 위치)**:
   - **단부 I (End-I)**: 상부 1단, 상부 2단, 하부 1단, 하부 2단
   - **중앙부 M (Center-M)**: 상부 1단, 상부 2단, 하부 1단, 하부 2단
   - **단부 J (End-J)**: 상부 1단, 상부 2단, 하부 1단, 하부 2단
2. **순간격 산정 공식**:
   - 수평 순간격:
     $$s_{clear} = \frac{b_w - 2(c_c + d_{stirrup}) - n \cdot d_b}{n - 1} \quad (n \ge 2)$$
     ($n = 1$ 인 경우 한 줄에 1개이므로 여유 충족으로 처리)
   - 규준 요구 최소 순간격 (KDS 14 20 50 제4.1절):
     $$s_{req} = \max(25\text{ mm}, d_b, 1.33 d_{agg}) \quad (\text{굵은골재 최대치수 } d_{agg}=25\text{mm})$$
   - 2단 배근 시 수직 순간격: $s_{vert} \ge \max(25\text{ mm}, d_b)$
3. **실시간 UI 표출 방식**:
   - **대표 상태 뱃지**: 12개 포인트 중 최소 순간격($\min s_{clear}$)을 갖는 거버닝 포인트를 상단/배근탭에 뱃지로 즉시 표출 (예: `최소 순간격: 32.5mm [M-하부1단] (O.K)` 또는 `NG: 18.2mm [I-상부1단]`).
   - **상세 상태표/팝오버**: 클릭 또는 호버 시 12개 위치별 $s_{clear}$ 및 O.K/N.G 상태를 일목요연하게 확인할 수 있는 그리드/툴팁 제공.

---

### 2.3. 배근 유형에 따른 부재력 입력 테이블 동적 `disabled` 및 대칭 복제 (`form_rc_beam.js`)
* **`rebar.arrange_type` 변경 이벤트 바인딩**:
  1. **`ONE_SECTION` (전단면 동일)**:
     - Center-M 행만 활성화 (`disabled = false`).
     - End-I, End-J 행은 `disabled = true` 처리 및 스타일(불투명도 0.5, 배경색 변경) 적용.
     - 안내 문구: *"전단면 동일 배근 (중앙부 부재력 적용)"*
  2. **`SYMMETRIC_ENDS` (양단부 대칭 및 중앙부)**:
     - End-I 행과 Center-M 행 활성화.
     - End-J 행은 `disabled = true` 처리.
     - End-I의 입력 필드(`Mu_neg`, `Mu_pos`, `Vu`, `Tu`) 수정 시 End-J의 해당 필드에 동일 값이 실시간 복제 반영됨 (*"단부-I 대칭 동기화"*).
  3. **`THREE_STATIONS` (각단부와 중앙부)**:
     - End-I, Center-M, End-J 3개 행 모두 활성화하여 독립 입력 허용.

---

### 2.4. 상단 Sticky 플로팅 바 & 32px 컴팩트 버튼 UI (전 모듈 공통 표준 `docs/07`)
1. **전 모듈 공통 Sticky 플로팅 컨테이너 (`style.css` & `form_rc_beam.js`)**:
   - `docs/07 PART 1 제4.2절 및 PART 4 제20절`에 신규 표준으로 제정된 공통 규격 적용.
   - `.form-sticky-header` (또는 `.beam-sticky-header`) 래퍼에 `position: sticky; top: 0; z-index: 25; backdrop-filter: blur(8px); background: rgba(var(--bg-card-rgb), 0.95);` 적용.
   - RC 보뿐만 아니라 향후 54개 전 모듈의 입력 폼 스크롤 시에도 3대 액션 버튼(`[💾 적용] [⚡ 검토] [✨ 자동설계]`)과 상부 서브탭 바가 최상단에 상시 고정 유지.
2. **32px 컴팩트 엔지니어링 버튼 표준**:
   - 버튼 높이: `32px` (기존 약 42px에서 슬림화하여 상단 낭비 공간 제거).
   - 패딩: `5px 12px`, 폰트: `12px / font-weight: 600`.
   - 전 모듈 공통 클래스(`.btn-action-compact`, `.btn-apply-action`, `.btn-check-action`, `.btn-design-action`)로 통일하여 일관된 고품격 마이크로 인터랙션 보장.

---

## 3. 완료 검증 기준 (Definition of Done)

- [x] `vector_rc_beam.js`에서 표피철근 0개 입력 시 캔버스에 비틀림 철근이 0개로 정확히 렌더링될 것.
- [x] 3-Station 4-Layer 총 12개 포인트 철근 순간격이 실시간으로 계산되고 최악 거버닝 뱃지와 상세 팝오버가 정상 작동할 것.
- [x] `rebar.arrange_type`에 따라 부재력 입력 테이블의 비활성화(disabled) 및 대칭 복제가 오동작 없이 실시간 반응할 것.
- [x] 서브탭 바 및 액션 버튼 바가 상단에 Sticky로 안정적으로 고정되고, 32px 컴팩트 버튼 디자인이 `docs/07` 표준에 부합하게 적용될 것.
- [x] 브라우저 콘솔 에러 0건 및 기존 회귀 테스트 100% 통과를 유지할 것.
