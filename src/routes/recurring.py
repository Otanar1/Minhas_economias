from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models import db, Transaction

recurring_bp = Blueprint('recurring', __name__, template_folder='../templates')

@recurring_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    recurring_transactions = Transaction.query.filter_by(user_id=user_id, recurring=True).all()
    return render_template('recurring/index.html', transactions=recurring_transactions)

@recurring_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    transaction = Transaction.query.get_or_404(id)
    if transaction.user_id != session['user_id']:
        return redirect(url_for('recurring.index'))

    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('recurring.index'))
