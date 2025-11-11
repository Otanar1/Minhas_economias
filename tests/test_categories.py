import pytest
from src.models import Category

def test_category_management(client, db, logged_in_client):
    """
    Testa a criação, edição e exclusão de categorias, verificando o estado do banco de dados.
    """
    _, user_id, _, _ = logged_in_client

    # Adicionar categoria
    client.post('/categories/add', data={'name': 'Test Category', 'type': 'saída'})
    category = Category.query.filter_by(name='Test Category', user_id=user_id).first()
    assert category is not None
    assert category.type == 'saída'

    # Editar categoria
    client.post(f'/categories/edit/{category.id}', data={'name': 'Updated Category', 'type': 'entrada'})
    db.session.refresh(category)
    assert category.name == 'Updated Category'
    assert category.type == 'entrada'

    # Excluir categoria
    client.post(f'/categories/delete/{category.id}')
    assert Category.query.get(category.id) is None
