# [요구사항19-1] AltDP_2nd Zero-Build 4분할 UI/UX 프레임워크 이식

## 1. 개요 및 목적
* AltDP_2nd의 정식 4-Pane 반응형 레이아웃 마크업과 6대 모듈러 CSS(`theme.css`, `layout.css`, `components.css`, `canvas.css`, `report.css`, `print.css`) 및 코어 UI 인프라 JS(`layout_resizer.js`, `theme_manager.js`, `unit_manager.js`, `project_store.js`, `member_manager.js`)를 `AltDP_3rd`에 완전 이식합니다.
* **소스 직접 재활용 & 토큰 효율성 원칙**: `AltDP_2nd/web/`의 검증된 파일들을 새로 작성하지 않고 그대로 직접 복사하여 이식함으로써 토큰 낭비를 차단하고 100% 레이아웃 정확성을 보장합니다.
* FastAPI 서버(`src/api/server.py`)의 정적 파일 마운트와 템플릿 서빙을 AltDP_2nd 단일 포트 Zero-Build 아키텍처에 맞게 정렬합니다.

---

## 2. 세부 개발 작업 명세

### 2.1. 6대 모듈러 CSS 이식 (`src/web/static/css/`)
* `AltDP_2nd/web/css/`에서 아래 6개 파일 복사 및 AltDP_3rd 경로 정렬:
  1. `theme.css`: 다크/라이트 테마 엔지니어링 토큰, 고대비 팔레트, 순백색 A4 변수.
  2. `layout.css`: 4-Split Grid/Flexbox 워크스페이스, 독립 리사이저 바 서식.
  3. `components.css`: 탑 마스터 툴바, 스마트 사이드바(고정핀, 카테고리 필스, 트리 레벨 버튼), 콤보박스, 부재 테이블.
  4. `canvas.css`: 2D Canvas 뷰포트, DCR 컬러 레전드 바, 리셋 버튼.
  5. `report.css`: A4 고정폭(794px), 순백색(`#ffffff`) 용지 강제, KDS 조항 표기 및 DCR 배지.
  6. `print.css`: 브라우저 A4 출력 전용 `@media print` 스타일 (여백 0, 컨트롤 숨김).

### 2.2. 코어 인터랙션 JS 컴포넌트 이식 (`src/web/static/js/`)
* **스토어 & 단위계 레이어**:
  - `src/web/static/js/store/unit_manager.js`: SI / SI-M / MKS / US 4대 단위계 환산 및 구독기.
  - `src/web/static/js/store/project_store.js`: 부재별 파라미터 상태 관리, JSON 저장/불러오기 (`exportProject`, `importProject`), 로컬스토리지 동기화.
* **UI 레이아웃 & 부재 관리자**:
  - `src/web/static/js/components/layout_resizer.js`: 4대 독립 리사이저(사이드바H, 메인H, 인풋/캔버스H, 부재목록/인풋V), 사이드바 3초 자동 숨김 & 고정핀(📌) 제어.
  - `src/web/static/js/components/theme_manager.js`: 다크/라이트 테마 토글 및 로컬 저장.
  - `src/web/static/js/components/member_manager.js`: 부재 CRUD(+추가, 복제, 삭제, 이름변경), DCR 점 및 요약 동기화.

### 2.3. 메인 레이아웃 템플릿 교체 (`src/web/templates/index.html`)
* 기존 리본바 실험용 템플릿을 AltDP_2nd의 완성형 4분할 레이아웃 마크업으로 전면 교체:
  - **Top Master Toolbar**: 브랜드, KDS 배지, 빠른 검색(`Ctrl+K`), 단위계 셀렉터, 테마 토글, 레이아웃 저장/초기화.
  - **Left Sidebar**: 설계 모듈 탐색기, JSON 저장/불러오기, 카테고리 필스(`전체`, `RC`, `Steel`, `PC`, `기타`), 1/2/3단계 트리 레벨 버튼, 고정핀(📌).
  - **Pane 1 (Member List)**: 부재 리스트 관리자 (`#pane-member-list`).
  - **Pane 2 (Input Form)**: 브레드크럼 배너 + 동적 폼 스크롤 래퍼 (`#pane-input-form`).
  - **Pane 3 (Graphic View)**: 2D 단면 Canvas 뷰포트 (`#pane-graphic-view`).
  - **Pane 4 (Report View)**: A4 고정형 KDS 계산서 뷰포트 (`#pane-right-report`).

---

## 3. 체크리스트 및 완료 검증
- [ ] 6대 CSS 파일이 `src/web/static/css/`에 배치되고 브라우저에서 정상 로드되는가?
- [ ] `index.html` 접근 시 Top Toolbar, Sidebar, 4-Split Panes가 시각적으로 완벽하게 렌더링되는가?
- [ ] 4개 리사이저 바(사이드바, 메인좌우, 인풋/캔버스좌우, 부재목록/폼상하) 드래그 시 부드럽게 크기가 조절되는가?
- [ ] 테마 토글(🌙/☀️) 및 단위계 셀렉터 변경 시 UI 상태가 정상 전환되는가?
- [ ] 사이드바 고정핀(📌) 및 `Ctrl+B`, `Ctrl+K` 단축키가 즉각 반응하는가?
- [ ] `pytest tests/ui/` 테스트 통과 및 서버 기동 정상 확인.
