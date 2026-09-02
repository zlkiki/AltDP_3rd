# 요구사항 06-3: 기초/옹벽 REST API 및 단면 시각화

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* 앞선 Phase 06-1과 06-2에서 완성된 RC 기초(독립/복합기초, 지중보) 및 옹벽(캔틸레버/중력식) 설계 엔진을 웹 프론트엔드 및 외부 클라이언트와 연동하기 위한 REST API 엔드포인트와 Pydantic DTO를 구축합니다.
* 또한 지반 접지압 분포 선도, 토압/수압 다이어그램, 기초 및 옹벽 단면 배근 형상을 2D 캔버스에서 실시간 시각화할 수 있는 렌더링 데이터 구조를 제공합니다.

### 1.2. 참조 Ground Truth 자산
* **엔진 소스**: [`src/engine/rc/footing.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rc/footing.py), [`src/engine/rc/retaining_wall.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rc/retaining_wall.py)
* **API 구조**: [`src/api/routes/rc_beam.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_beam.py), [`src/api/routes/rc_column.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_column.py)
* **대상 소스**:
  - [`src/api/schemas/rc_foundation.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_foundation.py)
  - [`src/api/routes/rc_foundation.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_foundation.py)
  - [`src/api/main.py`](file:///f:/PyProject/AltDP_3rd/src/api/main.py)

---

## 2. 세부 API 및 데이터 스키마 명세

### 2.1. Pydantic v2 DTO (`src/api/schemas/rc_foundation.py`)
* `FootingDesignRequest` / `FootingDesignResponse`:
  - 기하치수($B, L, H$), 상부 기둥치수($c_1, c_2$), 하중 조합($P_u, M_{ux}, M_{uy}$), $f_{ck}, f_y$, 지반 허용지지력 $q_a$.
  - 응답: 지반접지압 ($q_{max}, q_{min}$, 편심률), 1방향/2방향 전단강도비, 휨모멘트 및 $X/Y$ 방향 배근 정보, DCR, 2D 시각화 폴리곤/좌표.
* `RetainingWallDesignRequest` / `RetainingWallDesignResponse`:
  - 옹벽 높이, 저판폭(Toe/Heel), 두께, 토사 물성치($\gamma, \phi, c$), 수위, 상재하중.
  - 응답: 토압계수, 3대 안전율($F_{ot}, F_{sl}, q_{max}/q_a$), Stem/Toe/Heel 휨/전단 DCR 및 배근 정보, 토압선도 및 단면 렌더링 데이터.

### 2.2. FastAPI 엔드포인트 (`src/api/routes/rc_foundation.py`)
* `POST /api/v1/rc/footing/design`: 독립/복합 기초 설계 및 접지압/전단/휨 종합 검토
* `POST /api/v1/rc/footing/bearing-pressure`: 편심 하중에 따른 접지압 분포 전용 계산
* `POST /api/v1/rc/retaining-wall/stability`: 옹벽 3대 외적 안정성 검토
* `POST /api/v1/rc/retaining-wall/design`: 옹벽 외적 안정성 + 내적 단면 배근 종합 설계

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/api/schemas/rc_foundation.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_foundation.py) | [NEW] | 기초 및 옹벽 입출력 Pydantic 스키마 정의 |
| [`src/api/routes/rc_foundation.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_foundation.py) | [NEW] | 기초/옹벽 설계 및 안정성 검토 REST API 엔드포인트 구현 |
| [`src/api/main.py`](file:///f:/PyProject/AltDP_3rd/src/api/main.py) | [MODIFY] | `rc_foundation` 라우터 등록 |
| [`tests/api/test_rc_foundation_api.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_rc_foundation_api.py) | [NEW] | 기초/옹벽 API 엔드포인트 호출 및 응답 무결성 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] Pydantic v2 호환 기초 및 옹벽 Request/Response 스키마 정의
- [x] 기초/옹벽 계산 엔진 연동 FastAPI 라우터 구현
- [x] `src/api/server.py`에 라우터 등록 및 Swagger UI(`/docs`) 연동 확인
- [x] 2D 단면 및 압력 다이어그램 시각화 좌표 데이터 생성 로직 검증
- [x] `pytest tests/api/test_rc_foundation_api.py` 100% 통과 검증
