# 요구사항 24-4: Phase V1-3 Step 4 RC 전단벽 A4 5대장구분 8단계 KaTeX 구조계산서 명세서

## 1. 개요 및 계산서 출력 파이프라인 매핑

본 문서는 **RC 전단벽 (`rc_shear_wall`)**의 **Step 4 (A4 5대장구분 8단계 KaTeX 구조계산서)** 구현을 위한 상세 요구사항 명세서입니다.

* **부재 및 모듈 식별자**: `rc_shear_wall` (카탈로그 No. 4, Tier 1 플래그십)
* **담당 소스 파일**:
  - `src/web/static/js/report/redcr_rc_wall.js` (신규 전단벽 전용 KaTeX 계산서 렌더러)
  - `src/report/generator.py` (백엔드 HTML/PDF 보고서 생성기)
* **워크스페이스 타겟**:
  - **Right Dock (Pane 4: `#pane-right-report`)**: 상시 순백색(`#ffffff`) A4 고정 용지 계산서
* **2순위 원본 계산서 SSOT**:
  - 원본앱 `CMSOffice`, `CMSExcel` 심볼 및 전단벽 구조계산서 출력 양식
  - 원본 고유 적합성 판정 표기: `  →  O.K` 및 `  →  N.G`

---

## 2. A4 용지 레이아웃 및 뷰 모드 표준

1. **상시 순백색(`#ffffff`) A4 고정 용지**:
   - 다크 모드 활성화 시에도 실제 출력물과의 1:1 일치를 위해 계산서 시트는 항상 순백색(`#ffffff`) 배경과 고대비 텍스트(`#111827`) 유지.
   - 인쇄 여백: 상하좌우 20mm, A4 규격 폭($210\text{ mm} \times 297\text{ mm}$) 최적화.
2. **보고서 상단 컨트롤 툴바**:
   - 출력 모드 분기: `(•) 상세 (Detail)` / `( ) 요약 (Summary)` 라디오 버튼.
   - 입력 파라미터 포함 토글: `[☑] 사용자 입력 데이터 상세 포함`.
   - 엔지니어링 액션: `[🖨️ 인쇄 (Print)]`, `[📄 PDF 내보내기]`, `[📊 Excel 내보내기]`.

---

## 3. 원본앱 5대 장구분 계산서 구성 체계

```
================================================================================
KDS 14 20 00 / KDS 14 20 80 콘크리트구조설계기준
부재 설계 계산서: RC 전단벽 (Shear Wall) [ 부재명: 1F-W1 ]
================================================================================

1. 설계 개요 및 재료 물성치 (Design Overview & Material Properties)
   1.1 설계 기준 및 부재 개요
   1.2 콘크리트 및 철근 재료 특성치

2. 단면 제원 및 배근 상세 (Section Geometry & Reinforcement)
   2.1 벽체 형상 치수 (tw, lw, hw, Hw)
   2.2 수직 및 수평 철근 배근 (복배근, 배근비 rho_v, rho_h 최소기준 검토)
   2.3 단부 집중 주철근 및 경계요소 띠철근 배근

3. 설계 부재력 및 내진 조건 (Design Factored Loads & Seismic Conditions)
   3.1 계수 하중 (Pu, Mu, Vu) 및 전단 검토용 부재력
   3.2 내진 설계 등급 (특수 전단벽) 및 설계변위 delta_u

4. 전단강도 검토 (Shear Strength Verification - 8단계 KaTeX)
   4.1 유효깊이 d 산정
   4.2 콘크리트 전단강도 Vc 상세 유도 (Vc1, Vc2)
   4.3 전단철근 부담 전단강도 Vs 산정
   4.4 공칭전단강도 상한 Vn_max 검토
   4.5 설계전단강도 phi_Vn 및 전단 DCR 산출  →  O.K / N.G

5. 면내 휨-축력 및 특수경계요소(SBE) 상세 검토
   5.1 면내 P-M 상관 휨강도 phi_Mn 및 휨 DCR 검토  →  O.K / N.G
   5.2 변위기반 특수경계요소 필요성 판정 (c vs c_limit)  →  필요 / 불필요
   5.3 경계요소 소요 구속길이 lc 검토  →  O.K / N.G
   5.4 경계요소 횡구속 철근량 Ash 검토  →  O.K / N.G
   5.5 띠철근 최대 수직간격 s_max 검토  →  O.K / N.G
```

---

## 4. 제4장 전단강도 검토 8단계 KaTeX 수식 전개 사양

계산서 제4장에서는 KDS 14 20 22 4.8에 따른 전단강도 산정 전 과정을 8단계 수식으로 완벽히 전개합니다:

### [1단계] 유효깊이 $d$ 산정
$$d = 0.8 \times l_w = 0.8 \times 4{,}000 = 3{,}200\text{ mm}$$

### [2단계] 콘크리트 기본 전단강도 $V_{c1}$ (축력 효과 반영)
$$V_{c1} = 0.28 \lambda \sqrt{f_{ck}} t_w d + \frac{N_u d}{4 l_w}$$
$$V_{c1} = 0.28 \times 1.0 \times \sqrt{24} \times 300 \times 3{,}200 \times 10^{-3} + \frac{1{,}200 \times 3{,}200}{4 \times 4{,}000} = 1{,}316.94 + 240.00 = 1{,}556.94\text{ kN}$$

### [3단계] 콘크리트 상세 전단강도 $V_{c2}$ (모멘트/전단비 반영)
$$\alpha_m = \frac{M_u}{V_u} - \frac{l_w}{2} = \frac{2{,}400}{800} \times 10^3 - \frac{4{,}000}{2} = 3{,}000 - 2{,}000 = 1{,}000\text{ mm} > 0$$
$$V_{c2} = \left[ 0.05 \lambda \sqrt{f_{ck}} + \frac{l_w \left(0.1 \lambda \sqrt{f_{ck}} + 0.2 \frac{N_u}{l_w t_w}\right)}{\frac{M_u}{V_u} - \frac{l_w}{2}} \right] t_w d$$
$$V_{c2} = \left[ 0.245 + \frac{4{,}000 \times (0.490 + 0.2 \times \frac{1{,}200 \times 10^3}{4{,}000 \times 300})}{1{,}000} \right] \times 300 \times 3{,}200 \times 10^{-3} = 2{,}817.60\text{ kN}$$

### [4단계] 콘크리트 설계 전단강도 $V_c$ 결정
$$V_c = \min(V_{c1}, V_{c2}) = \min(1{,}556.94, \; 2{,}817.60) = 1{,}556.94\text{ kN}$$

### [5단계] 수평 전단철근 부담 전단강도 $V_s$
$$V_s = \frac{A_v f_{yt} d}{s_h} = \frac{253.4 \times 400 \times 3{,}200}{200} \times 10^{-3} = 1{,}621.76\text{ kN}$$

### [6단계] 공칭전단강도 상한 $V_{n,max}$ 검토
$$V_{n,max} = \frac{5}{6} \sqrt{f_{ck}} t_w d = \frac{5}{6} \times \sqrt{24} \times 300 \times 3{,}200 \times 10^{-3} = 3{,}919.18\text{ kN}$$
$$V_n = V_c + V_s = 1{,}556.94 + 1{,}621.76 = 3{,}178.70\text{ kN} \le V_{n,max} \quad \mathbf{\rightarrow\quad O.K}$$

### [7단계] 설계 전단강도 $\phi V_n$ 산정
$$\phi V_n = \phi (V_c + V_s) = 0.75 \times 3{,}178.70 = 2{,}384.03\text{ kN}$$

### [8단계] 전단 강도비 및 최종 적합성 판정
$$\text{DCR}_v = \frac{V_u}{\phi V_n} = \frac{800.00}{2{,}384.03} = 0.336 \le 1.000 \quad \mathbf{\rightarrow\quad O.K}$$

---

## 5. 제5장 특수경계요소(SBE) 상세 검토 KaTeX 수식 전개 사양

### 5.1. 변위기반 특수경계요소(SBE) 설치 필요성 판정 (KDS 14 20 80 4.6)
$$c_{limit} = \frac{l_w}{600 \left(\frac{\delta_u}{H_w}\right)} = \frac{4{,}000}{600 \left(\frac{30}{35{,}000}\right)} = \frac{4{,}000}{0.5143} = 7{,}777.78\text{ mm}$$
$$c = 850.00\text{ mm} < c_{limit} = 7{,}777.78\text{ mm} \quad \mathbf{\rightarrow\quad \text{특수경계요소 불필요 (선택적 보강)}}$$
*(참고: $c \ge c_{limit}$인 경우 `  →  특수경계요소 설치 필수 [SBE REQUIRED]`로 자동 분기)*

### 5.2. 경계요소 소요 구속길이 $l_c$ 검토
$$l_{c,req} = \max\left(c - 0.1 l_w, \; \frac{c}{2}\right) = \max(850 - 400, \; 425) = 450.00\text{ mm}$$
$$l_{c,prov} = 600.00\text{ mm} \ge l_{c,req} = 450.00\text{ mm} \quad \mathbf{\rightarrow\quad O.K}$$

### 5.3. 경계요소 횡보강근 소요 단면적 $A_{sh}$ 검토
$$\frac{A_{sh}}{s h_c} \ge 0.09 \frac{f_{ck}}{f_{yt}} = 0.09 \times \frac{24}{400} = 0.00540\text{ mm}^{-1}$$
$$A_{sh,req} = 0.00540 \times 100 \times 220 = 118.80\text{ mm}^2$$
$$A_{sh,prov} = 2 \times 71.3 = 142.60\text{ mm}^2 \ge 118.80\text{ mm}^2 \quad \mathbf{\rightarrow\quad O.K}$$

### 5.4. 띠철근 최대 수직간격 $s_{max}$ 검토
$$s_{max} \le \min\left(\frac{t_w}{3}, \; 6 d_b, \; 150\right) = \min(100, \; 6 \times 22.2, \; 150) = 100\text{ mm}$$
$$s_{prov} = 100\text{ mm} \le s_{max} = 100\text{ mm} \quad \mathbf{\rightarrow\quad O.K}$$

---

## 6. 완료 정의 (Definition of Done)

- [ ] `src/web/static/js/report/redcr_rc_wall.js` 렌더러 구현 완료.
- [ ] 5대 장구분 체계 및 8단계 KaTeX 수식 전개 정상 렌더링.
- [ ] 상세/요약 분기 및 사용자 입력 데이터 포함 토글 정상 동작.
- [ ] A4 순백색 시트 출력 및 `  →  O.K / N.G` 판정 표기 일치.
- [ ] 브라우저 인쇄 프리뷰 시 페이지 분할 무결성 및 콘솔 에러 0건.
