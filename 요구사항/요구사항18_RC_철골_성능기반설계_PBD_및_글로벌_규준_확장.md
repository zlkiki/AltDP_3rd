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

## 2. 세부 기능 개발 명세

### 2.1. PBD 소성힌지 엔진 (`src/engine/pbd/`)
* RC 보/기둥/전단벽 및 철골 부재 소성회전각 한계값($a, b, c$) 산정 및 백본 곡선 생성.

### 2.2. 국제 규준 어댑터 (`src/engine/international/`)
* `units.py` : SI $\leftrightarrow$ MKS $\leftrightarrow$ US Imperial 실시간 양방향 변환.
* `eurocode/`, `us/`, `is/` 설계 분기 파이프라인.

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] ASCE 41-17 및 Eurocode/ACI 표준 예제 대비 계산 오차 0.1% 미만.
- [ ] 단위 변환 수치 정밀도 $10^{-6}$ 이내 유지.
- [ ] `tests/engine/test_pbd.py`, `test_international_codes.py` 통과.
