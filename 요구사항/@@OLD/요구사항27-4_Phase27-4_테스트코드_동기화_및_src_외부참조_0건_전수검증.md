# 요구사항 27-4: Phase 27-4 테스트 코드 동기화 및 src 외부참조 0건 전수 검증 명세서

## 1. 개요 및 목적

본 문서는 Phase 27-1 ~ 27-3에서 단행된 런타임 소스 및 모델 인터페이스 변경 사항을 테스트 코드(`tests/`)에 완벽히 동기화하고, `src/` 전체에 대해 외부 참조 및 고유명사 0건 무결성을 최종 검증하는 마감 명세서입니다.

* **담당 소스 파일**:
  - `tests/engine/test_sdb_parser.py`
  - `tests/engine/test_mgt_parser.py`
  - `tests/engine/test_governing_lcb.py`
  - `tests/engine/test_batch_checker.py`
  - `tests/engine/test_fem_integration.py`
  - `tests/api/test_interop_routes.py`
  - 전체 단위/통합 테스트 스위트 (`pytest`)

---

## 2. 세부 구현 요구사항

### 2.1. 테스트 코드 경로 및 모델 동기화
1. **`tests/engine/test_sdb_parser.py`**:
   - `original_src` 하드코딩 경로를 `src.core.paths.DBASE_DIR`로 변경:
     ```python
     from src.core.paths import DBASE_DIR
     DEFAULT_DB_DIR = str(DBASE_DIR)
     ```
2. **`tests/engine/test_mgt_parser.py`**:
   - `MidasModel3D` $\rightarrow$ `FrameModel3D`, `MidasNode` $\rightarrow$ `FrameNode` 임포트 및 인스턴스 검증 동기화.
3. **`tests/engine/test_governing_lcb.py`**:
   - `MidasForceParser` $\rightarrow$ `FrameForceParser` 임포트 및 호출 동기화.
   - 임시 sqlite 파일명 `test_midas.db` $\rightarrow$ `test_frame.db`로 변경.
4. **`tests/engine/test_batch_checker.py`**:
   - `from src.engine.interop.model_schema import FrameModel3D, FrameNode, FrameElement, FrameSection, MemberForce` 임포트 갱신.
5. **`tests/engine/test_fem_integration.py`**:
   - docstring 내 `against Midas Design+ Ground Truth` $\rightarrow$ `against Analytical Benchmark Ground Truth`로 정리.
6. **`tests/api/test_interop_routes.py`**:
   - API 라우트 테스트 내 태그 및 응답 검증 동기화.

### 2.2. 정적 소스 코드 무결성 전수 검증 (Zero-Match Audit)
`src/` 디렉토리에 대해 정적 문자열 검색을 수행하여 다음 5대 키워드가 **단 1건도 일치하지 않음(0건)**을 검증:

```powershell
# 1. original_src 검색 -> 0건
rg -i "original_src" src/

# 2. decompiled_src 검색 -> 0건
rg -i "decompiled_src" src/

# 3. midas 검색 -> 0건
rg -i "midas" src/

# 4. design+ 검색 -> 0건
rg -i "design\+" src/

# 5. 원본 검색 -> 0건
rg "원본" src/
```

### 2.3. 회귀 테스트 100% PASS 검증
- 전체 단위/통합 테스트 실행:
  ```bash
  pytest
  ```
- **기대 결과**: 263개 이상의 모든 테스트 항목 100% PASS (Fail 0건).

---

## 3. 검증 및 완료 기준 (Definition of Done)

1. `tests/` 내 모든 변경 사항 반영 및 테스트 정상 통과.
2. `src/` 내 5대 금지 키워드 검색 결과 0건 확인 (로그 증적 확보).
3. `pytest` 263개 테스트 100% 통과 (Pass Rate: 100%).
4. 1개 단위 커밋 생성 및 원격 브랜치 푸시 완료.
