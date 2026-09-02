# 요구사항 18: RC 및 철골 성능기반설계 (PBD) 및 글로벌 규준 (Eurocode, US, IS) 확장

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+ 원본 바이너리에 탑재된 **성능기반 내진설계 모듈(`IDS_RIBBON_BARR_PBD`)**과 **유로코드(`DPLUS_EC.dll`)**, **미국 규준(`GEN_DgnCalc_US.dll`)**, **인도 규준(`DPLUS_IS.dll`)**을 웹 아키텍처로 확장 구축합니다.

### 1.2. 개발 목적
1. **성능기반설계 (PBD) 및 소성힌지 평가 엔진 (`src/engine/pbd/`)**:
   - KDS 41 17 00 / ASCE 41-17 기반 RC/철골 부재 $M-\theta, V-\gamma$ 백본 곡선 생성.
   - 거주한계(IO), 인명안전(LS), 붕괴방지(CP) 성능수준 판정.
2. **글로벌 설계 규준 및 다단위계 어댑터 (`src/engine/international/`)**:
   - Eurocode 2 (콘크리트), Eurocode 3 (강구조).
   - US ACI 318-19, AISC 360-16 및 Imperial 단위계 ($\text{kip, in, ksi}$).
   - Indian Standard IS 456, IS 800.

---

## 2. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 18-1** | [`요구사항18-1_PBD_비선형_소성힌지_백본곡선_및_성능수준평가_엔진.md`](file:///d:/PyProject/AltDP_3rd/요구사항/요구사항18-1_PBD_비선형_소성힌지_백본곡선_및_성능수준평가_엔진.md) | `src/engine/pbd/hinge_rc.py`, `hinge_steel.py`, `backbone_curve.py` | ASCE 41-17 / KDS 41 17 00 백본곡선 및 IO/LS/CP 판정 |
| **Phase 18-2** | [`요구사항18-2_글로벌_설계규준_Eurocode_US_IS_및_다단위계_어댑터.md`](file:///d:/PyProject/AltDP_3rd/요구사항/요구사항18-2_글로벌_설계규준_Eurocode_US_IS_및_다단위계_어댑터.md) | `src/engine/international/units.py`, `eurocode/`, `us_code/`, `is_code/` | SI/MKS/Imperial 단위 변환, Eurocode 2/3, ACI 318-19, IS 456 검토 |

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] ASCE 41-17 및 Eurocode/ACI 표준 예제 대비 계산 오차 0.1% 미만.
- [ ] 단위 변환 수치 정밀도 $10^{-6}$ 이내 유지.
- [ ] Pytest 스위트 통과: `tests/engine/test_pbd_hinge.py`, `tests/engine/test_units.py`, `tests/engine/test_international_codes.py`, `tests/api/test_international_routes.py`.
