"""Parser for MIDAS Gen Internal Forces from MGT scripts and SQLite/Access DBs.

Extracts 6-DOF internal forces (P, Vy, Vz, My, Mz, T) across load combinations
and member positions (I, M, J).
"""

from typing import List, Dict, Optional
import sqlite3
import re
from .model_schema import MemberForce


class MidasForceParser:
    """Parser for MIDAS Gen load combinations and member forces."""

    @staticmethod
    def parse_mgt_forces(content: str) -> Dict[int, List[MemberForce]]:
        """Parse internal forces from MGT text content.
        
        Supports *FORCE-BEAM, *FORCE-COLUMN, and *FORCE-WALL sections.
        Returns a mapping of elem_id -> list of MemberForce records.
        """
        forces_by_elem: Dict[int, List[MemberForce]] = {}
        lines = content.splitlines()
        
        current_section = None
        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith(";"):
                continue
            
            # Detect section header
            if line_str.startswith("*"):
                header = line_str.split()[0].upper()
                if header in ("*FORCE-BEAM", "*FORCE-COLUMN", "*FORCE-WALL", "*FORCE"):
                    current_section = "FORCE"
                else:
                    current_section = None
                continue
            
            if current_section == "FORCE":
                # Line format: ELEM_ID, LCB_NAME, PART(I/M/J), Axial(P), Vy, Vz, T, My, Mz
                # or space/comma separated
                parts = [p.strip() for p in re.split(r"[, \t]+", line_str) if p.strip()]
                if len(parts) >= 8:
                    try:
                        elem_id = int(parts[0])
                        lcb_name = parts[1]
                        pos = parts[2].upper()
                        # Some Gen exports have: P, Vy, Vz, T, My, Mz or P, Vy, Vz, My, Mz, T
                        p = float(parts[3])
                        vy = float(parts[4])
                        vz = float(parts[5])
                        if len(parts) >= 9:
                            t = float(parts[6])
                            my = float(parts[7])
                            mz = float(parts[8])
                        else:
                            my = float(parts[6])
                            mz = float(parts[7])
                            t = 0.0
                            
                        record = MemberForce(
                            elem_id=elem_id,
                            lcb_name=lcb_name,
                            position=pos,
                            p=p,
                            vy=vy,
                            vz=vz,
                            my=my,
                            mz=mz,
                            t=t
                        )
                        if elem_id not in forces_by_elem:
                            forces_by_elem[elem_id] = []
                        forces_by_elem[elem_id].append(record)
                    except (ValueError, IndexError):
                        continue

        return forces_by_elem

    @staticmethod
    def parse_sqlite_forces(db_path: str) -> Dict[int, List[MemberForce]]:
        """Parse internal forces from SQLite/MGB database.
        
        Queries BeamForce, ColumnForce, or MemberForce tables if present.
        """
        forces_by_elem: Dict[int, List[MemberForce]] = {}
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check available tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            target_tables = [t for t in ["BeamForce", "ColumnForce", "WallForce", "MemberForce"] if t in tables]
            for table in target_tables:
                cursor.execute(f"SELECT ElemID, LCB, Part, P, Vy, Vz, My, Mz, T FROM {table}")
                rows = cursor.fetchall()
                for row in rows:
                    elem_id, lcb, pos, p, vy, vz, my, mz, t = row
                    rec = MemberForce(
                        elem_id=int(elem_id),
                        lcb_name=str(lcb),
                        position=str(pos).upper(),
                        p=float(p),
                        vy=float(vy),
                        vz=float(vz),
                        my=float(my),
                        mz=float(mz),
                        t=float(t) if t is not None else 0.0
                    )
                    if elem_id not in forces_by_elem:
                        forces_by_elem[elem_id] = []
                    forces_by_elem[elem_id].append(rec)
            conn.close()
        except Exception:
            pass

        return forces_by_elem
