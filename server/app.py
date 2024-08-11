from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employment, Category, Application, SocialIntegration
from auth import initialize_auth_routes

def create_app():
    app = Flask(__name__)

    # Configure your database URI here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poverty.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'go high'  # Set your secret key

    # Initialize the database and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    api = Api(app)
    initialize_auth_routes(api)  # Initialize authentication routes

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

# Application routes
@app.route('/applications', methods=['POST'])
def create_application():
    data = request.get_json()
    if not data or not all(key in data for key in ['user_id', 'employment_id', 'status']):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    new_application = Application(
        user_id=data['user_id'],
        employment_id=data['employment_id'],
        status=data['status']
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
            'status': application.status
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
            'status': app.status
        } for app in applications
    ]), 200

@app.route('/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'message': 'Application not found!'}), 404
    
    data = request.get_json()
    if 'user_id' in data:
        application.user_id = data['user_id']
    if 'employment_id' in data:
        application.employment_id = data['employment_id']
    if 'status' in data:
        application.status = data['status']

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

if __name__ == '__main__':
    app.run(debug=True)
