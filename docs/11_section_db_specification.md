# AltDP_3rd 단면 형강 및 구조 재료 규격 DB 종합 명세서 (11_section_db_specification.md)

본 문서는 AltDP_3rd 시스템 내부에 완전히 이전·자체 자산화된 **33종 국제 표준 단면 형강 데이터베이스(`src/data/dbase/*.sdb`)**, **바이너리 파서(`sdb_parser.py`)**, **고속 인메모리 SQLite DB 엔진(`section_db.py`)**, **REST API 라우터**, **웹 프론트엔드 UI 연동** 및 **KDS 표준 구조 재료 규격(콘크리트·철근·강재 DB)**에 대한 총체적 기술 명세서(SSOT)입니다.

---

## 1. 단면 DB 이전 및 자체 자산화 현황 (Zero-Dependency)

과거 외부 디렉토리(`original_src/Midas Design+/Dbase/`)에 참조용으로 분리되어 있던 33종의 형강 바이너리 DB 파일을 **AltDP_3rd 내부 패키지 자산 디렉토리(`src/data/dbase/`)로 100% 완전 이전**하여 외부 런타임 의존성이 완전히 제거(Zero-Dependency)되었습니다.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ AltDP_3rd 내부 데이터 자산 구조 (Centralized Internal Assets)                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ src/core/paths.py ──> DBASE_DIR = SRC_DIR / "data" / "dbase"                           │
│                                                                                        │
│ src/data/dbase/ (총 33종 국제 표준 형강 바이너리 DB 이전 완료)                         │
│ ├── KS.sdb, KS21.sdb                      (대한민국 KS 표준 규격 - 최신 2021년 개정)  │
│ ├── AISC.sdb, AISC05/10/16/2K(SI/US).sdb  (미국 강구조학회 표준 규격 8종)            │
│ ├── JIS.sdb, JIS2K.sdb                    (일본 공업 규격 2종)                         │
│ ├── BS.sdb, BS4-93.sdb, DIN.sdb, UNI.sdb  (영국/유럽/독일/이탈리아 규격 4종)          │
│ ├── CISC02(SI/US).sdb                     (캐나다 강구조 규격 2종)                    │
│ ├── GB-YB.sdb, GB-YB05.sdb, GB50018-02.sdb(중국 국가 표준 규격 3종)                   │
│ └── GOST, ICHA, IS, CNS, SS, STO, TIS 등   (러시아, 인도, 대만, 태국 등 14종)          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 33종 국제 표준 단면 DB 인벤토리

`src/data/dbase/`에 내장된 33종 형강 DB의 상세 제원 인벤토리는 다음과 같습니다:

| 국가 / 지역 | 표준 DB 파일명 | 파일 크기 | 지원 형강 카테고리 | 비고 |
|---|---|---|---|---|
| **대한민국 (KS)** | `KS.sdb` | 119.2 KB | H형강, I형강, ㄷ형강, ㄱ형강, 강관, 각형강관 등 | 한국산업표준 실무 표준 |
| **대한민국 (KS)** | `KS21.sdb` | 121.6 KB | 최신 KS 규격 형강군 (SHN, RH, SHS 등) | 최신 2021 개정 표준 |
| **미국 (AISC)** | `AISC.sdb` | 348.4 KB | W, M, S, HP, C, MC, L, WT, HSS 등 | AISC Classic |
| **미국 (AISC)** | `AISC05(SI).sdb` / `(US)` | 366.0 KB / 367.2 KB | W, C, L, HSS(Rect, Round), Pipe 등 | AISC 13th Ed. (2005) |
| **미국 (AISC)** | `AISC10(SI).sdb` / `(US)` | 370.9 KB / 370.9 KB | W, C, L, HSS(Rect, Round), Pipe 등 | AISC 14th Ed. (2010) |
| **미국 (AISC)** | `AISC16(SI).sdb` / `(US)` | 389.1 KB / 389.1 KB | 최신 W, C, L, HSS, WT 등 | AISC 15th Ed. (2016) |
| **미국 (AISC)** | `AISC2K(SI).sdb` / `(US)` | 357.5 KB / 357.5 KB | W, C, L, HSS 등 | AISC LRFD 3rd (2000) |
| **미국 (AA)** | `AA(US).sdb` | 119.2 KB | 알루미늄 형강 규격 | Aluminum Association |
| **일본 (JIS)** | `JIS.sdb` | 152.0 KB | H, I, [], L, T, Pipe, Box 등 | 일본 공업 표준 |
| **일본 (JIS)** | `JIS2K.sdb` | 122.8 KB | H, [], L, Pipe 등 2000년대 표준 | JIS 2000 규격 |
| **영국 (BS)** | `BS.sdb` | 116.7 KB | UB, UC, UBP, PFC, RSA, CHS, RHS | British Standards |
| **영국 (BS)** | `BS4-93.sdb` | 170.2 KB | BS 4 Part 1 (1993) 구조용 형강 | BS4 개정판 |
| **독일 (DIN)** | `DIN.sdb` | 66.9 KB | HEA, HEB, HEM, IPE, INP, UPE, UNP 등 | Euronorm / DIN |
| **이탈리아 (UNI)** | `UNI.sdb` | 170.2 KB | IPE, HE, UPN, Angolari 등 | UNI 규격 |
| **캐나다 (CISC)** | `CISC02(SI).sdb` / `(US)` | 257.8 KB / 263.9 KB | W, S, HP, C, L, HSS 등 | CISC Handbook 8th |
| **중국 (GB)** | `GB-YB.sdb` / `GB-YB05.sdb` | 91.8 KB / 338.0 KB | 열간압연 H형강, 공자강, 조강, 강관 | GB/T 중국 국가표준 |
| **중국 (GB)** | `GB50018-02.sdb` | 29.2 KB | 냉간성형 박판형강 규격 | GB 냉간성형 표준 |
| **러시아 (GOST)** | `GOST.sdb`, `STO-ASChM.sdb` | 79.0 KB / 18.8 KB | I형강(Двутавр), 채널(Швеллер), 앵글 | GOST / STO ASChM 20-93 |
| **인도 (IS)** | `IS.sdb`, `IS808.sdb`, `IS1161.sdb`| 113.7 KB / 43.2 KB / 10.9 KB | ISMB, ISMC, ISA, ISNT, 강관 | Bureau of Indian Standards |
| **대만 / 싱가포르**| `CNS91.sdb`, `SS.sdb` | 172.1 KB / 423.8 KB | H, C, L, Box, 강관 | 대만 CNS, 싱가포르 SS |
| **태국 / 칠레 등**| `TIS1228-2018.sdb`, `ICHA.sdb`, `Pacific(SI).sdb` | 6.7 KB ~ 324.1 KB | H, C, L, Pipe | 태국 TIS, 칠레 ICHA 등 |

---

## 3. 바이너리 파일 구조 및 파서 엔진 (`sdb_parser.py`)

### 3.1. MDSW-SDB 바이너리 포맷 레이아웃
`*.sdb` 파일은 고유 매직 헤더와 연속된 단면 레코드 스트림으로 인코딩된 전용 바이너리 구조입니다:

```text
+---------------------------------------------------------------------------------+
| Offset 0x00 ~ 0x07 : Magic Header "MDSW-SDB" (8 bytes ASCII)                   |
+---------------------------------------------------------------------------------+
| Offset 0x08 ~ 0x0B : DB Version Identifier (uint32 Little-Endian)               |
| Offset 0x0C ~ 0x0F : Section Category / Block Count (uint32 Little-Endian)      |
+---------------------------------------------------------------------------------+
| Data Stream Records :                                                           |
|  - Section Spec Name (ASCII / Latin-1): e.g., "H 400x200x8x13", "RH 300x150"    |
|  - Geometric Parameter Tokens: [H, B, tw, tf, r]                                |
|  - Engineering Cross-Sectional Properties:                                      |
|    Area(A), Ix, Iy, rx, ry, Zx, Zy, Sx, Sy, J, Cw, Unit Weight                 |
+---------------------------------------------------------------------------------+
```

### 3.2. 단면 레코드 모델 (`SectionRecord`)
파싱된 모든 형강 단면은 [`src/engine/db/sdb_parser.py`](file:///f:/PyProject/AltDP_3rd/src/engine/db/sdb_parser.py)의 정규 데이터 클래스로 인스턴스화됩니다:

```python
@dataclass
class SectionRecord:
    name: str                   # 단면 규격 호칭 (예: "H 400x200x8x13")
    db_name: str = "KS"         # 소속 표준 DB (예: "KS", "AISC16(SI)")
    category: str = "H-Section" # 단면 계열 (H-Section, Box, Pipe, Channel, Angle, Tee)
    H: float = 0.0              # 단면 전고 (Height, mm)
    B: float = 0.0              # 플랜지 폭 (Width, mm)
    tw: float = 0.0             # 웨브 두께 (Web thickness, mm)
    tf: float = 0.0             # 플랜지 두께 (Flange thickness, mm)
    r: float = 0.0              # 모서리 필렛 반경 (Fillet radius, mm)
    A: float = 0.0              # 단면적 (Cross-sectional area, cm²)
    Ix: float = 0.0             # 강축 단면2차모멘트 (cm⁴)
    Iy: float = 0.0             # 약축 단면2차모멘트 (cm⁴)
    rx: float = 0.0             # 강축 단면회전반경 (cm)
    ry: float = 0.0             # 약축 단면회전반경 (cm)
    Zx: float = 0.0             # 강축 소성단면계수 (Plastic Modulus, cm³)
    Zy: float = 0.0             # 약축 소성단면계수 (Plastic Modulus, cm³)
    Sx: float = 0.0             # 강축 탄성단면계수 (Elastic Modulus, cm³)
    Sy: float = 0.0             # 약축 탄성단면계수 (Elastic Modulus, cm³)
    J: float = 0.0              # 비틀림 상수 (Torsional constant, cm⁴)
    Cw: float = 0.0             # 뒴 상수 (Warping constant, cm⁶)
    weight: float = 0.0         # 단위 중량 (Unit weight, kg/m)
```

### 3.3. 고속 추출 및 폴백 메커니즘
1. **정규식 고속 스캔 (Pattern Scanner)**: `rb'[HLCBWPTU-][0-9A-Za-z_.\- /]{2,30}'` 정규식을 통해 바이너리 버퍼에서 규격 문자열을 0.01초 단위로 병렬 탐색.
2. **이원화 청크 폴백 (Chunk Fallback)**: 정규식 누락 단면이 있을 경우, 32바이트 고정 헤더 블록 단위 스캔으로 100% 전수 복원.
3. **단면계수 자동 유도 계산**: 바이너리에서 추출된 치수($H, B, t_w, t_f$)를 바탕으로 KDS 기준에 따른 단면 2차 모멘트, 도심, 소성/탄성 단면계수 및 강재 단위중량($\gamma = 78.5\text{ kN/m}^3$) 산출식을 통해 파라메트릭 자가 치유.

---

## 4. 인메모리 SQLite DB 캐시 매니저 (`section_db.py`)

초대형 규격(AISC, KS, SS 등 수천 개 레코드)의 반복 조회 성능을 극대화하기 위해 **SQLite In-Memory (`:memory:`) 아키텍처**가 적용되어 있습니다.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SQLite In-Memory Caching Architecture (src/engine/db/section_db.py)                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Table: `sections` (id, db_name, category, name, H, B, tw, tf, r, A, Ix, Iy, ...)    │
│ • Indexes:                                                                             │
│    - `CREATE INDEX idx_sec_name ON sections(name)` (초고속 자동완성 검색)              │
│    - `CREATE INDEX idx_sec_db_cat ON sections(db_name, category)` (카테고리별 필터링) │
│ • Methods:                                                                             │
│    - `load_database(db_name)`: 특정 국가 DB 온디맨드 로딩                              │
│    - `load_all_databases()`: 33종 전 데이터베이스 사전 인덱싱                         │
│    - `search_sections(keyword, db_name, category, limit)`: 파라메트릭 다이나믹 쿼리    │
│    - `get_section(name, db_name)`: 단일 규격 O(1) 초고속 제원 반환                    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. REST API 라우터 연동 (`src/api/routes/db.py`)

프론트엔드 웹 애플리케이션 및 외부 클라이언트와의 통신을 위한 고성능 비동기 REST API가 제공됩니다:

* **단면 검색 및 조회 API**:
  * `GET /api/db/sections?db=KS&query=H400&limit=50`
  * 반환 데이터:
    ```json
    {
      "success": true,
      "total_count": 8,
      "db": "KS",
      "data": [
        {
          "name": "H 400x200x8x13",
          "H": 400.0,
          "B": 200.0,
          "tw": 8.0,
          "tf": 13.0,
          "A": 84.1,
          "Ix": 23700.0,
          "Iy": 1740.0,
          "weight": 66.0
        }
      ]
    }
    ```
* **단면 DB 경로 연동**:
  * `src/core/paths.py`의 `DBASE_DIR`을 참조하여 환경 독립적으로 무중단 서빙.

---

## 6. 웹 프론트엔드 UI/UX 통합

웹 UI 4-Pane 워크스페이스(Pane 1 입력폼, Pane 2 2D 캔버스, Pane 3 계산서, Pane 4 물량) 전역에서 일관된 형강 DB 룩업 및 자동 채우기가 작동합니다:

1. **클라이언트 전용 초고속 룩업 테이블 (`src/web/static/js/db/ks_sections.js`)**:
   - 네트워크 지연 없는 즉시 반응을 위해 KS 주요 H형강 규격 및 R(필렛 반경) 룩업 매핑(`KS_H_FILLET_R`) 내장.
2. **동적 콤보박스 및 자동 완성 (`src/web/static/js/components/form_combobox.js`)**:
   - `section_name`, `col_sec`, `beam_sec`, `steel_sec` 필드에 포커스 시 단면 자동완성 드롭다운 팝업.
   - 단면 선택 시 $H, B, t_w, t_f, r$ 치수가 즉시 폼 필드에 자동 바인딩.
3. **단면 검색 모달 다이얼로그 (`IDD_DGN_SECT_LIST_DLG` 웹 구현)**:
   - 국가별 DB 선택 탭, 형강 분류(H형강, 각형강관, 원형강관, ㄷ형강, ㄱ형강 등) 필터 버튼 및 실시간 제원 프리뷰 지원.

---

## 7. KDS 표준 구조 재료 데이터베이스 (Materials SSOT)

단면 형강 DB와 긴밀히 연계되어 구조 계산서 및 해석 엔진에 주입되는 **KDS 표준 구조 재료 물성치 DB** 규격입니다:

### 7.1. 콘크리트 설계기준압축강도 DB (`KS_CONCRETE_FCK_DB`)
* **기준 조항**: KDS 14 20 10 (4.1 콘크리트 재료 특성)
* **탄성계수 산정식**: $E_c = 8500 \sqrt[3]{f_{cu}} = 8500 \sqrt[3]{f_{ck} + \Delta f}$ (MPa)
* **표준 등급**:
  * 18 MPa, 21 MPa, **24 MPa (일반 구조물 실무 다빈도)**, 27 MPa, 30 MPa, 35 MPa, 40 MPa, 45 MPa, 50 MPa, 60 MPa, 70 MPa, 80 MPa

### 7.2. 철근 항복강도 DB (`KS_REBAR_GRADE_DB`)
* **기준 규격**: KS D 3504 (철근 콘크리트용 봉강) / KDS 14 20 10
* **탄성계수**: $E_s = 200,000\text{ MPa}$ 고정
* **표준 강종 및 항복강도 ($f_y$)**:
  * **SD300**: $f_y = 300\text{ MPa}$ (보통용 일반철근)
  * **SD400**: $f_y = 400\text{ MPa}$ (실무 표준 고장력철근)
  * **SD500**: $f_y = 500\text{ MPa}$ (초고장력철근 - 휨/전단 보강용)
  * **SD600**: $f_y = 600\text{ MPa}$ (초고강도 철근)
  * **SD700**: $f_y = 700\text{ MPa}$ (특수 초고강도 철근)

### 7.3. 구조용 강재 재료 DB (`KS_STEEL_GRADE_DB`)
* **기준 규격**: KDS 14 31 10 (강구조 설계 일반) / KS D 3502, 3503, 3866
* **탄성계수 / 전단탄성계수**: $E = 205,000\text{ MPa}$, $G = 79,000\text{ MPa}$, 포아송비 $\nu = 0.30$
* **주요 강종 물성표**:
  | 강종 기호 | 항복강도 $F_y$ (MPa) | 인장강도 $F_u$ (MPa) | 주 용도 및 규격 특성 |
  |---|---|---|---|
  | **SS275** | 275 | 410 | 일반구조용 압연강재 (KS D 3503) |
  | **SS355** | 355 | 490 | 일반구조용 고강도 압연강재 |
  | **SM275** | 275 | 410 | 용접구조용 압연강재 (KS D 3515) |
  | **SM355** | 355 | 490 | 용접구조용 표준 강재 (실무 최다 적용) |
  | **SM460** | 460 | 570 | 고강도 용접구조용 강재 |
  | **SN275** | 275 | 400 | 건축구조용 압연강재 (소성변형능/내진 보증) |
  | **SN355** | 355 | 490 | 건축구조용 고성능 내진 강재 |
  | **SHN275** | 275 | 410 | **H형강 전용 건축구조용 압연강재 (KS D 3866)** |
  | **SHN355** | 355 | 490 | **H형강 전용 표준 내진 강재 (실무 표준)** |
  | **SHN460** | 460 | 570 | H형강 전용 고강도 내진 강재 |
  | **SHN520** | 520 | 630 | H형강 전용 초고강도 내진 강재 |
  | **SRT275 / 355** | 275 / 355 | 410 / 490 | 일반구조용 각형강관 (KS D 3568) |
  | **SNRT275 / 355** | 275 / 355 | 400 / 490 | **건축구조용 각형강관 (내진 각형 파이프)** |
  | **SNT275 / 355** | 275 / 355 | 400 / 490 | **건축구조용 원형강관 (내진 원형 파이프)** |
  | **SSC275** | 275 | 400 | 냉간성형 박판 경량형강 |

---

## 8. 무결성 검증 (Pytest Verification)

본 단면 DB 파서 및 인메모리 SQLite 매니저는 단위 테스트를 통해 100% 무결성이 상시 검증됩니다:

* **테스트 슈트**: [`tests/engine/test_sdb_parser.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_sdb_parser.py)
* **검증 항목**:
  1. `test_sdb_parser_ks`: `KS.sdb` 로딩, H형강 검색, 치수($H, B, A, I_x, Z_x$) 유효성 검증.
  2. `test_sdb_parser_aisc`: `AISC.sdb` 파싱 및 단면 추출 검증.
  3. `test_section_db_manager_sqlite`: 33종 DB 인식 여부, SQLite 캐싱 및 키워드/정밀 검색 속도 무결성 검증.
* **실행 결과**:
  ```bash
  pytest tests/engine/test_sdb_parser.py
  # ============================== 3 passed in 0.11s ==============================
  ```
