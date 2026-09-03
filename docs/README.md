# AltDP_3rd 기술 문서 및 아키텍처 총람 (Documentation Index)

본 디렉토리는 **AltDP_3rd (Midas Design+ Web Migration & Engineering Platform)**의 설계 알고리즘, 바이너리 역공학 명세, 데이터베이스 규격, 아키텍처 및 테스팅 표준을 정리한 기술 문서(SSOT) 모음입니다.

---

## 📑 문서 인벤토리

| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| 01 | **전체 시스템 아키텍처** | 5대 논리 계층, 데이터 흐름도 및 전체 프로젝트 디렉토리/파일 인벤토리 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md) |
| 02 | **바이너리 리버스 엔지니어링 명세** | Midas Design+ 바이너리 구조, Ghidra 추출 파이프라인 및 C 자산 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/02_binary_reverse_engineering_specification.md) |
| 03 | **단면 형강 DB 명세** | `.sdb` 바이너리 포맷 파싱 및 JSON/SQLite 변환 사양 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/03_section_db_specification.md) |
| 04 | **RC 부재설계 기준서 (KDS 14 20 00)** | 보, 기둥, 슬래브, 전단벽, 기초, 옹벽 수식집 및 C 소스 매핑 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/04_rc_design_specification.md) |
| 05 | **철골 부재설계 기준서 (KDS 14 31 00)** | 철골보, 기둥, 가새, 접합부, 베이스플레이트 수식집 및 C 소스 매핑 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/05_steel_design_specification.md) |
| 06 | **Python 독립 엔진 아키텍처 명세서** | 백엔드/클라이언트 코어 엔지니어링 계산 엔진 사양 (SRC, ALU, 보강 포함) | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/06_python_engine_architecture_specification.md) |
| 07 | **Web Application UI/UX 명세서** | AltDP 모던 웹 UI, 2D/3D 부재 렌더러 및 P-M 상관도 차트 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md) |
| 08 | **Pytest 도메인별 3대 테스트 가이드** | 단위/통합 테스트 규약 및 초고속 실행 치트시트 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/08_pytest_testing_guide.md) |
| 09 | **추출 바이너리 및 심볼 자산 분석 명세서** | 20개 DLL 모듈, 47,110개 심볼 및 47종 C 수도코드 인벤토리 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/09_decompiled_source_and_symbol_inventory.md) |
| 10 | **에이전트 개발 프로토콜 및 세부 규약** | 모델 전략, Self-Healing, 세부 워크플로우 규약 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md) |
| 11 | **KDS 국가건설기준 연동 가이드 (kcsc2md)** | kcsc2md Ground Truth 자산 및 Self-Healing 연동 표준 | [상세보기](file:///f:/PyProject/kcsc2md/docs/외부프로젝트_연동_및_조회_가이드.md) |
| 12 | **전 기능 포팅 마스터플랜** | 20개 모듈/4.7만 심볼 100% 웹 마이그레이션 단계별 로드맵 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md) |
| 13 | **Midas Design+ 원본 UI/UX 역공학 명세서** | MFC 리본 메뉴, 4대 폼뷰, 3대 인터랙션 모드, 드로잉 및 계산서 분석 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/13_midas_design_plus_original_ui_specification.md) |
| 14 | **KDS 구조계산서 및 검토보고서 명세서** | 요약/상세/입력데이터 보고서 3대 모드, 보고서 옵션 및 KDS 수식 체계 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/14_structural_calculation_report_specification.md) |
| 15 | **FEM 해석 및 외부 솔버 역공학 명세서** | 5대 FEM 설계 모듈, FES/mfsolver/Iterative 외부 솔버, CM2 오토메셔 및 Python 마이그레이션 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/15_fem_analysis_and_external_solver_specification.md) |
| 16 | **FEM 솔버 이론 및 정식화 명세서** | DKMQ/MITC4 평판 휨 요소, Winkler/Winkler-Pasternak 지반 정식화, 비선형 접촉 수렴 | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/16_fem_engine_theoretical_manual_and_formulation.md) |
| 17 | **기존 솔버 비교 분석 및 벤치마크** | Midas 원본 DgnSolver (FES/mfsolver/Iterative) vs AltDP FEM 수치해석 벤치마크 (0.1% 무결성) | [상세보기](file:///f:/PyProject/AltDP_3rd/docs/17_fem_solver_comparative_analysis_and_benchmark.md) |


