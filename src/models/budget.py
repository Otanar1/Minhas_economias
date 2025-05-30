from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from datetime import datetime

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    category = db.relationship('Category', backref='budgets')
    
    def __init__(self, user_id, name, amount, month, year, category_id=None):
        self.user_id = user_id
        self.name = name
        self.amount = amount
        self.month = month
        self.year = year
        self.category_id = category_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'month': self.month,
            'year': self.year,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
