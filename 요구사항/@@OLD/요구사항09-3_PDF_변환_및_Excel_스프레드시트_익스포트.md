# 요구사항 09-3: PDF 변환 및 Excel 스프레드시트 익스포트

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+의 `CMSExcel` 모듈 기능을 순수 Python의 `openpyxl` 라이브러리로 완전 재구현하여 다중 시트 구조계산서 Excel 스프레드시트 내보내기 엔진(`src/report/excel_exporter.py`)을 구축합니다.
* HTML 계산서를 고해상도 PDF로 렌더링하거나 브라우저 원클릭 인쇄(Window.print)를 지원하는 PDF 익스포트 파이프라인(`src/report/pdf_exporter.py`)을 구현합니다.
* 웹 프론트엔드 및 외부 시스템에서 실시간으로 구조계산서 HTML, PDF, Excel을 호출 및 다운로드할 수 있는 통합 FastAPI REST 엔드포인트(`src/api/routes/report.py`)를 개발하고 `server.py`에 등록합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스**:
  - `decompiled_src/DGN_lib.dll_symbols.txt` (`CMSExcel`)
  - `decompiled_src/DPLUS_RCS.dll_symbols.txt` (`CMSOffice`)
* **대상 소스**:
  - [`src/report/excel_exporter.py`](file:///f:/PyProject/AltDP_3rd/src/report/excel_exporter.py)
  - [`src/report/pdf_exporter.py`](file:///f:/PyProject/AltDP_3rd/src/report/pdf_exporter.py)
  - [`src/api/routes/report.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/report.py)
  - [`src/api/server.py`](file:///f:/PyProject/AltDP_3rd/src/api/server.py)
  - [`tests/report/test_excel_exporter.py`](file:///f:/PyProject/AltDP_3rd/tests/report/test_excel_exporter.py)
  - [`tests/api/test_report_routes.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_report_routes.py)

---

## 2. Excel 및 PDF 출력 사양 및 API 스펙

### 2.1. Excel 워크북 시트 구성 표준 (`CMSExcel` 사양)
1. **Sheet 1: `Overview & Summary`**:
   - 프로젝트 정보, 부재 요약, 전체 검토항목별 DCR 및 최종 판정(OK/NG) 요약표 (조건부 서식 적용).
2. **Sheet 2: `Material & Section`**:
   - 콘크리트, 철근, 강재 물성치 및 단면 기하학적 치수 표.
3. **Sheet 3: `Detailed Design Checks`**:
   - 휨, 전단, 비틀림, 압축, 사용성 등 항목별 소요강도($U$), 설계강도($\phi R_n$), DCR 및 판정식.
4. **Sheet 4: `Load Combinations`**:
   - 검토에 사용된 모든 하중조합별 내력 데이터 테이블.

### 2.2. FastAPI REST 엔드포인트 규격
* `POST /api/v1/report/html`:
  - Request: `MemberReportRequest` (member_type, project_info, design_input, design_result)
  - Response: A4 HTML 계산서 스트링 (`text/html`)
* `POST /api/v1/report/excel`:
  - Request: `MemberReportRequest`
  - Response: `.xlsx` 바이너리 스트림 (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
* `POST /api/v1/report/pdf`:
  - Request: `MemberReportRequest`
  - Response: `.pdf` 바이너리 스트림 또는 인쇄용 HTML 메타 반환 (`application/pdf`)

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/report/excel_exporter.py`](file:///f:/PyProject/AltDP_3rd/src/report/excel_exporter.py) | [NEW] | openpyxl 기반 멀티시트 표준 구조계산서 엑셀 익스포터 |
| [`src/report/pdf_exporter.py`](file:///f:/PyProject/AltDP_3rd/src/report/pdf_exporter.py) | [NEW] | WeasyPrint / Headless Chrome 인쇄 기반 PDF 변환 파이프라인 |
| [`src/api/routes/report.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/report.py) | [NEW] | 구조계산서 HTML/PDF/Excel 생성 및 다운로드 REST 라우터 |
| [`src/api/server.py`](file:///f:/PyProject/AltDP_3rd/src/api/server.py) | [MODIFY] | `report_router` 마운트 및 라우트 등록 |
| [`tests/report/test_excel_exporter.py`](file:///f:/PyProject/AltDP_3rd/tests/report/test_excel_exporter.py) | [NEW] | 엑셀 워크북 생성, 셀 수식 및 서식 검증 테스트 |
| [`tests/api/test_report_routes.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_report_routes.py) | [NEW] | HTML/PDF/Excel API 엔드포인트 200 OK 및 미디어타입 검증 |

---

## 4. 구현 및 검증 체크리스트

- [x] `openpyxl` 기반 `ExcelReportExporter` 클래스 구축 (스타일, 폰트, 테두리, 배경색, 열 너비 자동 조정)
- [x] RC 보/기둥/벽체/슬래브/기초 및 철골 부재 Excel 덤프 로직 구현
- [x] `PDFReportExporter` PDF 변환기 구현 (WeasyPrint 또는 HTML 인쇄 폴백 메커니즘)
- [x] `src/api/routes/report.py` 라우터 구현 및 `src/api/server.py`에 등록
- [x] `pytest tests/report/test_excel_exporter.py` 100% 통과
- [x] `pytest tests/api/test_report_routes.py` 100% 통과
- [x] `pytest` 전체 통합 테스트 회귀 검증 100% 통과 (오차 0.1% 미만)
