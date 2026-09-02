# 요구사항 14-2: 단일 부재 4분할 Memb View 및 P/S/M 모드 파라메트릭 입력 폼

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+의 단일 부재 설계 환경(`CMainFormViewMemb`)은 좌측의 파라메트릭 속성 그리드와 우측의 2D 배근도, P-M 곡선, 계산서 요약창이 동기화된 4분할 워크스페이스입니다.
* 사용자가 단면 치수, 철근 배근, 재료 강도를 변경하면 즉시 2D Canvas 단면도와 3D P-M 곡선, 그리고 KDS DCR 계산 결과가 0.05초 이내 실시간 갱신되는 4-Pane 반응형 인터페이스를 구축하고, `P-Mode`(파라메트릭 자동설계), `S-Mode`(단면검토), `M-Mode`(일괄관리) 3대 인터랙션 모드를 완성합니다.

### 1.2. 참조 Ground Truth 자산
* **UI 역공학 명세 (SSOT)**: [`docs/13_midas_design_plus_original_ui_specification.md`](file:///d:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md)
* **디컴파일 폼 다이얼로그**: `original_src/Midas Design+/Dbase/` 및 `decompiled_src/core_routines/` 내 `DLG_*.ini` (RC 보/기둥/벽체/슬래브/기초, 철골 보/기둥/접합부/주각부 폼 24종)

---

## 2. 상세 구현 명세

### 2.1. 4분할 단일 부재 워크스페이스 (`src/web/templates/view_memb.html`)
* **Pane 1 (좌측: 파라메트릭 입력 패널)**:
  - 부재 선택 콤보박스(RC 보/기둥/벽체/슬래브/기초/옹벽, 철골 보/기둥/가새/접합부/베이스플레이트).
  - P-Mode / S-Mode / M-Mode 원클릭 전환 탭.
  - 단면 형상 치수, 주철근/늑근 배근 규격, 재료 강도($f_{ck}, f_y$), 하중 케이스 테이블 입력 그리드.
  - P-Mode 활성화 시 소요 철근량에 맞춘 'Auto Design' 원클릭 배근 자동 제안.
* **Pane 2 (우상단: 2D 단면 배근도 캔버스 `renderer2d.js`)**:
  - 단면 외곽선, 피복두께, 주철근, 전단 늑근/스터럽, 치수선, 철근 태그(예: 4-D25, D10@150) 실시간 드로잉.
  - 마우스 휠 줌/팬(Zoom/Pan) 및 더블클릭 초기화 지원.
* **Pane 3 (우하단: 3D/2D P-M 상관곡선 & 전단 DCR 차트 `pm_chart.js`)**:
  - 축력-휨($P-M_x, P-M_y$) 상관곡선 및 설계 하중점($P_u, M_u$) 플로팅, 실시간 DCR 게이지.
* **Pane 4 (하단: KDS 실시간 검토 요약표 & 빠른 계산서)**:
  - 휨, 전단, 비틀림, 균열, 처짐 항목별 $DCR = \frac{Design}{Capacity}$ 상태(PASS/NG) 및 핵심 지배 하중조합 표시.

### 2.2. 부재별 파라메트릭 폼 라이브러리 (`src/web/static/js/member_forms/`)
* RC 6대 부재 및 철골 6대 부재별 전용 입력 필드 바인딩 및 유효성 검사기 모듈화.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/web/templates/view_memb.html`](file:///d:/PyProject/AltDP_3rd/src/web/templates/view_memb.html) | [NEW] | 4분할 단일 부재 메인 워크스페이스 템플릿 구현 |
| [`src/web/static/js/renderer2d.js`](file:///d:/PyProject/AltDP_3rd/src/web/static/js/renderer2d.js) | [MODIFY] | RC/철골 전 부재 단면 및 치수선 인터랙티브 캔버스 렌더러 확장 |
| [`src/web/static/js/pm_chart.js`](file:///d:/PyProject/AltDP_3rd/src/web/static/js/pm_chart.js) | [MODIFY] | P-M 상관곡면 및 DCR 차트 반응형 플로팅 고도화 |
| [`src/web/static/js/member_forms.js`](file:///d:/PyProject/AltDP_3rd/src/web/static/js/member_forms.js) | [NEW] | 부재별 파라메트릭 입력 폼 제어 및 Auto-Design 로직 |
| [`tests/api/test_web_routes.py`](file:///d:/PyProject/AltDP_3rd/tests/api/test_web_routes.py) | [MODIFY] | Memb View 및 부재별 파라메트릭 폼 렌더링 검증 |

---

## 4. 구현 및 검증 체크리스트

- [ ] Memb View에서 치수 및 철근 변경 시 2D 배근도와 P-M 차트가 0.05초 이내 즉각 재계산/재렌더링되는지 확인
- [ ] P-Mode (자동배근) 클릭 시 KDS 기준을 만족하는 최적 철근 배근이 자동 도출되는지 검증
- [ ] RC 6대 부재 및 철골 6대 부재의 모든 입력 폼이 오류 없이 로드되고 API와 양방향 통신하는지 확인
- [ ] `pytest tests/api/test_web_routes.py` 100% 통과 (수행시간 < 0.5s)
