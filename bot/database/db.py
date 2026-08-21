"""Asynchronous SQLite database interface for anonymous telemetry, language preferences, and statistics."""

import logging
import os
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import aiosqlite

logger = logging.getLogger(__name__)


@dataclass
class AdminStats:
    """Aggregated usage statistics for administrators (no raw numbers)."""
    total_users: int
    total_lookups: int
    today_lookups: int
    top_countries: List[Tuple[str, int]]
    valid_lookups: int
    invalid_lookups: int


class DatabaseManager:
    """Manages anonymous usage records and statistics reporting."""

    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path

    async def initialize(self) -> None:
        """Create required tables and indices if they do not exist."""
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")

            # Users table: Tracks anonymous user interactions and language preference
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'en',
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_lookups INTEGER DEFAULT 1
                );
            """)

            # Lookups table: ONLY stores metadata aggregates (NO raw phone numbers)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS lookup_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    country_code TEXT,
                    country_calling_code TEXT,
                    number_type TEXT,
                    is_valid INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_lookup_created_at
                ON lookup_events (created_at);
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_lookup_country
                ON lookup_events (country_code);
            """)

            await db.commit()
            logger.info("Database initialized successfully at %s", self.db_path)

    async def get_user_language(self, user_id: int) -> str:
        """Retrieve user's preferred language (default 'en')."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT language FROM users WHERE user_id = ?;", (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row and row[0] else "en"
        except Exception:
            return "en"

    async def set_user_language(self, user_id: int, lang: str) -> None:
        """Save user's preferred language."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO users (user_id, language, first_seen, last_seen, total_lookups)
                    VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                    ON CONFLICT(user_id) DO UPDATE SET
                        language = excluded.language,
                        last_seen = CURRENT_TIMESTAMP;
                """, (user_id, lang))
                await db.commit()
        except Exception as e:
            logger.error("Failed to set user language: %s", e)

    async def get_all_user_ids(self) -> List[int]:
        """Fetch all distinct registered user IDs for broadcasts."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT user_id FROM users;") as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]
        except Exception as e:
            logger.error("Failed to fetch user IDs: %s", e)
            return []

    async def record_lookup(
        self,
        user_id: int,
        country_code: Optional[str] = None,
        country_calling_code: Optional[str] = None,
        number_type: Optional[str] = None,
        is_valid: bool = False,
    ) -> None:
        """Record an anonymous lookup event without raw phone number data."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO users (user_id, first_seen, last_seen, total_lookups)
                    VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                    ON CONFLICT(user_id) DO UPDATE SET
                        last_seen = CURRENT_TIMESTAMP,
                        total_lookups = total_lookups + 1;
                """, (user_id,))

                await db.execute("""
                    INSERT INTO lookup_events (
                        user_id, country_code, country_calling_code, number_type, is_valid, created_at
                    ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                """, (
                    user_id,
                    (country_code or "UNKNOWN").upper(),
                    country_calling_code or "N/A",
                    number_type or "Unknown",
                    1 if is_valid else 0,
                ))
                await db.commit()
        except Exception as e:
            logger.error("Failed to record lookup telemetry: %s", e)

    async def get_admin_stats(self) -> AdminStats:
        """Compute aggregate statistics for administrator review."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users;") as cursor:
                row = await cursor.fetchone()
                total_users = row[0] if row else 0

            async with db.execute("SELECT COUNT(*) FROM lookup_events;") as cursor:
                row = await cursor.fetchone()
                total_lookups = row[0] if row else 0

            async with db.execute("""
                SELECT COUNT(*) FROM lookup_events
                WHERE date(created_at) = date('now');
            """) as cursor:
                row = await cursor.fetchone()
                today_lookups = row[0] if row else 0

            top_countries: List[Tuple[str, int]] = []
            async with db.execute("""
                SELECT country_code, country_calling_code, COUNT(*) as cnt
                FROM lookup_events
                WHERE country_code != 'UNKNOWN'
                GROUP BY country_code, country_calling_code
                ORDER BY cnt DESC
                LIMIT 5;
            """) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    cc = row[0]
                    calling = row[1]
                    label = f"{cc} ({calling})" if calling and calling != "N/A" else cc
                    top_countries.append((label, row[2]))

            async with db.execute("SELECT COUNT(*) FROM lookup_events WHERE is_valid = 1;") as cursor:
                row = await cursor.fetchone()
                valid_lookups = row[0] if row else 0

            invalid_lookups = total_lookups - valid_lookups

            return AdminStats(
                total_users=total_users,
                total_lookups=total_lookups,
                today_lookups=today_lookups,
                top_countries=top_countries,
                valid_lookups=valid_lookups,
                invalid_lookups=invalid_lookups,
            )
