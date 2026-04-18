from __future__ import annotations

"""Database initialization and connection management."""
import os
import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path

DB_PATH = os.environ.get("FRIDGE_DB_PATH", "fridge.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


async def init_db() -> None:
    """Initialize the database: create tables and run integrity check."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable WAL mode for better concurrency and crash safety
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")

        # Run integrity check on startup
        cursor = await db.execute("PRAGMA integrity_check")
        result = await cursor.fetchone()
        if result and result[0] != "ok":
            raise RuntimeError(f"Database integrity check failed: {result[0]}")

        # Create tables from schema
        schema_sql = SCHEMA_PATH.read_text()
        await db.executescript(schema_sql)
        await db.commit()


@asynccontextmanager
async def get_db():
    """Async context manager that yields an aiosqlite connection."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
