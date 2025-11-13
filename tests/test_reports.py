import pytest
from src.models import Transaction
from datetime import date
import json

def test_reports(client, db, logged_in_client):
    """
    Testa a geração de relatórios e a exportação em CSV.
    """
    _, user_id, account_id, category_id = logged_in_client

    # Adicionar transação
    transaction = Transaction(
        description='Test Transaction',
        amount=100,
        type='saída',
        date=date.today(),
        account_id=account_id,
        category_id=category_id,
        user_id=user_id
    )
    db.session.add(transaction)
    db.session.commit()

    # Testar relatório de resumo
    response = client.post('/api/reports/summary', json={
        'start_date': date.today().isoformat(),
        'end_date': date.today().isoformat()
    })
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['total_expenses'] == 100
    assert len(data['expenses_by_category']) > 0
    assert data['expenses_by_category'][0]['category'] == 'Test Category'

    # Testar exportação CSV
    response = client.post('/api/reports/export_csv', json={
        'start_date': date.today().isoformat(),
        'end_date': date.today().isoformat()
    })
    assert response.status_code == 200
    assert 'text/csv' in response.content_type
    assert b'Test Transaction' in response.data
