from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employment, Category, Application, SocialIntegration, Funding, FundingApplication, Donation, DonationType, PaymentMethod, datetime, AppStatus
from auth import initialize_auth_routes
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)  

    # Configure your database URI here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poverty.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'go high'  # Set your secret key

    # Initialize the database and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    api = Api(app)
    initialize_auth_routes(api)  # Initialize authentication routes
    app.register_blueprint(auth)


    return app

app = create_app()

# User routes
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        profile_picture=data.get('profile_picture')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!', 'user_id': new_user.id}), 201

@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_picture': user.profile_picture
        } for user in users
    ]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_picture': user.profile_picture
        }), 200
    return jsonify({'message': 'User not found!'}), 404 

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']

    db.session.commit()
    return jsonify({'message': 'User updated successfully!'}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully!'}), 200
    return jsonify({'message': 'User not found!'}), 404

# Category routes
@app.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get(id)
    if category:
        return jsonify({
            'id': category.id,
            'name': category.name,
            'description': category.description,
        }), 200
    return jsonify({'message': 'Category not found'}), 404

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([
        {
            'id': category.id,
            'name': category.name,
            'description': category.description,
        } for category in categories
    ]), 200

@app.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data or not all(key in data for key in ['name']):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_category = Category(
        name=data['name'],
        description=data.get('description'),
        user_id=data.get('user_id')
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created successfully!', 'category_id': new_category.id}), 201

@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'message': 'Category not found!'}), 404

    data = request.get_json()
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Category updated successfully!'}), 200

@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully!'}), 200
    return jsonify({'message': 'Category not found!'}), 404

# Employment routes
@app.route('/employments', methods=['POST'])
def create_employment():
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'category_id', 'title', 'description']):
        return jsonify({'message': 'Missing required fields!'}), 400

    employment = Employment(
        user_id=data['user_id'],
        category_id=data['category_id'],
        title=data['title'],
        description=data['description'],
        requirements=data.get('requirements'),
        location=data.get('location'),
        salary_range=data.get('salary_range')
    )
    db.session.add(employment)
    db.session.commit()
    return jsonify({'message': 'Employment created successfully!', 'employment_id': employment.id}), 201

@app.route('/employments', methods=['GET'])
def get_employments():
    employments = Employment.query.all()
    return jsonify([
        {
            'id': employment.id,
            'user_id': employment.user_id,
            'category_id': employment.category_id,
            'title': employment.title,
            'description': employment.description,
            'requirements': employment.requirements,
            'location': employment.location,
            'salary_range': employment.salary_range
        } for employment in employments
    ]), 200

@app.route('/employments/<int:id>', methods=['GET'])
def get_employment(id):
    employment = Employment.query.get(id)
    if employment:
        return jsonify({
            'id': employment.id,
            'user_id': employment.user_id,
            'category_id': employment.category_id,
            'title': employment.title,
            'description': employment.description,
            'requirements': employment.requirements,
            'location': employment.location,
            'salary_range': employment.salary_range
        }), 200
    return jsonify({'message': 'Employment not found!'}), 404

@app.route('/employments/<int:id>', methods=['PUT'])
def update_employment(id):
    employment = Employment.query.get(id)
    if not employment:
        return jsonify({'message': 'Employment not found!'}), 404

    data = request.get_json()
    if 'title' in data:
        employment.title = data['title']
    if 'description' in data:
        employment.description = data['description']
    if 'requirements' in data:
        employment.requirements = data['requirements']
    if 'location' in data:
        employment.location = data['location']
    if 'salary_range' in data:
        employment.salary_range = data['salary_range']

    db.session.commit()
    return jsonify({'message': 'Employment updated successfully!'}), 200

@app.route('/employments/<int:id>', methods=['DELETE'])
def delete_employment(id):
    employment = Employment.query.get(id)
    if employment:
        db.session.delete(employment)
        db.session.commit()
        return jsonify({'message': 'Employment deleted successfully!'}), 200
    return jsonify({'message': 'Employment not found!'}), 404

from flask import Flask, request, jsonify
from models import db, SocialIntegration, User, Category  # Assuming these models are in a 'models' module

# Create a Social Integration
@app.route('/social_integrations', methods=['POST'])
def create_social_integration():
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'category_id', 'association_name', 'description']):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_social_integration = SocialIntegration(
        user_id=data['user_id'],
        category_id=data['category_id'],
        association_name=data['association_name'],
        description=data['description']
    )
    db.session.add(new_social_integration)
    db.session.commit()
    return jsonify({'message': 'Social Integration created successfully!', 'id': new_social_integration.id}), 201

# Get All Social Integrations
@app.route('/social_integrations', methods=['GET'])
def get_social_integrations():
    social_integrations = SocialIntegration.query.all()
    return jsonify([
        {
            'id': social_integration.id,
            'user_id': social_integration.user_id,
            'category_id': social_integration.category_id,
            'association_name': social_integration.association_name,
            'description': social_integration.description
        } for social_integration in social_integrations
    ]), 200

# Get a Single Social Integration by ID
@app.route('/social_integrations/<int:id>', methods=['GET'])
def get_social_integration(id):
    social_integration = SocialIntegration.query.get(id)
    if social_integration:
        return jsonify({
            'id': social_integration.id,
            'user_id': social_integration.user_id,
            'category_id': social_integration.category_id,
            'association_name': social_integration.association_name,
            'description': social_integration.description
        }), 200
    return jsonify({'message': 'Social Integration not found!'}), 404

# Update a Social Integration
@app.route('/social_integrations/<int:id>', methods=['PUT'])
def update_social_integration(id):
    social_integration = SocialIntegration.query.get(id)
    if not social_integration:
        return jsonify({'message': 'Social Integration not found!'}), 404

    data = request.get_json()
    if 'user_id' in data:
        social_integration.user_id = data['user_id']
    if 'category_id' in data:
        social_integration.category_id = data['category_id']
    if 'association_name' in data:
        social_integration.association_name = data['association_name']
    if 'description' in data:
        social_integration.description = data['description']
    if 'interested' in data:
        social_integration.interested = data['interested']
    if 'saved' in data:
        social_integration.saved = data['saved']

    db.session.commit()
    return jsonify({'message': 'Social Integration updated successfully!'}), 200


# Delete a Social Integration
@app.route('/social_integrations/<int:id>', methods=['DELETE'])
def delete_social_integration(id):
    social_integration = SocialIntegration.query.get(id)
    if social_integration:
        db.session.delete(social_integration)
        db.session.commit()
        return jsonify({'message': 'Social Integration deleted successfully!'}), 200
    return jsonify({'message': 'Social Integration not found!'}), 404

# Application routes
@app.route('/applications', methods=['POST'])
def create_application():
    data = request.get_json()
    required_fields = ['user_id', 'employment_id', 'status', 'name', 'phone_number', 'email', 'cover_letter', 'resume', 'linkedin', 'portfolio']
    
    if not data or not all(key in data for key in required_fields):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    try:
        status = AppStatus(data['status'])
    except ValueError:
        return jsonify({'message': 'Invalid status value!'}), 400

    new_application = Application(
        user_id=data['user_id'],
        employment_id=data['employment_id'],
        status=status,
        name=data['name'],
        phone_number=data['phone_number'],
        email=data['email'],
        cover_letter=data['cover_letter'],
        resume=data['resume'],
        linkedin=data.get('linkedin'),
        portfolio=data.get('portfolio')
    )
    db.session.add(new_application)
    db.session.commit()
    return jsonify({'message': 'Application created successfully!', 'application_id': new_application.id}), 201

@app.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = Application.query.get(application_id)
    if application:
        return jsonify({
            'id': application.id,
            'user_id': application.user_id,
            'employment_id': application.employment_id,
            'status': application.status.value,  # Convert Enum to string
            'name': application.name,
            'phone_number': application.phone_number,
            'email': application.email,
            'cover_letter': application.cover_letter,
            'resume': application.resume,
            'linkedin': application.linkedin,
            'portfolio': application.portfolio
        }), 200
    return jsonify({'message': 'Application not found!'}), 404

@app.route('/applications', methods=['GET'])
def get_all_applications():
    applications = Application.query.all()
    return jsonify([
        {
            'id': app.id,
            'user_id': app.user_id,
            'employment_id': app.employment_id,
            'status': app.status.value,  # Convert Enum to string
            'name': app.name,
            'phone_number': app.phone_number,
            'email': app.email,
            'cover_letter': app.cover_letter,
            'resume': app.resume,
            'linkedin': app.linkedin,
            'portfolio': app.portfolio
        } for app in applications
    ]), 200

@app.route('/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'message': 'Application not found!'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        try:
            application.status = AppStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    if 'user_id' in data:
        application.user_id = data['user_id']
    if 'employment_id' in data:
        application.employment_id = data['employment_id']
    if 'name' in data:
        application.name = data['name']
    if 'phone_number' in data:
        application.phone_number = data['phone_number']
    if 'email' in data:
        application.email = data['email']
    if 'cover_letter' in data:
        application.cover_letter = data['cover_letter']
    if 'resume' in data:
        application.resume = data['resume']
    if 'linkedin' in data:
        application.linkedin = data['linkedin']
    if 'portfolio' in data:
        application.portfolio = data['portfolio']

    db.session.commit()
    return jsonify({'message': 'Application updated successfully!'}), 200

@app.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    application = Application.query.get(application_id)
    if application:
        db.session.delete(application)
        db.session.commit()
        return jsonify({'message': 'Application deleted successfully!'}), 200
    return jsonify({'message': 'Application not found!'}), 404

# Funding routes
@app.route('/fundings', methods=['POST'])
def create_funding():
    data = request.get_json()
    if not data or not all(key in data for key in ['category_id', 'grant_name', 'grant_type', 'amount']):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_funding = Funding(
        category_id=data['category_id'],
        grant_name=data['grant_name'],
        grant_type=data['grant_type'],
        amount=data['amount'],
        description=data.get('description'),
        eligibility_criteria=data.get('eligibility_criteria')
    )
    db.session.add(new_funding)
    db.session.commit()
    return jsonify({'message': 'Funding created successfully!', 'funding_id': new_funding.id}), 201

@app.route('/fundings', methods=['GET'])
def get_fundings():
    fundings = Funding.query.all()
    return jsonify([
        {
            'id': funding.id,
            'category_id': funding.category_id,
            'grant_name': funding.grant_name,
            'grant_type': funding.grant_type.value,
            'amount': funding.amount,
            'description': funding.description,
            'eligibility_criteria': funding.eligibility_criteria
        } for funding in fundings
    ]), 200

@app.route('/fundings/<int:id>', methods=['GET'])
def get_funding(id):
    funding = Funding.query.get(id)
    if funding:
        return jsonify({
            'id': funding.id,
            'category_id': funding.category_id,
            'grant_name': funding.grant_name,
            'grant_type': funding.grant_type.value,
            'amount': funding.amount,
            'description': funding.description,
            'eligibility_criteria': funding.eligibility_criteria
        }), 200
    return jsonify({'message': 'Funding not found!'}), 404

@app.route('/fundings/<int:id>', methods=['PUT'])
def update_funding(id):
    funding = Funding.query.get(id)
    if not funding:
        return jsonify({'message': 'Funding not found!'}), 404

    data = request.get_json()
    if 'category_id' in data:
        funding.category_id = data['category_id']
    if 'grant_name' in data:
        funding.grant_name = data['grant_name']
    if 'grant_type' in data:
        funding.grant_type = data['grant_type']
    if 'amount' in data:
        funding.amount = data['amount']
    if 'description' in data:
        funding.description = data['description']
    if 'eligibility_criteria' in data:
        funding.eligibility_criteria = data['eligibility_criteria']

    db.session.commit()
    return jsonify({'message': 'Funding updated successfully!'}), 200

@app.route('/fundings/<int:id>', methods=['DELETE'])
def delete_funding(id):
    funding = Funding.query.get(id)
    if funding:
        db.session.delete(funding)
        db.session.commit()
        return jsonify({'message': 'Funding deleted successfully!'}), 200
    return jsonify({'message': 'Funding not found!'}), 404

# FundingApplication routes
@app.route('/funding_applications', methods=['POST'])
def create_funding_application():
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'funding_id', 'status', 'application_type']):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_funding_application = FundingApplication(
        user_id=data['user_id'],
        funding_id=data['funding_id'],
        status=data['status'],
        application_type=data['application_type'],
        supporting_documents=data.get('supporting_documents'),
        household_income=data.get('household_income'),
        number_of_dependents=data.get('number_of_dependents'),
        reason_for_aid=data.get('reason_for_aid'),
        concept_note=data.get('concept_note'),
        business_profile=data.get('business_profile')
    )
    db.session.add(new_funding_application)
    db.session.commit()
    return jsonify({'message': 'Funding application created successfully!', 'funding_application_id': new_funding_application.id}), 201

@app.route('/funding_applications', methods=['GET'])
def get_funding_applications():
    funding_applications = FundingApplication.query.all()
    return jsonify([
        {
            'id': funding_app.id,
            'user_id': funding_app.user_id,
            'funding_id': funding_app.funding_id,
            'status': funding_app.status.value,
            'application_type': funding_app.application_type.value,
            'supporting_documents': funding_app.supporting_documents,
            'household_income': funding_app.household_income,
            'number_of_dependents': funding_app.number_of_dependents,
            'reason_for_aid': funding_app.reason_for_aid,
            'concept_note': funding_app.concept_note,
            'business_profile': funding_app.business_profile
        } for funding_app in funding_applications
    ]), 200

@app.route('/funding_applications/<int:id>', methods=['GET'])
def get_funding_application(id):
    funding_application = FundingApplication.query.get(id)
    if funding_application:
        return jsonify({
            'id': funding_application.id,
            'user_id': funding_application.user_id,
            'funding_id': funding_application.funding_id,
            'status': funding_application.status.value,
            'application_type': funding_application.application_type.value,
            'supporting_documents': funding_application.supporting_documents,
            'household_income': funding_application.household_income,
            'number_of_dependents': funding_application.number_of_dependents,
            'reason_for_aid': funding_application.reason_for_aid,
            'concept_note': funding_application.concept_note,
            'business_profile': funding_application.business_profile
        }), 200
    return jsonify({'message': 'Funding application not found!'}), 404

@app.route('/funding_applications/<int:id>', methods=['PUT'])
def update_funding_application(id):
    funding_application = FundingApplication.query.get(id)
    if not funding_application:
        return jsonify({'message': 'Funding application not found!'}), 404

    data = request.get_json()
    if 'status' in data:
        funding_application.status = data['status']
    if 'application_type' in data:
        funding_application.application_type = data['application_type']
    if 'supporting_documents' in data:
        funding_application.supporting_documents = data['supporting_documents']
    if 'household_income' in data:
        funding_application.household_income = data['household_income']
    if 'number_of_dependents' in data:
        funding_application.number_of_dependents = data['number_of_dependents']
    if 'reason_for_aid' in data:
        funding_application.reason_for_aid = data['reason_for_aid']
    if 'concept_note' in data:
        funding_application.concept_note = data['concept_note']
    if 'business_profile' in data:
        funding_application.business_profile = data['business_profile']

    db.session.commit()
    return jsonify({'message': 'Funding application updated successfully!'}), 200

@app.route('/funding_applications/<int:id>', methods=['DELETE'])
def delete_funding_application(id):
    funding_application = FundingApplication.query.get(id)
    if funding_application:
        db.session.delete(funding_application)
        db.session.commit()
        return jsonify({'message': 'Funding application deleted successfully!'}), 200
    return jsonify({'message': 'Funding application not found!'}), 404

#Donations routes
@app.route('/donations', methods=['POST'])
def create_donation():
    data = request.json

    donation = Donation(
        user_id=data.get('user_id'),
        donation_type=DonationType(data['donation_type']),
        name=data.get('name'),
        organisation_name=data.get('organisation_name'),
        amount=data['amount'],
        payment_method=PaymentMethod(data['payment_method']),
        donation_date=datetime.utcnow()
    )

    db.session.add(donation)
    db.session.commit()

    return jsonify({"message": "Donation added successfully!", "donation_id": donation.donation_id}), 201

@app.route('/donations', methods=['GET'])
def get_donations():
    donations = Donation.query.all()
    return jsonify([
        {
            'donation_id': donation.donation_id,
            'user_id': donation.user_id,
            'donation_type': donation.donation_type.value,
            'name': donation.name,
            'organisation_name': donation.organisation_name,
            'amount': donation.amount,
            'payment_method': donation.payment_method.value,
            'donation_date': donation.donation_date
        } for donation in donations
    ]), 200

@app.route('/donations/<int:donation_id>', methods=['GET'])
def get_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    return jsonify(
        {
            'donation_id': donation.donation_id,
            'user_id': donation.user_id,
            'donation_type': donation.donation_type.value,
            'name': donation.name,
            'organisation_name': donation.organisation_name,
            'amount': donation.amount,
            'payment_method': donation.payment_method.value,
            'donation_date': donation.donation_date
        }
    ), 200

@app.route('/donations/<int:donation_id>', methods=['PUT'])
def update_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    data = request.json

    donation.donation_type = DonationType(data['donation_type'])
    donation.name = data.get('name', donation.name)
    donation.organisation_name = data.get('organisation_name', donation.organisation_name)
    donation.amount = data['amount']
    donation.payment_method = PaymentMethod(data['payment_method'])
    donation.donation_date = datetime.utcnow()

    db.session.commit()

    return jsonify({"message": "Donation updated successfully!"}), 200

@app.route('/donations/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    return jsonify({"message": "Donation deleted successfully!"}), 200

@app.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_profile = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture': user.profile_picture,
        'employments': [
            {
                'id': emp.id,
                'title': emp.title,
                'description': emp.description,
                'location': emp.location,
                'salary_range': emp.salary_range,
            } for emp in user.employments
        ] or "N/A",
        'applications': [
            {
                'id': app.id,
                'employment_id': app.employment_id,
                'status': app.status.value,
                'name': app.name,
                'phone_number': app.phone_number,
                'email': app.email,
                'cover_letter': app.cover_letter,
                'resume': app.resume,
                'linkedin': app.linkedin,
                'portfolio': app.portfolio,
            } for app in user.applications
        ] or "N/A",
        'social_integrations': [
            {
                'id': si.id,
                'association_name': si.association_name,
                'description': si.description,
            } for si in user.social_integrations
        ] or "N/A",
        'funding_applications': [
            {
                'id': fa.id,
                'funding_id': fa.funding_id,
                'status': fa.status.value,
                'application_type': fa.application_type.value,
                'supporting_documents': fa.supporting_documents,
                'household_income': fa.household_income,
                'number_of_dependents': fa.number_of_dependents,
                'reason_for_aid': fa.reason_for_aid,
                'concept_note': fa.concept_note,
                'business_profile': fa.business_profile,
            } for fa in user.funding_applications
        ] or "N/A",
        'donations': [
            {
                'donation_id': don.donation_id,
                'donation_type': don.donation_type.value,
                'name': don.name,
                'organisation_name': don.organisation_name,
                'amount': don.amount,
                'payment_method': don.payment_method.value,
                'donation_date': don.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
            } for don in user.donations
        ] or "N/A"
    }

    return jsonify(user_profile)

if __name__ == '__main__':
    app.run(debug=True)
