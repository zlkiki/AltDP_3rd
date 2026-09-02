"""Section Database Manager (SQLite In-Memory & Caching) for AltDP_3rd.

Provides fast querying, filtering, and caching of steel section profiles
from parsed .sdb files across 33 international standards.
"""

import os
import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

from src.engine.db.sdb_parser import SDBParser, SectionRecord


class SectionDBManager:
    """Manages steel section databases with in-memory SQLite backend."""

    DEFAULT_DB_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "original_src", "Midas Design+", "Dbase")
    )

    def __init__(self, db_dir: Optional[str] = None):
        self.db_dir = db_dir or self.DEFAULT_DB_DIR
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self._loaded_dbs: set = set()

    def _init_tables(self) -> None:
        """Create database tables for section properties."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_name TEXT NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                H REAL,
                B REAL,
                tw REAL,
                tf REAL,
                r REAL,
                A REAL,
                Ix REAL,
                Iy REAL,
                rx REAL,
                ry REAL,
                Zx REAL,
                Zy REAL,
                Sx REAL,
                Sy REAL,
                J REAL,
                Cw REAL,
                weight REAL,
                UNIQUE(db_name, name)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sec_name ON sections(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sec_db_cat ON sections(db_name, category)")
        self.conn.commit()

    def get_available_databases(self) -> List[str]:
        """Return list of available standard DB names."""
        if not os.path.exists(self.db_dir):
            return []
        files = [f for f in os.listdir(self.db_dir) if f.endswith(".sdb")]
        return sorted([os.path.splitext(f)[0] for f in files])

    def load_database(self, db_name: str) -> int:
        """Parse and load a specific database into SQLite. Returns number of records loaded."""
        if db_name in self._loaded_dbs:
            return 0

        sdb_file = os.path.join(self.db_dir, f"{db_name}.sdb")
        if not os.path.exists(sdb_file):
            # Try finding case-insensitively
            for f in os.listdir(self.db_dir):
                if f.lower() == f"{db_name.lower()}.sdb":
                    sdb_file = os.path.join(self.db_dir, f)
                    break

        if not os.path.exists(sdb_file):
            raise FileNotFoundError(f"Database file not found: {db_name}.sdb in {self.db_dir}")

        parser = SDBParser(sdb_file, db_name=db_name)
        records = parser.parse()

        cursor = self.conn.cursor()
        for r in records:
            cursor.execute("""
                INSERT OR REPLACE INTO sections 
                (db_name, category, name, H, B, tw, tf, r, A, Ix, Iy, rx, ry, Zx, Zy, Sx, Sy, J, Cw, weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.db_name, r.category, r.name, r.H, r.B, r.tw, r.tf, r.r,
                r.A, r.Ix, r.Iy, r.rx, r.ry, r.Zx, r.Zy, r.Sx, r.Sy, r.J, r.Cw, r.weight
            ))
        self.conn.commit()
        self._loaded_dbs.add(db_name)
        return len(records)

    def load_all_databases(self) -> Dict[str, int]:
        """Load all available .sdb files."""
        result = {}
        for db_name in self.get_available_databases():
            try:
                count = self.load_database(db_name)
                result[db_name] = count
            except Exception:
                result[db_name] = 0
        return result

    def search_sections(self, keyword: str, db_name: Optional[str] = None, category: Optional[str] = None, limit: int = 50) -> List[SectionRecord]:
        """Search sections with keyword filtering."""
        if db_name and db_name not in self._loaded_dbs:
            self.load_database(db_name)
        elif not self._loaded_dbs and self.get_available_databases():
            # Load default KS if nothing loaded
            if "KS" in self.get_available_databases():
                self.load_database("KS")
            else:
                self.load_database(self.get_available_databases()[0])

        query = "SELECT * FROM sections WHERE name LIKE ?"
        params: List[Any] = [f"%{keyword}%"]

        if db_name:
            query += " AND db_name = ?"
            params.append(db_name)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY H ASC, B ASC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [self._row_to_record(row) for row in rows]

    def get_section(self, name: str, db_name: Optional[str] = None) -> Optional[SectionRecord]:
        """Retrieve a single section by exact name."""
        if db_name and db_name not in self._loaded_dbs:
            self.load_database(db_name)
        elif not self._loaded_dbs and self.get_available_databases():
            if "KS" in self.get_available_databases():
                self.load_database("KS")

        query = "SELECT * FROM sections WHERE name = ?"
        params: List[Any] = [name]
        if db_name:
            query += " AND db_name = ?"
            params.append(db_name)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return self._row_to_record(row)
        return None

    def get_categories(self, db_name: str) -> List[str]:
        """Get list of categories in a specific DB."""
        if db_name not in self._loaded_dbs:
            self.load_database(db_name)
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM sections WHERE db_name = ? ORDER BY category", (db_name,))
        return [row[0] for row in cursor.fetchall()]

    def _row_to_record(self, row: sqlite3.Row) -> SectionRecord:
        """Convert a SQLite row to SectionRecord."""
        return SectionRecord(
            name=row["name"],
            db_name=row["db_name"],
            category=row["category"],
            H=row["H"],
            B=row["B"],
            tw=row["tw"],
            tf=row["tf"],
            r=row["r"],
            A=row["A"],
            Ix=row["Ix"],
            Iy=row["Iy"],
            rx=row["rx"],
            ry=row["ry"],
            Zx=row["Zx"],
            Zy=row["Zy"],
            Sx=row["Sx"],
            Sy=row["Sy"],
            J=row["J"],
            Cw=row["Cw"],
            weight=row["weight"]
        )


# Global singleton instance
_global_db_manager: Optional[SectionDBManager] = None


def get_section_db_manager() -> SectionDBManager:
    """Get or initialize global SectionDBManager singleton."""
    global _global_db_manager
    if _global_db_manager is None:
        _global_db_manager = SectionDBManager()
    return _global_db_manager
