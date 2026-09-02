# 요구사항 17-1: ezdxf 기반 2D 배근 상세도 CAD(DXF) 생성 엔진 (Phase 17-1)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+ 원본 4대 메인 폼뷰 중 도면 뷰(`CMainFormViewDraw`)의 CAD 생성 기능을 순수 Python `ezdxf` 라이브러리를 이용하여 웹 마이그레이션합니다.
* RC 보/기둥/벽체/기초 단면 배근도, 입면 배근도 및 배근 일람표(Schedule Table)를 AutoCAD 호환 표준 `.dxf` 벡터 도면으로 자동 생성합니다.

---

## 2. 세부 개발 명세

### 2.1. CAD 도면 생성 코어 (`src/report/cad_exporter.py`)
* **표준 레이어 및 스타일 시스템**:
  - `S-CONC` (콘크리트 외곽선, 색상: Cyan, 선가중치: 0.35mm)
  - `S-REBAR-MAIN` (주철근, 색상: Red, 선가중치: 0.50mm)
  - `S-REBAR-SUB` (스터럽/대근/배력근, 색상: Green, 선가중치: 0.25mm)
  - `S-DIM` (치수선 및 치수 보조선, 색상: Yellow, 문자 크기 2.5mm)
  - `S-TEXT` (부재명, 주석, 배근 표기, 색상: White)
  - `S-BORDER` (도각 및 도면 테두리, Title Block)
* **부재별 도면화 생성기**:
  - **RC 보**: 지점부($I, J$) 및 중앙부($M$) 단면 배근도, 주근/늑근 꺾임 상세, 앵커 정착 상세.
  - **RC 기둥/벽체**: 띠철근/나선철근 단면 배근도, 수직근 이음 상세.
  - **RC 기초/옹벽**: 상/하부 양방향 배근도, 주철근 배근 단면도.

### 2.2. 배근 일람표 (Schedule Table) 생성기 (`src/report/cad_schedule.py`)
* 층별/부재별 배근 리스트(보 일람표, 기둥 일람표, 벽체 일람표)를 표(Grid Table) 형태로 DXF 도면 영역에 자동 배열.
* 도면 축척(1:20, 1:30, 1:50)에 따른 치수선 및 폰트 크기 자동 스케일링.

---

## 3. 데이터 스키마 및 인터페이스

```python
from pydantic import BaseModel
from typing import List, Optional

class RebarDetail(BaseModel):
    bar_size: str      # "D19", "D22", "D25"
    count: int
    shape_type: str    # "STRAIGHT", "L_HOOK", "U_STIRRUP"
    length_mm: float

class CADExportOptions(BaseModel):
    member_type: str   # "BEAM", "COLUMN", "WALL", "FOOTING"
    scale: str         # "1:20", "1:30", "1:50"
    include_schedule: bool = True
    include_title_block: bool = True
```

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **CAD 호환성 검증**: 생성된 `.dxf` 파일이 AutoCAD, LibreCAD 등에서 깨짐 없이 열리고 레이어/색상 정상 표현.
- [ ] **형상 정밀도**: 단면 치수선, 철근 위치, 피복두께가 입력 파라미터와 100% 일치.
- [ ] **단위 테스트 통과**: `tests/report/test_cad_exporter.py` 작성 및 통과.
