import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from datetime import date, timedelta

from transactions.models import Transaction

_LOAD_FIELDS = ['id', 'date', 'amount', 'merchant', 'raw_merchant']

CADENCES = {
    'weekly': (5, 9),
    'biweekly': (11, 17),
    'monthly': (26, 35),
    'yearly': (355, 375)
}

AMOUNT_STABILITY_THRESHOLD = 0.2
GAP_STABILITY_THRESHOLD = 0.3

@dataclass
class CadenceResult:
    cadence: str
    confidence: float
    median_gap_days: int
    amount: float
    next_expected_date: date

def classify_cadence(group_df) -> CadenceResult | None:
    """
    Classify a group of transactions from the same merchant

    Returns None if no cadence is detected
    """
    if len(group_df) < 3:
        return None
    
    sorted_df = group_df.sort_values('date').reset_index(drop=True)
    dates = sorted_df['date'].tolist()
    amounts = sorted_df['amount'].astype(float).to_numpy()

    gaps = np.array([(dates[i] - dates[i - 1]).days for i in range(1, len(dates))])
    median_gap = float(np.median(gaps))

    cadence = _match_cadence(median_gap)
    if cadence is None:
        return None
    
    amount_cv = float(np.std(amounts) / np.abs(np.mean(amounts))) if np.mean(amounts) else 1.0
    if amount_cv > AMOUNT_STABILITY_THRESHOLD:
        return None
    
    gap_cv = float(np.std(gaps) / median_gap) if median_gap else 1.0
    if gap_cv > GAP_STABILITY_THRESHOLD:
        return None
    confidence = _confidence(gap_cv, amount_cv)

    return CadenceResult(
        cadence=cadence,
        confidence=confidence,
        median_gap_days=int(median_gap),
        amount=float(np.median(amounts)),
        next_expected_date=dates[-1] + timedelta(days=int(median_gap))
    )

def _match_cadence(median_gap: float) -> str | None:
    for label, (low, high) in CADENCES.items():
        if low <= median_gap <= high:
            return label
    return None

def _confidence(gap_cv: float, amount_cv: float) -> float:
    """
    Confidence = 1 - (gap_cv + amount_cv), clipped to [0, 1]

    Lower variance in either field increases overall confidence.
    Both contribute equally
    """
    raw = 1.0 - (gap_cv + amount_cv)
    return float(np.clip(raw, 0.0, 1.0))

def detect_recurring(account_id: int) -> list[dict]:
    """
    load -> group -> classifc -> return list of cadences detected
    """
    df = load_account_transactions(account_id)
    if df.empty:
        return []
    
    groups = group_by_merchant(df)

    results = []
    for merchant, group_df in groups.items():
        result = classify_cadence(group_df)

        if result is None:
            continue

        row = asdict(result)
        row['merchant'] = merchant
        results.append(row)

    return results

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