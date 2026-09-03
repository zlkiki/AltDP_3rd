# [요구사항19] AltDP_2nd UI/UX 전면 이식 및 전 엔지니어링 기능 완전 연동

## 1. 개요 및 배경
* **목적**: AltDP_3rd에 구축된 KDS 최고 정밀도의 엔지니어링 엔진(RC, 철골, 2D FEM, 3D P-M, KDS 3대 계산서, DXF CAD 도면, 물량산출, MIDAS Gen 연동 등)을 검증된 **AltDP_2nd의 Zero-Build 4분할 올인원 워크스페이스(스마트 사이드바 + 다중 부재 관리자 + 동적 폼 + 2D 단면/배근 캔버스 + A4 순백색 KDS 계산서)**로 전면 이식 및 100% 심리스하게 직결합니다.
* **핵심 지향점**:
  1. **Zero-Build 포터빌리티**: npm/webpack 없이 순수 Vanilla JS + CSS 기반 초경량/초고속 브라우저 구동.
  2. **독립 4분할 레이아웃 완벽 이식**: `layout_resizer.js` 기반 4대 영역 상호 간섭 없는 리사이징.
  3. **순백색 A4 계산서 가독성 100% 보장**: 다크 테마에서도 계산서는 `#ffffff` 용지 유지, 50%~200% 줌 및 `Ctrl+Wheel` 줌, A4 원클릭 인쇄.
  4. **3버튼 단일화 파이프라인**: [💾 적용], [⚡ 검토], [✨ 설계] 파이프라인으로 2D 단면도 즉시 반응 및 비실시간 안정적 KDS 계산.
  5. **AltDP_3rd 고유 엔지니어링 자산 100% 융합**: 54개 모듈 체계와 더불어 FEM 판휨/지반, 3D P-M 차트, CAD DXF, 물량산출, Gen 연동 모달을 유기적으로 결합.

---

## 2. 하위 Phase 분할 및 단계별 실행 로드맵 (5대 Phase)

컨텍스트 폭주 방지 및 품질 무결성을 위해 5개 하위 Phase로 분할하여 순차 실행합니다:

| 하위 Phase | 문서명 | 핵심 작업 내용 | 주요 타겟 파일 |
|---|---|---|---|
| **Phase 19-1** | [`요구사항19-1_AltDP_2nd_ZeroBuild_4분할_UI_UX_프레임워크_이식.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항19-1_AltDP_2nd_ZeroBuild_4분할_UI_UX_프레임워크_이식.md) | 4-Pane 레이아웃, 6대 CSS, 리사이저, 테마, 단위계, 중앙 스토어, 부재관리자 이식 | `src/web/templates/index.html`, `static/css/*.css`, `static/js/components/*.js`, `static/js/store/*.js` |
| **Phase 19-2** | [`요구사항19-2_단위부재_스키마_및_동적_폼_KS_DB_컴포넌트_연동.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항19-2_단위부재_스키마_및_동적_폼_KS_DB_컴포넌트_연동.md) | 동적 폼 빌더, KS 콤보박스, KS 규격 DB, 자동설계기, 백엔드 스키마 API 연동 | `static/js/components/form_*.js`, `static/js/db/*.js`, `static/js/designer/*.js`, `src/api/routes/schema.py` |
| **Phase 19-3** | [`요구사항19-3_2D_캔버스_및_KDS_계산서_리포트_렌더러_이식.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항19-3_2D_캔버스_및_KDS_계산서_리포트_렌더러_이식.md) | 2D Canvas & Vector SVG 렌더러군, A4 KDS 계산서 렌더러군, 줌 컨트롤러 이식 | `static/js/visual/`, `static/js/report/`, `static/js/report/redcr/` |
| **Phase 19-4** | [`요구사항19-4_AltDP_3rd_엔진_REST_API_디스패처_전수_연결_및_검증.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항19-4_AltDP_3rd_엔진_REST_API_디스패처_전수_연결_및_검증.md) | `/api/design/{cat}/{grp}/{mod}` 동적 디스패처 구축 및 AltDP_3rd 엔진(RC, Steel, Special) 전수 직결 | `src/api/routes/dispatch.py`, `src/api/server.py`, `tests/api/test_dispatch_api.py` |
| **Phase 19-5** | [`요구사항19-5_고급_특화기능(FEM_도면CAD_물량_PBD_Gen)_UI_연동_완성.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항19-5_고급_특화기능(FEM_도면CAD_물량_PBD_Gen)_UI_연동_완성.md) | 2D FEM 등고선, 3D P-M 곡면, CAD DXF 내보내기, 물량산출 대시보드, MIDAS Gen 연동 UI 통합 | `static/js/app.js`, `src/web/templates/index.html`, `tests/ui/` |

---

## 3. 핵심 아키텍처 및 연동 흐름 (Architecture Flow)

```
[사용자 브라우저 (Zero-Build 4-Split UI)]
  │
  ├── 1. 탐색기 (Sidebar) ──> 모듈 선택 (RC/Steel/PC/Misc 54종) + MIDAS Gen MGT 임포트
  ├── 2. 부재 관리 & 입력 ──> [M-1, M-2] CRUD + Dynamic Form + KS DB 콤보박스
  │       │
  │       ├── 실시간 변경 (50ms 디바운스) ──> Pane 3: 2D Canvas / Vector SVG 즉각 갱신
  │       └── [⚡ 검토] / [✨ 설계] 클릭 ──> Backend API 호출
  │
[백엔드 서버 (FastAPI 단일 포트 :8000)]
  │
  ├── GET /api/modules ────────────> 54개 모듈 메타데이터 반환
  ├── GET /api/schema/{c}/{g}/{m} ──> Pydantic 스키마 및 단위 제약 반환
  ├── POST /api/design/{c}/{g}/{m} ─> AltDP_3rd 고정밀 엔진 디스패칭
  │       │
  │       ├── RC 엔진 (보/기둥/벽체/슬래브/기초/옹벽)
  │       ├── Steel 엔진 (보/기둥/가새/개구부/접합부/베이스플레이트)
  │       ├── Special/SRC/알루미늄/보수보강 엔진
  │       └── 2D FEM 솔버 (매트기초/지하외벽/슬래브/접촉)
  │
  └── 응답 (결과 JSON) ───────────> Pane 4: A4 순백색 KDS 계산서 렌더링 + DCR 상태 배지
```

---

## 4. 완료 검증 기준 (Definition of Done)
1. **Zero-Build 단일 실행**: `.\run.ps1` 실행 시 에러 없이 단일 포트에서 완벽 구동.
2. **독립 4분할 레이아웃 작동**: 4개 리사이저 바 드래그 시 패널 간 왜곡 없이 부드러운 독립 리사이징 보장.
3. **54종 모듈 탐색 & 스키마 폼 로드**: RC, Steel, PC, Misc 모듈 선택 시 해당 폼 필드와 초기값이 정확히 렌더링.
4. **2D Canvas 실시간 단면도**: 폼 입력 변경 시 0.05초 이내에 2D 단면 및 배근도가 실시간 반응.
5. **KDS 계산서 & A4 출력 무결성**: 검토 버튼 클릭 시 결과 요약, 수식 유도, Step-by-Step 상세 계산서가 순백색 시트에 정상 표출되며 브라우저 인쇄 시 여백/양식 100% 호환.
6. **AltDP_3rd 고급 엔진 연동**: FEM 등고선, 3D P-M 곡선, CAD DXF 다운로드, 물량산출 대시보드가 UI에서 에러 없이 원클릭 작동.
7. **테스트 100% 통과**: 기존 243개 pytest 및 신규 UI/디스패처 테스트 전체 Pass.

---

## 5. 소스 재활용 및 토큰 효율화 행동 수칙 (Source Reuse & Token Efficiency)

* **AltDP_2nd 검증 소스 100% 직접 재활용 (Direct Asset Reuse)**:
  - 검증 완료된 `AltDP_2nd/web/`의 HTML, 6대 모듈러 CSS(`theme.css`, `layout.css`, `components.css`, `canvas.css`, `report.css`, `print.css`), JS 컴포넌트(`layout_resizer.js`, `member_manager.js`, `form_generator.js`, `form_combobox.js`, `auto_designer.js`), KS DB(`ks_sections.js`, `rebar_db.js`, `ks_bolt_db.js`), 2D 시각화(`canvas_renderer.js`, `vector_*.js`), KDS 계산서 렌더러(`redcr_common_renderer.js`, `redcr/*.js`), `app.js`는 처음부터 재작성하지 않고 **AltDP_2nd의 완성된 소스를 그대로 복사/가져와 이식**합니다.
* **토큰 소비 극소화 & 작업 정확성 극대화**:
  - 이미 수작업 검증 및 실무 디버깅이 끝난 프론트엔드 자산을 그대로 활용함으로써 **불필요한 LLM 코드 생성 토큰 낭비를 원천 차단**합니다.
  - 프론트엔드 UI를 빠르게 정착시킨 후, **AltDP_3rd의 백엔드 디스패처(`/api/design/...`, `/api/modules`, `/api/schema/...`) 및 고유 엔지니어링 엔진(RC, Steel, FEM 등)과의 정확한 데이터 인터페이스 바인딩에 집중**합니다.
