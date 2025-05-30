from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.budget import Budget
from src.models.category import Category
from src.models.transaction import Transaction
from datetime import datetime, date
import calendar

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obter mês e ano atuais ou dos parâmetros
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Buscar orçamentos do usuário para o mês/ano selecionado
    budgets = Budget.query.filter_by(
        user_id=session['user_id'],
        month=month,
        year=year
    ).all()
    
    # Buscar categorias do usuário
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    
    # Definir período
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Buscar transações do período para comparar com orçamentos
    transactions = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= first_day,
        Transaction.date <= last_day
    ).all()
    
    # Calcular gastos por categoria
    category_expenses = {}
    for transaction in transactions:
        if transaction.type == 'saída' and transaction.category_id:
            if transaction.category_id not in category_expenses:
                category_expenses[transaction.category_id] = 0
            category_expenses[transaction.category_id] += transaction.amount
    
    # Calcular totais
    total_budget = sum(budget.amount for budget in budgets)
    total_spent = sum(category_expenses.values())
    
    return render_template('budgets/index.html',
                          budgets=budgets,
                          categories=categories,
                          category_expenses=category_expenses,
                          total_budget=total_budget,
                          total_spent=total_spent,
                          month=month,
                          year=year)

@budgets_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        month = request.form.get('month')
        year = request.form.get('year')
        category_id = request.form.get('category_id')
        
        # Validar dados
        if not name or not amount or not month or not year:
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('budgets.create'))
        
        try:
            amount = float(amount)
            month = int(month)
            year = int(year)
        except ValueError:
            flash('Valores inválidos', 'error')
            return redirect(url_for('budgets.create'))
        
        # Criar novo orçamento
        new_budget = Budget(
            user_id=session['user_id'],
            name=name,
            amount=amount,
            month=month,
            year=year,
            category_id=category_id if category_id else None
        )
        
        db.session.add(new_budget)
        db.session.commit()
        
        flash('Orçamento criado com sucesso!', 'success')
        return redirect(url_for('budgets.index', month=month, year=year))
    
    # Buscar categorias do usuário
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('budgets/create.html', 
                          categories=categories,
                          current_month=datetime.now().month,
                          current_year=datetime.now().year)

@budgets_bp.route('/<int:budget_id>/edit', methods=['GET', 'POST'])
def edit(budget_id):
    # Buscar orçamento
    budget = Budget.query.filter_by(id=budget_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        month = request.form.get('month')
        year = request.form.get('year')
        category_id = request.form.get('category_id')
        
        # Validar dados
        if not name or not amount or not month or not year:
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('budgets.edit', budget_id=budget_id))
        
        try:
            amount = float(amount)
            month = int(month)
            year = int(year)
        except ValueError:
            flash('Valores inválidos', 'error')
            return redirect(url_for('budgets.edit', budget_id=budget_id))
        
        # Atualizar orçamento
        budget.name = name
        budget.amount = amount
        budget.month = month
        budget.year = year
        budget.category_id = category_id if category_id else None
        
        db.session.commit()
        
        flash('Orçamento atualizado com sucesso!', 'success')
        return redirect(url_for('budgets.index', month=month, year=year))
    
    # Buscar categorias do usuário
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('budgets/edit.html', 
                          budget=budget,
                          categories=categories)

@budgets_bp.route('/<int:budget_id>/delete', methods=['POST'])
def delete(budget_id):
    # Buscar orçamento
    budget = Budget.query.filter_by(id=budget_id, user_id=session['user_id']).first_or_404()
    
    month = budget.month
    year = budget.year
    
    # Excluir orçamento
    db.session.delete(budget)
    db.session.commit()
    
    flash('Orçamento excluído com sucesso!', 'success')
    return redirect(url_for('budgets.index', month=month, year=year))

@budgets_bp.route('/api/list')
def api_list():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Obter mês e ano dos parâmetros
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Buscar orçamentos do usuário para o mês/ano selecionado
    budgets = Budget.query.filter_by(
        user_id=session['user_id'],
        month=month,
        year=year
    ).all()
    
    # Converter para dicionário
    budgets_data = [budget.to_dict() for budget in budgets]
    
    return jsonify(budgets_data)
