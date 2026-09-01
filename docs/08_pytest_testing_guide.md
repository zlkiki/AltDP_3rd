# Pytest 도메인별 3대 테스트 가이드 (08_pytest_testing_guide.md)

## 1. 테스트 철학 및 구조

AltDP_3rd는 신속하고 무결한 개발을 위해 테스트 스위트를 **3대 도메인(엔진, API, UI)**으로 분리하여 관리합니다.

```text
tests/
├── conftest.py                     # 공통 픽스처 및 샘플 부재 데이터
├── engine/                         # Layer 1~3 공학 계산 엔진 단위 테스트
│   ├── test_materials.py           # 재료 물성치 및 KDS 계수 검증
│   ├── test_rc_beam.py             # RC 보 휨/전단 강도 계산 검증
│   ├── test_rc_column.py           # RC 기둥 및 P-M 상관도 검증
│   ├── test_rc_footing.py          # 독립기초 펀칭전단 검증
│   ├── test_sdb_parser.py          # .sdb 형강 DB 파싱 검증
│   └── test_steel_beam.py          # 철골보 LTB 및 휨강도 검증
├── api/                            # Layer 4 FastAPI 엔드포인트 테스트
│   ├── test_rc_routes.py           # RC 부재설계 API 요청/응답 검증
│   └── test_steel_routes.py        # 철골 부재설계 API 검증
└── ui/                             # Layer 5 웹 템플릿 및 정적 자산 테스트
    └── test_web_assets.py          # HTML/CSS/JS 정적 라우트 검증
```

---

## 2. 초고속 테스트 실행 치트시트

```bash
# 1. 엔지니어링 계산 엔진만 고속 검증 (0.5초)
pytest tests/engine/

# 2. REST API 엔드포인트만 검증 (0.8초)
pytest tests/api/

# 3. 웹 UI 템플릿 및 자산 검증 (0.3초)
pytest tests/ui/

# 4. 전체 전수 테스트 스위트 실행
pytest
```
