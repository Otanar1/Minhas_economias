import pytest
from src.models import Transaction, Account
from datetime import date

def test_add_expense_transaction(client, db, logged_in_client):
    """
    Testa a adição de uma transação de despesa.
    """
    _, _, account_id, category_id = logged_in_client
    account = Account.query.get(account_id)
    initial_balance = account.balance

    response = client.post('/transactions/add', data={
        'type': 'saída', 'description': 'Supermercado', 'amount': '100.00',
        'date': '2025-01-15', 'account_id': account_id, 'category_id': category_id
    })
    assert response.status_code == 302 # Verifica o redirecionamento

    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Transação adicionada com sucesso!'

    db.session.refresh(account)
    assert account.balance == initial_balance - 100.00

def test_add_income_transaction(client, db, logged_in_client):
    """
    Testa a adição de uma transação de receita.
    """
    _, _, account_id, category_id = logged_in_client
    account = Account.query.get(account_id)
    initial_balance = account.balance

    response = client.post('/transactions/add', data={
        'type': 'entrada', 'description': 'Salário', 'amount': '500.00',
        'date': '2025-01-05', 'account_id': account_id, 'category_id': category_id
    })
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Transação adicionada com sucesso!'

    db.session.refresh(account)
    assert account.balance == initial_balance + 500.00

def test_list_transactions(client, db, logged_in_client):
    """
    Testa a listagem de transações.
    """
    _, user_id, account_id, category_id = logged_in_client
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Almoço', amount=25.50, type='saída', date=date(2025, 1, 10)))
    db.session.commit()

    response = client.get('/transactions/')
    assert response.status_code == 200
    assert b"Almo\xc3\xa7o" in response.data

def test_delete_transaction(client, db, logged_in_client):
    """
    Testa a exclusão de uma transação e a restauração do saldo.
    """
    _, user_id, account_id, category_id = logged_in_client
    account = Account.query.get(account_id)
    initial_balance = account.balance
    transaction = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Gasto para excluir', amount=150.00, type='saída', date=date(2025, 1, 20))
    account.balance -= 150.00
    db.session.add(transaction)
    db.session.commit()

    client.post(f'/transactions/delete/{transaction.id}')
    assert Transaction.query.get(transaction.id) is None
    db.session.refresh(account)
    assert account.balance == initial_balance

def test_edit_transaction(client, db, logged_in_client):
    """
    Testa a edição de uma transação e o recálculo do saldo.
    """
    _, user_id, account_id, category_id = logged_in_client
    account = Account.query.get(account_id)
    initial_balance = account.balance
    transaction = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Compra', amount=50.00, type='saída', date=date(2025, 2, 1))
    account.balance -= 50.00
    db.session.add(transaction)
    db.session.commit()

    client.post(f'/transactions/edit/{transaction.id}', data={'amount': '75.00', 'description': 'Compra corrigida', 'type': 'saída', 'date': '2025-02-01', 'account_id': account_id, 'category_id': category_id})

    db.session.refresh(transaction)
    assert transaction.amount == 75.00
    db.session.refresh(account)
    assert account.balance == initial_balance - 75.00

def test_add_recurring_transaction(client, db, logged_in_client):
    """
    Testa a adição de uma transação recorrente.
    """
    _, _, account_id, category_id = logged_in_client
    client.post('/transactions/add', data={
        'description': 'Assinatura Mensal', 'amount': '29.99', 'date': '2025-02-01',
        'account_id': account_id, 'category_id': category_id, 'type': 'saída',
        'recurring': 'true', 'recurrence_frequency': 'mensal'
    })

    transaction = Transaction.query.filter_by(description='Assinatura Mensal').one()
    assert transaction.recurring is True
