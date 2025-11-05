from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.main import db
from src.main import Transaction, Account, Category
import datetime

transactions_bp = Blueprint('transactions', __name__, template_folder='../templates')

@transactions_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']

    if request.method == 'POST':
        try:
            # 1. Coletar dados do formulário
            trans_type = request.form.get('type')
            description = request.form.get('description')
            amount = float(request.form.get('amount'))
            date_str = request.form.get('date')
            account_id = int(request.form.get('account_id'))
            category_id = int(request.form.get('category_id'))

            # 2. Validar dados (básico)
            if not all([trans_type, description, amount, date_str, account_id, category_id]):
                flash('Todos os campos são obrigatórios.', 'error')
                return redirect(url_for('transactions.add_transaction'))

            if amount <= 0:
                flash('O valor da transação deve ser positivo.', 'error')
                return redirect(url_for('transactions.add_transaction'))

            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

            # 3. Buscar a conta no banco de dados
            account = db.session.get(Account, account_id)
            if not account or account.user_id != user_id:
                flash('Conta inválida.', 'error')
                return redirect(url_for('transactions.add_transaction'))

            # 4. Criar a nova transação
            new_transaction = Transaction(
                user_id=user_id,
                account_id=account_id,
                category_id=category_id,
                description=description,
                amount=amount,
                type=trans_type,
                date=date
            )

            # 5. Atualizar o saldo da conta
            if trans_type == 'saída':
                account.balance -= amount
            elif trans_type == 'entrada':
                account.balance += amount

            # 6. Salvar no banco de dados
            db.session.add(new_transaction)
            db.session.commit()

            flash('Transação adicionada com sucesso!', 'success')
            return redirect(url_for('dashboard.index'))

        except ValueError:
            flash('Ocorreu um erro com os valores fornecidos. Verifique se os números e as datas estão corretos.', 'error')
            db.session.rollback()
        except Exception as e:
            flash(f'Ocorreu um erro inesperado: {e}', 'error')
            db.session.rollback()

    # Para a requisição GET, buscamos as contas e categorias do usuário para popular os seletores do formulário.
    accounts = db.session.execute(db.select(Account).filter_by(user_id=user_id, active=True)).scalars().all()
    categories = db.session.execute(db.select(Category).filter_by(user_id=user_id)).scalars().all()

    return render_template('transactions/add_transaction.html', accounts=accounts, categories=categories)

@transactions_bp.route('/')
def list_transactions():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    # Busca todas as transações do usuário, ordenadas pela data mais recente
    transactions = db.session.execute(
        db.select(Transaction)
        .filter_by(user_id=user_id)
        .order_by(Transaction.date.desc())
    ).scalars().all()
    
    return render_template('transactions/list_transactions.html', transactions=transactions)

@transactions_bp.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        # 1. Buscar a transação
        transaction = db.session.get(Transaction, transaction_id)

        # 2. Verificar se a transação existe e pertence ao usuário
        if not transaction or transaction.user_id != user_id:
            flash('Transação não encontrada ou acesso não autorizado.', 'error')
            return redirect(url_for('transactions.list_transactions'))

        # 3. Reverter a alteração no saldo da conta
        account = transaction.account
        if transaction.type == 'saída':
            account.balance += transaction.amount
        elif transaction.type == 'entrada':
            account.balance -= transaction.amount

        # 4. Excluir a transação
        db.session.delete(transaction)
        db.session.commit()

        flash('Transação excluída com sucesso!', 'success')

    except Exception as e:
        flash(f'Ocorreu um erro ao excluir a transação: {e}', 'error')
        db.session.rollback()

    return redirect(url_for('transactions.list_transactions'))
