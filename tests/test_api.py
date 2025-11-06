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

def test_balance_evolution_api(logged_in_client):
    """
    Testa o endpoint da API de evolução de saldo.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        # Criar transações em datas diferentes
        t1 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Salário', amount=2000, type='entrada', date=date(2025, 1, 5))
        t2 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Aluguel', amount=800, type='saída', date=date(2025, 1, 10))
        t3 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Supermercado', amount=300, type='saída', date=date(2025, 1, 15))
        # Duas transações no mesmo dia
        t4 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Freela', amount=500, type='entrada', date=date(2025, 1, 20))
        t5 = Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Jantar', amount=100, type='saída', date=date(2025, 1, 20))
        db.session.add_all([t1, t2, t3, t4, t5])
        db.session.commit()

    response = client.get('/api/balance_evolution')
    assert response.status_code == 200

    data = response.json

    # Verificar os rótulos (datas)
    expected_labels = [
        '2025-01-05',
        '2025-01-10',
        '2025-01-15',
        '2025-01-20'
    ]
    assert data['labels'] == expected_labels

    # Verificar os dados (saldos cumulativos)
    expected_data = [
        2000.00, # Após t1
        1200.00, # Após t2
        900.00,  # Após t3
        1300.00  # Após t4 e t5 (2000 - 800 - 300 + 500 - 100)
    ]
    assert data['data'] == expected_data
