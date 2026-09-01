# 단면 형강 DB 명세서 (03_section_db_specification.md)

## 1. 개요

`original_src/Midas Design+/Dbase/`에 위치한 33개의 `*.sdb` 파일은 마이다스 소프트웨어의 전용 형강 단면 데이터베이스 파일입니다.

* **지원 규격 (33종)**:
  * 한국: `KS.sdb`, `KS21.sdb`
  * 미국: `AISC.sdb`, `AISC05(SI).sdb`, `AISC10(SI).sdb`, `AISC16(SI).sdb`, `AISC2K(SI).sdb` 등
  * 일본: `JIS.sdb`, `JIS2K.sdb`
  * 유럽/영국/독일: `BS.sdb`, `BS4-93.sdb`, `DIN.sdb`, `UNI.sdb`
  * 캐나다/중국/러시아/인도 등: `CISC02`, `GB-YB`, `GOST`, `IS`, `SS` 등

---

## 2. 파일 포맷 바이너리 구조

`*.sdb` 파일은 고정 헤더와 가변 길이 레코드 블록으로 구성된 C/C++ 직렬화 바이너리입니다.

```text
+-------------------------------------------------------------+
| 0x00 ~ 0x07 : Magic Header ("MDSW-SDB")                     |
+-------------------------------------------------------------+
| 0x08 ~ 0x0B : DB Version (uint32)                           |
| 0x0C ~ 0x0F : Section Category Count (uint32)               |
+-------------------------------------------------------------+
| Section Type Blocks (H-Section, Channel, Angle, Tube, etc.) |
|  - Category Name (e.g., "H-Section", "C-Section")           |
|  - Item Count                                               |
|  - Record Data (Name, H, B, tw, tf, r, Area, Ix, Iy, ...)   |
+-------------------------------------------------------------+
```

---

## 3. 형강 파서 및 변환 계획

`src/engine/db/sdb_parser.py`를 통해 모든 `.sdb` 파일을 파싱하여 다음 형태로 제공합니다:
1. **JSON 데이터베이스**: 웹 브라우저에서 초고속 검색 및 필터링이 가능한 JSON 인덱스 파일.
2. **SQLite 데이터베이스**: 고속 SQL 쿼리 및 파라메트릭 조회가 가능한 통합 SQLite DB.
3. **파이썬 Pydantic 모델**: 각 형강 제원에 대한 타입 안전한 객체 모델(`SectionSpec`).
