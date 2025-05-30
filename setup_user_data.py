import sys
sys.path.insert(0, '/app')
from src.main import app, db, User, Category, Account
import datetime

with app.app_context():
    # Obter o usuário existente
    user = User.query.filter_by(email='renatolelias@gmail.com').first()
    
    if user:
        # --- Gerenciamento de Categorias ---
        print("Verificando categorias...")
        default_categories = {
            'Alimentação': 'saída',
            'Transporte': 'saída',
            'Moradia': 'saída',
            'Lazer': 'saída',
            'Saúde': 'saída',
            'Educação': 'saída',
            'Salário': 'entrada',
            'Investimentos': 'entrada',
            'Outros': 'entrada'
        }
        existing_categories = {c.name for c in Category.query.filter_by(user_id=user.id).all()}
        
        new_categories = []
        for name, type in default_categories.items():
            if name not in existing_categories:
                new_categories.append(Category(name=name, type=type, user_id=user.id))
                print(f"  - Categoria '{name}' será criada.")
        
        if new_categories:
            db.session.bulk_save_objects(new_categories)
            db.session.commit()
            print("Novas categorias padrão criadas com sucesso!")
        else:
            print("Todas as categorias padrão já existem.")

        # --- Gerenciamento de Contas e Saldos ---
        print("\nVerificando contas e atualizando saldos...")
        default_accounts = {
            'Carteira': {'type': 'carteira', 'balance': 500.0},
            'Conta Corrente': {'type': 'conta_corrente', 'balance': 2500.0},
            'Poupança': {'type': 'poupanca', 'balance': 10000.0},
            'Cartão de Crédito': {'type': 'cartao_credito', 'balance': 0.0} # Saldo inicial de cartão é 0
        }

        existing_accounts = {acc.name: acc for acc in Account.query.filter_by(user_id=user.id).all()}
        
        accounts_to_add = []
        accounts_to_update = []

        for name, details in default_accounts.items():
            if name in existing_accounts:
                account = existing_accounts[name]
                # Atualiza o saldo apenas se for diferente do padrão (evita commits desnecessários)
                # Para cartão de crédito, o saldo representa a fatura, então não atualizamos aqui.
                if account.type != 'cartao_credito' and account.balance != details['balance']:
                    print(f"  - Atualizando saldo da conta '{name}' para {details['balance']:.2f}")
                    account.balance = details['balance']
                    accounts_to_update.append(account)
                elif account.type == 'cartao_credito':
                     print(f"  - Conta '{name}' (Cartão de Crédito) já existe. Saldo não será alterado por este script.")
                else:
                    print(f"  - Conta '{name}' já existe com saldo correto.")
            else:
                print(f"  - Conta '{name}' será criada com saldo {details['balance']:.2f}")
                accounts_to_add.append(
                    Account(name=name, type=details['type'], balance=details['balance'], user_id=user.id, active=True)
                )

        if accounts_to_add:
            db.session.bulk_save_objects(accounts_to_add)
            print(f"{len(accounts_to_add)} nova(s) conta(s) padrão criada(s)!")
            
        if accounts_to_update:
             print(f"{len(accounts_to_update)} conta(s) existente(s) teve(iveram) o saldo atualizado.")

        if not accounts_to_add and not accounts_to_update:
            print("Todas as contas padrão já existem com saldos corretos ou são cartões de crédito.")
        
        db.session.commit() # Salva as alterações (criação e/ou atualização)
        print("\nConfiguração de dados do usuário concluída.")

    else:
        print("Usuário 'renatolelias@gmail.com' não encontrado! Execute init_db.py primeiro.")

