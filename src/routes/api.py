from flask import Blueprint, jsonify, session, redirect, url_for, flash
from src.main import db
from src.main import Transaction, Category
from sqlalchemy import func
import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/summary')
def summary():
    if 'user_id' not in session:
        # Em uma API, em vez de redirecionar, geralmente retornamos um erro 401 ou 403.
        return jsonify({'error': 'Acesso não autorizado'}), 401

    user_id = session['user_id']

    # Obter o primeiro e último dia do mês atual
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    # Para encontrar o fim do mês, vamos para o primeiro dia do próximo mês e subtraímos um dia.
    next_month = start_of_month.replace(month=start_of_month.month % 12 + 1, year=start_of_month.year + (start_of_month.month // 12))
    end_of_month = next_month - datetime.timedelta(days=1)

    # Consulta para agrupar despesas por categoria no mês atual
    summary_data = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'saída',
        Transaction.date >= start_of_month,
        Transaction.date <= end_of_month
    ).group_by(Category.name).all()

    # Formatar os dados para o gráfico
    labels = [row[0] for row in summary_data]
    data = [float(row[1]) for row in summary_data]

    return jsonify({
        'labels': labels,
        'data': data
    })
