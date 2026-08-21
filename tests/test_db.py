"""Unit and integration tests for SQLite anonymous database operations."""

import os
import pytest
from bot.database.db import DatabaseManager


@pytest.mark.asyncio
async def test_database_initialization_and_operations(tmp_path):
    """Test table creation, event recording, and admin stats retrieval."""
    db_file = tmp_path / "test_bot.db"
    db = DatabaseManager(str(db_file))

    await db.initialize()
    assert os.path.exists(db_file)

    # Initial stats should be empty
    stats_empty = await db.get_admin_stats()
    assert stats_empty.total_users == 0
    assert stats_empty.total_lookups == 0
    assert stats_empty.today_lookups == 0
    assert len(stats_empty.top_countries) == 0

    # Record lookups from user 101
    await db.record_lookup(
        user_id=101,
        country_code="IN",
        country_calling_code="+91",
        number_type="Mobile",
        is_valid=True,
    )
    await db.record_lookup(
        user_id=101,
        country_code="IN",
        country_calling_code="+91",
        number_type="Mobile",
        is_valid=True,
    )

    # Record lookups from user 202
    await db.record_lookup(
        user_id=202,
        country_code="US",
        country_calling_code="+1",
        number_type="Fixed Line",
        is_valid=True,
    )
    await db.record_lookup(
        user_id=202,
        country_code="GB",
        country_calling_code="+44",
        number_type="Mobile",
        is_valid=False,
    )

    # Fetch stats
    stats = await db.get_admin_stats()
    assert stats.total_users == 2
    assert stats.total_lookups == 4
    assert stats.today_lookups == 4
    assert stats.valid_lookups == 3
    assert stats.invalid_lookups == 1

    # Top countries should list IN first (2 lookups), then US and GB (1 lookup each)
    assert len(stats.top_countries) == 3
    assert "IN (+91)" in stats.top_countries[0][0]
    assert stats.top_countries[0][1] == 2
