# Pytest 도메인별 3대 테스트 가이드 및 실행 기준 (08_pytest_testing_guide.md)

본 문서는 AltDP_3rd 프로젝트의 **테스트 구조, 도메인별 실행 명령어**, 그리고 작업 성격에 따른 **테스트 필수 vs 테스트 불필요(생략) 작업 분류 기준**을 규정하는 표준 가이드입니다.

---

## 1. 테스트 실행 여부 판단 기준 (테스트 필수 vs 생략 작업)

리소스 낭비와 불필요한 지연을 방지하기 위해, 작업 성격에 따라 테스트 실행 여부를 엄격히 구분합니다.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 작업 성격별 테스트 실행 매트릭스 (Testing Execution Matrix)                           │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ 🔴 [테스트 필수 (Must Run Test)]           │ 🟢 [테스트 생략 (Skip Test)]              │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ • 설계 엔진 알고리즘 신규 구현 및 수식 변경│ • docs/ 기술 문서 (.md) 신규 작성 및 수정 │
│ • Python 백엔드/API 엔드포인트 수정        │ • 요구사항/ 기획 문서 작성 및 아카이빙   │
│ • P-M 상관도/수치해석 솔버 수정            │ • README.md, AGENTS.md 등 가이드 수정     │
│ • 버그 수정 (Bug Fix) 및 회귀 검증        │ • 주석(Comments), 독스트링(Docstring) 정비│
│ • 데이터 모델 (Pydantic / DB 스키마) 변경  │ • 순수 UI 디자인/CSS 스타일/텍스트 레이블 │
│ • requirements.txt 패키지 의존성 변경     │ • 단순 코드 포맷팅 (Black/Flake8 등)      │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

### 1.1. 🔴 테스트가 반드시 필요한 작업 (Mandatory Testing)
1. **구조설계 계산 엔진 수정**: `src/engine/` 내의 RC, Steel, SRC, Alu, RFM 수식 및 알고리즘 변경 시 (KDS 14 20 00 / 14 31 00 정밀도 검증).
2. **API 라우트 및 스키마 변경**: `src/api/` 내의 FastAPI 엔드포인트, 요청/응답 Pydantic 모델, 상태코드 변경 시.
3. **P-M 솔버 및 단면 DB 수정**: `src/engine/solver/`, `src/engine/db/`의 수치해석 로직이나 SQLite/SDB 파서 변경 시.
4. **버그 수정 (Bug Fix)**: 1이슈 1테스트 원칙에 따라 결함 수정 후 회귀 테스트 필수.
5. **의존성 변경**: `requirements.txt`에 신규 패키지 추가 또는 버전 업그레이드 시.

### 1.2. 🟢 테스트를 실행하지 않는 작업 (Skip Testing)
1. **문서화 작업 (Documentation)**: `docs/*.md`, `요구사항/*.md`, `README.md`, `AGENTS.md` 등 순수 마크다운 문서 작성 및 편집.
2. **설계 기획 및 아키텍처 분석**: 원본 UI 분석, 코드 구조 조사, 마스터플랜 수립.
3. **비기능적 주석 및 타이핑 정리**: 계산 로직에 영향을 주지 않는 순수 설명 주석, 타입 힌트 보강.
4. **정적 웹 마크업 및 스타일링**: 순수 HTML/CSS 시각 요소 및 텍스트 레이블 변경 (엔진 연동 제외).

---

## 2. 테스트 스위트 디렉토리 구조

AltDP_3rd는 신속하고 무결한 개발을 위해 테스트 스위트를 **3대 도메인(엔진, API, 리포트/UI)**으로 분리하여 관리합니다.

```text
tests/
├── conftest.py                     # 공통 픽스처 및 샘플 부재 데이터
├── engine/                         # Layer 1~3 공학 계산 엔진 단위 테스트
│   ├── test_materials.py           # 재료 물성치 및 KDS 계수 검증
│   ├── test_rc_beam.py             # RC 보 휨/전단 강도 계산 검증
│   ├── test_rc_column.py           # RC 기둥 및 P-M 상관도 검증
│   ├── test_rc_footing.py          # 독립기초 펀칭전단 검증
│   ├── test_rc_slab.py             # 슬래브 1방향/2방향 검증
│   ├── test_rc_wall.py             # 전단벽 및 특수경계요소 검증
│   ├── test_steel_beam.py          # 철골보 LTB 및 휨강도 검증
│   ├── test_steel_connection.py    # 볼트/용접 접합부 검증
│   ├── test_sdb_parser.py          # .sdb 형강 DB 파싱 검증
│   └── test_fiber_section.py       # 파이버 단면 수치해석 검증
├── api/                            # Layer 4 FastAPI 엔드포인트 테스트
│   ├── test_rc_routes.py           # RC 부재설계 API 요청/응답 검증
│   ├── test_rc_beam_api.py         # RC 보 전용 엔드포인트 검증
│   ├── test_rc_column_api.py       # RC 기둥 전용 엔드포인트 검증
│   ├── test_steel_member_api.py    # 철골 부재 API 검증
│   └── test_report_routes.py       # 계산서 생성 및 다운로드 API 검증
└── report/                         # Layer 5 계산서 및 출력 검증
    ├── test_report_generator.py    # A4 구조계산서 Jinja2/KaTeX 렌더링
    ├── test_member_reports.py      # 부재별 계산서 및 SVG 벡터 그래픽
    └── test_excel_exporter.py      # OpenPyXL 엑셀 시트 생성 검증
```

---

## 3. 초고속 도메인별 테스트 실행 치트시트

코드 변경 시 변경된 도메인의 타겟 테스트를 우선 실행하여 1초 이내에 피드백을 확보합니다.

```bash
# 1. 엔지니어링 계산 엔진만 고속 검증 (0.5~1.0초)
pytest tests/engine/

# 2. 특정 부재 엔진만 단독 검증 (0.1~0.3초)
pytest tests/engine/test_rc_beam.py
pytest tests/engine/test_steel_connection.py

# 3. REST API 엔드포인트만 검증 (0.8초)
pytest tests/api/

# 4. A4 계산서 및 엑셀 출력 엔진 검증 (0.5초)
pytest tests/report/

# 5. 마스터 머지 전 전체 전수 테스트 스위트 검증
pytest
```
