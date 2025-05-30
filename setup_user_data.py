import sys
sys.path.insert(0, '/app')
from src.main import app, db, User, Category, Account
import datetime

with app.app_context():
    # Obter o usuário existente
    user = User.query.filter_by(email='renatolelias@gmail.com').first()
    
    if user:
        # Verificar se já existem categorias para o usuário
        categories_count = Category.query.filter_by(user_id=user.id).count()
        
        if categories_count == 0:
            # Criar categorias padrão
            categories = [
                Category(name='Alimentação', type='saída', user_id=user.id),
                Category(name='Transporte', type='saída', user_id=user.id),
                Category(name='Moradia', type='saída', user_id=user.id),
                Category(name='Lazer', type='saída', user_id=user.id),
                Category(name='Saúde', type='saída', user_id=user.id),
                Category(name='Educação', type='saída', user_id=user.id),
                Category(name='Salário', type='entrada', user_id=user.id),
                Category(name='Investimentos', type='entrada', user_id=user.id),
                Category(name='Outros', type='entrada', user_id=user.id)
            ]
            db.session.bulk_save_objects(categories)
            db.session.commit()
            print("Categorias criadas com sucesso!")
        else:
            print("Categorias já existem!")
            
        # Verificar se já existem contas para o usuário
        accounts_count = Account.query.filter_by(user_id=user.id).count()
        
        if accounts_count == 0:
            # Criar contas padrão
            accounts = [
                Account(name='Carteira', type='carteira', balance=500.0, user_id=user.id, active=True),
                Account(name='Conta Corrente', type='conta_corrente', balance=2500.0, user_id=user.id, active=True),
                Account(name='Poupança', type='poupanca', balance=10000.0, user_id=user.id, active=True),
                Account(name='Cartão de Crédito', type='cartao_credito', balance=0.0, user_id=user.id, active=True)
            ]
            db.session.bulk_save_objects(accounts)
            db.session.commit()
            print("Contas criadas com sucesso!")
        else:
            print("Contas já existem!")
    else:
        print("Usuário não encontrado!")
