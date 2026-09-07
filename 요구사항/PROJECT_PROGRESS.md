# AltDP_3rd 프로젝트 진행 현황 (PROJECT_PROGRESS.md)

> **[SSOT] 외부 기억 진행 추적표**  
> 세션 재시작 및 AI 모델 교체 시 현황을 즉시 복원하기 위한 상태 추적 문서입니다.  
> 세부 개발 프로토콜 및 UI/UX 규약은 [`AGENTS.md`](file:///f:/PyProject/AltDP_3rd/.agents/AGENTS.md), [`docs/16`](file:///f:/PyProject/AltDP_3rd/docs/16_goal_micro_execution_protocol.md), [`docs/07`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)을 참조합니다.

---

## 1. 현재 시스템 스냅샷 (Snapshot)

* **최종 갱신**: `2026-09-07T17:19:00+09:00`
* **최신 커밋**: `8c6fa86`
* **회귀 테스트**: **`pytest` 263 / 263 PASS (100% 통과, 0 Failures)**
* **차기 즉시 작업**: **`Phase 20-1`** (권장 모델: 🧠 **High**) ([`요구사항20-1`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-1_Phase20-1_백엔드_더미연산_제거_및_WIP_디스패처_구축.md))
* **실행 프롬프트**: `/goal docs 16 확인하고 요구사항 20과 20-1을 구현해줘` (전체 목록: [`GOAL_COMMANDS.md`](file:///f:/PyProject/AltDP_3rd/요구사항/GOAL_COMMANDS.md))

---

## 2. 요구사항 진행 현황 매트릭스 (Progress Matrix)

### 2.1. 기완료 아카이빙 ([`요구사항/@@OLD/`](file:///f:/PyProject/AltDP_3rd/요구사항/@@OLD/))
* [x] **요구사항 01~19**: 역공학 파이프라인, 단면DB, 기본 5대부재 엔진, P-M/FEM 솔버, 계산서, 3D골조, CAD 도면
* [x] **요구사항 27 (Phase 27-1 ~ 27-4)**: 단면DB 자체자산화, `paths.py`, `FrameModel3D`, 소스 순수화 및 외부참조 0건 검증 완료

---

### 2.2. 현재 활성 대기 요구사항 (Active Backlog)

#### [Phase 20] 더미코드 전면 제거 및 WIP 베이스라인 구축 ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md))
* [ ] **20-1**: [백엔드 더미연산 제거 및 WIP 디스패처 구축](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-1_Phase20-1_백엔드_더미연산_제거_및_WIP_디스패처_구축.md)
* [ ] **20-2**: [원본앱 61종 3단계 티어 메타 전수 주입](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-2_Phase20-2_원본앱_61종_3단계_티어_메타_전수_주입.md)
* [ ] **20-3**: [프론트엔드 입력부 WIP 안내카드 및 폼 방어](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-3_Phase20-3_프론트엔드_입력부_WIP_안내카드_및_폼_방어.md)
* [ ] **20-4**: [2D VDraw 캔버스 WIP 및 A4 계산서 하드코딩 청산 (redcr_common 제거)](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-4_Phase20-4_2D_VDraw_캔버스_WIP_및_A4_계산서_하드코딩_청산.md)
* [ ] **20-5**: [4열 통합 E2E 검증 및 콘솔에러 0건 검수창구 확립](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-5_Phase20-5_4열_통합_E2E_검증_및_콘솔에러_0건_검수창구_확립.md)

#### [Phase 21] DOCS 07 4-Pane 워크스페이스 레이아웃 & UI/UX ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md))
* [ ] **21-1**: [4-Pane 워크스페이스 레이아웃 및 4대 독립 리사이저](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-1_Phase21-1_DOCS07_4Pane_워크스페이스_레이아웃_및_4대_독립_리사이저.md)
* [ ] **21-2**: [스마트 계층형 모듈 탐색기 사이드바 및 즐겨찾기 시스템](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-2_Phase21-2_스마트_계층형_모듈_탐색기_사이드바_및_즐겨찾기_시스템.md)
* [ ] **21-3**: [다중 부재 매니저 Pane1 및 파라메트릭 입력폼 Pane2 고도화](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-3_Phase21-3_다중_부재_매니저_Pane1_및_파라메트릭_입력폼_Pane2_고도화.md)
* [ ] **21-4**: [세로 적층형 다중 뷰포트 그래픽 정보부 Pane3 구축](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-4_Phase21-4_세로_적층형_다중_뷰포트_그래픽_정보부_Pane3_구축.md)
* [ ] **21-5**: [원본 출력모듈 1:1 계승 KDS 표준 구조계산서 Pane4 엔진](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-5_Phase21-5_원본_출력모듈_1대1_계승_KDS_표준_구조계산서_Pane4_엔진.md)
* [ ] **21-6**: [부재별 다형적 모듈팩 디스패처 및 5대 플래그십 4열 E2E 통합](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-6_Phase21-6_부재별_다형적_모듈팩_디스패처_및_5대_플래그십_4열_E2E_통합.md)

#### [Phase 22] RC 보 (`rc_beam`) 수직관통 E2E ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22_PhaseV1_01_RC보_rc_beam_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md))
* [ ] **22-1 (Step 1)**: [RC보 KDS 계산엔진 및 Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md)
* [ ] **22-2 (Step 2)**: [RC보 원본앱 1:1 서브탭 입력폼 및 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md)
* [ ] **22-3 (Step 3)**: [RC보 2D VDraw 캔버스 배근도 및 부재력도 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md)
* [ ] **22-4 (Step 4)**: [RC보 A4 5대장구분 8단계 KaTeX 구조계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* [ ] **22-5 (Step 5)**: [RC보 4열통합 E2E 검증 및 실사용 UI 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-5_PhaseV1_01_Step5_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md)

#### [Phase 23] RC 기둥 (`rc_column`) 수직관통 E2E ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23_PhaseV1_02_RC기둥_rc_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md))
* [ ] **23-1 (Step 1)**: [RC기둥 KDS 계산엔진 및 파이버 PM 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-1_PhaseV1_02_Step1_RC기둥_KDS계산엔진_및_파이버PM_Pydantic스키마.md)
* [ ] **23-2 (Step 2)**: [RC기둥 원본앱 1:1 서브탭 입력폼 및 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-2_PhaseV1_02_Step2_RC기둥_원본앱_1대1_서브탭_입력폼_및_모달.md)
* [ ] **23-3 (Step 3)**: [RC기둥 2D VDraw 캔버스 배근도 및 PM 곡선 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-3_PhaseV1_02_Step3_RC기둥_2D_VDraw_캔버스_배근도_및_PM곡선_인터랙션.md)
* [ ] **23-4 (Step 4)**: [RC기둥 A4 5대장구분 8단계 KaTeX 구조계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-4_PhaseV1_02_Step4_RC기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* [ ] **23-5 (Step 5)**: [RC기둥 4열통합 E2E 검증 및 실사용 UI 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-5_PhaseV1_02_Step5_RC기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md)

#### [Phase 24] RC 전단벽 (`rc_shear_wall`) 수직관통 E2E ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24_PhaseV1_03_RC전단벽_rc_shear_wall_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md))
* [ ] **24-1 (Step 1)**: [RC전단벽 KDS 계산엔진 및 경계요소 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-1_PhaseV1_03_Step1_RC전단벽_KDS계산엔진_및_경계요소_Pydantic스키마.md)
* [ ] **24-2 (Step 2)**: [RC전단벽 원본앱 1:1 서브탭 입력폼 및 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-2_PhaseV1_03_Step2_RC전단벽_원본앱_1대1_서브탭_입력폼_및_모달.md)
* [ ] **24-3 (Step 3)**: [RC전단벽 2D VDraw 캔버스 배근도 및 경계요소 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-3_PhaseV1_03_Step3_RC전단벽_2D_VDraw_캔버스_배근도_및_경계요소_인터랙션.md)
* [ ] **24-4 (Step 4)**: [RC전단벽 A4 5대장구분 8단계 KaTeX 구조계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-4_PhaseV1_03_Step4_RC전단벽_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* [ ] **24-5 (Step 5)**: [RC전단벽 4열통합 E2E 검증 및 실사용 UI 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-5_PhaseV1_03_Step5_RC전단벽_4열통합_E2E검증_및_실사용UI_온라인전환.md)

#### [Phase 25] 철골 보/기둥 (`steel_beam_column`) 수직관통 E2E ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25_PhaseV1_04_철골보기둥_steel_beam_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md))
* [ ] **25-1 (Step 1)**: [철골보기둥 KDS 계산엔진 및 Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md)
* [ ] **25-2 (Step 2)**: [철골보기둥 원본앱 1:1 서브탭 입력폼 및 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md)
* [ ] **25-3 (Step 3)**: [철골보기둥 2D VDraw 캔버스 단면도 및 부재력도 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md)
* [ ] **25-4 (Step 4)**: [철골보기둥 A4 5대장구분 8단계 KaTeX 구조계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* [ ] **25-5 (Step 5)**: [철골보기둥 4열통합 E2E 검증 및 실사용 UI 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md)

#### [Phase 26] 철골 주각부 (`steel_baseplate`) 수직관통 E2E ([마스터](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26_PhaseV1_05_철골주각부_steel_baseplate_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md))
* [ ] **26-1 (Step 1)**: [철골주각부 KDS 계산엔진 및 Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md)
* [ ] **26-2 (Step 2)**: [철골주각부 원본앱 1:1 서브탭 입력폼 및 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md)
* [ ] **26-3 (Step 3)**: [철골주각부 2D VDraw 캔버스 상세도 및 지압응력 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md)
* [ ] **26-4 (Step 4)**: [철골주각부 A4 5대장구분 8단계 KaTeX 구조계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* [ ] **26-5 (Step 5)**: [철골주각부 4열통합 E2E 검증 및 실사용 UI 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md)

---

## 3. 외부 기억 동기화 규칙

1. **단위 작업 완료 즉시**: 작업한 Phase/Step의 `[ ]`를 `[x]`로 변경하고 최신 커밋 해시를 갱신합니다.
2. **커밋 동봉**: 본 문서 갱신 내역은 해당 구현 커밋 또는 직후 문서 커밋으로 원격 저장소에 푸시합니다.
