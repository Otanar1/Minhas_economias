import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!
from flask import Flask, render_template, redirect, url_for, session, flash, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import logging
from .utils import format_currency
from flask_migrate import Migrate
from src.models import db, User, Account, Category, Transaction, Dream, Budget

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'minhaseconomias2025secretkey')

# Configuração do banco de dados para produção
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', 'password')
    mysql_host = os.environ.get('MYSQL_HOST', 'db')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DB', 'minhas_economias')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 60,
        'pool_size': 10,
        'max_overflow': 20
    }

db.init_app(app)
migrate = Migrate(app, db)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            logger.info(f"Tentativa de login para o email: {email}")
            
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['email'] = user.email
                logger.info(f"Login bem-sucedido para o usuário: {user.id}")
                return redirect(url_for('dashboard.index'))
            else:
                flash('Email ou senha incorretos', 'error')
                logger.warning(f"Falha no login para o email: {email}")
        
        return render_template('auth/login.html')
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        flash('Ocorreu um erro ao processar o login. Por favor, tente novamente.', 'error')
        return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not name or not email or not password:
                flash('Todos os campos são obrigatórios', 'error')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash('As senhas não coincidem', 'error')
                return render_template('auth/register.html')
            
            existing_user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            if existing_user:
                flash('Este email já está em uso', 'error')
                return render_template('auth/register.html')
            
            new_user = User(
                name=name,
                email=email,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                updated_at=datetime.datetime.now(datetime.timezone.utc)
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            categories = [
                Category(name='Alimentação', type='saída', user_id=new_user.id),
                Category(name='Transporte', type='saída', user_id=new_user.id),
                Category(name='Moradia', type='saída', user_id=new_user.id),
                Category(name='Lazer', type='saída', user_id=new_user.id),
                Category(name='Saúde', type='saída', user_id=new_user.id),
                Category(name='Educação', type='saída', user_id=new_user.id),
                Category(name='Salário', type='entrada', user_id=new_user.id),
                Category(name='Investimentos', type='entrada', user_id=new_user.id),
                Category(name='Outros', type='entrada', user_id=new_user.id)
            ]
            db.session.bulk_save_objects(categories)
            
            accounts = [
                Account(name='Carteira', type='carteira', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Conta Corrente', type='conta_corrente', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Poupança', type='poupanca', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Cartão de Crédito', type='cartao_credito', balance=0.0, user_id=new_user.id, active=True)
            ]
            db.session.bulk__save_objects(accounts)
            
            db.session.commit()
            
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Erro no registro: {str(e)}")
        db.session.rollback()
        flash('Ocorreu um erro ao processar o registro. Por favor, tente novamente.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            
            if user:
                flash('Instruções para redefinição de senha foram enviadas para seu email', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Email não encontrado', 'error')
    except Exception as e:
        logger.error(f"Erro na recuperação de senha: {str(e)}")
        flash('Ocorreu um erro ao processar a recuperação de senha. Por favor, tente novamente.', 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user_id = session["user_id"]
        user = db.session.get(User, user_id)
        if not user:
            logger.error(f"Usuário com ID {user_id} não encontrado no banco de dados.")
            session.clear()
            return redirect(url_for("auth.login"))
        
        accounts = db.session.execute(db.select(Account).filter_by(user_id=user_id, active=True)).scalars().all()
        
        total_balance = sum(account.balance for account in accounts)
        
        recent_transactions = db.session.execute(
            db.select(Transaction)
            .filter_by(user_id=user_id)
            .order_by(Transaction.date.desc())
            .limit(5)
        ).scalars().all()

        accounts_formatted = [
            {'name': acc.name, 'balance_formatted': format_currency(acc.balance)}
            for acc in accounts
        ]
        total_balance_formatted = format_currency(total_balance)
        recent_transactions_formatted = [
            {
                'date_formatted': tx.date.strftime('%d/%m/%Y'),
                'description': tx.description,
                'category_name': tx.category.name if tx.category else 'Sem Categoria',
                'amount_formatted': format_currency(tx.amount)
            }
            for tx in recent_transactions
        ]
        
        return render_template("dashboard/index.html", 
                            user=user, 
                            accounts_formatted=accounts_formatted,
                            total_balance_formatted=total_balance_formatted,
                            recent_transactions_formatted=recent_transactions_formatted)
    except Exception as e:
        logger.error(f"Erro no dashboard: {str(e)}")
        flash('Ocorreu um erro ao carregar o dashboard. Por favor, tente novamente.', 'error')
        return redirect(url_for('auth.login'))

from src.routes.transactions import transactions_bp
from src.routes.api import api_bp
from src.routes.budgets import budgets_bp
from src.routes.dreams import dreams_bp
from src.routes.analysis import analysis_bp
from src.routes.accounts import accounts_bp
from src.routes.settings import settings_bp
from src.commands import register_commands
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(budgets_bp, url_prefix='/budgets')
app.register_blueprint(dreams_bp, url_prefix='/dreams')
app.register_blueprint(analysis_bp, url_prefix='/analysis')
app.register_blueprint(accounts_bp, url_prefix='/accounts')
app.register_blueprint(settings_bp, url_prefix='/settings')

register_commands(app)

@app.route('/')
def index_root():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
