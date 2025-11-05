import pytest
from src.main import app, db, User, Account, Category, Transaction
from datetime import date
from werkzeug.security import generate_password_hash


def test_add_expense_transaction(logged_in_client):
    """
    Testa a adição de uma transação de despesa (saída).
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        initial_balance = db.session.get(Account, account_id).balance

    # Adicionar transação e verificar o redirecionamento
    response = client.post('/transactions/add', data={
        'type': 'saída',
        'description': 'Supermercado',
        'amount': '100.00',
        'date': '2025-01-15',
        'account_id': account_id,
        'category_id': category_id
    })
    assert response.status_code == 302 # Verifica o redirecionamento

    # Verificar a mensagem flash na sessão
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Transação adicionada com sucesso!'

    # Verificar dados no banco de dados
    with app.app_context():
        transaction = db.session.query(Transaction).filter_by(description='Supermercado').one()
        assert transaction.amount == 100.00
        updated_account = db.session.get(Account, account_id)
        assert updated_account.balance == initial_balance - 100.00

def test_add_income_transaction(logged_in_client):
    """
    Testa a adição de uma transação de receita (entrada).
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        initial_balance = db.session.get(Account, account_id).balance

    response = client.post('/transactions/add', data={
        'type': 'entrada',
        'description': 'Salário',
        'amount': '500.00',
        'date': '2025-01-05',
        'account_id': account_id,
        'category_id': category_id
    })
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Transação adicionada com sucesso!'

    with app.app_context():
        transaction = db.session.query(Transaction).filter_by(description='Salário').one()
        assert transaction.amount == 500.00
        updated_account = db.session.get(Account, account_id)
        assert updated_account.balance == initial_balance + 500.00

def test_list_transactions(logged_in_client):
    """
    Testa a página de listagem de transações.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        t1 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Almoço', amount=25.50, type='saída', date=date(2025, 1, 10))
        t2 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Freela', amount=200.00, type='entrada', date=date(2025, 1, 11))
        db.session.add_all([t1, t2])
        db.session.commit()

    response = client.get('/transactions/')

    assert response.status_code == 200
    assert b"Minhas Transa\xc3\xa7\xc3\xb5es" in response.data
    assert b"Almo\xc3\xa7o" in response.data
    assert b"Freela" in response.data

def test_delete_transaction(logged_in_client):
    """
    Testa a exclusão de uma transação.
    Verifica se a transação é removida e o saldo da conta é restaurado.
    """
    client, user_id, account_id, category_id = logged_in_client

    # 1. Criar uma transação para ser excluída
    with app.app_context():
        initial_balance = db.session.get(Account, account_id).balance
        transaction_to_delete = Transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            description='Gasto para excluir',
            amount=150.00,
            type='saída',
            date=date(2025, 1, 20)
        )
        # Atualizar o saldo da conta manualmente para o teste
        account = db.session.get(Account, account_id)
        account.balance -= 150.00
        db.session.add(transaction_to_delete)
        db.session.commit()
        transaction_id = transaction_to_delete.id
        balance_before_delete = account.balance

    # 2. Enviar requisição para excluir a transação
    response = client.post(f'/transactions/delete/{transaction_id}')
    assert response.status_code == 302 # Verifica o redirecionamento

    # 3. Verificar o resultado
    with app.app_context():
        # A transação foi removida?
        deleted_transaction = db.session.get(Transaction, transaction_id)
        assert deleted_transaction is None

        # O saldo da conta foi restaurado?
        updated_account = db.session.get(Account, account_id)
        assert updated_account.balance == initial_balance

def test_edit_transaction(logged_in_client):
    """
    Testa a edição de uma transação.
    Verifica se o saldo da conta é recalculado corretamente.
    """
    client, user_id, account_id, category_id = logged_in_client

    # 1. Criar uma transação inicial
    with app.app_context():
        initial_balance = db.session.get(Account, account_id).balance
        transaction = Transaction(
            user_id=user_id, account_id=account_id, category_id=category_id,
            description='Compra inicial', amount=50.00, type='saída', date=date(2025, 2, 1)
        )
        account = db.session.get(Account, account_id)
        account.balance -= 50.00
        db.session.add(transaction)
        db.session.commit()
        transaction_id = transaction.id

    # 2. Editar a transação (mudar o valor de 50 para 75)
    response = client.post(f'/transactions/edit/{transaction_id}', data={
        'type': 'saída',
        'description': 'Compra corrigida',
        'amount': '75.00',
        'date': '2025-02-01',
        'account_id': account_id,
        'category_id': category_id
    })
    assert response.status_code == 302

    # 3. Verificar o resultado
    with app.app_context():
        edited_transaction = db.session.get(Transaction, transaction_id)
        assert edited_transaction.description == 'Compra corrigida'
        assert edited_transaction.amount == 75.00

        # O saldo deve ser o inicial menos o novo valor da transação
        updated_account = db.session.get(Account, account_id)
        assert updated_account.balance == initial_balance - 75.00
