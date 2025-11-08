from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Profile information
    birth_year = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    children_count = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)

    # Preferences
    preferences = db.Column(db.JSON, nullable=True)

    accounts = db.relationship('Account', backref='user', lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade="all, delete-orphan")
    dreams = db.relationship('Dream', backref='user', lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade="all, delete-orphan")
    categories = db.relationship('Category', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    active = db.Column(db.Boolean, default=True)

    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    recurring = db.Column(db.Boolean, default=False)
    recurrence_frequency = db.Column(db.String(20), nullable=True)
    consolidated = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'date': self.date.isoformat() if self.date else None,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'recurring': self.recurring,
            'recurrence_frequency': self.recurrence_frequency
        }

class Dream(db.Model):
    __tablename__ = 'dreams'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = db.Column(db.String(20), default='ativo')

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
