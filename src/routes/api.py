from flask import Blueprint, jsonify, session, request, Response
from src.models import db, Budget, Transaction, Category
from sqlalchemy import func, and_
import datetime
import csv
import io

api_bp = Blueprint('api', __name__)

@api_bp.route('/reports/summary', methods=['POST'])
def reports_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = request.json

    start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else None
    end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
    account_ids = data.get('accounts')
    category_ids = data.get('categories')

    query = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction.category).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída'
    )

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if account_ids:
        query = query.filter(Transaction.account_id.in_(account_ids))
    if category_ids:
        query = query.filter(Transaction.category_id.in_(category_ids))

    expenses_by_category = query.group_by(Category.name).all()

    income_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'entrada'
    )

    if start_date:
        income_query = income_query.filter(Transaction.date >= start_date)
    if end_date:
        income_query = income_query.filter(Transaction.date <= end_date)
    if account_ids:
        income_query = income_query.filter(Transaction.account_id.in_(account_ids))

    total_income = income_query.scalar() or 0
    total_expenses = sum(amount for _, amount in expenses_by_category)

    return jsonify({
        'expenses_by_category': [{'category': name, 'amount': amount} for name, amount in expenses_by_category],
        'total_expenses': total_expenses,
        'total_income': total_income
    })

@api_bp.route('/reports/export_csv', methods=['POST'])
def export_csv():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = request.json

    start_date = datetime.datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else None
    end_date = datetime.datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
    account_ids = data.get('accounts')
    category_ids = data.get('categories')

    query = db.session.query(
        Transaction.date,
        Transaction.description,
        Category.name,
        Transaction.amount,
        Transaction.type
    ).join(Transaction.category).filter(
        Transaction.user_id == user_id
    )

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if account_ids:
        query = query.filter(Transaction.account_id.in_(account_ids))
    if category_ids:
        query = query.filter(Transaction.category_id.in_(category_ids))

    transactions = query.order_by(Transaction.date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Data', 'Descrição', 'Categoria', 'Valor', 'Tipo'])

    for t in transactions:
        writer.writerow([t.date.strftime('%Y-%m-%d'), t.description, t.name, t.amount, t.type])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_transacoes.csv"}
    )


@api_bp.route('/summary')
def summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Acesso não autorizado'}), 401

    user_id = session['user_id']
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    if start_of_month.month == 12:
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1) - datetime.timedelta(days=1)
    else:
        end_of_month = start_of_month.replace(month=start_of_month.month + 1) - datetime.timedelta(days=1)

    spent_subquery = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total_spent')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída',
        Transaction.date.between(start_of_month, end_of_month)
    ).group_by(Transaction.category_id).subquery()

    budget_summary = db.session.query(
        Category.name,
        Budget.amount,
        spent_subquery.c.total_spent
    ).join(
        Budget, and_(
            Budget.category_id == Category.id,
            Budget.user_id == user_id,
            Budget.month == today.month,
            Budget.year == today.year
        )
    ).outerjoin(
        spent_subquery, Category.id == spent_subquery.c.category_id
    ).filter(
        Category.user_id == user_id,
        Category.type == 'saída'
    ).all()

    summary_data = [
        {
            "category": name,
            "budgeted": float(budgeted) if budgeted else 0,
            "spent": float(spent) if spent else 0
        }
        for name, budgeted, spent in budget_summary
    ]

    chart_data = [item for item in summary_data if item['spent'] > 0]
    chart_labels = [item['category'] for item in chart_data]
    chart_values = [item['spent'] for item in chart_data]

    return jsonify({
        'budget_progress': summary_data,
        'expense_chart': {
            'labels': chart_labels,
            'data': chart_values
        }
    })

@api_bp.route('/balance_evolution')
def balance_evolution():
    if 'user_id' not in session:
        return jsonify({'error': 'Acesso não autorizado'}), 401

    user_id = session['user_id']

    transactions = db.session.execute(
        db.select(Transaction).filter_by(user_id=user_id).order_by(Transaction.date.asc())
    ).scalars().all()

    labels = []
    data = []
    current_balance = 0

    for trans in transactions:
        if trans.type == 'entrada':
            current_balance += trans.amount
        else:
            current_balance -= trans.amount

        if not labels or labels[-1] != trans.date.strftime('%Y-%m-%d'):
            labels.append(trans.date.strftime('%Y-%m-%d'))
            data.append(round(current_balance, 2))
        else:
            data[-1] = round(current_balance, 2)

    return jsonify({'labels': labels, 'data': data})

@api_bp.route('/monthly_summary')
def monthly_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Acesso não autorizado'}), 401

    user_id = session['user_id']
    try:
        year = int(request.args.get('year', datetime.datetime.now().year))
        month = int(request.args.get('month', datetime.datetime.now().month))
    except (ValueError, TypeError):
        return jsonify({'error': 'Parâmetros de mês ou ano inválidos.'}), 400

    start_of_month = datetime.date(year, month, 1)
    # Correção para o cálculo do fim do mês
    if month == 12:
        end_of_month = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_of_month = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)


    # 1. Calcular Saldo Inicial (Saldo até o final do mês anterior)
    previous_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'entrada',
        Transaction.date < start_of_month
    ).scalar() or 0.0

    previous_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída',
        Transaction.date < start_of_month
    ).scalar() or 0.0

    opening_balance = previous_income - previous_expenses

    # 2. Calcular Entradas do Mês
    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'entrada',
        Transaction.date.between(start_of_month, end_of_month)
    ).scalar() or 0.0

    # 3. Calcular Saídas do Mês
    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída',
        Transaction.date.between(start_of_month, end_of_month)
    ).scalar() or 0.0

    return jsonify({
        'opening_balance': opening_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses
    })
