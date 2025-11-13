import pytest
from src.models import Transaction, Budget, Category
from datetime import date, timedelta
import json

def test_summary_unauthenticated(client):
    """
    Testa se a rota da API retorna erro 401 para usuários não autenticados.
    """
    response = client.get('/api/summary')
    assert response.status_code == 401
    assert response.json['error'] == 'Acesso não autorizado'

def test_summary_authenticated_with_data(client, db, logged_in_client):
    """
    Testa se a rota da API retorna os dados corretos de progresso de orçamento e gráfico.
    """
    _, user_id, account_id, _ = logged_in_client

    today = date.today()
    cat_food = Category(name='Alimentação', type='saída', user_id=user_id)
    cat_transport = Category(name='Transporte', type='saída', user_id=user_id)
    db.session.add_all([cat_food, cat_transport])
    db.session.commit()

    Budget.query.delete() # Limpar orçamentos anteriores
    db.session.add(Budget(user_id=user_id, category_id=cat_food.id, name="Orçamento Alimentação", amount=800, month=today.month, year=today.year))
    db.session.add(Budget(user_id=user_id, category_id=cat_transport.id, name="Orçamento Transporte", amount=300, month=today.month, year=today.year))

    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=cat_food.id, description='Supermercado', amount=150.75, type='saída', date=today))
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=cat_transport.id, description='Gasolina', amount=120.50, type='saída', date=today))
    db.session.commit()

    response = client.get('/api/summary')
    assert response.status_code == 200

    data = response.json

    assert len(data['budget_progress']) >= 2
    progress_map = {item['category']: item for item in data['budget_progress']}
    assert progress_map['Alimentação']['budgeted'] == 800
    assert progress_map['Alimentação']['spent'] == pytest.approx(150.75)

    chart_data = data['expense_chart']
    assert 'Alimentação' in chart_data['labels']
    assert 'Transporte' in chart_data['labels']

def test_balance_evolution_api(client, db, logged_in_client):
    """
    Testa o endpoint da API de evolução de saldo.
    """
    _, user_id, account_id, category_id = logged_in_client

    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Salário', amount=2000, type='entrada', date=date(2025, 1, 5)))
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Aluguel', amount=800, type='saída', date=date(2025, 1, 10)))
    db.session.commit()

    response = client.get('/api/balance_evolution')
    assert response.status_code == 200
    data = response.json
    assert data['labels'] == ['2025-01-05', '2025-01-10']
    assert data['data'] == [2000.00, 1200.00]

def test_monthly_summary(client, db, logged_in_client):
    """
    Testa o endpoint de resumo mensal com dados.
    """
    _, user_id, account_id, category_id = logged_in_client

    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Salário Antigo', type='entrada', amount=1000, date=date.today() - timedelta(days=45)))
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Aluguel Antigo', type='saída', amount=200, date=date.today() - timedelta(days=40)))
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Salário Atual', type='entrada', amount=500, date=date.today()))
    db.session.add(Transaction(user_id=user_id, account_id=account_id, category_id=category_id, description='Compra Atual', type='saída', amount=100, date=date.today()))
    db.session.commit()

    response = client.get(f'/api/monthly_summary?year={date.today().year}&month={date.today().month}')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['opening_balance'] == 800
    assert data['monthly_income'] == 500
    assert data['monthly_expenses'] == 100
