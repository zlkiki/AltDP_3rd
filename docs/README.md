# AltDP_3rd 기술 문서 및 아키텍처 총람 (Documentation Index)

본 디렉토리는 **AltDP_3rd (원본앱 Web Migration & Engineering Platform)**의 설계 알고리즘, 바이너리 역공학 명세, 데이터베이스 규격, 아키텍처 및 테스팅 표준을 정리한 기술 문서(SSOT) 모음입니다.

---

## 📑 문서 인벤토리

| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| 01 | **전체 시스템 아키텍처** | 5대 논리 계층, 데이터 흐름도 및 전체 프로젝트 디렉토리/파일 인벤토리 | [상세보기](01_system_architecture.md) |
| 02 | **바이너리 리버스 엔지니어링 명세** | 원본앱 바이너리 구조, Ghidra 추출 파이프라인 및 C 자산 | [상세보기](02_binary_reverse_engineering_specification.md) |
| 03 | **단면 형강 DB 명세** | `.sdb` 바이너리 포맷 파싱 및 JSON/SQLite 변환 사양 | [상세보기](03_section_db_specification.md) |
| 04 | **원본앱 61종 전체 모듈 종합 카탈로그 및 4대 자산 인벤토리 (SSOT)** | 전수 61종 모듈 4대 SSOT 1:1 매핑 및 티어 분류 마스터 인벤토리 | [상세보기](04_master_original_app_modules_comprehensive_catalog.md) |
| 05 | **[예비/보관]** | 구 설계요약(04, 05) 문서는 `docs/@@OLD/`로 보관 이동 | [보관폴더](@@OLD) |
| 06 | **Python 독립 엔진 아키텍처 명세서** | 백엔드/클라이언트 코어 엔지니어링 계산 엔진 사양 (SRC, ALU, 보강 포함) | [상세보기](06_python_engine_architecture_specification.md) |
| 07 | **Web Application UI/UX 및 원본앱 역공학 종합 명세서** | AltDP 모던 웹 UI 아키텍처, 원본앱 UI 분석 및 1:1 매핑 구현 사양 | [상세보기](07_web_application_ui_ux_specification.md) |
| 08 | **Pytest 도메인별 3대 테스트 가이드** | 단위/통합 테스트 규약 및 초고속 실행 치트시트 | [상세보기](08_pytest_testing_guide.md) |
| 09 | **추출 바이너리 및 심볼 자산 분석 명세서** | 20개 DLL 모듈, 47,110개 심볼 및 47종 C 수도코드 인벤토리 | [상세보기](09_decompiled_source_and_symbol_inventory.md) |
| 10 | **에이전트 개발 프로토콜 및 세부 규약** | 모델 전략, Self-Healing, 세부 워크플로우 규약 | [상세보기](10_agent_development_protocols.md) |
| 11 | **KDS 국가건설기준 연동 가이드 (kcsc2md)** | kcsc2md Ground Truth 자산 및 Self-Healing 연동 표준 | [상세보기](../../kcsc2md/docs/외부프로젝트_연동_및_조회_가이드.md) |
| 12 | **전 기능 포팅 마스터플랜** | 20개 모듈/4.7만 심볼 100% 웹 마이그레이션 단계별 로드맵 | [상세보기](12_full_feature_porting_master_plan.md) |
| 13 | **[예비/통합]** | 구 13번 UI 분석 문서는 `docs/07`로 통합 후 `docs/@@OLD/`로 보관 이동 | [보관폴더](@@OLD) |
| 14 | **KDS 구조계산서 및 검토보고서 명세서** | 요약/상세/입력데이터 보고서 3대 모드, 보고서 옵션 및 KDS 수식 체계 | [상세보기](14_structural_calculation_report_specification.md) |
| 15 | **FEM 해석 및 외부 솔버 역공학 명세서** | FES/mfsolver/Iterative 3대 외부 솔버, CM2 자동메셔 연동 및 해석 데이터 파이프라인 | [상세보기](15_fem_analysis_and_external_solver_specification.md) |
| 16 | **[예비/보관]** | 구 16번 공정 규약은 `AGENTS.md` 및 `docs/10`으로 통합 후 `docs/@@OLD/`로 보관 이동 | [보관폴더](@@OLD) |
| 101 | **FEM 솔버 이론 및 정식화 명세서** | DKMQ/MITC4 평판 휨 요소, Winkler/Winkler-Pasternak 지반 정식화, 비선형 접촉 수렴 | [상세보기](fem/101_fem_engine_theoretical_manual_and_formulation.md) |
| 102 | **기존 솔버 비교 분석 및 벤치마크** | 원본앱 DgnSolver (FES/mfsolver/Iterative) vs AltDP FEM 수치해석 벤치마크 (0.1% 무결성) | [상세보기](fem/102_fem_solver_comparative_analysis_and_benchmark.md) |


