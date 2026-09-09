# 요구사항 25-5: Phase V1-4 Step 5 철골 보/기둥 4열 통합 E2E 검증 & 실사용 UI 온라인 전환 명세서

## 1. 개요 및 통합 아키텍처 매핑

본 문서는 **철골 보/기둥 (`steel_beam_column`)**의 **Step 5 (4-Pane 워크스페이스 통합, 실시간 100ms 동기화, WIP 해제 및 정식 온라인 전환)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_beam_column` (카탈로그 No. 22, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/catalog.js` (모듈 카탈로그 메타데이터 WIP 해제: `is_wip: false`)
  - `src/web/static/js/core/dispatcher.js` (`ModuleDispatcher` 내 철골 보/기둥 라우팅 등록)
  - `src/web/static/js/store/project_store.js` (다중 부재 인스턴스 및 상태 동기화)
  - `src/web/static/js/app.js` (최상위 이벤트 버스 및 리사이저 연동)
  - `tests/test_e2e_steel_beam_column.py` (신규 E2E 자동화 통합 검증 스크립트)
* **2순위 원본 리소스 SSOT**:
  - 전체 워크스페이스 통합 프레임워크 (`CMainFrame`, `CChildFrame`, `CDgnDoc`)

---

## 2. 4-Pane 워크스페이스 100ms 실시간 동시 동기화 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4-Pane 워크스페이스 100ms 실시간 데이터 파이프라인 (ProjectStore & EventBus 중심)                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [사용자 입력] ──► [ProjectStore 바인딩] ──► [FastAPI /api/steel/... 백엔드 검토/설계]          │
│                            │                                                                    │
│            ┌───────────────┴───────────────────────────────┐                                    │
│            ▼                                               ▼                                    │
│  [Pane 3: 세로 적층형 2단 뷰포트]                [Pane 4: 순백색 A4 KaTeX 계산서]                │
│   • 상단: 입면/지지/LTB/모멘트도                 • 5대 장구분 및 8단계 KaTeX 수식 전개          │
│   • 하단: H형강 단면/치수선/조밀성               • DCR 및 O.K / N.G 판정 배지                   │
│                                                                                                 │
│  ※ 입력 변경 이벤트 발생 후 렌더링 완료까지 지연시간 ≤ 100ms 엄수 (Debounce 50ms 적용)          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1. 인터랙티브 반응 및 3대 액션 버튼 파이프라인
1. **단면 규격 및 제원 변경 시**:
   - Tab 1에서 호칭 규격을 변경(`H-400x200x8x13` $\rightarrow$ `H-300x300x10x15`)하거나 치수를 수정하면:
     * `ProjectStore` 상태 즉시 갱신 ($\le 10\text{ms}$).
     * Pane 3 하단 단면도 치수선 및 외곽선 실시간 재드로잉 ($\le 30\text{ms}$).
     * **불필요한 과부하를 막기 위해 계산서 갱신은 대기하고 단면 그래픽만 즉각 반영**.
2. **`[⚡ 검토 (Check)]` 버튼 클릭 시**:
   - 백엔드 KDS 14 31 10 조밀성/LTB/좌굴/P-M 해석 엔진 고속 호출 ($\le 40\text{ms}$).
   - Pane 1 요약 그리드의 규격 및 DCR 값 갱신.
   - 상단 뷰포트 모멘트도 포락선 및 LTB 파선 곡선 재렌더링.
   - Pane 4 순백색 A4 계산서의 단면 제원 테이블, 판폭두께비, LTB, P-M 상호작용비 8단계 KaTeX 수식 전개 ($\le 50\text{ms}$).
   - **총 검토 소요 시간 $\le 100\text{ ms}$**로 끊김 없는 인터랙티브 설계 환경 확보.
3. **`[✨ 자동설계 (Auto Design)]` 버튼 클릭 시**:
   - 현재 계수하중 및 지지조건에 적합한 최적 최소 중량 KS H형강 단면 자동 선별 후 폼에 주입.

---

## 3. 카탈로그 정식 온라인 전환 (`is_wip: false`)

`src/web/static/js/catalog.js`에서 `steel_beam_column` 모듈의 WIP 상태를 해제하여 실사용 모듈로 등록합니다:

```javascript
{
    id: "steel_beam_column",
    name: "철골 보/기둥",
    category: "steel",
    group: "frame",
    catalog_no: 22,
    tier: "Tier 1",
    is_wip: false,                 // WIP 해제 및 정식 온라인 활성화!
    icon: "bi-columns-gap",
    description: "KDS 14 31 10 H형강/강관 휨·LTB·압축좌굴·전단·P-M 조합력 통합 설계",
    route: "/api/steel/column/design",
    form_component: "form_steel_beam_column",
    canvas_component: "vector_steel_beam_column",
    report_component: "redcr_steel_beam_column"
}
```

---

## 4. E2E 통합 테스트 시나리오 및 전수 검증

`tests/test_e2e_steel_beam_column.py`를 통해 프론트엔드와 백엔드 간의 완전한 상호작용을 자동화 검증합니다:

### 시나리오 1: H형강 보 순수 휨 및 LTB 검토 (3대 액션 버튼 파이프라인)
1. 부재 선택: `steel_beam_column`, 단면 `H-400x200x8x13`, $SM355$.
2. 하중 입력: $P_u = 0$, $M_{ux} = 250\,\text{kN}\cdot\text{m}$, $V_u = 100\,\text{kN}$.
3. 지지 조건: $L = 6.0\,\text{m}$, $L_b = 2.0\,\text{m} \le L_p$.
4. 검증:
   - 폼 입력 시 캔버스 단면도 즉시 동기화되되 계산서는 갱신 대기 확인.
   - `[⚡ 검토]` 클릭 시 플랜지/웨브 조밀 판정 확인 (`COMPACT`), $M_n = M_p = 456.5\,\text{kN}\cdot\text{m}$, $\phi_b M_n = 410.9\,\text{kN}\cdot\text{m}$.
   - $\text{DCR} = 250 / 410.9 = 0.608 \le 1.0$ (`OK`).
   - A4 계산서 3장에 수식 정확 표출 및 총 검토 시간 $\le 100\text{ms}$.
   - `[✨ 자동설계]` 클릭 시 현재 모멘트에 적합한 최적 H형강 단면 자동 탐색 및 주입 확인.

### 시나리오 2: H형강 기둥 압축-휨 P-M 조합력 및 테마 전환 검증
1. 부재 선택: `steel_beam_column`, 단면 `H-350x350x12x19`, $SM355$.
2. 하중 입력: $P_u = 2,000\,\text{kN}$, $M_{ux} = 150\,\text{kN}\cdot\text{m}$, $M_{uy} = 30\,\text{kN}\cdot\text{m}$.
3. 지지 조건: $L = 4.0\,\text{m}$, $K_x = K_y = 1.0$.
4. `[⚡ 검토]` 클릭:
   - $P_u / \phi_c P_n \ge 0.20$ 판정 및 KDS 14 31 10 식 4.5-1 적용 확인.
   - P-M DCR 산출 및 Pane 1 요약 그리드에 녹색 O.K 표출.
5. 다크/라이트 테마 전환 시 폼/테이블 배경 및 글자색 반전 무결성 확인.

### 시나리오 3: 다중 부재 관리 및 서브탭 래핑 검증
1. Pane 1에서 `[+ 부재 추가]` 클릭 $\rightarrow$ `2F-SC1` 인스턴스 생성.
2. 부재 전환 시 즉시 폼/캔버스 동기화 확인.
3. Left-Sub 패널 폭 축소 시 상부 서브탭 버튼이 잘리지 않고 줄바꿈 래핑(`flex-wrap: wrap;`)되는지 확인.

---

## 5. 브라우저 콘솔 무결성 검수 (Console Error 0건)

- UI 로드 시 및 탭 전환, 모달 호출, 계산 실행 중 브라우저 콘솔 에러(`Uncaught TypeError`, `404 Not Found` 등) 0건 엄수.
- 단위계 전환(SI $\leftrightarrow$ MKS) 시 단면 치수(mm $\leftrightarrow$ cm) 및 하중(kN $\leftrightarrow$ tonf) 환산 정상 작동 확인.

---

## 6. DoD 검증 및 수용 기준 (Acceptance Criteria)

- [ ] 폼 입력 시 캔버스 동기화 및 `[⚡ 검토]` 클릭 시 100ms 이내 계산서/DCR 갱신 확인.
- [ ] 원본앱 3대 액션 버튼(`[💾적용] [⚡검토] [✨자동설계]`) 파이프라인 검증.
- [ ] 상부 서브탭 반응형 래핑 및 다크/라이트 테마 무결성 검증.
- [ ] `catalog.js`에서 `steel_beam_column`의 `is_wip: false` 전환 확인.
- [ ] E2E 통합 테스트 `pytest tests/test_e2e_steel_beam_column.py` 100% PASS.
- [ ] 브라우저 콘솔 에러 0건 확인.
- [ ] `docs/16`에 따른 4대 물리적 증거 첨부 및 1단위 Git 커밋/푸시 완료.
