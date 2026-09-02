# 요구사항 16-3: Gen 연동 REST API 및 다중 부재 일괄 설계 파이프라인 (Phase 16-3)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* MIDAS Gen `.mgt` / `.db` 파일 업로드부터 부재 자동 분류, 지배 하중조건 추출, AltDP 엔진 연동 일괄 단면 검토(Batch Checking), 결과 집계까지의 End-to-End 파이프라인을 구축합니다.
* 비동기 백그라운드 태스크 및 RESTful API를 통해 수백 개 부재의 일괄 설계를 웹 브라우저에서 실시간 프로그레스 바로 모니터링할 수 있도록 지원합니다.

---

## 2. 세부 개발 명세

### 2.1. 다중 부재 일괄 설계 엔진 (`src/engine/project/batch_checker.py`)
* **프로젝트 매니저 연계**:
  - `src/engine/project/project_manager.py`에 Gen 임포트 프로젝트 모델 통합.
* **병렬/비동기 검토 오케스트레이션**:
  - RC 부재: `src/engine/rc/` (`beam.py`, `column.py`, `wall.py`) 순차/병렬 호출.
  - 철골 부재: `src/engine/steel/` (`beam.py`, `column.py`, `brace.py`) 호출.
  - 부재별 최대 $\text{DCR}$ 산정 및 안전율 상태 판정 (Safe, Warning, Danger).
* **처리 성능**: 500개 부재 일괄 검토를 2.0초 이내에 완료.

### 2.2. REST API 엔드포인트 (`src/api/routes/interop.py`)
* `POST /api/v1/interop/mgt/upload` : `.mgt` 파일 multipart 업로드 및 3D 모델 파싱
* `POST /api/v1/interop/mgb/upload` : 해석 DB 파일 업로드 및 부재력 바인딩
* `POST /api/v1/interop/batch-design` : 특정 층 또는 전체 부재 일괄 설계 실행
* `GET /api/v1/interop/batch-status/{task_id}` : 일괄 검토 진행 상태 및 프로그레스(0~100%) 조회
* `GET /api/v1/interop/batch-summary` : 층별/부재별 DCR 결과 요약 테이블 조회

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **E2E 일괄 설계 파이프라인**: 100개 이상의 부재를 포함한 `.mgt` 파일 업로드 시 일괄 설계 및 DCR 산출 100% 성공.
- [ ] **API 응답 및 에러 핸들링**: 비정상 파일 업로드 시 400 Bad Request 및 명확한 에러 메시지 반환.
- [ ] **Pytest 스위트 통과**: `tests/api/test_interop_routes.py`, `tests/engine/test_batch_checker.py` 통과.
