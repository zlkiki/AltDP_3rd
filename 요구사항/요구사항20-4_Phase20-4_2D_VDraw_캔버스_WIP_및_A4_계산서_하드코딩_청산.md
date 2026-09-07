# 요구사항 20-4: Phase 20-4 2D VDraw 캔버스 WIP, KDS A4 계산서 하드코딩 청산 및 redcr_common_renderer 제거 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서(SSOT)**:
  - [`요구사항 20 (Phase 20 마스터)`](요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md) 제1.2절, 제3.3절, 제3.4절 및 제5절
  - [`docs/07_web_application_ui_ux_specification.md`](../docs/07_web_application_ui_ux_specification.md) (상시 순백색 `#ffffff` A4 용지 고정, Center 캔버스 및 VDraw 2D/3D 드로잉 엔진)
  - [`docs/14_structural_calculation_report_specification.md`](../docs/14_structural_calculation_report_specification.md) (KDS 3대 보고서 모드 & 5대 장구분 표준 목차)
* **목적**: 
  1. Center 캔버스(`pane-graphic-view`)와 Right 리포트(`pane-right-report`)에 잔존하는 **하드코딩된 정적 텍스트 및 가짜 계산 결과(가짜 처짐/강도, 무조건 ALL O.K 출력)를 100% 영구 청산**.
  2. AltDP_2nd 시절 임시로 뭉뚱그려 화면을 때우던 **레거시 범용 뷰어(`redcr_common_renderer.js`)의 2단 카드형 레이아웃 및 가짜 판정표를 전면 제거/청산**.
  3. `docs/14` 5대 장구분 규격에 기반한 **상시 순백색(`#ffffff`) A4 계산서 WIP 표준 시트**와 단정한 **2D VDraw Canvas WIP 플레이스홀더**를 렌더링하여 투명하고 무결한 엔지니어링 신뢰성을 확보.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. Center 영역 2D VDraw Canvas WIP 플레이스홀더 (`docs/07`)
* **구현 파일**: `src/web/static/js/renderer2d.js` (또는 `vdraw_engine.js`)
* **동작 사양**:
  - 전용 VDraw 드로잉이 미연동된 부재 선택 시:
    1. 캔버스 뷰포트를 클리어하고 부드러운 다크 엔지니어링 그리드(격자선) 렌더링.
    2. 캔버스 정중앙에 은은한 기하학적 단면 아이콘과 부재명 표시.
    3. 안내 텍스트: **"📐 2D VDraw 단면 및 배근도 그래픽 준비 중 (WIP)"**.
    4. 3D P-M 곡선 토글 버튼 비활성화 또는 WIP 안내 연동으로 캔버스 런타임 에러 완전 차단.

### 2.2. Right 영역 레거시 임시 범용 뷰어(`redcr_common_renderer.js`) 전면 청산 및 하드코딩 척결 (`docs/14`)
* **구현 파일**: `src/web/static/js/report/result_renderer.js`, `redcr_common_renderer.js`
* **청산 대상 (영구 삭제 및 정리)**:
  1. **레거시 4-Pillar 카드 뷰 청산**: A4 용지 규격을 위반하고 화면을 왜곡하던 2단 카드형 레이아웃(`four-pillar-container`) 및 계산서 내부 임베딩 캔버스(`pillar-section-canvas`) 전면 삭제.
  2. **기만적 뭉뚱그림 로직 청산**: 실제 KDS 기준식과 무관하게 백엔드 JSON 키를 임의 탐색하여 조합하던 가짜 판정표(`generateCheckTableHtml`) 및 수식 조립 코드 청산.
  3. **하드코딩 정적 텍스트 청산**: 계산 엔진의 실제 결과 전달 없이 미리 박혀있던 정적 문자열 (예: `δ = 8.2 mm ≤ 20.0 mm (만족)`, `ALL O.K`, 가짜 DCR 등) 전면 영구 삭제.
* **디스패치 분기 일원화 (`result_renderer.js`)**:
  - 부재별 전용 KDS 리포터(예: RC 보 `RedcrBeamReport`, RC 기둥 `RedcrColumnReport` 등)가 존재하는 경우 $\rightarrow$ 해당 전용 A4 계산서 렌더러 호출.
  - 전용 KDS 리포터가 미구현된 부재(WIP)의 경우 $\rightarrow$ `RedcrCommonRenderer`의 카드 뷰 대신 `docs/14` 5대 장구분 기반 **순백색(`#ffffff`) A4 WIP 표준 시트**로 직결 호출.
* **테스트 코드 정합성 유지**:
  - `tests/ui/test_visual_report_serving.py` 내 `redcr_common_renderer.js` 서빙 의존성을 순백색 A4 WIP 리포터로 안전하게 마이그레이션.

### 2.3. A4 구조계산서 5대 장구분 WIP 표준 시트 렌더링 (`docs/07`, `docs/14`)
* **구현 파일**: `src/web/static/js/report/result_renderer.js` (또는 `report_view.js`)
* **미구현 / 미계산 상태 시 동작 사양**:
  - **상시 순백색 `#ffffff` A4 용지 규격 고정 (`docs/07` 제1절 원칙 1)**.
  - 상단 문서 표제부: 부재명, 검토일자, 검토자, 적용 KDS 설계기준 표시.
  - `docs/14` 표준 5대 장구분 구조 기반 WIP 워터마크 안내:
    ```markdown
    ## 1. 일반 설계 조건: KDS 국가건설기준
    ## 2. 재질 및 단면: 제원 데이터 수신 대기 중
    ## 3. 설계 하중: 위험 하중조합 (Governing LCB) 산정 준비 중
    ## 4. 단면 안전성 검토: KDS 공식 수식 전개식 작성 예정 (WIP)
    ## 5. 종합 판정: [미구현 (WIP)]
    ```

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)

1. **Step 1 [High]**: 프론트엔드 리포트 렌더러 내 하드코딩 정적 텍스트 및 "8단계 KaTeX" 잔재 전수 검색/삭제.
2. **Step 2 [Medium]**: `renderer2d.js` 내 `renderWIPCanvas(canvas, meta)` 2D 플레이스홀더 함수 구현.
3. **Step 3 [High]**: `redcr_common_renderer.js` 카드형 레거시 청산 및 `result_renderer.js` 내 `docs/14` 5대 장구분 기반 순백색 A4 WIP 템플릿 직결 구현.
4. **Step 4 [Medium]**: 플래그십 부재(RC 보 등)의 실제 3대 보고서(요약/상세/입력데이터) 동적 렌더링 및 WIP 부재 A4 시트 표출 회귀 검증.
5. **Step 5 [High]**: 브라우저 인쇄 미리보기(Ctrl+P) 및 캔버스 화면 렌더링 최종 확인 (`test_visual_report_serving.py` PASS).

---

## 4. 완료 검증 기준 (Acceptance Criteria)
* 계산서 영역에 계산되지 않은 가짜 수치나 정적 하드코딩 문자열이 0건일 것.
* `redcr_common_renderer.js`의 구형 4-Pillar 카드형 레이아웃 노출이 0건일 것.
* 전용 계산서가 미구현된 부재 선택 시, 항상 상시 순백색 `#ffffff` A4 용지 규격의 `docs/14` 5대 장구분 WIP 시트가 단정하게 노출될 것.
* 미연동 부재 선택 시 3열 캔버스와 4열 계산서가 브라우저 콘솔 에러 없이 정직한 WIP 화면을 노출할 것.
