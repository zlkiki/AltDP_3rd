# 요구사항 11: 통합 반응형 웹 UI/UX 완성 및 전수 무결성 검증

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
AltDP_3rd의 최종 목표는 Midas Design+의 모든 설계 엔진을 순수 Python/Web 기반으로 완벽히 마이그레이션하여, 현대적인 브라우저에서 0.05초 이내에 반응하는 인터랙티브 구조설계 환경을 제공하는 것입니다.

### 1.2. 목적
1. RC(보, 기둥, 벽체, 슬래브, 기초, 옹벽), 철골(보, 기둥, 가새, 접합부, 베이스플레이트), SRC, 알루미늄, 보강의 **전 부재 통합 파라메트릭 웹 대시보드 UI/UX 구축**.
2. 고품질 디자인 토큰(다크/라이트 모드 지원, 세련된 공학 인디케이터, DCR 상태 바, 글래스모피즘), 반응형 2D 배근 단면도 캔버스, 3D P-M 상관도 뷰어를 결합.
3. Ghidra 추출 47개 핵심 C 소스, 47,110개 원본 심볼, `kcsc2md` 기준서 예제집에 대한 **3대 Pytest 스위트(엔진/API/UI) 전수 회귀 테스트 및 0.1% 오차 무결성 검증**.

---

## 2. 웹 UI/UX 아키텍처 및 디자인 시스템

### 2.1. 디자인 토큰 및 인터페이스 원칙
* **모던 공학 인터페이스**:
  - CSS Custom Properties를 이용한 테마 시스템 (Dark Slate Theme / Clean Light Theme).
  - 안전율 판정 인디케이터: Safe (초록, DCR $\le 0.90$), Warning (주황, $0.90 < \text{DCR} \le 1.0$), Danger (적색, $\text{DCR} > 1.0$).
* **실시간 비동기 연동 파이프라인**:
  - 치수/하중 입력 즉시 `fetch('/api/v1/...')` 비동기 호출 $\rightarrow$ 50ms 이내 수치 갱신 및 캔버스 재렌더링.

---

## 3. 웹 프론트엔드 및 테스트 디렉토리 아키텍처

```text
src/
├── web/
│   ├── templates/
│   │   ├── base.html          # 글로벌 네비게이션 및 공통 레이아웃
│   │   ├── dashboard.html     # 부재별 설계 현황 대시보드
│   │   ├── rc_designer.html   # RC 보/기둥/벽체/기초 통합 설계기
│   │   └── steel_designer.html# 철골/접합부 통합 설계기
│   └── static/
│       ├── css/
│       │   ├── design_tokens.css # 색상, 타이포그래피, 간격 변수
│       │   └── style.css         # 전 부재 컴포넌트 스타일
│       └── js/
│           ├── app.js            # 상태 관리 및 API 통신 매니저
│           ├── renderer2d.js     # Canvas 2D 단면 렌더러
│           └── pm_chart.js       # P-M 상관도 차트
tests/
├── engine/                    # 1. 수치해석/공학식 단위 테스트 (~0.5s)
├── api/                       # 2. FastAPI 엔드포인트 및 스키마 테스트 (~0.5s)
├── ui/                        # 3. 캔버스 렌더링 및 템플릿 테스트 (~0.5s)
└── e2e/                       # 4. 전체 부재 설계 $\rightarrow$ 계산서 출력 E2E 통합 테스트
```

---

## 4. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 11-1** | `요구사항11-1_통합_반응형_웹_대시보드_및_디자인시스템.md` | `src/web/templates/`, `design_tokens.css`, `style.css`, `app.js` | 모던 UI 컴포넌트, 다크모드, 반응형 레이아웃 |
| **Phase 11-2** | `요구사항11-2_전_부재_설계_캔버스_통합_인터랙션.md` | `renderer2d.js`, `pm_chart.js`, 부재별 실시간 캔버스 바인딩 | 파라미터 변경 즉시 캔버스/차트 실시간 동기화 |
| **Phase 11-3** | `요구사항11-3_전_도메인_회귀테스트_및_0_1퍼센트_무결성검증.md` | `tests/e2e/`, 3대 Pytest 스위트 전체 실행 스크립트 | 전체 pytest 100% 통과 (1.5초 이내) & 무결성 확정 |

---

## 5. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] **웹 UI 반응성 및 심미성**: 입력값 변경 시 50ms 이내 재계산 및 캔버스 갱신 완료, 모던 프리미엄 다크/라이트 디자인 구현.
- [ ] **3대 Pytest 체계 100% 통과**:
  - `pytest tests/engine/` : 모든 부재 내력 수치해석 오차 0.1% 미만 통과.
  - `pytest tests/api/` : 모든 REST API 라우트 정상 응답.
  - `pytest tests/ui/` : HTML 템플릿 및 캔버스 좌표 함수 검증.
- [ ] **E2E 전체 파이프라인 무결성**: 단면 선택 $\rightarrow$ 하중 입력 $\rightarrow$ 2D/3D 시각화 $\rightarrow$ A4 구조계산서 출력 전 과정 단절 없는 연속 동작 검증 완료.
