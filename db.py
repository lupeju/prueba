
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

class TravelDB:
    def __init__(self, db_path: str = "travelsmart.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP
                )
            """)
            conn.commit()

    def save_session(self, session_id: str, data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            json_data = json.dumps(data)
            conn.execute(
                "INSERT OR REPLACE INTO sessions (session_id, data, created_at) VALUES (?, ?, ?)",
                (session_id, json_data, datetime.now())
            )
            conn.commit()

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
