# 요구사항 14-3: 다중 부재 List View, 도면 Draw View, 물량 Qntt View 완성

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+는 단일 부재 설계 외에 건물 전체의 수백 개 부재를 한눈에 관리하는 **3대 종합 관리 폼뷰**(`CMainFormViewList`, `CMainFormViewDraw`, `CMainFormViewQntt`)를 제공합니다.
* 다중 부재 일괄 스프레드시트 검토 뷰(List View), 2D 배근 상세도 및 일람표 CAD 뷰어(Draw View), 그리고 콘크리트/거푸집/철근/형강 자동 물량 산출 대시보드(Qntt View)를 완성하여 상용 엔지니어링 프로그램 수준의 통합 웹 UI/UX를 달성합니다.

### 1.2. 참조 Ground Truth 자산
* **UI 역공학 명세 (SSOT)**: [`docs/13_midas_design_plus_original_ui_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md)
* **디컴파일 심볼**: `decompiled_src/DPLUS_VDraw.dll_symbols.txt` (`CMainFormViewList`, `CMainFormViewDraw`, `CMainFormViewQntt`)

---

## 2. 상세 구현 명세

### 2.1. 다중 부재 목록 및 일괄 검토 뷰 (`src/web/templates/view_list.html`, `batch_grid.js`)
* **좌측 계층 트리 네비게이터**:
  - 프로젝트 $\rightarrow$ 층(Story: 1F, 2F, B1) $\rightarrow$ 부재 유형(Beam, Column, Wall, Footing) 계층 구조 탐색.
* **우측 다중 부재 스프레드시트 그리드 (`batch_grid.js`)**:
  - 다중 부재의 제원, 하중, 철근 배근을 엑셀처럼 직접 편집 및 일괄 복사/붙여넣기.
  - 'Run All Batch' 버튼 클릭 시 전체 부재 KDS 일괄 검토 수행 $\rightarrow$ DCR 기준 컬러 히트맵(녹색 $\le 0.9$, 황색 $\le 1.0$, 적색 $> 1.0$) 표시.

### 2.2. 2D 배근 상세도 및 일람표 CAD 뷰어 (`src/web/templates/view_draw.html`, `draw_cad.js`)
* **구조 도면 및 배근 일람표 생성**:
  - RC 보 단면/종단면 상세도, 기둥 단면/입면 상세도, 슬래브/벽체 배근도 벡터 드로잉.
  - 표준 부재 일람표(Schedule Table) 생성.
  - SVG 및 DXF 다운로드 기능 지원.

### 2.3. 물량 산출 대시보드 (`src/web/templates/view_qntt.html`, `qntt_summary.js`)
* **재료별 물량 자동 적산 및 시각화**:
  - 콘크리트 체적($\text{m}^3$), 거푸집 면적($\text{m}^2$).
  - 철근 규격별(D10, D13, D16, D19, D22, D25, D29, D32) 길이(m) 및 중량(ton) 자동 집계.
  - 강재(H형강, 각형강관, 플레이트) 중량(ton) 및 볼트/용접 물량 집계.
  - Chart.js 기반 층별/부재별 물량 도넛 차트 및 Excel(`.xlsx`) 내보내기.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/web/templates/view_list.html`](file:///f:/PyProject/AltDP_3rd/src/web/templates/view_list.html) | [NEW] | 다중 부재 계층 트리 및 스프레드시트 일괄 검토 템플릿 |
| [`src/web/templates/view_draw.html`](file:///f:/PyProject/AltDP_3rd/src/web/templates/view_draw.html) | [NEW] | 2D 배근 상세도 및 일람표 CAD 도면 뷰어 템플릿 |
| [`src/web/templates/view_qntt.html`](file:///f:/PyProject/AltDP_3rd/src/web/templates/view_qntt.html) | [NEW] | 콘크리트/철근/형강 물량 산출 대시보드 템플릿 |
| [`src/web/static/js/batch_grid.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/batch_grid.js) | [NEW] | 다중 부재 고속 그리드 편집기 및 일괄 검토 클라이언트 |
| [`src/web/static/js/draw_cad.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/draw_cad.js) | [NEW] | 2D 구조 도면 및 배근 일람표 벡터 렌더러 |
| [`src/web/static/js/qntt_summary.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/qntt_summary.js) | [NEW] | 물량 자동 적산 엔진 및 통계 대시보드 스크립트 |
| [`tests/api/test_web_routes.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_web_routes.py) | [MODIFY] | 4대 폼뷰 전체 엔드포인트 무결성 검증 테스트 추가 |

---

## 4. 구현 및 검증 체크리스트

- [ ] List View에서 50개 부재 일괄 검토 시 0.5초 이내 DCR 히트맵이 정상 렌더링되는지 확인
- [ ] Draw View에서 보/기둥 단면 상세도 및 배근 일람표가 깨짐 없이 미려하게 렌더링되는지 검증
- [ ] Qntt View에서 부재 제원 변경 시 콘크리트/철근 물량이 0.01% 오차 없이 실시간 재집계되는지 확인
- [ ] `pytest tests/api/test_web_routes.py` 100% 통과 (수행시간 < 0.5s)
