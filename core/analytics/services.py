import pandas as pd

from transactions.models import Transaction

_LOAD_FIELDS = ['id', 'date', 'amount', 'merchant', 'raw_merchant']

def load_account_transactions(account_id: int) -> pd.DataFrame:
    """
    Load all transactions for an account into a DataFrame in one query
    """
    qs = Transaction.objects.filter(account_id=account_id).values(*_LOAD_FIELDS)
    return pd.DataFrame(list(qs), columns=_LOAD_FIELDS)

def group_by_merchant(df: pd.DataFrame, min_size: int = 3) -> dict[str, pd.DataFrame]:
    """
    Return {merchant: sub-df} for merchants with at least min_size rows
    """
    if df.empty:
        return {}
    
    groups = {}
    for merchant, sub_df in df.groupby('merchant'):
        if len(sub_df) >= min_size:
            groups[merchant] = sub_df.reset_index(drop=True)

    return groups