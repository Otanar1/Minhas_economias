import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!
from flask import Flask, render_template, redirect, url_for, session, flash, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'minhaseconomias2025secretkey')

# Configuração do banco de dados para produção
if os.environ.get('DATABASE_URL'):
    # Usar o DATABASE_URL fornecido pelo ambiente
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Configuração para MySQL local (desenvolvimento)
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', 'password')
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DB', 'minhas_economias')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 60,
    'pool_size': 10,
    'max_overflow': 20
}

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Definição dos modelos
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    preferences = db.Column(db.JSON, default={})
    
    accounts = db.relationship('Account', backref='user', lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")
    dreams = db.relationship('Dream', backref='user', lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade="all, delete-orphan")
    categories = db.relationship('Category', backref='user', lazy=True, cascade="all, delete-orphan")

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # carteira, conta_corrente, poupanca, cartao_credito
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # entrada, saída
    
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # entrada, saída
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'date': self.date.isoformat() if self.date else None,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Dream(db.Model):
    __tablename__ = 'dreams'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # viagem, carro, eletrônico, casa, etc
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='ativo')  # ativo, concluído, cancelado

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Definição das rotas de autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            logger.info(f"Tentativa de login para o email: {email}")
            
            # Otimização: Consulta direta sem relacionamentos para melhorar performance
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
                password=generate_password_hash(password),
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Criar categorias padrão para o novo usuário
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
            
            # Criar contas padrão para o novo usuário
            accounts = [
                Account(name='Carteira', type='carteira', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Conta Corrente', type='conta_corrente', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Poupança', type='poupanca', balance=0.0, user_id=new_user.id, active=True),
                Account(name='Cartão de Crédito', type='cartao_credito', balance=0.0, user_id=new_user.id, active=True)
            ]
            db.session.bulk_save_objects(accounts)
            
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
                # Em um ambiente real, enviaríamos um email com link para redefinição de senha
                # Aqui, apenas simulamos o processo
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

# Definição das rotas de dashboard
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user_id = session["user_id"] # Corrigido: Indentação ajustada
        user = db.session.get(User, user_id) # Corrigido: Indentação ajustada
        if not user:
            logger.error(f"Usuário com ID {user_id} não encontrado no banco de dados.")
            session.clear()
            return redirect(url_for("auth.login"))
        
        # Otimização: Consultas separadas para melhorar performance
        accounts = db.session.execute(db.select(Account).filter_by(user_id=user_id, active=True)).scalars().all()
        
        # Calcular saldo total
        total_balance = sum(account.balance for account in accounts)
        
        # Obter transações recentes - limitando a 5 para melhorar performance
        recent_transactions = db.session.execute(
            db.select(Transaction)
            .filter_by(user_id=user_id)
            .order_by(Transaction.date.desc())
            .limit(5)
        ).scalars().all()
        
        return render_template("dashboard/index.html", 
                            user=user, # Passar o objeto user para o template
                            accounts=accounts, 
                            total_balance=total_balance,
                            recent_transactions=recent_transactions) # Corrigido: Removido 's)' extra
    except Exception as e:
        logger.error(f"Erro no dashboard: {str(e)}")
        flash('Ocorreu um erro ao carregar o dashboard. Por favor, tente novamente.', 'error')
        return redirect(url_for('auth.login'))

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

# Rota raiz
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

# Função para criar tabelas e dados iniciais
def setup_database():
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            
            # Verificar se já existem usuários
            user_count = db.session.query(db.func.count(User.id)).scalar()
            if user_count == 0:
                # Criar usuário de teste
                test_user = User(
                    name='Usuário de Teste',
                    email='renatolelias@gmail.com',
                    password=generate_password_hash('teste123'),
                    created_at=datetime.datetime.utcnow()
                )
                db.session.add(test_user)
                db.session.commit()
                
                # Criar categorias padrão
                categories = [
                    Category(name='Alimentação', type='saída', user_id=test_user.id),
                    Category(name='Transporte', type='saída', user_id=test_user.id),
                    Category(name='Moradia', type='saída', user_id=test_user.id),
                    Category(name='Lazer', type='saída', user_id=test_user.id),
                    Category(name='Saúde', type='saída', user_id=test_user.id),
                    Category(name='Educação', type='saída', user_id=test_user.id),
                    Category(name='Salário', type='entrada', user_id=test_user.id),
                    Category(name='Investimentos', type='entrada', user_id=test_user.id),
                    Category(name='Outros', type='entrada', user_id=test_user.id)
                ]
                db.session.bulk_save_objects(categories)
                db.session.commit()
                
                # Criar contas padrão
                accounts = [
                    Account(name='Carteira', type='carteira', balance=500.0, user_id=test_user.id, active=True),
                    Account(name='Conta Corrente', type='conta_corrente', balance=2500.0, user_id=test_user.id, active=True),
                    Account(name='Poupança', type='poupanca', balance=10000.0, user_id=test_user.id, active=True),
                    Account(name='Cartão de Crédito', type='cartao_credito', balance=0.0, user_id=test_user.id, active=True)
                ]
                db.session.bulk_save_objects(accounts)
                db.session.commit()
                
                logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"Erro na inicialização do banco de dados: {str(e)}")
        raise

# Executar setup do banco de dados
setup_database()

# Iniciar o servidor Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
