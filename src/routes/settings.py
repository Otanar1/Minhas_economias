from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do usuário
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    return render_template('settings/index.html', user=user)

@settings_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do usuário
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Validar dados
        if not name or not email:
            flash('Nome e e-mail são obrigatórios', 'error')
            return render_template('settings/profile.html', user=user)
        
        # Verificar se o e-mail já está em uso (se for diferente do atual)
        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Este e-mail já está em uso', 'error')
                return render_template('settings/profile.html', user=user)
        
        # Atualizar dados do usuário
        user.name = name
        user.email = email
        
        db.session.commit()
        
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html', user=user)

@settings_bp.route('/security', methods=['GET', 'POST'])
def security():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do usuário
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validar dados
        if not current_password or not new_password or not confirm_password:
            flash('Todos os campos são obrigatórios', 'error')
            return render_template('settings/security.html', user=user)
        
        # Verificar senha atual
        if not check_password_hash(user.password, current_password):
            flash('Senha atual incorreta', 'error')
            return render_template('settings/security.html', user=user)
        
        # Verificar se as senhas novas coincidem
        if new_password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('settings/security.html', user=user)
        
        # Atualizar senha
        user.password = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Senha atualizada com sucesso!', 'success')
        return redirect(url_for('settings.security'))
    
    return render_template('settings/security.html', user=user)

@settings_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do usuário
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        # Obter preferências do formulário
        currency = request.form.get('currency', 'BRL')
        date_format = request.form.get('date_format', 'dd/mm/yyyy')
        notifications = request.form.get('notifications', 'off') == 'on'
        
        # Atualizar preferências do usuário
        # Nota: Assumindo que temos um campo preferences no modelo User que armazena um JSON
        user.preferences = {
            'currency': currency,
            'date_format': date_format,
            'notifications': notifications
        }
        
        db.session.commit()
        
        flash('Preferências atualizadas com sucesso!', 'success')
        return redirect(url_for('settings.preferences'))
    
    # Obter preferências atuais (ou definir padrões)
    preferences = user.preferences if hasattr(user, 'preferences') and user.preferences else {
        'currency': 'BRL',
        'date_format': 'dd/mm/yyyy',
        'notifications': False
    }
    
    return render_template('settings/preferences.html', user=user, preferences=preferences)

@settings_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Implementação para gerenciamento de categorias
    # (Esta rota seria para gerenciar categorias personalizadas)
    
    return render_template('settings/categories.html')

@settings_bp.route('/export', methods=['GET'])
def export_data():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Implementação para exportação de dados
    # (Esta rota seria para exportar dados do usuário em diferentes formatos)
    
    return render_template('settings/export.html')

@settings_bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar dados do usuário
    user = User.query.filter_by(id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        # Validar dados
        if not password or confirm != 'EXCLUIR':
            flash('Por favor, preencha todos os campos corretamente', 'error')
            return render_template('settings/delete_account.html')
        
        # Verificar senha
        if not check_password_hash(user.password, password):
            flash('Senha incorreta', 'error')
            return render_template('settings/delete_account.html')
        
        # Excluir conta do usuário
        db.session.delete(user)
        db.session.commit()
        
        # Limpar sessão
        session.clear()
        
        flash('Sua conta foi excluída com sucesso', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('settings/delete_account.html')
