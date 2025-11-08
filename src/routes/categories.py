from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.models import db, Category, User

categories_bp = Blueprint('categories', __name__, template_folder='../templates')

@categories_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('categories/index.html', categories=categories)

@categories_bp.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        user_id = session['user_id']

        new_category = Category(name=name, type=type, user_id=user_id)
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('categories.index'))

    return render_template('categories/add.html')

@categories_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    category = Category.query.get_or_404(id)
    if category.user_id != session['user_id']:
        return redirect(url_for('categories.index'))

    if request.method == 'POST':
        category.name = request.form.get('name')
        category.type = request.form.get('type')
        db.session.commit()
        return redirect(url_for('categories.index'))

    return render_template('categories/edit.html', category=category)

@categories_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    category = Category.query.get_or_404(id)
    if category.user_id != session['user_id']:
        return redirect(url_for('categories.index'))

    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('categories.index'))
