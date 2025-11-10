import pytest
from src.main import app, db
from src.models import User, Transaction, Account, Category
import datetime
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_reports(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    account = Account(name='Test Account', type='corrente', balance=1000, user=user)
    category = Category(name='Test Category', type='saída', user=user)
    db.session.add_all([user, account, category])
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Add a transaction
    transaction = Transaction(
        description='Test Transaction',
        amount=100,
        type='saída',
        date=datetime.date.today(),
        account=account,
        category=category,
        user=user
    )
    db.session.add(transaction)
    db.session.commit()

    # Test summary report
    response = client.post('/api/reports/summary', json={
        'start_date': datetime.date.today().isoformat(),
        'end_date': datetime.date.today().isoformat()
    })
    data = json.loads(response.data)
    assert data['total_expenses'] == 100
    assert data['expenses_by_category'][0]['category'] == 'Test Category'

    # Test CSV export
    response = client.post('/api/reports/export_csv', json={
        'start_date': datetime.date.today().isoformat(),
        'end_date': datetime.date.today().isoformat()
    })
    assert response.status_code == 200
    assert 'text/csv' in response.content_type
