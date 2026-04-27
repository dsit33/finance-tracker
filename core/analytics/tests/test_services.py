import pandas as pd
import pytest
from django.test.utils import CaptureQueriesContext
from django.db import connection
from datetime import date, timedelta
from decimal import Decimal

from analytics.services import group_by_merchant, load_account_transactions, classify_cadence, detect_recurring
from transactions.factories import TransactionFactory

pytestmark = pytest.mark.django_db

def test_load_returns_dataframe_with_expected_columns(account):
    TransactionFactory(account=account)
    df = load_account_transactions(account.pk)

    assert {'date', 'amount', 'merchant', 'raw_merchant', 'id'}.issubset(df.columns)

def test_load_returns_empty_df_for_account_with_no_txns(account):
    df = load_account_transactions(account.pk)
    assert {'date', 'amount', 'merchant', 'raw_merchant', 'id'}.issubset(df.columns)
    assert df.empty

def test_load_runs_single_query(account):
    TransactionFactory.create_batch(10, account=account)

    with CaptureQueriesContext(connection) as ctx:
        load_account_transactions(account.pk)

    assert len(ctx) == 1, f'Expected 1 query, got {len(ctx): {ctx.captured_queries}}'

def test_group_drops_groups_with_lt_3_txns():
    df = pd.DataFrame({
        'merchant': ['netflix', 'netflix', 'netflix', 'spotify', 'spotify'],
        'amount': [-15.99, -15.99, -15.99, -9.99, -9.99],
    })

    grouped = group_by_merchant(df)

    assert 'netflix' in grouped
    assert 'spotify' not in grouped

def test_group_returns_subdfs_for_qualifying_merchants():
    df = pd.DataFrame({
        'merchant': ['netflix', 'netflix', 'netflix', 'spotify', 'spotify'],
        'amount': [-15.99, -15.99, -15.99, -9.99, -9.99],
    })

    grouped = group_by_merchant(df)

    assert len(grouped['netflix']) == 3

def _build_group(start: date, gap_days: int, amount: Decimal, count: int):
    return pd.DataFrame({
        'date': [start + timedelta(days=gap_days * i) for i in range(count)],
        'amount': [float(amount)] * count,
        'merchant': ['netflix'] * count,
    })

def test_cadence_weekly():
    df = _build_group(date(2026, 1, 1), 7, Decimal('9.99'), 4)
    result = classify_cadence(df)

    assert result is not None
    assert result.cadence == 'weekly'

def test_cadence_monthly():
    df = _build_group(date(2026, 1, 1), 30, Decimal(12.99), 4)
    result = classify_cadence(df)

    assert result is not None
    assert result.cadence == 'monthly'

def test_cadence_yearly():
    df = _build_group(date(2022, 1, 1), 365, Decimal('15.99'), 4)
    result = classify_cadence(df)

    assert result is not None
    assert result.cadence == 'yearly'

def test_cadence_none_when_variance_too_high():
    df = pd.DataFrame({
        'date': [date(2026, 1, 1), date(2026, 1, 5), date(2026, 3, 20), date(2026, 4, 1)],
        'amount': [-15.99] * 4,
        'merchant': ['netflix'] * 4
    })

    assert classify_cadence(df) is None

def test_cadence_none_when_amount_unstable():
    df = _build_group(date(2026, 1, 1), 30, Decimal('15.99'), 4)
    df.loc[2, 'amount'] = -100.00

    assert classify_cadence(df) is None

def test_confidence_higher_when_variance_lower():
    perfect = _build_group(date(2026, 1, 1), 30, Decimal('15.99'), 5)
    noisy_dates = perfect.copy()
    noisy_dates.loc[1, 'date'] = date(2026, 1, 28)

    assert classify_cadence(perfect).confidence >= classify_cadence(noisy_dates).confidence

def test_next_expected_date_is_last_plus_median_gap():
    df = _build_group(date(2026, 1, 1), 30, Decimal('15.99'), 4)
    result = classify_cadence(df)

    last_date = date(2026, 1, 1) + timedelta(days=30*3)
    assert result.next_expected_date == last_date + timedelta(days=30)

def test_detect_recurring_returns_dicts(account):
    start = date(2026, 1, 1)
    for i in range(5):
        TransactionFactory(
            account= account,
            date=start + timedelta(days=30 * i),
            amount=Decimal('15.99'),
            merchant='netflix',
            raw_merchant='NETFLIX.COM',
            import_hash=f'netflix-{i}',
        )

    results = detect_recurring(account.pk)

    assert any(r['merchant'] == 'netflix' and r['cadence'] == 'monthly' for r in results)