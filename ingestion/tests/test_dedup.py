from datetime import date, timedelta

import pandas as pd

from pipeline.dedup import fuzzy_dedup

def _row(d, amount, merchant):
    return {'date': d, 'amount': amount, 'merchant': merchant}

def _df(*rows):
    return pd.DataFrame(list(rows))

def test_exact_match_removed():
    new = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))
    existing = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))

    assert fuzzy_dedup(new, existing).empty

def test_within_3_day_window_removed():
    new = _df(_row(date(2026, 4, 17), -15.99, 'netflix'))
    existing = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))

    assert fuzzy_dedup(new, existing).empty

def test_outside_3_day_window_kept():
    new = _df(_row(date(2026, 4, 16), -15.99, 'netflix'))
    existing = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))

    assert len(fuzzy_dedup(new, existing)) == 1

def test_different_amount_kept():
    new = _df(_row(date(2026, 4, 20), -8.99, 'netflix'))
    existing = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))

    assert len(fuzzy_dedup(new, existing)) == 1

def test_type_merchant_at_high_ratio_removed():
    new = _df(_row(date(2026, 4, 20), -15.99, 'netfilx'))
    existing = _df(_row(date(2026, 4, 20), -15.99, 'netflix'))

    assert fuzzy_dedup(new, existing).empty

def test_empty_existing_returns_all_new():
    new = _df(
        _row(date(2026, 4, 20), -15.99, 'netflix'),
        _row(date(2026, 4, 18), -15.99, 'spotify'),
        )
    existing = pd.DataFrame(columns=['date', 'amount', 'merchant'])

    assert len(fuzzy_dedup(new, existing)) == 2

def test_preserves_order_of_survivors():
    new = _df(
        _row(date(2026, 4, 1), -15.99, "netflix"),
        _row(date(2026, 4, 2), -5.75, "starbucks"),
        _row(date(2026, 4, 3), -9.99, "spotify"),
    )
    existing = _df(_row(date(2026, 4, 2), -5.75, 'strbucks'))

    result = fuzzy_dedup(new, existing)
    assert result['merchant'].tolist() == ['netflix', 'spotify']