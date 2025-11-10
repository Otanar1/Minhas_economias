from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from src.models import User, db, Account
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar informações do usuário
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Buscar contas do usuário
    accounts = db.session.execute(db.select(Account).filter_by(user_id=session['user_id'], active=True)).scalars().all()
    
    # Calcular saldo total
    total_balance = sum(account.balance for account in accounts)
    
    # Renderizar o dashboard principal
    return render_template('dashboard/index.html', 
                          user=user, 
                          accounts=accounts, 
                          total_balance=total_balance)
