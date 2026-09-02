# 요구사항 16-1: MIDAS MGT 텍스트 스크립트 파서 및 3D 모델 구축 (Phase 16-1)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* MIDAS Gen / Building의 전체 구조해석 모델 텍스트 파일인 `.mgt` 스크립트를 파싱하여, 3차원 골조 해석 모델의 절점(Node), 요소(Element), 재료(Material), 단면(Section), 층(Story) 정보를 AltDP_3rd의 데이터 모델로 완전 복원합니다.
* C++ 원본의 `DgnPlugIn/` (`AnalysisDB.dll`, `GEN_UmdDataBase.dll`) 역공학 자산을 바탕으로 순수 Python 기반 고속 텍스트 파서를 구축합니다.

---

## 2. 세부 개발 명세

### 2.1. MIDAS MGT 텍스트 명령어 파서 (`src/engine/interop/mgt_parser.py`)
* **핵심 파싱 명령어 블록**:
  - `*NODE` : 절점 번호($\text{ID}$) 및 3차원 좌표 ($X, Y, Z$)
  - `*ELEMENT` : 요소 번호, 요소 유형(`BEAM`, `TRUSS`, `WALL`), 재료 번호, 단면 번호, 구성 절점($N_1, N_2, \dots$)
  - `*MATERIAL` : 콘크리트($f_{ck}$), 철근($f_y$), 강재($F_y, F_u$) 재료 특성치
  - `*SECTION` : 단면 형상 타입(`DBUSER`, `ANGLE`, `CHANNEL`, `H-SECTION`, `RECT`) 및 주요 치수
  - `*STORY` : 층 이름, 층 높이, 층 레벨($Z$)
* **처리 성능**: 10,000줄 이상의 대용량 `.mgt` 파일을 0.2초 이내에 인메모리 구조체로 고속 파싱.

### 2.2. 3D 프레임 기하 및 부재 분류 모델 (`src/engine/interop/model_schema.py`)
* **부재 자동 분류 알고리즘**:
  - 요소 방향 벡터 $\vec{v} = (X_2 - X_1, Y_2 - Y_1, Z_2 - Z_1)$ 기반 분류:
    - $|\vec{v}_z| / \|\vec{v}\| \ge 0.85 \rightarrow$ **기둥 (Column)**
    - $|\vec{v}_z| / \|\vec{v}\| < 0.15 \rightarrow$ **보 (Beam)**
    - $0.15 \le |\vec{v}_z| / \|\vec{v}\| < 0.85 \rightarrow$ **가새 (Brace)**
  - 평판 요소 및 벽체 요소(`*ELEMENT, WALL`) $\rightarrow$ **전단벽 (Wall)**
* **층(Story) 자동 바인딩**: 절점의 $Z$ 좌표를 기준으로 해당 부재가 속한 층(Floor/Story)을 자동 판정.
* **단면 DB 매핑**: Midas SDB 형강 규격명(`H 400x200x8/13` 등)을 AltDP 단면 DB(`src/engine/db/section_db.py`)와 100% 매핑.

---

## 3. 데이터 스키마 (Pydantic DTO)

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MidasNode(BaseModel):
    node_id: int
    x: float
    y: float
    z: float

class MidasElement(BaseModel):
    elem_id: int
    elem_type: str  # "BEAM", "COLUMN", "WALL", "BRACE"
    mat_id: int
    sec_id: int
    nodes: List[int]
    story: Optional[str] = None

class MidasModel3D(BaseModel):
    nodes: Dict[int, MidasNode]
    elements: Dict[int, MidasElement]
    materials: Dict[int, dict]
    sections: Dict[int, dict]
    stories: List[dict]
```

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **MGT 구문 파싱 완성**: 표준 MIDAS Gen `.mgt` 파일 파싱 시 절점, 요소, 재료, 단면 무손실 추출 (100% 일치).
- [ ] **부재 분류 정확도**: 3D 골조 모델에서 보, 기둥, 가새, 벽체 자동 판정 정확도 100%.
- [ ] **단위 테스트 통과**: `tests/engine/test_mgt_parser.py` 작성 및 통과.
