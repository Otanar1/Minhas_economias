from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from src.models.user import User, db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # receita, despesa
    color = db.Column(db.String(7), nullable=True)  # código de cor em hexadecimal
    icon = db.Column(db.String(50), nullable=True)
    order = db.Column(db.Integer, default=0)
    
    def __init__(self, user_id, name, type, color=None, icon=None, order=0):
        self.user_id = user_id
        self.name = name
        self.type = type
        self.color = color
        self.icon = icon
        self.order = order
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'color': self.color,
            'icon': self.icon,
            'order': self.order
        }
