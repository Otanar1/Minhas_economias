import pytest
from src.main import app, db, User, Budget, Category

def test_add_budget(logged_in_client):
    """
    Testa a criação de um novo orçamento.
    """
    client, user_id, account_id, category_id = logged_in_client

    response = client.post('/budgets/add', data={
        'category_id': category_id,
        'amount': '800.00',
        'month': '11',
        'year': '2025'
    })

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Orçamento adicionado com sucesso!'

    with app.app_context():
        budget = Budget.query.one()
        assert budget.amount == 800.00
        assert budget.month == 11
        assert budget.year == 2025
        assert budget.category_id == category_id

def test_list_budgets(logged_in_client):
    """
    Testa a listagem de orçamentos.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        category = db.session.get(Category, category_id)
        category_name = category.name
        b1 = Budget(user_id=user_id, category_id=category_id, name=f"Orçamento para {category_name}", amount=500, month=10, year=2025)
        db.session.add(b1)
        db.session.commit()

    response = client.get('/budgets/')

    assert response.status_code == 200
    assert b"Meus Or\xc3\xa7amentos" in response.data
    assert bytes(category_name, 'utf-8') in response.data
    assert b"500" in response.data

def test_edit_budget(logged_in_client):
    """
    Testa a edição de um orçamento.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        budget = Budget(user_id=user_id, category_id=category_id, name="Orçamento a ser editado", amount=100, month=1, year=2025)
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id

    response = client.post(f'/budgets/edit/{budget_id}', data={
        'category_id': category_id,
        'amount': '150.50',
        'month': '2',
        'year': '2026'
    })

    assert response.status_code == 302

    with app.app_context():
        edited_budget = db.session.get(Budget, budget_id)
        assert edited_budget.amount == 150.50
        assert edited_budget.month == 2
        assert edited_budget.year == 2026

def test_delete_budget(logged_in_client):
    """
    Testa a exclusão de um orçamento.
    """
    client, user_id, account_id, category_id = logged_in_client

    with app.app_context():
        budget = Budget(user_id=user_id, category_id=category_id, name="Orçamento a ser excluído", amount=200, month=3, year=2025)
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id

    response = client.post(f'/budgets/delete/{budget_id}')

    assert response.status_code == 302

    with app.app_context():
        deleted_budget = db.session.get(Budget, budget_id)
        assert deleted_budget is None
