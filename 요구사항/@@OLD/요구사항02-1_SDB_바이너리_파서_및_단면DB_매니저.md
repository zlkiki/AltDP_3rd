# 요구사항 02-1: SDB 바이너리 파서 및 단면 DB 매니저

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+의 단면 데이터베이스 파일(`original_src/Midas Design+/Dbase/*.sdb`, 총 33종)은 강구조 및 합성부재 설계의 기본 자산입니다.
* `KS.sdb`, `KS21.sdb`, `AISC.sdb`, `JIS.sdb`, `DIN.sdb` 등 전 규격 바이너리 포맷을 완벽히 디코딩하고, SQLite 메모리 DB 및 빠른 검색 캐시를 갖춘 Python 독립 단면 매니저(`SectionDBManager`)를 구축합니다.

### 1.2. 참조 Ground Truth 자산
* **바이너리 파일**: `original_src/Midas Design+/Dbase/*.sdb` (33개 파일)
* **바이너리 역공학 명세**: [`docs/03_section_db_specification.md`](file:///f:/PyProject/AltDP_3rd/docs/03_section_db_specification.md)
* **디컴파일 심볼**: `decompiled_src/core_routines/db/` 내 `CSteelSectDB` / `CAluSectDB` 루틴

---

## 2. 상세 구현 명세

### 2.1. SDB 바이너리 파서 고도화 (`src/engine/db/sdb_parser.py`)
* **바이너리 매직 헤더 검증**: `MDSW-SDB` (0x00~0x07) 확인
* **카테고리 및 레코드 파싱**:
  - H-Section, Channel, Angle, Box, Pipe, Tee, Cold-Formed 등 전 카테고리 지원
  - 바이너리 바이트 스트림 정밀 디코딩 (부동소수점 제원: H, B, tw, tf, r, r1, r2 등)
  - 레코드 누락 방지를 위한 Fallback 파서(명칭 기반 치수 추출)와 바이너리 레코드 파서의 하이브리드 결합
* **데이터 모델 (`SectionRecord`)**:
  ```python
  @dataclass
  class SectionRecord:
      name: str                  # 규격 명칭 (예: H 400x200x8x13)
      db_name: str = "KS"        # DB 명칭 (KS, AISC, JIS 등)
      category: str = "H-Section"# 단면 형상 유형
      H: float = 0.0             # 높이 (mm)
      B: float = 0.0             # 폭 (mm)
      tw: float = 0.0            # 복부 두께 (mm)
      tf: float = 0.0            # 플랜지 두께 (mm)
      r: float = 0.0             # 필렛 반경 (mm)
      A: float = 0.0             # 단면적 (cm2)
      Ix: float = 0.0            # 단면2차모멘트 X (cm4)
      Iy: float = 0.0            # 단면2차모멘트 Y (cm4)
      rx: float = 0.0            # 회전반경 X (cm)
      ry: float = 0.0            # 회전반경 Y (cm)
      Zx: float = 0.0            # 소성단면계수 X (cm3)
      Zy: float = 0.0            # 소성단면계수 Y (cm3)
      Sx: float = 0.0            # 탄성단면계수 X (cm3)
      Sy: float = 0.0            # 탄성단면계수 Y (cm3)
      J: float = 0.0             # 비틀림상수 (cm4)
      Cw: float = 0.0            # 뜀상수 (cm6)
      weight: float = 0.0        # 단위중량 (kg/m)
  ```

### 2.2. 단면 데이터베이스 매니저 (`src/engine/db/section_db.py`)
* **`SectionDBManager` 싱글톤/인스턴스 매니저**:
  - `load_database(db_name: str)`: 특정 규격 또는 전체 규격 DB 로드 및 SQLite 인메모리 테이블 매핑
  - `search_sections(keyword: str, category: Optional[str] = None) -> List[SectionRecord]`: 고속 필터링
  - `get_section(db_name: str, section_name: str) -> Optional[SectionRecord]`: 단면 단건 조회
  - `get_available_databases() -> List[str]`: 가용 DB 목록 반환 (33종)
  - `get_categories(db_name: str) -> List[str]`: 특정 DB의 가용 형상 카테고리 목록 반환

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/db/sdb_parser.py`](file:///f:/PyProject/AltDP_3rd/src/engine/db/sdb_parser.py) | [MODIFY] | 바이너리 디코딩 고도화 및 레코드 구조 완성 |
| [`src/engine/db/section_db.py`](file:///f:/PyProject/AltDP_3rd/src/engine/db/section_db.py) | [NEW] | 인메모리 SQLite 기반 단면 DB 매니저 구현 |
| [`tests/engine/test_sdb_parser.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_sdb_parser.py) | [MODIFY] | KS, AISC, JIS 단면 DB 파싱 및 검색 검증 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] `sdb_parser.py`가 `original_src/Midas Design+/Dbase/` 내 `.sdb` 파일을 정상 인식하고 에러 없이 파싱하는지 확인
- [x] `section_db.py`의 `SectionDBManager`가 H형강, 각형강관, C형강 등 주요 규격을 SQLite 테이블로 색인하고 질의 가능한지 확인
- [x] 단면 이름 검색(`search_sections`) 및 치수 속성 접근이 즉각(10ms 이내) 수행되는지 검증
- [x] `pytest tests/engine/test_sdb_parser.py` 테스트 케이스 100% 통과 (오차 0%, 수행시간 < 0.5s)
