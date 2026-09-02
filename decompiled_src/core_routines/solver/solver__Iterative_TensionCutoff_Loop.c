/* 
 * AltDP_3rd Decompiled Ground Truth Asset
 * Symbol: Iterative_SolveNonlinearTensionCutoff
 * Source: DgnSolver/Iterative.exe
 * Domain: Foundation Soil-Structure Interaction & Contact FEM
 */

#include <stdbool.h>
#include <math.h>

typedef struct {
    int node_count;
    int element_count;
    double* K_global;       // Global CSR Sparse Stiffness Matrix
    double* P_load;         // External Nodal Load Vector
    double* u_disp;         // Output Displacement Vector [w_i, thx_i, thy_i]
    double* soil_ks;        // Nodal Subgrade Reaction Modulus (kN/m^3)
    bool* spring_active;    // Compression-active mask
} DGN_SOLVER_ITERATIVE_CONTEXT;

bool Iterative_SolveNonlinearTensionCutoff(DGN_SOLVER_ITERATIVE_CONTEXT* ctx, double tolerance, int max_iterations) {
    if (!ctx || ctx->node_count <= 0) return false;

    // 1. Initial State: All soil springs activated (Compressive assumption)
    for (int i = 0; i < ctx->node_count; i++) {
        ctx->spring_active[i] = true;
    }

    bool converged = false;
    for (int iter = 0; iter < max_iterations; iter++) {
        // 2. Assemble Effective Stiffness Matrix: K_eff = K_plate + K_soil(active)
        // 3. Solve Linear System: [K_eff] {u} = {P}
        
        // 4. Tension Check on Soil Reaction: R_i = k_s * w_i
        // Sign convention: w_i < 0 is downward settlement (Compression), w_i > 0 is uplift (Tension)
        int changed_springs = 0;
        for (int i = 0; i < ctx->node_count; i++) {
            double settlement = ctx->u_disp[3 * i]; // Vertical DOF
            bool is_compressive = (settlement <= 0.0);
            
            if (ctx->spring_active[i] != is_compressive) {
                ctx->spring_active[i] = is_compressive;
                changed_springs++;
            }
        }

        // 5. Convergence achieved when no spring state changes
        if (changed_springs == 0) {
            converged = true;
            break;
        }
    }

    return converged;
}
