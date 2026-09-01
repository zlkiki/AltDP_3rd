# Python 독립 엔진 아키텍처 명세서 (06_python_engine_architecture_specification.md)

## 1. 엔진 설계 원칙

1. **외부 레거시 DLL 완전 독립**: Wibu Dongle이나 Windows C++ MFC 라이브러리에 일체 의존하지 않고, 순수 Python 3.10+ 및 표준 수치해석 라이브러리(`numpy`, `scipy`, `shapely`)로 동작합니다.
2. **타입 안전성 (Type Safety)**: 모든 데이터 모델과 설계 파라미터는 `pydantic v2` 및 `dataclasses`를 기반으로 엄격한 유효성 검증을 거칩니다.
3. **고속 수치해석**: P-M 상관도 계산 시 벡터화된 넘파이 연산 및 파이버 메시 분할 알고리즘을 사용하여 단일 부재 검토를 5ms 이내에 완료합니다.

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
│   └── connection.py               # 볼트/용접 접합부
├── src_composite/                  # SRC 합성부재
│   ├── composite_beam.py           # 합성보 휨/전단연결재(Stud)
│   └── composite_column.py         # 매입형/충전형 합성기둥
└── solver/                         # 수치해석 공통 솔버
    ├── fiber_section.py            # 파이버 단면 분할 모델
    ├── pm_diagram.py               # P-M / P-M-M 3D 포락면 해석기
    └── section_properties.py       # 임의 다각형 단면 성질 적분기
```
