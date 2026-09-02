# 바이너리 리버스 엔지니어링 명세서 (02_binary_reverse_engineering_specification.md)

## 1. 바이너리 분석 개요

Midas Design+ 원본 바이너리는 Microsoft Visual C++ (MSVC)로 빌드된 64비트 Native PE 바이너리이며, 코드 섹션 암호화나 패커 보호 조치 없이 온전한 PE 구조를 유지하고 있습니다.

모듈 간 동적 링킹을 위해 내보낸(Exported) C++ 심볼 47,110개가 완벽히 보존되어 있어 클래스 명세, 멤버 함수, 설계 검토 파이프라인의 100% 역추적이 가능합니다.

추가로 Ghidra Headless Analyzer 연동 파이프라인([scripts/ghidra_extract.py](file:///d:/PyProject/AltDP_3rd/scripts/ghidra_extract.py))을 통해 핵심 설계 알고리즘 47종의 무손실 C 수도코드를 [decompiled_src/core_routines/](file:///d:/PyProject/AltDP_3rd/decompiled_src/core_routines/)로 자산화 완료하였습니다.

---

## 2. 모듈별 핵심 C++ 클래스 및 함수 맵

### 1) `DPLUS_RCS.dll` (RC 구조설계 엔진)
* **`CRCSCodeCheck`**: KDS 14 20 00 기반 RC 부재 검토 마스터 클래스
  * `CHK_BBBE`: RC 보(Beam) 복철근 휨강도($\phi M_n$), 전단-비틀림 합성, 유효단면2차모멘트($I_e$) 처짐 검토
  * `CHK_BCCO`: RC 기둥(Column) 다축 P-M 상관도 곡선 계산, 중립축 수렴 루프, 이축휨 브레슬러/윤곽선법
  * `CHK_BWUW`: RC 전단벽(Wall) 면내전단강도($V_c, V_s$) 및 특수경계요소(Boundary Element) 판정
  * `CHK_SLAB`: RC 슬래브(Slab) 1방향/2방향 직접설계법(DDM) 및 2방향 펀칭 전단응력 검토
  * `CHK_UFDN`: RC 기초(Footing) 편심 접지압, 2방향 펀칭전단 위험단면($d/2$) 및 휨철근 배근 검토
  * `CHK_URAB`: RC 지하외벽 / 옹벽(Retaining Wall) Rankine/Coulomb 토압, 전도/활동/지지력 안전율 계산
  * `CHK_URBE`: RC 지중보 / 전이보 검토
* **`CRCSDataBase`**: RC 부재 입력 제원, 배근 정보, 하중 케이스 컨테이너
* **`CMSOffice`**: 구조계산서 및 엑셀/워드 출력 엔진

### 2) `DPLUS_STEEL.dll` (철골 구조설계 엔진)
* **`CSTLCodeCheck`**: KDS 14 31 00 기반 강구조 검토 마스터 클래스
  * `CHK_USMC`: 철골 부재(보/기둥/가새) 폭두께비 조밀 판정, 비지지길이($L_b$)별 LTB 휨강도, 전단좌굴, 강축/약축 휨좌굴, 축력-휨 조합 $P_u/\phi P_n \ge 0.2$ 분기 수식
  * `CHK_USBP` / `CBasePlate`: 기둥 주각부 베이스플레이트 콘크리트 지압응력 삼각/사다리꼴 분포, 플레이트 두께($t_p$), 앵커볼트 검토
  * `CHK_USBC` / `CSteelBoltConnection`: 고장력 볼트(F10T, TS볼트) 전단/인장/지압 강도 및 블록전단파단(Block Shear) 한계면 산정
  * `CHK_USEP`: 보-기둥 모멘트 엔드플레이트 접합부 두께 및 볼트 장력 산출
  * `CHK_USWE` / `CSteelWelding`: 맞댐/모살 용접 유효목두께 및 허용응력 검토
  * `CHK_USWO`: 철골 보 웨브 개구부 보강 설계
  * `CHK_USPG`: 플레이트 거더 휨/전단 좌굴 검토
  * `CHK_USWB`: 가새 부재 인장 순단면 파단($U$) 및 거셋플레이트 검토

### 3) `DPLUS_DB.dll` (부재 데이터베이스 및 단면 관리)
* **`CBaseClass`**: 모든 구조 부재 데이터 모델의 추상 베이스 클래스
* **`CSteelSectDB` / `CAluSectDB`**: 단면 형상 정의 및 기하학적 성질($A, I, Z, S, r, J, C_w$) 계산 루틴
* **`CDataCompare`**: 하중 조합별 최대/최소 단면력 추출 및 포락선(Envelope) 계산

### 4) `DPLUS_ALU.dll` & `DPLUS_SRC.dll` (특수/합성 구조 엔진)
* **`CALUCodeCheck`**: 알루미늄 부재 휨·압축·국부좌굴 검토 (`CHK_UAAG`, `CHK_UAMT`)
* **`CSRCCodeCheck`**: CFT 및 매입형 SRC 기둥/합성보 전단연결재 검토 (`CHK_UCCO`, `CHK_UCFT`)

---

## 3. 심볼 역공학 및 C 수도코드 자산 활용 원칙 (Ground Truth Protocol)
1. 신규 파이썬 부재설계 엔진(`src/engine/`) 개발 시, 각 함수는 [decompiled_src/core_routines/](file:///d:/PyProject/AltDP_3rd/decompiled_src/core_routines/)에 수록된 C 수도코드의 분기 조건문과 수식을 직접 대조하여 구현합니다.
2. 입력 변수 명칭 및 단면 제원 필드는 Midas Design+의 표준 명명 규칙을 수렴하여 데이터 호환성을 극대화합니다.
3. 세부 심볼 원문은 [decompiled_src/](file:///d:/PyProject/AltDP_3rd/decompiled_src/) 디렉토리 내의 텍스트 덤프 및 [core_routines/README.md](file:///d:/PyProject/AltDP_3rd/decompiled_src/core_routines/README.md) 총괄 색인표를 참조합니다.
