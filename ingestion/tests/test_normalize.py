from datetime import date

import pandas as pd

from adapters import get_adapter
from pipeline.normalize import clean_merchants, normalize_schema

def _chase_df():
    return pd.DataFrame({
        'date': [date(2026, 4, 1)],
        'raw_merchant': ['Netflix.com'],
        'amount': [-15.99]
    })

def _boa_df():
    return pd.DataFrame({
        'date': [date(2026, 4, 1), date(2026, 4, 3)],
        'raw_merchant': ['COSTCO', 'DIRECT DEPOSIT'],
        'amount_debit': [154.32, None],
        'amount_credit': [None, 2200.00]
    })

def test_normalize_chase_preserves_signed_amount():
    df = normalize_schema(_chase_df(), get_adapter('chase'))

    assert df['amount'].iloc[0] == -15.99
    assert list(df.columns) == ['date', 'raw_merchant', 'amount']

def test_normalize_boa_signs_debit_negative():
    df = normalize_schema(_boa_df(), get_adapter('boa'))

    assert df['amount'].iloc[0] == -154.32
    assert df['amount'].iloc[1] == 2200.00

def test_clean_merchant_lowercases():
    df = _boa_df()
    out = clean_merchants(df)

    assert out['merchant'].tolist() == ['costco', 'direct deposit']

def test_clean_merchant_strips_store_number_suffix():
    df = pd.DataFrame({"raw_merchant": ["STARBUCKS #1234", "Whole Foods 4567"]})
    out = clean_merchants(df)

    assert out['merchant'].tolist() == ['starbucks', 'whole foods']

def test_clean_merchants_collapses_whitespace():
    df = pd.DataFrame({"raw_merchant": ["AMAZON   MARKETPLACE"]})
    out = clean_merchants(df)

    assert out['merchant'].iloc[0] == 'amazon marketplace'

def test_clean_merchants_preserves_raw():
    df = pd.DataFrame({"raw_merchant": ["STARBUCKS #1234"]})
    out = clean_merchants(df)

    assert out['raw_merchant'].iloc[0] == 'STARBUCKS #1234'
    assert out['merchant'].iloc[0] == 'starbucks'