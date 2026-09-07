# 요구사항 20-2: Phase 20-2 Midas 54종 3단계 티어 메타 전수 주입 및 카탈로그 고도화 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서(SSOT)**:
  - [`요구사항 20 (Phase 20 마스터)`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md) 제4절 및 제5절
  - [`docs/01_system_architecture.md`](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md) (단면 DB 및 부재 카탈로그 구조)
  - [`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md) (Phase 1~6 기완료 부재 현황)
  - [`docs/13_midas_design_plus_original_ui_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md) (`Menu.ini` 6대 탭 및 `DLG_*.ini` 리소스)
* **목적**: Midas Design+ 원본 6대 대분류에 기반한 **54종 전체 설계/검토 모듈 카탈로그에 3단계 티어(Tier 1: 10종 핵심, Tier 2: 18종 주요, Tier 3: 26종 특수), KDS 표준 코드 및 Midas 원본 DLG 심볼을 전수 주입**하고, `docs/12` 기완료 엔진 현황(`engine_status: VERIFIED/WIP`)을 일치시켜 단일 진실 공급원(SSOT) 카탈로그를 완성합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. 54종 카탈로그 메타데이터 스키마 확장
* **구현 파일**: `app/engines/__init__.py`, `src/web/static/js/catalog.js`, `src/api/routes/schema.py`
* **메타데이터 필수 필드 규격**:
  - `key`: 부재 식별 유니크 키 (예: `rc/beam/rc_beam`)
  - `name`: Midas 한국어 공식 명칭 (예: `보 (RC Beam)`)
  - `midas_dlg`: Midas 원본 리소스 심볼 (예: `IDD_RCS_BEAM_PMODE_DLG`)
  - `category`: 대분류 (`rc`, `steel`, `src`, `alu`, `rfm`, `fem`)
  - `tier`: 우선순위 등급 (`Tier 1`, `Tier 2`, `Tier 3`)
  - `standard`: 관련 KDS 국가건설기준 (예: `KDS 14 20 00 : 2022`)
  - `engine_status`: KDS 엔진 상태 (`VERIFIED` 기완료 / `WIP` 연동준비중)

### 2.2. Midas 54종 3단계 티어 및 Midas 원본 DLG 1:1 매핑 목록
1. **Tier 1 (10종 최우선 핵심 부재)**:
   - `rc/beam/rc_beam`: RC 보 (`IDD_RCS_BEAM_PMODE_DLG`, KDS 14 20 20)
   - `rc/column/rc_column`: RC 기둥 (`IDD_RCS_COLUMN_PMODE_DLG`, KDS 14 20 20)
   - `rc/wall/rc_wall`: RC 전단벽 (`IDD_RCS_WALL_PMODE_DLG`, KDS 14 20 22)
   - `rc/footing/rc_footing_iso`: RC 독립기초 (`IDD_RCS_FOOT_PMODE_DLG`, KDS 14 20 70)
   - `rc/retaining_wall/rc_retaining_wall`: RC 옹벽 (`IDD_RCS_RETAINING_WALL_INPUT_DLG`, KDS 14 20 70)
   - `steel/beam/steel_beam`: 철골 보 (`IDD_STL_BEAMCOLUMN_INPUT_DLG`, KDS 14 31 10)
   - `steel/column/steel_column`: 철골 기둥 (`IDD_STL_BEAMCOLUMN_INPUT_DLG`, KDS 14 31 10)
   - `steel/brace/steel_brace`: 철골 가새 (`IDD_STL_BRACE_INPUT_DLG`, KDS 14 31 15)
   - `steel/baseplate/steel_baseplate`: 주각부 베이스플레이트 (`IDD_STL_BASEPLATE_DLG`, KDS 14 31 25)
   - `steel/connection/steel_connection`: 보-기둥 접합부 (`IDD_STL_CONN_BEAMCOL_DLG`, KDS 14 31 25)
2. **Tier 2 (18종 실무 주요 및 기초/합성/FEM 부재)**:
   - 슬래브(`IDD_RCS_SLAB_PMODE_DLG`), 지하외벽(`IDD_RCS_BASEMENT_WALL_DLG`), 복합/말뚝/매트기초, 이형기둥/벽체, 엔드플레이트, 개구부보, 크레인거더, 트러스, SRC 3종, 알루미늄 2종, 보수보강 2종
3. **Tier 3 (26종 특수/상세/인터페이스 모듈)**:
   - 앵커볼트 상세, 특수접합, 단면기하성질 산정(SDB), 하중생성기, MIDAS Gen 인터페이스 등 26종

### 2.3. 티어별 통계 API 엔드포인트
* `GET /api/modules`: 54종 전체 카탈로그 및 `summary: { total: 54, tier1: 10, tier2: 18, tier3: 26, verified: X, wip: Y }` 통계 제공.

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)

1. **Step 1 [High]**: `docs/13` 기반 54종 전수 인벤토리와 Midas DLG 심볼 1:1 매핑 딕셔너리 구축.
2. **Step 2 [Medium]**: `app/engines/__init__.py` 및 `src/api/routes/schema.py` 메타데이터 파이프라인 확장.
3. **Step 3 [Medium]**: 프론트엔드 `catalog.js`에 백엔드 티어 및 Midas DLG 메타데이터 동기화.
4. **Step 4 [Medium]**: `GET /api/modules` 엔드포인트에 3단계 티어 및 검증 상태 집계 로직 탑재.
5. **Step 5 [High]**: `tests/api/test_catalog_tiers.py` 작성 및 54종 전수 주입 무결성 검증 (오차 0건, 100% PASS).

---

## 4. 완료 검증 기준 (Acceptance Criteria)
* `/api/modules` 응답의 54종 모든 부재 객체에 `tier`, `standard`, `midas_dlg`, `engine_status`가 100% 누락 없이 존재할 것.
* Tier 1(10종), Tier 2(18종), Tier 3(26종)의 합이 정확히 54종으로 일치할 것.
* `pytest tests/api/test_catalog_tiers.py` 통과 (Exit Code 0).
