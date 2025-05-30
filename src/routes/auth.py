from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from src.models.user import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['email'] = user.email
            
            if remember:
                # Configurar sessão para durar mais tempo
                session.permanent = True
            
            # Atualizar último login
            user.update_last_login()
            
            return redirect(url_for('dashboard.index'))
        else:
            flash('Email ou senha inválidos', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Em um sistema real, enviaríamos um email com link para redefinir senha
            # Aqui apenas simulamos o processo
            flash('Instruções para redefinir sua senha foram enviadas para seu email', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email não encontrado', 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Verificar se o email já está em uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Este email já está em uso', 'error')
            return render_template('auth/register.html')
        
        # Verificar se as senhas coincidem
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
            return render_template('auth/register.html')
        
        # Criar novo usuário
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
