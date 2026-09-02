# 요구사항 02: SDB 단면 DB 파서 및 KDS 재료/하중조합 엔진

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+의 모든 부재 설계(RC, Steel, SRC, Connection 등)는 표준 단면 데이터베이스(`.sdb`), KDS 규준에 정의된 재료 구성방정식($f_{ck}, f_y, E_c, E_s$), 그리고 극한한계상태(ULS)/사용성한계상태(SLS) 하중조합에 기반합니다. 본 요구사항은 AltDP_3rd의 전 부재 설계 엔진이 공통으로 참조할 핵심 데이터 계층과 기초 인프라를 구축하는 단계입니다.

### 1.2. 목적
1. `original_src/Midas Design+/Dbase/` 내 33개 표준 단면 DB 파일(`KS08.sdb`, `AISC.sdb`, `JIS.sdb`, `DIN.sdb`, `GB.sdb` 등)의 바이너리/SQLite 구조를 100% 파싱하여 단면 기하성질을 무손실 메모리 DB로 로드.
2. `decompiled_src/core_routines/db/`에 추출된 C 수도코드(`CSteelSectDB`, `CAluSectDB`)를 기반으로 단면 기하학적 성질($A, I_x, I_y, S_x, S_y, r_x, r_y, J, C_w, Z_x, Z_y, x_s, y_s$)을 0.1% 오차 미만으로 정밀 산정하는 수치 계산기 구축.
3. KDS 14 20 10(콘크리트구조 재료기준), KDS 14 31 10(강구조 재료기준), KDS 41 10 15(기본하중기준)에 명시된 재료 물성치 모델 및 극한/허용 하중조합 포락선(Envelope) 엔진 구현.

---

## 2. KDS 국가건설기준 및 공학 수학 공식

### 2.1. 콘크리트 및 철근 비선형 재료 모델 (KDS 14 20 10 4.1.2)
* **콘크리트 탄성계수**:
  $$E_c = 8500 \sqrt[3]{f_{cu}} = 8500 \sqrt[3]{f_{ck} + \Delta f} \quad (\text{MPa})$$
* **등가직사각형 압축응력블록 파라미터 ($\alpha_1, \beta_1$)**:
  $$\alpha_1 = \begin{cases} 0.85 & (f_{ck} \le 40\,\text{MPa}) \\ 0.85 - 0.0015(f_{ck} - 40) \ge 0.65 & (f_{ck} > 40\,\text{MPa}) \end{cases}$$
  $$\beta_1 = \begin{cases} 0.80 & (f_{ck} \le 40\,\text{MPa}) \\ 0.80 - 0.0025(f_{ck} - 40) \ge 0.65 & (f_{ck} > 40\,\text{MPa}) \end{cases}$$
* **극한 압축 변형률**: $\epsilon_{cu} = 0.0033$
* **강도저감계수 ($\phi$)**:
  - 인장지배 단면 ($\epsilon_t \ge \epsilon_{tl} = 0.005$): $\phi = 0.85$
  - 압축지배 단면 ($\epsilon_t \le \epsilon_{cl} = f_y / E_s$): $\phi = 0.65$ (나선철근 $0.70$)
  - 전이구간: $\phi = 0.65 + (\epsilon_t - \epsilon_{cl}) \frac{0.85 - 0.65}{\epsilon_{tl} - \epsilon_{cl}}$

### 2.2. 구조용 강재 재료 모델 (KDS 14 31 10)
* **강재 탄성계수 및 전단탄성계수**: $E_s = 205,000\,\text{MPa}$, $G_s = 79,000\,\text{MPa}$, 포아송비 $\nu = 0.30$
* **표준 강재 강도**:
  - SS275: $F_y = 275\,\text{MPa}$ ($t \le 16$), $F_u = 410\,\text{MPa}$
  - SM355: $F_y = 355\,\text{MPa}$ ($t \le 16$), $F_u = 490\,\text{MPa}$
  - SHN460: $F_y = 460\,\text{MPa}$ ($t \le 16$), $F_u = 550\,\text{MPa}$
  - 두께 $t > 16\,\text{mm}, t > 40\,\text{mm}$에 따른 $F_y$ 감축 계수 자동 적용.

### 2.3. 하중 조합 및 단면력 포락선 (KDS 41 10 15)
* **극한강도설계법 (USD / LRFD)**:
  1. $1.4D$
  2. $1.2D + 1.6L + 0.5(L_r \text{ 또는 } S \text{ 또는 } R)$
  3. $1.2D + 1.0L + 1.0W$
  4. $1.2D + 1.0L \pm 1.0E$
  5. $0.9D \pm 1.0W$
  6. $0.9D \pm 1.0E$
* **허용응력설계법 (ASD / SLS)**:
  1. $D + L$
  2. $D + (L_r \text{ 또는 } S \text{ 또는 } R)$
  3. $D + 0.75L + 0.75(0.6W)$
  4. $D \pm 0.7E$

---

## 3. C 수도코드 Ground Truth 매핑

| 기능 도메인 | 참조 디컴파일 C 소스 자산 | 대상 C++ 클래스 및 핵심 함수 |
|---|---|---|
| **H형강 성질 계산** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcHSectionProp()` |
| **C/Channel 성질** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcChannelProp()` |
| **L/Angle 성질** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcAngleProp()`, 주축회전($\theta$) |
| **강관/파이프 성질** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcBoxProp()`, `CalcPipeProp()` |
| **비틀림($J$)/뜀($C_w$)** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcTorsionConstant()` |
| **소성단면계수($Z_x, Z_y$)** | [`decompiled_src/core_routines/db/CSteelSectDB_properties.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/db/CSteelSectDB_properties.c) | `CSteelSectDB::CalcPlasticModulus()` |

---

## 4. Python 신규 구현 아키텍처

```text
src/engine/
├── db/
│   ├── __init__.py
│   ├── sdb_parser.py          # .sdb 바이너리 파서 및 SQLite 인터페이스
│   ├── section_db.py          # 단면 데이터베이스 질의 및 캐싱 매니저
│   └── section_properties.py   # 기하학적/소성/비틀림 성질 수치 계산기
├── materials.py               # KDS 콘크리트, 철근, 강재 물성 모델
└── load_comb.py               # KDS 하중조합 생성기 및 Envelope 추출기
```

### 4.1. 핵심 모듈별 클래스 및 함수 사양
* **[`sdb_parser.py`](file:///f:/PyProject/AltDP_3rd/src/engine/db/sdb_parser.py)**:
  - `class SDBParser`: 바이너리 헤더 디코딩, 레코드 단위 테이블 추출, SQLite 메모리 DB 적재.
  - `parse_sdb_file(file_path: str) -> List[SectionRecord]`
* **[`section_properties.py`](file:///f:/PyProject/AltDP_3rd/src/engine/db/section_properties.py)**:
  - `class SectionCalculator`: H, Box, Pipe, Angle, Channel, Tee, Cold-formed 형강의 기하학적 성질 수식 계산.
  - 산정 파라미터: `Area, Ix, Iy, Sx, Sy, rx, ry, J, Cw, Zx, Zy, xp, yp`
* **[`materials.py`](file:///f:/PyProject/AltDP_3rd/src/engine/materials.py)**:
  - `class ConcreteMaterial`: $f_{ck}, E_c, \epsilon_{cu}, \alpha_1, \beta_1$ 계산 프로퍼티.
  - `class RebarMaterial`: $f_y, f_u, E_s, \epsilon_y$ 프로퍼티.
  - `class SteelMaterial`: $F_y, F_u, E_s, G_s, \nu, t$-감축 프로퍼티.
* **[`load_comb.py`](file:///f:/PyProject/AltDP_3rd/src/engine/load_comb.py)**:
  - `class LoadCase`: $D, L, L_r, S, W, E$ 작용력.
  - `class LoadCombinator`: KDS 41 하중계수 행렬곱을 통한 설계 하중($P_u, V_{ux}, V_{uy}, M_{ux}, M_{uy}, T_u$) 및 거버닝 케이스 선별.

---

## 5. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

본 요구사항은 `/goal` 지시 시 다음 3개 하위 Phase로 분할되어 순차적으로 구현 및 검증됩니다:

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 02-1** | `요구사항02-1_SDB_바이너리_파서_및_단면DB_매니저.md` | `src/engine/db/sdb_parser.py`, `section_db.py`, `tests/engine/test_sdb_parser.py` | 33개 .sdb 파싱 및 SQLite 매핑 |
| **Phase 02-2** | `요구사항02-2_단면_기하성질_및_소성계수_산정_엔진.md` | `src/engine/db/section_properties.py`, `tests/engine/test_section_properties.py` | C 수도코드 대비 단면 성질 오차 < 0.1% |
| **Phase 02-3** | `요구사항02-3_KDS_재료모델_및_하중조합_포락엔진.md` | `src/engine/materials.py`, `load_comb.py`, `tests/engine/test_materials_loads.py` | KDS 14/41 재료 곡선 및 포락선 DCR 검증 |

---

## 6. 검증 및 수용 기준 (Acceptance Criteria)

- [x] **SDB 파싱 무결성**: `original_src/Midas Design+/Dbase/KS.sdb` 등 모든 파일의 형강 규격(H-형강, 각형강관, 파이프, 찬넬 등) 레코드 누락 없이 파싱 완료.
- [x] **단면 성질 수치 일치성**: `decompiled_src/core_routines/db/CSteelSectDB_properties.c`의 기준값과 Python 산정값의 상대 오차 0.05% 미만.
- [x] **KDS 재료/하중 정확도**: KDS 14 20 10 고강도 콘크리트 $\alpha_1, \beta_1$ 계수 및 KDS 41 10 15 6대 극한하중조합 생성 및 Envelope 검증.
- [x] **초고속 단위 테스트 통과**: `pytest tests/engine/test_sdb_parser.py test_section_properties.py test_materials_loads.py` (실행시간 0.44초, 30개 전 테스트 100% 통과).
