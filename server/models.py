from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin  # Import UserMixin

db = SQLAlchemy()


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