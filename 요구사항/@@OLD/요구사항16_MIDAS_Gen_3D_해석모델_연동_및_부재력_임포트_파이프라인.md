# 요구사항 16: MIDAS Gen 3D 해석 모델 연동 및 부재력 임포트 파이프라인 (DgnPlugIn)

## 1. 개요 및 목적 (Overview & Goals)

### 1.1. 배경
Midas Design+의 핵심 경쟁력은 3차원 골조 해석 프로그램인 **MIDAS Gen / MIDAS Building**과의 직접 연동 기능입니다 (`DgnPlugIn/` 디렉토리 내 `AnalysisDB.dll`, `GEN_UmdDataBase.dll`, `GEN_DgnCalc_KR.dll` 등). 사용자는 Gen에서 전체 구조해석을 수행한 후, 수만 개의 하중조합 부재력을 일일이 수동 입력하지 않고 파일 임포트를 통해 Design+로 가져와 단면 검토를 수행합니다.

### 1.2. 개발 목적
1. **MIDAS 텍스트 모델/부재력 파일 (`.mgt`) 파서 구축**:
   - `*NODE`, `*ELEMENT`, `*MATERIAL`, `*SECTION`, `*STORY` 키워드 파싱.
   - `*LOAD COMBINATION` 및 `*FORCE-BEAM`, `*FORCE-COLUMN`, `*FORCE-WALL` 텍스트 데이터 추출.
2. **MIDAS SQLite/Access 해석 DB (`.db`, `.mgb`) 파서 구축**:
   - 3D 골조 해석 결과 테이블에서 층별, 부재 번호별, 하중조합별 계수 단면력($P, V_y, V_z, M_y, M_z, T$) 자동 쿼리.
3. **AltDP 부재 매핑 및 최악 하중조건(Governing LCB) 자동 선별**:
   - 추출된 다축 부재력을 AltDP_3rd 부재 모델(`src/engine/rc/`, `steel/`)로 자동 매핑.
   - 각 부재별 최대 DCR을 유발하는 지배 하중조합을 자동 선별하여 일괄 설계 대기열에 등록.

---

## 2. 역공학 참조 자산 및 파이프라인 아키텍처

```mermaid
flowchart TD
    subgraph MIDAS_Assets ["MIDAS Gen / Building 출력 자산"]
        MGT[".mgt 텍스트 모델/명령어 파일"]
        MGB[".mgb / .db 해석 결과 바이너리/DB"]
    end

    subgraph Parser_Layer ["AltDP_3rd 임포트 파서 (src/engine/interop/)"]
        MGT_PARSER["mgt_parser.py<br>(절점/요소/재료/단면/부재력 파서)"]
        MGB_PARSER["mgb_parser.py<br>(해석 DB SQL 쿼리 및 테이블 추출)"]
        MAPPER["governing_lcb.py<br>(지배 하중조건 선별 및 단면 매핑)"]
    end

    subgraph Execution_Layer ["AltDP 일괄 설계 & UI 연동"]
        PROJ_ENG["src/engine/project/project_manager.py"]
        BATCH_RUN["src/engine/project/batch_checker.py"]
        REST_API["src/api/routes/interop.py"]
    end

    MGT --> MGT_PARSER
    MGB --> MGB_PARSER
    MGT_PARSER & MGB_PARSER --> MAPPER
    MAPPER --> PROJ_ENG
    PROJ_ENG --> BATCH_RUN --> REST_API
```

---

## 3. 하위 Phase 분할 로드맵 (Partitioned Phases for `/goal`)

| Phase | 세부 요구사항 문서 | 주요 구현 및 산출물 | 검증 타겟 |
|:---:|---|---|---|
| **Phase 16-1** | [`요구사항16-1_MIDAS_MGT_텍스트스크립트_파서_및_3D모델구축.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항16-1_MIDAS_MGT_텍스트스크립트_파서_및_3D모델구축.md) | `src/engine/interop/mgt_parser.py`, `model_schema.py` | `*NODE`, `*ELEMENT` 파싱, 3D 부재/층 자동 분류 |
| **Phase 16-2** | [`요구사항16-2_부재력_DB_파서_및_최악하중_Governing_LCB_자동선별.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항16-2_부재력_DB_파서_및_최악하중_Governing_LCB_자동선별.md) | `src/engine/interop/mgb_parser.py`, `governing_lcb.py` | 6자유도 부재력 추출, 지배 LCB 자동 필터링 |
| **Phase 16-3** | [`요구사항16-3_Gen연동_REST_API_및_다중부재_일괄설계_파이프라인.md`](file:///f:/PyProject/AltDP_3rd/요구사항/요구사항16-3_Gen연동_REST_API_및_다중부재_일괄설계_파이프라인.md) | `src/api/routes/interop.py`, `batch_checker.py` | 대용량 부재 일괄 설계 API, 층별 요약 JSON |

---

## 4. 검증 및 수용 기준 (Acceptance Criteria)

- [ ] 실제 MIDAS Gen 예제 `.mgt` 파일(절점 1,000개 이상) 파싱 시 0.5초 이내 완료.
- [ ] MIDAS 수동 산출 최악 부재력과 AltDP 자동 추출 최악 부재력 100% 일치 (오차 0.0%).
- [ ] 500개 부재 일괄 단면 검토 실행 시간 2.0초 이내 완료 및 요약 결과 무결성 확인.
- [ ] Pytest 스위트 통과: `tests/engine/test_mgt_parser.py`, `test_governing_lcb.py`, `test_batch_checker.py`, `tests/api/test_interop_routes.py`.
