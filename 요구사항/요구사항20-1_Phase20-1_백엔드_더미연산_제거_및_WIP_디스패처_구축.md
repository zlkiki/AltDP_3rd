# 요구사항 20-1: Phase 20-1 백엔드 더미연산 전면 제거 및 WIP 디스패처 구축 명세서

## 1. 개요 및 목적 (Background & Objectives)
* **상위 기술 문서(SSOT)**:
  - [`요구사항 20 (Phase 20 마스터)`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항20_Phase20_더미코드_전면제거_및_정직한_WIP_베이스라인_구축.md) 제3.1절 및 제5절
  - [`docs/01_system_architecture.md`](file:///f:/PyProject/AltDP_3rd/docs/01_system_architecture.md) (REST API 디스패처 계층)
  - [`docs/10_agent_development_protocols.md`](file:///f:/PyProject/AltDP_3rd/docs/10_agent_development_protocols.md) (오차 $\le 0.10\%$ 무결성 및 Proof-First Mandate)
  - [`docs/12_full_feature_porting_master_plan.md`](file:///f:/PyProject/AltDP_3rd/docs/12_full_feature_porting_master_plan.md) (Phase 1~6 기완료 엔진 100% 보호)
* **목적**: 시스템 전반(엔진, 라우트, 디스패처)에 잠재된 **기만적 가짜 숫자(Mock/Stub 강도값, 임의의 150/100, DCR=0.8, 가짜 OK 판정)를 전면 척결**하고, `docs/12`에서 이미 검증 완료된 KDS 엔진은 철저히 보호하면서, 아직 전용 스키마 및 UI 연동이 완비되지 않은 모듈 요청 시 일관되고 정직한 **표준 `WIPResponse`(`NOT_YET_IMPLEMENTED`)**를 반환하는 중앙 백엔드 디스패치 인프라를 구축합니다.

---

## 2. 세부 개발 사양 (Detailed Specifications)

### 2.1. 표준 Pydantic WIP 응답 스키마 구현
* **구현 파일**: `src/api/models/wip.py` (또는 `src/api/routes/dispatch.py`)
* **스키마 정의**:
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class WIPModuleDetail(BaseModel):
    key: str                    # 예: "rc/wall/rc_basement_wall"
    name: str                   # 예: "RC 지하외벽 (Basement Wall)"
    midas_dlg: str              # 예: "IDD_RCS_BASEMENT_WALL_DLG" (docs/13)
    category: str               # "rc", "steel", "src", "alu", "rfm", "fem"
    group: str                  # "wall", "beam", "column", "footing", "conn"
    domain: str                 # "RC", "STEEL", "SRC", "ALU"
    tier: str                   # "Tier 1", "Tier 2", "Tier 3"
    standard: str               # "KDS 14 20 40 : 2022"
    engine_status: str          # "VERIFIED" (엔진완료) | "WIP" (엔진준비중)
    notice: str = "Midas Design+ 1:1 서브탭 및 VDraw 드로잉 명세에 따라 전용 폼과 계산서가 순차 탑재됩니다."

class WIPResponse(BaseModel):
    success: bool = False
    status: str = "NOT_YET_IMPLEMENTED"
    code: str = "WIP_MODULE"
    message: str
    module: WIPModuleDetail
```

### 2.2. 중앙 디스패처 (`src/api/routes/dispatch.py`) WIP 핸들러 연결
* **엔드포인트**: `POST /api/design/{category}/{group}/{module_id}`
* **동작 사양**:
  1. `get_module(category, group, module_id)`를 조회하여 등록 여부 확인.
  2. 등록된 모듈의 `calculate` 함수가 실제 구현체가 아닌 더미(Mock)이거나 아직 연동 준비 중(WIP)인 경우:
     - 404나 500 에러를 던지지 않고, `WIPResponse`를 정직하게 반환.
     - 가짜 강도치(`phi_mn=150`, `phi_vn=100`, `dcr=0.8`) 임의 산출 코드를 100% 영구 삭제.
  3. **`docs/12` 기완료 검증 엔진 보호**:
     - `src/engine/rc/beam.py` (보 휨/전단/처짐)
     - `src/engine/rc/column.py` (기둥 3D P-M)
     - `src/engine/rc/wall.py` (전단벽)
     - `src/engine/rc/footing.py` (독립기초)
     - `src/engine/steel/beam.py` (철골보 LTB)
     - `src/engine/fem/` (5대 FEM 부재: 매트기초, 2방향 지하외벽, 주각부, 엔드플레이트, 슬래브)
     - 상기 이미 오차 $\le 0.10\%$ 검증이 완료된 엔진들의 KDS 수치 연산 결과는 100% 온전하게 반환 보장.

---

## 3. 세부 작업 5단계 공정 (Step 1 ~ Step 5)

1. **Step 1 [High]**: `src/api/routes/dispatch.py` 및 관련 라우트 내 임의 기본값 및 잠재 더미 연산 블록 전수 색출 및 삭제.
2. **Step 2 [Medium]**: `WIPModuleDetail`, `WIPResponse` Pydantic 모델 정의 및 직렬화 검증.
3. **Step 3 [Medium]**: 미연동/WIP 모듈 요청 시 `WIPResponse`를 안전하게 반환하는 분기 라우팅 완성.
4. **Step 4 [High]**: `docs/12` 기완료 엔진(RC 보/기둥/기초, 철골 보/기둥, 5대 FEM 등)과의 통합 응답 포맷 일관성 및 회귀 검증.
5. **Step 5 [Medium]**: `tests/api/test_wip_dispatch.py` 작성 및 `pytest` 100% PASS 검증 (Exit Code 0).

---

## 4. 완료 검증 기준 (Acceptance Criteria)
* 미연동 모듈 엔드포인트 호출 시 HTTP 200과 함께 `status: "NOT_YET_IMPLEMENTED"` JSON이 정상 반환될 것.
* 백엔드 코드 베이스 전역에 가짜 강도/DCR 하드코딩 숫자가 0건일 것.
* `docs/12` 기완료 검증 엔진 14종의 계산 오차 $\le 0.10\%$ 무결성이 일체의 회귀 결함 없이 유지될 것.
* `pytest tests/api/test_wip_dispatch.py` 및 기존 `test_dispatch_api.py`가 100% 통과할 것.
