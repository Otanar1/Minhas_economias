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
