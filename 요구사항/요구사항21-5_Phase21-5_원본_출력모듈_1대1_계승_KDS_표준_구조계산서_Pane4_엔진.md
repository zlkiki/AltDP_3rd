# 요구사항 21-5: Phase 21-5 원본 출력모듈 1:1 계승 KDS 표준 구조계산서 Pane 4 엔진 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서 (SSOT)**:
  - [`요구사항 21 (마스터)`](요구사항21_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md) 제5절
  - [`docs/07_web_application_ui_ux_specification.md`](../docs/07_web_application_ui_ux_specification.md) 제4.4절
  - [`docs/14_structural_calculation_report_specification.md`](../docs/14_structural_calculation_report_specification.md) (KDS 8단계 수식 유도식 명세)
  - 원본앱 출력 모듈: `IDD_DGN_CHECK_MODE_DLG`, `DgnReportBase.ini`, `GENDgnReportKR.ini`
* **목적**: 인허가 관공서 및 구조심의 제출용 초정밀 공학 계산서를 위해, **상시 순백색 A4 용지 원칙, 상세/요약 2대 모드 분기, 입력 데이터 상세 포함 토글, 머릿말/회사명 설정 모달, KaTeX 8단계 수식 유도식 및 원본앱 고유의 O.K/N.G 판정 표기**를 제공하는 KDS 표준 구조계산서 엔진(`report_engine.js`)을 구축합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. 계산서 상단 제어 툴바 (Report Control Toolbar)
* **대상 파일**: `src/web/static/js/core/report_engine.js`, `src/web/static/css/report.css`
* **툴바 UI 구조**:
  ```html
  <div id="report-control-toolbar" class="report-toolbar">
    <!-- 1. 보고서 유형 분기 -->
    <div class="toolbar-group">
      <span class="group-label">유형:</span>
      <label class="radio-label">
        <input type="radio" name="report-mode" value="detail" checked> 상세 보고서 (Detail)
      </label>
      <label class="radio-label">
        <input type="radio" name="report-mode" value="summary"> 요약 보고서 (Summary)
      </label>
    </div>

    <!-- 2. 출력 옵션 체크박스 -->
    <div class="toolbar-group">
      <label class="checkbox-label" title="설계자가 입력한 재료/배근/하중 제원 상세 표 수록 여부">
        <input type="checkbox" id="chk-report-include-input" checked> 사용자 입력 데이터 상세 포함
      </label>
      <label class="checkbox-label" title="2D 단면도 및 P-M 곡선 이미지 삽입">
        <input type="checkbox" id="chk-report-include-graphics" checked> 그래픽 임베딩
      </label>
    </div>

    <!-- 3. 커스텀 설정 및 출력 액션 -->
    <div class="toolbar-actions">
      <button id="btn-report-header-settings" class="btn-tool" title="머릿말/회사명/서명란 설정">⚙️ 머릿말 설정</button>
      <button id="btn-report-print" class="btn-primary-sm" title="브라우저 인쇄">🖨️ 인쇄</button>
      <button id="btn-report-pdf" class="btn-tool" title="WeasyPrint 고화질 PDF 다운로드">📄 PDF</button>
      <button id="btn-report-excel" class="btn-tool" title="OpenPyXL 엑셀 내보내기">📊 Excel</button>
    </div>
  </div>
  ```

### 2.2. 상시 순백색(`#ffffff`) A4 고정 용지 원칙
* **대상 파일**: `src/web/static/css/report.css`, `src/web/static/css/print.css`
* **규격 및 스타일**:
  - 메인 UI 테마(다크 모드 등)와 완전히 독립된 **순백색(`#ffffff`) 배경과 고대비 텍스트(`#111827`)** 고정.
  - 컨테이너 폭: 고정 794px(210mm 대응), 20mm 패딩, 은은한 그림자(`box-shadow`).
  - `@media print` 스타일: 그림자 제거, 100% 여백 일치, 불필요한 툴바/사이드바 자동 숨김.

### 2.3. 2대 보고서 모드 및 옵션별 동적 렌더링
1. **[요약 보고서 (Summary Report)]**:
   - 1~2페이지 A4 압축 레이아웃.
   - 핵심 설계조건, 재료 제원, 2D 단면도, 지배 LCB 및 종합 DCR 안전성 검토표.
2. **[상세 보고서 (Detail Report)] - (초정밀 공학 계산서)**:
   - 인허가 관공서 및 구조심의 제출용 정밀 공학 계산서.
   - KDS 14 20 00 / 14 31 00 기준 조항 번호 1:1 명기.
   - **KaTeX 8단계 수식 유도식**:
     * 공식 기호 $\rightarrow$ 수치 대입 $\rightarrow$ 중간 계산값($a, c, \epsilon_t, \phi, V_c, V_s$ 등) $\rightarrow$ 최종 설계강도 및 DCR 도출.
   - 전체 하중조합 케이스별 내력비 전수 테이블 수록.
3. **사용자 입력 데이터 포함/불포함 옵션 (`chk-report-include-input`)**:
   - `[☑ 체크 ON]` (기본값): 계산서 제2장에 **[사용자 입력 데이터 상세]** 섹션을 완전 수록(재료, 경간, 치수, 배근, 하중 전수 표기)하여 역추적성 보장.
   - `[☐ 체크 OFF]`: 제2장을 생략하고 곧바로 제3장 [단면 특성치] 및 제5장 [KDS 수식 계산]으로 직행하여 장수 슬림화.

### 2.4. 머릿말(Header) & 꼬릿말(Footer) 커스텀 모달
* 모달 팝업(`IDD_REPORT_HEADER_DLG`)을 통해 프로젝트명, 회사명(정식/약칭), 부재 태그, 검토자/승인자 서명란, 날짜, 회사 로고를 입력받아 계산서 상단에 실시간 인쇄 배너로 렌더링.

### 2.5. 원본 5대 장구분 구조 및 O.K / N.G 판정 표기
* **1장: 일반 설계 조건** (적용 기준, 단위계, 부재 개요)
* **2장: 사용자 입력 데이터** (*옵션 체크 시*)
* **3장: 재질 및 단면** (2D 단면 SVG 그래픽 임베딩)
* **4장: 설계 하중** (하중 조합표 및 지배 LCB)
* **5장: 단면 정밀 안전성 검토** (KaTeX 8단계 수식 전개식)
* **6장: 종합 판정 (Summary & Verdict)**:
  - 원본 원본앱 고유의 판정 표기 완벽 재현:
    * `  →  O.K` 🟢 (DCR $\le 1.0$)
    * `  →  N.G` 🔴 (DCR $> 1.0$)

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)
* **Step 1: 계산서 상단 툴바 및 순백색 A4 컨테이너 CSS 확립**
  - `report.css`, `print.css` 상시 순백색 및 인쇄 미디어 쿼리 구축.
* **Step 2: 2대 보고서 모드(상세/요약) 및 입력데이터 토글 로직 구현**
  - `report_engine.js` 라디오/체크박스 상태에 따른 섹션 가시성 제어기 구현.
* **Step 3: KaTeX 8단계 수식 유도 템플릿 렌더러 탑재**
  - 수식 기호, 수치 대입, 결과값 도출 KaTeX 파이프라인 연동.
* **Step 4: 머릿말 설정 모달 및 인쇄/PDF/Excel 액션 연결**
  - 모달 팝업 연동 및 브라우저 `window.print()` / 백엔드 PDF 라우트 연결.
* **Step 5: A4 렌더링 프리뷰 검증 및 Git 커밋**
  - 상세/요약 전환, 입력포함 토글, O.K/N.G 표기, 인쇄 프리뷰 확인 후 커밋/푸시.

---

## 4. 수용 기준 및 1:1 체크리스트 (Acceptance Criteria)
- [x] 다크 테마 상태에서도 계산서 용지 내부가 순백색(`#ffffff`)과 고대비 글자로 유지되는가?
- [x] `상세 보고서` 선택 시 KaTeX 수식 전개 과정(기호 → 수치대입 → 결과)이 완벽히 렌더링되는가?
- [x] `사용자 입력 데이터 상세 포함` 체크 해제 시 제2장 입력 데이터 표가 계산서에서 즉시 숨겨지는가?
- [x] 머릿말 설정 모달에서 회사명/프로젝트명을 입력하면 계산서 최상단 헤더에 즉각 반영되는가?
- [x] 종합 판정란에 원본앱 스타일의 `  →  O.K` (녹색) 또는 `  →  N.G` (적색)가 정확히 표기되는가?
