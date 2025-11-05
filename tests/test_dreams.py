import pytest
from src.main import app, db, User, Dream, Account

def test_add_dream(logged_in_client):
    """
    Testa a criação de um novo sonho.
    """
    client, user_id, _, _ = logged_in_client

    response = client.post('/dreams/add', data={
        'name': 'Viagem para a Lua',
        'target_amount': '100000.00',
        'target_date': '2030-01-01'
    })

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Sonho adicionado com sucesso!'

    with app.app_context():
        dream = Dream.query.one()
        assert dream.name == 'Viagem para a Lua'
        assert dream.target_amount == 100000.00

def test_list_dreams(logged_in_client):
    """
    Testa a listagem de sonhos.
    """
    client, user_id, _, _ = logged_in_client

    with app.app_context():
        d1 = Dream(user_id=user_id, name="Carro Novo", target_amount=50000, type="Geral")
        db.session.add(d1)
        db.session.commit()

    response = client.get('/dreams/')

    assert response.status_code == 200
    assert b"Meus Sonhos" in response.data
    assert b"Carro Novo" in response.data
    assert b"50000" in response.data

def test_edit_dream(logged_in_client):
    """
    Testa a edição de um sonho.
    """
    client, user_id, _, _ = logged_in_client

    with app.app_context():
        dream = Dream(user_id=user_id, name="Sonho a ser editado", target_amount=1000, type="Geral")
        db.session.add(dream)
        db.session.commit()
        dream_id = dream.id

    response = client.post(f'/dreams/edit/{dream_id}', data={
        'name': 'Sonho Editado',
        'target_amount': '1500.50'
    })

    assert response.status_code == 302

    with app.app_context():
        edited_dream = db.session.get(Dream, dream_id)
        assert edited_dream.name == 'Sonho Editado'
        assert edited_dream.target_amount == 1500.50

def test_delete_dream(logged_in_client):
    """
    Testa a exclusão de um sonho.
    """
    client, user_id, _, _ = logged_in_client

    with app.app_context():
        dream = Dream(user_id=user_id, name="Sonho a ser excluído", target_amount=2000, type="Geral")
        db.session.add(dream)
        db.session.commit()
        dream_id = dream.id

    response = client.post(f'/dreams/delete/{dream_id}')

    assert response.status_code == 302

    with app.app_context():
        deleted_dream = db.session.get(Dream, dream_id)
        assert deleted_dream is None

def test_contribute_to_dream_success(logged_in_client):
    """
    Testa uma contribuição bem-sucedida a um sonho.
    """
    client, user_id, account_id, _ = logged_in_client

    with app.app_context():
        account = db.session.get(Account, account_id)
        initial_balance = account.balance
        dream = Dream(user_id=user_id, name="Meu Sonho", target_amount=1000, type="Geral")
        db.session.add(dream)
        db.session.commit()
        dream_id = dream.id

    response = client.post(f'/dreams/contribute/{dream_id}', data={
        'amount': '100.00',
        'account_id': account_id
    })

    assert response.status_code == 302

    with app.app_context():
        updated_dream = db.session.get(Dream, dream_id)
        updated_account = db.session.get(Account, account_id)
        assert updated_dream.current_amount == 100.00
        assert updated_account.balance == initial_balance - 100.00

def test_contribute_to_dream_insufficient_funds(logged_in_client):
    """
    Testa uma contribuição a um sonho com saldo insuficiente.
    """
    client, user_id, account_id, _ = logged_in_client

    with app.app_context():
        dream = Dream(user_id=user_id, name="Sonho Caro", target_amount=5000, type="Geral")
        db.session.add(dream)
        db.session.commit()
        dream_id = dream.id
        account = db.session.get(Account, account_id)
        account.balance = 50.00
        db.session.commit()

    response = client.post(f'/dreams/contribute/{dream_id}', data={
        'amount': '100.00',
        'account_id': account_id
    })

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert 'Saldo insuficiente' in session['_flashes'][0][1]

def test_contribute_to_dream_unauthenticated(test_client):
    """
    Testa o acesso à página de contribuição sem autenticação.
    """
    response = test_client.get('/dreams/contribute/1')
    assert response.status_code == 302
    assert '/login' in response.location
