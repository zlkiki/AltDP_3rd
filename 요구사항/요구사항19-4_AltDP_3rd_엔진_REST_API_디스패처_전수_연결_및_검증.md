# [요구사항19-4] AltDP_3rd 엔진 REST API 디스패처 전수 연결 및 검증

## 1. 개요 및 목적
* AltDP_2nd 프론트엔드의 단일화된 계산 디스패처 `POST /api/design/{category}/{group}/{module_id}`를 AltDP_3rd에 구축된 고정밀 Python 엔지니어링 엔진군에 1:1 완전 연결합니다.
* **소스 직접 재활용 & 토큰 효율성 원칙**: AltDP_2nd의 백엔드 동적 디스패치 및 스키마 직렬화 메커니즘(`app/main.py`, `app/engines/` registry)을 직접 재활용하여 신규 코드 작성량을 최소화하고, AltDP_3rd의 검증된 고정밀 엔진(`src/engine/rc/`, `steel/` 등)과의 0.1% 오차 무결성 바인딩에 집중합니다.
* 54종 모듈의 입력 DTO를 AltDP_3rd의 엔진 파라미터로 매핑하고, KDS 계산 결과 및 DCR 데이터를 프론트엔드가 요구하는 포맷으로 표준화하여 응답합니다.

---

## 2. 세부 개발 작업 명세

### 2.1. 동적 계산 디스패처 라우트 구축 (`src/api/routes/dispatch.py`)
* 엔드포인트: `POST /api/design/{category}/{group}/{module_id}`
* 역할:
  - 수신된 JSON payload를 해당 도메인 모듈에 전달.
  - 카테고리(`rc`, `steel`, `pc`, `misc`) 및 하위 그룹(`beam`, `column`, `footing`, `slab`, `wall`, `member`, `connection` 등)별로 AltDP_3rd의 검증된 엔진 호출.

### 2.2. 도메인별 엔진 직결 매핑
1. **RC 콘크리트 (`rc/`)**:
   - `rc/beam/*` ➔ `src/engine/rc/beam.py` (직사각형, T형보, 처짐, 개구부, 내력표)
   - `rc/column/*` ➔ `src/engine/rc/column.py` & `src/engine/solver/pm_diagram.py` (기둥, 상세배근, P-M 곡면)
   - `rc/footing/*` ➔ `src/engine/rc/footing.py` (독립기초, 복합기초, 말뚝기초)
   - `rc/slab/*` ➔ `src/engine/rc/slab.py` (1방향/2방향 슬래브, 펀칭전단)
   - `rc/wall/*` ➔ `src/engine/rc/wall.py` & `src/engine/rc/retaining_wall.py` (전단벽, 옹벽, 지하외벽)
2. **Steel 강구조 (`steel/`)**:
   - `steel/member/*` ➔ `src/engine/steel/beam.py`, `column.py`, `brace.py` (H형강/강관 보, 기둥 좌굴, 가새)
   - `steel/connection/*` ➔ `src/engine/steel/connection.py`, `baseplate.py`, `endplate.py` (볼트, 용접, 주각부 베이스플레이트, 엔드플레이트)
   - `steel/composite/*` ➔ `src/engine/steel/web_opening.py`, `src/engine/src_composite/` (개구부 보강, 합성보)
3. **PC / Misc (`pc/`, `misc/`)**:
   - `misc/src/*` ➔ `src/engine/src_composite/` (CFT 기둥, SRC 합성보)
   - `misc/special/*` ➔ `src/engine/alu/`, `src/engine/rfm/` (알루미늄, CFRP/강판 보수보강)
   - `pc/*` ➔ 표준 PC/PSC 계산 루틴 연계

### 2.3. 응답 데이터 표준화 (Standard Result Schema)
* 백엔드 반환 JSON 구조:
  ```json
  {
    "success": true,
    "key": "rc/beam/base",
    "result": {
      "dcr": 0.654,
      "governing_dcr": 0.654,
      "verdict": "OK",
      "phiMn": 382.5,
      "phiVn": 184.2,
      "summary": { ... },
      "checks": [ ... ],
      "sections": [ ... ]
    }
  }
  ```

---

## 3. 체크리스트 및 완료 검증
- [ ] `POST /api/design/rc/beam/base` 호출 시 AltDP_3rd의 RC 보 계산 엔진이 호출되어 올바른 결과가 반환되는가?
- [ ] `POST /api/design/rc/column/base` 호출 시 3D P-M 상관도 및 DCR이 정확히 산출되는가?
- [ ] `POST /api/design/steel/member/beam` 호출 시 H형강 휨/전단/조밀성 검토 결과가 반환되는가?
- [ ] `POST /api/design/steel/connection/baseplate` 호출 시 베이스플레이트 및 앵커볼트 내력이 반환되는가?
- [ ] 프론트엔드 [⚡ 검토] 버튼 클릭 시 에러 없이 KDS 계산서가 즉각 표출되는가?
- [ ] 디스패처 단위 테스트(`tests/api/test_dispatch_api.py`) 작성 및 100% 통과.
