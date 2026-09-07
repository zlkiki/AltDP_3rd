# 요구사항 21-4: Phase 21-4 세로 적층형 다중 뷰포트 그래픽 정보부 Pane 3 구축 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서 (SSOT)**:
  - [`요구사항 21 (마스터)`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md) 제4절
  - [`docs/07_web_application_ui_ux_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) 제4.3절
  - [`docs/09_decompiled_source_and_symbol_inventory.md`](file:///f:/PyProject/AltDP_3rd/docs/09_decompiled_source_and_symbol_inventory.md) (`DPLUS_VDraw.dll` 드로잉 엔진 분석)
* **목적**: 4-Pane 레이아웃에서 종방향(세로)으로 길게 확보되는 중앙 Center Pane의 특성을 극대화하여, **상단(단면 및 형상 상세)**과 **하단(공학 역학 및 P-M 상관도 다이어그램)**으로 분할된 **세로 적층형 다중 뷰포트(Vertical Multi-Card Viewport)**를 구축하고, RC/Steel/접합부/기초/PC 전 부재군의 2D 그래픽 시각화를 완성합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. 세로 적층형 2단 다중 뷰포트 컨테이너 구조
* **대상 파일**: `src/web/static/js/components/graphic_viewport.js`, `src/web/static/css/canvas.css`
* **레이아웃 구조**:
  ```html
  <div id="center-pane-container" class="center-viewport-stack">
    <!-- 상단 뷰포트: 형상 및 단면 상세 (Top Viewport) -->
    <div id="viewport-card-geometry" class="viewport-card">
      <div class="viewport-toolbar">
        <span class="viewport-title">📐 형상 및 단면 상세 (Cross-Section & Detailing)</span>
        <div class="viewport-actions">
          <button id="btn-fit-geom" class="btn-tool" title="화면 맞춤">⛶ Fit</button>
          <button id="btn-zoom-in-geom" class="btn-tool" title="확대">+</button>
          <button id="btn-zoom-out-geom" class="btn-tool" title="축소">-</button>
          <button id="btn-toggle-dim" class="btn-tool active" title="치수선 켜기/끄기">📏 Dim</button>
        </div>
      </div>
      <div class="canvas-wrapper">
        <canvas id="canvas-geometry" width="600" height="400"></canvas>
      </div>
    </div>

    <!-- 하단 뷰포트: 공학 역학 다이어그램 (Bottom Viewport) -->
    <div id="viewport-card-mechanics" class="viewport-card">
      <div class="viewport-toolbar">
        <span class="viewport-title">📊 공학 역학 다이어그램 (Mechanics & P-M Diagram)</span>
        <div class="viewport-actions">
          <button id="btn-fit-mech" class="btn-tool" title="화면 맞춤">⛶ Fit</button>
          <button id="btn-toggle-3d" class="btn-tool" title="3D 곡면 전환">🌐 3D</button>
          <button id="btn-toggle-dcr-bar" class="btn-tool active" title="DCR 바 토글">📶 DCR</button>
        </div>
      </div>
      <div class="canvas-wrapper">
        <canvas id="canvas-mechanics" width="600" height="400"></canvas>
      </div>
    </div>
  </div>
  ```

### 2.2. 전 부재군 2D 그래픽 특성화 매트릭스 (`renderer2d.js`, `pm_chart.js`)
* **대상 파일**: `src/web/static/js/renderer2d.js`, `src/web/static/js/pm_chart.js`
* **부재 도메인별 시각화 명세**:
  1. **RC 보 / 기둥**:
     - **상단**: 콘크리트 외곽선 해칭, 피복선, 135° 내진 갈고리 스터럽/대근($r=2d_b$), 상/하부 1단 및 2단 주철근 솔리드 점, 치수선.
     - **하단**: 기둥 축력-모멘트 P-M 상관곡선(공칭 $P_n-M_n$ 파란 실선 vs 설계 $\phi P_n-\phi M_n$ 빨간 실선), 계수하중($P_u, M_u$) 타점 마커(녹색 OK / 적색 NG 십자 마커). 보의 경우 계수 휨모멘트($M_u$) / 전단력($V_u$) 포락선 다이어그램.
  2. **철골 보 / 기둥**:
     - **상단**: KS H형강, 각형강관 단면 형상, 플랜지/웨브 두께 치수선, 판폭두께비 조밀(초록)/비조밀(노랑)/세장(빨강) 영역 색상 코딩.
     - **하단**: 횡비틀림좌굴(LTB) 모멘트 구배 다이어그램($C_b$) 및 비지지길이($L_b$) 구간도.
  3. **철골 접합부 / 베이스플레이트**:
     - **상단**: 2D CAD 평면도(볼트 구멍, 볼트 게이지/피치/연단거리 치수선, 용접 비드).
     - **하단**: 입면 단면도(모르타르 두께, 기초 콘크리트 지압선, 앵커볼트 인장 콘/전단 파열선).
  4. **RC 슬래브 / 기초 / 옹벽**:
     - **상단**: 기초판 평면도($B \times L$), 기둥 위치, 말뚝(Pile) 그리드, 1/2방향 전단 위험단면($d, d/2$) 적색 점선.
     - **하단**: 편심하중에 따른 지반 접지압 분포도(사다리꼴/삼각형 $q_{min} \sim q_{max}$ 다이어그램).
  5. **PC / PSC 및 보수보강(RFM)**:
     - **상단**: 프리캐스트 단면(더블티, 할로우코어) 및 긴장재(Strand) 중심선 배치도.
     - **하단**: CFRP 탄소섬유판/강판 접착 위치 및 보강 전 vs 보강 후 내력 증분 비교 막대 차트.

### 2.3. 대화형 인터랙션 (Zoom, Pan, Hover Tooltip)
* **상단/하단 독립 조작**: 마우스 휠 줌(Zoom), 마우스 드래그 팬(Pan), 원클릭 뷰포트 맞춤(`[⛶ Fit]`).
* **실시간 호버 툴팁(Hover Tooltip)**:
  - 캔버스 내 철근 점, 볼트 구멍, 텐던 위에 마우스 오버 시 직경, 배근 간격, 단면적 툴팁 오버레이 표출.
* **치수선(Dimension Line) 토글**: `[📏 Dim]` 버튼으로 치수선 레이어 ON/OFF 지원.

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)
* **Step 1: 세로 적층형 다중 뷰포트 컨테이너 레이아웃 구축**
  - `src/web/static/css/canvas.css` 상/하 2단 카드 레이아웃 및 툴바 스타일 구현.
* **Step 2: 상단 뷰포트 단면 및 배근 렌더러 정밀화 (`renderer2d.js`)**
  - RC 직사각형/T형 보, 기둥, H형강, 기초 평면도 렌더링 로직 통합.
* **Step 3: 하단 뷰포트 공학 역학 다이어그램 엔진 구축 (`pm_chart.js` 등)**
  - P-M 상관곡선, 지반 접지압, LTB 다이어그램 렌더링 파이프라인 완성.
* **Step 4: 인터랙션(Zoom/Pan/Fit/Tooltip) 엔진 탑재 (`graphic_viewport.js`)**
  - 상/하단 카드별 독립 매트릭스 변환 및 마우스 이벤트 바인딩.
* **Step 5: 캔버스 그래픽 렌더링 검증 및 Git 커밋**
  - 부재 변경 시 상/하단 뷰포트 동시 렌더링 확인 후 커밋/푸시.

---

## 4. 수용 기준 및 1:1 체크리스트 (Acceptance Criteria)
- [ ] Center Pane 내에 상단(단면/형상)과 하단(공학 역학) 2단 세로 적층 카드가 명확히 분할되어 표시되는가?
- [ ] 기둥 부재 선택 시 상단에 단면 배근도가, 하단에 P-M 상관곡선(공칭/설계)과 타점 마커가 정확히 그려지는가?
- [ ] 보, 기초, H형강 부재 선택 시 부재별 고유 형상 및 역학 다이어그램이 정상 표출되는가?
- [ ] 상단/하단 카드가 서로 간섭 없이 독립적으로 줌, 팬, Fit 동작을 수행하는가?
- [ ] 철근 또는 볼트 그래픽에 마우스 오버 시 제원 호버 툴팁이 표출되는가?
