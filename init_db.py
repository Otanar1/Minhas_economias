import sys
import os
import datetime
import logging
from werkzeug.security import generate_password_hash

# Adicionar o diretório do projeto ao sys.path para importação correta
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.main import app, db, User, Category, Account
except ImportError as e:
    logging.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """
    Inicializa o banco de dados:
    1. Cria todas as tabelas com base nos modelos definidos.
    2. Cria um usuário de teste se não existir.
    3. Cria categorias e contas padrão para o usuário de teste.
    """
    try:
        with app.app_context():
            logger.info("Iniciando a configuração do banco de dados...")

            # 1. Criar todas as tabelas
            db.create_all()
            logger.info("Tabelas criadas (ou já existentes).")

            # 2. Verificar e criar usuário de teste
            user_email = 'renatolelias@gmail.com'
            user = db.session.query(User).filter_by(email=user_email).first()

            if not user:
                logger.info(f"Usuário '{user_email}' não encontrado. Criando...")
                user = User(
                    name='Usuário de Teste',
                    email=user_email,
                    password=generate_password_hash('teste123'),
                    created_at=datetime.datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"Usuário '{user_email}' criado com sucesso.")
            else:
                logger.info(f"Usuário '{user_email}' já existe.")

            # 3. Criar categorias e contas padrão (apenas se o usuário foi recém-criado)
            # Para garantir a idempotência, verificamos se as categorias já existem
            existing_categories = {c.name for c in db.session.query(Category).filter_by(user_id=user.id).all()}
            default_categories = {
                'Alimentação': 'saída', 'Transporte': 'saída', 'Moradia': 'saída',
                'Lazer': 'saída', 'Saúde': 'saída', 'Educação': 'saída',
                'Salário': 'entrada', 'Investimentos': 'entrada', 'Outros': 'entrada'
            }

            new_categories = []
            for name, type in default_categories.items():
                if name not in existing_categories:
                    new_categories.append(Category(name=name, type=type, user_id=user.id))

            if new_categories:
                db.session.bulk_save_objects(new_categories)
                db.session.commit()
                logger.info("Categorias padrão criadas com sucesso.")

            # Verificar e criar contas padrão
            existing_accounts = {a.name for a in db.session.query(Account).filter_by(user_id=user.id).all()}
            default_accounts = {
                'Carteira': {'type': 'carteira', 'balance': 500.0},
                'Conta Corrente': {'type': 'conta_corrente', 'balance': 2500.0},
                'Poupança': {'type': 'poupanca', 'balance': 10000.0},
                'Cartão de Crédito': {'type': 'cartao_credito', 'balance': 0.0}
            }

            new_accounts = []
            for name, details in default_accounts.items():
                if name not in existing_accounts:
                    new_accounts.append(
                        Account(name=name, type=details['type'], balance=details['balance'], user_id=user.id, active=True)
                    )

            if new_accounts:
                db.session.bulk_save_objects(new_accounts)
                db.session.commit()
                logger.info("Contas padrão criadas com sucesso.")

            logger.info("Configuração do banco de dados concluída com sucesso!")

    except Exception as e:
        logger.error(f"Erro durante a inicialização do banco de dados: {e}")
        # Em caso de erro, faz rollback para não deixar o banco em estado inconsistente
        db.session.rollback()
        sys.exit(1)

if __name__ == '__main__':
    setup_database()
