import pytest
from src.models import User
from werkzeug.security import check_password_hash

def test_successful_registration(client, db):
    """
    Testa o registro bem-sucedido e a persistência no banco de dados.
    """
    client.post('/auth/register', data={
        'name': 'New User', 'email': 'newuser@example.com',
        'password': 'password123', 'confirm_password': 'password123'
    })
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.name == 'New User'

def test_login_and_logout(client, db):
    """
    Testa o login com credenciais corretas e o logout.
    """
    user = User(name='Test User', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password123'})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['user_id'] == user.id

    response = client.get('/auth/logout')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' not in session

def test_password_reset_flow(client, db):
    """
    Testa o fluxo de redefinição de senha.
    """
    user = User(name='Reset User', email='reset@example.com')
    user.set_password('oldpassword')
    db.session.add(user)
    db.session.commit()

    token = user.get_reset_token()

    client.post(f'/auth/reset-password/{token}', data={
        'password': 'newpassword', 'confirm_password': 'newpassword'
    })

    db.session.refresh(user)
    assert check_password_hash(user.password, 'newpassword')
