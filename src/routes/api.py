from flask import Blueprint, jsonify, session
from src.main import db, Budget, Transaction, Category
from sqlalchemy import func, and_
import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/summary')
def summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Acesso não autorizado'}), 401

    user_id = session['user_id']
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    # Correção para o cálculo do fim do mês para evitar problemas com dezembro
    if start_of_month.month == 12:
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1) - datetime.timedelta(days=1)
    else:
        end_of_month = start_of_month.replace(month=start_of_month.month + 1) - datetime.timedelta(days=1)


    # Subconsulta para calcular os gastos por categoria no mês atual
    spent_subquery = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total_spent')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída',
        Transaction.date.between(start_of_month, end_of_month)
    ).group_by(Transaction.category_id).subquery()

    # Consulta principal para juntar orçamentos e gastos
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

    # Formatar os dados para o frontend
    summary_data = [
        {
            "category": name,
            "budgeted": float(budgeted) if budgeted else 0,
            "spent": float(spent) if spent else 0
        }
        for name, budgeted, spent in budget_summary
    ]

    # Separar os dados para o gráfico de pizza (apenas categorias com gastos)
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
