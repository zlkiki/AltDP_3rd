# [요구사항19-2] 단위부재 스키마 및 동적 폼 KS DB 컴포넌트 연동

## 1. 개요 및 목적
* 54종 단위부재의 입력 인터페이스를 구성하는 동적 폼 빌더(`form_generator.js`), KS 표준 콤보박스(`form_combobox.js`), KS 규격 DB 자산(`ks_sections.js`, `rebar_db.js`, `ks_bolt_db.js`), 최적 자동설계기(`auto_designer.js`)를 이식합니다.
* **소스 직접 재활용 & 토큰 효율성 원칙**: `AltDP_2nd/web/js/`의 검증된 폼, 콤보박스, 자동설계기 및 KS DB 소스를 그대로 복사하여 활용함으로써 토큰을 절약하고 콤보박스/폼 동작 정밀도를 완벽히 유지합니다.
* 백엔드에 `/api/modules` 및 `/api/schema/{category}/{group}/{module_id}` 엔드포인트를 구축하여 부재 선택 시 실시간으로 파라메트릭 인풋 폼이 생성되도록 연결합니다.

---

## 2. 세부 개발 작업 명세

### 2.1. KS 표준 DB 자산 이식 (`src/web/static/js/db/`)
1. `ks_sections.js`: KS H형강, 각형강관, 원형강관, C형강 단면 제원 DB.
2. `rebar_db.js`: KS D 3504 이형철근(D10~D57) 공칭직경, 공칭단면적, 단위중량 DB.
3. `ks_bolt_db.js`: KS F10T, TS볼트 고력볼트 규격 및 전단/인장 설계강도 DB.

### 2.2. 동적 폼 & 콤보박스 컴포넌트 이식 (`src/web/static/js/components/`)
1. `form_combobox.js`:
   - 클릭 즉시 드롭다운 팝업 리스트 + 직접 키보드 타이핑 검색 지원 하이브리드 위젯.
   - 철근 직경, 강종, 형강 규격 변경 시 즉시 폼 이벤트 디스패치.
2. `form_generator.js`:
   - 백엔드 JSON Schema를 파싱하여 라벨, 단위 뱃지, 유효범위, 툴팁이 완비된 그리드 폼 자동 렌더링.
   - 2단 적층형 헤더 및 모듈 경로 브레드크럼 배너 (`RC › 보 (Beam) › 직사각형 보`).
   - 3버튼 액션 바: **[💾 적용]**, **[⚡ 검토]**, **[✨ 설계]** 통합 파이프라인 연동.
3. `auto_designer.js`:
   - 부재 단면 및 철근 배근을 순차적으로 탐색하여 $DCR \le 1.0$을 만족하는 최적 규격을 자동 도출하는 클라이언트 엔진.

### 2.3. 백엔드 스키마 엔드포인트 구축 (`src/api/routes/schema.py`)
1. `GET /api/modules`:
   - 54개 모듈 메타데이터(`key`, `name`, `category`, `group`, `id`, `geomType`, `description`) 반환.
2. `GET /api/schema/{category}/{group}/{module_id}`:
   - 해당 모듈의 Pydantic Input Schema 및 기본값, 최소/최대 제약조건 반환.

---

## 3. 체크리스트 및 완료 검증
- [ ] KS 규격 DB 3종(`ks_sections.js`, `rebar_db.js`, `ks_bolt_db.js`)이 정상 로드되는가?
- [ ] 좌측 탐색기에서 임의의 모듈(예: `rc/beam/base`, `steel/member/beam`) 선택 시 동적 폼이 즉각 렌더링되는가?
- [ ] 콤보박스에서 철근 규격(`D25`, `D22`) 및 강종(`SD400`, `SD500`) 선택이 원활한가?
- [ ] 폼 입력값 변경 시 50ms 디바운스로 `ProjectStore` 및 캔버스에 실시간 반영되는가?
- [ ] 스키마 엔드포인트 `GET /api/modules` 및 `GET /api/schema/...`가 유효한 JSON을 반환하는가?
- [ ] 관련 pytest 테스트 통과 확인.
