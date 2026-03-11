"""
VELOCITY A-OS: STORAGE
Database wrapper (ChromaDB + SQLite)
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import Optional, Dict


class StorageManager:
    """Manages persistent storage for memories and logs"""
    
    def __init__(self, db_path: str = "./data/velocity.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    async def initialize(self):
        """Initialize database"""
        print(f"[STORAGE] Initializing at {self.db_path}...")
        self.conn = sqlite3.connect(str(self.db_path))
        await self._create_tables()
    
    async def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()
        
        # Memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata JSON
            )
        """)
        
        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                event_type TEXT NOT NULL,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    async def store_log(self, event_type: str, message: str):
        """Store event log"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO logs (event_type, message) VALUES (?, ?)",
            (event_type, message)
        )
        self.conn.commit()
    
    async def shutdown(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
        print("[STORAGE] Database closed")
