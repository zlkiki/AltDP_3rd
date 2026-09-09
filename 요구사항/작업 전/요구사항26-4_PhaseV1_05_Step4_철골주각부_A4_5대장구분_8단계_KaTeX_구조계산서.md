# 요구사항 26-4: Phase V1-5 Step 4 철골 주각부 A4 5대 장구분 8단계 KaTeX 구조계산서 명세서

## 1. 개요 및 원본 계산서 체계 매핑

본 문서는 **철골 주각부 (`steel_baseplate`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 구조계산서 렌더러)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_baseplate` (카탈로그 No. 24, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/redcr/SteelReportGenerator.js` (기존 철골 계산서 생성기 확장)
  - `src/web/static/js/report/redcr_steel_baseplate.js` (신규 철골 주각부 전용 8단계 KaTeX 렌더러)
  - `src/web/static/js/core/report_renderer.js` (Pane 4 A4 용지 컨테이너 마운트 및 익스포트 파이프라인)
* **2순위 원본 리소스 SSOT**:
  - 리포트 템플릿: `original_src/Midas Design+/DgnReportBase.ini`
  - 리포트 생성 심볼: `CMSOffice`, `CMSExcel`, `CReportSteelBaseplate`
  - MFC 리포트 핸들러: `WriteReport_CUSBPPModeDlg`, `OnReportSummary_CUSBPPModeDlg`, `OnReportDetail_CUSBPPModeDlg`

---

## 2. Pane 4 순백색 A4 구조계산서 레이아웃 규격

[`docs/07 제1절 및 제14절`](../docs/07_web_application_ui_ux_specification.md)의 엄격한 인쇄 품질 사양을 준수합니다:

1. **상시 순백색 용지 (`#ffffff`)**:
   - 다크/라이트 테마와 무관하게 계산서 뷰포트는 언제나 순백색(`#ffffff`) 배경과 고대비 텍스트(`#111827`) 유지.
2. **A4 인쇄 표준 규격**:
   - 가로 `210mm`, 상하좌우 여백 `15mm` (스크린 표시 폭: 약 `794px`).
   - 다중 페이지 인쇄 시 CSS `@page { size: A4 portrait; margin: 15mm; }` 및 `page-break-inside: avoid` 규칙 적용.
3. **상단 컨트롤 툴바**:
   - `[● 상세 보고서]  [○ 요약 보고서]` 라디오 분기.
   - `[☑ 사용자 입력 데이터 상세 포함]` 체크박스 토글.
   - `[🖨️ 인쇄]` `[📄 PDF 저장]` `[📊 Excel 내보내기]` 액션 버튼.

---

## 3. 원본앱 5대 장구분 계산서 구성 체계

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Right Pane 4: KDS 14 31 25 철골 주각부 구조계산서 - 순백색 A4 용지]                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 설계 개요 및 주각부 제원 (Design Overview & Base Plate Geometry)                      │
│    • 프로젝트명, 부재 ID (1F-BP1), 설계기준 (KDS 14 31 25 / KDS 14 20 54)               │
│    • 기둥 단면 (H-400x400x13x21, SM355), 베이스플레이트 (PL-600x600x35, SM355)          │
│    • 페데스탈 콘크리트 (800x800, fck=27 MPa), 앵커볼트 (4-M24, SS400, hef=300 mm)       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. 설계 부재력 및 편심 상태 판정 (Design Forces & Eccentricity Analysis)               │
│    • 설계하중: Pu = 600.0 kN, Mu = 150.0 kN·m, Vu = 80.0 kN                            │
│    • 하중 편심거리 e = Mu / Pu = 250.0 mm vs 임계편심 ecrit = 224.5 mm                 │
│    • 상태 판정: e > ecrit ──► 대편심 (Large Eccentricity / Anchor Tension)  →  O.K     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. 콘크리트 기초 지압강도 검토 (Concrete Bearing Capacity Check)                       │
│    • 지압면적 비 A2/A1 = (800x800)/(600x600) = 1.778 ──► sqrt(A2/A1) = 1.333 ≤ 2.0    │
│    • 설계지압강도: φc·Pp = φc·(0.85·fck·A1·1.333) = 7,160.4 kN                         │
│    • 최대 지압응력: fp = 19.89 MPa ≤ fp,max = 19.89 MPa (DCR = 0.784) ──► O.K         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. 베이스플레이트 휨 두께 검토 (Base Plate Flexural Thickness Check)                   │
│    • 캔틸레버 돌출길이: m = (N - 0.95d)/2 = 110.0 mm, n = (B - 0.8bf)/2 = 140.0 mm    │
│    • 내측 휨 λn' = 1.0·(sqrt(400x400)/4) = 100.0 mm ──► 지배암 l = max = 140.0 mm     │
│    • 소요두께 tp,req = l·sqrt(2·fp / (0.90·Fy)) = 32.2 mm ≤ tp = 35.0 mm ──► O.K       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. 앵커볼트 인장·전단 및 복합응력 검토 (Anchor Bolt Tensile & Shear Capacity)          │
│    • 앵커 소요인장력: Tu = C - Pu = 142.5 kN (개당 Tu,i = 71.3 kN)                     │
│    • 강재인장강도: φNsa = 162.8 kN, 콘크리트 브레이크아웃: φNcb = 148.5 kN ──► DCR = 0.48│
│    • 강재전단강도: φVsa = 188.0 kN, 콘크리트 프라이아웃: φVcp = 207.9 kN ──► DCR = 0.43│
│    • 복합 상호작용: (Tu/φNn)^1.67 + (Vu/φVn)^1.67 = 0.284 + 0.237 = 0.521 ≤ 1.000 ──► O.K│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 8단계 KaTeX 수식 전개식 상세 정의

### Step 1: 콘크리트 지압 증대계수 및 설계지압강도 산정
$$A_1 = B \times N = 600 \times 600 = 360,000\text{ mm}^2$$
$$A_2 = B_2 \times N_2 = 800 \times 800 = 640,000\text{ mm}^2$$
$$\sqrt{\frac{A_2}{A_1}} = \sqrt{\frac{640,000}{360,000}} = 1.333 \le 2.0$$
$$f_{p,\max} = \phi_c \cdot (0.85 f_{ck}) \cdot \sqrt{\frac{A_2}{A_1}} = 0.65 \times (0.85 \times 27.0) \times 1.333 = 19.89\text{ MPa}$$
$$\phi_c P_p = f_{p,\max} \cdot A_1 = 19.89 \times 360,000 \times 10^{-3} = 7,160.4\text{ kN}$$

### Step 2: 하중 편심거리 및 편심 상태 판정
$$e = \frac{M_u}{P_u} = \frac{150.0 \times 10^6\text{ N}\cdot\text{mm}}{600.0 \times 10^3\text{ N}} = 250.0\text{ mm}$$
$$q_{\max} = f_{p,\max} \cdot B = 19.89 \times 600 = 11,934\text{ N/mm}$$
$$e_{crit} = \frac{N}{2} - \frac{P_u}{2 q_{\max}} = \frac{600}{2} - \frac{600,000}{2 \times 11,934} = 300 - 25.1 = 274.9\text{ mm}$$
$$\text{판정: } e = 250.0\text{ mm} \le e_{crit} = 274.9\text{ mm} \implies \text{중편심 (부분 압축, 앵커 인장 미발생)}$$

### Step 3: 콘크리트 최대 지압응력 검토
$$Y_c = 3 \left(\frac{N}{2} - e\right) = 3 \times (300 - 250.0) = 150.0\text{ mm}$$
$$f_p = \frac{2 P_u}{3 B (N/2 - e)} = \frac{2 \times 600,000}{3 \times 600 \times 50.0} = 13.33\text{ MPa}$$
$$\text{DCR}_{bearing} = \frac{f_p}{f_{p,\max}} = \frac{13.33}{19.89} = 0.670 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 4: 캔틸레버 굽힘암 유도 (AISC DG-1 모델)
$$m = \frac{N - 0.95 d}{2} = \frac{600 - 0.95 \times 400}{2} = 110.0\text{ mm}$$
$$n = \frac{B - 0.80 b_f}{2} = \frac{600 - 0.80 \times 400}{2} = 140.0\text{ mm}$$
$$n' = \frac{1}{4}\sqrt{d \cdot b_f} = \frac{1}{4}\sqrt{400 \times 400} = 100.0\text{ mm}$$
$$X = \frac{4 d b_f}{(d + b_f)^2} \frac{P_u}{\phi_c P_p} = \frac{4 \times 400 \times 400}{(400 + 400)^2} \frac{600.0}{7,160.4} = 0.0838$$
$$\lambda = \frac{2\sqrt{X}}{1 + \sqrt{1 - X}} = \frac{2\sqrt{0.0838}}{1 + \sqrt{1 - 0.0838}} = 0.296 \le 1.0$$
$$l = \max(m, n, \lambda n') = \max(110.0, 140.0, 0.296 \times 100.0) = 140.0\text{ mm}$$

### Step 5: 베이스플레이트 소요두께 산정 및 휨 검토
$$t_{req} = l \sqrt{\frac{2 f_p}{\phi_b F_y}} = 140.0 \times \sqrt{\frac{2 \times 13.33}{0.90 \times 355}} = 140.0 \times 0.204 = 28.6\text{ mm}$$
$$\text{DCR}_{plate} = \left(\frac{t_{req}}{t_p}\right)^2 = \left(\frac{28.6}{35.0}\right)^2 = 0.668 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 6: 앵커볼트 인장강도 검토 (대편심 시 인장력 $T_u$ 발생 시)
$$A_{se} = \frac{\pi \cdot 24^2}{4} = 452.4\text{ mm}^2$$
$$\phi N_{sa} = 0.75 \cdot n_{ta} \cdot A_{se} \cdot f_{uta} = 0.75 \times 2 \times 452.4 \times 400 \times 10^{-3} = 271.4\text{ kN}$$
$$N_b = 12.5 \times 1.0 \times \sqrt{27.0} \times 300^{1.5} \times 10^{-3} = 337.5\text{ kN}$$
$$\phi N_{cb} = 0.70 \cdot \frac{A_{Nc}}{A_{Nc0}} \cdot \psi_{ed,N} \cdot N_b = 0.70 \times 1.0 \times 1.0 \times 337.5 = 236.3\text{ kN}$$
$$\phi N_n = \min(\phi N_{sa}, \phi N_{cb}) = 236.3\text{ kN}$$
$$\text{DCR}_{tension} = \frac{T_u}{\phi N_n} \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 7: 앵커볼트 전단강도 및 콘크리트 프라이아웃 검토
$$\phi V_{sa} = 0.65 \cdot (0.60 \cdot n_{total} \cdot A_{se} \cdot f_{uta}) = 0.65 \times (0.60 \times 4 \times 452.4 \times 400) \times 10^{-3} = 282.3\text{ kN}$$
$$\phi V_{cp} = 0.70 \cdot (k_{cp} \cdot N_{cb}) = 0.70 \times (2.0 \times 337.5) = 472.5\text{ kN} \quad (h_{ef} \ge 65\text{ mm})$$
$$\phi V_n = \min(\phi V_{sa}, \phi V_{cp}) = 282.3\text{ kN}$$
$$\text{DCR}_{shear} = \frac{V_u}{\phi V_n} = \frac{80.0}{282.3} = 0.283 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 8: 앵커볼트 인장-전단 상호작용 검토
$$\text{DCR}_{comb} = \left(\frac{T_u}{\phi N_n}\right)^{1.67} + \left(\frac{V_u}{\phi V_n}\right)^{1.67} \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

---

## 5. 상세/요약 분기 및 내보내기 사양

* **요약 보고서**:
  - 1장 요약 테이블: 부재 정보, $P_u, M_u, V_u$, 지압응력/강도($f_p / \phi P_p$), 플레이트 두께($t_{req} / t_p$), 앵커 DCR, 종합 판정 `O.K`.
* **내보내기 파이프라인**:
  - `[🖨️ 인쇄]`: 브라우저 기본 인쇄 대화창 호출 (`window.print()`).
  - `[📄 PDF 저장]`: A4 세로 규격 1:1 완벽 보존 PDF 생성.
  - `[📊 Excel 내보내기]`: 수치 요약 테이블 Excel(`.xlsx`/HTML 포맷) 다운로드.

---

## 6. 완료 정의 (DoD) 및 체크리스트

- [ ] **A4 8단계 KaTeX 계산서 구현**: `src/web/static/js/report/redcr_steel_baseplate.js` 작성.
- [ ] **수식 유도 무결성**: 8단계 KaTeX 수식 전개식 렌더링 정상 확인.
- [ ] **순백색(`#ffffff`) A4 고정**: 테마 전환 시에도 순백색 고정 확인.
- [ ] **상세/요약 토글**: 라디오 버튼 전환에 따른 뷰 변경 정상 확인.
- [ ] **인쇄/PDF/Excel**: 익스포트 파이프라인 정상 작동 확인.
