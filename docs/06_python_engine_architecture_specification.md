# Python 독립 엔진 아키텍처 명세서 (06_python_engine_architecture_specification.md)

## 1. 엔진 설계 원칙

1. **외부 레거시 DLL 완전 독립**: Wibu Dongle이나 Windows C++ MFC 라이브러리에 일체 의존하지 않고, 순수 Python 3.10+ 및 표준 수치해석 라이브러리(`numpy`, `scipy`, `shapely`)로 동작합니다.
2. **타입 안전성 (Type Safety)**: 모든 데이터 모델과 설계 파라미터는 `pydantic v2` 및 `dataclasses`를 기반으로 엄격한 유효성 검증을 거칩니다.
3. **고속 수치해석**: P-M 상관도 계산 시 벡터화된 넘파이 연산 및 파이버 메시 분할 알고리즘을 사용하여 단일 부재 검토를 5ms 이내에 완료합니다.
4. **수퍼 파일(Superfile) 지양 및 엄격한 모듈화 (Strict Modularity)**: 단일 파일 300~500라인 한계를 엄수하고 단일 책임 원칙(SRP)에 따라 공학 수식, 데이터 모델, 검토 오케스트레이션을 분리합니다.

---

## 2. 패키지 및 모듈 계층 구조

```text
src/engine/
├── __init__.py
├── db/                             # 단면 및 재료 데이터베이스
│   ├── materials.py                # 콘크리트, 철근, 강재 물성 모델
│   ├── sdb_parser.py               # .sdb 바이너리 파서
│   └── section_db.py               # 형강 라이브러리 쿼리 인터페이스
├── rc/                             # KDS 14 20 00 RC 설계 엔진
│   ├── beam.py                     # 보 휨/전단/처짐 검토
│   ├── column.py                   # 기둥 P-M 상관도 및 세장비 검토
│   ├── footing.py                  # 독립/복합 기초 1방향/2방향 전단
│   ├── retaining_wall.py           # 옹벽/지하외벽 토압 및 안정성
│   ├── slab.py                     # 슬래브 1방향/2방향 검토
│   └── wall.py                     # 전단벽 면내전단 및 경계요소
├── steel/                          # KDS 14 31 00 철골 설계 엔진
│   ├── baseplate.py                # 베이스플레이트 및 앵커볼트
│   ├── beam.py                     # 철골보 휨/전단/LTB
│   ├── brace.py                    # 가새 인장/압축
│   ├── column.py                   # 철골기둥 휨좌굴/비틀림좌굴/P-M
│   ├── connection.py               # 볼트/용접 접합부
│   ├── endplate.py                 # 엔드플레이트 모멘트 접합부
│   └── web_opening.py              # 철골보 웨브 개구부 보강 검토
├── src_composite/                  # SRC 합성부재
│   ├── composite_beam.py           # 합성보 휨/전단연결재(Stud)
│   └── composite_column.py         # 매입형/충전형 합성기둥
├── alu/                            # 알루미늄 합금 설계
│   └── beam_column.py              # 알루미늄 보/기둥/멀리온
├── rfm/                            # 보수보강 설계
│   └── retrofit.py                 # CFRP / 강판 휨·전단 보강
├── fem/                            # 2D FEM 평판 휨 및 지반/접촉 솔버
│   ├── element_dkmq.py             # DKMQ 평판 휨 요소 강성행렬
│   ├── solver_plate.py             # 평판 휨 선형 FEM 솔버
│   ├── foundation_fem.py           # 매트기초 Winkler 지반 스프링 솔버
│   ├── baseplate_fem.py            # 주각부 비선형 접촉 솔버
│   └── slab_fem.py                 # 슬래브 Wood-Armer 설계 솔버
├── pbd/                            # 성능기반 내진설계 비선형 소성힌지 백본곡선 엔진
│   ├── hinge_rc.py                 # RC 부재 모멘트-회전각 비선형 백본곡선
│   └── hinge_steel.py              # 철골 부재 소성힌지 및 거동모드 판정
├── international/                  # 글로벌 설계규준 및 초정밀 다단위계
│   ├── units.py                    # SI/MKS/Imperial 양방향 단위변환기
│   ├── eurocode/                   # Eurocode 2 / 3 어댑터
│   ├── us_code/                    # ACI 318 / AISC 360 어댑터
│   └── is_code/                    # IS 456 / IS 800 어댑터
├── interop/                        # MIDAS Gen 3D 해석모델 연동
│   ├── mgt_parser.py               # *.mgt 텍스트 스크립트 파서
│   └── governing_lcb.py            # 해석 부재력 파싱 및 지배 LCB 자동선별
├── project/                        # KDS 표준 물량산출 엔진
│   └── quantity_engine.py          # 콘크리트/철근/형강 물량 집계
└── solver/                         # 수치해석 공통 솔버
    ├── fiber_section.py            # 파이버 단면 분할 모델
    ├── pm_diagram.py               # P-M / P-M-M 3D 포락면 해석기
    └── section_properties.py       # 임의 다각형 단면 성질 적분기
```

---

## 3. 수퍼 파일 방지 및 모듈 분할 가이드라인

1. **단일 파일 크기 상한선 (Size Limits)**:
   - 권장: 파일 당 **300라인 이하**
   - 최대: 파일 당 **500라인 절대 초과 금지**
2. **패키지 분할 트리거 (Sub-Package Promotion)**:
   - 특정 부재(예: RC 보, 기둥)의 코드가 500라인을 초과할 경우, 단일 파일(`beam.py`) 대신 하위 패키지 디렉토리(`rc/beam/`)로 승격하여 분할:
     * `rc/beam/models.py`: 입력/출력 데이터 모델
     * `rc/beam/flexure.py`: 휨 강도 계산
     * `rc/beam/shear.py`: 전단 및 비틀림 계산
     * `rc/beam/serviceability.py`: 즉시/장기 처짐 및 균열폭 산정
     * `rc/beam/auto_design.py`: 최적 배근 자동 산출기
3. **재사용 공통 유틸리티 격리**:
   - 단위 환산, 수식 포맷터, KaTeX 문자열 헬퍼 등은 `src/engine/common/` 또는 `src/utils/`로 격리하여 중복을 원천 차단.
