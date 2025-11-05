import pytest
from src.main import app, db, User, Account, Category, Transaction
from datetime import date
import json

def test_summary_unauthenticated(test_client):
    """
    Testa se a rota da API retorna erro 401 para usuários não autenticados.
    """
    response = test_client.get('/api/summary')
    assert response.status_code == 401
    assert response.json['error'] == 'Acesso não autorizado'

def test_summary_authenticated_with_data(logged_in_client):
    """
    Testa se a rota da API retorna os dados corretos para um usuário autenticado.
    """
    client, user_id, account_id, category_id = logged_in_client

    # Criar algumas transações de teste no mês atual
    with app.app_context():
        today = date.today()
        cat_food = Category(name='Alimentação', type='saída', user_id=user_id)
        cat_transport = Category(name='Transporte', type='saída', user_id=user_id)
        db.session.add_all([cat_food, cat_transport])
        db.session.commit()

        t1 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_food.id, description='Supermercado', amount=150.75, type='saída', date=today)
        t2 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_food.id, description='Restaurante', amount=80.00, type='saída', date=today)
        t3 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_transport.id, description='Gasolina', amount=120.50, type='saída', date=today)
        # Transação de entrada (não deve aparecer no gráfico de despesas)
        t4 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Salário', amount=2000.00, type='entrada', date=today)
        db.session.add_all([t1, t2, t3, t4])
        db.session.commit()

    response = client.get('/api/summary')
    assert response.status_code == 200

    data = response.json
    # A ordem pode variar, então verificamos o conteúdo de forma mais flexível
    assert 'Alimentação' in data['labels']
    assert 'Transporte' in data['labels']

    # Verificar os totais
    food_index = data['labels'].index('Alimentação')
    transport_index = data['labels'].index('Transporte')

    assert data['data'][food_index] == pytest.approx(150.75 + 80.00)
    assert data['data'][transport_index] == pytest.approx(120.50)

    # Garantir que apenas 2 categorias de despesa foram retornadas
    assert len(data['labels']) == 2
