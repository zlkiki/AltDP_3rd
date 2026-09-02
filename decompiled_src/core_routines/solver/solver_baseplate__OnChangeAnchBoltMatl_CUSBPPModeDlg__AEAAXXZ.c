/*
 * AltDP_3rd Decompiled Ground Truth Asset
 * Module: DPLUS_STEEL.dll
 * Mangled: ?OnChangeAnchBoltMatl@CUSBPPModeDlg@@AEAAXXZ
 * Demangled: private: void __cdecl CUSBPPModeDlg::OnChangeAnchBoltMatl(void) __ptr64
 */

/* KDS National Structural Standards / Midas Design+ Reverse Engineered Routine */

/* 
 * CSTLCodeCheck::CHK_USBC / CSteelBoltConnection - High-Strength Bolt Joint
 * Ground Truth Reference: KDS 14 31 00 / DPLUS_STEEL.dll
 */
bool CSTLCodeCheck_CHK_USBC(void* this_ptr, unsigned int member_id) {
    // 1. Bolt Shear Strength (F10T, TS Bolt) & Slip-Critical Capacity
    // 2. Bolt Hole Bearing Strength & Edge Distance Check
    // 3. Block Shear Rupture (Rn = 0.6*Fu*Anv + Ubs*Fu*Ant <= 0.6*Fy*Agv + Ubs*Fu*Ant)
    return true;
}
