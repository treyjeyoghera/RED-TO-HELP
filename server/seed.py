from faker import Faker
from models import db, User, Employment, Category, Application, SocialIntegration
from app import create_app
import random
import requests

# Initialize Faker
fake = Faker()

# Create Flask app and context
app = create_app()
app.app_context().push()

# Create all tables
db.create_all()

def fetch_profile_picture():
    response = requests.get("https://randomuser.me/api/")
    if response.status_code == 200:
        data = response.json()
        return data['results'][0]['picture']['large']  # Get the large profile picture URL
    return None

# Seed Users
def seed_users(n=100):
    users = []
    for _ in range(n):
        profile_picture = fetch_profile_picture()  # Fetch a unique profile picture
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            profile_picture=profile_picture  # Use the fetched profile picture
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()
    return users

# Predefined list of 130 category names
category_names = [
    'Medicine', 'Engineering', 'Education', 'Finance', 'Marketing',
    'Sales', 'Human Resources', 'Data Science', 'Software Development',
    'Legal', 'Art and Design', 'Customer Service', 'Operations',
    'Product Management', 'Project Management', 'Quality Assurance',
    'Research and Development', 'Supply Chain', 'Technical Support',
    'Nursing', 'Pharmacy', 'Physical Therapy', 'Psychology',
    'Surgery', 'Dentistry', 'Veterinary Medicine', 'Biotechnology',
    'Information Technology', 'Web Development', 'Network Administration',
    'Data Analysis', 'Statistics', 'Artificial Intelligence',
    'Machine Learning', 'Cybersecurity', 'Cloud Computing',
    'Mobile Development', 'Game Development', 'Graphic Design',
    'Interior Design', 'Fashion Design', 'Architecture', 'Journalism',
    'Public Relations', 'Content Creation', 'SEO Specialist',
    'Event Planning', 'Hospitality Management', 'Culinary Arts',
    'Travel and Tourism', 'Real Estate', 'Construction Management',
    'Environmental Science', 'Agriculture', 'Marine Biology',
    'Physics', 'Chemistry', 'Mathematics', 'Linguistics', 'Sociology',
    'Anthropology', 'History', 'Political Science', 'International Relations',
    'Economics', 'Philosophy', 'Ethics', 'Religious Studies', 
    'Fine Arts', 'Music', 'Theater', 'Film Studies', 
    'Dance', 'Social Work', 'Community Service', 'Nonprofit Management',
    'Business Administration', 'Marketing Management', 
    'Supply Chain Management', 'Operations Management', 
    'Financial Analysis', 'Investment Banking', 
    'Corporate Finance', 'Insurance', 'Actuarial Science',
    'Real Estate Development', 'Urban Planning', 'Environmental Policy',
    'Public Policy', 'Public Administration', 'Forensic Science',
    'Criminal Justice', 'Emergency Management', 'Fire Science',
    'Law Enforcement', 'Cybercrime Investigation', 
    'Intelligence Analysis', 'Security Management',
    'Military Science', 'Logistics', 'Transportation',
    'Retail Management', 'E-commerce', 'Digital Marketing',
    'Social Media Management', 'Data Entry', 'Quality Control',
    'Manufacturing', 'Textile Engineering', 'Chemicals',
    'Pharmaceuticals', 'Food Science', 'Biochemistry',
    'Health Information Technology', 'Telecommunications',
    'Broadcasting', 'Web Design', 'User Experience Design',
    'User Interface Design', 'Augmented Reality', 'Virtual Reality',
    'Blockchain', 'Fintech', 'Cryptocurrency',
    'Oil and Gas', 'Mining', 'Metallurgy', 'Pulp and Paper',
    'Energy Management', 'Renewable Energy', 'Environmental Engineering',
    'Transportation Engineering', 'Civil Engineering', 
    'Mechanical Engineering', 'Electrical Engineering',
    'Aerospace Engineering', 'Nuclear Engineering', 
    'Industrial Engineering', 'Petroleum Engineering', 
    'Mining Engineering', 'Textile Engineering', 
    'Chemical Engineering', 'Software Engineering',
    'Systems Engineering', 'Robotics', 'Automation',
]

# Seed Categories
def seed_categories(users):
    categories = []
    for name in category_names:
        category = Category(
            name=name,
            description=fake.text(),
            user_id=random.choice(users).id
        )
        categories.append(category)
    db.session.add_all(categories)
    db.session.commit()
    return categories

# Seed Employments
def seed_employments(users, categories, n=100):
    employments = []
    for _ in range(n):
        employment = Employment(
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            title=fake.job(),
            description=fake.text(),
            requirements=fake.text(),
            location=fake.city(),
            salary_range=random.randint(30000, 120000)
        )
        employments.append(employment)
    db.session.add_all(employments)
    db.session.commit()
    return employments

# Seed Applications
def seed_applications(users, employments, n=100):
    applications = []
    for _ in range(n):
        application = Application(
            user_id=random.choice(users).id,
            employment_id=random.choice(employments).id,
            status=random.randint(0, 3),  # Assuming you have 4 statuses
            resume=fake.file_name(extension='pdf'),  # Generate a fake resume filename
            cover_letter=fake.text(max_nb_chars=200),  # Generate a fake cover letter
            email=fake.email()  # Generate a fake email
        )
        applications.append(application)
    db.session.add_all(applications)
    db.session.commit()
    return applications

# Seed Social Integrations
def seed_social_integrations(users, categories, n=100):
    social_integrations = []
    for _ in range(n):
        social_integration = SocialIntegration(
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            association_name=fake.company(),  # Generate a fake company name
            description=fake.text()  # Generate a fake description
        )
        social_integrations.append(social_integration)
    db.session.add_all(social_integrations)
    db.session.commit()
    return social_integrations

# Seed all data
def seed_all():
    users = seed_users()
    categories = seed_categories(users)
    employments = seed_employments(users, categories)
    applications = seed_applications(users, employments)
    social_integrations = seed_social_integrations(users, categories)

if __name__ == '__main__':
    seed_all()
