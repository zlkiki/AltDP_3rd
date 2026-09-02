# 요구사항 12-1: Ghidra 솔버 인터페이스 핀포인트 추출 및 Ground Truth 자산화

## 1. 개요 및 목적 (Overview)
본 단계는 Midas Design+의 FEM 해석 및 외부 솔버 연동과 관련된 핵심 인터페이스 4대 루틴을 Ghidra로 핀포인트 디컴파일하여 C 수도코드 및 구조체 메타데이터를 `decompiled_src/core_routines/solver/`에 Ground Truth 자산으로 등록하는 작업입니다.

---

## 2. 세부 추출 대상 및 분석 범위

1. **`DPLUS_DB.dll`**:
   - `CDBSolverTool::ConvertToCurrentUnit`
   - `CDBManagerTool::ConvertModel_Plate`
   - 입출력 구조체: `DGNFES_NODE`, `DGNFES_PLATE`, `DGNFES_PLATE_FORCE`, `DGNFES_REACTION`
2. **`DgnSolver/Iterative.exe`**:
   - 지반 인장 분리(Tension Cut-off) 수렴 판정 기준 ($\epsilon \le 10^{-4}$), 강성 행렬 갱신 조건
3. **`DPLUS_STEEL.dll`**:
   - `CUSBPPModeDlg::OnCheckPreviewMeshLine` 및 `CESBPPModeDlg::HideRowEAMFEM`
   - 콘크리트 등가 지압 스프링 계수 수식 ($k_{conc} = E_c / t_{eff}$ 또는 $k_s$)
4. **`DPLUS_RCS.dll`**:
   - `CURBUPModeDlg` / `CURBWPModeDlg`
   - 지하외벽 2방향 하중 재하 및 다층 지지 경계조건 매핑

---

## 3. 핵심 산출물 (Deliverables)

```text
decompiled_src/core_routines/solver/
├── solver__CDBSolverTool_ConvertModel_Plate.c
├── solver__CDBSolverTool_ConvertModel_Plate.json
├── solver__Iterative_TensionCutoff_Loop.c
├── solver__Iterative_TensionCutoff_Loop.json
├── solver__CUSBPPModeDlg_BasePlate_Spring.c
├── solver__CUSBPPModeDlg_BasePlate_Spring.json
├── solver__CURBUPModeDlg_Wall_Boundary.c
└── solver__CURBUPModeDlg_Wall_Boundary.json

decompiled_src/core_routines/README.md  # 메타데이터 인덱스 갱신
```

---

## 4. 완료 및 수용 기준 (Checklist)
- [x] Ghidra 12.1.3 및 `scripts/ghidra_extract.py`를 활용하여 4대 핵심 루틴 디컴파일 완료
- [x] C 수도코드 파일 4종 및 JSON 메타데이터 파일 4종 생성
- [x] `decompiled_src/core_routines/README.md` 총괄 인덱스에 색인 반영 완료

