# 요구사항 22-4-1-3: Phase V1-01 Step 4-3 RC 보 원본앱 1:1 대조 배근 유형(1/2/3단면 설계) 라디오 옵션 및 주근 복합 분리입력(개수+호칭경 콤보) UI 전면 개편 명세서

## 1. 개요 및 목적

본 문서는 **RC 보 (`rc_beam`)** 입력폼의 Tab 2(배근 탭)를 원본앱(`Design+.exe`) 실측 리소스와 1:1로 일치시키기 위해, **(1) 원본앱 배근 유형(Arrange Type: 1개 단면 / 2개 단면 / 3개 단면 설계) 라디오 옵션 그룹 구현**, **(2) 기존 단일 문자열 텍스트박스(`4-D25`) 입력을 원본앱 1:1 대조 [개수 텍스트박스] + [-] 라벨 + [호칭경 콤보박스] 복합 인라인 컨트롤로 전면 개편**, **(3) 단별 배근 개수 유효성 제약(1단 $\ge 2$, 2단 $\ge 0$ 및 0 입력 시 디밍/미배치 처리)**, 그리고 **(4) 배근 유형별 실시간 양방향 자동 동기화 및 반응형 레이아웃 방어**를 완수하기 위한 프론트엔드 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/components/form_rc_beam.js` (입력폼: 배근 유형 라디오 추가, 주근 복합 분리 컨트롤 전면 개편, 동기화 로직)
  - `src/web/static/css/styles.css` (복합 인라인 컨트롤 스타일 및 리사이즈 방어)
* **권장 AI 모델**: ⚙️ **Medium (Fast / Accurate)** - DOM 조작, 컴포넌트 렌더링, 이벤트 바인딩, 반응형 CSS 방어
* **1순위 원본앱 리소스 Ground Truth**:
  - `original_src/Midas Design+/Language/Korean/DLG_DPLUS_RCS.ini`
    * `IDD_RCS_BEAM_PMODE_DLG`: `IDC_GURBE_FRAME_ARRANGE = "배근 유형"`
    * `IDC_GURBE_RADIO_ARRANGETYPE1 = "배근 유형-1 ( 전단면 )"`
    * `IDC_GURBE_RADIO_ARRANGETYPE2 = "배근 유형-2 ( 양단부와 중앙부 )"`
    * `IDC_GURBE_RADIO_ARRANGETYPE3 = "배근 유형-3 ( 각단부와 중앙부 )"`
    * `IDC_GURGC_LABEL_MAIN_BAR2 = "-"` (구분자 고정 라벨)
  - `decompiled_src/DPLUS_RCS.dll_symbols.txt`: `CURBEPModeDlg::LeaveDropDownCell`, `InitGrid`, `RedrawBarGrid`

---

## 2. 배근 유형(Arrange Type) 라디오 옵션 상세 명세

### 2.1. 3대 배근 유형 정의 및 UI 배치
Tab 2 배근 탭 상단(`위치별 주철근 및 스터럽 배근` 섹션 직상단)에 원본 1:1 라디오 버튼 그룹을 배치합니다:

```html
<div class="eng-form-section">
    <div class="form-section-header">배근 유형 (Reinforcement Arrange Type)</div>
    <div class="arrange-type-radio-group" style="display:flex; gap:16px; margin-bottom:12px; font-size:12px;">
        <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="radio" name="beam_arrange_type" value="ONE_SECTION">
            <span>배근 유형-1 (전단면)</span>
        </label>
        <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="radio" name="beam_arrange_type" value="SYMMETRIC_ENDS" checked>
            <span>배근 유형-2 (양단부와 중앙부)</span>
        </label>
        <label class="radio-label" style="display:flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="radio" name="beam_arrange_type" value="THREE_STATIONS">
            <span>배근 유형-3 (각단부와 중앙부)</span>
        </label>
    </div>
</div>
```

### 2.2. 배근 유형별 동기화 동작 규칙
1. **배근 유형-1 (전단면, `ONE_SECTION`)**:
   - 단일 단면(중앙부/전단면) 배근 테이블 셀만 직접 수정 가능하거나, 임의 셀 수정 시 End-I, Center-M, End-J 3개 위치의 해당 단(상/하부 1, 2단 및 스터럽)에 동일 값이 즉시 일괄 복사 동기화.
2. **배근 유형-2 (양단부와 중앙부, `SYMMETRIC_ENDS`, 기본값 Default)**:
   - 실무 표준 설정.
   - 단부-I (End-I)의 개수/호칭경/스터럽 조작 시 단부-J (End-J)의 해당 셀이 실시간 양방향 자동 동기화.
   - 단부-J 행에는 시각적으로 `[단부-I 대칭 연동]` 안내 태그 표출 또는 셀 디밍 처리.
3. **배근 유형-3 (각단부와 중앙부, `THREE_STATIONS`)**:
   - End-I, Center-M, End-J 3개 위치 모든 셀이 독립적으로 활성화되어 비대칭 배근 지원.

---

## 3. 주근 복합 분리입력 컨트롤 (Composite Control) UI 규격

### 3.1. 문제 배경 및 개편
* 기존 단일 텍스트박스(`<input type="text">`에 `4-D25` 직접 타이핑)는 공백, 오탈자, 하이픈 누락 등 휴먼 에러를 유발하므로, 원본앱 DropDown Cell 방식과 1:1로 일치하는 **[개수 텍스트박스] + [-] 고정 라벨 + [호칭경 콤보박스]** 조합으로 전면 대체합니다.

### 3.2. 셀 내부 렌더링 HTML 구조
```html
<!-- 1단 (상부 1단, 하부 1단): 스터럽 코너 정착 최소 2개 필수 제약 (min="2") -->
<div class="rebar-cell-composite" data-station="end_i" data-row="top_layer1">
    <input type="number" class="form-input rebar-count-input" min="2" max="30" step="1" value="4">
    <span class="rebar-sep">-</span>
    <select class="form-input rebar-dia-select">
        <option value="D10">D10</option>
        <option value="D13">D13</option>
        <option value="D16">D16</option>
        <option value="D19">D19</option>
        <option value="D22">D22</option>
        <option value="D25" selected>D25</option>
        <option value="D29">D29</option>
        <option value="D32">D32</option>
        <option value="D35">D35</option>
    </select>
</div>

<!-- 2단 (상부 2단, 하부 2단): 보강단이므로 0개 이상 허용 (min="0") -->
<div class="rebar-cell-composite" data-station="end_i" data-row="top_layer2">
    <input type="number" class="form-input rebar-count-input" min="0" max="30" step="1" value="0">
    <span class="rebar-sep">-</span>
    <select class="form-input rebar-dia-select">
        <!-- 동일 9종 옵션 -->
    </select>
</div>
```

### 3.3. 상세 스타일 및 반응형 방어 (`styles.css`)
```css
.rebar-cell-composite {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    white-space: nowrap;
}
.rebar-cell-composite .rebar-count-input {
    width: 38px !important;
    text-align: center;
    padding: 2px 2px !important;
    font-size: 12px;
}
.rebar-cell-composite .rebar-sep {
    font-weight: 700;
    color: var(--text-muted, #888);
    font-size: 13px;
    user-select: none;
}
.rebar-cell-composite .rebar-dia-select {
    width: 62px !important;
    padding: 2px 4px !important;
    font-size: 12px;
    font-weight: 600;
}
.beam-rebar-table th, .beam-rebar-table td {
    min-width: 110px;
}
```

---

## 4. 상태 관리 및 이벤트 동기화 규칙

1. **초기값 파싱 (`parseRebarStr`)**:
   - `4-D25` $\rightarrow$ `{ count: 4, dia: 'D25' }`
   - `0` 또는 빈값 $\rightarrow$ `{ count: 0, dia: 'D22' }`
2. **단별 배근 개수 유효성 제약**:
   - **1단**: `count < 2` 입력 시 `2`로 자동 보정.
   - **2단**: `count === 0`일 때 호칭경 콤보박스 `opacity: 0.45` 디밍 및 비활성화, 데이터 모델에는 `"0"`으로 직렬화 저장.
3. **정상 조합 및 브로드캐스팅**:
   - `count >= 1`인 경우 `${count}-${dia}` (예: `4-D25`) 문자열로 결합하여 `this.data.rebar[station][row]`에 저장.
   - `this._broadcastChange()`를 호출하여 `ProjectStore`, 2D 캔버스, 계산서에 100ms 이내 실시간 동기화.
4. **배근 유형 변경 이벤트**:
   - 라디오 버튼 변경 시 `this.data.rebar.arrange_type`에 즉시 저장하고 위 제2.2절 동기화 규칙에 따라 테이블 뷰를 즉시 갱신.

---

## 5. 완료 검증 기준 (DoD)

- [ ] Tab 2 배근 탭 상단에 배근 유형 3종 라디오가 정상 배치되고 초기값이 `SYMMETRIC_ENDS`로 설정될 것.
- [ ] 배근 테이블 12개 주근 셀이 [개수 텍스트박스 + '-' 라벨 + 호칭경 콤보] 복합 컨트롤로 정상 렌더링될 것.
- [ ] 1단 개수 최소 2개(`min="2"`), 2단 개수 0개(`min="0"`) 제약이 정상 작동할 것.
- [ ] 2단 개수 `0` 입력 시 호칭경 콤보 디밍 및 데이터 모델 `"0"` 정규화 처리가 정상 수행될 것.
- [ ] 개수 또는 콤보 변경 시 `{count}-{dia}` 결합 문자열이 생성되어 캔버스 및 계산서와 실시간 동기화될 것.
- [ ] 브라우저 창/패널 리사이즈 시 배근 테이블 열이 겹치거나 깨지지 않고 가로 스크롤로 안전하게 방어될 것.
- [ ] 브라우저 콘솔 에러가 0건일 것.
