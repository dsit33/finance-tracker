from decimal import Decimal
import pandas as pd
from flask import Blueprint, jsonify, request
from adapters import get_adapter
from pipeline.dedup import fuzzy_dedup
from pipeline.django_client import fetch_recent, post_bulk
from pipeline.normalize import clean_merchants, normalize_schema
from pipeline.parse import parse_csv

ingest_bp = Blueprint('ingest', __name__)

@ingest_bp.post('/ingest/csv')
def ingest_csv():
    bank_id = request.form.get('bank_id')
    account_id = request.form.get('account_id')
    upload = request.files.get('file')

    if not bank_id or not account_id or upload is None:
        return jsonify({'error': 'bank_id, account_id, and file are required'}), 400
    
    adapter = get_adapter(bank_id)
    if adapter is None:
        return jsonify({'error': f'Unknown bank_id: {bank_id}'}), 400
    
    # Pipeline: parse, normalize and clean
    parsed = parse_csv(upload.stream, adapter)
    normalized = normalize_schema(parsed, adapter)
    cleaned = clean_merchants(normalized)

    # Fetch what Django already has, dedup against it
    existing = fetch_recent(int(account_id))
    existing_df = _existing_to_df(existing)
    print("CLEANED:\n", cleaned.dtypes, cleaned)                                                                                                                                                                                                                                            
    print("EXISTING:\n", existing_df.dtypes, existing_df)    
    survivors = fuzzy_dedup(cleaned, existing_df)

    payload = _rows_for_django(survivors, account_id)

    if not payload:
        return jsonify({'received': len(cleaned), 'deduped': len(cleaned), 'created': 0, 'skipped': 0}), 200
    
    result = post_bulk(payload)
    
    return jsonify({
        'received': len(cleaned),
        'deduped': len(cleaned) - len(survivors),
        'created': result['created'],
        'skipped': result['skipped']
    })

def _existing_to_df(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=['date', 'amount', 'merchant'])
    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['amount'] = df['amount'].astype(float)
    return df[['date', 'amount', 'merchant']]

def _rows_for_django(df: pd.DataFrame, account_id: str) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        rows.append({
            'account': int(account_id),
            'date': row['date'].isoformat(),
            'amount': str(Decimal(f'{row['amount']:.2f}')),
            'merchant': row['merchant'],
            'raw_merchant': row.get('raw_merchant', row['merchant'])
        })

    return rows