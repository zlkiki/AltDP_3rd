# 요구사항 27-3: Phase 27-3 프론트엔드 UI, 스크립트 및 소스 주석 고유명사 전면 소거 명세서

## 1. 개요 및 목적

본 문서는 웹 프론트엔드 UI 템플릿, 클라이언트 자바스크립트, 스타일시트, 엑셀 출력 엔진 및 개발 스크립트에 잔존하는 타사 고유명사(`Design+`, `MIDAS Gen`, `re-DCR` 등)와 '원본' 관련 표현을 일체 소거하고, 자체 순수 소프트웨어(AltDP) 표준 명칭 체계로 완전히 전환하기 위한 상세 명세서입니다.

* **담당 소스 파일**:
  - `src/web/templates/index.html`
  - `src/web/static/js/app.js`
  - `src/web/static/js/core/report_renderer.js`
  - `src/web/static/js/core/modal_manager.js`
  - `src/web/static/js/core/common_dialogs.js`
  - `src/web/static/js/core/tree_menu.js`
  - `src/web/static/js/report/redcr/*.js`
  - `src/web/static/css/views.css`, `ribbon.css`, `modal.css`
  - `src/report/excel_exporter.py`
  - `src/engine/solver/fiber_section.py`
  - `scripts/scan_midas_modules.py` $\rightarrow$ `scripts/scan_modules.py`

---

## 2. 세부 구현 요구사항

### 2.1. 웹 UI 및 프론트엔드 버튼/메시지 정제
1. **`src/web/templates/index.html`**:
   - `id="btn-import-gen"`의 title 및 표시 텍스트 수정:
     - 기존: `title="MIDAS Gen .mgt 모델 임포트">🏗️ Gen</button>`
     - 변경: `title="3D 골조 .mgt 모델 임포트">🏗️ 3D MGT</button>`
2. **`src/web/static/js/app.js`**:
   - 주석: `// 4. MIDAS Gen .mgt Import Button` $\rightarrow$ `// 4. 3D Frame .mgt Import Button`
   - 임포트 완료 알림 메시지:
     - 기존: `alert('MIDAS Gen 모델 임포트 완료!...')`
     - 변경: `alert('3D 골조 모델 임포트 완료!...')`

### 2.2. 프론트엔드 핵심 코어 스크립트 주석 정제
1. **`src/web/static/js/core/report_renderer.js`**:
   - `Conforms to Midas Design+ DgnReportBase.ini / GENDgnReportKR.ini specification`
     $\rightarrow$ `Conforms to KDS Standard 5-Section Structural Calculation Report Specification`
2. **`src/web/static/js/core/modal_manager.js`**:
   - `Manages modal lifecycles for Midas Design+ sub-dialogs`
     $\rightarrow$ `Manages modal lifecycles for Parametric Engineering Sub-Dialogs`
3. **`src/web/static/js/core/common_dialogs.js`**:
   - `Implements Midas Design+ sub-dialog templates`
     $\rightarrow$ `Implements Parametric Engineering Sub-Dialog Templates`
4. **`src/web/static/js/core/tree_menu.js`**:
   - `// 원본 6대 탭 및 모듈 순서 완벽 고정`
     $\rightarrow$ `// KDS 6대 탭 및 표준 모듈 카테고리 순서 고정`

### 2.3. 계산서 렌더러 및 스타일시트 정제
1. **`src/web/static/js/report/redcr/*.js`**:
   - `SteelReportGenerator.js`: `MIDAS Gen style steel detailed calculation report...` $\rightarrow$ `KDS 14 31 10 : 2024 (LRFD) Steel Detailed Calculation Report`
   - `SlabReportGenerator.js`: `MIDAS Gen / KDS 스타일` $\rightarrow$ `KDS 14 20 00 콘크리트 슬래브 표준 계산서`
   - `FootingReportGenerator.js`: `MIDAS Gen / KDS 스타일` $\rightarrow$ `KDS 14 20 00 독립기초/복합기초/말뚝기초 표준 계산서`
   - `redcr_common_renderer.js`: `(MIDAS Gen / re-DCR 일치 포맷)` $\rightarrow$ `(KDS A4 표준 공학 포맷)`
2. **`src/web/static/css/*.css`**:
   - `views.css`: `Re-engineered from Midas Design+ CMainFormView...` $\rightarrow$ `4-Pane Engineering Workspace Views`
   - `ribbon.css`: `Re-engineered from Midas Design+ Ribbon Interface` $\rightarrow$ `Top Global Engineering Ribbon Interface`
   - `modal.css`: `/* modal.css - AltDP 3열 서브탭 폼 및 원본 서브 대화창(ModalManager)... */` $\rightarrow$ `/* modal.css - AltDP 3열 서브탭 폼 및 서브 대화창(ModalManager)... */`

### 2.4. 백엔드 엔진 주석 및 파일명 변경
1. **`src/report/excel_exporter.py`**:
   - `Adheres to Midas Design+ CMSExcel format.` $\rightarrow$ `Adheres to Multi-Tab Engineering Spreadsheet Format.`
2. **`src/engine/solver/fiber_section.py`**:
   - `and reverse engineered Midas Design+ solver logic.` $\rightarrow$ `and fiber discretization numerical integration.`
3. **`scripts/` 파일명 및 내부 문자열 변경**:
   - `scripts/scan_midas_modules.py` $\rightarrow$ `scripts/scan_modules.py` (파일명 변경)
   - 스크립트 내부 주석 및 콘솔 출력 메시지에서 `MIDAS` 단어 정리.

---

## 3. 검증 및 완료 기준 (Definition of Done)

1. `src/web/` 및 `src/report/` 내 모든 파일에서 타사 고유명사 및 '원본' 주석 소거 완료.
2. `scripts/scan_modules.py` 파일명 변경 및 정상 실행 확인.
3. 브라우저에서 메인 화면 로딩 및 3D MGT 임포트 버튼 툴팁 정상 확인.
