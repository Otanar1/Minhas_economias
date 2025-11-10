from flask import Blueprint, render_template, session, redirect, url_for
from src.models import User, Account, Category

reports_bp = Blueprint('reports', __name__, template_folder='../templates')

@reports_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    accounts = Account.query.filter_by(user_id=user_id).all()
    categories = Category.query.filter_by(user_id=user_id).all()

    return render_template('reports/index.html', accounts=accounts, categories=categories)
