from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.account import Account
from datetime import datetime

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar contas do usuário
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    return render_template('accounts/index.html', accounts=accounts)

@accounts_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        account_type = request.form.get('type')
        initial_balance = float(request.form.get('initial_balance', 0))
        
        # Validar dados
        if not name or not account_type:
            flash('Nome e tipo de conta são obrigatórios', 'error')
            return render_template('accounts/create.html')
        
        # Criar nova conta
        new_account = Account(
            user_id=session['user_id'],
            name=name,
            type=account_type,
            balance=initial_balance
        )
        
        db.session.add(new_account)
        db.session.commit()
        
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('accounts/create.html')

@accounts_bp.route('/<int:account_id>/edit', methods=['GET', 'POST'])
def edit(account_id):
    # Buscar conta
    account = Account.query.filter_by(id=account_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        account_type = request.form.get('type')
        
        # Validar dados
        if not name or not account_type:
            flash('Nome e tipo de conta são obrigatórios', 'error')
            return render_template('accounts/edit.html', account=account)
        
        # Atualizar conta
        account.name = name
        account.type = account_type
        db.session.commit()
        
        flash('Conta atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('accounts/edit.html', account=account)

@accounts_bp.route('/<int:account_id>/delete', methods=['POST'])
def delete(account_id):
    # Buscar conta
    account = Account.query.filter_by(id=account_id, user_id=session['user_id']).first_or_404()
    
    # Desativar conta (soft delete)
    account.active = False
    db.session.commit()
    
    flash('Conta removida com sucesso!', 'success')
    return redirect(url_for('dashboard.index'))

@accounts_bp.route('/api/list')
def api_list():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Buscar contas do usuário
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    # Converter para dicionário
    accounts_data = [account.to_dict() for account in accounts]
    
    return jsonify(accounts_data)
