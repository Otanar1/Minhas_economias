from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.account import Account
from src.models.transaction import Transaction
from datetime import datetime, date
import calendar

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar contas do usuário
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    # Obter parâmetros de filtro
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    account_id = request.args.get('account_id')
    
    # Converter para inteiros
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Definir período
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Construir query base
    query = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= first_day,
        Transaction.date <= last_day
    )
    
    # Filtrar por conta se especificado
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    # Executar query
    transactions = query.order_by(Transaction.date).all()
    
    # Calcular totais
    total_income = sum(t.amount for t in transactions if t.type == 'entrada')
    total_expense = sum(t.amount for t in transactions if t.type == 'saída')
    balance = total_income - total_expense
    
    # Renderizar template
    return render_template('transactions/index.html',
                          accounts=accounts,
                          transactions=transactions,
                          total_income=total_income,
                          total_expense=total_expense,
                          balance=balance,
                          month=month,
                          year=year)

@transactions_bp.route('/create', methods=['GET', 'POST'])
def create():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar contas do usuário
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        transaction_date = request.form.get('date')
        transaction_type = request.form.get('type')
        category_id = request.form.get('category_id')
        consolidated = request.form.get('consolidated') == 'on'
        recurring = request.form.get('recurring') == 'on'
        recurrence_frequency = request.form.get('recurrence_frequency')
        
        # Validar dados
        if not account_id or not description or not amount or not transaction_date or not transaction_type:
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return render_template('transactions/create.html', accounts=accounts)
        
        try:
            amount = float(amount)
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Valor ou data inválidos', 'error')
            return render_template('transactions/create.html', accounts=accounts)
        
        # Criar nova transação
        new_transaction = Transaction(
            user_id=session['user_id'],
            account_id=account_id,
            description=description,
            amount=amount,
            date=transaction_date,
            type=transaction_type,
            category_id=category_id if category_id else None,
            consolidated=consolidated,
            recurring=recurring,
            recurrence_frequency=recurrence_frequency if recurring else None
        )
        
        db.session.add(new_transaction)
        
        # Atualizar saldo da conta se a transação for consolidada
        if consolidated:
            account = Account.query.get(account_id)
            if transaction_type == 'entrada':
                account.balance += amount
            else:
                account.balance -= amount
        
        db.session.commit()
        
        flash('Transação criada com sucesso!', 'success')
        return redirect(url_for('transactions.index'))
    
    return render_template('transactions/create.html', accounts=accounts)

@transactions_bp.route('/<int:transaction_id>/edit', methods=['GET', 'POST'])
def edit(transaction_id):
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar transação
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=session['user_id']).first_or_404()
    
    # Buscar contas do usuário
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        transaction_date = request.form.get('date')
        transaction_type = request.form.get('type')
        category_id = request.form.get('category_id')
        consolidated = request.form.get('consolidated') == 'on'
        recurring = request.form.get('recurring') == 'on'
        recurrence_frequency = request.form.get('recurrence_frequency')
        
        # Validar dados
        if not account_id or not description or not amount or not transaction_date or not transaction_type:
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return render_template('transactions/edit.html', transaction=transaction, accounts=accounts)
        
        try:
            amount = float(amount)
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Valor ou data inválidos', 'error')
            return render_template('transactions/edit.html', transaction=transaction, accounts=accounts)
        
        # Se a transação era consolidada, reverter o efeito no saldo da conta
        if transaction.consolidated:
            old_account = Account.query.get(transaction.account_id)
            if transaction.type == 'entrada':
                old_account.balance -= transaction.amount
            else:
                old_account.balance += transaction.amount
        
        # Atualizar transação
        transaction.account_id = account_id
        transaction.description = description
        transaction.amount = amount
        transaction.date = transaction_date
        transaction.type = transaction_type
        transaction.category_id = category_id if category_id else None
        transaction.consolidated = consolidated
        transaction.recurring = recurring
        transaction.recurrence_frequency = recurrence_frequency if recurring else None
        
        # Se a transação for consolidada, atualizar o saldo da conta
        if consolidated:
            account = Account.query.get(account_id)
            if transaction_type == 'entrada':
                account.balance += amount
            else:
                account.balance -= amount
        
        db.session.commit()
        
        flash('Transação atualizada com sucesso!', 'success')
        return redirect(url_for('transactions.index'))
    
    return render_template('transactions/edit.html', transaction=transaction, accounts=accounts)

@transactions_bp.route('/<int:transaction_id>/delete', methods=['POST'])
def delete(transaction_id):
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar transação
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=session['user_id']).first_or_404()
    
    # Se a transação era consolidada, reverter o efeito no saldo da conta
    if transaction.consolidated:
        account = Account.query.get(transaction.account_id)
        if transaction.type == 'entrada':
            account.balance -= transaction.amount
        else:
            account.balance += transaction.amount
    
    # Excluir transação
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transação excluída com sucesso!', 'success')
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/api/list')
def api_list():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Obter parâmetros de filtro
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    account_id = request.args.get('account_id')
    
    # Converter para inteiros
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Definir período
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Construir query base
    query = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= first_day,
        Transaction.date <= last_day
    )
    
    # Filtrar por conta se especificado
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    # Executar query
    transactions = query.order_by(Transaction.date).all()
    
    # Converter para dicionário
    transactions_data = [transaction.to_dict() for transaction in transactions]
    
    return jsonify(transactions_data)
