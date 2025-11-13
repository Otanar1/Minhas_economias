import pytest
from src.main import app as create_app
from src.models import db as _db

@pytest.fixture(scope='session')
def app():
    """Cria uma instância da aplicação Flask para a sessão de testes."""
    app = create_app
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-for-sessions"
    })
    return app

@pytest.fixture(scope='function')
def db(app):
    """Cria e limpa o banco de dados para cada função de teste."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    """Cria um cliente de teste para cada função."""
    return app.test_client()

@pytest.fixture
def logged_in_client(client, db):
    """
    Cria um usuário, hasheia a senha, faz o login e retorna o cliente e os IDs.
    """
    from src.models import User, Account, Category

    user = User(name='Test User', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    account = Account(name='Test Account', balance=1000.0, user_id=user.id, type='conta_corrente')
    db.session.add(account)

    category = Category(name='Test Category', type='saída', user_id=user.id)
    db.session.add(category)
    db.session.commit()

    client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password123'})

    # Retorna o ID do usuário, não o objeto
    return client, user.id, account.id, category.id
