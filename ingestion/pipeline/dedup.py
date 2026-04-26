from datetime import timedelta
import pandas as pd
from rapidfuzz import fuzz

DEDUP_DATE_WINDOW = timedelta(days=3)

def fuzzy_dedup(new_df: pd.DataFrame, existing_df: pd.DataFrame, threshold: int=85) -> pd.DataFrame:
    """
    Filter new_df to rows that don't match in existing_df

    In order to be considered a new row, the amount cannot equal,
    the date must be outside 3 day range, and the merchants cannot
    match within the provided match score threshold
    """
    if existing_df.empty:
        return new_df.copy()
    
    keep_mask = []
    for _, new_row in new_df.iterrows():
        is_dup = _matches_any(new_row, existing_df, threshold)
        keep_mask.append(not is_dup)

    return new_df[keep_mask].reset_index(drop=True)

def _matches_any(new_row, existing_df: pd.DataFrame, threshold: int) -> bool:
    candidates = existing_df[
        (existing_df['amount'] == new_row['amount']) &
         ((existing_df['date'] - new_row['date']).abs() <= DEDUP_DATE_WINDOW)
    ]

    for _, existing_row in candidates.iterrows():
        if fuzz.ratio(new_row['merchant'], existing_row['merchant']) >= threshold:
            return True
        
    return False