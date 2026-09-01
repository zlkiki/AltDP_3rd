# Web Application UI/UX 명세서 (07_web_application_ui_ux_specification.md)

## 1. 디자인 시스템 & UX 철학

**AltDP_3rd** 웹 애플리케이션은 현대적인 **AltDP Glassmorphism 디자인 시스템**을 적용하여 전문가용 엔지니어링 툴의 직관성과 심미성을 극대화합니다.

* **테마**: 다크 모드(기본) 및 라이트 모드 지원 (다크 슬레이트 `#0f172a`, 네이비 `#1e293b`, 엑센트 블루 `#38bdf8`, 성공 그린 `#22c55e`, 경고 레드 `#ef4444`).
* **타이포그래피**: `Pretendard`, `Inter`, 고정폭 `JetBrains Mono` 폰트 적용.
* **레이아웃**: 3열 반응형 레이아웃
  * **좌측 패널 (Sidebar)**: 부재 타입 네비게이션 (RC 보/기둥/벽/기초, Steel 보/기둥/접합부) 및 프로젝트 트리.
  * **중앙 캔버스 (Main Canvas)**: 실시간 2D 배근 단면도 / 3D 단면 뷰어 및 하중 다이어그램.
  * **우측 패널 (Property & Check)**: 단면 치수, 재료, 철근 배근, 하중 입력 및 실시간 DCR(안전율) 요약 카드.
  * **하단 도킹 패널 (Bottom Dock)**: 대화형 P-M 상관도 차트 및 KDS 계산 검토 상세 로그.

---

## 2. 2D/3D 대화형 렌더링 컴포넌트

1. **2D Canvas 배근 렌더러 (`renderer2d.js`)**:
   * 피복두께(Cover Concrete), 주근 원형 심볼, 늑근/대근 절곡 형상, 치수 보조선 자동 렌더링.
   * 줌/팬(Zoom & Pan) 및 단면 크기 변경 시 실시간 동기화.
2. **P-M 상관도 차트 (`pm_chart.js`)**:
   * Chart.js 기반 KDS 공칭강도($P_n-M_n$) 및 설계강도($\phi P_n-\phi M_n$) 곡선 플로팅.
   * 설계 하중점($(M_u, P_u)$) 표시 및 안전 여유도(DCR) 컬러 코딩 (DCR $\le 1.0$: Green, DCR $> 1.0$: Red).
3. **A4 구조계산서 뷰어**:
   * 브라우저 인쇄(`@media print`) 및 PDF 출력에 최적화된 A4 규격 계산서 템플릿.
