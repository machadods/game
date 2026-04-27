import sqlite3
import json
import shutil
from datetime import datetime


class GameDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn    = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE,
                color      TEXT    DEFAULT '#FFFFFF',
                ship_x     REAL    DEFAULT 0,
                ship_y     REAL    DEFAULT 0,
                health     INTEGER DEFAULT 3,
                kills      INTEGER DEFAULT 0,
                score      INTEGER DEFAULT 0,
                gold       INTEGER DEFAULT 0,
                created_at TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS planets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                x           REAL,
                y           REAL,
                radius_km   REAL,
                planet_type TEXT,
                difficulty  INTEGER,
                minerals    TEXT,
                owner_id    INTEGER REFERENCES players(id),
                conquered   INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()

    def _migrate(self):
        """Adiciona colunas novas sem quebrar bancos antigos."""
        migrations = [
            "ALTER TABLE players ADD COLUMN gold INTEGER DEFAULT 0",
            "ALTER TABLE planets ADD COLUMN conquered INTEGER DEFAULT 0",
        ]
        for sql in migrations:
            try:
                self.conn.execute(sql)
                self.conn.commit()
            except Exception:
                pass  # coluna já existe

    # ── Players ───────────────────────────────────────────────────────────────
    def create_player(self, username: str, color: str = '#FFFFFF') -> int:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO players (username, color) VALUES (?, ?)",
            (username, color)
        )
        self.conn.commit()
        # Se já existia (IGNORE), busca o id
        if cur.lastrowid == 0:
            row = self.get_player_by_username(username)
            return row['id'] if row else -1
        return cur.lastrowid

    def get_player(self, player_id: int) -> dict:
        row = self.conn.execute(
            "SELECT * FROM players WHERE id = ?", (player_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_player_by_username(self, username: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM players WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_players(self) -> list:
        return self.conn.execute("SELECT * FROM players").fetchall()

    def save_player(self, player_id: int, username: str,
                    ship_x: float, ship_y: float,
                    health: int, kills: int, score: int,
                    gold: int = 0):
        self.conn.execute("""
            UPDATE players
            SET username=?, ship_x=?, ship_y=?, health=?, kills=?, score=?, gold=?
            WHERE id=?
        """, (username, ship_x, ship_y, health, kills, score, gold, player_id))
        self.conn.commit()

    # ── Planets ───────────────────────────────────────────────────────────────
    def create_planet(self, name: str, x: float, y: float,
                      radius_km: float, planet_type: str,
                      difficulty: int, minerals: dict) -> int:
        cur = self.conn.execute("""
            INSERT INTO planets (name, x, y, radius_km, planet_type, difficulty, minerals)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, x, y, radius_km, planet_type, difficulty, json.dumps(minerals)))
        self.conn.commit()
        return cur.lastrowid

    def get_all_planets(self) -> list:
        return self.conn.execute("SELECT * FROM planets").fetchall()

    def set_planet_conquered(self, planet_id: int, owner_id: int):
        self.conn.execute(
            "UPDATE planets SET conquered=1, owner_id=? WHERE id=?",
            (owner_id, planet_id)
        )
        self.conn.commit()

    # ── Utility ───────────────────────────────────────────────────────────────
    def backup(self):
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.replace('.db', f'_backup_{ts}.db')
        shutil.copy2(self.db_path, backup_path)
        print(f"[DB] Backup: {backup_path}")

    def close(self):
        self.conn.close()
