from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum as PyEnum
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Corrected from 'tablename' to '__tablename__'

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
    funding_applications = db.relationship('FundingApplication', backref='applicant', lazy=True) # Changed backref name
    donations = db.relationship('Donation', back_populates='user', overlaps='donor', lazy=True)


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
    __tablename__ = 'employment'  # Corrected from 'tablename' to '__tablename__'

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

class Category(db.Model):
    __tablename__ = 'category'  # Corrected from 'tablename' to '__tablename__'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    employments = db.relationship('Employment', back_populates='category', lazy=True)
    social_integrations = db.relationship('SocialIntegration', back_populates='category', lazy=True)
    fundings = db.relationship('Funding', backref='source_category', lazy=True) # Changed backref name
    creator = db.relationship('User', back_populates='categories', lazy=True)

class SocialIntegration(db.Model):
    __tablename__ = 'socialintegration'  # Corrected from 'tablename' to '__tablename__'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    association_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='social_integrations', lazy=True)
    category = db.relationship('Category', back_populates='social_integrations', lazy=True)

class AppStatus(PyEnum):
    PENDING = "Pending"
    IN_REVIEW = "IN_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Application(db.Model):
    __tablename__ = 'application'  # Corrected from 'tablename' to '__tablename__'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employment_id = db.Column(db.Integer, db.ForeignKey('employment.id'), nullable=False)
    status = db.Column(Enum(AppStatus), nullable=False)    
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    cover_letter = db.Column(db.String, nullable=False)
    resume = db.Column(db.String, nullable=False)
    linkedin = db.Column(db.String, nullable=True) # URL or File Path
    portfolio = db.Column(db.String, nullable=True) # URL or File Path
  
    # Relationships
    user = db.relationship('User', back_populates='applications', lazy=True)
    employment = db.relationship('Employment', back_populates='applications', lazy=True)

class GrantType(PyEnum):
    SOCIAL_AID = 'Social Aid'
    BUSINESS = 'Business'

class Funding(db.Model):
    __tablename__ = 'funding'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    grant_name = db.Column(db.String(120), nullable=False)
    grant_type = db.Column(db.Enum(GrantType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    eligibility_criteria = Column(Text, nullable=True)
    
    # Relationships
    category = relationship('Category', back_populates='fundings', viewonly=True) # Marked as view-only to resolve relationship conflict //querying for funded projects by a specific category
    funding_applications = db.relationship('FundingApplication', back_populates='funding', lazy=True)

class ApplicationStatus(PyEnum):
    APPLIED = "Applied"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    DENIED = "Denied"

class ApplicationType(PyEnum):
    SOCIAL_AID = 'SocialAid'
    BUSINESS = 'Business'

class FundingApplication(db.Model):
    __tablename__ = 'funding_application'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    funding_id = db.Column(db.Integer, db.ForeignKey('funding.id'), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), nullable=False)
    application_type = db.Column(db.Enum(ApplicationType), nullable=False)
    supporting_documents = db.Column(db.Text, nullable=True)  # URL or File Path

    # Social Aid Specific Fields
    household_income = db.Column(db.Integer, nullable=True)
    number_of_dependents = db.Column(db.Integer, nullable=True)
    reason_for_aid = db.Column(db.Text, nullable=True)

    # Business Specific Fields
    concept_note = db.Column(db.Text, nullable=True)
    business_profile = db.Column(db.Text, nullable=True)

    #Relationships
    user = db.relationship('User', back_populates='funding_applications', overlaps="applicant")
    funding = db.relationship('Funding', back_populates='funding_applications', lazy=True)

class DonationType(PyEnum):
    INDIVIDUAL = 'Individual'
    ORGANISATION = 'Organisation'

class PaymentMethod(PyEnum):
    CREDIT_CARD = 'Credit Card'
    PAYPAL = 'PayPal'
    MPESA = 'MPESA'

class Donation(db.Model):
    __tablename__ = 'donation'

    donation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    donation_type = db.Column(db.Enum(DonationType), nullable=False)
    name = db.Column(db.String, nullable=True) #individual specific field
    organisation_name = db.Column(db.String, nullable=True) #organisation specific field
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='donations', lazy=True)