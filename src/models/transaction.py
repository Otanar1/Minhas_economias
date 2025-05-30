from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from src.models.account import Account
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # entrada, saída
    consolidated = db.Column(db.Boolean, default=False)
    recurring = db.Column(db.Boolean, default=False)
    recurrence_frequency = db.Column(db.String(20), nullable=True)  # mensal, semanal, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    account = db.relationship('Account', backref='transactions')
    category = db.relationship('Category', backref='transactions')
    
    def __init__(self, user_id, account_id, description, amount, date, type, category_id=None, consolidated=False, recurring=False, recurrence_frequency=None):
        self.user_id = user_id
        self.account_id = account_id
        self.category_id = category_id
        self.description = description
        self.amount = amount
        self.date = date
        self.type = type
        self.consolidated = consolidated
        self.recurring = recurring
        self.recurrence_frequency = recurrence_frequency
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'type': self.type,
            'consolidated': self.consolidated,
            'recurring': self.recurring,
            'recurrence_frequency': self.recurrence_frequency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
