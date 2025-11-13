import pytest
from src.models import Transaction
from datetime import date

def test_recurring_transaction_management(client, db, logged_in_client):
    """
    Testa a criação, listagem e exclusão de transações recorrentes.
    """
    _, user_id, account_id, category_id = logged_in_client

    # Adicionar transação recorrente
    recurring_transaction = Transaction(
        description='Recurring Test', amount=100, type='saída', date=date.today(),
        recurring=True, recurrence_frequency='mensal',
        account_id=account_id, category_id=category_id, user_id=user_id
    )
    db.session.add(recurring_transaction)
    db.session.commit()

    # Listar transações recorrentes
    response = client.get('/recurring/')
    assert response.status_code == 200
    assert b'Recurring Test' in response.data

    # Excluir transação recorrente
    response = client.post(f'/recurring/delete/{recurring_transaction.id}')
    assert response.status_code == 302

    # Verificar se a transação foi excluída do banco de dados
    assert Transaction.query.get(recurring_transaction.id) is None
