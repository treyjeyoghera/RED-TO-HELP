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

if __name__ == '__main__':
    app.run(debug=True)
