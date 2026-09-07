# [보류 요구사항] src, tests, scripts 소스 코드 내 '원본앱' 명칭 정리 및 물리 경로 추상화

## 1. 개요
본 문서는 현재 문서군(`docs/`, `요구사항/`, `AGENTS.md`, `README.md`)에 적용된 **「원본앱」** 명칭 표준화를 향후 소스 코드(`src/`), 테스트 코드(`tests/`), 개발 스크립트(`scripts/`) 영역까지 확장하여 일관성을 완성하기 위한 기술 과제 명세서입니다.

---

## 2. 작업 배경 및 주요 과제

현재 문서 레벨에서는 명칭이 "원본앱"으로 통일되었으나, 소스 코드 레벨에서는 다음과 같은 기술적 의존성으로 인해 분리 보존되어 있습니다:

1. **물리적 디스크 경로 직참조**:
   - `src/api/routes/db.py`: `os.path.join(BASE_DIR, "original_src", "원본앱", "Dbase")`
   - `src/engine/db/section_db.py`: `os.path.join(..., "original_src", "원본앱", "Dbase")`
   - `tests/engine/test_sdb_parser.py`: `os.path.join(..., "original_src", "원본앱", "Dbase")`
   - `scripts/ghidra_extract.py`, `scripts/scan_*.py`, `scripts/extract_symbols.py`
2. **독립 소프트웨어(`MIDAS Gen`) 연동과의 혼선 방지**:
   - `src/engine/interop/` 패키지의 `MidasModel3D`, `MgtParser` 등은 3D 골조해석 프로그램(`MIDAS Gen`)과의 연동 인터페이스이므로, 본 과제 수행 시 오인 변경되지 않도록 엄격히 격리해야 함.
3. **소스 코드 내 주석 및 Docstring**:
   - `src/engine/solver/fiber_section.py` (원본앱 solver logic)
   - `src/report/excel_exporter.py` (원본앱 CMSExcel format)
   - `src/web/static/css/views.css`, `ribbon.css` (원본앱 CMainFormView...)
   - `src/web/static/js/core/*.js`
   - `tests/engine/test_fem_integration.py`

---

## 3. 세부 구현 로드맵 (향후 실행 방안)

### Step 1: 경로 추상화 레이어 구축 (Path Abstraction Layer)
- 하드코딩된 `"원본앱"` 디렉토리 문자열을 제거하고, 공통 설정 모듈(`src/core/config.py` 또는 `src/engine/db/paths.py`)에서 단일 상수 또는 환경변수로 관리:
  ```python
  # src/core/config.py (예시)
  ORIGINAL_APP_DIR_NAME = os.getenv("ORIGINAL_APP_DIR_NAME", "원본앱")
  ORIGINAL_APP_PATH = BASE_DIR / "original_src" / ORIGINAL_APP_DIR_NAME
  ```
- 이후 코드베이스 전체에서 `ORIGINAL_APP_PATH`를 참조하도록 리팩토링하여 디스크 폴더명 의존성을 완전히 격리.

### Step 2: 주석 및 Docstring 내 명칭 치환
- `src/` 및 `tests/` 내 주석과 docstring에서 `원본앱` -> `원본앱`으로 일괄 치환.

### Step 3: MIDAS Gen 연동 모듈 명칭 검토
- `src/engine/interop/`의 `MidasModel3D` 등 명칭을 유지할 것인지, 아니면 `GenModel3D` 또는 `MgtModel3D`로 명확히 명명하여 혼동을 원천 차단할 것인지 확정 후 반영.

### Step 4: 무결성 회귀 테스트
- `pytest` 전체 테스트 패스 확인 (단면 DB 로딩, 파이버 단면 수치해석, FEM 솔버 연동 등).
