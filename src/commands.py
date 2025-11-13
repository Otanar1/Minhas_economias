import click
from flask.cli import with_appcontext
from src.main import db, Transaction, Account
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def _generate_recurring_transactions_logic():
    """
    Lógica principal para verificar e gerar transações recorrentes.
    """
    today = date.today()
    recurring_transactions = db.session.execute(
        db.select(Transaction).filter_by(recurring=True)
    ).scalars().all()

    print(f"Verificando {len(recurring_transactions)} transações recorrentes em {today}...")

    for trans in recurring_transactions:
        next_due_date = trans.date
        while True:
            next_due_date = calculate_next_due_date(next_due_date, trans.recurrence_frequency)
            if next_due_date > today:
                break

            if not has_transaction_for_period(trans, next_due_date):
                create_new_instance(trans, next_due_date)
                trans.date = next_due_date # Update the original transaction's date
                db.session.commit()

@click.command('generate-recurring')
@with_appcontext
def generate_recurring_transactions():
    """
    Verifica e gera transações recorrentes que estão vencidas.
    """
    _generate_recurring_transactions_logic()


def calculate_next_due_date(start_date, frequency):
    """Calcula a próxima data de vencimento com base na frequência."""
    if frequency == 'diaria':
        return start_date + timedelta(days=1)
    elif frequency == 'semanal':
        return start_date + timedelta(weeks=1)
    elif frequency == 'mensal':
        return start_date + relativedelta(months=1)
    elif frequency == 'anual':
        return start_date + relativedelta(years=1)
    return date.max # Retorna uma data futura se a frequência for desconhecida


def has_transaction_for_period(original_trans, check_date):
    """
    Verifica se uma transação baseada na original já foi criada para o período (hoje).
    Isso é uma simplificação. A lógica real pode precisar ser mais robusta para
    evitar duplicatas, por exemplo, verificando por um intervalo de datas.
    """
    existing_transaction = db.session.execute(
        db.select(Transaction).filter_by(
            description=original_trans.description,
            amount=original_trans.amount,
            account_id=original_trans.account_id,
            category_id=original_trans.category_id,
            date=check_date,
            recurring=False # As transações geradas não são recorrentes
        )
    ).scalar_one_or_none()

    return existing_transaction is not None


def create_new_instance(original_trans, new_date):
    """Cria uma nova instância de transação e atualiza o saldo da conta."""
    print(f"Gerando nova transação para '{original_trans.description}' em {new_date}")

    # 1. Cria a nova transação
    new_transaction = Transaction(
        user_id=original_trans.user_id,
        account_id=original_trans.account_id,
        category_id=original_trans.category_id,
        description=original_trans.description,
        amount=original_trans.amount,
        type=original_trans.type,
        date=new_date,
        recurring=False, # A instância gerada não é recorrente
        consolidated=True # Marcamos como consolidada
    )

    # 2. Atualiza o saldo da conta
    account = db.session.get(Account, original_trans.account_id)
    if account:
        if new_transaction.type == 'saída':
            account.balance -= new_transaction.amount
        elif new_transaction.type == 'entrada':
            account.balance += new_transaction.amount
        print(f"Saldo da conta '{account.name}' atualizado para {account.balance}")

    # 3. Salva no banco de dados
    db.session.add(new_transaction)
    print("Nova transação adicionada à sessão.")


def register_commands(app):
    app.cli.add_command(generate_recurring_transactions)
