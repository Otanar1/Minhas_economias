from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.account import Account
from src.models.transaction import Transaction
from src.models.category import Category
from datetime import datetime, date, timedelta
import calendar
import json

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obter parâmetros de filtro
    period = request.args.get('period', 'month')
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Definir período de análise
    today = date.today()
    
    if period == 'month':
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        period_name = f"{calendar.month_name[month]} de {year}"
    elif period == 'year':
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_name = f"Ano de {year}"
    elif period == '3months':
        # Últimos 3 meses
        end_date = today
        start_date = date(today.year, today.month - 2 if today.month > 2 else (today.month + 10), 1)
        if today.month <= 2:
            start_date = date(today.year - 1, start_date.month, start_date.day)
        period_name = f"Últimos 3 meses"
    elif period == '6months':
        # Últimos 6 meses
        end_date = today
        start_date = date(today.year, today.month - 5 if today.month > 5 else (today.month + 7), 1)
        if today.month <= 5:
            start_date = date(today.year - 1, start_date.month, start_date.day)
        period_name = f"Últimos 6 meses"
    else:
        # Padrão: mês atual
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        period_name = f"{calendar.month_name[today.month]} de {today.year}"
    
    # Buscar transações do período
    transactions = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Buscar categorias
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    
    # Calcular totais por categoria
    category_totals = {}
    for transaction in transactions:
        if transaction.category_id:
            category_id = transaction.category_id
            if category_id not in category_totals:
                category_totals[category_id] = {
                    'income': 0,
                    'expense': 0
                }
            
            if transaction.type == 'entrada':
                category_totals[category_id]['income'] += transaction.amount
            else:
                category_totals[category_id]['expense'] += transaction.amount
    
    # Calcular totais gerais
    total_income = sum(transaction.amount for transaction in transactions if transaction.type == 'entrada')
    total_expense = sum(transaction.amount for transaction in transactions if transaction.type == 'saída')
    balance = total_income - total_expense
    
    # Preparar dados para gráficos
    income_by_category = []
    expense_by_category = []
    
    for category in categories:
        if category.id in category_totals:
            if category_totals[category.id]['income'] > 0:
                income_by_category.append({
                    'name': category.name,
                    'value': category_totals[category.id]['income']
                })
            
            if category_totals[category.id]['expense'] > 0:
                expense_by_category.append({
                    'name': category.name,
                    'value': category_totals[category.id]['expense']
                })
    
    # Ordenar por valor
    income_by_category.sort(key=lambda x: x['value'], reverse=True)
    expense_by_category.sort(key=lambda x: x['value'], reverse=True)
    
    # Preparar dados para gráfico de evolução mensal
    monthly_data = {}
    
    # Se o período for anual, preparar dados mensais
    if period == 'year':
        for month_num in range(1, 13):
            month_start = date(year, month_num, 1)
            month_end = date(year, month_num, calendar.monthrange(year, month_num)[1])
            
            month_transactions = [t for t in transactions if month_start <= t.date <= month_end]
            
            month_income = sum(t.amount for t in month_transactions if t.type == 'entrada')
            month_expense = sum(t.amount for t in month_transactions if t.type == 'saída')
            month_balance = month_income - month_expense
            
            monthly_data[month_num] = {
                'name': calendar.month_name[month_num],
                'income': month_income,
                'expense': month_expense,
                'balance': month_balance
            }
    
    return render_template('analysis/index.html',
                          period=period,
                          period_name=period_name,
                          month=month,
                          year=year,
                          total_income=total_income,
                          total_expense=total_expense,
                          balance=balance,
                          income_by_category=json.dumps(income_by_category),
                          expense_by_category=json.dumps(expense_by_category),
                          monthly_data=json.dumps(list(monthly_data.values())) if monthly_data else None,
                          categories=categories)

@analysis_bp.route('/reports')
def reports():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obter parâmetros de filtro
    report_type = request.args.get('type', 'monthly')
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Definir período do relatório
    if report_type == 'monthly':
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        report_name = f"Relatório Mensal - {calendar.month_name[month]} de {year}"
    elif report_type == 'annual':
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        report_name = f"Relatório Anual - {year}"
    elif report_type == 'custom':
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            report_name = f"Relatório Personalizado - {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        except (ValueError, TypeError):
            start_date = date(year, month, 1)
            end_date = date(year, month, calendar.monthrange(year, month)[1])
            report_name = f"Relatório Mensal - {calendar.month_name[month]} de {year}"
    else:
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        report_name = f"Relatório Mensal - {calendar.month_name[month]} de {year}"
    
    # Buscar transações do período
    transactions = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).order_by(Transaction.date).all()
    
    # Buscar contas
    accounts = Account.query.filter_by(user_id=session['user_id'], active=True).all()
    
    # Calcular totais
    total_income = sum(t.amount for t in transactions if t.type == 'entrada')
    total_expense = sum(t.amount for t in transactions if t.type == 'saída')
    balance = total_income - total_expense
    
    # Calcular totais por conta
    account_totals = {}
    for account in accounts:
        account_transactions = [t for t in transactions if t.account_id == account.id]
        account_income = sum(t.amount for t in account_transactions if t.type == 'entrada')
        account_expense = sum(t.amount for t in account_transactions if t.type == 'saída')
        account_balance = account_income - account_expense
        
        account_totals[account.id] = {
            'income': account_income,
            'expense': account_expense,
            'balance': account_balance
        }
    
    return render_template('analysis/reports.html',
                          report_type=report_type,
                          report_name=report_name,
                          start_date=start_date,
                          end_date=end_date,
                          transactions=transactions,
                          accounts=accounts,
                          account_totals=account_totals,
                          total_income=total_income,
                          total_expense=total_expense,
                          balance=balance)

@analysis_bp.route('/api/data')
def api_data():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Obter parâmetros de filtro
    period = request.args.get('period', 'month')
    month = request.args.get('month', datetime.now().month)
    year = request.args.get('year', datetime.now().year)
    
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = datetime.now().month
        year = datetime.now().year
    
    # Definir período de análise
    today = date.today()
    
    if period == 'month':
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
    elif period == 'year':
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    elif period == '3months':
        # Últimos 3 meses
        end_date = today
        start_date = date(today.year, today.month - 2 if today.month > 2 else (today.month + 10), 1)
        if today.month <= 2:
            start_date = date(today.year - 1, start_date.month, start_date.day)
    elif period == '6months':
        # Últimos 6 meses
        end_date = today
        start_date = date(today.year, today.month - 5 if today.month > 5 else (today.month + 7), 1)
        if today.month <= 5:
            start_date = date(today.year - 1, start_date.month, start_date.day)
    else:
        # Padrão: mês atual
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    
    # Buscar transações do período
    transactions = Transaction.query.filter(
        Transaction.user_id == session['user_id'],
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    # Preparar dados para resposta
    transactions_data = [transaction.to_dict() for transaction in transactions]
    
    return jsonify(transactions_data)
