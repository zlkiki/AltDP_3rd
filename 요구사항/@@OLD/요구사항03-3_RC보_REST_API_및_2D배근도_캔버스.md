# 요구사항 03-3: RC보 REST API 및 2D 배근도 캔버스 렌더러

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* 완성된 RC 보 강도 및 사용성 해석 엔진을 웹 환경에서 호출할 수 있는 고성능 비동기 REST API를 구축합니다.
* HTML5 Canvas를 활용하여 단면 치수, 1단/2단 주철근, 스터럽, 치수선 및 철근 제원을 직관적이고 미려하게 렌더링하는 2D 배근도 렌더러를 구현합니다.

### 1.2. 참조 Ground Truth 자산
* **UI/UX 명세서**: [`docs/07_web_application_ui_ux_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)
* **기존 API 구조**: [`src/api/routes/rc.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc.py)

---

## 2. 상세 구현 명세

### 2.1. Pydantic API 스키마 및 엔드포인트 (`src/api/`)
* **스키마 정의 (`src/api/schemas/rc_beam.py`)**:
  - `RCBeamCheckRequest`: 단면 크기($b, h$, 피복), 재료($f_{ck}, f_y, f_{yt}$), 배근 정보($A_s, A_s', A_v, s$), 부재력($M_u, V_u, T_u, M_s$)
  - `RCBeamCheckResponse`: 강도/사용성/DCR 결과, 위험도 플래그, 배근 상세 좌표
  - `RCBeamAutoDesignRequest` / `Response`: 단면 및 부재력 입력 시 추천 최적 배근안 반환
* **FastAPI 라우트 (`src/api/routes/rc_beam.py` 또는 `rc.py`)**:
  - `POST /api/v1/rc/beam/check`: 보 단면 검토 및 DCR/처짐/균열 계산
  - `POST /api/v1/rc/beam/auto-design`: 보 자동 최적 배근 도출

### 2.2. HTML5 Canvas 2D 배근도 렌더러 (`src/web/static/js/renderer2d.js`)
* **단면 렌더링 파이프라인**:
  - `drawRCBeamSection(ctx, canvasWidth, canvasHeight, beamData)`
  - 콘크리트 외곽 사각형 및 해칭 렌더링
  - 스터럽 폐합 루프 및 135도 표준 갈고리 형상 렌더링
  - 상부/하부 주철근(1단, 2단) 원형 심볼 및 중심점 정확 배치
  - 상/하/좌/우 치수선 및 철근 태그(예: `3-D22`, `2-D10@200`) 자동 라벨링
  - Canvas 마우스 오버 시 철근 직경/위치/응력 정보 툴팁 표시
* **반응형 뷰포트**: 줌/팬(Zoom/Pan) 및 고해상도(Retina Display) 지원

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/api/schemas/rc_beam.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_beam.py) | [NEW] | RC 보 전용 Pydantic 요청/응답 스키마 |
| [`src/api/routes/rc_beam.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_beam.py) | [NEW] | RC 보 검토 및 자동설계 REST 엔드포인트 |
| [`src/web/static/js/renderer2d.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/renderer2d.js) | [MODIFY] | RC 보 2D 단면 배근도 캔버스 렌더링 함수 구현 |
| [`tests/api/test_rc_beam_api.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_rc_beam_api.py) | [NEW] | RC 보 API 검토 및 자동설계 엔드포인트 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] `/api/v1/rc/beam/check` 및 `/api/v1/rc/beam/auto-design` 엔드포인트 정상 동작 및 유효성 검사
- [x] 2D Canvas 렌더러가 1단/2단 배근 및 스터럽을 정확한 축척으로 렌더링하는지 확인
- [x] DCR 및 배근 정보에 대한 시각적 하이라이트(안전: 녹색, NG: 적색) 동작 확인
- [x] `pytest tests/api/test_rc_beam_api.py` 100% 통과 (수행시간 < 0.5초)
