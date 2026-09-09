# 00. AltDP_3rd 마스터 기술 문서 총람 및 인덱스 (00_master_documentation_index.md)

---

## 1. 개요 및 6대 기술 문서 번호 체계 (Documentation Tiering Rules)

본 문서는 **AltDP_3rd (KDS 국가건설기준 웹 부재설계 시스템 / 원본앱 Web Migration & Engineering Platform)**의 모든 설계 알고리즘, 바이너리 역공학 명세, 데이터베이스 규격, 아키텍처, UI/UX, 테스팅 표준 및 엔지니어링 개발 프로토콜을 총망라한 **최상위 기술 문서 총람(Master Documentation Index & SSOT Router)**입니다.

에이전트 및 개발자는 대형 문서를 사전에 통째로 읽어 토큰을 낭비하지 않고, 본 인덱스를 통해 **현재 작업에 반드시 필요한 문서의 위치와 역할을 즉시 특정(JIT On-Demand Retrieval)**하여 열람합니다.

### 📌 기술 문서 번호 부여 규칙 (Numbering Convention)
프로젝트 내 모든 기술 문서는 명확한 책임 분리와 온디맨드 조회를 위해 다음 **6대 번호 대역 규칙**에 따라 엄격히 관리됩니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AltDP_3rd 6대 문서 번호 체계 및 역할 분담 규칙 (Master Documentation Tiering)                          │
├──────────────┬────────────────────────┬────────────────────────────────────────────────────────────────┤
│ 대역 (Tier)  │ 카테고리 정의           │ 수록 문서 및 핵심 역할                                         │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **00**       │ **마스터 인덱스**       │ • 00_master_documentation_index.md (전체 문서 라우터 & SSOT)   │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **01 ~ 10**  │ **앱 개발 기술 문서**   │ • 01: 전체 시스템 아키텍처 및 소프트웨어 스택                 │
│              │ (시스템 엔지니어링)    │ • 02: 전 기능 수직 포팅 마스터플랜 (로드맵 & 스프린트)          │
│              │                        │ • 03: Python 코어 엔진 아키텍처 및 모듈 레이어 규격            │
│              │                        │ • 04: Pytest TDD 0.10% 오차 무결성 테스팅 가이드               │
│              │                        │ • 05: 에이전트 개발 프로토콜 및 엔지니어링 행동 강령           │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **11 ~ 50**  │ **우리앱 공통 명세**   │ UI관련, 계산서관련, FEM관련, 형강/재료 DB 등 전 부재 공통 사양:│
│              │ (AltDP_3rd 공통 표준)  │ • 11: 단면 형강 및 구조 재료 규격 DB 명세서                    │
│              │                        │ • 12: Web Application UI/UX 종합 명세서 (4-Pane 워크스페이스)  │
│              │                        │ • 13: KDS 순백색 A4 KaTeX 구조계산서 및 리포트 엔진 명세       │
│              │                        │ • 14: FEM 해석 및 2D 솔버 공통 명세서 (CM2 메셔 연동)         │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **51 ~ 100** │ **원본앱 역공학 분석** │ 원본 데스크톱앱(Design+.exe) C++ 바이너리 및 리소스 Ground Truth│
│              │ (Ground Truth 레퍼런스)│ • 51: 원본 바이너리 리버스 엔지니어링 및 의존성 명세           │
│              │                        │ • 52: 디컴파일 소스 및 4.7만 심볼 인벤토리                    │
│              │                        │ • 53: 61종 원본 부재 매핑 종합 카탈로그 (SSOT)                │
│              │                        │ • 54: 원본 데스크톱 UI/UX 역공학 종합 분석 명세서              │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **101 ~ 200**│ **고급 수치/FEM 솔버** │ 고난도 비선형 수치해석, 평판/지반 솔버 정식화 이론 및 벤치마크:│
│              │ (Advanced Solvers)     │ • 101: FEM 솔버 이론 및 정식화 명세서 (DKMQ/MITC4 후판 요소)   │
│              │                        │ • 102: 기존 솔버 비교 분석 및 수치 벤치마크 (0.10% 무결성)    │
├──────────────┼────────────────────────┼────────────────────────────────────────────────────────────────┤
│ **201 ~ 300**│ **단위 부재별 모듈 명세│ 61종 개별 부재별 특화된 UI, 배근 규칙, KDS 수식 및 계산서 전문:│
│              │ (Member Specifications)│ • 201: RC 보 (RC Beam) 설계 모듈 종합 명세서 (`rc_beam`)       │
│              │                        │ • (향후 202: RC 기둥, 203: RC 전단벽, 204: 슬래브, 205: 기초 등)│
└──────────────┴────────────────────────┴────────────────────────────────────────────────────────────────┘
```

---

## 2. 전체 기술 문서 전수 인벤토리 (Master Document Inventory)

### 2.1. [00] 마스터 인덱스 (Master Index)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **00** | `00_master_documentation_index.md` | **마스터 기술 문서 총람 및 인덱스**<br>6대 문서 번호 체계 규칙, 상호 참조 맵 및 온디맨드 라우팅 총괄 | 시스템 총괄 / 라우터 | [상세보기](00_master_documentation_index.md) |

### 2.2. [01 ~ 10] 앱 개발 관련 기술 문서 (Application Engineering Tech Specs)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **01** | `01_system_architecture.md` | **전체 시스템 아키텍처**<br>5대 논리 계층(DB, 역학솔버, 구조기준, REST API, 웹UI), 데이터 흐름도 및 프로젝트 구조 | 전체 시스템 설계 | [상세보기](01_system_architecture.md) |
| **02** | `02_full_feature_porting_master_plan.md` | **전 기능 수직 포팅 마스터플랜**<br>61종 전수 모듈 부재별 수직 관통(Step 1~4) 개발 패러다임 및 6대 스프린트 로드맵 | 포팅 로드맵 / 스프린트 | [상세보기](02_full_feature_porting_master_plan.md) |
| **03** | `03_engine_architecture_specification.md` | **엔진 아키텍처 명세서**<br>순수 Python 코어 엔지니어링 계산 엔진 사양 (RC, Steel, SRC, ALU, FEM 등) 및 아키텍처 상호 참조 맵 | 계산 엔진 / 데이터 모델 | [상세보기](03_engine_architecture_specification.md) |
| **04** | `04_pytest_testing_guide.md` | **Pytest 도메인별 3대 테스트 가이드**<br>단위/통합 테스트 규약, 테스트 필수 vs 생략 작업 분류표, 초고속 검증 치트시트 | 테스트 / 품질 보증 | [상세보기](04_pytest_testing_guide.md) |
| **05** | `05_agent_development_protocols.md` | **에이전트 상세 개발 규약 및 엔지니어링 프로토콜**<br>4대 참조 우선순위 계층, kcsc2md 연동, 3자 삼각대조 0.10% 오차 무결성, 1부재 1마스터 규약 | 개발 행동 규약 / 표준 | [상세보기](05_agent_development_protocols.md) |

### 2.3. [11 ~ 50] 우리앱 공통 명세 (AltDP_3rd Common Specifications)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **11** | `11_section_db_specification.md` | **단면 형강 및 구조 재료 규격 DB 명세서**<br>33종 `*.sdb` 바이너리 내부 자산화(`src/data/dbase/`), In-Memory SQLite 캐시, REST API 및 KDS 재료 DB | 형강/재료 DB / 제원 | [상세보기](11_section_db_specification.md) |
| **12** | `12_web_application_ui_ux_specification.md` | **Web Application UI/UX 종합 명세서**<br>4-Pane 워크스페이스, 4대 독립 리사이저, 디자인 토큰, 3버튼 파이프라인 (전 부재 공통 Web UI/UX 표준) | 프론트엔드 / UI/UX | [상세보기](12_web_application_ui_ux_specification.md) |
| **13** | `13_structural_calculation_report_specification.md` | **KDS 구조계산서 및 검토보고서 종합 명세서**<br>요약/상세/입력데이터 3대 보고서 체계, DLG 옵션 역공학, A4 순백색 KaTeX 7대장 수식 체계 | 구조계산서 / KaTeX | [상세보기](13_structural_calculation_report_specification.md) |
| **14** | `14_fem_analysis_and_external_solver_specification.md` | **FEM 해석 및 2D 솔버 공통 명세서**<br>2D FEM 평판/지반 솔버 규격, CM2 자동메셔 연동, 5대 FEM 설계 모듈 사양 | FEM / 지반-구조물 솔버 | [상세보기](14_fem_analysis_and_external_solver_specification.md) |

### 2.4. [51 ~ 100] 원본앱 분석 문서 (Original App Reverse Engineering / Ground Truth)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **51** | `51_binary_reverse_engineering_specification.md` | **바이너리 리버스 엔지니어링 명세서**<br>원본앱 64비트 MSVC 바이너리 구조, 4.7만 심볼 분석, Ghidra Headless 추출 파이프라인 | 역공학 / 원본 소스 대조 | [상세보기](51_binary_reverse_engineering_specification.md) |
| **52** | `52_decompiled_source_and_symbol_inventory.md` | **추출 바이너리 및 심볼 자산 분석 명세서**<br>20개 DLL 모듈, 47,110개 심볼, 47종 C 핵심 수도코드 인벤토리 및 Ground Truth 프로토콜 | 디컴파일 소스 / 심볼 | [상세보기](52_decompiled_source_and_symbol_inventory.md) |
| **53** | `53_master_original_app_modules_comprehensive_catalog.md` | **원본앱 61종 전체 모듈 종합 카탈로그 (SSOT)**<br>전수 61종 모듈 4대 SSOT(소스, 매뉴얼, 예제집, KDS) 1:1 매핑 및 3단계 티어 인벤토리 | 61종 부재 총괄 / 로드맵 | [상세보기](53_master_original_app_modules_comprehensive_catalog.md) |
| **54** | `54_original_app_ui_specification.md` | **원본앱 UI/UX 역공학 종합 분석 명세서**<br>MFC/BCGControlBar 윈도우 프레임워크, Menu.ini 11개 탭, 4대 폼뷰, 3대 모드, DLG_*.ini, VDraw 엔진 | 데스크톱 역공학 / Ground Truth | [상세보기](54_original_app_ui_specification.md) |

### 2.5. [101 ~ 200] 고급 수치해석 및 FEM 특수 솔버 명세 (Advanced Solvers & FEM Formulations)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **101**| `101_fem_engine_theoretical_manual_and_formulation.md` | **FEM 솔버 이론 및 정식화 명세서**<br>DKMQ/MITC4 후판 휨 요소 강성행렬, Winkler-Pasternak 지반 정식화, 접촉 비선형 수렴 이론 | 평판/지반 수치이론 | [상세보기](101_fem_engine_theoretical_manual_and_formulation.md) |
| **102**| `102_fem_solver_comparative_analysis_and_benchmark.md` | **기존 솔버 비교 분석 및 수치 벤치마크**<br>원본앱 DgnSolver(FES/mfsolver) vs AltDP Python FEM 솔버 수치 대조 검증 (오차 ≤ 0.10%) | FEM 검증 / 벤치마크 | [상세보기](102_fem_solver_comparative_analysis_and_benchmark.md) |

### 2.6. [201 ~ 300] 단위 부재별 전용 모듈 설계 명세서 (Member-Specific Design Specifications)
| 문서 번호 | 파일명 | 문서 제목 및 핵심 내용 | 주요 참조 도메인 | 링크 |
|:---:|---|---|---|:---:|
| **201**| `201_rc_beam_module_specification.md` | **RC 보 (RC Beam) 설계 모듈 종합 명세서**<br>C BEAM 역공학, 4대 서브탭, 배근유형 라디오, 12포인트 순간격, 1,811줄 KDS 엔진 및 7대장 계산서 전문 | RC 보 전용 모듈 명세 | [상세보기](201_rc_beam_module_specification.md) |

---

## 3. 상호 참조 매핑 다이어그램 (Inter-Document Cross-Reference Map)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AltDP_3rd 문서 상호 참조 및 데이터 흐름 맵                                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│                        [00. 마스터 인덱스 (총괄 라우터)]                                         │
│                                       │                                                         │
│         ┌─────────────────────────────┼─────────────────────────────┐                           │
│         ▼                             ▼                             ▼                           │
│  [01~10. 개발 기술 문서]      [11~50. 우리앱 공통 명세]     [51~100. 원본앱 역공학 분석]        │
│   • 01 시스템 아키텍처         • 11 형강/재료 DB 명세        • 51 바이너리 리버스엔지니어링     │
│   • 02 수직 포팅 마스터플랜    • 12 UI/UX 종합 명세          • 52 추출 심볼/C 수도코드 인벤토리│
│   • 03 엔진 아키텍처 명세      • 13 구조계산서 명세          • 53 61종 전체 모듈 카탈로그      │
│   • 04 Pytest 테스팅 가이드    • 14 FEM 솔버 공통 명세       • 54 원본 데스크톱 UI/UX 분석     │
│   • 05 에이전트 개발 프로토콜                                                                  │
│         │                             │                             │                           │
│         └─────────────────────────────┼─────────────────────────────┘                           │
│                                       │                                                         │
│                     ┌─────────────────┴─────────────────┐                                       │
│                     ▼                                   ▼                                       │
│         [101~200. 고급 수치/FEM]            [201~300. 단위 부재별 명세]                         │
│          • 101 FEM 이론 및 정식화            • 201 RC 보 설계 모듈 종합 명세                   │
│          • 102 FEM 솔버 벤치마크             • 202 RC 기둥 설계 모듈 종합 명세 (원본 100% 인벤토리) │
│                                              • (차후 203 전단벽, 204 슬래브 등 순차 확장)       │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 에이전트 온디맨드 열람 및 개발 가이드 (Agent Workflow)

1. **상시 열람 금지**: 문서 전체를 미리 컨텍스트에 올리지 마십시오.
2. **도메인별 분기 진입**:
   * 엔진 아키텍처 및 계층 구조 확인 시: [03_engine_architecture_specification.md](file:///f:/PyProject/AltDP_3rd/docs/03_engine_architecture_specification.md)
   * 부재 개발 규약 및 0.10% 오차 검증 기준 확인 시: [05_agent_development_protocols.md](file:///f:/PyProject/AltDP_3rd/docs/05_agent_development_protocols.md)
   * 부재 매핑, C 함수명, 원본 다이얼로그 확인 시: [53_master_original_app_modules_comprehensive_catalog.md](file:///f:/PyProject/AltDP_3rd/docs/53_master_original_app_modules_comprehensive_catalog.md)
   * 원본 데스크톱 UI/UX 구조 확인 시: [54_original_app_ui_specification.md](file:///f:/PyProject/AltDP_3rd/docs/54_original_app_ui_specification.md)
   * 웹 프론트엔드 공통 UI 컴포넌트 및 리사이저 규칙 확인 시: [12_web_application_ui_ux_specification.md](file:///f:/PyProject/AltDP_3rd/docs/12_web_application_ui_ux_specification.md)
   * 단면 DB 구조 및 형강 데이터 확인 시: [11_section_db_specification.md](file:///f:/PyProject/AltDP_3rd/docs/11_section_db_specification.md)
   * 계산서 출력 양식 및 KaTeX 수식 구성 확인 시: [13_structural_calculation_report_specification.md](file:///f:/PyProject/AltDP_3rd/docs/13_structural_calculation_report_specification.md)
   * 평판/지반 FEM 솔버 및 CM2 메셔 연동 확인 시: [14_fem_analysis_and_external_solver_specification.md](file:///f:/PyProject/AltDP_3rd/docs/14_fem_analysis_and_external_solver_specification.md)
   * 고급 FEM 정식화 이론 및 수치 벤치마크 확인 시: [101_fem_engine_theoretical_manual_and_formulation.md](file:///f:/PyProject/AltDP_3rd/docs/101_fem_engine_theoretical_manual_and_formulation.md)
   * RC 보 개별 모듈 개발 및 상세 제원 확인 시: [201_rc_beam_module_specification.md](file:///f:/PyProject/AltDP_3rd/docs/201_rc_beam_module_specification.md)
   * RC 기둥 개별 모듈 및 원본 전수 기능 인벤토리 확인 시: [202_rc_column_module_specification.md](file:///f:/PyProject/AltDP_3rd/docs/202_rc_column_module_specification.md)
