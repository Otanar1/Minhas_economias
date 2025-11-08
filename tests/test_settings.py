import pytest
import os
from src.main import app, db
from src.models import User
from werkzeug.security import check_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'

    # Create a dummy base.html template
    os.makedirs('src/templates', exist_ok=True)
    with open('src/templates/base.html', 'w') as f:
        f.write('{% block content %}{% endblock %}')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_update_profile_and_preferences(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Update profile and preferences
    response = client.post('/settings/', data={
        'birth_year': 1990,
        'gender': 'Masculino',
        'marital_status': 'Solteiro',
        'children_count': 0,
        'country': 'Brasil',
        'state': 'SP',
        'city': 'São Paulo',
        'receive_tips': 'on',
        'receive_news': 'on',
        'receive_partner_news': 'off',
        'initial_screen': 'transactions.index',
        'default_account': 1
    }, follow_redirects=True)

    assert response.status_code == 200

    # Verify the changes in the database
    updated_user = User.query.get(user.id)
    assert updated_user.birth_year == 1990
    assert updated_user.gender == 'Masculino'
    assert updated_user.preferences['receive_tips'] == True
    assert updated_user.preferences['receive_news'] == True
    assert 'receive_partner_news' not in updated_user.preferences or updated_user.preferences['receive_partner_news'] == False
    assert updated_user.preferences['initial_screen'] == 'transactions.index'
    assert updated_user.preferences['default_account'] == '1'

def test_change_password(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Change password
    response = client.post('/settings/change-password', data={
        'current_password': 'password',
        'new_password': 'new_password',
        'confirm_password': 'new_password'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Verify the password was changed
    updated_user = User.query.get(user.id)
    assert check_password_hash(updated_user.password, 'new_password')

def test_change_email(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Change email
    response = client.post('/settings/change-email', data={
        'new_email': 'new@example.com',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Verify the email was changed
    updated_user = User.query.get(user.id)
    assert updated_user.email == 'new@example.com'
