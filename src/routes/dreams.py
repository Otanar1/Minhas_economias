from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.dream import Dream
from datetime import datetime, date

dreams_bp = Blueprint('dreams', __name__)

@dreams_bp.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Buscar sonhos do usuário
    dreams = Dream.query.filter_by(user_id=session['user_id']).all()
    
    # Calcular progresso total
    total_target = sum(dream.target_amount for dream in dreams)
    total_current = sum(dream.current_amount for dream in dreams)
    total_progress = round((total_current / total_target) * 100, 2) if total_target > 0 else 0
    
    return render_template('dreams/index.html', 
                          dreams=dreams, 
                          total_target=total_target,
                          total_current=total_current,
                          total_progress=total_progress)

@dreams_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        dream_type = request.form.get('type')
        target_amount = request.form.get('target_amount')
        target_date = request.form.get('target_date')
        current_amount = request.form.get('current_amount', 0)
        
        # Validar dados
        if not name or not dream_type or not target_amount:
            flash('Nome, tipo e valor alvo são obrigatórios', 'error')
            return render_template('dreams/create.html')
        
        try:
            target_amount = float(target_amount)
            current_amount = float(current_amount) if current_amount else 0
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None
        except (ValueError, TypeError):
            flash('Valores inválidos', 'error')
            return render_template('dreams/create.html')
        
        # Criar novo sonho
        new_dream = Dream(
            user_id=session['user_id'],
            name=name,
            type=dream_type,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date
        )
        
        db.session.add(new_dream)
        db.session.commit()
        
        flash('Sonho criado com sucesso!', 'success')
        return redirect(url_for('dreams.index'))
    
    return render_template('dreams/create.html')

@dreams_bp.route('/<int:dream_id>/edit', methods=['GET', 'POST'])
def edit(dream_id):
    # Buscar sonho
    dream = Dream.query.filter_by(id=dream_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        dream_type = request.form.get('type')
        target_amount = request.form.get('target_amount')
        target_date = request.form.get('target_date')
        current_amount = request.form.get('current_amount')
        status = request.form.get('status')
        
        # Validar dados
        if not name or not dream_type or not target_amount or not current_amount:
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return render_template('dreams/edit.html', dream=dream)
        
        try:
            target_amount = float(target_amount)
            current_amount = float(current_amount)
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else None
        except (ValueError, TypeError):
            flash('Valores inválidos', 'error')
            return render_template('dreams/edit.html', dream=dream)
        
        # Atualizar sonho
        dream.name = name
        dream.type = dream_type
        dream.target_amount = target_amount
        dream.current_amount = current_amount
        dream.target_date = target_date
        
        if status:
            dream.status = status
        
        db.session.commit()
        
        flash('Sonho atualizado com sucesso!', 'success')
        return redirect(url_for('dreams.index'))
    
    return render_template('dreams/edit.html', dream=dream)

@dreams_bp.route('/<int:dream_id>/delete', methods=['POST'])
def delete(dream_id):
    # Buscar sonho
    dream = Dream.query.filter_by(id=dream_id, user_id=session['user_id']).first_or_404()
    
    # Excluir sonho
    db.session.delete(dream)
    db.session.commit()
    
    flash('Sonho excluído com sucesso!', 'success')
    return redirect(url_for('dreams.index'))

@dreams_bp.route('/<int:dream_id>/update_amount', methods=['POST'])
def update_amount(dream_id):
    # Buscar sonho
    dream = Dream.query.filter_by(id=dream_id, user_id=session['user_id']).first_or_404()
    
    amount = request.form.get('amount')
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        flash('Valor inválido', 'error')
        return redirect(url_for('dreams.edit', dream_id=dream_id))
    
    # Atualizar valor atual
    dream.current_amount += amount
    
    # Verificar se o sonho foi alcançado
    if dream.current_amount >= dream.target_amount:
        dream.status = 'concluído'
    
    db.session.commit()
    
    flash('Valor atualizado com sucesso!', 'success')
    return redirect(url_for('dreams.index'))
