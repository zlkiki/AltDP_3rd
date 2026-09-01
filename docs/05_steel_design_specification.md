# 철골 부재설계 기준서 (KDS 14 31 00) (05_steel_design_specification.md)

## 1. 적용 설계기준
* **KDS 14 31 10 (강구조 부재설계기준 - 하중저항계수설계법 LRFD)**
* **KDS 14 31 25 (강구조 접합부 설계기준)**

---

## 2. 부재별 핵심 설계 수식

### 1) 철골 보 (Steel Beam - `CSTLCodeCheck::CHK_SBM`)
* **단면 콤팩트성(판폭두께비) 판정**:
  * 플랜지: $\lambda = b/t_f \le \lambda_p = 0.38 \sqrt{E/F_y}$
  * 웨브: $\lambda = h/t_w \le \lambda_p = 3.76 \sqrt{E/F_y}$
* **공칭 휨강도 ($M_n$) 및 횡비틀림좌굴(LTB)**:
  * 비지지길이 $L_b \le L_p$: $M_n = M_p = F_y Z_x$
  * $L_p < L_b \le L_r$:
    $$M_n = C_b \left[ M_p - (M_p - 0.7 F_y S_x) \left(\frac{L_b - L_p}{L_r - L_p}\right) \right] \le M_p$$
  * $L_b > L_r$:
    $$M_n = F_{cr} S_x \le M_p, \quad F_{cr} = \frac{C_b \pi^2 E}{\left(\frac{L_b}{r_{ts}}\right)^2} \sqrt{1 + 0.078 \frac{J c}{S_x h_o}\left(\frac{L_b}{r_{ts}}\right)^2}$$
  * 강도감소계수: $\phi_b = 0.90$

---

### 2) 철골 기둥 (Steel Column - `CSTLCodeCheck::CHK_SCOL`)
* **공칭 압축강도 ($P_n$)**:
  * 탄성/비탄성 휨좌굴:
    $$\frac{K L}{r} \le 4.71 \sqrt{\frac{E}{F_y}} \implies F_{cr} = \left[0.658^{\frac{F_y}{F_e}}\right] F_y$$
    $$\frac{K L}{r} > 4.71 \sqrt{\frac{E}{F_y}} \implies F_{cr} = 0.877 F_e$$
    여기서 $F_e = \frac{\pi^2 E}{(KL/r)^2}$, $\quad P_n = F_{cr} A_g, \quad \phi_c = 0.90$.
* **축압축과 휨의 조합응력 (P-M Interaction)**:
  * $\frac{P_u}{\phi_c P_n} \ge 0.2 \implies \frac{P_u}{\phi_c P_n} + \frac{8}{9}\left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$
  * $\frac{P_u}{\phi_c P_n} < 0.2 \implies \frac{P_u}{2 \phi_c P_n} + \left(\frac{M_{ux}}{\phi_b M_{nx}} + \frac{M_{uy}}{\phi_b M_{ny}}\right) \le 1.0$

---

### 3) 철골 접합부 (Connection - `CSteelBoltConnection`)
* **고장력 볼트 전단강도**:
  $$R_n = F_{nv} A_b \quad (\phi = 0.75)$$
* **지압강도**:
  $$R_n = \min(1.2 l_c t F_u, 2.4 d t F_u) \quad (\phi = 0.75)$$
* **블록전단파단 (Block Shear Rupture)**:
  $$R_n = 0.60 F_u A_{nv} + U_{bs} F_u A_{nt} \le 0.60 F_y A_{gv} + U_{bs} F_u A_{nt}$$
