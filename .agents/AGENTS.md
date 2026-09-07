# AltDP_3rd Master Agent Guide (AGENTS.md)

본 문서는 **AltDP_3rd (Midas Design+ 리버스 엔지니어링 기반 KDS 국가건설기준 웹 부재설계 시스템)** 개발 에이전트의 핵심 행동 규약이자 초고속 인덱스 가이드입니다.

> [!IMPORTANT]
> **🚨 필수 선행 열람 규약 (Mandatory Protocol)**:
> 새로운 세션 시작이나 작업 착수 시, 모든 세부 개발 프로토콜과 행동 규약의 단일 진실 공급원(SSOT)인 **[`docs/10_agent_development_protocols.md`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)** 및 Goal 마이크로 공정 지침인 **[`docs/16_goal_micro_execution_protocol.md`](file:///f:/PyProject/AltDP_3rd/docs/16_goal_micro_execution_protocol.md)**를 **반드시 함께 열람(`view_file`)**해야 합니다.

---

## 1. 프로젝트 미션 & 4대 포팅 참조 우선순위 (SSOT Hierarchy)

* **목표**: Midas Design+(`Design+.exe`)의 모든 설계/검토 알고리즘, 단면 DB, P-M 수치해석 및 계산서 시스템을 **순수 Python/Web(KDS 14 20 00 / 14 31 00 / 41 00 00)**으로 100% 웹 마이그레이션.
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `1순위 (최우선)`: **추출된 원본 소스** (`decompiled_src/core_routines/*.c`, `symbols/*.txt`, `binaries/`)
     - 원본 프로그램의 실제 연산, 분기 조건, 내부 수치 처리의 **절대적 1순위 Ground Truth**.
  2. `2순위`: **매뉴얼 및 도움말** (`decompiled_src/manuals/`, Midas Design+ 공식 기술 매뉴얼)
     - 공식 설계 이론, 약산/엄밀 해석 옵션, 파라미터 정의, 벤치마크 예제.
  3. `3순위`: **kcsc2md 공식 예제집** (`F:/PyProject/KCSC2MD/output/예제집/`)
     - 콘크리트구조 학회기준 예제집(2020) & 강구조설계예제집(2019) 등 공인 예제집 기반 **계산 오차 $\le 0.10\%$ 검증용 실무 벤치마크 정답 데이터**.
  4. `4순위`: **kcsc2md 국가건설기준** (`F:/PyProject/KCSC2MD/output/kds_md/`)
     - KDS 14 20 00 / 14 31 00 / 41 00 00 국토교통부 표준 원문 & LaTeX 수식 (기준서 오류 발견 시 `patch_kds_md.py` 선 치유(Patch-First) 원칙 적용).
* **무결성 3자 삼각 대조 원칙**:
  - `[원본 소스/매뉴얼]` $\leftrightarrow$ `[kcsc2md 예제집]` $\leftrightarrow$ `[AltDP_3rd 엔진]` 3자 삼각 대조로 오차 $\le 0.10\%$ 엄수.
  - 외부 파일시스템이나 런타임 DLL/Dongle에 의존하지 않는 독립(Zero-Dependency) 패키지 유지.

---

## 2. 0.1s 초고속 파일 라우팅 맵

| 도메인 / 부재 | 바이너리 심볼 레퍼런스 | 기술 문서 (SSOT) | 주요 구현 파일 (`src/`) |
|---|---|---|---|
| **RC 보 / 기둥 / 전단벽** | `decompiled_src/DPLUS_RCS.dll_symbols.txt` | [`docs/17 (4대 SSOT)`](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md) | `src/engine/rc/beam.py`, `column.py`, `wall.py` |
| **RC 슬래브 / 기초 / 옹벽** | `decompiled_src/DPLUS_RCS.dll_symbols.txt` | [`docs/17 (4대 SSOT)`](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md) | `src/engine/rc/slab.py`, `footing.py`, `retaining_wall.py` |
| **철골 보 / 기둥 / 가새 / 개구부** | `decompiled_src/DPLUS_STEEL.dll_symbols.txt` | [`docs/17 (4대 SSOT)`](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md) | `src/engine/steel/beam.py`, `column.py`, `brace.py`, `web_opening.py`, `compactness.py` |
| **철골 접합부 / 베이스플레이트 / 엔드플레이트** | `decompiled_src/DPLUS_STEEL.dll_symbols.txt` | [`docs/17 (4대 SSOT)`](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md) | `src/engine/steel/connection.py`, `baseplate.py`, `endplate.py` |
| **SRC / 알루미늄 / 보수보강** | `decompiled_src/DPLUS_SRC.dll_symbols.txt`, `DPLUS_ALU.dll_symbols.txt` | [`docs/06_python_engine_architecture_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md) | `src/engine/src_composite/`, `src/engine/alu/`, `src/engine/rfm/` |
| **단면 형강 DB (.sdb) & 재료 / 하중조합** | `original_src/Midas Design+/Dbase/` | [`docs/03_section_db_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/03_section_db_specification.md) | `src/engine/db/sdb_parser.py`, `section_db.py`, `materials.py`, `load_comb.py` |
| **P-M 상관도 & 수치 솔버** | `decompiled_src/DPLUS_DB.dll_symbols.txt` | [`docs/01_system_architecture.md`](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md) | `src/engine/solver/pm_diagram.py`, `fiber_section.py` |
| **2D FEM 평판 휨 & 지반/접촉 솔버** | `original_src/Midas Design+/DgnSolver/` | [`docs/15_fem_analysis_and_external_solver_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) | `src/engine/fem/` (`element_dkmq.py`, `solver_plate.py`, `foundation_fem.py`, `baseplate_fem.py`) |
| **Web UI & 2D/3D 캔버스** | `decompiled_src/DPLUS_VDraw.dll_symbols.txt` | [`docs/07_web_application_ui_ux_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md), [`docs/13_midas_design_plus_original_ui_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md) | `src/web/`, `src/web/static/js/renderer2d.js`, `pm_chart.js`, `app.js` |
| **A4 구조계산서 출력 (HTML/PDF/Excel)** | `CMSOffice`, `CMSExcel` 심볼 | [`docs/14_structural_calculation_report_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md) | `src/report/generator.py`, `src/report/templates/` |
| **전체 61종 모듈 카탈로그 & 4대 자산 SSOT** | `Menu.ini`, `DLG_*.ini`, 20개 DLL | [`docs/17_master_midas_modules_comprehensive_catalog.md`](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md) | `docs/17_master_midas_modules_comprehensive_catalog.md`, `src/web/static/js/catalog.js` |
| **FastAPI REST API 라우트** | - | [`docs/01_system_architecture.md`](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md) | `src/api/routes/` (`rc.py`, `steel.py`, `rc_foundation.py`, `rc_wall_slab.py`, `special.py`, `fem.py`, `db.py`, `report.py`, `interop.py`, `quantity.py`, `international.py`) |

---

## 3. 핵심 개발 및 행동 원칙 (Core Rules)

1. **소스 격리 & Zero-Dependency**:
   - `original_src/`, `decompiled_src/`는 Read-Only Ground Truth.
   - Wibu Dongle/MFC DLL 의존 없는 독립 Python 패키지 개발.
2. **KDS 기준 & 0.1% 오차 무결성 (3자 삼각 대조)**:
   - `[원본 소스/매뉴얼]` $\leftrightarrow$ `[kcsc2md 예제집]` $\leftrightarrow$ `[AltDP_3rd 엔진]` 교차 대조 (0.10% 이하 오차).
   - 기준서 오류 발견 시 `kcsc2md` 선 치유(Patch-First) 원칙 적용.
3. **증거 강제 제출 규약 (Proof-First Mandate)**:
   - 완료 주장 시 텍스트 보고 금지. 반드시 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 (`docs/16`).
4. **2단계 5정밀 마이크로 공정 준수**:
   - 부재 개발 시 Step 1~5(엔진 $\rightarrow$ 폼 $\rightarrow$ 캔버스 $\rightarrow$ 계산서 $\rightarrow$ 통합) 단독 완수 후 즉시 정지(Stop Protocol) (`docs/16`).
5. **소스 재활용 & 토큰 효율성 (Engineering Precision)**:
   - 검증된 기존 계산 로직, 공통 모듈, 단면 DB 파서, UI 컴포넌트 적극 재활용 (중복 구현 금지).
6. **요구사항 라이프사이클 (경량화 & 분할)**:
   - 요구사항 문서 생성 요청 시 별도 Plan 아티팩트 없이 `요구사항/요구사항XX.md` 직접 작성.
   - 대규모 작업(파일 10개 이상/3개 이상 레이어)은 사전 확인 후 하위 Phase로 분할 제안.
   - 완료 아카이빙(`요구사항/@@OLD/`) 및 `README.md` 갱신은 사용자 명시적 요청 시에만 수행.
7. **Goal 주도형 단계적 연속 구현 (Goal-Driven Partitioned Execution)**:
   - `/goal` 전체 지시 시 단일 컨텍스트 폭주 방지를 위해 하위 Phase 문서(`요구사항XX-1`, `XX-2`) 단위로 순차 실행.
   - 각 하위 Phase의 체크리스트 및 `pytest` 100% 통과 즉시 다음 Phase로 중단 없이 자율 진입하여 마스터 요구사항 완수.
8. **버그 수정 및 개별 이슈 대응 (1이슈 1Phase 원칙)**:
   - 버그 픽스 및 결함 조치는 원인 규명과 영향도 검증을 위해 1이슈 1Phase 격리 원칙 적용.
   - 경미한 연관 버그는 최대 1~3개 묶음 가능하나, 일반 요구사항 내 버그 수정도 독립 실행 단위로 분리 검증.
9. **도메인별 3대 Pytest 검증 및 실행 판단 기준**:
   - **🔴 테스트 필수 (Must Test)**: 설계 엔진(`src/engine/`), API 라우트(`src/api/`), P-M 솔버, 버그 픽스, 의존성(`requirements.txt`) 수정 시.
     * 설계 엔진: `pytest tests/engine/` (0.5~1.0s)
     * API 라우트: `pytest tests/api/` (0.8s)
     * 계산서 출력: `pytest tests/report/` (0.5s)
     * 전체 검증: `pytest`
   - **🟢 테스트 생략 (Skip Test)**: `docs/` 기술 문서, `요구사항/` 기획 문서, `README.md`, `AGENTS.md` 등 순수 마크다운(`.md`) 작성/수정 및 주석/스타일링 작업 시 테스트 실행을 전면 생략하여 리소스 낭비 방지 ([`docs/08_pytest_testing_guide.md`](file:///f:/PyProject/AltDP_3rd/docs/08_pytest_testing_guide.md) 준수).
10. **수퍼 파일(Superfile) 지양 및 엄격한 모듈화 (Anti-Superfile Rule)**:
    - **파일 크기 상한**: 단일 파일 당 권장 300라인 이하, **최대 500라인 절대 초과 금지** (500라인 근접 시 즉시 서브패키지/모듈로 분할).
    - **단일 책임 원칙 (SRP)**: 수치 계산, 데이터 모델, 검토 오케스트레이션, UI 컴포넌트, 렌더러를 명확히 분리하여 거대 모놀리식 파일 발생 원천 차단.
11. **단위 작업 = 1 커밋 & 원격 푸시 완수**:
    - 단위 작업(Phase/Step) 완료 즉시 1개의 Git 커밋을 생성하고 원격(`git push origin main`)까지 완료.

---

## 4. 상세 기술 문서 및 프로토콜 레퍼런스 (SSOT)

* 🚦 **[16. Goal 마이크로 공정 표준 실행 지침](file:///f:/PyProject/AltDP_3rd/docs/16_goal_micro_execution_protocol.md)** (5대 정밀 공정, 단독 완수 원칙, TDD, Proof-First)
* 📋 **[17. Midas Design+ 61종 전체 모듈 종합 카탈로그 및 4대 자산 인벤토리](file:///f:/PyProject/AltDP_3rd/docs/17_master_midas_modules_comprehensive_catalog.md)** (단일 진실 공급원 SSOT)
* 🎯 **[12. 전 기능 포팅 마스터플랜 (Master Plan)](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md)**
* 📖 **[10. 상세 개발 프로토콜 및 KDS 연동 가이드](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md)** (모델 전략, Self-Healing, 상세 규약)
* 📐 **[01. 전체 시스템 아키텍처 & 파일 인벤토리](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md)** | 🗂️ **[09. 추출 바이너리 및 심볼 자산 명세서](file:///f:/PyProject/AltDP_3rd/docs/09_decompiled_source_and_symbol_inventory.md)**
* 🔍 **[02. 바이너리 역공학 명세](file:///f:/PyProject/AltDP_3rd/docs/02_binary_reverse_engineering_specification.md)** | 📚 **[03. 단면 형강 DB 명세](file:///f:/PyProject/AltDP_3rd/docs/03_section_db_specification.md)** | 📦 **[구 설계기준 요약(04, 05) 보관](file:///f:/PyProject/AltDP_3rd/docs/@@OLD/)**
* 🚀 **[06. Python 독립 엔진 사양](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md)** | 💻 **[07. Web UI/UX 사양](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)** | 🖥️ **[13. Midas Design+ 원본 UI 역공학 사양](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md)** | 📑 **[14. KDS 구조계산서 명세서](file:///f:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md)** | 🔬 **[15. FEM 해석 및 외부 솔버 역공학 사양](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md)**
* 📐 **[101. FEM 솔버 이론 및 정식화 명세서](file:///f:/PyProject/AltDP_3rd/docs/fem/101_fem_engine_theoretical_manual_and_formulation.md)** | 📊 **[102. 기존 솔버 비교 분석 및 벤치마크](file:///f:/PyProject/AltDP_3rd/docs/fem/102_fem_solver_comparative_analysis_and_benchmark.md)** | 🧪 **[08. Pytest 테스트 가이드](file:///f:/PyProject/AltDP_3rd/docs/08_pytest_testing_guide.md)**
