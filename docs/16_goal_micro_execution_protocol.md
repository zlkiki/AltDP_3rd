# 16. Goal 마이크로 공정 표준 실행 지침 (Goal Micro Execution Protocol)

본 문서는 `/goal` 명령 기반 장기 실행 및 부재별 5대 정밀 공정(Step 1~5) 실행 시 컨텍스트 폭주와 작업 누락을 방지하기 위한 **마이크로 실행 격리(Micro Partitioning), 즉시 정지(Stop Protocol) 및 증거 강제 제출(Proof-First Mandate)의 단일 진실 공급원(SSOT)**입니다.

> [!IMPORTANT]
> **🚨 Goal 단독 실행 절대 원칙 (Single-Scope Execution)**:
> 사용자가 `/goal` 명령으로 작업을 지시할 때, 에이전트는 본 지침과 [`AGENTS.md`](file:///f:/PyProject/AltDP_3rd/.agents/AGENTS.md), [`docs/10`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)의 규약을 엄격히 준수하여 **지정된 단 하나의 하위 Phase 또는 단 하나의 Step만 완수**하고, 4대 물리적 증거를 제출한 뒤 즉시 작업을 정지(Stop Protocol)해야 합니다.

---

## 1. 대상 작업 자동 라우팅 및 단독 실행 격리 규칙

에이전트는 사용자의 프롬프트로부터 아래 대상을 자동으로 식별하고 열람(`view_file`)하여 작업을 시작합니다:

1. **프로젝트 공통 규칙**: [`AGENTS.md`](file:///f:/PyProject/AltDP_3rd/.agents/AGENTS.md), [`docs/10`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md), [`docs/07`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) (작업 착수 전 필수 열람)
2. **도메인별 기술 사양 SSOT**: [`docs/04 (61종 전수 매핑)`](file:///f:/PyProject/AltDP_3rd/docs/04_master_original_app_modules_comprehensive_catalog.md), [`docs/01 (아키텍처)`](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md), [`docs/03 (단면DB)`](file:///f:/PyProject/AltDP_3rd/docs/03_section_db_specification.md), [`docs/14 (계산서)`](file:///f:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md), [`docs/15 (FEM)`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md)
3. **대상 요구사항 문서**: 사용자가 지정한 하위 명세서 (예: [`요구사항20-5`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20-5_Phase20-5_4열_통합_E2E_검증_및_콘솔에러_0건_검수창구_확립.md), [`요구사항22-1`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md) 등)
4. **단독 실행 스코프 격리 (2대 실행 모드)**:
   - **모드 A [하위 Phase 단위 실행]**: 지정된 하위 Phase(예: `Phase 20-5`, `Phase 21-1`)의 작업 스코프만 독립 완수.
   - **모드 B [부재별 5대 정밀 공정 단위 실행]**: 부재 수직 관통 시 지정된 특정 Step(1~5 중 택 1)만 단독 완수.

---

## 2. 2단계 5정밀 마이크로 공정 레퍼런스 (Step 1 ~ Step 5)

원본앱 부재 설계 모듈의 Step 단위 실행 시 적용되는 5대 공정, 권장 모델 티어 및 완료 검증 기준(DoD)입니다:

| 공정 단계 | 권장 모델 | 공정 명칭 | 핵심 산출물 및 작업 내용 | 필수 검증 기준 (DoD) | 연동 SSOT |
|:---:|:---:|---|---|:---:|:---:|
| **Step 1** | 🧠 **High** | **KDS 계산 엔진 & Pydantic 스키마** | KDS 14 20/31 수식 순수 파이썬 구현, P-M/FEM 솔버 연동, 입출력 스키마 | `pytest` 100% PASS<br>(오차 $\le 0.10\%$) | [`docs/10`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md) |
| **Step 2** | ⚙️ **Medium** | **원본앱 1:1 서브탭 입력폼 & 모달** | 원본 `DLG_*.ini` 1:1 서브탭 폼, 재료/단면(.sdb) 모달, 유효성 검증 | 브라우저 DOM 정상<br>콘솔 에러 0건 | [`docs/07 PART 4`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) |
| **Step 3** | ⚙️ **Medium** | **2D Canvas 배근도/치수선/그래픽스** | VDraw 기하 알고리즘 이식, 주근/늑근 배근도, 치수선, 철근태그 렌더링 | Canvas 그래픽스 정상<br>줌/팬 인터랙션 | [`docs/07 PART 4`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) |
| **Step 4** | 🧠 **High** | **A4 8단계 KaTeX 수식 전개식 계산서** | 5대 장구분 완벽 계승, 8단계 수식 전개식, 순백색(`#ffffff`) A4 템플릿 | A4 인쇄 프리뷰 정상<br>공학 계산서 레이아웃 | [`docs/14`](file:///f:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md) |
| **Step 5** | ⚙️ **Medium** | **E2E 통합 테스트 & 실사용 UI 최종 검증** | 4열 통합(트리-폼-캔버스-계산서) 100ms 실시간 동기화, 콘솔에러 0건 | E2E 테스트 PASS &<br>브라우저 육안 확인 | [`docs/07 PART 4`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) |

---

## 3. 공학 무결성 5대 게이트 (Engineering Gates)

모든 단위 구현 시 아래 5대 무결성 게이트를 무조건 통과해야 합니다:

1. **4대 SSOT 계층 준수**: `1순위 추출 소스 > 2순위 매뉴얼 > 3순위 공인 예제집 > 4순위 KDS 원문` 우선순위 엄수 ([`docs/10 제1.1절`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)).
2. **0.10% 오차 한계 엄수**: 학회 공인 예제집 및 원본 프로그램 대비 계산 오차는 반드시 **0.10% 이하($\le 0.10\%$)** 유지 ([`docs/10 제1.4절`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)).
3. **선 치유(Patch-First) 의무**: 마크다운 기준서(4순위) 및 공식 예제집(3순위) 오류 발견 시 `kcsc2md` 선행 영구 치유 선행 ([`docs/10 제1.3절`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)).
4. **공학 완전성 (더미 코드 절대 금지)**: 수식 축약이나 하드코딩 Mock/Stub(예: `phi_mn = 150.0`) 반환 전면 금지, 미구현 시 투명한 WIP 응답 반환.
5. **3-View 100ms 실시간 동기화**: `ProjectStore` 중심 입력폼-캔버스-계산서 **100ms 이내 동시 반응** 보장 ([`docs/07 PART 4`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)).

---

## 4. 정지 규칙 (Stop Protocol) & 증거 강제 규약 (Proof-First Mandate)

> [!CAUTION]
> **🚨 증거 없는 완료 보고 전면 무효 (Proof-First Mandate)**:
> 에이전트는 "테스트 통과했습니다", "오차 없습니다"라는 단순 텍스트 주장만으로 작업을 마칠 수 없습니다. **4대 물리적 증거(Evidence)가 누락된 보고는 즉각 반려**됩니다.

1. **물리적 TDD 검증**:
   - 기능 작성 전/후 대상 도메인 테스트를 실행하고, 터미널 Exit Code 0 및 오차 $\le 0.10\%$를 물리적 로그로 입증하십시오 ([`docs/08`](file:///f:/PyProject/AltDP_3rd/docs/08_pytest_testing_guide.md)).
2. **1 작업 = 1 Git 커밋 & 원격 푸시**:
   - 단위 작업 완료 즉시 1개의 Git 커밋을 생성하고 원격(`git push origin main`)까지 푸시 완료하십시오 ([`AGENTS.md 제3절 11항`](file:///f:/PyProject/AltDP_3rd/.agents/AGENTS.md)).
   - 커밋 메시지: `feat([요구사항번호]-[Phase/Step]): [구현 요약] (오차/규약 검증 완료)`
3. **외부 기억 갱신 동봉**:
   - 단위 작업 완료 직전, [`요구사항/PROJECT_PROGRESS.md`](file:///f:/PyProject/AltDP_3rd/요구사항/PROJECT_PROGRESS.md)의 진행 상태와 최신 커밋 해시를 갱신하십시오.
4. **즉시 작업 정지 (Stop Protocol)**:
   - 푸시 완료 후 제5절의 증거 보고 양식을 제출한 뒤 **즉시 작업을 멈추십시오. 다음 단계로 임의 전진하지 마십시오.**

---

## 5. 표준 완료 증거 보고 양식 (Proof-First Evidence Report)

단위 작업 완료 시 보고서 본문에 반드시 아래 4대 물리적 증거 블록을 순서대로 포함하십시오:

```markdown
### 1. 완수 작업 개요
- 작업 대상: [요구사항 번호 및 하위 작업/Step명]
- 생성 커밋: [커밋 해시] [커밋 메시지]
- 푸시 상태: origin/main 동기화 완료

### 2. [증거 1] 원본 Ground Truth 실제 조회 및 Self-Healing 내역
- 원본 파일 및 라인: `[파일 경로]` Line XXX
- 원본 발췌 텍스트 / KCSC2MD 선 치유 패치 커밋 해시: [해시 또는 텍스트]

### 3. [증거 2] 수학적 3자 삼각대조 오차표
| 검증 항목 | [3순위] 학회 예제집 | [1·2순위] 원본앱 / KDS | [AltDP_3rd] 엔진 계산치 | 오차율(%) | 판정 (기준 <= 0.10%) |
|---|---|---|---|---|---|
| 휨 / 압축 / 전단 | ... | ... | ... | X.XX% | PASS |

### 4. [증거 3] 터미널 Raw 실행 로그
```text
[pytest -v 또는 E2E 테스트 실행 터미널 로그 복사본 (Exit Code 0)]
```

### 5. [증거 4] Git Diff 영수증 (`git show --stat`)
```text
[git show --stat 커밋 변경 파일 및 라인 수 내역]
```
```

---

## 6. 실전 /goal 프롬프트 표준 레퍼런스 (사용자용)

작업 실행 시 [`요구사항/PROJECT_PROGRESS.md`](file:///f:/PyProject/AltDP_3rd/요구사항/PROJECT_PROGRESS.md)의 [실행 명령문]을 복사하여 아래 형식으로 지시합니다:

* **하위 Phase 단위 실행 시 (예: Phase 20-5)**:
  ```text
  /goal docs 16 확인하고 요구사항 20과 20-5를 구현해줘
  ```
* **부재별 Step 단위 실행 시 (예: Phase 22-1 Step 1)**:
  ```text
  /goal docs 16 확인하고 요구사항 22와 22-1을 구현해줘
  ```
