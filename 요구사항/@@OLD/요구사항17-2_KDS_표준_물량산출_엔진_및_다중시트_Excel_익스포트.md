# 요구사항 17-2: KDS 표준 물량산출 엔진 및 다중시트 Excel 익스포트 (Phase 17-2)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+ 원본 물량 산출 뷰(`CMainFormViewQntt`)의 물량 집계 알고리즘을 구현하여, 설계된 구조물의 부재별/층별 공사 물량을 정밀 산출합니다.
* KDS 14 20 52(정착 및 이음) 기준을 반영한 철근 규격별 중량(ton), 콘크리트 타설 체적($\text{m}^3$), 거푸집 면적($\text{m}^2$), 구조용 강재 중량(ton)을 집계하고 다중 시트 Excel(`.xlsx`) 파일로 내보냅니다.

---

## 2. 세부 개발 명세

### 2.1. KDS 기반 공종별 물량산출 코어 (`src/engine/project/quantity_engine.py`)
* **1. 콘크리트 물량 ($V_c, \text{m}^3$)**:
  - 기둥/보 접합부 체적 중복 제거 알고리즘.
  - 슬래브 개구부 및 기초 단차 공제.
* **2. 거푸집 면적 ($A_f, \text{m}^2$)**:
  - 보 측면/밑면, 기둥 4면, 벽체 양면, 슬래브 바닥면, 기초 측면 거푸집 면적 자동 전개.
* **3. 철근 물량 ($W_s, \text{kg, ton}$)**:
  - 규격별(D10, D13, D16, D19, D22, D25, D29, D32, D35) 단위중량($\text{kg/m}$) 적용.
  - KDS 14 20 52 인장/압축 정착길이($l_d$) 및 B급 인장 이음길이($1.3 l_d$), 표준 갈고리(Hook) 길이 자동 가산.
  - 철근 할증률(이형철근 3~5%) 옵션 반영.
* **4. 강구조 및 플레이트 중량**:
  - H형강, 각형강관, 플레이트 단위 중량 및 볼트 수량 집계.

### 2.2. 다중 시트 Excel 물량집계표 생성 (`src/report/excel_quantity_exporter.py`)
* `openpyxl`을 활용한 세련된 서식의 보고서 생성:
  - Sheet 1: **총괄 물량 집계표** (공종별/재료별 총 중량 및 체적)
  - Sheet 2: **층별 물량 집계표** (Story별 콘크리트, 거푸집, 철근 분할)
  - Sheet 3: **부재별 상세 내역서** (Member ID별 단면, 길이, 철근 가공조서)

### 2.3. REST API 엔드포인트 (`src/api/routes/quantity.py`)
* `POST /api/v1/project/quantity/calculate` : 프로젝트 전체 물량 산출 JSON 반환
* `GET /api/v1/project/quantity/export-excel` : 다중 시트 `.xlsx` 파일 다운로드
* `POST /api/v1/project/cad/export-dxf` : 단면/일람표 DXF 다운로드

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **물량 산출 정밀도**: 수동 산출 물량 대비 콘크리트 체적, 거푸집 면적, 철근 중량 오차 0.1% 미만.
- [ ] **정착/이음 가산 검증**: KDS 14 20 52 수식에 따른 정착/이음 길이 정상 반영 확인.
- [ ] **단위 테스트 통과**: `tests/engine/test_quantity_engine.py`, `tests/report/test_excel_quantity.py` 통과.
