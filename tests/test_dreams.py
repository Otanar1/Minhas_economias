import pytest
from src.models import Dream, Account
from datetime import date

def test_add_dream(client, db, logged_in_client):
    """
    Testa a criação de um novo sonho.
    """
    response = client.post('/dreams/add', data={
        'name': 'Viagem', 'target_amount': '10000.00', 'target_date': '2030-01-01'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Sonho adicionado com sucesso!'
    assert Dream.query.filter_by(name='Viagem').first() is not None

def test_edit_dream(client, db, logged_in_client):
    """
    Testa a edição de um sonho.
    """
    _, user_id, _, _ = logged_in_client
    dream = Dream(user_id=user_id, name="Meu Sonho", target_amount=1000, type="Geral")
    db.session.add(dream)
    db.session.commit()

    response = client.post(f'/dreams/edit/{dream.id}', data={
        'name': 'Sonho Editado', 'target_amount': '1500.50'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Sonho atualizado com sucesso!'

    db.session.refresh(dream)
    assert dream.name == 'Sonho Editado'

def test_delete_dream(client, db, logged_in_client):
    """
    Testa a exclusão de um sonho.
    """
    _, user_id, _, _ = logged_in_client
    dream = Dream(user_id=user_id, name="Para Excluir", target_amount=2000, type="Geral")
    db.session.add(dream)
    db.session.commit()

    response = client.post(f'/dreams/delete/{dream.id}')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Sonho excluído com sucesso!'
    assert Dream.query.get(dream.id) is None

def test_contribute_to_dream(client, db, logged_in_client):
    """
    Testa a contribuição para um sonho.
    """
    _, user_id, account_id, _ = logged_in_client
    dream = Dream(user_id=user_id, name="Meu Sonho", target_amount=1000, type="Geral")
    db.session.add(dream)
    db.session.commit()

    response = client.post(f'/dreams/contribute/{dream.id}', data={'amount': '100.00', 'account_id': account_id})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Contribuição realizada com sucesso!'

    db.session.refresh(dream)
    assert dream.current_amount == 100.00
