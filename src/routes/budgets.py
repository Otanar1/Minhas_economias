from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.main import db
from src.main import Budget, Category
from sqlalchemy.orm import joinedload
import datetime

budgets_bp = Blueprint('budgets', __name__, template_folder='../templates')

@budgets_bp.route('/')
def list_budgets():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    query = db.select(Budget).filter_by(user_id=user_id).options(joinedload(Budget.category))
    budgets = db.session.execute(query).scalars().all()
    
    return render_template('budgets/list_budgets.html', budgets=budgets)

@budgets_bp.route('/add', methods=['GET', 'POST'])
def add_budget():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        try:
            category_id = int(request.form.get('category_id'))
            amount = float(request.form.get('amount'))
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))

            category = db.session.get(Category, category_id)
            if not category or category.user_id != user_id:
                flash('Categoria inválida.', 'error')
                return redirect(url_for('budgets.add_budget'))

            new_budget = Budget(
                user_id=user_id,
                category_id=category_id,
                name=f"Orçamento para {category.name}",
                amount=amount,
                month=month,
                year=year
            )
            db.session.add(new_budget)
            db.session.commit()
            flash('Orçamento adicionado com sucesso!', 'success')
            return redirect(url_for('budgets.list_budgets'))
        except Exception as e:
            flash(f'Ocorreu um erro ao adicionar o orçamento: {e}', 'error')
            db.session.rollback()

    categories = db.session.execute(
        db.select(Category).filter_by(user_id=user_id, type='saída')
    ).scalars().all()

    return render_template('budgets/add_budget.html', categories=categories)

@budgets_bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
def edit_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    budget = db.session.get(Budget, budget_id)

    if not budget or budget.user_id != user_id:
        flash('Orçamento não encontrado.', 'error')
        return redirect(url_for('budgets.list_budgets'))

    if request.method == 'POST':
        try:
            budget.category_id = int(request.form.get('category_id'))
            budget.amount = float(request.form.get('amount'))
            budget.month = int(request.form.get('month'))
            budget.year = int(request.form.get('year'))

            category = db.session.get(Category, budget.category_id)
            budget.name = f"Orçamento para {category.name}"

            db.session.commit()
            flash('Orçamento atualizado com sucesso!', 'success')
            return redirect(url_for('budgets.list_budgets'))
        except Exception as e:
            flash(f'Ocorreu um erro ao atualizar o orçamento: {e}', 'error')
            db.session.rollback()

    categories = db.session.execute(
        db.select(Category).filter_by(user_id=user_id, type='saída')
    ).scalars().all()
    
    return render_template('budgets/edit_budget.html', budget=budget, categories=categories)

@budgets_bp.route('/delete/<int:budget_id>', methods=['POST'])
def delete_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    budget = db.session.get(Budget, budget_id)

    if not budget or budget.user_id != user_id:
        flash('Orçamento não encontrado.', 'error')
        return redirect(url_for('budgets.list_budgets'))

    try:
        db.session.delete(budget)
        db.session.commit()
        flash('Orçamento excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o orçamento: {e}', 'error')
        db.session.rollback()

    return redirect(url_for('budgets.list_budgets'))
