# 요구사항 04-3: RC기둥 장주·이축휨설계, REST API 및 3D P-M 차트 UI

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* KDS 14 20 20에 따른 RC 기둥의 세장비 검토 및 모멘트 확대계수법($\delta_{ns}, \delta_s$), 이축휨 설계(Bresler 식, PCA 하중등고선법), 띠철근/나선철근 상세 규준 검토를 통합 구현합니다.
* FastAPI 기반 REST API 엔드포인트와 Web 프론트엔드 대화형 3D/2D P-M 상관도 차트(`src/web/static/js/pm_chart.js`)를 구축하여 웹에서 즉각적인 기둥 설계 및 시각화가 가능하도록 합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스**: [`decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCCO_column_pm.c), [`decompiled_src/core_routines/solver/CHK_BCGR_column_group.c`](file:///f:/PyProject/AltDP_3rd/decompiled_src/core_routines/solver/CHK_BCGR_column_group.c)
* **KDS 기준서**: KDS 14 20 20 (세장효과, 모멘트 확대), KDS 14 20 50 (철근상세 - 띠철근/나선철근 간격)
* **대상 소스**: [`src/engine/rc/column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rc/column.py), [`src/api/routes/rc_column.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_column.py), [`src/web/static/js/pm_chart.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/pm_chart.js)

---

## 2. 상세 구현 명세

### 2.1. 장주효과 및 세장비 검토 (KDS 14 20 20)
* **세장비 한계 판정**:
  - 비횡구속 골조: $k L_u / r \le 22$ (단주) $\implies$ 모멘트 확대 불필요
  - 횡구속 골조: $k L_u / r \le 34 - 12(M_1/M_2) \le 40$
  - 단면 2차 회전반경: 직사각형 $r = 0.3 h$, 원형 $r = 0.25 D$
* **모멘트 확대계수 산정 ($\delta_{ns}$)**:
  - 오일러 좌굴하중: $P_c = \frac{\pi^2 (EI)_{eff}}{(k L_u)^2}$
  - 유효 휨강성: $(EI)_{eff} = \frac{0.4 E_c I_g}{1 + \beta_{dns}}$ 또는 $\frac{0.2 E_c I_g + E_s I_{se}}{1 + \beta_{dns}}$
  - $\delta_{ns} = \frac{C_m}{1 - P_u / (0.75 P_c)} \ge 1.0 \quad (C_m = 0.6 + 0.4(M_1/M_2) \ge 0.4)$
  - 확대 휨모멘트: $M_c = \delta_{ns} M_2 \ge P_u (15 + 0.03 h)$ (최소 편심 모멘트 적용)

### 2.2. 이축휨 및 전단/철근상세 검토
* **이축휨 평가**:
  - Bresler 역수식: $\frac{1}{P_n} = \frac{1}{P_{nx}} + \frac{1}{P_{ny}} - \frac{1}{P_0}$
  - PCA Load Contour 법: $\left(\frac{M_{ux}}{\phi M_{nx}}\right)^\alpha + \left(\frac{M_{uy}}{\phi M_{ny}}\right)^\alpha \le 1.0$ ($\alpha \approx 1.15 \sim 1.5$)
  - 파이버 3D P-M 표면 기반 직접 판정(최고 정밀도) 지원
* **띠철근/나선철근 간격 규준 (KDS 14 20 50)**:
  - 띠철근 수직간격 $s_{max} = \min(16 d_b, 48 d_t, \text{단면 최소치수})$
  - 나선철근 체적비 $\rho_s = 0.45 \left(\frac{A_g}{A_{ch}} - 1\right) \frac{f_{ck}}{f_{yt}}$

### 2.3. REST API & Web 대화형 3D/2D P-M 차트 UI
* **FastAPI 엔드포인트**:
  - `POST /api/v1/rc/column/design`: 기둥 세장비, 이축휨, 전단 및 상세 종합 설계
  - `POST /api/v1/rc/column/pm-curve`: 2D/3D P-M 상관곡선 데이터 포인트 반환
* **Web UI 차트 (`pm_chart.js`)**:
  - 2D Canvas / Plotly 기반 $P-M_x$, $P-M_y$ 곡선 및 설계 하중 작용점 매핑
  - 3D 표면 인터랙티브 뷰 및 DCR 게이지 표시

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/engine/rc/column.py`](file:///f:/PyProject/AltDP_3rd/src/engine/rc/column.py) | [MODIFY] | 세장비/모멘트확대, 이축휨, 띠철근 상세 및 파이버 솔버 연동 고도화 |
| [`src/api/schemas/rc_column.py`](file:///f:/PyProject/AltDP_3rd/src/api/schemas/rc_column.py) | [NEW] | 기둥 설계 및 P-M 곡선 Pydantic v2 I/O 스키마 |
| [`src/api/routes/rc_column.py`](file:///f:/PyProject/AltDP_3rd/src/api/routes/rc_column.py) | [NEW] | FastAPI 기둥 설계 및 P-M 곡선 엔드포인트 |
| [`src/api/main.py`](file:///f:/PyProject/AltDP_3rd/src/api/main.py) | [MODIFY] | `rc_column` 라우터 등록 |
| [`src/web/static/js/pm_chart.js`](file:///f:/PyProject/AltDP_3rd/src/web/static/js/pm_chart.js) | [NEW] | 대화형 2D/3D P-M 상관도 및 하중점 렌더러 |
| [`tests/engine/test_rc_column.py`](file:///f:/PyProject/AltDP_3rd/tests/engine/test_rc_column.py) | [NEW] | 장주효과($\delta_{ns}$), Bresler 이축휨, 철근간격 검증 단위테스트 |
| [`tests/api/test_rc_column_api.py`](file:///f:/PyProject/AltDP_3rd/tests/api/test_rc_column_api.py) | [NEW] | FastAPI `/api/v1/rc/column/*` 엔드포인트 E2E 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] 단주/장주 자동 판정 및 모멘트 확대계수 $\delta_{ns} \ge 1.0$ 산정 검증
- [x] 최소 편심 모멘트 $P_u (15 + 0.03 h)$ 적용 검증
- [x] 띠철근 최대 간격 및 축방향 철근비($1\% \le \rho_g \le 8\%$) 한계상태 검증
- [x] FastAPI `/api/rc/column/design` 및 `/pm-curve` 응답 무결성 검증
- [x] `pytest tests/engine/test_rc_column.py tests/api/test_rc_column_api.py` 100% 통과 (수행시간 < 1.0초)
