# 요구사항 27-1: Phase 27-1 단면 DB 자체 자산화 및 경로 추상화 레이어 (paths.py) 구축 명세서

## 1. 개요 및 목적

본 문서는 **AltDP_3rd 시스템이 런타임에 외부 연구용 폴더(`original_src`, `decompiled_src`)를 직접 참조하는 물리적 결함을 원천 제거**하고, 형강 단면 데이터베이스를 시스템 내부 표준 데이터 폴더(`src/data/dbase/`)로 완전 이관하여 **독립형 자체 자산(Standalone Asset)**으로 구축하는 상세 명세서입니다.

* **담당 소스 파일**:
  - `src/core/paths.py` (신규 생성)
  - `src/data/dbase/` (33개 .sdb 파일 이관)
  - `src/engine/db/section_db.py`
  - `src/api/routes/db.py`
  - `src/engine/steel/baseplate.py`
  - `src/engine/steel/connection.py`
  - `src/engine/steel/endplate.py`

---

## 2. 세부 구현 요구사항

### 2.1. 경로 추상화 레이어 구축 (`src/core/paths.py`)
- 프로젝트 최상위 루트 디렉토리를 기준으로 하는 `Path` 객체 기반의 싱글톤 경로 관리 모듈 신설:
  ```python
  """Application Path Abstraction Layer for AltDP_3rd.

  Centralizes all filesystem paths for standalone execution without external dependencies.
  """

  import os
  from pathlib import Path

  # Base Directories
  SRC_DIR = Path(__file__).resolve().parent.parent
  PROJECT_ROOT = SRC_DIR.parent

  # Internal Data Asset Directories
  DATA_DIR = SRC_DIR / "data"
  DBASE_DIR = DATA_DIR / "dbase"

  # Static & Template Directories
  WEB_DIR = SRC_DIR / "web"
  STATIC_DIR = WEB_DIR / "static"
  TEMPLATES_DIR = WEB_DIR / "templates"
  ```

### 2.2. 단면 DB 파일 33종 전수 이관 (`src/data/dbase/`)
- `original_src/Midas Design+/Dbase/*.sdb` (33개 국제 표준 단면 파일)를 `src/data/dbase/`로 완전 복사하여 독립 패키징 자산화:
  - `KS.sdb`, `KS21.sdb`, `AISC.sdb`, `AISC16(SI).sdb`, `JIS.sdb` 등 33종 (약 5.8MB)

### 2.3. 런타임 코드 하드코딩 제거 및 `paths.py` 연동
1. **`src/engine/db/section_db.py`**:
   - 기존:
     ```python
     DEFAULT_DB_DIR = os.path.abspath(
         os.path.join(os.path.dirname(__file__), "..", "..", "..", "original_src", "Midas Design+", "Dbase")
     )
     ```
   - 변경:
     ```python
     from src.core.paths import DBASE_DIR

     class SectionDBManager:
         DEFAULT_DB_DIR = str(DBASE_DIR)
     ```
2. **`src/api/routes/db.py`**:
   - 기존:
     ```python
     BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
     SDB_DIR = os.path.join(BASE_DIR, "original_src", "Midas Design+", "Dbase")
     ```
   - 변경:
     ```python
     from src.core.paths import DBASE_DIR
     SDB_DIR = str(DBASE_DIR)
     ```

### 2.4. Docstring 내 `decompiled_src` 참조 제거
- `src/engine/steel/baseplate.py`:
  - `decompiled_src/core_routines/steel/steel__CHK_USBP_*.c` $\rightarrow$ `KDS 14 31 10 : 2024 / KDS 14 31 25 주각부 설계 규준`
- `src/engine/steel/connection.py`:
  - `decompiled_src/core_routines/steel/steel__CHK_USBC_*.c` $\rightarrow$ `KDS 14 31 25 : 2024 볼트 및 용접 접합부 설계 규준`
- `src/engine/steel/endplate.py`:
  - `decompiled_src/core_routines/steel/steel__CHK_USEP_*.c` $\rightarrow$ `KDS 14 31 25 : 2024 엔드플레이트 모멘트접합부 규준`

---

## 3. 검증 및 완료 기준 (Definition of Done)

1. `src/core/paths.py` 파일 생성 및 `DBASE_DIR.exists()` 검증 완료.
2. `src/data/dbase/` 내 33개 `.sdb` 파일 존재 확인.
3. `src/engine/db/section_db.py` 및 `src/api/routes/db.py`에서 `original_src` 문자열 완전 소거.
4. `src/engine/steel/` 내 3개 파일에서 `decompiled_src` 문자열 완전 소거.
5. `pytest tests/engine/test_sdb_parser.py` 단독 테스트 통과.
