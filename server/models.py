from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin

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

class Employment(db.Model):
    __tablename__ = 'employment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String)
    salary_range = db.Column(db.Integer)

    # Relationships
    user = db.relationship('User', back_populates='employments')
    category = db.relationship('Category', back_populates='employments', lazy=True)
    applications = db.relationship('Application', back_populates='employment', lazy=True)

    @staticmethod
    def create(user_id, category_id, title, description, requirements=None, location=None, salary_range=None):
        employment = Employment(
            user_id=user_id,
            category_id=category_id,
            title=title,
            description=description,
            requirements=requirements,
            location=location,
            salary_range=salary_range
        )
        db.session.add(employment)
        db.session.commit()
        return employment

    @staticmethod
    def get_all():
        return Employment.query.all()

    @staticmethod
    def get_by_id(id):
        return Employment.query.get(id)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
