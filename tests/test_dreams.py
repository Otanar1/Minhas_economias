import pytest
from src.main import app, db, User, Dream

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
