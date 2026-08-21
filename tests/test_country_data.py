"""Unit tests for country data directory, flag generation, and search."""

from bot.utils.country_data import get_flag_emoji, search_country


def test_flag_emoji_generation():
    """Verify flag emoji generation from ISO country codes."""
    assert get_flag_emoji("IN") == "🇮🇳"
    assert get_flag_emoji("US") == "🇺🇸"
    assert get_flag_emoji("GB") == "🇬🇧"
    assert get_flag_emoji(None) == "🌐"
    assert get_flag_emoji("INVALID") == "🌐"


def test_search_country():
    """Verify search by country name, calling code, or ISO code."""
    # Search by ISO 2
    res_in = search_country("IN")
    assert res_in is not None
    assert res_in.name_en == "India"
    assert res_in.calling_code == "+91"
    assert res_in.flag == "🇮🇳"

    # Search by calling code
    res_code = search_country("+44")
    assert res_code is not None
    assert res_code.name_en == "United Kingdom"

    # Search by name
    res_name = search_country("Japan")
    assert res_name is not None
    assert res_name.iso2 == "JP"
    assert res_name.calling_code == "+81"

    # Search non-existent
    res_none = search_country("NonExistentLand")
    assert res_none is None
