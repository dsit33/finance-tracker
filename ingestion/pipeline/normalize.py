import re

import numpy as np
import pandas as pd

from adapters import BankAdapter

_STORE_NUMBER_RE = re.compile(r'\s*#?\d{3,}\s*$')
_WHITESPACE_RE = re.compile(r'\s+')

def normalize_schema(df: pd.DataFrame, adapter: BankAdapter) -> pd.DataFrame:
    """
    Collapse debit/credit columns into a single amount column
    """
    df = df.copy()

    if len(adapter.amount_columns) == 2:
        debit = df['amount_debit'].fillna(0).astype(float)
        credit = df['amount_credit'].fillna(0).astype(float)
        df['amount'] = credit - debit
        df = df.drop(columns=['amount_debit', 'amount_credit'])
    else:
        df['amount'] = df['amount'].astype(float)

    canonical_cols = ['date', 'raw_merchant', 'amount']
    return df[canonical_cols]

def clean_merchants(df: pd.DataFrame) -> pd.DataFrame:
    """
    add a 'merchant' column of cleaned raw_merchant entries
    """

    df = df.copy()

    cleaned = (
        df['raw_merchant']
            .str.lower()
            .str.replace(_STORE_NUMBER_RE, '', regex=True)
            .str.replace(_WHITESPACE_RE, ' ', regex=True)
            .str.strip()
    )
    df['merchant'] = cleaned

    return df