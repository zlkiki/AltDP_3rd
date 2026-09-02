# 요구사항 10: SRC 합성부재 및 알루미늄/구조물 보수보강 엔진

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
철골철근콘크리트(SRC) 및 콘크리트 충전강관(CFT) 등 합성구조는 고층 건물과 대경간 구조물에서 초고강도와 연성을 확보하기 위해 널리 사용됩니다. 또한 알루미늄 합금 압출재 구조와 탄소섬유판(CFRP)/강판을 활용한 기존 건축물의 구조성능 보수·보강(Retrofit) 역시 현대 구조설계의 중요한 축입니다. Midas Design+는 `DPLUS_SRC.dll`, `DPLUS_ALU.dll`, `DPLUS_RFM.dll`을 통해 이들 특수 설계를 지원합니다.

### 1.2. 목적
1. 원본 C++ 바이너리(`DPLUS_SRC.dll` 505 심볼, `DPLUS_ALU.dll` 329 심볼, `DPLUS_RFM.dll` 529 심볼)를 분석하여, 순수 Python 합성구조/알루미늄/보강 엔진(`src/engine/src_composite/`, `alu/`, `rfm/`) 구현.
2. 매입형(SRC) 및 충전형(CFT 원형/각형) 합성기둥 소성압축강도($P_{no}$)와 유효휨강성($EI_{eff}$) 산정 및 합성보 전단연결재(Stud Bolt) 설계.
3. KDS 14 31 40 알루미늄 압출형재 휨/압축/열영향부(HAZ) 검토 및 KDS 14 20 90 탄소섬유판/강판 보수보강 내력 증진도 및 계면 부착파괴 검토.

---

## 2. KDS 국가건설기준 및 합성/보강 공학 공식

### 2.1. SRC 및 CFT 합성기둥 설계 (KDS 14 31 30)
* **소성단면 압축강도 ($P_{no}$)**:
  - 매입형 (Encased SRC): $P_{no} = F_y A_s + F_{ysr} A_{sr} + 0.85 f_{ck} A_c$
  - 충전형 (Filled CFT): $P_{no} = F_y A_s + F_{ysr} A_{sr} + C_2 f_{ck} A_c$ ($C_2 = 0.85 \text{ 각형}, \; 0.95 \text{ 원형}$)
* **유효 휨강성 ($EI_{eff}$)**:
  $$EI_{eff} = E_s I_s + E_s I_{sr} + C_1 E_c I_c, \quad C_1 = 0.1 + 2\left(\frac{A_s}{A_s + A_c}\right) \le 0.3$$
* **합성보 전단연결재 강도 ($Q_n$)**:
  $$Q_n = 0.5 A_{sa} \sqrt{f_{ck} E_c} \le R_g R_p A_{sa} F_u$$

### 2.2. 알루미늄 합금 설계 (KDS 14 31 40)
* 알루미늄 합금(6061-T6, 6063-T6 등) 항복강도($F_{ty}, F_{cy}$), 극한강도($F_{tu}$), 열영향부(HAZ) 강도저감계수($k_{haz}$) 적용.

### 2.3. 탄소섬유(CFRP) 및 강판 보수/보강 설계 (KDS 14 20 90)
* **CFRP 유효 인장변형률 ($\epsilon_{fe}$)**:
  $$\epsilon_{fe} = \min\left(0.004, \; \kappa_v \epsilon_{fu}\right), \quad \kappa_v = \frac{k_1 k_2 L_e}{11900 \epsilon_{fu}} \le 0.75$$
* **휨/전단 내력 증진**: $\phi M_n = \phi (M_{n,RC} + \psi_f M_{n,CFRP})$, $\phi V_n = \phi (V_{c} + V_{s} + \psi_f V_{f})$

---

## 3. C++ 바이너리 심볼 Ground Truth 매핑

| 기능 도메인 | 대상 C++ DLL 및 심볼군 | 주요 클래스 |
|---|---|---|
| **SRC/CFT 합성설계** | `DPLUS_SRC.dll` (505 Symbols) | `CSRCCodeCheck`, `CSRCSectProp`, `CSRCColumn` |
| **알루미늄 구조설계** | `DPLUS_ALU.dll` (329 Symbols) | `CALUCodeCheck`, `CALUSectProp` |
| **보수보강(Retrofit)** | `DPLUS_RFM.dll` (529 Symbols) | `CRFMCodeCheck`, `CCFRPDesign`, `CSteelPlateDesign` |

---

## 4. Python 신규 구현 아키텍처

```text
src/engine/
├── src_composite/
│   ├── __init__.py
│   ├── composite_column.py    # CFT/SRC 기둥 소성강도 및 P-M 상관도
│   └── composite_beam.py      # 합성보 소성모멘트 및 스터드 전단연결재
├── alu/
│   ├── __init__.py
│   └── alu_design.py          # 알루미늄 합금 부재 휨/압축/HAZ 검토
└── rfm/
    ├── __init__.py
    └── retrofit_design.py     # CFRP 및 강판 보강 휨/전단 증진도 해석기
```

---

## 5. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 10-1** | `요구사항10-1_SRC_CFT_합성기둥_및_합성보_설계엔진.md` | `src/engine/src_composite/`, `test_composite.py` | CFT/SRC $P_{no}, EI_{eff}$ 및 전단연결재 |
| **Phase 10-2** | `요구사항10-2_알루미늄_구조설계_엔진.md` | `src/engine/alu/alu_design.py`, `test_alu.py` | 알루미늄 HAZ 및 휨/압축 강도 |
| **Phase 10-3** | `요구사항10-3_CFRP_강판_보수보강_설계엔진.md` | `src/engine/rfm/retrofit_design.py`, `test_rfm.py` | CFRP 유효변형률 및 내력 증진비 |

---

## 6. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **합성부재 소성내력 일치성**: KDS 14 31 30 기준 CFT 원형/각형 소성압축강도 $P_{no}$ 오차 0.1% 미만.
- [ ] **CFRP 보강 내력 검증**: KDS 14 20 90 계면 부착파괴 한계변형률 $\epsilon_{fe}$ 및 전단보강 기여분 $V_f$ 수치 일치.
- [ ] **Pytest 스위트 통과**: `pytest tests/engine/test_composite.py test_alu.py test_rfm.py` (100% 통과).
