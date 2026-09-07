# 요구사항 25-4: Phase V1-4 Step 4 철골 보/기둥 A4 5대 장구분 8단계 KaTeX 구조계산서 명세서

## 1. 개요 및 원본 계산서 체계 매핑

본 문서는 **철골 보/기둥 (`steel_beam_column`)**의 **Step 4 (A4 5대 장구분 8단계 KaTeX 구조계산서 렌더러)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `steel_beam_column` (카탈로그 No. 22, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/redcr/SteelReportGenerator.js` (기존 철골 계산서 생성 엔진 확장)
  - `src/web/static/js/report/redcr_steel_beam_column.js` (신규 철골 보/기둥 전용 8단계 KaTeX 렌더러)
  - `src/web/static/js/core/report_renderer.js` (Pane 4 A4 용지 컨테이너 마운트 및 익스포트 파이프라인)
* **2순위 원본 리소스 SSOT**:
  - 리포트 베이스 템플릿: `original_src/Midas Design+/DgnReportBase.ini`
  - 리포트 생성 심볼: `CMSOffice`, `CMSExcel`, `CReportSteelBeamColumn`

---

## 2. Pane 4 순백색 A4 구조계산서 레이아웃 규격

[`docs/07 제1절 및 제14절`](file:///f:/PyProject/AltDP_3rd/docs/07_web_application_ui_ux_specification.md)의 엄격한 인쇄 품질 사양을 준수합니다:

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
│ [Right Pane 4: KDS 14 31 10 철골 보/기둥 구조계산서 - 순백색 A4 용지]                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 설계 개요 및 형강 단면 제원 (Design Overview & Section Properties)                    │
│    • 프로젝트명, 부재 ID (1F-SC1), 설계기준 (KDS 14 31 10 : 2019 한계상태설계법)       │
│    • 강종 (SM355, Fy=355 MPa, Fu=490 MPa), 단면 규격 (H-400x200x8x13)                   │
│    • 단면 기하특성치 요약 테이블 (A, Ix, Iy, Zx, Zy, Sx, Sy, rx, ry, J, Cw)             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. 단면 조밀성 판정 (Section Compactness / Width-to-Thickness Ratio)                   │
│    • 플랜지 판폭두께비 λf = B / 2tf 산정 및 한계값 (λp, λr) 대조 ──► COMPACT  →  O.K   │
│    • 웨브 판폭두께비 λw = h / tw 산정 및 한계값 (λp, λr) 대조 ────► COMPACT  →  O.K   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. 휨강도 및 횡비틀림좌굴 검토 (Flexural Strength & LTB Check)                         │
│    • 소성모멘트 Mp = Fy·Zx 및 횡지지 한계길이 Lp, Lr 산정                              │
│    • Lb vs Lp, Lr 비교 판정 및 모멘트구배계수 Cb 적용 휨좌굴강도 Mn 산정               │
│    • 강축 휨검토: Mux / φb·Mnx = 180.0 / 369.8 = 0.487 ≤ 1.000 ────────► O.K          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. 압축/인장강도 검토 (Axial Strength & Column Buckling Check)                         │
│    • 유효세장비 KL/r = max(Kx·Lx/rx, Ky·Ly/ry) = 64.0 ≤ 200 ──────────► O.K          │
│    • Euler 탄성좌굴응력 Fe 산정 및 비탄성 임계좌굴응력 Fcr 산출                         │
│    • 설계압축강도: φc·Pn = 0.90·Fcr·Ag = 1,840 kN                                      │
│    • 축압축 검토: Pu / φc·Pn = 1,200.0 / 1,840.0 = 0.652 ≤ 1.000 ──────► O.K          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. 조합력 상호작용 검토 (Combined Axial Compression & Biaxial Flexure Check)          │
│    • 축력비 Pu / φc·Pn = 0.652 ≥ 0.20 ──► KDS 14 31 10 식 4.5-1 적용                   │
│    • DCR = Pu / (φc·Pn) + (8/9)·[ B1·Mux / (φb·Mnx) + B1·Muy / (φb·Mny) ]               │
│    • DCR = 0.652 + (8/9)·[ 0.487 + 0.125 ] = 0.812 ≤ 1.000 ───────────► O.K          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 8단계 KaTeX 수식 전개식 상세 명세

구조계산서의 핵심 수식은 축약 없이 완전한 LaTeX 유도 과정을 표출합니다:

### Step 1: 강재 재료 강도 및 탄성계수
$$\text{강종: } \text{SM355}, \quad F_y = 355\,\text{MPa}, \quad F_u = 490\,\text{MPa}, \quad E = 205,000\,\text{MPa}$$

### Step 2: 플랜지 판폭두께비 검토
$$\lambda_f = \frac{B}{2 t_f} = \frac{200}{2 \times 13} = 7.69$$
$$\lambda_{pf} = 0.38 \sqrt{\frac{E}{F_y}} = 0.38 \sqrt{\frac{205,000}{355}} = 9.13$$
$$\lambda_f = 7.69 \le \lambda_{pf} = 9.13 \implies \mathbf{COMPACT\ (조밀)} \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 3: 웨브 판폭두께비 검토
$$\lambda_w = \frac{h}{t_w} = \frac{400 - 2(13 + 16)}{8} = 42.75$$
$$\lambda_{pw} = 3.76 \sqrt{\frac{E}{F_y}} = 3.76 \sqrt{\frac{205,000}{355}} = 90.34$$
$$\lambda_w = 42.75 \le \lambda_{pw} = 90.34 \implies \mathbf{COMPACT\ (조밀)} \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 4: 소성모멘트 및 한계 횡비지지길이 산정
$$M_{px} = F_y Z_x = 355 \times 1,286 \times 10^3 \times 10^{-6} = 456.53\,\text{kN}\cdot\text{m}$$
$$L_p = 1.76 r_y \sqrt{\frac{E}{F_y}} = 1.76 \times 46.9 \times \sqrt{\frac{205,000}{355}} = 1,982.8\,\text{mm}$$
$$L_r = 1.95 r_{ts} \frac{E}{0.7 F_y} \sqrt{\frac{J c}{S_x h_0} + \sqrt{\left(\frac{J c}{S_x h_0}\right)^2 + 6.76\left(\frac{0.7 F_y}{E}\right)^2}} = 5,640.2\,\text{mm}$$

### Step 5: 횡비틀림좌굴(LTB) 강축 공칭 및 설계 휨강도 산출 ($L_p < L_b \le L_r$)
$$M_{nx} = C_b \left[ M_{px} - (M_{px} - 0.7 F_y S_x) \left(\frac{L_b - L_p}{L_r - L_p}\right) \right] \le M_{px}$$
$$M_{nx} = 1.00 \left[ 456.53 - (456.53 - 0.7 \times 355 \times 1,190 \times 10^{-3}) \left(\frac{3,000 - 1,982.8}{5,640.2 - 1,982.8}\right) \right] = 410.89\,\text{kN}\cdot\text{m}$$
$$\phi_b M_{nx} = 0.90 \times 410.89 = 369.80\,\text{kN}\cdot\text{m}$$
$$\frac{M_{ux}}{\phi_b M_{nx}} = \frac{180.0}{369.80} = 0.487 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 6: 압축재 유효세장비 및 Euler 탄성좌굴응력
$$\frac{KL}{r} = \max\left(\frac{1.0 \times 6,000}{168.0}, \frac{1.0 \times 3,000}{46.9}\right) = \max(35.71, 63.97) = 63.97 \le 200 \quad \longrightarrow \quad \mathbf{O.K}$$
$$F_e = \frac{\pi^2 E}{(KL/r)^2} = \frac{\pi^2 \times 205,000}{(63.97)^2} = 494.59\,\text{MPa}$$

### Step 7: 비탄성 임계좌굴응력 및 설계 압축강도
$$\frac{KL}{r} = 63.97 \le 4.71 \sqrt{\frac{E}{F_y}} = 113.15 \quad \left(\frac{F_y}{F_e} = 0.718 \le 2.25\right)$$
$$F_{cr} = \left[ 0.658^{\frac{F_y}{F_e}} \right] F_y = \left[ 0.658^{0.718} \right] \times 355.0 = 262.91\,\text{MPa}$$
$$\phi_c P_n = 0.90 F_{cr} A_g = 0.90 \times 262.91 \times 6,353 \times 10^{-3} = 1,503.26\,\text{kN}$$
$$\frac{P_u}{\phi_c P_n} = \frac{1,200.0}{1,503.26} = 0.798 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

### Step 8: 축압축-이축휨 P-M 조합력 상호작용 검토
$$\because \frac{P_u}{\phi_c P_n} = 0.798 \ge 0.20 \quad \implies \quad \text{KDS 14 31 10 식 4.5-1 적용}$$
$$\text{DCR}_{pm} = \frac{P_u}{\phi_c P_n} + \frac{8}{9} \left( \frac{B_1 M_{ux}}{\phi_b M_{nx}} + \frac{B_1 M_{uy}}{\phi_b M_{ny}} \right)$$
$$\text{DCR}_{pm} = 0.798 + \frac{8}{9} \left( 0.487 + 0.082 \right) = 0.798 + 0.506 = 0.894 \le 1.000 \quad \longrightarrow \quad \mathbf{O.K}$$

---

## 5. 원본 고유 판정 표기 및 인쇄 스타일링 규약

1. **판정 화살표 및 배지**:
   - `  →  O.K` : 볼드 녹색 (`#16a34a`)
   - `  →  N.G` : 볼드 적색 (`#dc2626`)
2. **반응형 폰트 및 KaTeX 인라인**:
   - 수식 폰트 크기: `0.95rem` (줄바꿈 방지 `overflow-x: auto`)
   - 테이블 내부 테두리: 미세 그레이 (`#e5e7eb`)

---

## 6. DoD 검증 및 수용 기준 (Acceptance Criteria)

- [ ] `src/web/static/js/report/redcr_steel_beam_column.js` 신규 구현 완료.
- [ ] 5대 장구분 및 8단계 KaTeX 수식 전개식 브라우저 정상 렌더링 확인.
- [ ] 상세 보고서 / 요약 보고서 전환 및 사용자 입력 포함 토글 확인.
- [ ] 브라우저 인쇄 프리뷰(`Ctrl + P`) 시 A4 용지 규격에 맞게 분할 출력 확인.
- [ ] 브라우저 콘솔 에러 0건 유지.
