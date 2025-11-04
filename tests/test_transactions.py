import pytest
from src.main import app, db, User, Account, Category, Transaction
from datetime import date
from werkzeug.security import generate_password_hash

@pytest.fixture
def logged_in_client(test_client):
    """
    Usa a fixture 'test_client' do conftest.py para obter um cliente limpo
    e depois cria os dados necessários e faz o login.
    """
    with app.app_context():
        # 1. Criar dados com senha hasheada
        user = User(name='Test User', email='test@example.com', password=generate_password_hash('password123'))
        db.session.add(user)
        db.session.commit()

        account = Account(name='Test Account', balance=1000.0, user_id=user.id, type='conta_corrente')
        db.session.add(account)

        category = Category(name='Test Category', type='saída', user_id=user.id)
        db.session.add(category)
        db.session.commit()

        user_id = user.id
        account_id = account.id
        category_id = category.id

    # 2. Fazer login
    test_client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)

    # 3. Retornar dados
    return test_client, user_id, account_id, category_id

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
