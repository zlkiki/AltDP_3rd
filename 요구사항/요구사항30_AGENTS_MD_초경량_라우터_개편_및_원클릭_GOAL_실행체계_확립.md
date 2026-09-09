# 요구사항 30: AGENTS.md 초경량 라우터 개편 및 원클릭 /goal 실행 체계 확립

## 1. 개요 및 목적

### 1.1 배경 및 사용자 핵심 니즈
* **사용자 지시 표준화 목표**:
  ```text
  /goal agents.md를 읽고 요구사항X를 구현해줘.
  ```
* **현행 문제점 및 진단**:
  - 기존 `AGENTS.md`는 상단에 `🚨 필수 선행 열람 규약`을 두어 매 턴마다 `docs/10`, `docs/16`, `docs/07`, `PROJECT_PROGRESS.md` 등 **11만 바이트(3.5만~4.5만 토큰)**의 문서를 강제로 읽도록 요구하여 컨텍스트 오염과 토큰 낭비를 유발했습니다.
  - `docs/16`의 "Step 1개 완수 후 즉시 정지(Stop Protocol)"와 "수천 자의 4대 마크다운 증거 보고서 작성 강제"로 인해, 단일 부재 수직관통(Core → Engine → TDD → UI 4-Pane)을 한 번에 완주하지 못하고 중간에 멈춰 섰습니다.
  - `docs/10`(17.5KB)은 개발 과정 전체를 관통하는 핵심 철학과 상세 절차를 담고 있으나, 이를 `AGENTS.md`에 통째로 넣으면 너무 비대해지고, 완전히 배제하면 핵심 엔지니어링 철학을 유실하는 딜레마가 존재했습니다.
* **본 문서의 목적**:
  - `AGENTS.md`를 **"지정된 요구사항으로 즉시 직행하는 초경량 라우터(Router)이자 5대 불변 행동 원칙을 담은 상시 헌법"**으로 전면 개편합니다.
  - `docs/16`을 정식 보관(`docs/@@OLD/`) 처리하고, `docs/10`과의 관계를 **"헌법(AGENTS.md 상시 기억) vs 세부 규정 사전(docs/10 온디맨드 참조)"의 2계층 분리 모델**로 확립합니다.
  - 사용자가 위 단 한 줄의 명령을 내렸을 때 에이전트가 즉각 요구사항 명세서로 진입하여 **엔진 → TDD → UI 4-Pane 전체를 단번에 완주(E2E Run-to-Finish)**하는 실행 환경을 확립합니다.

---

## 2. AGENTS.md ↔ docs/10 2계층 아키텍처 및 쇄신 방향

```mermaid
graph TD
    subgraph Layer1 [계층 1: AGENTS.md (상시 탑재 초경량 헌법 & 라우터)]
        A["5대 불변 행동 원칙 (1줄 요약, 약 15줄)"]
        B["원클릭 /goal 실행 규약 (단일 마스터 연속 완주)"]
        C["JIT 온디맨드 사전 라우터 (docs 링크)"]
    end

    subgraph Layer2 [계층 2: docs/10 (상세 실행 매뉴얼 백과사전)]
        D["kcsc2md CLI 스크립트 실행법 (search_kds, render_page 등)"]
        E["예제집 원문 검증 우선 5단계 & 신기준 재계산 상세 프로토콜"]
        F["권장 모듈 레이어 분할 표준 아키텍처"]
    end

    Layer1 -.->|"구체적 CLI 명령어/절차 필요 시에만 view_file"| Layer2
```

### 2.1 4대 쇄신 원칙 상세 대조

| 항목 | 기존 방식 (AS-IS) | 쇄신 방식 (TO-BE) | 개선 효과 |
|:---|:---|:---|:---|
| **1. 문서 열람 규칙** | `docs/10, 16, 07` 무조건 선행 강제 열람 | **무조건 강제 열람 전면 폐지**.<br>오직 `요구사항X.md`만 즉시 열람하고, docs는 모르는 내용이 나올 때만 찾아보는 **JIT 온디맨드 사전**으로 전환 | • 시작 토큰 **35,000+ $\rightarrow$ 3,000 토큰 이하**로 90% 절감<br>• 모델 주의력(Attention)의 100%를 실제 구현 코드에 집중 |
| **2. docs/10 연동 모델** | 매번 통째로 읽히거나 무시됨 | **2계층 분리 (헌법 요약 vs 상세 사전)**.<br>`AGENTS.md`에 핵심 5대 원칙 1줄 압축 상시 탑재, 세부 절차는 `docs/10` 온디맨드 참조 | • 핵심 철학(Zero-Dependency, 0.1% 오차 등) 100% 보존<br>• 토큰 낭비 0 |
| **3. 실행 완주 범위** | Step 1개(예: 엔진)만 하고 무조건 멈춤 (`Stop Protocol`, docs/16) | **단일 마스터 요구사항 100% 완주**.<br>요구사항 23과 같은 1부재 마스터 명세서의 전 체크리스트(Step 1~4)를 한 번에 끝까지 자율 완주 | • 수동 프롬프트 호출 횟수 **5회 $\rightarrow$ 1회**로 단축<br>• `docs/16` 정식 보관(`docs/@@OLD/`) 처리 완료 |
| **4. 검증 및 완료 보고** | 마크다운 3자 오차표, raw 로그 등 텍스트 증거 보고서 강제 | **Pytest 자동 단언문(TDD) 중심**.<br>`test_xxx_benchmark.py`의 `assert abs(calc - ans)/ans < 0.001` 통과 및 터미널 Exit Code 0으로 완료 확정 | • 환각성 텍스트 보고서 낭비 제거<br>• 기계적으로 증명되는 100% 신뢰성 확보 |

---

## 3. 신규 `AGENTS.md` 반영 전문 (Final Specification)

아래 내용으로 `.agents/AGENTS.md`를 전면 교체 반영합니다:

```markdown
# AltDP_3rd Master Agent Guide (AGENTS.md)

본 문서는 **AltDP_3rd (KDS 국가건설기준 웹 부재설계 시스템)** 에이전트의 핵심 행동 강령이자 초경량 라우터(Router)입니다.

---

## 1. /goal 원클릭 실행 핵심 규칙 (Single-Command Execution)

사용자가 `/goal agents.md를 읽고 요구사항X를 구현해줘` 지시를 내리면, 에이전트는 다음 흐름으로 작업을 완주합니다:

1. **지정된 명세서 즉시 진입**:
   - `docs/`의 대형 문서들을 사전에 통째로 읽지 마십시오 (토큰 낭비 금지).
   - 사용자가 지정한 **[`요구사항/요구사항X.md`]**를 열람(`view_file`)하여 목표와 작업 체크리스트를 확인하십시오.
   - (요구사항 번호가 지정되지 않은 경우 [`요구사항/PROJECT_PROGRESS.md`]의 [차기 즉시 작업]을 수행)
2. **단일 마스터 연속 자율 완주 (Run-to-Finish)**:
   - 중간에 임의로 멈추지 말고, 요구사항 문서 내의 체크리스트(Step 1 Core/엔진 ~ Step 4 UI 4-Pane/온라인 전환)를 순차적으로 모두 완수하십시오.
3. **Pytest TDD 기반 검증 (0.10% 오차 무결성)**:
   - 텍스트 증거 보고서를 길게 작성하지 마십시오.
   - `pytest tests/benchmarks/`에서 공인 예제집 대비 **오차 ≤ 0.10%** 통과(Exit Code 0)로 엔지니어링 무결성을 입증하십시오.
4. **1 커밋 & 원격 푸시 & 외부 기억 갱신**:
   - 구현 완료 즉시 [`요구사항/PROJECT_PROGRESS.md`]의 상태(`[x]`)와 최신 커밋을 갱신하고, `git commit` 및 `git push origin main`까지 완료한 뒤 보고하십시오.

---

## 2. 도메인별 온디맨드 기술 사전 (JIT Reference Router)

문서 전체를 미리 읽지 말고, **구현 중 특정 지식이나 규격이 필요할 때만 해당 문서의 관련 섹션을 열람(`view_file`)**하십시오:

* 📖 **KDS 연동·예제집 검증 상세 절차 & 모듈 레이어 가이드**: [`docs/10`](../docs/10_agent_development_protocols.md)
* 📋 **61종 원본앱 부재 매핑 (C 함수/심볼/다이얼로그 SSOT)**: [`docs/04`](../docs/04_master_original_app_modules_comprehensive_catalog.md)
* 💻 **4-Pane 워크스페이스 레이아웃 & 프론트엔드 UI 표준**: [`docs/07`](../docs/07_web_application_ui_ux_specification.md)
* 📚 **단면 형강 DB (.sdb) & 재료 규격**: [`docs/03`](../docs/03_section_db_specification.md)
* 📑 **순백색 A4 KaTeX 구조계산서 표준 양식**: [`docs/14`](../docs/14_structural_calculation_report_specification.md)
* 🔬 **2D FEM 평판·지반 솔버 및 수치 이론**: [`docs/15`](../docs/15_fem_analysis_and_external_solver_specification.md)
* 📌 **프로젝트 전체 진행 현황 및 외부 기억**: [`요구사항/PROJECT_PROGRESS.md`](../요구사항/PROJECT_PROGRESS.md)

---

## 3. 핵심 엔지니어링 행동 원칙 (Core Invariants)

1. **Zero-Dependency & 자체 자산화**:
   - `original_src/`, `decompiled_src/`는 Read-Only 레퍼런스입니다. 런타임 코드는 외부 DLL/바이너리 의존 없는 순수 Python 패키지를 유지합니다.
2. **KDS 3자 삼각 대조 (오차 ≤ 0.10%)**:
   - `[원본 소스/매뉴얼]` ↔ `[현행 KDS 신기준 재계산 예제집]` ↔ `[AltDP_3rd 엔진]` 3자 대조 오차 0.10% 이하 엄수.
   - 예제집이 구 기준일 경우 현행 KDS 신 기준으로 재계산된 결과값만을 단일 검증자료로 채택합니다.
3. **1부재 1마스터 요구사항 완주 원칙**:
   - 부재 개발 시 수십 개의 하위 문서를 만들지 않고, 90~150줄 내외의 단일 마스터 체크리스트 문서(`요구사항XX_부재명.md`)로 일원화하여 한 번에 완주합니다.
4. **포팅 우선 & 사후 리팩토링 (Anti-Superfile 실용주의)**:
   - 개발 도중 인위적인 파일 라인 수 제한으로 흐름을 끊지 않으며, 기능 완수 및 오차 검증 후 추후 리팩토링 단계에서 체계적으로 분할합니다.
5. **1이슈 1작업 격리 (Bug Fix Protocol)**:
   - 버그 픽스 및 결함 조치는 원인 규명과 회귀 방지를 위해 1가지 이슈마다 독립 작업 단위로 분리 검증합니다.
6. **기존 소스 재활용 & 토큰 효율성**:
   - `src/core/tracer.py`, `src/core/geometry.py`, `ProjectStore`, 공통 모듈 및 UI 컴포넌트를 적극 재활용합니다.
7. **테스트 필수 vs 생략 기준**:
   - 🔴 **테스트 필수**: 엔진(`src/engine/`), 스키마/API(`src/api/`), 벤치마크(`tests/benchmarks/`) 수정 시 즉시 `pytest` 실행.
   - 🟢 **테스트 생략**: 순수 문서(`.md`), 주석, 단순 스타일 수정 시 테스트를 생략하여 실행 속도 극대화.
```

---

## 4. 공정별 세부 구현 과제

### Step 1: `.agents/AGENTS.md` 전면 교체 적용
- [x] 원본 백업본 생성: `.agents/@@OLD/AGENTS_backup_260909.md` 및 `docs/@@OLD/AGENTS_backup_260909.md` 완료.
- [x] 제3절의 최종 개정안으로 `.agents/AGENTS.md`를 덮어쓰기 적용 완료.
- [x] 상단의 4만 토큰 강제 열람 규약(`🚨 필수 선행 열람 규약`) 및 `docs/10, 16, 07` 강제 조항 영구 제거 완료.

### Step 2: `docs/16` 보관 처리
- [x] `docs/16_goal_micro_execution_protocol.md` $\rightarrow$ `docs/@@OLD/16_goal_micro_execution_protocol.md` 보관 이동 완료.

### Step 3: `docs/10` 2계층 분리 위상 정립
- [x] `docs/10_agent_development_protocols.md`를 상시 필수 필독서에서 "필요할 때만 찾는 온디맨드 How-To 백과사전"으로 위상 정리 완료.
- [x] `docs/10` 제2절 2항을 "1부재 1마스터 요구사항 원칙"으로 갱신 완료.
- [x] `AGENTS.md` 제2절 라우터에 1순위로 링크 제공 완료.

### Step 4: `요구사항/PROJECT_PROGRESS.md` 실행 명령문 표준화
- [x] 차기 작업(Phase 23 RC 기둥 등)의 실행 명령문을 모두 다음 표준 형식으로 통일 완료:
  ```text
  /goal agents.md를 읽고 요구사항 23을 구현해줘
  ```

---

## 5. 수용 기준 (Acceptance Criteria)

1. [x] **[토큰 경량화]**: AI 에이전트가 새 세션에서 작업을 시작할 때 `docs/`의 수만 토큰을 사전 로딩하지 않고, 지정된 `요구사항X.md`만 즉시 열람하여 실행에 착수함.
2. [x] **[실행 완주성]**: `/goal agents.md를 읽고 요구사항 23을 구현해줘` 실행 시 중간 정지(Stop Protocol) 없이 엔진 $\rightarrow$ 벤치마크 TDD $\rightarrow$ 4-Pane UI 연동까지 단일 컨텍스트로 완주함.
3. [x] **[문서 동기화]**: `AGENTS.md`, `PROJECT_PROGRESS.md`, `docs/10` 간의 지침 불일치 0건.
