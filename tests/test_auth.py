import pytest
from src.main import app, db, User
from werkzeug.security import generate_password_hash

def test_index_redirects_to_login(test_client):
    """
    Testa se a rota raiz ('/') redireciona para a página de login
    quando o usuário não está autenticado.
    """
    response = test_client.get('/', follow_redirects=True)
    # Verifica se a resposta foi bem-sucedida (código 200)
    assert response.status_code == 200
    # Verifica se a página de login é exibida
    assert b"Acesse sua conta" in response.data

def test_successful_registration(test_client):
    """
    Testa se um novo usuário pode se registrar com sucesso.
    """
    response = test_client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    # Verifica se o registro foi bem-sucedido e redirecionou para o login
    assert response.status_code == 200
    # Verifica se a mensagem de sucesso é exibida
    assert b"Cadastro realizado com sucesso!" in response.data

    # Verifica se o usuário foi realmente criado no banco de dados
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.name == 'Test User'

def test_registration_with_existing_email(test_client):
    """
    Testa se o registro falha se o email já estiver em uso.
    """
    # Primeiro, cria um usuário para o teste
    test_client.post('/auth/register', data={
        'name': 'First User',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # Tenta registrar com o mesmo email
    response = test_client.post('/auth/register', data={
        'name': 'Second User',
        'email': 'test@example.com',
        'password': 'password456',
        'confirm_password': 'password456'
    }, follow_redirects=True)

    # Verifica se a resposta foi bem-sucedida (código 200, pois renderiza a página de novo)
    assert response.status_code == 200
    # Verifica se a mensagem de erro é exibida
    assert b"Este email j\xc3\xa1 est\xc3\xa1 em uso" in response.data # "Este email já está em uso"

def test_successful_login_and_logout(test_client):
    """
    Testa o fluxo completo de login e logout de um usuário.
    """
    # 1. Registrar um usuário para o teste
    test_client.post('/auth/register', data={
        'name': 'Login User',
        'email': 'login@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # 2. Fazer login com o usuário criado
    response = test_client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Verifica se o login foi bem-sucedido e redirecionou para o dashboard
    assert response.status_code == 200
    assert b"Contas" in response.data  # Verifica um texto estático do dashboard
    assert b"login@example.com" in response.data # Verifica se o email do usuário aparece

    # 3. Fazer logout
    response = test_client.get('/auth/logout', follow_redirects=True)

    # Verifica se o logout foi bem-sucedido e redirecionou para a página de login
    assert response.status_code == 200
    assert b"Acesse sua conta" in response.data

def test_login_with_incorrect_password(test_client):
    """
    Testa se o login falha com uma senha incorreta.
    """
    # Registrar um usuário
    test_client.post('/auth/register', data={
        'name': 'Login User',
        'email': 'login@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # Tentar fazer login com a senha errada
    response = test_client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    # Verifica se a resposta foi bem-sucedida (código 200, pois renderiza a página de novo)
    assert response.status_code == 200
    # Verifica se a mensagem de erro é exibida
    assert b"Email ou senha incorretos" in response.data
