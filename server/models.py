from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin  # Import UserMixin

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    employments = db.relationship('Employment', back_populates='category', lazy=True)
    social_integrations = db.relationship('SocialIntegration', back_populates='category', lazy=True)
    creator = db.relationship('User', back_populates='categories', lazy=True)