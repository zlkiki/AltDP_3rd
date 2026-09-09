# 요구사항 22: Phase V1-1 RC 보 (rc_beam) 수직 관통 마스터 명세서

## 1. 개요 및 61종 마스터플랜 매핑 (Master Plan Alignment)

### 1.1. 모듈 개요 및 SSOT 매핑
본 문서는 **[`docs/04_master_original_app_modules_comprehensive_catalog.md`](../docs/04_master_original_app_modules_comprehensive_catalog.md)**(61종 전수 모듈 인벤토리) 및 **[`docs/12_full_feature_porting_master_plan.md`](../docs/12_full_feature_porting_master_plan.md)**(Phase V1~V6 수직 포팅 마스터플랜)에 따라, 최우선 기반 부재군인 **Tier 1 플래그십 핵심 부재 No. 1**인 **RC 보 (`rc_beam`)**를 6대 공정(Step 1~6)으로 수직 관통(Vertical Slice)하여 100% 작동 가능한 상용 엔지니어링 웹 모듈로 완성하기 위한 **총괄 마스터 명세서**입니다.

* **모듈 식별자**: `rc_beam` (카탈로그 번호 No. 1, Tier 1 플래그십)
* **4대 포팅 참조 우선순위 (SSOT Hierarchy)**:
  1. `[1순위 추출 소스]`: `decompiled_src/core_routines/rc/` (`rc__CHK_BBBE_*.c`, `CHK_BBBE_beam.c`, `DPLUS_RCS.dll`, `symbols/DPLUS_RCS.dll_symbols.txt`)
  2. `[2순위 원본 리소스]`: `original_src/Midas Design+/Language/Korean/` (`DLG_DPLUS_RCS.ini`, `Menu.ini`, 원본앱 공식 기술 매뉴얼 보 편)
  3. `[3순위 학회 예제집]`: `F:/PyProject/KCSC2MD/output/예제집/` (한국콘크리트학회 2020 콘크리트구조설계기준 예제집 `3.1 단철근/복철근 휨/Branson 처짐`, `3.2 균열 철근간격`, `4.1 전단설계`, `4.3 비틀림`, 오류 시 Patch-First 선 치유 원칙)
  4. `[4순위 국가건설기준]`: `F:/PyProject/KCSC2MD/output/kds_md/` (KDS 14 20 10 재료/일반, KDS 14 20 20 휨/연성, KDS 14 20 22 전단/비틀림, KDS 14 20 30 사용성, 오류 시 Patch-First 선 치유 원칙)

---

## 2. 6대 마이크로 공정 하위 요구사항 세분화 인덱스 (`docs/16` 규약 연동)

본 마스터 요구사항은 `docs/10` 제2절(Scope Partitioning) 및 `docs/16`(Goal 마이크로 공정 표준 실행 지침)에 따라 **단일 책임과 독립 실행이 가능한 6개의 세부 하위 명세서(Step 1 ~ Step 6)**로 분할되어 관리됩니다.
특히 수치 오차 $\le 0.10\%$ 검증 및 방대한 KaTeX 수식 전개식이 요구되는 **Step 1, Step 4, Step 5는 High 모델(Thinking 모드)**로 전담하고, 브라우저 DOM/Canvas 그래픽스 및 E2E 조작 중심의 **Step 2, Step 3, Step 6은 Medium 모델**로 역할 분담하여 토큰 낭비와 컨텍스트 누락을 원천 차단합니다:

| 공정 단계 | 상태 | 권장 AI 모델 | 하위 명세서 링크 | 핵심 산출물 및 주요 업무 | DoD 검증 기준 |
|:---:|:---:|:---:|---|---|:---:|
| **Step 1** | [x] 완료 | 🧠 **High** | [**요구사항 22-1**](요구사항22-1_PhaseV1_01_Step1_RC보_KDS계산엔진_및_Pydantic스키마.md) | • KDS 14 20 20/22/30 보 해석 엔진 (`src/engine/rc/beam.py`)<br>• 단/복철근 및 T형 플랜지 등가응력블록 휨 수렴 해석<br>• 전단($V_c, V_s$), 비틀림($T_{cr}, T_n, A_l$), Branson $I_e$ 장단기 처짐 | `pytest` 100% PASS<br>(오차 $\le 0.10\%$) |
| **Step 2** | [x] 완료 | ⚙️ **Medium** | [**요구사항 22-2**](요구사항22-2_PhaseV1_01_Step2_RC보_원본앱_1대1_서브탭_입력폼_및_모달.md) | • 원본앱 `IDD_RCS_BEAM_PMODE_DLG` 1:1 서브탭 폼 (`form_rc_beam.js`)<br>• 원본앱 3버튼 툴바(`[💾적용] [⚡검토] [✨자동설계]`) 연동<br>• 적용: 메모리 저장 및 캔버스 갱신, 검토: 클릭 시에만 계산서/DCR 갱신, 자동설계: KDS 최적배근 산출<br>• 단부(I/J)/중앙(M) 배근 테이블 및 스터럽 입력, 테마/너비반응형 래핑 | 브라우저 DOM 정상<br>콘솔 에러 0건<br>3버튼 파이프라인 무결성 |
| **Step 3** | [x] 완료 | ⚙️ **Medium** | [**요구사항 22-3**](요구사항22-3_PhaseV1_01_Step3_RC보_2D_VDraw_캔버스_배근도_및_부재력도_인터랙션.md) | • 상단 뷰포트: 보 경간($L$) 종단면 배근도 & $M/V$ 부재력 포락선<br>• 하단 뷰포트: 단부 I, 중앙 M, 단부 J 3개 횡단면도, 135° 갈고리 스터럽<br>• 피복 옵셋, 치수선, 철근태그, 휠 줌/팬/Fit/호버 툴팁 | Canvas 그래픽스 렌더링<br>인터랙션 무결성 |
| **Step 4** | [x] 완료 | 🧠 **High** | [**요구사항 22-4**](요구사항22-4_PhaseV1_01_Step4_RC보_A4_5대장구분_8단계_KaTeX_구조계산서.md)<br>([**4-1-1**](요구사항22-4-1-1_PhaseV1_01_Step4_1_RC보_KDS철근비현행화_및_3Station휨전단엔진.md) \| [**4-1-2**](요구사항22-4-1-2_PhaseV1_01_Step4_2_redcr_잔재청산_및_표준네이밍_리팩토링.md)<br>\| [**4-1-3**](요구사항22-4-1-3_PhaseV1_01_Step4_3_RC보_원본대조_배근유형_및_주근분리입력_UI개편.md) \| [**4-1-4**](요구사항22-4-1-4_PhaseV1_01_Step4_4_RC보_A4계산서_3Station_개별KaTeX출력_및_E2E통합검증.md)) | • 원본 5대 장구분 계승 및 3-Station 개별 KaTeX 계산근거 출력 (`rc_beam_report.js`)<br>• KDS 14 20 20: 2022 철근비 기준 현행화 ($\phi M_n \ge 1.2 M_{cr}, \epsilon_t \ge \epsilon_{t,\min}$)<br>• `redcr_` 레거시 청산 및 표준 네이밍 리팩토링<br>• 배근유형 3종 옵션 및 `[개수]+[-]+[호칭경]` 복합 분리입력 UI 개편 | A4 인쇄 레이아웃<br>KaTeX 수식 무결성<br>349+ 회귀 테스트 PASS |
| **Step 5** | [ ] 대기 | 🧠 **High** | [**요구사항 22-5**](요구사항22-5_PhaseV1_01_Step5_RC보_기준검토_계산서_캔버스_입력폼_정밀개선_명세서.md)<br>([**5-1**](요구사항22-5-1_PhaseV1_01_Step5_1_RC보_KDS사용성_Ie처짐_균열smax_엔진확장.md) \| [**5-2**](요구사항22-5-2_PhaseV1_01_Step5_2_RC보_12포인트순간격_부재력disabled_캔버스버그패치_UI개편.md)<br>\| [**5-3**](요구사항22-5-3_PhaseV1_01_Step5_3_RC보_A4계산서_제3장연성검토신설_KaTeX줄바꿈_0하중생략.md) \| [**5-4**](요구사항22-5-4_PhaseV1_01_Step5_4_RC보_22-5_정밀개선_E2E통합검증_및_회귀테스트.md)) | • 기준검토 위치 이동(제 3장 단면 연성/최소철근량 신설) 및 KaTeX aligned 줄바꿈<br>• 지점/배근유형별 Branson $I_e$ 가중평균 처짐 및 균열방지 철근간격 $s \le s_{\max}$ 검토<br>• 0하중 동적 생략, 캔버스 표피 0개 버그 수정, 12포인트 순간격 전수 검토<br>• 배근유형 연동 부재력 disabled 동기화, Sticky 플로팅 바 & 32px 컴팩트 버튼 | 12개 정밀개선 완료<br>오버플로우 0건<br>테스트 100% PASS |
| **Step 6** | [ ] 대기 | ⚙️ **Medium** | [**요구사항 22-6**](요구사항22-6_PhaseV1_01_Step6_RC보_4열통합_E2E검증_및_실사용UI_온라인전환.md) | • 4-Pane(사이드바-Left-Sub(부재/폼)-중앙그래픽-순백색A4계산서) 100ms 통합<br>• 파라미터 수정 $\rightarrow$ 캔버스 30ms, [검토] $\rightarrow$ A4 계산서 100ms 동기화<br>• `catalog.js`에서 `rc_beam`의 `is_wip: false`, `status: "Online"` 정식 전환<br>• 브라우저 6대 시나리오 E2E 통합 테스트 및 콘솔 에러 0건 검증 | E2E 전수 테스트 PASS<br>WIP 완전 청산<br>콘솔 에러 0건 |

---

## 3. 실행 및 커맨드 가이드 (`docs/16` 준수)

사용자 및 에이전트는 아래의 표준 명령어를 통해 각 Step을 독립적으로 안전하게 실행합니다:

```markdown
# [Step 5-1: KDS 사용성(처짐 Ie & 균열 s_max) 엔진 확장 단독 실행 - High 모델 권장]
/goal docs 16 확인하고 요구사항 22와 22-5-1을 구현해줘

# [Step 5-2: 12포인트 순간격 검토, 부재력 disabled, 캔버스 버그 패치 UI 개편 - Medium 모델 권장]
/goal docs 16 확인하고 요구사항 22와 22-5-2를 구현해줘

# [Step 5-3: A4 계산서 제 3장 연성검토 신설, KaTeX 줄바꿈, DCR 전수화 - High 모델 권장]
/goal docs 16 확인하고 요구사항 22와 22-5-3을 구현해줘

# [Step 5-4: 12개 정밀개선 E2E 통합 검증 및 회귀 테스트 - High/Medium 모델 권장]
/goal docs 16 확인하고 요구사항 22와 22-5-4를 구현해줘

# [Step 6: 4-Pane 통합 E2E 검증 및 온라인 정식 오픈 단독 실행 - Medium 모델 권장]
/goal docs 16 확인하고 요구사항 22와 22-6의 Step 6을 구현해줘
```

---

## 4. 마스터 종합 검증 및 수용 기준 (Acceptance Criteria)

- [x] **[Step 1 수치 무결성]**: `tests/engine/test_rc_beam.py` 100% 통과 (콘크리트학회 예제집 3.1, 4.1, 4.3, 6.1 대비 오차 $\le 0.10\%$).
- [x] **[Step 2 입력폼 1:1]**: 원본앱 `IDD_RCS_BEAM_PMODE_DLG` 4대 서브탭(단면/재료, 철근배근, 부재력, 사용성) 및 상세 배근 모달 정상 렌더링.
- [x] **[Step 3 2D 캔버스]**: **동적 가변 세로 3단 뷰포트** (1단: 단부(i), 2단: 중앙(m), 3단: 단부(j) 독립 횡단면 배근도 & 135° 내진갈고리 스터럽, 다단배근, 피복선, 치수선 렌더링, 잔존 종단면 배근선 제거).
- [x] **[Step 4 A4 계산서 & 하위 고도화]**: 3-Station 개별 KaTeX 수식 전개, KDS 현행 철근비($\phi M_n \ge 1.2 M_{cr}, \epsilon_t \ge \epsilon_{t,\min}$) 적용, `redcr_` 네이밍 청산, 배근유형 3종 및 주근 복합 분리입력(`[개수]+[-]+[호칭경]`) 완비.
- [ ] **[Step 5 정밀 개선]**: 최소철근/연성 검토 위치 제 3장 이동, KaTeX `aligned` 줄바꿈 오버플로우 0건, 지점별 Branson $I_e$ 처짐, 균열 $s_{\max}$, 표피철근 0개 캔버스 버그 패치, 12포인트 순간격 검토, 부재력 disabled 동기화, Sticky 플로팅 바 & 32px 컴팩트 버튼.
- [ ] **[Step 6 4-Pane 통합 및 온라인 전환]**: 폼 조작 $\rightarrow$ 캔버스 30ms, [검토] $\rightarrow$ 4열 A4 계산서 100ms 이내 실시간 동기화, 콘솔 에러 0건, `is_wip: false` 정식 온라인 전환.
- [ ] **[증거 제출 규약]**: `docs/16`에 따른 4대 물리적 증거(원본 발췌, 3자 오차표, raw 로그, git diff) 첨부 및 단위 Git 커밋/푸시 완료.
