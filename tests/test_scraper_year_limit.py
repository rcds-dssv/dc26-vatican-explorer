"""Regression test for the per-year speech cap in step04.

``max_n_speeches`` used to be assigned inside the per-year loop, so the first
year scraped set a ceiling for every later year. Because month indexes are
walked newest-first, that silently removed the beginning of each year from the
corpus. This test pins the loop to a per-year bound.
"""

import pytest

import dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts as step04

# Two years of deliberately different sizes. The bug capped 2014 at len(2013).
FAKE_SPEECHES = {
    "2013": [{"title": f"t13-{i}", "url": f"https://x/2013/{i}.html", "date": None} for i in range(3)],
    "2014": [{"title": f"t14-{i}", "url": f"https://x/2014/{i}.html", "date": None} for i in range(9)],
}


def _stub_network(monkeypatch, considered):
    """Replace every network-touching name in step04 with a canned answer.

    Speeches are reported as already present in the database, so the loop
    records each URL it reaches and then moves on without fetching anything.
    """
    monkeypatch.setattr(step04, "vatican_fetch_pope_directory_recent", lambda: [{"display_name": "Francis"}])
    monkeypatch.setattr(step04, "papal_find_by_display_name", lambda popes, name: {"slug": "francesco", "url": "https://x"})
    monkeypatch.setattr(step04, "fetch_pope_main_html", lambda url: "<html></html>")
    monkeypatch.setattr(step04, "extract_pope_metadata_from_main", lambda html: {})
    monkeypatch.setattr(
        step04,
        "extract_year_links_from_main",
        lambda html, slug, years, section: [
            {"year": y, "url": f"https://x/{y}.index.html"} for y in sorted(FAKE_SPEECHES)
        ],
    )
    monkeypatch.setattr(step04, "fetch_html", lambda url, **kw: "<html></html>")
    monkeypatch.setattr(
        step04,
        "collect_speeches_for_year_index",
        lambda idx_html, idx_url, pope_slug, section, year, fetcher=None: FAKE_SPEECHES[year],
    )

    def fake_exists(db_path, url, require_content=False):
        considered.append(url)
        return True

    monkeypatch.setattr(step04, "speech_url_exists_in_db", fake_exists)
    monkeypatch.setattr(step04, "get_speech_text_by_url", lambda db_path, url: "already stored")


def test_year_limit_does_not_leak_into_later_years(monkeypatch):
    """Each year must be walked in full, regardless of how small the first is."""
    considered: list[str] = []
    _stub_network(monkeypatch, considered)

    # Everything is reported as already stored, so nothing is collected and the
    # function bails out at the end. The loop bound is what is under test.
    with pytest.raises(SystemExit):
        step04.fetch_speeches_to_feather(pope="Francis", years_spec="2013-2014", lang="EN", section="speeches")

    from_2013 = [u for u in considered if "/2013/" in u]
    from_2014 = [u for u in considered if "/2014/" in u]

    assert len(from_2013) == 3
    # The bug produced 3 here: 2013's length leaking forward as the ceiling.
    assert len(from_2014) == 9


def test_explicit_max_n_speeches_applies_to_every_year(monkeypatch):
    """An explicit cap is a per-year limit, not a budget shared across years."""
    considered: list[str] = []
    _stub_network(monkeypatch, considered)

    with pytest.raises(SystemExit):
        step04.fetch_speeches_to_feather(
            pope="Francis", years_spec="2013-2014", lang="EN", section="speeches", max_n_speeches=2
        )

    assert len([u for u in considered if "/2013/" in u]) == 2
    assert len([u for u in considered if "/2014/" in u]) == 2
