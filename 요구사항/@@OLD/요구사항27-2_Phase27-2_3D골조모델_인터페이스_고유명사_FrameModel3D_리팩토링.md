# 요구사항 27-2: Phase 27-2 3D 골조 모델 인터페이스 고유명사 FrameModel3D 리팩토링 명세서

## 1. 개요 및 목적

본 문서는 `src/engine/interop/` 및 관련 모듈에 잔존하는 특정 상용 소프트웨어 고유명사(`Midas*`)를 전면 제거하고, KDS 및 범용 구조 역학 기반의 표준 인터페이스 체계(`Frame*`)로 리팩토링하여 시스템의 독립성과 순수성을 확립하기 위한 상세 명세서입니다.

* **담당 소스 파일**:
  - `src/engine/interop/model_schema.py`
  - `src/engine/interop/mgb_parser.py`
  - `src/engine/interop/mgt_parser.py`
  - `src/engine/interop/__init__.py`
  - `src/engine/project/batch_checker.py`
  - `src/api/routes/interop.py`

---

## 2. 세부 구현 요구사항

### 2.1. 데이터 모델 및 스키마 리팩토링 (`src/engine/interop/model_schema.py`)
기존 `Midas*` 클래스명을 범용 구조 골조 명칭인 `Frame*`으로 일괄 변경:

```python
# 변경 전 -> 변경 후
class MidasNode(BaseModel):       -> class FrameNode(BaseModel):
class MidasElement(BaseModel):    -> class FrameElement(BaseModel):
class MidasMaterial(BaseModel):   -> class FrameMaterial(BaseModel):
class MidasSection(BaseModel):    -> class FrameSection(BaseModel):
class MidasStory(BaseModel):      -> class FrameStory(BaseModel):
class MidasModel3D(BaseModel):    -> class FrameModel3D(BaseModel):
```
- docstring 및 필드 설명 내 "MIDAS Gen" 등의 명칭을 "3D Structural Frame Model" 등 범용 공학 용어로 치환.

### 2.2. 파서 및 유틸리티 클래스 리팩토링
1. **`src/engine/interop/mgb_parser.py`**:
   - `class MidasForceParser` $\rightarrow$ `class FrameForceParser`
   - 메서드명 및 docstring 내 `MIDAS Gen` $\rightarrow$ `3D Frame Model Forces`
2. **`src/engine/interop/mgt_parser.py`**:
   - `MgtParser.parse_text()`의 반환 타입을 `MidasModel3D` $\rightarrow$ `FrameModel3D`로 갱신.
   - 모듈 docstring: `MIDAS Gen MGT Text Script Parser` $\rightarrow$ `3D Frame MGT Text Script Parser and Model Builder`
3. **`src/engine/interop/__init__.py`**:
   - 노출 심볼 및 `__all__` 갱신:
     ```python
     from src.engine.interop.model_schema import (
         FrameNode,
         FrameElement,
         FrameMaterial,
         FrameSection,
         FrameStory,
         FrameModel3D,
         MemberForce,
         GoverningForceSummary,
     )
     from src.engine.interop.mgt_parser import MgtParser
     from src.engine.interop.mgb_parser import FrameForceParser
     ```

### 2.3. 일괄 설계 검토 엔진 동기화 (`src/engine/project/batch_checker.py`)
- `from src.engine.interop.model_schema import MidasModel3D` $\rightarrow$ `FrameModel3D`
- 모듈 docstring: `Batch Design Checking Engine for MIDAS Gen 3D Frame Models` $\rightarrow$ `Batch Design Checking Engine for 3D Frame Models`

### 2.4. FastAPI 연동 라우트 동기화 (`src/api/routes/interop.py`)
- APIRouter 태그 및 설명:
  - `tags=["MIDAS Gen Interoperability"]` $\rightarrow$ `tags=["3D Frame Model Interoperability"]`
  - 엔드포인트 docstring 내 `MIDAS Gen .mgt` $\rightarrow$ `3D Frame .mgt`

---

## 3. 검증 및 완료 기준 (Definition of Done)

1. `src/engine/interop/` 내 모든 파일에서 `Midas` 고유명사 클래스 및 docstring 소거 완료.
2. `src/engine/project/batch_checker.py` 및 `src/api/routes/interop.py` 연동 정상화.
3. `pytest tests/engine/test_mgt_parser.py tests/engine/test_governing_lcb.py tests/engine/test_batch_checker.py` 실행 시 100% 통과 (테스트 파일 내 import 동기화 병행).
