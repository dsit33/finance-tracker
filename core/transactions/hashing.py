import hashlib


def compute_import_hash(account_id, date, amount, raw_merchant):
    payload = f"{account_id}|{date.isoformat()}|{amount}|{raw_merchant.strip()}"
    return hashlib.sha256(payload.encode()).hexdigest()