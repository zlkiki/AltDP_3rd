# 요구사항 01-3: Group 2 - RC 5대 부재 핵심 설계식 추출

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+의 RC 부재설계 엔진(`DPLUS_RCS.dll`)에는 KDS 14 20 00 기반 보, 전단벽, 슬래브, 기초, 옹벽의 휨·전단·비틀림·사용성 및 엣지케이스 판정 공식이 집약되어 있습니다.

### 1.2. 목적
1. `DPLUS_RCS.dll`로부터 RC 5대 부재(보, 전단벽, 슬래브, 기초, 옹벽)의 핵심 설계 검토 함수를 무손실 디컴파일 추출.
2. `decompiled_src/core_routines/rc/` 디렉토리에 정형화된 C 수도코드와 심볼 메타데이터 파일로 저장.
3. KDS 14 20 00 설계 기준식과의 일대일 대응 관계 및 엣지케이스 조건문 분석.

---

## 2. 추출 대상 심볼 및 바이너리 매핑

| 부재 분류 | 핵심 심볼 (DPLUS_RCS.dll) | 엔지니어링 역할 및 KDS 설계식 |
|---|---|---|
| **보 (Beam)** | `?CHK_BBBE@CRCSCodeCheck@@...` | 복철근 휨강도($\phi M_n$), 전단-비틀림 합성응력, 유효단면2차모멘트($I_e$) 처짐 |
| **전단벽 (Wall)** | `?CHK_BWUW@CRCSCodeCheck@@...` | 면내 전단강도($V_c, V_s$), 특수경계요소(Boundary Element) 판정 분기 |
| **슬래브 (Slab)** | `?CHK_SLAB@CRCSCodeCheck@@...` | 1방향/2방향 슬래브 DDM/EFM 모멘트, 2방향 펀칭 전단응력 계산 |
| **기초 (Footing)** | `?CHK_UFDN@CRCSCodeCheck@@...` | 독립/복합 기초 편심 접지압, 2방향 펀칭전단 위험단면($d/2$) 산정 |
| **옹벽/외벽 (Retaining)** | `?CHK_URAB@CRCSCodeCheck@@...` | 지하외벽 및 옹벽 토압 합력점, 전도/활동/지지력 안전율 계산 |
| **지중보 (Underground Beam)** | `?CHK_URBE@CRCSCodeCheck@@...` | 지중보(Underground Beam) 휨/전단 및 지반 반력 검토 |

---

## 3. 세부 작업 항목 (Checklist)

- [x] `scripts/ghidra_extract.py`로 RC 5대 부재 함수군 일괄 추출
  - 대상 DLL: `original_src/Midas Design+/DPLUS_RCS.dll`
  - 대상 심볼: `CHK_BBBE`, `CHK_BWUW`, `CHK_SLAB`, `CHK_UFDN`, `CHK_URAB`, `CHK_URBE`
- [x] 출력 파일 생성 및 확인:
  - `decompiled_src/core_routines/rc/` 하위 C 소스 14건 및 `rc_meta.json` 생성 완료
- [x] C 수도코드 분석 및 KDS 14 20 00 조항 매핑 검증
- [x] 단위 테스트(`tests/engine/test_extract_group2.py`) 작성 및 `pytest tests/engine/` 통과

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

1. RC 5대 부재 C 소스 6개 파일이 모두 온전하게 생성될 것.
2. 각 파일에 강도감소계수($\phi$), 콘크리트 전단강도($V_c$), 철근 배근 간격 산정 로직이 포함되어 있을 것.
3. `pytest tests/engine/test_extract_group2.py` 테스트 100% 통과.
