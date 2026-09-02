# 요구사항 01-5: Group 5 - 단면 DB 연산 추출, 색인 및 무결성 검증

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+의 단면 엔진(`DPLUS_DB.dll`)은 다양한 형강 및 임의 단면의 도심, 주축 단면2차모멘트($I_x, I_y$), 소성단면계수($Z_x, Z_y$), 비틀림상수($J$), 뜀상수($C_w$) 등을 해석적으로 산출합니다.
전체 Group 1~5에서 추출된 C 수도코드 자산을 체계적으로 정리하고 색인화하여 Python 엔진 포팅의 단일 Ground Truth로 확립해야 합니다.

### 1.2. 목적
1. `DPLUS_DB.dll`로부터 단면 기하학적 성질 및 단면 DB 연산 C 루틴 추출.
2. `decompiled_src/core_routines/` 하위 전체 추출 C 소스(Group 1~5)의 무결성 검증.
3. 전체 추출 심볼 20+종의 원본 바이너리, C++ 심볼, 추출 파일명, KDS 설계 기준 조항 매핑 총괄 색인표(`decompiled_src/core_routines/README.md`) 작성.

---

## 2. 추출 대상 심볼 및 바이너리 매핑

| 분류 | 핵심 심볼 (DPLUS_DB.dll) | 엔지니어링 역할 및 수식 |
|---|---|---|
| **강재 단면 DB (Steel Sect)** | `CSteelSectDB` / `CSteelSection` | 임의/표준 형강 단면 성질($A, I_x, I_y, Z_x, Z_y, J, C_w, r_x, r_y$) 산출 |
| **알루미늄 단면 (Alu Sect)** | `CAluSectDB` / `CAluSection` | 알루미늄 압출 형재 유효단면계수 및 비틀림 성질 계산 |
| **단면 해석 솔버 (Sect Calc)** | `CSectionCalc` / `CSectProp` | 임의 다각형 단면의 그린 정리(Green's Theorem) 면적/모멘트 적분 |

---

## 3. 세부 작업 항목 (Checklist)

- [x] `scripts/ghidra_extract.py`로 단면 DB 연산 함수군 추출
  - 대상 DLL: `original_src/Midas Design+/DPLUS_DB.dll`
  - 대상 심볼: `CSteelSectDB`, `CAluSectDB`, `CSectionCalc`
- [x] 출력 파일 생성 및 확인:
  - `decompiled_src/core_routines/db/` 하위 C 소스 12건 및 `db_meta.json` 생성 완료
- [x] 전체 C 수도코드 통합 색인 문서 작성 (`decompiled_src/core_routines/README.md`)
  - 모듈별(solver, rc, steel, db) 디렉토리 맵
  - 원본 심볼 $\leftrightarrow$ C 파일명 $\leftrightarrow$ KDS 조항 일대일 매핑 테이블
- [x] 전체 파이프라인 및 추출 결과 무결성 회귀 테스트 스위트 실행
  - `pytest tests/engine/` 전체 통과 (0.1s 초고속 검증)

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

1. `decompiled_src/core_routines/` 내에 4개 서브디렉토리(`solver/`, `rc/`, `steel/`, `db/`) 및 15개 이상의 C 수도코드 파일이 정상 완비될 것.
2. `decompiled_src/core_routines/README.md` 총괄 색인표가 누락 없이 작성될 것.
3. `pytest tests/engine/` 전체 테스트 100% 통과 (오류 0건).
