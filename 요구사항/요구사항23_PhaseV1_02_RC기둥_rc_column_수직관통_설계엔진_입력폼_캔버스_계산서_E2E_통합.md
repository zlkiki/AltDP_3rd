# 요구사항 23: Phase V1-2 RC 기둥 (rc_column) 수직 관통 마스터 명세서

## 1. 개요 및 61종 마스터플랜 매핑 (Master Plan Alignment)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/04_master_original_app_modules_comprehensive_catalog.md`](file:///f:/PyProject/AltDP_3rd/docs/04_master_original_app_modules_comprehensive_catalog.md)**(61종 전수 모듈 인벤토리) 및 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**(Phase V1~V6 수직 포팅 마스터플랜)에 따라, Tier 1 플래그십 핵심 부재인 **RC 기둥 (`rc_column`)**을 5대 공정(Step 1~5)으로 수직 관통(Vertical Slice)하여 100% 작동 가능한 완성형 상용 웹 모듈로 개발하기 위한 **총괄 마스터 명세서**입니다.

* **모듈 식별자**: `rc_column` (카탈로그 번호 No. 2, Tier 1 플래그십)
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/` (`solver__CHK_BCCO_*.c`, `CDBSolverTool`, `DPLUS_RCS.dll`, `DPLUS_DB.dll`)
  2. `[2순위 원본 리소스]`: `original_src/Midas Design+/Language/Korean/` (`DLG_DPLUS_RCS.ini`, `Menu.ini`, 공식 매뉴얼)
  3. `[3순위 학회 예제집]`: `F:/PyProject/KCSC2MD/output/예제집/` (콘크리트구조학회 2020 예제집 5.1/5.2/5.3, 오류 시 Patch-First 선 치유 원칙)
  4. `[4순위 국가건설기준]`: `F:/PyProject/KCSC2MD/output/kds_md/` (KDS 14 20 10, KDS 14 20 20, KDS 14 20 22, 오류 시 Patch-First 선 치유 원칙)

---

## 2. 5대 마이크로 공정 하위 요구사항 세분화 인덱스 (`docs/16` 규약 연동)

본 마스터 요구사항은 `docs/10` 제2절(Scope Partitioning) 및 `docs/16`(Goal 마이크로 공정 표준 실행 지침)에 따라 **단일 책임과 독립 실행이 가능한 5개의 세부 하위 명세서**로 분할되어 관리됩니다:

| 공정 단계 | 권장 AI 모델 | 하위 명세서 링크 | 핵심 산출물 및 주요 업무 | DoD 검증 기준 |
|:---:|:---:|---|---|:---:|
| **Step 1** | 🧠 **High** | [**요구사항 23-1**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-1_PhaseV1_02_Step1_RC기둥_KDS계산엔진_및_파이버PM_Pydantic스키마.md) | • KDS 14 20 20 축휨/전단 파이썬 엔진 (`src/engine/rc/column.py`)<br>• 200 파이버 단면 수치적분 P-M 솔버 연동<br>• 장주 모멘트확대($\delta_{ns}, \delta_s$) 및 Bresler 이축휨 | `pytest` 100% PASS<br>(오차 $\le 0.10\%$) |
| **Step 2** | ⚙️ **Medium** | [**요구사항 23-2**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-2_PhaseV1_02_Step2_RC기둥_원본앱_1대1_서브탭_입력폼_및_모달.md) | • 원본앱 `IDD_RCS_COLUMN_PMODE_DLG` 1:1 서브탭 폼 (`form_rc_column.js`)<br>• 배근 상세 설정 서브대화창 모달 (`IDD_RCS_COLM_REBAR_DLG`)<br>• P-M 상관곡선 인터랙티브 뷰어 확장 모달 | 브라우저 DOM 정상<br>콘솔 에러 0건 |
| **Step 3** | ⚙️ **Medium** | [**요구사항 23-3**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-3_PhaseV1_02_Step3_RC기둥_2D_VDraw_캔버스_배근도_및_PM곡선_인터랙션.md) | • 상단: 사각/원형 단면, 135° 절곡 띠대근, 솔리드 주철근, 치수선, 태그<br>• 하단: KDS 200 파이버 $\phi P_n-\phi M_n$ 상관곡선 및 설계하중점 플롯<br>• 마우스 휠 줌/팬/Fit 및 하중점 마우스 호버 DCR 툴팁 | Canvas 그래픽스 렌더링<br>인터랙션 무결성 |
| **Step 4** | 🧠 **High** | [**요구사항 23-4**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-4_PhaseV1_02_Step4_RC기둥_A4_5대장구분_8단계_KaTeX_구조계산서.md) | • 원본 5대 장구분 완벽 계승 (개요-부재력-PM-이축휨-전단)<br>• 8단계 Step-by-Step KaTeX 수식 전개식 (`redcr_rc_column.js`)<br>• 순백색(`#ffffff`) A4 용지 인쇄 프리뷰 및 `  →  O.K / N.G` 판정 | A4 인쇄 레이아웃<br>KaTeX 수식 무결성 |
| **Step 5** | ⚙️ **Medium** | [**요구사항 23-5**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항23-5_PhaseV1_02_Step5_RC기둥_4열통합_E2E검증_및_실사용UI_온라인전환.md) | • 4-Pane(사이드바-Left-Sub(부재/폼)-중앙그래픽-순백색A4계산서) 연동<br>• 파라미터 입력 시 **100ms 이내 실시간 3-View 동시 동기화**<br>• `catalog.js`에서 `rc_column`의 `is_wip: false` 정식 온라인 전환 | E2E 전수 테스트 Pass<br>콘솔 에러 0건 |

---

## 3. 실행 및 커맨드 가이드 (`docs/16` 준수)

사용자 및 에이전트는 아래의 표준 명령어를 통해 각 Step을 독립적으로 안전하게 실행합니다:

```markdown
# [Step 1: KDS 엔진 및 파이버 P-M 단독 실행 - High 모델 권장]
/goal
docs 16을 확인하고, 요구사항 23과 하위 23-1의 Step 1을 구현해줘.

# [Step 2: 원본앱 1:1 서브탭 폼 및 모달 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 23과 하위 23-2의 Step 2를 구현해줘.

# [Step 3: 2D VDraw 캔버스 및 P-M 다이어그램 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 23과 하위 23-3의 Step 3을 구현해줘.

# [Step 4: A4 5대장구분 8단계 KaTeX 계산서 단독 실행 - High 모델 권장]
/goal
docs 16을 확인하고, 요구사항 23과 하위 23-4의 Step 4를 구현해줘.

# [Step 5: 4-Pane 통합 E2E 검증 및 온라인 오픈 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 23과 하위 23-5의 Step 5를 구현해줘.

# [Phase V1-02 전체 연속 완수 지시 시]
/goal
docs 16을 확인하고, 요구사항 23의 Step 1부터 Step 5까지 순차적으로 구현해줘.
```

---

## 4. 마스터 종합 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **[Step 1 수치 무결성]**: `tests/engine/test_rc_column.py` 100% 통과 (학회 예제집 5.1/5.2/5.3 대비 오차 $\le 0.10\%$).
- [ ] **[Step 2 입력폼 1:1]**: 원본 `IDD_RCS_COLUMN_PMODE_DLG` 4대 서브탭, 배근/P-M 모달 정상 렌더링 및 Pane 1(다중 부재 매니저) 데이터 연동.
- [ ] **[Step 3 2D 캔버스]**: 상단 단면 배근도 + 하단 200 파이버 KDS P-M 상관곡선/설계하중점 인터랙티브 플롯 정상 작동.
- [ ] **[Step 4 A4 계산서]**: 순백색(`#ffffff`) A4 용지 고정, 5대 장구분 8단계 KaTeX 수식 전개식, `  →  O.K / N.G` 판정 화살표, `[입력 데이터 상세 포함]` 토글.
- [ ] **[Step 5 4-Pane 통합]**: 4-Pane(사이드바-Left-Sub(부재/폼)-Center그래픽-Right계산서) 실시간 100ms 동기화 검증 및 `is_wip: false` 정식 온라인 전환.
- [ ] **[증거 제출 규약]**: `docs/16` 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 및 1단위 Git 푸시 완료.
