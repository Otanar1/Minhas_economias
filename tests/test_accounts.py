import pytest
from src.main import app, db, User, Account
from datetime import date

def test_list_accounts(logged_in_client):
    """
    Testa a listagem de contas.
    """
    client, user_id, _, _ = logged_in_client

    response = client.get('/accounts/')
    assert response.status_code == 200
    assert b"Gerenciar Contas" in response.data
    # A conta padrão 'Test Account' deve estar na lista
    assert b"Test Account" in response.data

def test_add_account(logged_in_client):
    """
    Testa a adição de uma nova conta.
    """
    client, user_id, _, _ = logged_in_client

    response = client.post('/accounts/add', data={
        'name': 'Nova Conta Poupança',
        'type': 'poupanca',
        'balance': '500.00'
    })
    assert response.status_code == 302

    with app.app_context():
        account = db.session.query(Account).filter_by(name='Nova Conta Poupança').one()
        assert account.type == 'poupanca'
        assert account.balance == 500.00

def test_edit_account(logged_in_client):
    """
    Testa a edição de uma conta.
    """
    client, user_id, account_id, _ = logged_in_client

    response = client.post(f'/accounts/edit/{account_id}', data={
        'name': 'Conta Corrente Editada',
        'active': 'true'
    })
    assert response.status_code == 302

    with app.app_context():
        account = db.session.get(Account, account_id)
        assert account.name == 'Conta Corrente Editada'

def test_deactivate_account(logged_in_client):
    """
    Testa a desativação de uma conta.
    """
    client, user_id, account_id, _ = logged_in_client

    response = client.post(f'/accounts/edit/{account_id}', data={
        'name': 'Conta a ser desativada',
        # O checkbox não envia valor se não estiver marcado
    })
    assert response.status_code == 302

    with app.app_context():
        account = db.session.get(Account, account_id)
        assert account.active is False
