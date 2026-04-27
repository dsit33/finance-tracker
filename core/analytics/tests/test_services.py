import pandas as pd
import pytest
from django.test.utils import CaptureQueriesContext
from django.db import connection

from analytics.services import group_by_merchant, load_account_transactions
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

