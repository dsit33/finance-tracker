from adapters import BankAdapter

BOA = BankAdapter(
    name='boa',
    column_map={
        'Posted Date': 'date',
        'Payee': 'raw_merchant',
        'Debit': 'amount_debit',
        'Credit': 'amount_credit'
    },
    date_format='%m/%d/%Y',
    amount_columns={'Debit', 'Credit'}
)