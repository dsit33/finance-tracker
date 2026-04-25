import pandas as pd

from adapters import BankAdapter

def parse_csv(file, adapter: BankAdapter) -> pd.DataFrame:
    """
    Load a bank CSV and rename the columns to make our schema.

    Returns a DataFrame with adapter-renamed columns and parsed dates.
    Amount handling happens in normalize_schema
    """
    df = pd.read_csv(file)
    df = df.rename(columns=adapter.column_map)

    df['date'] = pd.to_datetime(
        df['date'], format=adapter.date_format, errors='raise'
    ).dt.date

    return df