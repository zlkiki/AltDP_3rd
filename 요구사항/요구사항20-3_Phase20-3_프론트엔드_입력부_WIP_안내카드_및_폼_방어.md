# 요구사항 20-3: Phase 20-3 프론트엔드 입력부 WIP 안내카드 및 폼 방어 구축 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서(SSOT)**:
  - [`요구사항 20 (Phase 20 마스터)`](요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md) 제3.2절 및 제5절
  - [`docs/07_web_application_ui_ux_specification.md`](../docs/07_web_application_ui_ux_specification.md) (Left-Sub 워크스페이스, 3버튼 액션 파이프라인 및 원본앱 다이얼로그 탭 구조)
* **목적**: 1열 탐색기에서 원본앱 1:1 서브탭 전용 폼이 아직 연동 준비 중(WIP)인 부재를 선택했을 때, **`docs/07`의 Left-Sub 영역(`pane-input-form`)에 이전 부재의 폼이 잔존하거나 엉뚱한 필드가 노출되는 결함을 완벽히 차단**하고, 모던 글래스모피즘 기반의 **"원본앱 전용 WIP 안내 카드"**를 렌더링하며, 상단 툴바의 **3버튼 액션 파이프라인(`적용/검토/설계`)**과 안전하게 연동합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. Left-Sub 폼 완전 언마운트 및 상태 초기화 가드 (`docs/07`)
* **구현 파일**: `src/web/static/js/core/dispatcher.js` 및 `src/web/static/js/member_forms.js`
* **동작 사양**:
  - `ModuleDispatcher.switchModule(key)` 실행 시, 대상 모듈에 전용 폼 팩이 없거나 WIP 상태인 경우:
    1. `pane-input-form` 내부의 기존 폼 이벤트 리스너를 완전 해제하고 DOM을 깨끗이 비움(`innerHTML = ''`).
    2. 상단 부재 리스트 매니저(`pane-member-list`)와의 연동을 보호하여 부재 생성/복제/삭제 시 런타임 에러 차단.

### 2.2. 원본앱 전용 WIP 안내 카드 렌더러 (`WIPCardRenderer`)
* **구현 컴포넌트**: `WIPCardRenderer.render(container, moduleMeta)`
* **UI 디자인 및 구성 요소 (`docs/07`, `docs/13`)**:
  1. **헤더 티어 뱃지**: `[Tier 1 핵심 부재]`, `[Tier 2 주요 부재]`, `[Tier 3 특수]`.
  2. **부재 명칭 및 원본앱 DLG 코드**: (예: `RC 지하외벽`, `IDD_RCS_BASEMENT_WALL_DLG`).
  3. **적용 KDS 국가건설기준**: (예: `KDS 14 20 40 : 2022`).
  4. **지원 예정 서브탭 안내**: 원본앱 1:1 서브탭 (`[재질 및 단면]`, `[배근 상세]`, `[설계 하중]`, `[토압/수압 조건]`).
  5. **로드맵 알림문**: "본 부재는 KDS 수식 및 원본앱 1:1 서브탭 전용 폼 개발 준비 중입니다."

### 2.3. 3버튼 액션 파이프라인 안전 방어 (`docs/07` 제1절)
* 상단 마스터 툴바의 **`[💾 적용 (Apply)]`**, **`[⚡ 검토 (Check)]`**, **`[✨ 설계 (Design)]`** 버튼 클릭 시:
  - WIP 상태인 부재일 경우 가짜 계산 요청을 전송하지 않고:
  - 브라우저 우하단에 **"⚠️ 해당 부재는 원본앱 1:1 전용 서브탭 폼 및 KDS 연산 탑재 준비 중입니다."** 토스트 알림 연동.

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)

1. **Step 1 [Medium]**: `dispatcher.js`의 Fallback 분기에서 기존 폼 언마운트 및 클린업 로직 구현.
2. **Step 2 [Medium]**: `src/web/static/js/forms/wip_card.js` 컴포넌트 작성 및 글래스모피즘 카드 스타일링.
3. **Step 3 [Medium]**: 티어별 뱃지 및 원본앱 DLG 코드/KDS 기준 자동 바인딩 로직 구현.
4. **Step 4 [Medium]**: `docs/07` 3버튼 액션(`적용/검토/설계`) 클릭 시 안전 토스트 알림 연동.
5. **Step 5 [High]**: 브라우저 UI에서 미연동 부재 클릭 시 Left-Sub 영역에 잔존 폼 없이 WIP 카드 렌더링 확인 (콘솔 에러 0건).

---

## 4. 완료 검증 기준 (Acceptance Criteria)
* 미연동 부재 선택 시 이전 부재의 폼이 0.1%도 잔존하지 않고 깨끗이 초기화될 것.
* Left-Sub의 사용자 입력부에 부재명, 티어 뱃지, 원본앱 DLG 코드가 기재된 WIP 카드가 렌더링될 것.
* 3버튼 액션 클릭 시 콘솔 에러 없이 정상 토스트 알림이 발생할 것.
