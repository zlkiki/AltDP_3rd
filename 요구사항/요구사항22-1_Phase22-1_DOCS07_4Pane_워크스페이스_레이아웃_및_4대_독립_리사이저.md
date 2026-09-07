# 요구사항 22-1: Phase 22-1 DOCS 07 4-Pane 워크스페이스 레이아웃 및 4대 독립 리사이저 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서 (SSOT)**:
  - [`요구사항 22 (마스터)`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md) 제1절, 제6절
  - [`docs/07_web_application_ui_ux_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) 제1절, 제2절, 제5절
  - [`docs/10_agent_development_protocols.md`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)
* **목적**: DOCS 07에 정의된 표준 4-Pane(탐색기/사이드바 ↔ 부재매니저/입력폼 ↔ 2D/3D 그래픽 ↔ KDS 계산서) 올인원 워크스페이스 레이아웃을 웹에 물리적으로 정렬하고, 상호 연쇄 간섭 없이 부드럽게 크기를 조절하는 4대 독립 리사이저 엔진(`layout_resizer.js`)을 확립합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. 워크스페이스 DOM 및 CSS Grid/Flex 정렬
* **대상 파일**: `src/web/templates/index.html`, `src/web/static/css/layout.css`
* **DOM 계층 구조**:
  ```html
  <div id="app-container" class="app-root">
    <!-- Top Master Toolbar -->
    <header id="top-toolbar" class="top-master-toolbar">
      <div class="brand-group">
        <span class="brand-title">AltDP Member Designer</span>
        <span class="kds-badge">KDS 2022</span>
      </div>
      <div class="toolbar-actions">
        <div id="unit-selector-container"></div>
        <button id="btn-theme-toggle" class="btn-icon" title="테마 전환 (🌙/☀️)">🌙</button>
        <button id="btn-save-layout" class="btn-sm" title="레이아웃 비율 저장">📌 저장</button>
        <button id="btn-reset-layout" class="btn-sm" title="레이아웃 초기화">🔄 초기화</button>
      </div>
    </header>

    <!-- Main Workspace (4-Pane) -->
    <main id="main-workspace" class="workspace-4pane">
      <!-- 1. Left Sidebar -->
      <aside id="sidebar-nav" class="pane-sidebar">
        <!-- 계층형 모듈 탐색기 컨테이너 -->
      </aside>

      <!-- Resizer 1: Sidebar-Horizontal -->
      <div id="resizer-sidebar-h" class="resizer-h" data-direction="horizontal"></div>

      <!-- 2. Left-Sub Pane (Member Manager + Input Form) -->
      <section id="left-sub-pane" class="pane-left-sub">
        <div id="pane-member-list" class="subpane-member-list">
          <!-- Pane 1: 다중 부재 매니저 그리드 -->
        </div>
        <!-- Resizer 2: Left-Vertical -->
        <div id="resizer-left-v" class="resizer-v" data-direction="vertical"></div>
        <div id="pane-input-form" class="subpane-input-form">
          <!-- Pane 2: 파라메트릭 인풋 폼 -->
        </div>
      </section>

      <!-- Resizer 3: Left-Horizontal -->
      <div id="resizer-left-h" class="resizer-h" data-direction="horizontal"></div>

      <!-- 3. Center Graphic Pane (2D/3D Multi-Viewport) -->
      <section id="center-pane" class="pane-center-graphic">
        <!-- Pane 3: 세로 적층형 다중 뷰포트 -->
      </section>

      <!-- Resizer 4: Main-Horizontal -->
      <div id="resizer-main-h" class="resizer-h" data-direction="horizontal"></div>

      <!-- 4. Right Report Pane (KDS Calculation Sheet) -->
      <aside id="right-pane" class="pane-right-report">
        <!-- Pane 4: KDS 표준 계산서 컨테이너 -->
      </aside>
    </main>
  </div>
  ```

### 2.2. 4대 독립 리사이저 엔진 구현 (`layout_resizer.js`)
* **대상 파일**: `src/web/static/js/components/layout_resizer.js`
* **동작 및 바운딩 제약 명세**:
  | 리사이저 ID | 타겟 및 동작 대상 | 최소/최대 바운딩 제약 | 기본값 |
  |---|---|---|---|
  | `resizer-sidebar-h` | 사이드바 너비 조절 | $200\text{px} \le W_{sb} \le 480\text{px}$ | $280\text{px}$ |
  | `resizer-left-h` | Left-Sub Pane(부재+폼) 너비 조절 | 워크스페이스 가용폭의 $20\% \le W_{sub} \le 50\%$ | $380\text{px}$ |
  | `resizer-left-v` | Pane 1(부재목록) 상하 높이 조절 | $80\text{px} \le H_{memb} \le 400\text{px}$ | $160\text{px}$ |
  | `resizer-main-h` | Center(그래픽) ↔ Right(계산서) 비율 조절 | 중앙/우측 가용폭의 $25\% \le W_{center} \le 75\%$ | $50 : 50$ |
* **상세 기능 요구사항**:
  1. **PointerLock / Global Dragging**: 마우스 커서가 iframe/canvas 위를 지나더라도 끊김 없는 `window.addEventListener('pointermove')` 추적 및 드래그 중 텍스트 선택 방지(`user-select: none`).
  2. **상태 영속화 (`localStorage`)**: 드래그 종료 시 4대 치수를 `AltDP_layout_ratios` 키에 JSON으로 즉시 저장. 페이지 재방문 시 자동 복원.
  3. **원클릭 리셋 (`#btn-reset-layout`)**: 기본 황금비 및 표준 치수로 즉시 원복.
  4. **반응형 윈도우 리사이즈 대응**: 브라우저 창 축소 시 최소 가시 폭을 보장하는 스마트 클램핑(Clamping).

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)
* **Step 1: HTML/CSS 4-Pane 골격 정렬**
  - `src/web/templates/index.html` 4-Pane 및 4대 리사이저 ID/클래스 전면 정렬.
  - `src/web/static/css/layout.css` Flex/Grid 분할 스타일 및 리사이저 드래그 핸들 UI(호버 시 블루 하이라이트) 구축.
* **Step 2: 리사이저 드래그 엔진 구현 (`layout_resizer.js`)**
  - 4개 분할 지점별 독립 마우스/터치 드래그 산출 로직 구현.
  - 음수/오버플로 방지 최소·최대 클램핑 적용.
* **Step 3: 상태 영속화 및 툴바 연동**
  - `localStorage` 세션 저장 및 복원 파이프라인 연동.
  - 상단 툴바의 `📌 저장` 및 `🔄 초기화` 버튼 이벤트 리스너 연결.
* **Step 4: 브라우저 DOM 렌더링 및 인터랙션 검증**
  - 각 리사이저 드래그 시 인접 패널만 매끄럽게 리사이징되는지 4개 지점 전수 수동/자동 검증.
  - 캔버스/계산서 왜곡 없는 리플로우(Reflow) 보장.
* **Step 5: E2E 통합 확인 및 Git 커밋**
  - 콘솔 에러 0건 확인 및 `feat(req22-1): 4-Pane 레이아웃 및 4대 독립 리사이저 엔진 완수` 커밋/푸시.

---

## 4. 수용 기준 및 1:1 체크리스트 (Acceptance Criteria)
- [ ] `index.html` 내에 `resizer-sidebar-h`, `resizer-left-h`, `resizer-left-v`, `resizer-main-h` 4대 리사이저 DOM이 명확히 정의되어 있는가?
- [ ] 4개 리사이저가 독립적으로 동작하며 다른 패널에 원치 않는 레이아웃 깨짐을 유발하지 않는가?
- [ ] 리사이저별 최소/최대 바운딩 제약(사이드바 200~480px, 부재목록 80~400px 등)이 엄격히 적용되는가?
- [ ] 브라우저 새로고침 후에도 사용자가 조절한 레이아웃 크기가 유지되는가?
- [ ] `🔄 초기화` 버튼 클릭 시 기본 권장 레이아웃으로 0.05초 내 즉시 복원되는가?
