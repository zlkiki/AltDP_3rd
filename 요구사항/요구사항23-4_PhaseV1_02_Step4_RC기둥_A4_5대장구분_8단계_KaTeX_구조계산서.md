# 요구사항 23-4: Phase V1-2 Step 4 RC 기둥 A4 5대 장구분 8단계 KaTeX 구조계산서 명세서

## 1. 개요 및 계산서 SSOT 매핑

본 문서는 **RC 기둥 (`rc_column`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 공학 구조계산서)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `rc_column` (카탈로그 No. 2, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/redcr_rc_column.js` (신규 기둥 계산서 렌더러 모듈)
  - `src/web/static/js/report_view.js` (계산서 디스패처 등록)
  - `src/report/generator.py` (A4 인쇄용 HTML/PDF 템플릿 엔진)
* **1순위/2순위 계산서 SSOT**:
  - `original_src/Midas Design+/Dbase/DgnReportBase.ini`
  - 원본 계산서 5대 대단원 장구분 및 Step-by-Step 수식 전개 방식 완벽 계승

---

## 2. A4 구조계산서 레이아웃 및 5대 장구분 구성

모든 계산서는 인쇄 시 표준 A4 용지 규격(순백색 `#ffffff` 배경, 20mm 표준 여백)에 최적화되며 아래 5개 대단원으로 구성됩니다:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [RC COLUMN STRUCTURAL CALCULATION REPORT - KDS 14 20 00]                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 설계 기본 정보 및 단면 제원 (Design Information & Section Geometry)                  │
│ 2. 설계 부재력 및 세장비 검토 (Factored Loads & Slenderness Effect)                     │
│ 3. 축력-휨 P-M 상관강도 검토 (Axial & Flexural P-M Interaction Check)                   │
│ 4. 이축휨 상호작용 검토 (Biaxial Bending Interaction Check)                             │
│ 5. 기둥 전단강도 검토 (Shear Strength Check with Axial Force)                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 8단계 KaTeX 수식 전개식 상세 명세

### 3.1. 제1장: 설계 기본 정보 및 단면 제원 (Design Information)
* **프로젝트 및 부재명 메타데이터 헤더**:
  - 프로젝트명, 부재 번호(`COL-01`), 검토 일시, 설계 기준(`KDS 14 20 00 : 2022`).
* **재료 물성치 및 기하 파라미터 테이블**:
  - $f_{ck} = 27.0\text{ MPa}$, $f_y = 400.0\text{ MPa}$, $f_{ys} = 400.0\text{ MPa}$, $E_c = 8,500 \sqrt[3]{f_{cu}} = 26,066\text{ MPa}$, $E_s = 200,000\text{ MPa}$.
  - 단면 치수: $B = 500\text{ mm}, H = 500\text{ mm}, A_g = 250,000\text{ mm}^2$.
  - 주철근 배근: $12\text{-D25}, A_{st} = 6,080.4\text{ mm}^2$.
  - 띠철근 배근: $\text{D10 @300}, A_v = 142.6\text{ mm}^2$.
* **주철근비 한계 검토 (KaTeX 수식)**:
  $$\rho_g = \frac{A_{st}}{A_g} = \frac{6,080.4}{250,000} = 0.0243 \quad (2.43\%)$$
  $$0.010 \le \rho_g \le 0.080 \quad \longrightarrow \quad \mathbf{O.K}$$

### 3.2. 제2장: 설계 부재력 및 세장비 검토 (Slenderness Effect)
* **설계 계수하중**:
  - $P_u = 1,500.0\text{ kN}, M_{ux,top} = 120.0\text{ kN}\cdot\text{m}, M_{ux,bot} = -80.0\text{ kN}\cdot\text{m}, V_{ux} = 90.0\text{ kN}$.
* **세장비 산정 및 장주 판정 (KaTeX 수식)**:
  $$r_x = 0.30 \times H = 0.30 \times 500 = 150.0\text{ mm}$$
  $$\frac{k_x L_u}{r_x} = \frac{1.0 \times 3,500}{150.0} = 23.33$$
  $$\left(\frac{k_x L_u}{r_x}\right)_{limit} = 34 - 12 \left(\frac{M_1}{M_2}\right) = 34 - 12 \left(\frac{-80.0}{120.0}\right) = 42.00$$
  $$\frac{k_x L_u}{r_x} = 23.33 \le 42.00 \quad \longrightarrow \quad \text{단주 (Short Column, 모멘트 확대 불필요, } \delta_{ns} = 1.000\text{)}$$
  *(장주일 경우 Euler 좌굴하중 $P_c$ 및 모멘트확대계수 $\delta_{ns}$ 전개식을 완벽히 출력)*
* **최소 편심 모멘트 검토**:
  $$M_{2,min} = P_u (15 + 0.03 H) \times 10^{-3} = 1,500.0 \times (15 + 15) \times 10^{-3} = 45.00\text{ kN}\cdot\text{m}$$
  $$M_{cx} = \max(M_{ux}, M_{2,min}) = \max(120.0, 45.0) = 120.00\text{ kN}\cdot\text{m}$$

### 3.3. 제3장: 축력-휨 P-M 상관강도 검토 (P-M Interaction Check)
* **8단계 Step-by-Step 수식 전개**:
  1. 순수 압축강도 $P_0$ 산정:
     $$P_0 = 0.85 f_{ck} (A_g - A_{st}) + f_y A_{st} = 0.85 \times 27 \times (250,000 - 6,080.4) + 400 \times 6,080.4 = 8,031.1\text{ kN}$$
  2. 최대 설계축강도 $\phi P_{n,max}$ 산정 (띠철근 $\phi = 0.65$):
     $$\phi P_{n,max} = 0.80 \times 0.65 \times P_0 = 0.52 \times 8,031.1 = 4,176.2\text{ kN}$$
     $$P_u = 1,500.0\text{ kN} \le \phi P_{n,max} = 4,176.2\text{ kN} \quad \longrightarrow \quad \mathbf{O.K}$$
  3. 설계하중 편심거리:
     $$e_x = \frac{M_{cx}}{P_u} = \frac{120.00 \times 10^3}{1,500.0} = 80.0\text{ mm}$$
  4. 200 파이버 수치해석에 의한 중립축 $c$ 및 변형률 분포 수렴:
     $$c = 284.5\text{ mm}, \quad \epsilon_t = 0.0033 \left(\frac{d - c}{c}\right) = 0.0033 \left(\frac{440 - 284.5}{284.5}\right) = 0.00180$$
  5. 강도감소계수 $\phi$ 결정:
     $$\epsilon_t \le \epsilon_y = 0.0020 \implies \phi = 0.650 \quad (\text{압축지배단면})$$
  6. 공칭강도 $P_n, M_n$ 및 설계강도 $\phi P_n, \phi M_n$ 도출:
     $$P_n = 2,950.8\text{ kN}, \quad M_n = 236.1\text{ kN}\cdot\text{m}$$
     $$\phi P_n = 0.65 \times 2,950.8 = 1,918.0\text{ kN}, \quad \phi M_n = 0.65 \times 236.1 = 153.47\text{ kN}\cdot\text{m}$$
  7. 강도비 (DCR) 산정:
     $$\text{DCR}_{PM,x} = \frac{P_u}{\phi P_n} = \frac{M_{cx}}{\phi M_n} = \frac{1,500.0}{1,918.0} = 0.782$$
  8. 최종 판정:
     $$\text{DCR}_{PM,x} = 0.782 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### 3.4. 제4장: 이축휨 상호작용 검토 (Biaxial Bending Check)
* **Bresler 상호작용 역수식 전개**:
  $$\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}$$
  $$\frac{1}{P_n} = \frac{1}{2,950.8} + \frac{1}{3,210.4} - \frac{1}{8,031.1} = 0.0003389 + 0.0003115 - 0.0001245 = 0.0005259\text{ kN}^{-1}$$
  $$P_n = 1,901.5\text{ kN}, \quad \phi P_n = 0.65 \times 1,901.5 = 1,236.0\text{ kN} \quad (\text{또는 파이버 직접 3D 곡면 판정})$$
  $$\text{Bresler Ratio} = \frac{P_u}{\phi P_n} = 0.865 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### 3.5. 제5장: 기둥 전단강도 검토 (Shear Strength Check)
* **축압축력을 고려한 콘크리트 전단강도 $V_c$ 산정**:
  $$V_c = \frac{1}{6} \left(1 + \frac{P_u}{14 A_g}\right) \lambda \sqrt{f_{ck}} b_w d$$
  $$V_c = \frac{1}{6} \left(1 + \frac{1,500 \times 10^3}{14 \times 250,000}\right) \times 1.0 \times \sqrt{27} \times 500 \times 440 \times 10^{-3} = 269.4\text{ kN}$$
* **전단철근(띠철근) 부담 전단강도 $V_s$ 산정**:
  $$V_s = \frac{A_v f_{ys} d}{s} = \frac{142.6 \times 400 \times 440}{300} \times 10^{-3} = 83.7\text{ kN}$$
* **설계 전단강도 $\phi V_n$ 및 DCR 판정**:
  $$\phi V_n = 0.75 \times (V_c + V_s) = 0.75 \times (269.4 + 83.7) = 264.8\text{ kN}$$
  $$\text{DCR}_V = \frac{V_u}{\phi V_n} = \frac{90.0}{264.8} = 0.340 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

---

## 4. 계산서 시각화 및 내보내기 규약

1. **단면 배근도 및 P-M 곡선 이미지 삽입**:
   - 계산서 상단에 기둥 배근 상세도 캔버스 스냅샷을 고해상도 벡터/PNG로 임베딩.
   - P-M 검토 장에 현재 하중점이 표시된 KDS P-M 상관곡선 차트 이미지 삽입.
2. **A4 인쇄 프리뷰 및 페이지 나눔 제어**:
   - CSS `@media print` 규칙을 통해 각 장(Chapter)별 페이지 브레이크(`page-break-inside: avoid`) 엄수.
3. **요약/상세 모드 스위칭**:
   - Summary 모드: 1페이지 요약 테이블 (모든 DCR 및 최종 판정).
   - Detail 모드: 전수 8단계 KaTeX 수식 전개식 3~4페이지 상세 계산서.

---

## 5. 완료 정의 (DoD: Definition of Done)

- [ ] `src/web/static/js/report/redcr_rc_column.js` 모듈 구현 완료
- [ ] 5대 장구분 및 8단계 KaTeX 수식 전개식이 오류 없이 완벽히 렌더링됨
- [ ] 단면 배근도 및 P-M 다이어그램 그림이 계산서 본문에 정상 임베딩됨
- [ ] A4 인쇄 프리뷰 시 페이지 잘림이나 깨짐 없이 순백색(#ffffff)으로 깔끔하게 출력됨
- [ ] 브라우저 콘솔 에러 0건 유지
