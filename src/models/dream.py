from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from datetime import datetime

class Dream(db.Model):
    __tablename__ = 'dreams'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # viagem, carro, eletrônico, casa, etc
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ativo')  # ativo, concluído, cancelado
    
    def __init__(self, user_id, name, type, target_amount, target_date=None, current_amount=0.0):
        self.user_id = user_id
        self.name = name
        self.type = type
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.target_date = target_date
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'progress': round((self.current_amount / self.target_amount) * 100, 2) if self.target_amount > 0 else 0
        }
