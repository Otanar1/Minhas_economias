import pytest
from src.main import app, db
from src.models import User, Transaction, Account, Category
import datetime

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

def test_recurring_transaction_management(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    account = Account(name='Test Account', type='corrente', balance=1000, user=user)
    category = Category(name='Test Category', type='saída', user=user)
    db.session.add_all([user, account, category])
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Add a recurring transaction
    recurring_transaction = Transaction(
        description='Recurring Test',
        amount=100,
        type='saída',
        date=datetime.date.today(),
        recurring=True,
        recurrence_frequency='mensal',
        account=account,
        category=category,
        user=user
    )
    db.session.add(recurring_transaction)
    db.session.commit()

    # List recurring transactions
    response = client.get('/recurring/')
    assert b'Recurring Test' in response.data

    # Delete the recurring transaction
    client.post(f'/recurring/delete/{recurring_transaction.id}', follow_redirects=True)

    # Verify the recurring transaction was deleted
    deleted_transaction = Transaction.query.get(recurring_transaction.id)
    assert deleted_transaction is None
