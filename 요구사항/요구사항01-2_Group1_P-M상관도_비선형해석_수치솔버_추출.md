# 요구사항 01-2: Group 1 - P-M 상관도 및 비선형 수치해석 솔버 추출

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+의 RC 기둥 및 전단벽 설계의 핵심은 축력-휨($P-M$) 상관곡선 산정 및 비선형 중립축 평형 수렴 알고리즘에 있습니다. 이는 단순한 단일 수식이 아닌 파이버 단면 적분 및 이축휨 브레슬러/윤곽선법 수치해석 솔버입니다.

### 1.2. 목적
1. `DPLUS_RCS.dll` 및 `DPLUS_DB.dll`로부터 기둥 축력-모멘트 P-M 상관도 및 비선형 평형 루틴 추출.
2. `decompiled_src/core_routines/solver/`에 C 수도코드 및 심볼 메타데이터 저장.
3. 추출된 C 소스의 비선형 수렴 루프, 변형률 적합조건, 응력블록 적분 알고리즘의 보존 무결성 검증.

---

## 2. 추출 대상 심볼 및 바이너리 매핑

| 바이너리 모듈 | 핵심 클래스 / 심볼 | 디망글드 시그니처 및 엔지니어링 역할 |
|---|---|---|
| `DPLUS_RCS.dll` | `?CHK_BCCO@CRCSCodeCheck@@QEAA_NAEBV?$CArray@II@@@Z` | 기둥(Column) 다축 P-M 상관곡선 계산 및 강도 검토 |
| `DPLUS_RCS.dll` | `?CHK_BCCO@CRCSCodeCheck@@QEAA_NI@Z` | 단일 기둥 부재 P-M 상관곡선 및 DCR 판정 루틴 |
| `DPLUS_RCS.dll` | `?CHK_BCGR@CRCSCodeCheck@@QEAA_N...` | 기둥 그룹 검토 및 최악 하중조건(Worst Envelope) 선별 |
| `DPLUS_DB.dll` / `DPLUS_DGN.dll` | `CDGN_PMCurveDrawWnd` / `mfsolver.exe` | P-M 상관곡선 좌표점 샘플링 및 위험 단면 포락선 추출 |

---

## 3. 세부 작업 항목 (Checklist)

- [x] `scripts/ghidra_extract.py`를 실행하여 Group 1 타겟 함수 추출
  - 대상 DLL: `original_src/Midas Design+/DPLUS_RCS.dll`, `DPLUS_DB.dll`
  - 대상 심볼: `CHK_BCCO`, `CHK_BCGR`, `CDGN_PMCurveDrawWnd`
- [x] 출력 디렉토리 확인 및 C 파일 생성:
  - `decompiled_src/core_routines/solver/` 하위 C 소스 4건 및 `solver_meta.json` 생성 완료
- [x] C 수도코드 분석 및 알고리즘 주석화:
  - 중립축 깊이($c$) 이분법/뉴턴-랩슨 수렴 루프 식별
  - 콘크리트 등가응력블록($\alpha_1, \beta_1$) 및 철근 탄소성 변형률 계산 로직 확인
  - 이축휨 브레슬러($1/P_n = 1/P_{nx} + 1/P_{ny} - 1/P_0$) 분기 수식 확인
- [x] 단위 테스트(`tests/engine/test_extract_group1.py`) 작성 및 `pytest tests/engine/` 통과

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

1. `decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`가 생성되고 비어있지 않아야 함.
2. C 코드 내에서 축력($P$), 모멘트($M_x, M_y$), 중립축 각도($\theta$) 계산 루프가 온전히 보존되어야 함.
3. `pytest tests/engine/test_extract_group1.py` 테스트가 통과할 것.
