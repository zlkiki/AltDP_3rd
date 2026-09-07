# 요구사항 22: Phase V1-1 RC 보 (rc_beam) 수직 관통 마스터 명세서

## 1. 개요 및 61종 마스터플랜 매핑 (Master Plan Alignment)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/04_master_original_app_modules_comprehensive_catalog.md`](file:///f:/PyProject/AltDP_3rd/docs/04_master_original_app_modules_comprehensive_catalog.md)**(61종 전수 모듈 인벤토리) 및 **[`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**(Phase V1~V6 수직 포팅 마스터플랜)에 따라, 최우선 기반 부재군인 **Tier 1 플래그십 핵심 부재 No. 1**인 **RC 보 (`rc_beam`)**를 5대 공정(Step 1~5)으로 수직 관통(Vertical Slice)하여 100% 작동 가능한 상용 엔지니어링 웹 모듈로 개발하기 위한 **총괄 마스터 명세서**입니다.

* **모듈 식별자**: `rc_beam` (카탈로그 번호 No. 1, Tier 1 플래그십)
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/rc/` (`rc__CHK_BBBE_*.c`, `CHK_BBBE_beam.c`, `DPLUS_RCS.dll`, `symbols/DPLUS_RCS.dll_symbols.txt`)
  2. `[2순위 원본 리소스]`: `original_src/Midas Design+/Language/Korean/` (`DLG_DPLUS_RCS.ini`, `Menu.ini`, 원본앱 공식 기술 매뉴얼 보 편)
  3. `[3순위 학회 예제집]`: `F:/PyProject/KCSC2MD/output/예제집/` (한국콘크리트학회 2020 콘크리트구조설계기준 예제집 `3.1 단철근/복철근 휨`, `4.1 전단설계`, `4.3 비틀림`, `6.1 사용성 처짐/균열`)
  4. `[4순위 국가건설기준]`: `F:/PyProject/KCSC2MD/output/kds_md/` (KDS 14 20 10 재료/일반, KDS 14 20 20 휨, KDS 14 20 22 전단/비틀림, KDS 14 20 30 사용성)

---

## 2. 5대 마이크로 공정 하위 요구사항 세분화 인덱스 (`docs/16` 규약 연동)

본 마스터 요구사항은 `docs/10` 제2절(Scope Partitioning) 및 `docs/16`(Goal 마이크로 공정 표준 실행 지침)에 따라 **단일 책임과 독립 실행이 가능한 5개의 세부 하위 명세서**로 분할되어 관리됩니다.
특히 수치 오차 $\le 0.10\%$ 검증 및 방대한 KaTeX 수식 전개식이 요구되는 **Step 1과 Step 4는 High 모델(Thinking 모드)**로 전담하고, 브라우저 DOM/Canvas 그래픽스 중심의 **Step 2, Step 3, Step 5는 Medium 모델**로 역할 분담하여 토큰 낭비와 컨텍스트 누락을 원천 차단합니다:

| 공정 단계 | 권장 AI 모델 | 하위 명세서 링크 | 핵심 산출물 및 주요 업무 | DoD 검증 기준 |
|:---:|:---:|---|---|:---:|
| **Step 1** | 🧠 **High** | [**요구사항 22-1**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md) | • KDS 14 20 20/22/30 보 해석 엔진 (`src/engine/rc/beam.py`)<br>• 단/복철근 및 T형 플랜지 등가응력블록 휨 수렴 해석<br>• 전단($V_c, V_s$), 비틀림($T_{cr}, T_n, A_l$), Branson $I_e$ 장단기 처짐 | `pytest` 100% PASS<br>(오차 $\le 0.10\%$) |
| **Step 2** | ⚙️ **Medium** | [**요구사항 22-2**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md) | • 원본앱 `IDD_RCS_BEAM_PMODE_DLG` 1:1 서브탭 폼 (`form_rc_beam.js`)<br>• 단부(I/J)/중앙(M) 다단 배근 테이블 및 스터럽 입력<br>• 배근 상세 모달(`IDD_RCS_BEAM_REBAR_DLG`) 및 T형 단면 모달 | 브라우저 DOM 정상<br>콘솔 에러 0건 |
| **Step 3** | ⚙️ **Medium** | [**요구사항 22-3**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md) | • 상단 뷰포트: 보 경간($L$) 종단면 배근도 & $M/V$ 부재력 포락선<br>• 하단 뷰포트: 단부 I, 중앙 M, 단부 J 3개 횡단면도, 135° 갈고리 스터럽<br>• 피복 옵셋, 치수선, 철근태그, 휠 줌/팬/Fit/호버 툴팁 | Canvas 그래픽스 렌더링<br>인터랙션 무결성 |
| **Step 4** | 🧠 **High** | [**요구사항 22-4**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md) | • 원본 5대 장구분 계승 (개요-부재력-휨-전단/비틀림-사용성처짐균열)<br>• 8단계 Step-by-Step KaTeX 수식 전개식 (`redcr_rc_beam.js`)<br>• 순백색(`#ffffff`) A4 용지 인쇄 프리뷰 및 `  →  O.K / N.G` 판정 | A4 인쇄 레이아웃<br>KaTeX 수식 무결성 |
| **Step 5** | ⚙️ **Medium** | [**요구사항 22-5**](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-5_PhaseV1_01_Step5_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md) | • 4-Pane(사이드바-Left-Sub(부재/폼)-중앙그래픽-순백색A4계산서) 연동<br>• 파라미터 수정 시 **100ms 이내 실시간 3-View 동시 동기화**<br>• `catalog.js`에서 `rc_beam`의 `is_wip: false` 정식 온라인 전환 | E2E 전수 테스트 Pass<br>콘솔 에러 0건 |

---

## 3. 실행 및 커맨드 가이드 (`docs/16` 준수)

사용자 및 에이전트는 아래의 표준 명령어를 통해 각 Step을 독립적으로 안전하게 실행합니다:

```markdown
# [Step 1: KDS 계산 엔진 및 Pydantic 스키마 단독 실행 - High 모델 권장]
/goal
docs 16을 확인하고, 요구사항 22와 하위 22-1의 Step 1을 구현해줘.

# [Step 2: 원본앱 1:1 서브탭 입력폼 및 모달 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 22와 하위 22-2의 Step 2를 구현해줘.

# [Step 3: 2D VDraw 캔버스 배근도 및 부재력도 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 22와 하위 22-3의 Step 3을 구현해줘.

# [Step 4: A4 5대장구분 8단계 KaTeX 계산서 단독 실행 - High 모델 권장]
/goal
docs 16을 확인하고, 요구사항 22와 하위 22-4의 Step 4를 구현해줘.

# [Step 5: 4-Pane 통합 E2E 검증 및 온라인 오픈 단독 실행 - Medium 모델 권장]
/goal
docs 16을 확인하고, 요구사항 22와 하위 22-5의 Step 5를 구현해줘.

# [Phase V1-01 전체 연속 완수 지시 시]
/goal
docs 16을 확인하고, 요구사항 22의 Step 1부터 Step 5까지 순차적으로 구현해줘.
```

---

## 4. 마스터 종합 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **[Step 1 수치 무결성]**: `tests/engine/test_rc_beam.py` 100% 통과 (콘크리트학회 예제집 3.1, 4.1, 4.3, 6.1 대비 오차 $\le 0.10\%$).
- [ ] **[Step 2 입력폼 1:1]**: 원본앱 `IDD_RCS_BEAM_PMODE_DLG` 4대 서브탭(단면/재료, 철근배근, 부재력, 사용성) 및 상세 배근 모달 정상 렌더링.
- [ ] **[Step 3 2D 캔버스]**: 상단 종단면 부재력선 오버레이 + 하단 단부(I/J)/중앙(M) 3개 횡단면 135° 내진 갈고리 스터럽 그래픽스 렌더링 검증.
- [ ] **[Step 4 A4 계산서]**: 5대 장구분 및 8단계 KaTeX 수식 전개, `  →  O.K / N.G` 판정 화살표, A4 인쇄 프리뷰 레이아웃 완비.
- [ ] **[Step 5 4-Pane 통합]**: 파라미터 변경 시 100ms 이내 실시간 3-View 동기화, 콘솔 에러 0건, `is_wip: false` 정식 온라인 전환.
- [ ] **[증거 제출 규약]**: `docs/16`에 따른 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 및 단위 Git 커밋/푸시 완료.
