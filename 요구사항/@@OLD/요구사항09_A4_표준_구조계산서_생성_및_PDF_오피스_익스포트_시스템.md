# 요구사항 09: A4 표준 구조계산서 생성 및 PDF/오피스 익스포트 시스템

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
구조설계 소프트웨어의 최종 산출물은 인허가 관청 및 감리자에게 제출되는 **A4 표준 구조계산서(Structural Calculation Report)**입니다. Midas Design+는 MFC 기반의 `CMSOffice`, `CMSExcel`, `CMSWorkRec` 모듈을 통해 MS Word 및 Excel 형식으로 계산서를 출력했습니다.

### 1.2. 목적
1. 원본 C++ `CMSOffice` 심볼군의 수식 전개 포맷과 계산서 레이아웃을 순수 Python 기반(Jinja2 + KaTeX LaTeX + CSS Paged Media / WeasyPrint)의 웹 구조계산서 엔진(`src/report/generator.py`)으로 전환.
2. 부재별 설계 개요, 적용 KDS 기준, 재료 물성치, 공학 수식 전개 과정(기호 수식 $\rightarrow$ 변수 대입 $\rightarrow$ 계산 결과 $\rightarrow$ 허용치 판정/DCR), 2D 배근 단면도 및 3D P-M 차트를 완벽히 임베딩.
3. 웹 화면 즉시 조회, A4 원클릭 브라우저 인쇄(Page-break 방지, 머리글/바닥글, 쪽번호 자동 매김) 및 PDF/Excel 익스포트 기능 제공.

---

## 2. 계산서 구성 표준 및 템플릿 규격

### 2.1. A4 계산서 섹션 구성 표준
1. **표지 및 프로젝트 정보 (Header & Project Info)**:
   - 프로젝트명, 부재 번호, 설계자/검토자, 적용 기준 (KDS 14 20 00 / 14 31 00), 설계 일자.
2. **단면 기하 및 재료 물성치 요약 (Section & Materials)**:
   - 콘크리트 $f_{ck}$, 철근 $f_y$, 강재 $F_y$, 단면 치수 표 및 2D 단면 형상 그래픽.
3. **설계 하중 및 하중조합 (Design Loads & Load Combinations)**:
   - 계수 축력($P_u$), 전단력($V_u$), 휨모멘트($M_u$), 지배 하중조합 명시.
4. **상세 설계 및 검토 과정 (Step-by-Step Verifications with $\LaTeX$)**:
   - 휨 설계: $\phi M_n \ge M_u$ (기호식, 대입값, DCR 표기)
   - 전단/비틀림: $\phi V_n \ge V_u, \phi T_n \ge T_u$
   - 사용성: 처짐 $\Delta \le L/240$, 균열폭 $w \le w_{lim}$
5. **종합 결과 요약 (Design Summary & OK/NG 판정)**:
   - 부재 검토 항목별 DCR 및 최종 적합 여부(PASS/FAIL) 색상 하이라이트.

### 2.2. CSS Paged Media 인쇄 규격
```css
@page {
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
    @top-center { content: "AltDP_3rd 구조계산서 - " attr(data-member-id); font-size: 9pt; }
    @bottom-right { content: counter(page) " / " counter(pages); font-size: 9pt; }
}
.page-break { page-break-before: always; }
.avoid-break { page-break-inside: avoid; }
```

---

## 3. C 수도코드 / 바이너리 Ground Truth 매핑

| 기능 도메인 | 원본 모듈 및 심볼 레퍼런스 | 역할 및 변환 사양 |
|---|---|---|
| **Office 문서 생성** | `DPLUS_RCS.dll` (`CMSOffice`) | 구조계산서 페이지 분할, 테이블 생성, 텍스트 포맷팅 |
| **Excel 익스포트** | `DGN_lib.dll` (`CMSExcel`) | 부재 검토 결과 및 하중조합 데이터 스프레드시트 덤프 |
| **수식/결과 기록기** | `DGN_lib.dll` (`CMSWorkRec`) | 계산 단계별 중간값 및 수식 문자열 로깅 |

---

## 4. Python & Web 신규 구현 아키텍처

```text
src/
├── report/
│   ├── __init__.py
│   ├── generator.py           # Jinja2 템플릿 바인딩 및 HTML/PDF 생성기
│   ├── excel_exporter.py      # openpyxl 기반 Excel 계산서 익스포터
│   └── templates/
│       ├── base_report.html   # A4 공통 인쇄 레이아웃 & KaTeX 수식 스타일
│       ├── rc_beam_report.html
│       ├── rc_column_report.html
│       ├── steel_member_report.html
│       └── connection_report.html
```

---

## 5. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 09-1** | `요구사항09-1_Jinja2_KaTeX_기반_A4_구조계산서_엔진.md` | `src/report/generator.py`, `templates/base_report.html`, `test_report_generator.py` | A4 HTML 계산서 생성 및 LaTeX 수식 |
| **Phase 09-2** | `요구사항09-2_부재별_상세_계산서_템플릿_및_그래픽임베딩.md` | `rc_beam_report.html`, `rc_column_report.html`, 차트/단면 SVG 임베딩 | 2D/3D 벡터 그래픽 임베딩 및 DCR |
| **Phase 09-3** | `요구사항09-3_PDF_변환_및_Excel_스프레드시트_익스포트.md` | `src/report/excel_exporter.py`, WeasyPrint/Print CSS, API 엔드포인트 | 원클릭 인쇄, PDF 렌더링, Excel 다운로드 |

---

## 6. 검증 및 수용 기준 (Acceptance Criteria)

- [x] **A4 인쇄 레이아웃 무결성**: 브라우저 인쇄 미리보기 시 테이블/수식 잘림(Page-break 에러) 없이 완벽한 A4 정렬.
- [x] **수식 전개 정밀도**: 기호식부터 최종 안전율까지 $\LaTeX$ 수식이 깨짐 없이 선명하게 렌더링.
- [x] **Pytest 스위트 통과**: `pytest tests/report/test_report_generator.py test_excel_exporter.py` (100% 통과).
