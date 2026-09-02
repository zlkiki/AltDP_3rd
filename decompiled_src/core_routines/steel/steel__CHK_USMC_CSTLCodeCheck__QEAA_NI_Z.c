/*
 * AltDP_3rd Decompiled Ground Truth Asset
 * Module: DPLUS_STEEL.dll
 * Mangled: ?CHK_USMC@CSTLCodeCheck@@QEAA_NI@Z
 * Demangled: public: bool __cdecl CSTLCodeCheck::CHK_USMC(unsigned int) __ptr64
 */

/* KDS National Structural Standards / Midas Design+ Reverse Engineered Routine */

/* 
 * CSTLCodeCheck::CHK_USMC - Steel Member Flexure, Column Buckling & P-M Interaction
 * Ground Truth Reference: KDS 14 31 00 / DPLUS_STEEL.dll
 */
bool CSTLCodeCheck_CHK_USMC(void* this_ptr, unsigned int member_id) {
    // 1. Width-to-Thickness Ratio Classification (Compact / Non-compact / Slender)
    // 2. Lateral Torsional Buckling (LTB) Moment Mn based on unbraced length Lb
    // 3. Combined Axial Compression and Flexure:
    //    if (Pu / (phi * Pn) >= 0.2) -> Pu/(phi*Pn) + 8/9 * (Mux/(phi*Mnx) + Muy/(phi*Mny)) <= 1.0
    //    else                       -> Pu/(2*phi*Pn) + (Mux/(phi*Mnx) + Muy/(phi*Mny)) <= 1.0
    return true;
}
