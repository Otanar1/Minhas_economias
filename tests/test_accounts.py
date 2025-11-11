import pytest
from src.models import Account

def test_list_accounts(client, logged_in_client):
    """
    Testa a listagem de contas.
    """
    response = client.get('/accounts/')
    assert response.status_code == 200
    assert b"Gerenciar Contas" in response.data
    assert b"Test Account" in response.data

def test_add_account(client, logged_in_client):
    """
    Testa a adição de uma nova conta.
    """
    _, user_id, _, _ = logged_in_client
    response = client.post('/accounts/add', data={
        'name': 'Nova Conta Poupança',
        'type': 'poupanca',
        'balance': '500.00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Conta adicionada com sucesso" in response.data

    account = Account.query.filter_by(name='Nova Conta Poupança', user_id=user_id).first()
    assert account is not None
    assert account.balance == 500.00

def test_edit_account(client, logged_in_client):
    """
    Testa a edição de uma conta.
    """
    _, _, account_id, _ = logged_in_client
    response = client.post(f'/accounts/edit/{account_id}', data={
        'name': 'Conta Corrente Editada',
        'active': 'true'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Conta atualizada com sucesso" in response.data

    account = Account.query.get(account_id)
    assert account.name == 'Conta Corrente Editada'
    assert account.active is True

def test_deactivate_account(client, db, logged_in_client):
    """
    Testa se desmarcar 'active' na edição desativa a conta.
    """
    _, user_id, account_id, _ = logged_in_client

    # Edita a conta, mas não inclui 'active' no formulário (simulando um checkbox desmarcado)
    response = client.post(f'/accounts/edit/{account_id}', data={
        'name': 'Conta Desativada',
        'type': 'poupanca',
        'balance': '100.0'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Conta atualizada com sucesso" in response.data

    account = Account.query.get(account_id)
    assert account.active is False
