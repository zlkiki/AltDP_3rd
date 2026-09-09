# 요구사항 22-4-1-2: Phase V1-01 Step 4-2 레거시 명칭(redcr) 전면 청산 및 AltDP_3rd 표준 네이밍 리팩토링 명세서

## 1. 개요 및 목적

본 문서는 AltDP_3rd 프론트엔드 및 계산서 모듈에 잔존하는 **타 프로젝트 레거시 고유명사(`redcr`)를 전면 청산**하고, AltDP_3rd의 표준 네이밍 규약(`rc_beam_report`, `report_common_renderer`, `RCBeamReportGenerator`, `window.renderRCBeamReport`, `.altdp-report`)으로 1:1 완벽 대체 및 리팩토링을 완수하기 위한 마이크로 실행 명세서입니다.

* **부재 및 모듈 식별자**: `rc_beam` (카탈로그 No. 1, Tier 1 플래그십)
* **담당 파일**:
  - `src/web/static/js/report/redcr_rc_beam.js` $\rightarrow$ `src/web/static/js/report/rc_beam_report.js` (파일 리네이밍)
  - `src/web/static/js/report/redcr_common_renderer.js` $\rightarrow$ `src/web/static/js/report/report_common_renderer.js` (파일 리네이밍)
  - `src/web/templates/index.html` (엔트리포인트 `<script>` 태그 표준화)
  - `src/web/static/js/core/report_engine.js` (계산서 통합 디스패처 호출부 표준화)
  - `src/web/static/css/report.css` (CSS 선택자 클래스 표준화)
  - `tests/ui/test_phase22_4_rc_beam_report.py` (자체 검증 테스트 스위트 표준화)
* **권장 AI 모델**: ⚙️ **Medium (Fast / Accurate)** - 파일 리네이밍, 식별자 1:1 치환 및 정적 서빙/테스트 검증

---

## 2. 1:1 대체 및 리네이밍 상세 인벤토리

| 구분 | 레거시 타 프로젝트 명칭 (`redcr`) | AltDP_3rd 신규 표준 명칭 | 상세 변경 내용 |
|:---|:---|:---|:---|
| **A4 렌더러 파일** | `src/web/static/js/report/redcr_rc_beam.js` | `src/web/static/js/report/rc_beam_report.js` | 파일 리네이밍 및 내부 클래스/전역함수 표준화 |
| **공통 렌더러 파일** | `src/web/static/js/report/redcr_common_renderer.js` | `src/web/static/js/report/report_common_renderer.js` | 파일 리네이밍 및 공통 헬퍼 클래스 표준화 |
| **렌더러 클래스명** | `class RedcrRcBeamReport` | `class RCBeamReportGenerator` | 표준 리포트 제너레이터 클래스명 적용 |
| **전역 등록 함수** | `window.renderRedcrRCBeamReport` | `window.renderRCBeamReport` | 표준 전역 함수 등록 (`window.renderRCBeamReport`) |
| **공통 렌더러 객체** | `window.RedcrCommonRenderer` | `window.ReportCommonRenderer` | 표준 전역 객체명 |
| **CSS 컨테이너 클래스** | `.redcr-report`, `.redcr-report-container` | `.altdp-report`, `.altdp-report-container` | `report.css` 및 렌더러 HTML 템플릿 동기화 |
| **HTML 스크립트 로드** | `<script src="/static/js/report/redcr_rc_beam.js">`<br>`<script src="/static/js/report/redcr_common_renderer.js">` | `<script src="/static/js/report/rc_beam_report.js">`<br>`<script src="/static/js/report/report_common_renderer.js">` | `index.html` 태그 변경 |
| **디스패처 호출부** | `report_engine.js` 내 `renderRedcrRCBeamReport` | `report_engine.js` 내 `renderRCBeamReport` | 표준 함수 호출로 교체 |
| **단위 테스트 스위트** | `tests/ui/test_phase22_4_rc_beam_report.py` | `tests/ui/test_phase22_4_rc_beam_report.py` | 테스트 함수 및 문자열 검증부 표준화 |

*(주의: `src/web/static/js/report/redcr/` 하위 모듈 폴더는 타 부재 순차 마이그레이션 시 자체 모듈로 단계적 흡수 예정이므로 본 Phase에서는 `rc_beam` 관련 상위 파일 2종 및 연동부를 집중 청산)*

---

## 3. 세부 수정 및 연동 지침

### 3.1. 파일 리네이밍
- `src/web/static/js/report/redcr_rc_beam.js`를 `src/web/static/js/report/rc_beam_report.js`로 이동.
- `src/web/static/js/report/redcr_common_renderer.js`를 `src/web/static/js/report/report_common_renderer.js`로 이동.

### 3.2. `rc_beam_report.js` 내부 심볼 변경
```javascript
// 기존
class RedcrRcBeamReport { ... }
window.renderRedcrRCBeamReport = function(data, options) { ... };

// 변경
class RCBeamReportGenerator { ... }
window.renderRCBeamReport = function(data, options) {
    const generator = new RCBeamReportGenerator(data, options);
    return generator.render();
};
```

### 3.3. `index.html` 내 스크립트 태그 동기화
```html
<!-- AS-IS -->
<script src="/static/js/report/redcr_common_renderer.js"></script>
<script src="/static/js/report/redcr_rc_beam.js"></script>

<!-- TO-BE -->
<script src="/static/js/report/report_common_renderer.js"></script>
<script src="/static/js/report/rc_beam_report.js"></script>
```

### 3.4. `report_engine.js` 디스패처 동기화
```javascript
// AS-IS
if (typeof window.renderRedcrRCBeamReport === 'function') {
    return window.renderRedcrRCBeamReport(memberData, options);
}

// TO-BE
if (typeof window.renderRCBeamReport === 'function') {
    return window.renderRCBeamReport(memberData, options);
}
```

---

## 4. 단위 테스트 명세 (`tests/ui/test_phase22_4_rc_beam_report.py`)

1. **`test_rc_beam_report_js_serving`**:
   - `GET /static/js/report/rc_beam_report.js`가 HTTP 200으로 정상 서빙되는지 검증.
   - `RCBeamReportGenerator`, `window.renderRCBeamReport` 식별자가 포함되어 있는지 검증.
2. **`test_index_html_contains_rc_beam_report`**:
   - `index.html`에 `<script src="/static/js/report/rc_beam_report.js"></script>` 태그가 존재하는지 검증.
3. **`test_report_engine_delegates_to_rc_beam_report`**:
   - `report_engine.js`가 `window.renderRCBeamReport`를 호출하도록 위임되어 있는지 검증.
4. 기존 7대 단위 테스트 전수 검증:
   - `pytest tests/ui/test_phase22_4_rc_beam_report.py` 실행 시 7 passed (100% 통과) 확인.

---

## 5. 완료 검증 기준 (DoD)

- [x] `redcr_rc_beam.js` 및 `redcr_common_renderer.js` 파일이 `rc_beam_report.js`, `report_common_renderer.js`로 완전히 리네이밍될 것.
- [x] `index.html`, `report_engine.js`, `report.css` 내 레거시 명칭이 AltDP_3rd 표준 명칭으로 전면 교체될 것.
- [x] `tests/ui/test_phase22_4_rc_beam_report.py` 단위 테스트 7개가 100% 무결점 통과할 것.
- [x] 전체 회귀 테스트 `pytest` 349+ 통과를 유지할 것 (현재 352/352 100% 통과).
