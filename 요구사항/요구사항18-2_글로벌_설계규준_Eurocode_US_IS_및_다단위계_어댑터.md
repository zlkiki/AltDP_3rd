# 요구사항 18-2: 글로벌 설계규준 (Eurocode, US, IS) 및 다단위계 어댑터 (Phase 18-2)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+ 원본 바이너리 자산인 **`DPLUS_EC.dll` (Eurocode)**, **`GEN_DgnCalc_US.dll` (US ACI/AISC)**, **`DPLUS_IS.dll` (Indian Standard)**을 순수 Python 어댑터 패턴으로 구축합니다.
* 글로벌 프로젝트 지원을 위한 **SI $\leftrightarrow$ MKS $\leftrightarrow$ US Imperial ($\text{kip, in, ft, ksi}$)** 실시간 단위 변환 파이프라인을 완성합니다.

---

## 2. 세부 개발 명세

### 2.1. 초정밀 다단위계 변환기 (`src/engine/international/units.py`)
* **단위계 정의**:
  - `SI` : $\text{mm, N, MPa, kN, kN}\cdot\text{m}$
  - `MKS` : $\text{cm, kgf, tf, kgf/cm}^2\text{, tf}\cdot\text{m}$
  - `US_IMPERIAL` : $\text{in, ft, lb, kip, ksi, ft}\cdot\text{kip}$
* **변환 정밀도**: 양방향 변환 시 부동소수점 오차 $10^{-7}$ 이하 유지.

### 2.2. 글로벌 설계 기준 어댑터 (`src/engine/international/`)
* **1. Eurocode 어댑터 (`eurocode/`)**:
  - 콘크리트: EN 1992-1-1 ($\gamma_c = 1.5, \gamma_s = 1.15, \alpha_{cc} = 0.85$ or $1.0$).
  - 강구조: EN 1993-1-1 ($\gamma_{M0} = 1.0, \gamma_{M1} = 1.0, \gamma_{M2} = 1.25$).
* **2. US Standards 어댑터 (`us_code/`)**:
  - RC: ACI 318-19 (인장지배/압축지배 강도감소계수 $\phi = 0.65 \sim 0.90$, $\beta_1$ 계수 산정).
  - 강구조: AISC 360-16 LRFD ($\phi_b = 0.90, \phi_c = 0.90, \phi_v = 0.90$).
* **3. Indian Standards 어댑터 (`is_code/`)**:
  - IS 456 (콘크리트), IS 800 (철골).

### 2.3. REST API 엔드포인트 (`src/api/routes/international.py`)
* `POST /api/v1/intl/convert-units` : 데이터 모델 단위계 일괄 변환
* `POST /api/v1/intl/design-check` : 지정된 국가 규준(KDS / EC / ACI / IS) 기반 부재 설계 검토

---

## 3. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **단위 변환 정밀도**: SI $\leftrightarrow$ US Imperial 변환 후 역변환 시 오차 $10^{-6}$ 이내.
- [ ] **글로벌 규준 일치성**: ACI 318-19 및 Eurocode 2 공식 예제 답안 대비 강도 오차 0.1% 미만.
- [ ] **단위 테스트 통과**: `tests/engine/test_units.py`, `tests/engine/test_international_codes.py` 통과.
