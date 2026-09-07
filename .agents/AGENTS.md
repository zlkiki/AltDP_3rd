# AltDP_3rd Master Agent Guide (AGENTS.md)

본 문서는 **AltDP_3rd (원본앱 리버스 엔지니어링 기반 KDS 국가건설기준 웹 부재설계 시스템)** 개발 에이전트의 핵심 행동 규약이자 초고속 인덱스 가이드입니다.

> [!IMPORTANT]
> **🚨 필수 선행 열람 규약 (Mandatory Protocol)**:
> 새로운 세션 시작이나 AI 모델 교체, 작업 착수 시, 특히 **수직 구현계획(Vertical Slice) 수립 및 요구사항 문서 작성/검토 시**, 모든 세부 개발 프로토콜과 행동 규약의 단일 진실 공급원(SSOT)인 **[`docs/10_agent_development_protocols.md`](../docs/10_agent_development_protocols.md)**, Goal 마이크로 공정 지침인 **[`docs/16_goal_micro_execution_protocol.md`](../docs/16_goal_micro_execution_protocol.md)**, 4-Pane 워크스페이스 및 웹 UI/UX 연동 표준인 **[`docs/07_web_application_ui_ux_specification.md`](../docs/07_web_application_ui_ux_specification.md)**, 그리고 프로젝트 진행 상태, 모델 핸드오버 및 /goal 실행 인덱스 SSOT인 **[`요구사항/PROJECT_PROGRESS.md`](../요구사항/PROJECT_PROGRESS.md)**를 **반드시 함께 열람(`view_file`)**해야 합니다.

---

## 1. 프로젝트 미션 & 4대 포팅 참조 우선순위 (SSOT Hierarchy)

* **목표**: 원본앱(`Design+.exe`)의 모든 설계/검토 알고리즘, 단면 DB, P-M 수치해석 및 계산서 시스템을 **순수 Python/Web(KDS 14 20 00 / 14 31 00 / 41 00 00)**으로 100% 웹 마이그레이션.
* **4대 포팅 참조 우선순위**: **`1순위 추출 소스` > `2순위 매뉴얼/리소스` > `3순위 공인 예제집` > `4순위 국가건설기준`**
  - **3자 삼각 대조**: `[원본 소스/매뉴얼]` ↔ `[kcsc2md 예제집]` ↔ `[AltDP_3rd 엔진]` 3자 삼각 대조로 오차 $\le 0.10\%$ 엄수 및 Zero-Dependency 유지.
  - **선 치유 의무**: 기준서(4순위) 및 공식 예제집(3순위) 오류 발견 시 `kcsc2md` 선 치유(Patch-First) 원칙 적용.
  - *(상세 자산 인벤토리, 검색 스크립트 및 세부 프로토콜은 **[`docs/10 제1절`](../docs/10_agent_development_protocols.md)** 참조)*

---

## 2. 도메인별 기술 문서 라우터 (SSOT Master Index)

부재 개발, 수치 해석 및 UI/UX 작업 시 아래 도메인별 단일 진실 공급원(SSOT) 문서를 열람(`view_file`)하십시오:

* 📋 **61종 전체 모듈 카탈로그 & 소스·심볼·파일 1:1 매핑**: [`docs/04 (전수 SSOT)`](../docs/04_master_original_app_modules_comprehensive_catalog.md)
* 📐 **전체 시스템 아키텍처 & 디렉토리 인벤토리**: [`docs/01`](../docs/01_system_architecture.md) | 🗂️ **추출 바이너리/심볼 명세**: [`docs/09`](../docs/09_decompiled_source_and_symbol_inventory.md)
* 📚 **단면 형강 DB (.sdb) & 재료 규격 명세**: [`docs/03`](../docs/03_section_db_specification.md)
* 💻 **4-Pane 워크스페이스 & 웹 UI/UX 연동 표준**: [`docs/07`](../docs/07_web_application_ui_ux_specification.md)
* 📑 **KDS 표준 순백색 A4 구조계산서 출력 사양**: [`docs/14`](../docs/14_structural_calculation_report_specification.md)
* 🔬 **2D FEM 평판·지반 솔버 & 수치 이론**: [`docs/15`](../docs/15_fem_analysis_and_external_solver_specification.md) | [`docs/fem/101 (정식화)`](../docs/fem/101_fem_engine_theoretical_manual_and_formulation.md) | [`docs/fem/102 (벤치마크)`](../docs/fem/102_fem_solver_comparative_analysis_and_benchmark.md)
* 🚦 **Goal 마이크로 5대 공정 표준 실행 지침**: [`docs/16`](../docs/16_goal_micro_execution_protocol.md)
* 📖 **에이전트 상세 개발 규약 & KDS 연동 가이드**: [`docs/10`](../docs/10_agent_development_protocols.md)
* 🎯 **전 기능 포팅 마스터플랜 (Phase V1~V6 로드맵)**: [`docs/12`](../docs/12_full_feature_porting_master_plan.md)
* 🧪 **Pytest 테스트 가이드**: [`docs/08`](../docs/08_pytest_testing_guide.md)
* 📌 **마스터 진행 현황 및 외부 기억**: [`요구사항/PROJECT_PROGRESS.md`](../요구사항/PROJECT_PROGRESS.md)

---

## 3. 핵심 개발 및 행동 원칙 (Core Rules)

1. **소스 격리 & Zero-Dependency**:
   - `original_src/`, `decompiled_src/`는 Read-Only Ground Truth.
   - Wibu Dongle/MFC DLL 의존 없는 독립 Python 패키지 개발.
2. **KDS 기준 & 0.1% 오차 무결성 (3자 삼각 대조)**:
   - `[원본 소스/매뉴얼]` $\leftrightarrow$ `[kcsc2md 예제집]` $\leftrightarrow$ `[AltDP_3rd 엔진]` 교차 대조 (0.10% 이하 오차).
   - 기준서 및 공식 예제집 오류 발견 시 `kcsc2md` 선 치유(Patch-First) 원칙 적용.
3. **증거 강제 제출 규약 (Proof-First Mandate)**:
   - 완료 주장 시 텍스트 보고 금지. 반드시 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 (`docs/16`).
4. **2단계 5정밀 마이크로 공정 준수**:
   - 부재 개발 시 Step 1~5(엔진 $\rightarrow$ 폼 $\rightarrow$ 캔버스 $\rightarrow$ 계산서 $\rightarrow$ 통합) 단독 완수 후 즉시 정지(Stop Protocol) (`docs/16`).
   - 각 Step 구현 시 **[`docs/07 PART 4`](../docs/07_web_application_ui_ux_specification.md)**의 UI/UX 결합 사양(Step 2 서브탭 폼 & 서브 모달 4종, Step 3 세로 적층형 2단 뷰포트, Step 4 순백색 A4 8단계 KaTeX 계산서, Step 5 4열 100ms 동기화)을 1:1 완벽 준수.
5. **소스 재활용 & 토큰 효율성 (Engineering Precision)**:
   - 검증된 기존 계산 로직, 공통 모듈, 단면 DB 파서, UI 컴포넌트 적극 재활용 (중복 구현 금지).
6. **요구사항 라이프사이클 (경량화 & UI/UX 사전 검토 의무)** ([`docs/10 제2절`](../docs/10_agent_development_protocols.md)):
   - 요구사항 생성 시 별도 Plan 아티팩트 없이 `요구사항/요구사항XX.md` 직접 작성.
   - **수직 슬라이스 작성 시 UI/UX 선행 반영 의무**: [`docs/07 제21절`](../docs/07_web_application_ui_ux_specification.md) 6대 체크리스트(사이드바, 부재매니저, 4대 서브탭, 2단 뷰포트, 순백색 A4, 100ms 동기화) 선행 확인(`view_file`) 및 필수 반영.
   - 대규모 작업(파일 10개 이상/3개 이상 레이어) 사전 확인 후 하위 Phase 분할 제안. 완료 아카이빙 및 README 갱신은 사용자 명시 요청 시에만 수행.
7. **Goal 주도형 단계적 연속 구현** ([`docs/10 제3절`](../docs/10_agent_development_protocols.md), [`docs/16`](../docs/16_goal_micro_execution_protocol.md)):
   - `/goal` 마스터 지시 시 단일 컨텍스트 폭주 방지를 위해 하위 Phase 문서(`요구사항XX-1` 등) 단위로 순차 실행.
   - 각 하위 Phase 체크리스트 및 `pytest` 100% 통과 즉시 다음 Phase로 중단 없이 자율 진입하여 마스터 요구사항 완수.
8. **버그 수정 및 개별 이슈 대응 (1이슈 1Phase 원칙)** ([`docs/10 제4절`](../docs/10_agent_development_protocols.md)):
   - 결함 원인 규명 및 영향도 검증을 위해 1이슈 1Phase 격리 해결 원칙 적용 (경미한 연관 버그는 1~3개 묶음 허용, 일반 요구사항 내 버그 픽스도 독립 실행 단위로 분리 검증).
9. **도메인별 3대 Pytest 검증 및 실행 판단 기준**:
   - **🔴 테스트 필수 (Must Test)**: 설계 엔진(`src/engine/`), API 라우트(`src/api/`), P-M 솔버, 버그 픽스, 의존성(`requirements.txt`) 수정 시.
     * 설계 엔진: `pytest tests/engine/` (0.5~1.0s)
     * API 라우트: `pytest tests/api/` (0.8s)
     * 계산서 출력: `pytest tests/report/` (0.5s)
     * 전체 검증: `pytest`
   - **🟢 테스트 생략 (Skip Test)**: `docs/` 기술 문서, `요구사항/` 기획 문서, `README.md`, `AGENTS.md` 등 순수 마크다운(`.md`) 작성/수정 및 주석/스타일링 작업 시 테스트 실행을 전면 생략하여 리소스 낭비 방지 ([`docs/08_pytest_testing_guide.md`](../docs/08_pytest_testing_guide.md) 준수).
10. **수퍼 파일 주의 및 점진적 리팩토링 (Pragmatic Anti-Superfile)** ([`docs/10 제5절`](../docs/10_agent_development_protocols.md)):
    - **포팅 우선 (인위적 라인수 제한 지양)**: 포팅 흐름 단절 및 오버엔지니어링 방지를 위해 파일 라인 수 강제 제한을 지양하며, 설계 알고리즘 완성 및 0.10% 오차 검증을 최우선 완수.
    - **사후 리팩토링**: 포팅 중 발생한 수퍼파일은 조기 분할하지 않고, 부재 기능 완성 및 오차 검증 완료 후 추후 리팩토링 단계에서 체계적으로 분할 정리.
11. **단위 작업 = 1 커밋 & 원격 푸시 완수**:
    - 단위 작업(Phase/Step) 완료 즉시 1개의 Git 커밋을 생성하고 원격(`git push origin main`)까지 완료.
12. **외부 기억 파일 유지보수 및 세션/모델 핸드오버 규약 (External Memory Mandate)**:
    - AI 모델 교체나 새 세션 시작 시 **[`요구사항/PROJECT_PROGRESS.md`](../요구사항/PROJECT_PROGRESS.md)**를 즉시 열람하여 프로젝트 스냅샷, 직전 커밋, 다음 작업 번호를 100% 복원.
    - 단위 작업(Phase/Step) 완료 직전, 해당 진행 상태를 `요구사항/PROJECT_PROGRESS.md`에 즉시 반영하고 Git 커밋에 동봉.
    - `/goal` 명령문 실행 및 제안 시 **[`요구사항/PROJECT_PROGRESS.md`](../요구사항/PROJECT_PROGRESS.md)**의 정밀 프롬프트 및 권장 모델 티어를 1순위로 사용.

