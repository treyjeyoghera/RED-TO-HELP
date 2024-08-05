from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employment, Category, Application, SocialIntegration

def create_app():
    app = Flask(__name__)

    # Configure your database URI here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poverty.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'go high'  # Set your secret key

    # Initialize the database and Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    app = create_app()

    if __name__ == '__main__':
     app.run(debug=True)