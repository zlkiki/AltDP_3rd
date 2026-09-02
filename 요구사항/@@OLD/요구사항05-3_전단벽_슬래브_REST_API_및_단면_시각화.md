# 요구사항 05-3: 전단벽/슬래브 REST API 및 단면 시각화

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* 구현된 `RCShearWall` 및 `RCSlabSection`(1방향, 2방향, 펀칭전단) 엔진을 웹 플랫폼 및 프론트엔드 UI와 연동하기 위해 FastAPI REST API 엔드포인트와 단면/배근/위험단면 시각화 렌더링 데이터 생성기를 구축합니다.
* DCR(Demand Capacity Ratio), 안전율, 모멘트 분배도 및 펀칭 위험단면 기하 형상을 JSON 및 SVG 호환 포맷으로 직렬화하여 반환합니다.

### 1.2. 참조 Ground Truth 자산
* **기존 API 패턴**: [`src/api/routes/rc_beam.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_beam.py), [`src/api/routes/rc_column.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_column.py)
* **대상 소스**:
  - [`src/api/schemas/rc_wall.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_wall.py)
  - [`src/api/schemas/rc_slab.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_slab.py)
  - [`src/api/routes/rc_wall_slab.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_wall_slab.py)

---

## 2. 상세 API 명세

### 2.1. 전단벽 검토 API (`POST /api/rc/wall/check`)
* **Request**: 벽체 치수($l_w, t_w, h_w$), 재료 물성치, 단부/복부 배근, 설계 하중 ($P_u, V_u, M_u$), 층간변위비 ($\delta_u / h_w$)
* **Response**: 면내 전단강도 $\phi V_n$, 전단 DCR, 최소 철근비 만족 여부, 특수경계요소 필요 여부, 필요 경계요소 길이 $b_e$, 횡구속 철근 소요량 및 단면 시각화 JSON

### 2.2. 슬래브 휨/모멘트 검토 API (`POST /api/rc/slab/check`)
* **Request**: 슬래브 형식(1방향 / 2방향 DDM), 경간 길이, 두께, 하중($w_u$), 단면 배근
* **Response**: 주열대/중간대 부/정모멘트 설계치, 소요/배근 철근량, 최소 두께 검토 결과, DCR

### 2.3. 펀칭 전단 검토 API (`POST /api/rc/slab/punching`)
* **Request**: 슬래브 두께, 유효깊이 $d$, 기둥 치수($c_1, c_2$), 기둥 위치(내부/변단/모서리), 계수 전단력 $V_u$, 불균형 모멘트 $M_{unb}$
* **Response**: 위험단면 둘레길이 $b_0$, 3대 $V_c$ 산정치 및 최소값, $\gamma_v$, 전단응력 $v_u$, $\phi v_c$, 펀칭 DCR, 위험단면 폴리곤 좌표

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/api/schemas/rc_wall.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_wall.py) | [NEW] | 전단벽 Pydantic 요청/응답 스키마 |
| [`src/api/schemas/rc_slab.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_slab.py) | [NEW] | 슬래브 및 펀칭전단 Pydantic 요청/응답 스키마 |
| [`src/api/routes/rc_wall_slab.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_wall_slab.py) | [NEW] | 전단벽 및 슬래브/펀칭 REST API 라우터 |
| [`src/api/main.py`](file:///f:/PyProject/AltDP_3rd/src/api/main.py) | [MODIFY] | 전단벽/슬래브 라우터 등록 |
| [`tests/api/test_rc_wall_slab_api.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_rc_wall_slab_api.py) | [NEW] | 전단벽 및 슬래브/펀칭 API 통합 엔드투엔드 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] 전단벽 및 슬래브/펀칭 검토 Pydantic 스키마 정의 및 Validation
- [x] `/api/rc/wall/check` 엔드포인트 구현 및 DCR/경계요소 출력 검증
- [x] `/api/rc/slab/check` (또는 `/api/rc/slab/one-way/check`) 엔드포인트 구현 및 DDM 모멘트 분배 출력 검증
- [x] `/api/rc/slab/punching` 엔드포인트 구현 및 펀칭 위험단면 좌표 반환 검증
- [x] `src/api/server.py`에 라우터 등록 및 Swagger UI 확인
- [x] `pytest tests/api/test_rc_wall_slab_api.py` 100% 통과 (수행시간 < 1초)
