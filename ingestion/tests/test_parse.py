from pathlib import Path
from adapters import get_adapter
from pipeline.parse import parse_csv

FIXTURES = Path(__file__).parent / 'fixtures'

def test_parse_chase_csv_returns_canonical_columns():
    df = parse_csv(FIXTURES / 'chase_sample.csv', get_adapter('chase'))

    print(df)

    assert 'date' in df.columns
    assert 'raw_merchant' in df.columns
    assert 'amount' in df.columns
    assert len(df) == 15

def test_parse_boa_csv_returns_canonical_columns():
    df = parse_csv(FIXTURES / 'boa_sample.csv', get_adapter('boa'))

    print(df)

    assert 'date' in df.columns
    assert 'raw_merchant' in df.columns
    assert 'amount_debit' in df.columns
    assert 'amount_credit' in df.columns
    assert len(df) == 15