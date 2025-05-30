from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # carteira, cartão de crédito, conta corrente, poupança
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def __init__(self, user_id, name, type, balance=0.0):
        self.user_id = user_id
        self.name = name
        self.type = type
        self.balance = balance
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'balance': self.balance,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active': self.active
        }
