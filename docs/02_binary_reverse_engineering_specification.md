# 바이너리 리버스 엔지니어링 명세서 (02_binary_reverse_engineering_specification.md)

## 1. 바이너리 분석 개요

Midas Design+ 원본 바이너리는 Microsoft Visual C++ (MSVC)로 빌드된 64비트 Native 바이너리이며, 코드 섹션 암호화나 패커 보호 조치 없이 온전한 PE 구조를 유지하고 있습니다.

특히 모듈 간 동적 링킹을 위해 내보낸(Exported) C++ 심볼 47,110개가 완벽히 보존되어 있어 클래스 명세, 멤버 함수, 설계 검토 파이프라인의 100% 역추적이 가능합니다.

---

## 2. 모듈별 핵심 C++ 클래스 및 함수 맵

### 1) `DPLUS_RCS.dll` (RC 구조설계 엔진)
* **`CRCSCodeCheck`**: KDS/ACI 기반 RC 부재 검토 마스터 클래스
  * `CHK_BBBE`: RC 보(Beam) 휨/전단 단면 검토
  * `CHK_BCCO`: RC 기둥(Column) P-M 상관도 및 축력/휨/전단 검토
  * `CHK_BWUW`: RC 전단벽(Wall) 면내전단 및 휨압축 검토
  * `CHK_SLAB`: RC 1방향/2방향 슬래브(Slab) 검토
  * `CHK_UFDN`: RC 직접/말뚝 기초(Footing) 1방향/2방향 전단 및 휨 검토
  * `CHK_URAB`: RC 지하외벽 / 옹벽(Retaining Wall) 안정성 및 단면 검토
  * `CHK_URBE`: RC 지중보 / 전이보 검토
* **`CRCSDataBase`**: RC 부재 입력 제원, 배근 정보, 하중 케이스 컨테이너
* **`CMSOffice`**: 구조계산서 및 엑셀/워드 출력 엔진

### 2) `DPLUS_STEEL.dll` (철골 구조설계 엔진)
* **`CSTLCodeCheck`**: KDS/AISC 기반 강구조 검토 마스터 클래스
  * `CHK_SBM`: 철골보(Steel Beam) 휨, 전단, 횡비틀림좌굴(LTB) 검토
  * `CHK_SCOL`: 철골기둥(Steel Column) 축압축, 휨좌굴, 비틀림좌굴, P-M 조합응력 검토
  * `CHK_SBRC`: 철골 가새(Brace) 인장/압축 검토
* **`CSteelBoltConnection`**: 고장력 볼트 마찰/지압 접합부 검토
* **`CSteelWeldConnection`**: 맞댐/모살 용접 접합부 검토
* **`CBasePlate`**: 기둥 하부 베이스플레이트 및 앵커볼트 인장/전단 검토

### 3) `DPLUS_DB.dll` (부재 데이터베이스 및 단면 관리)
* **`CBaseClass`**: 모든 구조 부재 데이터 모델의 추상 베이스 클래스
* **`CAluSectDB` / `CSteelSectDB`**: 단면 형상 정의 및 기하학적 성질($A, I, Z, S, r, J, C_w$) 캐싱
* **`CDataCompare`**: 하중 조합별 최대/최소 단면력 추출 및 포락선(Envelope) 계산

---

## 3. 심볼 역공학 활용 원칙
1. 신규 파이썬 부재설계 엔진(`src/engine/`) 개발 시, 각 함수는 원본 `CRCSCodeCheck` 및 `CSTLCodeCheck`의 검토 로직과 계산 순서를 준수합니다.
2. 입력 변수 명칭 및 단면 제원 필드는 Midas Design+의 표준 명명 규칙을 수렴하여 데이터 호환성을 극대화합니다.
3. 세부 심볼 원문은 [`decompiled_src/`](file:///f:/PyProject/re-DP/decompiled_src/) 디렉토리 내의 텍스트 덤프를 참조합니다.
