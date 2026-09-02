# 요구사항 15-3: 전 부재 일괄 바인딩 PDF 생성기 및 다중 시트 Excel API 완성

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+는 단일 부재 계산서 출력 외에 건물 전체의 수십~수백 개 부재를 한 권의 책으로 묶어 인쇄하는 **종합 계산서 일괄 출력(Batch Print)** 및 MS Excel 다중 시트 통합 내보내기 기능을 갖추고 있습니다.
* 표지(Cover Page), 자동 목차(Table of Contents), 일련 페이지 번호(Header/Footer)를 포함하는 일괄 PDF 바인더(`binder.py`)를 구현하고, 다중 시트 Excel 익스포터(`excel_exporter.py`)와 FastAPI 리포트 엔드포인트(`src/api/routes/report.py`)를 완성합니다.

### 1.2. 참조 Ground Truth 자산
* **보고서 역공학 명세 (SSOT)**: [`docs/14_structural_calculation_report_specification.md`](file:///d:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md)
* **디컴파일 심볼**: `decompiled_src/core_routines/` 내 `CMSOffice`, `CMSExcel` 심볼

---

## 2. 상세 구현 명세

### 2.1. 프로젝트 전 부재 일괄 PDF 바인더 (`src/report/binder.py`)
* **표지 및 목차 템플릿 (`cover_and_toc.html`)**:
  - 프로젝트 명, 구조설계사, 설계자, 작성일자, 적용 설계기준(KDS 14 20 00 / 14 31 00) 표기.
  - 부재 유형 및 층별 자동 생성 목차 및 시작 페이지 번호 링크.
* **WeasyPrint / PyPDF 기반 고속 바인딩**:
  - 수십 개 부재의 계산서를 비동기 병렬 렌더링 후 단일 PDF로 결합.
  - 전역 일련 페이지 번호(Page X of Y) 및 헤더/푸터 자동 삽입.

### 2.2. MS Excel 다중 시트 통합 익스포터 고도화 (`src/report/excel_exporter.py`)
* **openpyxl 기반 다중 시트 구조화**:
  - Sheet 1: `Project_Summary` (프로젝트 개요 및 부재별 DCR 요약표).
  - Sheet 2~N: `RC_Beams`, `RC_Columns`, `RC_Walls`, `Steel_Members`, `Connections` 등 부재별 정밀 검토표.
  - KDS 조건부 서식(DCR > 1.0 시 빨간색 강조, DCR < 0.9 시 연녹색) 및 셀 스타일링.

### 2.3. REST API 엔드포인트 완성 (`src/api/routes/report.py`)
* `POST /api/v1/report/generate` : 단일 부재 계산서 (HTML/PDF/Excel) 생성.
* `POST /api/v1/report/batch-generate` : 전 부재 일괄 종합 PDF 바인딩 생성.
* `POST /api/v1/report/export-excel` : 프로젝트 통합 다중 시트 Excel 파일 다운로드.

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/report/binder.py`](file:///d:/PyProject/AltDP_3rd/src/report/binder.py) | [NEW] | 표지/목차/페이지번호 포함 일괄 PDF 바인더 구현 |
| [`src/report/templates/cover_and_toc.html`](file:///d:/PyProject/AltDP_3rd/src/report/templates/cover_and_toc.html) | [NEW] | 종합 계산서 표지 및 자동 목차 템플릿 |
| [`src/report/excel_exporter.py`](file:///d:/PyProject/AltDP_3rd/src/report/excel_exporter.py) | [MODIFY] | 다중 시트 엑셀 워크북 및 조건부 서식 완성 |
| [`src/api/routes/report.py`](file:///d:/PyProject/AltDP_3rd/src/api/routes/report.py) | [MODIFY] | 일괄 PDF 바인딩 및 Excel 내보내기 API 엔드포인트 연동 |
| [`tests/report/test_binder.py`](file:///d:/PyProject/AltDP_3rd/tests/report/test_binder.py) | [NEW] | 일괄 PDF 바인딩 및 목차/페이지 번호 검증 |
| [`tests/api/test_report_routes.py`](file:///d:/PyProject/AltDP_3rd/tests/api/test_report_routes.py) | [MODIFY] | 일괄 바인딩 및 엑셀 다운로드 API 검증 테스트 보강 |

---

## 4. 구현 및 검증 체크리스트

- [ ] 50페이지 이상의 전 부재 종합 계산서가 목차 및 일련 페이지 번호 누락 없이 2초 이내 PDF로 생성되는지 확인
- [ ] 생성된 다중 시트 Excel 파일이 Excel에서 손상 없이 열리고 DCR 조건부 서식이 정상 작동하는지 검증
- [ ] 일괄 PDF 및 Excel 다운로드 API가 올바른 MIME 타입 및 파일 스트림을 반환하는지 확인
- [ ] `pytest tests/report/test_binder.py tests/api/test_report_routes.py` 100% 통과 (수행시간 < 0.8s)
