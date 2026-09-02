# 요구사항 09-1: Jinja2 + KaTeX 기반 A4 구조계산서 엔진 및 베이스 프레임워크

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경 및 목적
* Midas Design+의 MFC 기반 `CMSOffice` 및 `CMSWorkRec` 모듈이 수행하던 구조계산서 생성 시스템을 순수 Python 기반(Jinja2 템플릿 엔진 + KaTeX LaTeX 수식 + A4 CSS Paged Media)의 웹 구조계산서 엔진(`src/report/generator.py`)으로 전환합니다.
* 인허가 관청 및 구조감리 제출용 A4 표준 규격(여백 20mm/15mm, 머리글/바닥글, 쪽번호 자동 매김, `.avoid-break`, `.page-break`)을 준수하는 공통 베이스 템플릿(`src/report/templates/base_report.html`)을 구축합니다.
* 공학 수식 전개에 필요한 Jinja2 커스텀 필터(KaTeX LaTeX 렌더링, 소수점/지수 포맷팅, 부재 DCR 색상 배지, 단위 변환기)를 개발하여 일관된 고품질 계산서 기반을 제공합니다.

### 1.2. 참조 Ground Truth 자산
* **디컴파일 소스**:
  - `decompiled_src/DPLUS_RCS.dll_symbols.txt` (`CMSOffice`)
  - `decompiled_src/DPLUS_DGN.dll_symbols.txt` (`CMSWorkRec`)
* **KDS 기준서**: KDS 14 20 00 (콘크리트구조설계기준), KDS 14 31 00 (강구조설계기준) 계산서 표기 규약
* **대상 소스**:
  - [`src/report/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/report/__init__.py)
  - [`src/report/generator.py`](file:///f:/PyProject/AltDP_3rd/src/report/generator.py)
  - [`src/report/templates/base_report.html`](file:///f:/PyProject/AltDP_3rd/src/report/templates/base_report.html)
  - [`tests/report/test_report_generator.py`](file:///f:/PyProject/AltDP_3rd/tests/report/test_report_generator.py)

---

## 2. 계산서 공통 레이아웃 및 CSS Paged Media 규격

### 2.1. A4 인쇄 스타일시트 명세
```css
@page {
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
    @top-left { content: "AltDP_3rd Structural Design Report"; font-size: 8pt; color: #666; font-family: 'Pretendard', sans-serif; }
    @top-right { content: attr(data-project-name); font-size: 8pt; color: #666; font-family: 'Pretendard', sans-serif; }
    @bottom-center { content: "- " counter(page) " -"; font-size: 9pt; font-weight: 500; font-family: 'Pretendard', sans-serif; }
}

@media print {
    body { font-size: 9.5pt; line-height: 1.45; color: #111; }
    .page-break { page-break-before: always; }
    .avoid-break { page-break-inside: avoid; }
    .no-print { display: none !important; }
}
```

### 2.2. 공통 계산서 구성 블록
1. **표지 및 프로젝트 헤더 블록**:
   - 프로젝트명, 구조물 위치, 설계자(Engineered by), 검토자(Checked by), 승인자(Approved by), 계산 일자.
2. **부재 메타데이터 및 설계 개요**:
   - 부재 식별자(Member ID), 부재 유형(Beam, Column, Wall, etc.), 적용 설계 규준(KDS 14 20 / 14 31).
3. **재료 물성치 및 기하 단면 요약 테이블**:
   - 콘크리트 $f_{ck}$, 탄성계수 $E_c$, 철근 $f_y, f_{ys}$, 강재 $F_y, F_u$, 단면 치수($b, h, t_w, t_f, d$).
4. **설계 하중 및 지배 하중조합 (Governing Load Combination)**:
   - 계수 축력($P_u$), 전단력($V_u$), 휨모멘트($M_u$), 비틀림모멘트($T_u$) 및 한계상태별 조합식.
5. **종합 결과 요약 (Executive Summary & Status Banner)**:
   - 전체 DCR 최대치, 주요 지배 검토항목, 최종 판정(PASS - 초록 / FAIL - 빨강).

---

## 3. 대상 파일 및 변경 범위

| 파일 경로 | 상태 | 설명 |
|---|:---:|---|
| [`src/report/__init__.py`](file:///f:/PyProject/AltDP_3rd/src/report/__init__.py) | [NEW] | Report 패키지 초기화 및 주요 인터페이스 노출 |
| [`src/report/generator.py`](file:///f:/PyProject/AltDP_3rd/src/report/generator.py) | [NEW] | `ReportGenerator` 엔진 (Jinja2 환경 설정, 커스텀 수식/DCR 필터, 컨텍스트 바인딩) |
| [`src/report/templates/base_report.html`](file:///f:/PyProject/AltDP_3rd/src/report/templates/base_report.html) | [NEW] | A4 Paged Media 레이아웃, KaTeX 0.16.x CDN, Pretendard 웹폰트, 인쇄 최적화 스타일 |
| [`tests/report/test_report_generator.py`](file:///f:/PyProject/AltDP_3rd/tests/report/test_report_generator.py) | [NEW] | 베이스 템플릿 렌더링, 필터 유효성, A4 CSS 클래스 및 DCR 하이라이트 단위 테스트 |

---

## 4. 구현 및 검증 체크리스트

- [x] `src/report/__init__.py` 및 `src/report/generator.py` 생성
- [x] Jinja2 템플릿 환경 구성 및 KaTeX 수식 필터(`katex_inline`, `katex_block`) 구현
- [x] 공학 수치 포맷팅 필터(`fmt_num`, `fmt_stress`, `fmt_force`, `fmt_moment`, `fmt_dcr`) 구현
- [x] DCR 상태 판정 및 CSS 색상 클래스/배지 매핑 함수 구현
- [x] `src/report/templates/base_report.html` A4 인쇄 표준 템플릿 작성 (머리글/바닥글, 쪽번호, 스타일)
- [x] 프로젝트 메타데이터, 재료 테이블, 하중조건 공통 컨텍스트 바인딩 검증
- [x] `pytest tests/report/test_report_generator.py` 100% 통과 (0.1% 미만 오차 및 렌더링 무결성)
