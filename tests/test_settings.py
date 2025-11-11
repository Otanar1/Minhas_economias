import pytest
from src.models import User
from werkzeug.security import check_password_hash
import json

def test_update_profile(client, db, logged_in_client):
    """
    Testa a atualização do perfil do usuário.
    """
    _, user_id, _, _ = logged_in_client

    response = client.post('/settings/', data={'birth_year': 1990, 'gender': 'Masculino'})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Configurações atualizadas com sucesso!'

    user = User.query.get(user_id)
    assert user.birth_year == 1990

def test_update_preferences(client, db, logged_in_client):
    """
    Testa a atualização das preferências do usuário.
    """
    _, user_id, _, _ = logged_in_client

    response = client.post('/settings/', data={'initial_screen': 'transactions.index'})
    assert response.status_code == 302

    user = User.query.get(user_id)
    assert user.preferences['initial_screen'] == 'transactions.index'

def test_change_password(client, db, logged_in_client):
    """
    Testa a alteração de senha.
    """
    _, user_id, _, _ = logged_in_client

    response = client.post('/settings/change-password', data={
        'current_password': 'password123', 'new_password': 'new_password', 'confirm_password': 'new_password'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Senha atualizada com sucesso!'

    user = User.query.get(user_id)
    assert check_password_hash(user.password, 'new_password')

def test_change_email(client, db, logged_in_client):
    """
    Testa a alteração de email.
    """
    _, user_id, _, _ = logged_in_client

    response = client.post('/settings/change-email', data={
        'new_email': 'new@example.com', 'password': 'password123'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'E-mail atualizado com sucesso!'

    user = User.query.get(user_id)
    assert user.email == 'new@example.com'

def test_backup(client, logged_in_client):
    """
    Testa a funcionalidade de backup de dados.
    """
    response = client.get('/settings/backup')
    assert response.status_code == 200
    assert 'application/json' in response.content_type
