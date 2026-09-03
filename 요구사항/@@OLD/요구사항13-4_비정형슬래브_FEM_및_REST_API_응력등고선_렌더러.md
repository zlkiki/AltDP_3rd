# 요구사항 13-4: 비정형 슬래브 FEM 및 REST API 응력 등고선 렌더러

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+의 슬래브 모듈(`CHK_URSL`, `CHK_SLAB`)은 직접설계법(DDM)이나 등가골조법(EFM)을 적용하기 어려운 불규칙 기둥 배치, 대형 개구부, 편심 코너 슬래브에 대해 2D 평판 FEM을 통해 휨모멘트 및 펀칭 전단을 산정합니다.
* 비정형 슬래브 2D FEM 해석 모듈을 완성하고, 5대 FEM 해석을 호출하는 FastAPI REST API 라우트(`src/api/routes/fem.py`)와 웹 브라우저 Canvas 2D 실시간 응력 등고선(Stress Contour) 렌더러(`stress_contour.js`)를 구축합니다.

### 1.2. 참조 Ground Truth 자산
* **바이너리 & 외부 솔버**: `original_src/Midas Design+/DgnSolver/FES.EXE`
* **기술 명세서 (SSOT)**: [`docs/15_fem_analysis_and_external_solver_specification.md`](file:///d:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md), [`docs/07_web_application_ui_ux_specification.md`](file:///d:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)
* **심볼 레퍼런스**: `decompiled_src/DPLUS_RCS.dll_symbols.txt` (`CHK_URSL`)

---

## 2. 상세 구현 명세

### 2.1. 비정형/개구부 슬래브 2D FEM 해석기 (`src/engine/fem/slab_fem.py`)
* **비정형 슬래브 형상 및 개구부 모델링**:
  - 임의 다각형 외곽선 및 내부 다중 개구부(Opening)에 대한 DKMQ/DKT 혼합 자동 메시 생성.
  - 기둥 지지점(점지지/탄성 회전스프링) 및 벽체 지지선(선지지) 경계조건 부여.
* **휨모멘트 적분 및 펀칭 전단 집중 해석**:
  - 요소 단위폭당 설계 휨모멘트($M_x, M_y, M_{xy}$)의 Wood-Armer 수식을 통한 설계 모멘트($M_{ux}^*, M_{uy}^*$) 산정.
  - 기둥 헤드 주변 $d/2$ 이격 위험단면 전단응력 적분을 통한 펀칭 전단비 검토.

### 2.2. FEM REST API 라우트 (`src/api/routes/fem.py`)
* `POST /api/v1/fem/foundation/solve` : 매트/복합기초 비선형 지반 해석
* `POST /api/v1/fem/wall-2way/solve` : 지하외벽 2방향 판 휨 FEM 해석
* `POST /api/v1/fem/baseplate/solve` : 주각부 베이스플레이트 비선형 접촉 해석
* `POST /api/v1/fem/endplate/solve` : 모멘트 엔드플레이트 항복선 FEM 해석
* `POST /api/v1/fem/slab/solve` : 비정형 슬래브 2D FEM 해석

### 2.3. Web Canvas 2D 실시간 응력 등고선 렌더러 (`src/web/static/js/stress_contour.js`)
* **Rainbow / Jet 컬러 맵 등고선 렌더링**:
  - 절점/요소 변위($w$), 휨모멘트($M_{xx}, M_{yy}$), 접지압($q$) 값의 수치 보간 및 Canvas 2D 그라데이션 채색.
  - 컬러 바(Legend Bar, Min/Max 값), 메쉬 와이어프레임(Wireframe) 토글, 마우스 호버 시 해당 절점 수치 툴팁 표시.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/fem/slab_fem.py`](file:///d:/PyProject/AltDP_3rd/src/engine/fem/slab_fem.py) | [NEW] | 비정형/개구부 슬래브 2D FEM 해석 엔진 구현 |
| [`src/api/routes/fem.py`](file:///d:/PyProject/AltDP_3rd/src/api/routes/fem.py) | [NEW] | 5대 부재 FEM 해석 통합 REST API 엔드포인트 구현 |
| [`src/api/main.py`](file:///d:/PyProject/AltDP_3rd/src/api/main.py) | [MODIFY] | FEM 라우트 등록 |
| [`src/web/static/js/stress_contour.js`](file:///d:/PyProject/AltDP_3rd/src/web/static/js/stress_contour.js) | [NEW] | Canvas 2D 실시간 컬러 등고선 및 범례 렌더러 구현 |
| [`tests/engine/test_fem_slab.py`](file:///d:/PyProject/AltDP_3rd/tests/engine/test_fem_slab.py) | [NEW] | 개구부 슬래브 휨 및 펀칭 전단 FEM 해석 검증 |
| [`tests/api/test_fem_api.py`](file:///d:/PyProject/AltDP_3rd/tests/api/test_fem_api.py) | [NEW] | 5대 FEM API 엔드포인트 입출력 검증 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] 개구부 포함 비정형 슬래브의 FEM 해석이 0.05초 이내 완료되고 Wood-Armer 설계 모멘트가 정확히 계산되는지 확인
- [x] 5대 FEM API 엔드포인트가 비동기/동기 요청에 대해 200 OK와 정밀한 JSON 결과를 반환하는지 검증
- [x] Canvas 응력 등고선 렌더러가 0.02초 이내에 매끄러운 컬러 맵을 웹 화면에 그리는지 검증
- [x] `pytest tests/engine/test_fem_slab.py tests/api/test_fem_api.py` 100% 통과 (수행시간 < 0.8s)
