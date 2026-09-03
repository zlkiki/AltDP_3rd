# 요구사항 16-2: 해석 결과 부재력 파서 및 최악 하중조건 (Governing LCB) 자동 선별 (Phase 16-2)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* MIDAS Gen / Building 해석 결과 파일(`.mgt` 내 `*FORCE` 및 SQLite/Access `.db`, `.mgb`)로부터 하중조합별 6자유도 계수 부재력($P, V_y, V_z, M_y, M_z, T$)을 고속 추출합니다.
* 수십~수백 개의 하중조합(LCB) 중 각 부재의 단면 설계를 결정짓는 **지배 하중조합(Governing Load Combinations)**을 P-M 상관도 및 전단 포락선 기준으로 자동 압축·선별합니다.

---

## 2. 세부 개발 명세

### 2.1. 부재력 데이터 파서 (`src/engine/interop/mgb_parser.py`)
* **파싱 대상**:
  - `*LOAD COMBINATION` : 하중조건(CB, CS) 및 하중계수($1.2D + 1.6L, 1.2D + 1.0E$ 등)
  - `*FORCE-BEAM` / `*FORCE-COLUMN` : 요소별, 하중조합별, 절점 위치($I, M, J$) 부재력
  - SQLite/Access `.db` 테이블: `BeamForce`, `ColumnForce`, `WallForce` 테이블 쿼리

### 2.2. 최악 하중조건 (Governing LCB) 자동 선별기 (`src/engine/interop/governing_lcb.py`)
* **부재별 지배 하중조건 필터링 알고리즘**:
  1. **RC / 철골 기둥 (P-M 이축 휨)**:
     - $\max(P_u), \min(P_u)$ (최대 압축 / 최대 인장)
     - $\max(|M_{uy}|), \max(|M_{uz}|)$ (각 주축별 최대 모멘트)
     - AltDP 간이 P-M 솔버 기반 최대 DCR($\text{DCR}_{\max}$) 유발 상위 4~8개 LCB 선별
  2. **RC / 철골 보 (휨 & 전단)**:
     - 단부($I, J$) 및 중앙($M$)에서의 $\max(M_u^+), \max(M_u^-)$ (최대 정/부 모멘트)
     - 지점부 $\max(|V_u|)$ (최대 전단력)
  3. **RC 전단벽**:
     - $\max(P_u), \max(M_u), \max(V_u)$ 및 P-M 포락선 극점 LCB 선별
* **압축 효과**: 부재당 수백 개 LCB $\rightarrow$ 설계 검토용 핵심 4~12개 LCB로 지능적 압축 (계산 시간 90% 이상 절감).

---

## 3. 데이터 스키마 (Pydantic DTO)

```python
from pydantic import BaseModel, Field
from typing import List, Dict

class MemberForce(BaseModel):
    lcb_name: str
    position: str  # "I", "M", "J"
    p: float       # 축력 (kN)
    vy: float      # y축 전단력 (kN)
    vz: float      # z축 전단력 (kN)
    my: float      # y축 휨모멘트 (kN*m)
    mz: float      # z축 휨모멘트 (kN*m)
    t: float       # 비틀림모멘트 (kN*m)

class GoverningForceSummary(BaseModel):
    member_id: int
    member_type: str
    total_lcb_count: int
    governing_lcb_list: List[str]
    critical_forces: List[MemberForce]
    max_dcr_estimated: float
```

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **부재력 일치도**: MIDAS Gen 해석 결과 테이블의 단면력과 파싱된 단면력 오차 0.0%.
- [ ] **지배 LCB 선별 정확도**: 전체 LCB 전수 해석 시의 최대 DCR과 지배 LCB 선별 후의 최대 DCR이 100% 일치.
- [ ] **단위 테스트 통과**: `tests/engine/test_governing_lcb.py` 작성 및 통과.
