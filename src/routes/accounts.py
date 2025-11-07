from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.main import db, Account

accounts_bp = Blueprint('accounts', __name__, template_folder='../templates')

@accounts_bp.route('/')
def index():
    """
    Renderiza a página de gerenciamento de contas, listando todas as contas do usuário.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    accounts = db.session.execute(db.select(Account).filter_by(user_id=user_id)).scalars().all()
    
    return render_template('accounts/index.html', accounts=accounts)

@accounts_bp.route('/add', methods=['GET', 'POST'])
def add_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            account_type = request.form.get('type')
            balance = float(request.form.get('balance'))
            user_id = session['user_id']

            if not name or not account_type:
                flash('Nome e tipo da conta são obrigatórios.', 'error')
                return render_template('accounts/add_account.html')

            new_account = Account(
                user_id=user_id,
                name=name,
                type=account_type,
                balance=balance
            )
            db.session.add(new_account)
            db.session.commit()
            flash('Conta adicionada com sucesso!', 'success')
            return redirect(url_for('accounts.index'))

        except Exception as e:
            flash(f'Ocorreu um erro ao adicionar a conta: {e}', 'error')
            db.session.rollback()

    return render_template('accounts/add_account.html')

@accounts_bp.route('/edit/<int:account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    account = db.session.get(Account, account_id)

    if not account or account.user_id != user_id:
        flash('Conta não encontrada ou acesso não autorizado.', 'error')
        return redirect(url_for('accounts.index'))

    if request.method == 'POST':
        try:
            account.name = request.form.get('name')
            account.active = request.form.get('active') == 'true'

            db.session.commit()
            flash('Conta atualizada com sucesso!', 'success')
            return redirect(url_for('accounts.index'))
        except Exception as e:
            flash(f'Ocorreu um erro ao atualizar a conta: {e}', 'error')
            db.session.rollback()

    return render_template('accounts/edit_account.html', account=account)
