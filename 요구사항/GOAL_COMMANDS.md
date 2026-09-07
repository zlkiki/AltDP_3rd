# AltDP_3rd 마스터 /goal 명령문 모음집 (GOAL_COMMANDS.md)

대기 중인 전수 요구사항(Phase 20 ~ 26)을 즉시 실행하기 위한 원클릭 `/goal` 명령문 인덱스입니다.

> **💡 권장 모델 가이드 ([docs/16](file:///f:/PyProject/AltDP_3rd/docs/16_goal_micro_execution_protocol.md) 연동)**
> * 🧠 **High** (Gemini Pro, Claude Sonnet, GPT-4.5 등): 공학 수식, KDS 계산 엔진, KaTeX 전개식, 엄밀한 TDD (오차 $\le 0.10\%$)
> * ⚙️ **Medium** (Gemini Flash, Claude Haiku 등): HTML/JS 입력폼, DOM UI 조작, Canvas 드로잉, E2E 이벤트 연결 및 검증

---

## 1. Phase 20: 더미코드 제거 및 WIP 베이스라인

| Phase | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **20-1** | 🧠 **High** | [백엔드 더미연산 제거 및 WIP 디스패처](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-1_Phase20-1_백엔드_더미연산_제거_및_WIP_디스패처_구축.md) | `/goal docs 16 확인하고 요구사항 20과 20-1을 구현해줘` |
| **20-2** | ⚙️ **Medium** | [원본앱 61종 3단계 티어 메타 전수 주입](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-2_Phase20-2_원본앱_61종_3단계_티어_메타_전수_주입.md) | `/goal docs 16 확인하고 요구사항 20과 20-2를 구현해줘` |
| **20-3** | ⚙️ **Medium** | [프론트엔드 입력부 WIP 안내카드/폼방어](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-3_Phase20-3_프론트엔드_입력부_WIP_안내카드_및_폼_방어.md) | `/goal docs 16 확인하고 요구사항 20과 20-3을 구현해줘` |
| **20-4** | 🧠 **High** | [2D캔버스 WIP 및 A4 계산서 하드코딩 청산](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-4_Phase20-4_2D_VDraw_캔버스_WIP_및_A4_계산서_하드코딩_청산.md) | `/goal docs 16 확인하고 요구사항 20과 20-4를 구현해줘` |
| **20-5** | ⚙️ **Medium** | [4열 통합 E2E 검증 및 콘솔에러 0건](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-5_Phase20-5_4열_통합_E2E_검증_및_콘솔에러_0건_검수창구_확립.md) | `/goal docs 16 확인하고 요구사항 20과 20-5를 구현해줘` |

---

## 2. Phase 21: DOCS 07 4-Pane 워크스페이스 레이아웃 & UI/UX

| Phase | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **21-1** | ⚙️ **Medium** | [4-Pane 레이아웃 및 4대 독립 리사이저](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-1_Phase21-1_DOCS07_4Pane_워크스페이스_레이아웃_및_4대_독립_리사이저.md) | `/goal docs 16 확인하고 요구사항 21과 21-1을 구현해줘` |
| **21-2** | ⚙️ **Medium** | [스마트 계층형 모듈 탐색기 및 즐겨찾기](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-2_Phase21-2_스마트_계층형_모듈_탐색기_사이드바_및_즐겨찾기_시스템.md) | `/goal docs 16 확인하고 요구사항 21과 21-2를 구현해줘` |
| **21-3** | ⚙️ **Medium** | [다중 부재 매니저 Pane1 & 입력폼 Pane2](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-3_Phase21-3_다중_부재_매니저_Pane1_및_파라메트릭_입력폼_Pane2_고도화.md) | `/goal docs 16 확인하고 요구사항 21과 21-3을 구현해줘` |
| **21-4** | ⚙️ **Medium** | [세로 적층형 다중 뷰포트 정보부 Pane3](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-4_Phase21-4_세로_적층형_다중_뷰포트_그래픽_정보부_Pane3_구축.md) | `/goal docs 16 확인하고 요구사항 21과 21-4를 구현해줘` |
| **21-5** | 🧠 **High** | [순백색 A4 KDS 표준 구조계산서 Pane4](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-5_Phase21-5_원본_출력모듈_1대1_계승_KDS_표준_구조계산서_Pane4_엔진.md) | `/goal docs 16 확인하고 요구사항 21과 21-5를 구현해줘` |
| **21-6** | 🧠 **High** | [모듈팩 디스패처 및 5대 플래그십 E2E](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-6_Phase21-6_부재별_다형적_모듈팩_디스패처_및_5대_플래그십_4열_E2E_통합.md) | `/goal docs 16 확인하고 요구사항 21과 21-6을 구현해줘` |

---

## 3. Phase 22: RC 보 (`rc_beam`) 수직관통 E2E

| Step | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **22-1** | 🧠 **High** | [Step 1: RC보 KDS 계산엔진 & Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md) | `/goal docs 16 확인하고 요구사항 22와 22-1을 구현해줘` |
| **22-2** | ⚙️ **Medium** | [Step 2: RC보 원본 1:1 서브탭 폼 & 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md) | `/goal docs 16 확인하고 요구사항 22와 22-2를 구현해줘` |
| **22-3** | ⚙️ **Medium** | [Step 3: RC보 2D VDraw 캔버스 배근도/부재력](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md) | `/goal docs 16 확인하고 요구사항 22와 22-3을 구현해줘` |
| **22-4** | 🧠 **High** | [Step 4: RC보 순백색 A4 8단계 KaTeX 계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md) | `/goal docs 16 확인하고 요구사항 22와 22-4를 구현해줘` |
| **22-5** | ⚙️ **Medium** | [Step 5: RC보 4열 통합 E2E 및 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-5_PhaseV1_01_Step5_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md) | `/goal docs 16 확인하고 요구사항 22와 22-5를 구현해줘` |

---

## 4. Phase 23: RC 기둥 (`rc_column`) 수직관통 E2E

| Step | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **23-1** | 🧠 **High** | [Step 1: RC기둥 KDS 계산엔진 & 파이버 PM 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-1_PhaseV1_02_Step1_RC기둥_KDS계산엔진_및_파이버PM_Pydantic스키마.md) | `/goal docs 16 확인하고 요구사항 23과 23-1을 구현해줘` |
| **23-2** | ⚙️ **Medium** | [Step 2: RC기둥 원본 1:1 서브탭 폼 & 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-2_PhaseV1_02_Step2_RC기둥_원본앱_1대1_서브탭_입력폼_및_모달.md) | `/goal docs 16 확인하고 요구사항 23과 23-2를 구현해줘` |
| **23-3** | ⚙️ **Medium** | [Step 3: RC기둥 2D VDraw 배근도/PM곡선 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-3_PhaseV1_02_Step3_RC기둥_2D_VDraw_캔버스_배근도_및_PM곡선_인터랙션.md) | `/goal docs 16 확인하고 요구사항 23과 23-3을 구현해줘` |
| **23-4** | 🧠 **High** | [Step 4: RC기둥 순백색 A4 8단계 KaTeX 계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-4_PhaseV1_02_Step4_RC기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md) | `/goal docs 16 확인하고 요구사항 23과 23-4를 구현해줘` |
| **23-5** | ⚙️ **Medium** | [Step 5: RC기둥 4열 통합 E2E 및 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-5_PhaseV1_02_Step5_RC기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md) | `/goal docs 16 확인하고 요구사항 23과 23-5를 구현해줘` |

---

## 5. Phase 24: RC 전단벽 (`rc_shear_wall`) 수직관통 E2E

| Step | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **24-1** | 🧠 **High** | [Step 1: RC전단벽 KDS 계산엔진 & 경계요소 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-1_PhaseV1_03_Step1_RC전단벽_KDS계산엔진_및_경계요소_Pydantic스키마.md) | `/goal docs 16 확인하고 요구사항 24와 24-1을 구현해줘` |
| **24-2** | ⚙️ **Medium** | [Step 2: RC전단벽 원본 1:1 서브탭 폼 & 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-2_PhaseV1_03_Step2_RC전단벽_원본앱_1대1_서브탭_입력폼_및_모달.md) | `/goal docs 16 확인하고 요구사항 24와 24-2를 구현해줘` |
| **24-3** | ⚙️ **Medium** | [Step 3: RC전단벽 2D VDraw 배근도/경계요소 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-3_PhaseV1_03_Step3_RC전단벽_2D_VDraw_캔버스_배근도_및_경계요소_인터랙션.md) | `/goal docs 16 확인하고 요구사항 24와 24-3을 구현해줘` |
| **24-4** | 🧠 **High** | [Step 4: RC전단벽 순백색 A4 8단계 KaTeX 계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-4_PhaseV1_03_Step4_RC전단벽_A4_5대장구분_8단계_KaTeX_구조계산서.md) | `/goal docs 16 확인하고 요구사항 24와 24-4를 구현해줘` |
| **24-5** | ⚙️ **Medium** | [Step 5: RC전단벽 4열 통합 E2E 및 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-5_PhaseV1_03_Step5_RC전단벽_4열통합_E2E검증_및_실사용UI_온라인전환.md) | `/goal docs 16 확인하고 요구사항 24와 24-5를 구현해줘` |

---

## 6. Phase 25: 철골 보/기둥 (`steel_beam_column`) 수직관통 E2E

| Step | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **25-1** | 🧠 **High** | [Step 1: 철골보기둥 KDS 계산엔진 & Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md) | `/goal docs 16 확인하고 요구사항 25와 25-1을 구현해줘` |
| **25-2** | ⚙️ **Medium** | [Step 2: 철골보기둥 원본 1:1 서브탭 폼 & 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md) | `/goal docs 16 확인하고 요구사항 25와 25-2를 구현해줘` |
| **25-3** | ⚙️ **Medium** | [Step 3: 철골보기둥 2D VDraw 단면도/부재력도 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md) | `/goal docs 16 확인하고 요구사항 25와 25-3을 구현해줘` |
| **25-4** | 🧠 **High** | [Step 4: 철골보기둥 순백색 A4 8단계 KaTeX 계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md) | `/goal docs 16 확인하고 요구사항 25와 25-4를 구현해줘` |
| **25-5** | ⚙️ **Medium** | [Step 5: 철골보기둥 4열 통합 E2E 및 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md) | `/goal docs 16 확인하고 요구사항 25와 25-5를 구현해줘` |

---

## 7. Phase 26: 철골 주각부 (`steel_baseplate`) 수직관통 E2E

| Step | 권장 모델 | 대상 명세서 | 실행 명령문 (복사용) |
|:---:|:---:|---|---|
| **26-1** | 🧠 **High** | [Step 1: 철골주각부 KDS 계산엔진 & Pydantic 스키마](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md) | `/goal docs 16 확인하고 요구사항 26과 26-1을 구현해줘` |
| **26-2** | ⚙️ **Medium** | [Step 2: 철골주각부 원본 1:1 서브탭 폼 & 모달](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md) | `/goal docs 16 확인하고 요구사항 26과 26-2를 구현해줘` |
| **26-3** | ⚙️ **Medium** | [Step 3: 철골주각부 2D VDraw 상세도/지압응력 인터랙션](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md) | `/goal docs 16 확인하고 요구사항 26과 26-3을 구현해줘` |
| **26-4** | 🧠 **High** | [Step 4: 철골주각부 순백색 A4 8단계 KaTeX 계산서](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md) | `/goal docs 16 확인하고 요구사항 26과 26-4를 구현해줘` |
| **26-5** | ⚙️ **Medium** | [Step 5: 철골주각부 4열 통합 E2E 및 온라인 전환](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md) | `/goal docs 16 확인하고 요구사항 26과 26-5를 구현해줘` |
