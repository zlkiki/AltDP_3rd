# AltDP_3rd (Midas Design+ Reverse Engineering & Web Migration) - Master Agent Guide (AGENTS.md)

본 문서는 **AltDP_3rd (Midas Design+ 리버스 엔지니어링 기반 KDS/국가건설기준 웹 부재설계 시스템)** 프로젝트에서 작업하는 AI 에이전트(Antigravity / Gemini)의 핵심 원칙, 규약 및 워크플로우를 정의합니다.

---

## 1. 프로젝트 목적 및 에이전트 미션

* **프로젝트명**: AltDP_3rd (Web-based Structural Member Design Platform)
* **프로젝트 핵심 목적**:
  * 기존 상용 건축 구조설계 데스크톱 프로그램인 **Midas Design+(`Design+.exe`)의 모든 기능, 부재설계/검토 알고리즘, 단면 DB 및 계산서 시스템을 모던 AltDP 웹 애플리케이션으로 100% 포팅(Full Web Migration)**하는 것.
* **에이전트 미션**:
  1. 원본 바이너리(`original_src/Midas Design+`)에서 추출된 **47,000+ C++ 심볼 및 역공학 자산(`decompiled_src/`)을 Ground Truth(정답 기준)로 삼아 모든 부재설계 알고리즘, 엣지 케이스 수식, 수치해석 노하우를 무결하게 웹 엔진으로 포팅**.
  2. **RC(철근콘크리트), Steel(철골), SRC(철골철근콘크리트), Aluminum(알루미늄), 기초(Footing), 접합부(Connection), 옹벽/지하외벽** 등 전 부재에 대한 **KDS 14 20 00(콘크리트), KDS 14 31 00(강구조), KDS 41 00 00(건축구조기준) 설계 파이프라인**을 모던 웹 UI로 완전 구현.
  3. 단면 제원 입력, 2D/3D 대화형 배근도 및 응력 분포 렌더링, P-M 상관도 곡선, 부재 안전성 자동 판정, A4 표준 구조계산서 출력까지 웹 브라우저에서 원클릭 완결.

---

## 2. 초고속 파일 라우팅 맵 (0.1s Fast Routing Index)

> 💡 기능 구현 및 수식 분석 시 전체 검색(Grep)을 최소화하고 아래 지정된 대상 파일로 즉시 직행합니다.

| 도메인 / 부재 | 원본 C++ 바이너리 심볼 레퍼런스 | 기술 문서 (SSOT) | 주요 신규 구현 파일 및 역할 |
|---|---|---|---|
| **RC 보 / 기둥 / 전단벽** | [`decompiled_src/DPLUS_RCS.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_RCS.dll_symbols.txt) (`CRCSCodeCheck::CHK_BBBE`, `CHK_BCCO`, `CHK_BWUW`) | [`docs/04_rc_design_specification.md`](file:///f:/PyProject/re-DP/docs/04_rc_design_specification.md) | `src/engine/rc/beam.py`, `column.py`, `wall.py` (휨/전단/P-M 상관도) |
| **RC 슬래브 / 기초 / 옹벽** | [`decompiled_src/DPLUS_RCS.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_RCS.dll_symbols.txt) (`CRCSCodeCheck::CHK_SLAB`, `CHK_UFDN`, `CHK_URAB`) | [`docs/04_rc_design_specification.md`](file:///f:/PyProject/re-DP/docs/04_rc_design_specification.md) | `src/engine/rc/slab.py`, `footing.py`, `retaining_wall.py` (지반반력, 2방향 전단) |
| **철골 보 / 기둥 / 가새** | [`decompiled_src/DPLUS_STEEL.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_STEEL.dll_symbols.txt) (`CSTLCodeCheck::CHK_SBM`, `CHK_SCOL`) | [`docs/05_steel_design_specification.md`](file:///f:/PyProject/re-DP/docs/05_steel_design_specification.md) | `src/engine/steel/beam.py`, `column.py`, `brace.py` (좌굴, LTB, 휨/압축 조합) |
| **철골 접합부 / 베이스플레이트** | [`decompiled_src/DPLUS_STEEL.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_STEEL.dll_symbols.txt) (`CSteelBoltConnection`, `CBasePlate`) | [`docs/05_steel_design_specification.md`](file:///f:/PyProject/re-DP/docs/05_steel_design_specification.md) | `src/engine/steel/connection.py`, `baseplate.py` (볼트/용접/지압 검토) |
| **SRC / 알루미늄 설계** | [`decompiled_src/DPLUS_SRC.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_SRC.dll_symbols.txt)<br>[`decompiled_src/DPLUS_ALU.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_ALU.dll_symbols.txt) | [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/re-DP/docs/06_python_engine_architecture_specification.md) | `src/engine/src_composite/`, `src/engine/alu/` |
| **단면 형강 DB (.sdb)** | [`original_src/Midas Design+/Dbase/`](file:///f:/PyProject/re-DP/original_src/Midas%20Design+/Dbase/) (`KS.sdb`, `AISC.sdb` 등) | [`docs/03_section_db_specification.md`](file:///f:/PyProject/re-DP/docs/03_section_db_specification.md) | `src/engine/db/sdb_parser.py`, `section_db.py` (형강 제원 및 기하학적 성질) |
| **P-M 상관도 & 수치 솔버** | [`decompiled_src/DPLUS_DB.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_DB.dll_symbols.txt)<br>[`DgnSolver/mfsolver.exe`](file:///f:/PyProject/re-DP/original_src/Midas%20Design+/DgnSolver/mfsolver.exe) | [`docs/01_system_architecture.md`](file:///f:/PyProject/re-DP/docs/01_system_architecture.md) | `src/engine/solver/pm_diagram.py`, `fiber_section.py` (파이버 분할 수치적분) |
| **Web UI & 2D/3D 캔버스** | - | [`docs/07_web_application_ui_ux_specification.md`](file:///f:/PyProject/re-DP/docs/07_web_application_ui_ux_specification.md) | `src/web/`, `src/web/static/js/renderer2d.js`, `pm_chart.js` |
| **A4 구조계산서 출력** | [`decompiled_src/DPLUS_RCS.dll_symbols.txt`](file:///f:/PyProject/re-DP/decompiled_src/DPLUS_RCS.dll_symbols.txt) (`CMSOffice`) | [`docs/01_system_architecture.md`](file:///f:/PyProject/re-DP/docs/01_system_architecture.md) | `src/report/generator.py`, `src/report/templates/` (인쇄/PDF 표준 계산서) |

---

## 3. 핵심 개발 및 행동 원칙 (Core Rules)

### 3.1. 소스코드 격리 및 참조 원칙 (Isolation Rules)
* **`original_src/` 및 `decompiled_src/`는 오직 읽기 전용(Read-Only) 레퍼런스**:
  * 원본 실행 파일, DLL 바이너리 및 심볼 파일은 설계 알고리즘 분석과 검증의 정답(Ground Truth)으로만 사용하며, 임의로 변형하지 않습니다.
* **신규 개발 엔진(`src/`)의 독립성**:
  * 신규 구현은 Wibu Dongle이나 Windows 전용 MFC DLL에 일체 의존하지 않는 **순수 Python/Web 기반 모던 아키텍처**로 독립 작성합니다.

### 3.2. KDS 국가건설기준 및 kcsc2md 자산화 연동 규약 (KDS Reference & Self-Healing Protocol)
* **KDS 설계기준 준수 대상**:
  * 콘크리트: **KDS 14 20 00** (KDS 14 20 10 휨/압축, KDS 14 20 22 전단/비틀림, KDS 14 20 54 앵커 등)
  * 강구조: **KDS 14 31 00** (KDS 14 31 10 강도설계, 접합부 등)
  * 건축구조기준: **KDS 41 00 00**
* **인접 워크스페이스 `kcsc2md` Ground Truth 자산 및 도구 연동**:
  1. **고품질 마크다운 기준서 (`f:/PyProject/kcsc2md/output/kds_md/`)**: 국토부 원본 HWPX와 1:1 수식 주입(`LaTeX`)이 완료된 분할 마크다운을 설계식의 절대적 정답 기준(Ground Truth)으로 삼습니다.
  2. **추출 이미지 자산 (`f:/PyProject/kcsc2md/output/KDS_ImageExtracted/`)**: HWP 원문에서 무손실 추출된 표준 배근도, 다이어그램 이미지를 웹 UI 및 도움말 렌더링에 직접 연동/활용합니다.
  3. **공식 구조설계 예제집 (`f:/PyProject/kcsc2md/output/예제집/`)**: 콘크리트학회/강구조학회 공인 예제집 마크다운을 단위 테스트(`tests/engine/`) 검증 벤치마크 데이터로 활용합니다.
  4. **0.01s 초고속 KDS 조항 라우터 (`kds-inspector`)**:
     ```bash
     python ../kcsc2md/.agents/skills/kds-inspector/scripts/search_kds.py --code "14 20 10" --query "등가직사각형"
     ```
  5. **HWPX 원본 수식/표 검증기 (`hwpx-inspector`)**:
     ```bash
     python ../kcsc2md/.agents/skills/hwpx-inspector/scripts/extract_formula.py --code "14 20 10" --keyword "alpha1"
     ```
* **우선 치유(Patch-First) 및 Self-Healing 환류 프로토콜**:
  * `AltDP_3rd` 엔진 개발 및 KDS 검증 중 마크다운 기준서의 수식/표 오탈자나 누락을 발견한 경우, **`AltDP_3rd` 코드를 임의로 우회 수정하지 않고 먼저 `kcsc2md`의 Self-Healing 패치 도구(`patch_kds_md.py`)를 통해 원본 마크다운 자산을 영구 치유한 후 최신화된 기준을 반영**합니다.
* **0.1% 오차 무결성 검증 (Cross-Validation)**:
  * 원본 Midas Design+ 계산 결과, `kcsc2md` 공식 예제집 해답, 신규 AltDP_3rd 엔진 계산치를 삼각 대조하여 **오차 0.1% 미만의 무결성**을 입증합니다.
* **Zero-Dependency 런타임 원칙**:
  * `kcsc2md` 자산과 도구는 개발/검증/빌드 타임의 Ground Truth 레퍼런스로 활용하며, `AltDP_3rd`의 프로덕션 런타임 코드는 외부 파일시스템에 의존하지 않는 독립 파이썬 패키지를 유지합니다.

### 3.3. 디렉토리 수명 및 스크래치 관리 규칙 (Scratch Rule)
* **`scratch/` 폴더 휘발성 원칙**:
  * `scratch/` 디렉토리는 임시 테스트 스크립트 공간으로, 사용자에 의해 언제든 삭제될 수 있습니다.
  * 영구 보존해야 하는 코드 및 문서는 반드시 `src/` 또는 `docs/`에 배치합니다.

### 3.4. 요구사항 & 문서 라이프사이클 (AltDP 표준 규약)
* **요구사항 문서 생성 규칙 (경량화)**: 
  * 사용자가 채팅으로 메모형식의 요청사항을 전달하며 "요구사항 문서 만들어줘" 등을 요청할 때는 **별도의 Implementation Plan 아티팩트나 구현 계획을 생성하지 않고**, 오직 요구사항 정리 및 `요구사항/요구사항XX.md` 파일 생성에만 집중합니다. (일련번호는 `요구사항/@@OLD/` 마지막 번호의 다음 번호 부여)
* **대규모 요구사항 사전 점검 및 하위 문서 세분화 제안 (Scope Partitioning)**:
  * 작업 범위가 다수 부재/모듈(3개 이상 레이어/파일 10개 이상 등)에 걸쳐 있어 구현 누락 위험이 높다고 판단되면:
    1. 사용자에게 대규모 구현에 따른 **누락 위험을 사전에 알리고 확인을 요청**.
    2. 단일 요구사항을 하위 문서(예: `요구사항XX-1.md`, `요구사항XX-2.md` 또는 명확한 독립 Phase)로 **세분화하여 단계별로 구분 진행할 것을 제안**.
* **요구사항 전수 체크리스트 검증 의무 (Zero-Omission Verification)**:
  * 요구사항 문서 작업 시 문서 내 세부 항목과 검증 기준(Acceptance Criteria)을 1:1 체크리스트로 대조 검증하고 누락 0건 확인 후 완료 보고.
* **명시적 요청 시에만 완료/아카이빙**:
  * 사용자 요청 시에만 `요구사항/` 파일을 `요구사항/@@OLD/요구사항XX-YYMMDD_HHMM.md`로 이동 및 아카이빙.
* **README.md 일괄 업데이트**:
  * 중간에 임의 수정하지 않고 사용자 명시적 요청 시에만 일괄 갱신.
* **기술 문서는 실시간 최신화**:
  * `docs/` 내의 기술 문서는 아키텍처/구조 변경 시 지속 동기화.

### 3.5. Goal 주도형 단계적 연속 구현 규약 (Goal-Driven Continuous Partitioned Execution)
* **작은 단위 분할 실행**:
  * `/goal` 등으로 전체 작업을 지시받았을 때, 토큰 효율과 집중력을 위해 분할된 하위 Phase 단위(`요구사항XX-1` 등)로 순차 실행.
* **단계별 무결성 자율 전진 (Phase-by-Phase Verification)**:
  1. 각 하위 Phase별 지정된 모듈/부재만 정밀 구현.
  2. Acceptance Criteria 및 `pytest` 100% 통과 확인.
  3. 완료 즉시 다음 Phase로 중단 없이 자율 진입하여 연속 작업.

### 3.6. 버그 수정 및 개별 이슈 대응 규약 (Bug Fix & Issue Resolution Protocol)
* **1이슈 1Phase 원칙**:
  * 버그 픽스 및 결함 조치는 1가지 이슈마다 독립된 Phase로 구별하여 원인 규명 및 수정 후 `pytest` 확인.

### 3.7. 도메인별 3대 Pytest 초고속 검증 규약 (Domain-Specific Pytest Protocol)
* 전체 테스트를 매번 실행하지 않고 작업 도메인 디렉토리만 타겟팅하여 0.5~1.5초 내에 신속 검증합니다.
  * **설계 엔진 작업 시**: `pytest tests/engine/`
  * **API 라우트 작업 시**: `pytest tests/api/`
  * **UI / 템플릿 작업 시**: `pytest tests/ui/`
  * **마스터 완료 시**: `pytest`

### 3.8. 작업별 모델 활용 전략 (Model Tier Guidelines)
1. **High 모델 (Flash High / Pro)**: P-M 상관도 비선형 수치해석, KDS 규준 복합 하중 조합 수식 유도, C++ 심볼 바이너리 역공학
2. **Medium 모델 (Flash Medium)**: 파이썬 부재 계산 모듈 구현, 단위 테스트 작성, UI 컴포넌트 개발
3. **Low 모델 (Flash Low / Lite)**: 단순 파일 조회, Git 커밋/푸시 실행

---

## 4. 세부 기술 문서 및 인벤토리 맵 (Documentation References)

* 📑 **[프로젝트 구조 및 파일 인벤토리 명세 (SSOT)](file:///f:/PyProject/re-DP/docs/프로젝트_구조_및_파일_인벤토리_명세.md)**: 47,110개 복원 심볼 및 모듈별 역할 명세
* 📐 **[전체 시스템 아키텍처](file:///f:/PyProject/re-DP/docs/01_system_architecture.md)**: 전체 시스템 구조 및 5대 계층 흐름도
* 🔍 **[바이너리 리버스 엔지니어링 명세](file:///f:/PyProject/re-DP/docs/02_binary_reverse_engineering_specification.md)**: Midas Design+ 바이너리 구조 및 노출 심볼 인벤토리
* 📚 **[단면 형강 DB 명세](file:///f:/PyProject/re-DP/docs/03_section_db_specification.md)**: .sdb 바이너리 포맷 파싱 및 JSON/SQLite 변환 사양
* 🧱 **[RC 부재설계 기준서 (KDS 14 20 00)](file:///f:/PyProject/re-DP/docs/04_rc_design_specification.md)**: 보, 기둥, 슬래브, 전단벽, 기초, 옹벽 수식집
* 🏗️ **[철골 부재설계 기준서 (KDS 14 31 00)](file:///f:/PyProject/re-DP/docs/05_steel_design_specification.md)**: 철골보, 기둥, 가새, 접합부, 베이스플레이트 수식집
* 🚀 **[Python 독립 엔진 아키텍처 명세서](file:///f:/PyProject/re-DP/docs/06_python_engine_architecture_specification.md)**: 백엔드/클라이언트 코어 엔지니어링 계산 엔진 사양
* 💻 **[Web Application UI/UX 명세서](file:///f:/PyProject/re-DP/docs/07_web_application_ui_ux_specification.md)**: AltDP 모던 웹 UI, 2D/3D 부재 렌더러 및 P-M 상관도 차트
* 🧪 **[Pytest 도메인별 3대 테스트 가이드](file:///f:/PyProject/re-DP/docs/08_pytest_testing_guide.md)**: 단위/통합 테스트 규약
* 🔗 **[KDS 국가건설기준 연동 가이드 (kcsc2md)](file:///f:/PyProject/kcsc2md/docs/외부프로젝트_연동_및_조회_가이드.md)**: KDS 기준 Ground Truth 조회 표준
