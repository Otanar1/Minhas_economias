import pytest
from src.main import app, db
from src.models import User, Category

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

def test_category_management(client):
    # Create a user and log in
    user = User(name='Test User', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Add a category
    client.post('/categories/add', data={'name': 'Test Category', 'type': 'saída'}, follow_redirects=True)

    # Verify the category was added
    category = Category.query.filter_by(name='Test Category').first()
    assert category is not None
    assert category.type == 'saída'

    # Edit the category
    client.post(f'/categories/edit/{category.id}', data={'name': 'Updated Category', 'type': 'entrada'}, follow_redirects=True)

    # Verify the category was updated
    updated_category = Category.query.get(category.id)
    assert updated_category.name == 'Updated Category'
    assert updated_category.type == 'entrada'

    # Delete the category
    client.post(f'/categories/delete/{category.id}', follow_redirects=True)

    # Verify the category was deleted
    deleted_category = Category.query.get(category.id)
    assert deleted_category is None
