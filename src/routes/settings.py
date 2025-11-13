from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        # Handle Profile Information
        user.birth_year = request.form.get('birth_year')
        user.gender = request.form.get('gender')
        user.marital_status = request.form.get('marital_status')
        user.children_count = request.form.get('children_count')
        user.country = request.form.get('country')
        user.state = request.form.get('state')
        user.city = request.form.get('city')

        # Handle Preferences
        preferences = user.preferences or {}
        preferences['receive_tips'] = request.form.get('receive_tips') == 'on'
        preferences['receive_news'] = request.form.get('receive_news') == 'on'
        preferences['receive_partner_news'] = request.form.get('receive_partner_news') == 'on'
        preferences['initial_screen'] = request.form.get('initial_screen')
        preferences['default_account'] = request.form.get('default_account')
        user.preferences = preferences
        
        db.session.commit()
        
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('settings.index'))
    
    return render_template('settings/index.html', user=user)

@settings_bp.route('/change-email', methods=['POST'])
def change_email():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    new_email = request.form.get('new_email')
    password = request.form.get('password')
    
    if not new_email or not password:
        flash('E-mail e senha são obrigatórios.', 'error')
        return redirect(url_for('settings.index'))
    
    if not check_password_hash(user.password, password):
        flash('Senha incorreta.', 'error')
        return redirect(url_for('settings.index'))
    
    if User.query.filter_by(email=new_email).first():
        flash('Este e-mail já está em uso.', 'error')
        return redirect(url_for('settings.index'))
    
    user.email = new_email
    db.session.commit()
    
    flash('E-mail atualizado com sucesso!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(id=session['user_id']).first_or_404()

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('settings.index'))

    if not check_password_hash(user.password, current_password):
        flash('Senha atual incorreta.', 'error')
        return redirect(url_for('settings.index'))

    if new_password != confirm_password:
        flash('As senhas não coincidem.', 'error')
        return redirect(url_for('settings.index'))
    
    user.set_password(new_password)
    db.session.commit()
    
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/backup')
def backup():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    backup_data = {
        'user': {
            'name': user.name,
            'email': user.email,
            'birth_year': user.birth_year,
            'gender': user.gender,
            'marital_status': user.marital_status,
            'children_count': user.children_count,
            'country': user.country,
            'state': user.state,
            'city': user.city,
            'preferences': user.preferences
        },
        'accounts': [{'name': a.name, 'type': a.type, 'balance': a.balance} for a in user.accounts],
        'transactions': [{'description': t.description, 'amount': t.amount, 'type': t.type, 'date': t.date.isoformat()} for t in user.transactions],
        'budgets': [{'name': b.name, 'amount': b.amount, 'month': b.month, 'year': b.year} for b in user.budgets],
        'dreams': [{'name': d.name, 'target_amount': d.target_amount, 'current_amount': d.current_amount} for d in user.dreams],
        'categories': [{'name': c.name, 'type': c.type} for c in user.categories]
    }

    response = jsonify(backup_data)
    response.headers['Content-Disposition'] = 'attachment;filename=backup.json'
    return response
