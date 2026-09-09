# AltDP_3rd 기술 문서 및 아키텍처 총람 (Documentation Index)

본 디렉토리는 **AltDP_3rd (KDS 국가건설기준 웹 부재설계 시스템 / 원본앱 Web Migration & Engineering Platform)**의 설계 알고리즘, 바이너리 역공학 명세, 데이터베이스 규격, 아키텍처 및 테스팅 표준을 정리한 기술 문서(SSOT) 모음입니다.

---

## 📑 6대 문서 번호 체계 및 인벤토리

### 1. [00] 마스터 인덱스 (Master Index)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **00** | **마스터 기술 문서 총람 및 인덱스** | 6대 문서 번호 체계 요약, 상호 참조 맵 및 온디맨드 라우팅 총괄 | [상세보기](00_master_documentation_index.md) |

### 2. [01 ~ 10] 앱 개발 관련 기술 문서 (Engineering Tech Specs)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **01** | **전체 시스템 아키텍처** | 5대 논리 계층, 데이터 흐름도 및 전체 프로젝트 디렉토리/파일 인벤토리 | [상세보기](01_system_architecture.md) |
| **02** | **전 기능 수직 포팅 마스터플랜** | 61종 전수 모듈 부재별 수직 관통(Step 1~4) 개발 패러다임 및 6대 스프린트 로드맵 | [상세보기](02_full_feature_porting_master_plan.md) |
| **03** | **엔진 아키텍처 명세서** | 코어 엔지니어링 계산 엔진 사양 (RC, Steel, SRC, ALU, FEM) 및 아키텍처 상호 참조 맵 | [상세보기](03_engine_architecture_specification.md) |
| **04** | **Pytest 도메인별 3대 테스트 가이드** | 단위/통합 테스트 규약, 0.10% 오차 무결성 및 초고속 실행 치트시트 | [상세보기](04_pytest_testing_guide.md) |
| **05** | **에이전트 개발 프로토콜 및 세부 규약** | 4대 참조 우선순위, kcsc2md 연동, 3자 삼각대조 0.10% 오차 무결성, 1부재 1마스터 규약 | [상세보기](05_agent_development_protocols.md) |

### 3. [11 ~ 50] 우리앱 공통 명세 (AltDP_3rd Common Specifications)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **11** | **단면 형강 및 재료 규격 DB 명세서** | 33종 `*.sdb` 바이너리 내부 자산화(`src/data/dbase/`), SQLite 캐시, REST API 및 KDS 재료 DB | [상세보기](11_section_db_specification.md) |
| **12** | **Web Application UI/UX 종합 명세서** | 4-Pane 워크스페이스, 독립 리사이저, 디자인 토큰, 3버튼 파이프라인 (전 부재 공통 Web UI/UX 표준) | [상세보기](12_web_application_ui_ux_specification.md) |
| **13** | **KDS 구조계산서 및 검토보고서 종합 명세서** | 요약/상세/입력데이터 보고서 3대 모드, 보고서 옵션 및 A4 순백색 KaTeX 7대장 수식 체계 | [상세보기](13_structural_calculation_report_specification.md) |
| **14** | **FEM 해석 및 2D 솔버 공통 명세서** | 2D FEM 평판·지반 솔버 규격, CM2 자동메셔 연동 및 해석 데이터 파이프라인 | [상세보기](14_fem_analysis_and_external_solver_specification.md) |

### 4. [51 ~ 100] 원본앱 분석 문서 (Original App Reverse Engineering / Ground Truth)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **51** | **바이너리 리버스 엔지니어링 명세서** | 원본앱 64비트 바이너리 구조, Ghidra 추출 파이프라인 및 C 자산 분석 | [상세보기](51_binary_reverse_engineering_specification.md) |
| **52** | **추출 바이너리 및 심볼 자산 분석 명세서** | 20개 DLL 모듈, 47,110개 심볼 및 47종 C 수도코드 인벤토리 | [상세보기](52_decompiled_source_and_symbol_inventory.md) |
| **53** | **원본앱 61종 전체 모듈 종합 카탈로그 (SSOT)** | 전수 61종 모듈 4대 SSOT 1:1 매핑 및 티어 분류 마스터 인벤토리 | [상세보기](53_master_original_app_modules_comprehensive_catalog.md) |
| **54** | **원본앱 UI/UX 역공학 종합 분석 명세서** | MFC/BCGControlBar 윈도우 프레임워크, Menu.ini 11개 탭, 4대 폼뷰, 3대 모드, DLG_*.ini, VDraw 엔진 | [상세보기](54_original_app_ui_specification.md) |

### 5. [101 ~ 200] 고급 수치해석 및 FEM 특수 솔버 명세 (Advanced Solvers)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **101**| **FEM 솔버 이론 및 정식화 명세서** | DKMQ/MITC4 평판 휨 요소, Winkler/Winkler-Pasternak 지반 정식화, 비선형 접촉 수렴 | [상세보기](101_fem_engine_theoretical_manual_and_formulation.md) |
| **102**| **기존 솔버 비교 분석 및 벤치마크** | 원본앱 DgnSolver (FES/mfsolver/Iterative) vs AltDP FEM 수치해석 벤치마크 (0.1% 무결성) | [상세보기](102_fem_solver_comparative_analysis_and_benchmark.md) |

### 6. [201 ~ 300] 단위 부재별 전용 모듈 설계 명세서 (Member Specifications)
| 번호 | 문서명 | 내용 요약 | 링크 |
|:---:|---|---|:---:|
| **201**| **RC 보 (RC Beam) 설계 모듈 종합 명세서** | C BEAM 역공학, 4대 서브탭, 배근유형 라디오, 12포인트 순간격, 1,811줄 KDS 엔진 및 7대장 계산서 전문 | [상세보기](201_rc_beam_module_specification.md) |
