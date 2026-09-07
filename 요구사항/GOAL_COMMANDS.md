# AltDP_3rd 마스터 /goal 명령문 모음집 (GOAL_COMMANDS.md)

본 문서는 사용자가 구현 작업을 진행할 때 복사하여 채팅창에 즉시 입력할 수 있도록, **대기 중인 전수 요구사항(Phase 20 ~ 26)의 최적화된 `/goal` 슬래시 커맨드**를 집대성한 공식 인덱스 가이드입니다.

> [!TIP]
> **💡 `/goal` 실행 규약 (AGENTS.md 제7절 연동)**
> * 단일 컨텍스트 폭주 및 모델의 조기 탈진을 방지하기 위해, 모든 프롬프트는 **"마스터 요구사항 + 하위 세부 Phase(또는 Step)"** 단위로 정밀하게 분할되어 있습니다.
> * 하나의 하위 Phase가 완료되면 `pytest` 100% 통과, 4대 증거 제출, Git 커밋 및 푸시가 자동으로 완수되므로, 사용자는 다음 순번의 커맨드를 복사하여 순차적으로 실행하시면 됩니다.
> * 작업 완료 시 [`docs/PROJECT_PROGRESS.md`](file:///f:/PyProject/AltDP_3rd/docs/PROJECT_PROGRESS.md) 외부 기억 파일이 자동으로 동기화됩니다.

---

## 🗺️ 전체 추천 실행 로드맵 (Recommended Roadmap)

```
[Phase 20: 더미코드 제거 & WIP 베이스라인 (20-1 ~ 20-5)]
                    ▼
[Phase 21: DOCS 07 4-Pane UI/UX 프레임워크 (21-1 ~ 21-6)]
                    ▼
[Phase 22: Tier 1 No.1 RC 보 수직관통 (22-1 ~ 22-5)]
                    ▼
[Phase 23: Tier 1 No.2 RC 기둥 수직관통 (23-1 ~ 23-5)]
                    ▼
[Phase 24: Tier 1 No.3 RC 전단벽 수직관통 (24-1 ~ 24-5)]
                    ▼
[Phase 25: Tier 1 No.4 철골 보/기둥 수직관통 (25-1 ~ 25-5)]
                    ▼
[Phase 26: Tier 1 No.5 철골 주각부 수직관통 (26-1 ~ 26-5)]
```

---

## 1. Phase 20: 더미코드 전면 제거 및 정직한 WIP 베이스라인 구축

> **목표**: 시스템 내 잠재된 가짜 연산(Mock/Stub 강도치 150/100, 임의 OK 판정), 레거시 카드 뷰어(`redcr_common_renderer.js`)를 전면 청산하고 61종 모듈 3단계 티어 메타 주입 및 순백색 A4 WIP 시트 확립.  
> **마스터 명세**: [`요구사항/요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md)

### [20-1] 백엔드 더미연산 제거 및 WIP 디스패처 구축
```text
/goal docs 16 확인하고 요구사항 20과 20-1을 구현해줘
```
* **명세서**: [`요구사항20-1_Phase20-1_백엔드_더미연산_제거_및_WIP_디스패처_구축.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-1_Phase20-1_백엔드_더미연산_제거_및_WIP_디스패처_구축.md)
* **내용**: 백엔드 가짜 강도치/더미 연산 전면 삭제, `NOT_YET_IMPLEMENTED`/`WIP_MODULE` 표준 JSON 응답 구축.

### [20-2] 원본앱 61종 3단계 티어 메타 전수 주입
```text
/goal docs 16 확인하고 요구사항 20과 20-2를 구현해줘
```
* **명세서**: [`요구사항20-2_Phase20-2_원본앱_61종_3단계_티어_메타_전수_주입.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-2_Phase20-2_원본앱_61종_3단계_티어_메타_전수_주입.md)
* **내용**: `docs/04` 기반 61종 전수 모듈에 `tier` (Tier 1: 9종, Tier 2: 26종, Tier 3: 26종), `is_wip`, `original_dlg_id` 메타 주입.

### [20-3] 프론트엔드 입력부 WIP 안내카드 및 폼 방어
```text
/goal docs 16 확인하고 요구사항 20과 20-3을 구현해줘
```
* **명세서**: [`요구사항20-3_Phase20-3_프론트엔드_입력부_WIP_안내카드_및_폼_방어.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-3_Phase20-3_프론트엔드_입력부_WIP_안내카드_및_폼_방어.md)
* **내용**: 미구현 부재 선택 시 기만적 입력폼 대신 원본 DLG 정보와 KDS 기준이 안내되는 표준 WIP 안내 카드 렌더링.

### [20-4] 2D VDraw 캔버스 WIP 및 A4 계산서 하드코딩 청산
```text
/goal docs 16 확인하고 요구사항 20과 20-4를 구현해줘
```
* **명세서**: [`요구사항20-4_Phase20-4_2D_VDraw_캔버스_WIP_및_A4_계산서_하드코딩_청산.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-4_Phase20-4_2D_VDraw_캔버스_WIP_및_A4_계산서_하드코딩_청산.md)
* **내용**: 레거시 4-Pillar 카드형 뷰어(`redcr_common_renderer.js`) 완전 제거, 2D 캔버스 WIP 플레이스홀더 및 5대 장구분 순백색 A4 WIP 시트 일원화.

### [20-5] 4열 통합 E2E 검증 및 콘솔에러 0건 검수창구 확립
```text
/goal docs 16 확인하고 요구사항 20과 20-5를 구현해줘
```
* **명세서**: [`요구사항20-5_Phase20-5_4열_통합_E2E_검증_및_콘솔에러_0건_검수창구_확립.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-5_Phase20-5_4열_통합_E2E_검증_및_콘솔에러_0건_검수창구_확립.md)
* **내용**: 61종 전수 모듈 순회 클릭 시 브라우저 콘솔 에러 0건 및 4열 워크스페이스 무결성 E2E 검증.

---

## 2. Phase 21: DOCS 07 기반 4-Pane 워크스페이스 레이아웃 및 초고접근성 UI/UX

> **목표**: `docs/07` 표준 워크스페이스(사이드바 - 부재매니저/입력폼 - 세로2단뷰포트 - 순백색 A4 계산서) 및 4대 독립 리사이저, 즐겨찾기, DCR 글자 표기 구현.  
> **마스터 명세**: [`요구사항/요구사항21_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21_원본앱_모듈별_이질성_수용_및_초고접근성_UI_UX_명세.md)

### [21-1] 4-Pane 워크스페이스 레이아웃 및 4대 독립 리사이저
```text
/goal docs 16 확인하고 요구사항 21과 21-1을 구현해줘
```
* **명세서**: [`요구사항21-1_Phase21-1_DOCS07_4Pane_워크스페이스_레이아웃_및_4대_독립_리사이저.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-1_Phase21-1_DOCS07_4Pane_워크스페이스_레이아웃_및_4대_독립_리사이저.md)
* **내용**: Zero-Build 4-Pane Flexbox/Grid 셸 및 4대 독립 리사이저(`layout_resizer.js`) 드래그 동기화.

### [21-2] 스마트 계층형 모듈 탐색기 사이드바 및 즐겨찾기 시스템
```text
/goal docs 16 확인하고 요구사항 21과 21-2를 구현해줘
```
* **명세서**: [`요구사항21-2_Phase21-2_스마트_계층형_모듈_탐색기_사이드바_및_즐겨찾기_시스템.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-2_Phase21-2_스마트_계층형_모듈_탐색기_사이드바_및_즐겨찾기_시스템.md)
* **내용**: 사이드바 카테고리 필터(RC/Steel/SRC/ALU/RFM/FEM), 즐겨찾기(⭐) 상시 고정, DCR 2단계 글자(OK/NG).

### [21-3] 다중 부재 매니저 Pane 1 및 파라메트릭 입력폼 Pane 2 고도화
```text
/goal docs 16 확인하고 요구사항 21과 21-3을 구현해줘
```
* **명세서**: [`요구사항21-3_Phase21-3_다중_부재_매니저_Pane1_및_파라메트릭_입력폼_Pane2_고도화.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-3_Phase21-3_다중_부재_매니저_Pane1_및_파라메트릭_입력폼_Pane2_고도화.md)
* **내용**: 부재 추가/복제/삭제 매니저, 4대 서브탭 입력폼 및 4종 서브 모달 팝업.

### [21-4] 세로 적층형 다중 뷰포트 그래픽 정보부 Pane 3 구축
```text
/goal docs 16 확인하고 요구사항 21과 21-4를 구현해줘
```
* **명세서**: [`요구사항21-4_Phase21-4_세로_적층형_다중_뷰포트_그래픽_정보부_Pane3_구축.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-4_Phase21-4_세로_적층형_다중_뷰포트_그래픽_정보부_Pane3_구축.md)
* **내용**: 상단 뷰포트(단면/배근/형상) + 하단 뷰포트(부재력도/P-M 곡선/등고선) 세로 적층 및 줌/팬/Fit 툴바.

### [21-5] KDS 표준 구조계산서 Pane 4 엔진
```text
/goal docs 16 확인하고 요구사항 21과 21-5를 구현해줘
```
* **명세서**: [`요구사항21-5_Phase21-5_원본_출력모듈_1대1_계승_KDS_표준_구조계산서_Pane4_엔진.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-5_Phase21-5_원본_출력모듈_1대1_계승_KDS_표준_구조계산서_Pane4_엔진.md)
* **내용**: 상시 순백색(#ffffff) A4 용지 고정, 5대 장구분 목차, 3대 보고서 모드 라디오, KaTeX 수식 전개식.

### [21-6] 부재별 다형적 모듈팩 디스패처 및 5대 플래그십 4열 E2E 통합
```text
/goal docs 16 확인하고 요구사항 21과 21-6을 구현해줘
```
* **명세서**: [`요구사항21-6_Phase21-6_부재별_다형적_모듈팩_디스패처_및_5대_플래그십_4열_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항21-6_Phase21-6_부재별_다형적_모듈팩_디스패처_및_5대_플래그십_4열_E2E_통합.md)
* **내용**: 입력 시 100ms 이내 실시간 3-View 동시 동기화 및 4-Pane 통합 E2E 검증.

---

## 3. Phase 22: Tier 1 No.1 RC 보 (`rc_beam`) 수직관통 E2E

> **목표**: RC 보 단/복철근 휨·전단·처짐 설계엔진부터 원본 1:1 서브탭, 2D VDraw 캔버스, 순백색 A4 8단계 KaTeX 계산서까지 5대 공정으로 100% 수직 관통.  
> **마스터 명세**: [`요구사항/요구사항22_PhaseV1_01_RC보_rc_beam_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22_PhaseV1_01_RC보_rc_beam_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md)

### [22-1] Step 1: RC보 KDS 계산엔진 및 Pydantic 스키마
```text
/goal docs 16 확인하고 요구사항 22와 22-1을 구현해줘
```
* **명세서**: [`요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md)
* **검증**: 학회 예제집 대비 휨/전단 강도 오차 $\le 0.10\%$ TDD Pass.

### [22-2] Step 2: RC보 원본앱 1:1 서브탭 입력폼 및 모달
```text
/goal docs 16 확인하고 요구사항 22와 22-2를 구현해줘
```
* **명세서**: [`요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md)
* **검증**: `IDD_RCS_BEAM_PMODE_DLG` 1:1 매핑 4대 서브탭 및 철근/재료 모달 렌더링.

### [22-3] Step 3: RC보 2D VDraw 캔버스 배근도 및 부재력도 인터랙션
```text
/goal docs 16 확인하고 요구사항 22와 22-3을 구현해줘
```
* **명세서**: [`요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md)
* **검증**: 135° 스터럽 절곡, 피복 옵셋, 다단 주철근 단면도 및 부재력도 Canvas 렌더링.

### [22-4] Step 4: RC보 A4 5대장구분 8단계 KaTeX 구조계산서
```text
/goal docs 16 확인하고 요구사항 22와 22-4를 구현해줘
```
* **명세서**: [`요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md)
* **검증**: 순백색 A4 8단계 KaTeX 수식 전개식, 단면 배근도 SVG 임베딩, `  →  O.K` 표기.

### [22-5] Step 5: RC보 4열통합 E2E 검증 및 실사용 UI 온라인 전환
```text
/goal docs 16 확인하고 요구사항 22와 22-5를 구현해줘
```
* **명세서**: [`요구사항22-5_PhaseV1_01_Step5_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-5_PhaseV1_01_Step5_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md)
* **검증**: 파라미터 입력 시 100ms 3-View 동시 동기화, `is_wip: false` 정식 온라인 전환.

---

## 4. Phase 23: Tier 1 No.2 RC 기둥 (`rc_column`) 수직관통 E2E

> **목표**: 200 파이버 수치적분 3D P-M 곡면, 사각/원형 주철근 배근 캔버스, 이축휨/장주효과 A4 계산서까지 5대 공정 수직 관통.  
> **마스터 명세**: [`요구사항/요구사항23_PhaseV1_02_RC기둥_rc_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23_PhaseV1_02_RC기둥_rc_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md)

### [23-1] Step 1: RC기둥 KDS 계산엔진 및 파이버 PM Pydantic 스키마
```text
/goal docs 16 확인하고 요구사항 23과 23-1을 구현해줘
```
* **명세서**: [`요구사항23-1_PhaseV1_02_Step1_RC기둥_KDS계산엔진_및_파이버PM_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-1_PhaseV1_02_Step1_RC기둥_KDS계산엔진_및_파이버PM_Pydantic스키마.md)

### [23-2] Step 2: RC기둥 원본앱 1:1 서브탭 입력폼 및 모달
```text
/goal docs 16 확인하고 요구사항 23과 23-2를 구현해줘
```
* **명세서**: [`요구사항23-2_PhaseV1_02_Step2_RC기둥_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-2_PhaseV1_02_Step2_RC기둥_원본앱_1대1_서브탭_입력폼_및_모달.md)

### [23-3] Step 3: RC기둥 2D VDraw 캔버스 배근도 및 PM곡선 인터랙션
```text
/goal docs 16 확인하고 요구사항 23과 23-3을 구현해줘
```
* **명세서**: [`요구사항23-3_PhaseV1_02_Step3_RC기둥_2D_VDraw_캔버스_배근도_및_PM곡선_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-3_PhaseV1_02_Step3_RC기둥_2D_VDraw_캔버스_배근도_및_PM곡선_인터랙션.md)

### [23-4] Step 4: RC기둥 A4 5대장구분 8단계 KaTeX 구조계산서
```text
/goal docs 16 확인하고 요구사항 23과 23-4를 구현해줘
```
* **명세서**: [`요구사항23-4_PhaseV1_02_Step4_RC기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-4_PhaseV1_02_Step4_RC기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md)

### [23-5] Step 5: RC기둥 4열통합 E2E 검증 및 실사용 UI 온라인 전환
```text
/goal docs 16 확인하고 요구사항 23과 23-5를 구현해줘
```
* **명세서**: [`요구사항23-5_PhaseV1_02_Step5_RC기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-5_PhaseV1_02_Step5_RC기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md)

---

## 5. Phase 24: Tier 1 No.3 RC 전단벽 (`rc_shear_wall`) 수직관통 E2E

> **목표**: 벽체 전단강도, 변위/응력 기반 특수경계요소 판정, 단부 보강 배근 캔버스, 벽체 A4 계산서까지 5대 공정 수직 관통.  
> **마스터 명세**: [`요구사항/요구사항24_PhaseV1_03_RC전단벽_rc_shear_wall_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24_PhaseV1_03_RC전단벽_rc_shear_wall_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md)

### [24-1] Step 1: RC전단벽 KDS 계산엔진 및 경계요소 Pydantic 스키마
```text
/goal docs 16 확인하고 요구사항 24와 24-1을 구현해줘
```
* **명세서**: [`요구사항24-1_PhaseV1_03_Step1_RC전단벽_KDS계산엔진_및_경계요소_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-1_PhaseV1_03_Step1_RC전단벽_KDS계산엔진_및_경계요소_Pydantic스키마.md)

### [24-2] Step 2: RC전단벽 원본앱 1:1 서브탭 입력폼 및 모달
```text
/goal docs 16 확인하고 요구사항 24와 24-2를 구현해줘
```
* **명세서**: [`요구사항24-2_PhaseV1_03_Step2_RC전단벽_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-2_PhaseV1_03_Step2_RC전단벽_원본앱_1대1_서브탭_입력폼_및_모달.md)

### [24-3] Step 3: RC전단벽 2D VDraw 캔버스 배근도 및 경계요소 인터랙션
```text
/goal docs 16 확인하고 요구사항 24와 24-3을 구현해줘
```
* **명세서**: [`요구사항24-3_PhaseV1_03_Step3_RC전단벽_2D_VDraw_캔버스_배근도_및_경계요소_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-3_PhaseV1_03_Step3_RC전단벽_2D_VDraw_캔버스_배근도_및_경계요소_인터랙션.md)

### [24-4] Step 4: RC전단벽 A4 5대장구분 8단계 KaTeX 구조계산서
```text
/goal docs 16 확인하고 요구사항 24와 24-4를 구현해줘
```
* **명세서**: [`요구사항24-4_PhaseV1_03_Step4_RC전단벽_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-4_PhaseV1_03_Step4_RC전단벽_A4_5대장구분_8단계_KaTeX_구조계산서.md)

### [24-5] Step 5: RC전단벽 4열통합 E2E 검증 및 실사용 UI 온라인 전환
```text
/goal docs 16 확인하고 요구사항 24와 24-5를 구현해줘
```
* **명세서**: [`요구사항24-5_PhaseV1_03_Step5_RC전단벽_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항24-5_PhaseV1_03_Step5_RC전단벽_4열통합_E2E검증_및_실사용UI_온라인전환.md)

---

## 6. Phase 25: Tier 1 No.4 철골 보/기둥 (`steel_beam_column`) 수직관통 E2E

> **목표**: H/Box/Pipe 조밀성 분류, LTB 좌굴강도, 축휨 P-M 상관, 강재 상세도 캔버스, 철골 A4 계산서까지 5대 공정 수직 관통.  
> **마스터 명세**: [`요구사항/요구사항25_PhaseV1_04_철골보기둥_steel_beam_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25_PhaseV1_04_철골보기둥_steel_beam_column_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md)

### [25-1] Step 1: 철골보기둥 KDS 계산엔진 및 Pydantic 스키마
```text
/goal docs 16 확인하고 요구사항 25와 25-1을 구현해줘
```
* **명세서**: [`요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-1_PhaseV1_04_Step1_철골보기둥_KDS계산엔진_및_Pydantic스키마.md)

### [25-2] Step 2: 철골보기둥 원본앱 1:1 서브탭 입력폼 및 모달
```text
/goal docs 16 확인하고 요구사항 25와 25-2를 구현해줘
```
* **명세서**: [`요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-2_PhaseV1_04_Step2_철골보기둥_원본앱_1대1_서브탭_입력폼_및_모달.md)

### [25-3] Step 3: 철골보기둥 2D VDraw 캔버스 단면도 및 부재력도 인터랙션
```text
/goal docs 16 확인하고 요구사항 25와 25-3을 구현해줘
```
* **명세서**: [`요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-3_PhaseV1_04_Step3_철골보기둥_2D_VDraw_캔버스_단면도_및_부재력도_인터랙션.md)

### [25-4] Step 4: 철골보기둥 A4 5대장구분 8단계 KaTeX 구조계산서
```text
/goal docs 16 확인하고 요구사항 25와 25-4를 구현해줘
```
* **명세서**: [`요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-4_PhaseV1_04_Step4_철골보기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md)

### [25-5] Step 5: 철골보기둥 4열통합 E2E 검증 및 실사용 UI 온라인 전환
```text
/goal docs 16 확인하고 요구사항 25와 25-5를 구현해줘
```
* **명세서**: [`요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항25-5_PhaseV1_04_Step5_철골보기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md)

---

## 7. Phase 26: Tier 1 No.5 철골 주각부 (`steel_baseplate`) 수직관통 E2E

> **목표**: 콘크리트 지압, 베이스플레이트 휨 두께, 앵커볼트 인장/전단, 주각부 2D 상세도 캔버스, 주각부 A4 계산서까지 5대 공정 수직 관통.  
> **마스터 명세**: [`요구사항/요구사항26_PhaseV1_05_철골주각부_steel_baseplate_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26_PhaseV1_05_철골주각부_steel_baseplate_수직관통_설계엔진_입력폼_캔버스_계산서_E2E_통합.md)

### [26-1] Step 1: 철골주각부 KDS 계산엔진 및 Pydantic 스키마
```text
/goal docs 16 확인하고 요구사항 26과 26-1을 구현해줘
```
* **명세서**: [`요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-1_PhaseV1_05_Step1_철골주각부_KDS계산엔진_및_Pydantic스키마.md)

### [26-2] Step 2: 철골주각부 원본앱 1:1 서브탭 입력폼 및 모달
```text
/goal docs 16 확인하고 요구사항 26과 26-2를 구현해줘
```
* **명세서**: [`요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-2_PhaseV1_05_Step2_철골주각부_원본앱_1대1_서브탭_입력폼_및_모달.md)

### [26-3] Step 3: 철골주각부 2D VDraw 캔버스 상세도 및 지압응력 인터랙션
```text
/goal docs 16 확인하고 요구사항 26과 26-3을 구현해줘
```
* **명세서**: [`요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-3_PhaseV1_05_Step3_철골주각부_2D_VDraw_캔버스_상세도_및_지압응력_인터랙션.md)

### [26-4] Step 4: 철골주각부 A4 5대장구분 8단계 KaTeX 구조계산서
```text
/goal docs 16 확인하고 요구사항 26과 26-4를 구현해줘
```
* **명세서**: [`요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-4_PhaseV1_05_Step4_철골주각부_A4_5대장구분_8단계_KaTeX_구조계산서.md)

### [26-5] Step 5: 철골주각부 4열통합 E2E 검증 및 실사용 UI 온라인 전환
```text
/goal docs 16 확인하고 요구사항 26과 26-5를 구현해줘
```
* **명세서**: [`요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항26-5_PhaseV1_05_Step5_철골주각부_4열통합_E2E검증_및_실사용UI_온라인전환.md)

---

## 8. 기완료 벤치마크: 요구사항 27 (Phase 27-1 ~ 27-4) 기록

> **결과**: 전 항목 성공적으로 100% 완수 및 [`요구사항/@@OLD/`](file:///f:/PyProject/AltDP_3rd/요구사항/@@OLD/) 아카이빙 완료 (`pytest 263/263 PASS`).

| 완료 단계 | 실행 커맨드 | 생성 커밋 | 비고 |
|---|---|:---:|---|
| **Phase 27-1** | `/goal docs 16 확인하고 요구사항 27과 27-1을 구현해줘` | `34ac784` | 33종 단면DB 자체 자산화 및 `src/core/paths.py` |
| **Phase 27-2** | `/goal docs 16 확인하고 요구사항 27과 27-2을 구현해줘` | `dcb287c` | 3D 골조 모델 인터페이스 `FrameModel3D` 순수화 |
| **Phase 27-3** | `/goal docs 16 확인하고 요구사항 27과 27-3을 구현해줘` | `58876dc` | 프론트엔드 UI/스크립트 및 소스주석 고유명사 소거 |
| **Phase 27-4** | `/goal docs 16 확인하고 요구사항 27과 27-4을 구현해줘` | `7f99466` | 테스트 코드 동기화 및 `src/` 외부참조 0건 전수검증 |
