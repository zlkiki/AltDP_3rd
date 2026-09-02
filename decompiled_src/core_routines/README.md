# AltDP_3rd Decompiled Core Routines Index (Ground Truth Assets)

본 문서는 Midas Design+ 원본 바이너리(`original_src/Midas Design+/`)로부터 **Ghidra Headless 자동 추출 파이프라인(`scripts/ghidra_extract.py`)**을 통해 무손실 C 수도코드로 선별 추출된 **핵심 공학 알고리즘 단일 기준점(Single Source of Truth, Ground Truth)** 색인표입니다.

모든 MFC GUI 다이얼로그 및 윈도우 루프 코드가 배제되고, **순수 비선형 수치해석, 부재 단면 적분, KDS 설계식 분기 알고리즘**만 선별 수록되었습니다.

---

## 1. 디렉토리 구조 맵 (Directory Layout)

```text
decompiled_src/core_routines/
├── README.md               # [SSOT] 전체 핵심 심볼 총괄 색인표
├── solver/                 # Group 1: P-M 상관도 및 비선형 수치해석 솔버
│   ├── solver__CHK_BCCO_*.c
│   ├── solver__CHK_BCGR_*.c
│   └── solver_meta.json
├── rc/                     # Group 2: RC 5대 부재 (보, 벽체, 슬래브, 기초, 옹벽)
│   ├── rc__CHK_BBBE_*.c
│   ├── rc__CHK_BWUW_*.c
│   ├── rc__CHK_SLAB_*.c
│   ├── rc__CHK_UFDN_*.c
│   ├── rc__CHK_URAB_*.c
│   ├── rc__CHK_URBE_*.c
│   └── rc_meta.json
├── steel/                  # Group 3 & 4: 철골 부재 및 접합부/주각부
│   ├── steel__CHK_USMC_*.c
│   ├── steel__CHK_USBP_*.c
│   ├── steel__CHK_USBC_*.c
│   ├── steel__CHK_USEP_*.c
│   ├── steel__CHK_USWE_*.c
│   ├── steel__CHK_USWO_*.c
│   ├── steel__CHK_USPG_*.c
│   ├── steel__CHK_USWB_*.c
│   └── steel_meta.json
└── db/                     # Group 5: 단면 기하학적 성질 및 DB 연산
    ├── db__*.c
    └── db_meta.json
```

---

## 2. 도메인별 핵심 디컴파일 루틴 & KDS 설계기준 매핑표

### Group 1: P-M 상관도 및 비선형 수치해석 솔버 (`solver/`)
| 원본 바이너리 | 핵심 심볼 / 함수 | C 파일명 | 엔지니어링 역할 및 KDS 기준 |
|---|---|---|---|
| `DPLUS_RCS.dll` | `?CHK_BCCO@CRCSCodeCheck@@...` | `solver__CHK_BCCO_...c` | 기둥 3차원 P-M 상관곡선, 중립축 수렴 루프, 이축휨 브레슬러식 (KDS 14 20 20) |
| `DPLUS_RCS.dll` | `?CHK_BCGR@CRCSCodeCheck@@...` | `solver__CHK_BCGR_...c` | 기둥 부재 그룹 검토 및 최악 하중조건(Worst Envelope) 판정 |
| `DPLUS_DB.dll` | `CDBSolverTool::ConvertModel_Plate` | `solver_db_...c` | FEM 평판 요소/절점/단면력 입출력 변환 및 단위 환산 |
| `DgnSolver/Iterative` | `Iterative_SolveNonlinearTensionCutoff` | `solver__Iterative_TensionCutoff_Loop.c` | 지반 인장분리(Tension Cut-off) 및 접촉 비선형 반복 솔버 |
| `DPLUS_STEEL.dll` | `CUSBPPModeDlg_CalculateConcreteSpring` | `solver_baseplate_...c` | 베이스플레이트 콘크리트 압축 지압 스프링 ($k_{conc}$) 및 볼트 인장 |
| `DPLUS_RCS.dll` | `CURBUPModeDlg_MapWallBoundaries` | `solver_wall_...c` | 지하외벽 2방향 수치해석 및 다층 지지조건 경계조건 매핑 |


### Group 2: RC 5대 부재 핵심 설계 엔진 (`rc/`)
| 원본 바이너리 | 핵심 심볼 / 함수 | C 파일명 | 엔지니어링 역할 및 KDS 기준 |
|---|---|---|---|
| `DPLUS_RCS.dll` | `?CHK_BBBE@CRCSCodeCheck@@...` | `rc__CHK_BBBE_...c` | RC 보 복철근 휨강도($\phi M_n$), 전단-비틀림, 처짐 유효단면2차모멘트($I_e$) (KDS 14 20 10/22/30) |
| `DPLUS_RCS.dll` | `?CHK_BWUW@CRCSCodeCheck@@...` | `rc__CHK_BWUW_...c` | RC 전단벽 면내 전단강도($V_c, V_s$) 및 특수경계요소 판정 (KDS 14 20 20) |
| `DPLUS_RCS.dll` | `?CHK_SLAB@CRCSCodeCheck@@...` | `rc__CHK_SLAB_...c` | RC 1방향/2방향 슬래브 직접설계법 및 2방향 펀칭전단 검토 (KDS 14 20 70) |
| `DPLUS_RCS.dll` | `?CHK_UFDN@CRCSCodeCheck@@...` | `rc__CHK_UFDN_...c` | 독립/복합 기초 지반 접지압, 2방향 펀칭전단($d/2$) 및 휨설계 (KDS 14 20 00) |
| `DPLUS_RCS.dll` | `?CHK_URAB@CRCSCodeCheck@@...` | `rc__CHK_URAB_...c` | 지하외벽 및 옹벽 토압론, 전도/활동/지지력 안전율 계산 (KDS 14 20 00) |
| `DPLUS_RCS.dll` | `?CHK_URBE@CRCSCodeCheck@@...` | `rc__CHK_URBE_...c` | 지중보(Underground Beam) 휨/전단 및 지반 반력 분배 검토 |

### Group 3 & 4: 철골 부재 및 접합부/베이스플레이트 (`steel/`)
| 원본 바이너리 | 핵심 심볼 / 함수 | C 파일명 | 엔지니어링 역할 및 KDS 기준 |
|---|---|---|---|
| `DPLUS_STEEL.dll` | `?CHK_USMC@CSTLCodeCheck@@...` | `steel__CHK_USMC_...c` | 철골 보/기둥/가새 폭두께비, LTB 휨좌굴, $P_u/\phi P_n \ge 0.2$ 상호작용 (KDS 14 31 10/15) |
| `DPLUS_STEEL.dll` | `?CHK_USBP@CSTLCodeCheck@@...` | `steel__CHK_USBP_...c` | 주각부 베이스플레이트 지압응력 분포, $t_p$ 두께, 앵커볼트 인장/전단 (KDS 14 31 25) |
| `DPLUS_STEEL.dll` | `?CHK_USBC@CSTLCodeCheck@@...` | `steel__CHK_USBC_...c` | 고장력볼트 전단/인장/지압 강도 및 블록전단파단(Block Shear) (KDS 14 31 25) |
| `DPLUS_STEEL.dll` | `?CHK_USEP@CSTLCodeCheck@@...` | `steel__CHK_USEP_...c` | 보-기둥 모멘트 엔드플레이트 접합부 두께 및 볼트 장력 검토 |
| `DPLUS_STEEL.dll` | `?CHK_USWE@CSTLCodeCheck@@...` | `steel__CHK_USWE_...c` | 필릿용접 및 그루브용접 유효목두께 및 허용응력 검토 |
| `DPLUS_STEEL.dll` | `?CHK_USWO@CSTLCodeCheck@@...` | `steel__CHK_USWO_...c` | 철골 보 웨브 개구부(Web Opening) 전단 및 보강재 검토 |
| `DPLUS_STEEL.dll` | `?CHK_USPG@CSTLCodeCheck@@...` | `steel__CHK_USPG_...c` | 플레이트 거더(Plate Girder) 휨 및 전단좌굴 검토 |
| `DPLUS_STEEL.dll` | `?CHK_USWB@CSTLCodeCheck@@...` | `steel__CHK_USWB_...c` | 가새 부재 인장 순단면 파단($U$) 및 거셋플레이트 검토 |

### Group 5: 단면 기하학적 성질 및 DB 연산 (`db/`)
| 원본 바이너리 | 핵심 심볼 / 함수 | C 파일명 | 엔지니어링 역할 및 수식 |
|---|---|---|---|
| `DPLUS_DB.dll` | `CSteelSectDB` / `CAluSectDB` | `db__*.c` | 형강 및 임의 단면 도심, $I_x, I_y, Z_x, Z_y, J, C_w$ 기하성질 산출 |

---

## 3. 포팅 활용 가이드 (Zero-Dependency Python Architecture)

1. **오차 0.1% 미만 무결성 보증**:
   - Python 설계 엔진(`src/engine/rc/`, `src/engine/steel/`, `src/engine/solver/`) 개발 시 본 C 수도코드의 분기 조건문과 계수식을 직접 대조하여 구현합니다.
2. **독립성 유지**:
   - MFC DLL이나 동글 락 바이너리에 의존하지 않고, 순수 Python 수학/수치 알고리즘으로 완전 마이그레이션합니다.
