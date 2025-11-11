import pytest
from src.models import Budget, Category

def test_add_budget(client, db, logged_in_client):
    """
    Testa a criação de um novo orçamento.
    """
    _, _, _, category_id = logged_in_client

    response = client.post('/budgets/add', data={
        'category_id': category_id, 'amount': '800.00', 'month': '11', 'year': '2025'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Orçamento adicionado com sucesso!'

    assert Budget.query.filter_by(month=11, year=2025).first() is not None

def test_list_budgets(client, db, logged_in_client):
    """
    Testa a listagem de orçamentos.
    """
    _, user_id, _, category_id = logged_in_client
    category = Category.query.get(category_id)
    db.session.add(Budget(user_id=user_id, category_id=category_id, name=f"Orçamento para {category.name}", amount=500, month=10, year=2025))
    db.session.commit()

    response = client.get('/budgets/')
    assert response.status_code == 200
    assert bytes(category.name, 'utf-8') in response.data

def test_edit_budget(client, db, logged_in_client):
    """
    Testa a edição de um orçamento.
    """
    _, user_id, _, category_id = logged_in_client
    budget = Budget(user_id=user_id, category_id=category_id, name="Orçamento Antigo", amount=100, month=1, year=2025)
    db.session.add(budget)
    db.session.commit()

    response = client.post(f'/budgets/edit/{budget.id}', data={
        'category_id': category_id, 'amount': '150.50', 'month': '1', 'year': '2025'
    })
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Orçamento atualizado com sucesso!'

    db.session.refresh(budget)
    assert budget.amount == 150.50

def test_delete_budget(client, db, logged_in_client):
    """
    Testa a exclusão de um orçamento.
    """
    _, user_id, _, category_id = logged_in_client
    budget = Budget(user_id=user_id, category_id=category_id, name="Para Excluir", amount=200, month=3, year=2025)
    db.session.add(budget)
    db.session.commit()
    budget_id = budget.id

    response = client.post(f'/budgets/delete/{budget_id}')
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['_flashes'][0][1] == 'Orçamento excluído com sucesso!'

    assert Budget.query.get(budget_id) is None
