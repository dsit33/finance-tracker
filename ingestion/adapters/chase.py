from adapters import BankAdapter

CHASE = BankAdapter(
    name='chase',
    column_map={
        'Transaction Date': 'date',
        'Description': 'raw_merchant',
        'Amount': 'amount'
    },
    date_format='%m/%d/%Y',
    amount_columns={'Amount',}
)