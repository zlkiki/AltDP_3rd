# RC 부재설계 기준서 (KDS 14 20 00) (04_rc_design_specification.md)

## 1. 적용 설계기준
* **KDS 14 20 00 (콘크리트구조설계기준)**
* **KDS 14 20 10 (휨 및 압축 설계기준)**
* **KDS 14 20 22 (전단 및 비틀림 설계기준)**
* **KDS 14 20 54 (콘크리트용 앵커 설계기준)**

---

## 2. 부재별 핵심 설계 수식

### 1) RC 보 (Beam - `CRCSCodeCheck::CHK_BBBE`)
* **등가직사각형 응력블록 계수**:
  $$\alpha_1 = 0.85, \quad \beta_1 = \max\left(0.85 - 0.007(f_{ck} - 28), 0.65\right) \quad (f_{ck} \ge 28\text{ MPa})$$
* **공칭 휨강도 ($M_n$)**:
  $$a = \frac{A_s f_y - A_s' f_s'}{\alpha_1 f_{ck} b}, \quad M_n = A_s f_y \left(d - \frac{a}{2}\right) + A_s' f_s' \left(\frac{a}{2} - d'\right)$$
* **강도감소계수 ($\phi$)**:
  * 인장지배단면 ($\epsilon_t \ge 0.005$ 또는 $2.5\epsilon_y$): $\phi = 0.85$
  * 압축지배단면 ($\epsilon_t \le \epsilon_y$): $\phi = 0.65$
  * 전이구간: $\phi = 0.65 + (\epsilon_t - \epsilon_y) \frac{0.85 - 0.65}{0.005 - \epsilon_y}$
* **공칭 전단강도 ($V_n = V_c + V_s$)**:
  $$V_c = \frac{1}{6} \lambda \sqrt{f_{ck}} b_w d, \quad V_s = \frac{A_v f_{yt} d}{s} (\sin\alpha + \cos\alpha)$$
  $$\phi V_n \ge V_u \quad (\phi = 0.75)$$

---

### 2) RC 기둥 (Column - `CRCSCodeCheck::CHK_BCCO`)
* **최대 공칭 압축강도 ($P_{n,max}$)**:
  * 띠철근(Tied): $P_{n,max} = 0.80 \left[0.85 f_{ck}(A_g - A_{st}) + f_y A_{st}\right]$
  * 나선철근(Spiral): $P_{n,max} = 0.85 \left[0.85 f_{ck}(A_g - A_{st}) + f_y A_{st}\right]$
* **P-M 상관도 곡선 산정 (Fiber Analysis)**:
  * 중립축 깊이 $c$를 무한대(순수압축)부터 0(순수인장)까지 변화시키며 단면 내 변형률 선도 계산:
  $$\epsilon_s(y) = \epsilon_{cu} \frac{c - y}{c} \quad (\epsilon_{cu} = 0.0033)$$
  * 콘크리트 압축력 $C_c$ 및 각 단근 인장/압축력 $T_s, C_s$의 평형방정식으로부터 $P_n, M_n$ 유도:
  $$P_n = \int \sigma_c \, dA + \sum A_{si} \sigma_{si}, \quad M_n = \int \sigma_c (y - y_c) \, dA + \sum A_{si} \sigma_{si} (y_i - y_c)$$
* **이축휨 검토 (Biaxial Bending)**:
  * Bresler 역수근사법: $\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_o}$ 또는 하중등고선법.

---

### 3) RC 전단벽 (Wall - `CRCSCodeCheck::CHK_BWUW`)
* **공칭 전단강도**:
  $$V_n = A_{cv} \left( \alpha_c \lambda \sqrt{f_{ck}} + \rho_t f_y \right)$$
  여기서 $h_w / l_w \le 1.5$이면 $\alpha_c = 0.25$, $h_w / l_w \ge 2.0$이면 $\alpha_c = 0.17$.
* **경계요소(Boundary Element) 필요성 검토**:
  $$c \ge \frac{l_w}{600 (\delta_u / h_w)}$$

---

### 4) RC 독립기초 (Footing - `CRCSCodeCheck::CHK_UFDN`)
* **1방향 전단 (보 작용)**: 기둥 면에서 $d$ 거리 단면에서 $V_u \le \phi V_c$.
* **2방향 전단 (펀칭 전단)**: 기둥 둘레에서 $d/2$ 떨어진 위험단면($b_o$)에서 검토:
  $$V_c = \min\left( \left(1 + \frac{2}{\beta}\right)\frac{\sqrt{f_{ck}} b_o d}{6}, \left(\frac{\alpha_s d}{b_o} + 2\right)\frac{\sqrt{f_{ck}} b_o d}{12}, \frac{1}{3}\sqrt{f_{ck}} b_o d \right)$$
* **지반 지지력 검토**:
  $$q_{max} = \frac{P}{B L} \pm \frac{6 M_x}{B L^2} \pm \frac{6 M_y}{B^2 L} \le q_a$$
