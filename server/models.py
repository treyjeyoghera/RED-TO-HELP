from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin  # Import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    profile_picture = db.Column(db.String)

    # Relationships
    employments = db.relationship('Employment', back_populates='user', lazy=True)
    applications = db.relationship('Application', back_populates='user', lazy=True)
    categories = db.relationship('Category', back_populates='creator', lazy=True)
    social_integrations = db.relationship('SocialIntegration', back_populates='user', lazy=True)

    @property
    def is_active(self):
        return True  

    @property
    def is_authenticated(self):
        return True  

    @property
    def is_anonymous(self):
        return False  