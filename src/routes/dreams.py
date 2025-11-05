from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.main import db
from src.main import Dream
import datetime

dreams_bp = Blueprint('dreams', __name__, template_folder='../templates')

@dreams_bp.route('/')
def list_dreams():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    dreams = db.session.execute(db.select(Dream).filter_by(user_id=user_id)).scalars().all()
    
    return render_template('dreams/list_dreams.html', dreams=dreams)

@dreams_bp.route('/add', methods=['GET', 'POST'])
def add_dream():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            target_amount = float(request.form.get('target_amount'))
            target_date_str = request.form.get('target_date')

            target_date = None
            if target_date_str:
                target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()

            new_dream = Dream(
                user_id=session['user_id'],
                name=name,
                target_amount=target_amount,
                target_date=target_date,
                type="Geral"
            )
            db.session.add(new_dream)
            db.session.commit()
            flash('Sonho adicionado com sucesso!', 'success')
            return redirect(url_for('dreams.list_dreams'))
        except Exception as e:
            flash(f'Ocorreu um erro ao adicionar o sonho: {e}', 'error')
            db.session.rollback()

    return render_template('dreams/add_dream.html')

@dreams_bp.route('/edit/<int:dream_id>', methods=['GET', 'POST'])
def edit_dream(dream_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    dream = db.session.get(Dream, dream_id)

    if not dream or dream.user_id != user_id:
        flash('Sonho não encontrado.', 'error')
        return redirect(url_for('dreams.list_dreams'))

    if request.method == 'POST':
        try:
            dream.name = request.form.get('name')
            dream.target_amount = float(request.form.get('target_amount'))
            target_date_str = request.form.get('target_date')

            if target_date_str:
                dream.target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
            else:
                dream.target_date = None

            db.session.commit()
            flash('Sonho atualizado com sucesso!', 'success')
            return redirect(url_for('dreams.list_dreams'))
        except Exception as e:
            flash(f'Ocorreu um erro ao atualizar o sonho: {e}', 'error')
            db.session.rollback()
    
    return render_template('dreams/edit_dream.html', dream=dream)

@dreams_bp.route('/delete/<int:dream_id>', methods=['POST'])
def delete_dream(dream_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    dream = db.session.get(Dream, dream_id)

    if not dream or dream.user_id != user_id:
        flash('Sonho não encontrado.', 'error')
        return redirect(url_for('dreams.list_dreams'))

    try:
        # Adicionar lógica para reverter contribuições aqui no futuro
        db.session.delete(dream)
        db.session.commit()
        flash('Sonho excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o sonho: {e}', 'error')
        db.session.rollback()

    return redirect(url_for('dreams.list_dreams'))
