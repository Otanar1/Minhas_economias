import pytest
from src.main import app, db

@pytest.fixture(scope='function')
def test_client():
    """
    Fixture centralizada para configurar a aplicação e o banco de dados para os testes.
    - Usa 'scope=function' para garantir que esta fixture seja executada para cada função de teste.
    - Limpa e recria o banco de dados para cada teste, garantindo total isolamento.
    """
    # Configuração do app para o modo de teste
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Desativa CSRF para simplificar os testes de formulário

    with app.test_client() as client:
        with app.app_context():
            # Limpa o banco de dados completamente
            db.drop_all()
            # Cria todas as tabelas
            db.create_all()

        # O 'yield' passa o cliente de teste para a função de teste
        yield client

        # Código de limpeza executado após cada teste
        with app.app_context():
            # Garante que a sessão seja limpa
            db.session.remove()
            # Limpa o banco de dados novamente
            db.drop_all()

@pytest.fixture
def logged_in_client(test_client):
    """
    Cria e autentica um usuário, retornando o cliente e os IDs dos dados criados.
    """
    from src.main import User, Account, Category
    from werkzeug.security import generate_password_hash

    with app.app_context():
        user = User(name='Test User', email='test@example.com', password=generate_password_hash('password123'))
        db.session.add(user)
        db.session.commit()

        account = Account(name='Test Account', balance=1000.0, user_id=user.id, type='conta_corrente')
        db.session.add(account)

        category = Category(name='Test Category', type='saída', user_id=user.id)
        db.session.add(category)
        db.session.commit()

        user_id = user.id
        account_id = account.id
        category_id = category.id

    test_client.post('/auth/login', data={'email': 'test@example.com', 'password': 'password123'}, follow_redirects=True)

    return test_client, user_id, account_id, category_id
