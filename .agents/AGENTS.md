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
