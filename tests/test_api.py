import pytest
from src.main import app, db, User, Account, Category, Transaction, Budget
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
    Testa se a rota da API retorna os dados corretos de progresso de orçamento e gráfico.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        today = date.today()
        cat_food = Category(name='Alimentação', type='saída', user_id=user_id)
        cat_transport = Category(name='Transporte', type='saída', user_id=user_id)
        cat_lazer = Category(name='Lazer', type='saída', user_id=user_id)
        db.session.add_all([cat_food, cat_transport, cat_lazer])
        db.session.commit()

        # Orçamentos
        budget_food = Budget(user_id=user_id, category_id=cat_food.id, name="Orçamento Alimentação", amount=800, month=today.month, year=today.year)
        budget_transport = Budget(user_id=user_id, category_id=cat_transport.id, name="Orçamento Transporte", amount=300, month=today.month, year=today.year)
        budget_lazer = Budget(user_id=user_id, category_id=cat_lazer.id, name="Orçamento Lazer", amount=400, month=today.month, year=today.year)
        db.session.add_all([budget_food, budget_transport, budget_lazer])

        # Transações com descrição
        t1 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_food.id, description='Supermercado', amount=150.75, type='saída', date=today)
        t2 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_food.id, description='Restaurante', amount=80.00, type='saída', date=today)
        t3 = Transaction(user_id=user_id, account_id=account_id, category_id=cat_transport.id, description='Gasolina', amount=120.50, type='saída', date=today)
        db.session.add_all([t1, t2, t3])
        db.session.commit()

    response = client.get('/api/summary')
    assert response.status_code == 200

    data = response.json

    # Verificar progresso do orçamento
    assert len(data['budget_progress']) >= 3
    progress_map = {item['category']: item for item in data['budget_progress']}

    assert progress_map['Alimentação']['budgeted'] == 800
    assert progress_map['Alimentação']['spent'] == pytest.approx(150.75 + 80.00)

    assert progress_map['Transporte']['budgeted'] == 300
    assert progress_map['Transporte']['spent'] == pytest.approx(120.50)

    assert progress_map['Lazer']['budgeted'] == 400
    assert progress_map['Lazer']['spent'] == 0

    # Verificar dados do gráfico
    chart_data = data['expense_chart']
    assert len(chart_data['labels']) == 2
    assert 'Alimentação' in chart_data['labels']
    assert 'Transporte' in chart_data['labels']

    food_index = chart_data['labels'].index('Alimentação')
    transport_index = chart_data['labels'].index('Transporte')

    assert chart_data['data'][food_index] == pytest.approx(230.75)
    assert chart_data['data'][transport_index] == pytest.approx(120.50)
