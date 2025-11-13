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
from src.routes.categories import categories_bp
from src.routes.auth import auth_bp
from src.commands import register_commands

from flask import g

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id is not None else None

# Register the format_currency filter
app.jinja_env.filters['format_currency'] = format_currency

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(budgets_bp, url_prefix='/budgets')
app.register_blueprint(dreams_bp, url_prefix='/dreams')
app.register_blueprint(analysis_bp, url_prefix='/analysis')
app.register_blueprint(accounts_bp, url_prefix='/accounts')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(categories_bp, url_prefix='/categories')

from src.routes.recurring import recurring_bp
app.register_blueprint(recurring_bp, url_prefix='/recurring')

from src.routes.reports import reports_bp
app.register_blueprint(reports_bp, url_prefix='/reports')

register_commands(app)

@app.route('/')
def index_root():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.preferences and 'initial_screen' in user.preferences:
            return redirect(url_for(user.preferences['initial_screen']))
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
