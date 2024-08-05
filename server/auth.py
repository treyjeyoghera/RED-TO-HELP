from flask import request, jsonify
from flask_restful import Resource
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models import User

class LoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            user = User.query.filter_by(email=email).first()
            print(f"Attempting to log in user: {email}")

            if not user:
                print("User not found")
                return {'message': 'Invalid email or password'}, 401
            
            if not check_password_hash(user.password, password):
                print("Password does not match")
                return {'message': 'Invalid email or password'}, 401
            
            login_user(user)
            print("User logged in successfully")
            return {
                'message': 'Logged in successfully',
                'profile_picture': user.profile_picture  # Include profile picture if exists
            }, 200
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return {'message': str(e)}, 500

class SignupResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            profile_picture = data.get('profile_picture')  # Get the optional profile_picture

            if not email or not username or not password:
                return {'message': 'Missing required fields'}, 400
            
            user = User.query.filter_by(email=email).first()

            if user:
                return {'message': 'Email address already exists'}, 400

            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                first_name=first_name,
                last_name=last_name,
                profile_picture=profile_picture  # Set the profile_picture if provided
            )
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'User created successfully'}, 201
        except Exception as e:
            return {'message': str(e)}, 500

class LogoutResource(Resource):
    @login_required
    def post(self):
        try:
            logout_user()
            return {'message': 'Logged out successfully'}, 200
        except Exception as e:
            return {'message': str(e)}, 500

def initialize_auth_routes(api):
    api.add_resource(LoginResource, '/login')
    api.add_resource(SignupResource, '/signup')
    api.add_resource(LogoutResource, '/logout')
