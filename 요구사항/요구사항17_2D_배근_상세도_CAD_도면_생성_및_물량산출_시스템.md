# 요구사항 17: 2D 배근 상세도 CAD 도면 생성 및 물량산출 시스템 (Draw & Qntt View)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+ 원본 4대 메인 폼뷰 중 **도면 생성 뷰(`CMainFormViewDraw`)**와 **물량 산출 뷰(`CMainFormViewQntt`)**는 설계 완료 후 실무 납품을 완성하는 핵심 파이프라인입니다 ([docs/13](file:///d:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md) 참조).

### 1.2. 개발 목적
1. **2D 배근 상세도 CAD (DXF/DWG) 내보내기 엔진 (`src/report/cad_exporter.py`)**:
   - `CMainFormViewDraw`의 CAD 도면화 기능을 순수 Python `ezdxf` 라이브러리로 구축.
   - RC 보/기둥/벽체/기초 단면도, 배근 입면도, 배근 일람표(Schedule Table)를 표준 DXF/DWG CAD 파일로 출력.
   - 표준 레이어(`S-CONC`, `S-REBAR-MAIN`, `S-STIRRUP`, `S-DIM`, `S-TEXT`), 도각(Title Block), 축척(1:20, 1:30) 자동 배치.
2. **KDS 표준 콘크리트/철근/형강 물량산출 엔진 (`src/engine/project/quantity_engine.py`)**:
   - 콘크리트 체적($\text{m}^3$), 거푸집 면적($\text{m}^2$), 철근 규격별(D10~D35) 총 중량(ton, 정착/이음 길이 포함), 강재 중량(ton) 산정.
   - 층별/부재별 물량 집계표 생성 및 MS Excel(`.xlsx`) 다중 시트 내보내기.

---

## 2. 세부 기능 개발 명세

### 2.1. CAD 생성 엔진 (`src/report/cad_exporter.py`)
* `POLYLINE`, `LWPOLYLINE`, `HATCH`, `DIMENSION`, `TEXT` 엔티티 생성.
* AutoCAD R2018 호환 DXF 출력.

### 2.2. 물량 산출 엔진 (`src/engine/project/quantity_engine.py`)
* KDS 14 20 52 정착/이음길이 자동 산정식 연동 철근 톤수 집계.
* 다중 시트 Excel 익스포트.

### 2.3. REST API 엔드포인트
* `POST /api/v1/report/export-dxf` : 단면/입면 배근 상세도 DXF 다운로드
* `POST /api/v1/report/export-schedule-dxf` : 층별 배근 일람표 DXF 다운로드
* `GET /api/v1/project/export-quantity-excel` : 물량 집계표 Excel 다운로드

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] 생성된 `.dxf` 파일이 표준 CAD 프로그램에서 결함 없이 열리고 레이어/치수선 정상 표현.
- [ ] 철근 톤수 및 콘크리트 체적($\text{m}^3$) 산출 오차 0.1% 미만 검증.
- [ ] `tests/report/test_cad_exporter.py`, `tests/engine/test_quantity_engine.py` 통과.
