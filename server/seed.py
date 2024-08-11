from faker import Faker
from models import db, User, Employment, Category, Application, SocialIntegration, Funding, FundingApplication, ApplicationStatus, ApplicationType, GrantType
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
    try:
        response = requests.get("https://randomuser.me/api/")
        if response.status_code == 200:
            data = response.json()
            return data['results'][0]['picture']['large']  # Get the large profile picture URL
    except requests.RequestException as e:
        print(f"Failed to fetch profile picture: {e}")
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

# Predefined list of grant names
grant_names = [
    'Health Innovation Grant', 'Engineering Excellence Fund', 'Educational Outreach Grant',
    'Financial Empowerment Grant', 'Marketing Leadership Award',
    'Tech Startup Grant', 'Research & Development Fund', 'Artistic Creativity Grant',
    'Community Development Grant', 'Environmental Protection Fund',
    'AI and Robotics Grant', 'Digital Transformation Fund', 'Energy Innovation Grant',
    'Social Welfare Grant', 'Global Education Fund'
]

# Predefined list of descriptions and eligibility criteria
descriptions = [
    "This grant supports innovative health projects aimed at improving community health standards.",
    "Funding for outstanding engineering projects with a focus on sustainable development.",
    "Grants for educational initiatives that promote equal access to quality education.",
    "Financial empowerment for underprivileged communities through targeted financial literacy programs.",
    "Award for groundbreaking marketing campaigns that demonstrate exceptional creativity and impact.",
    "Funding to support early-stage technology startups with a focus on innovation and scalability.",
    "Research and development fund for cutting-edge scientific and technological research projects.",
    "Support for artistic projects that explore new mediums and push creative boundaries.",
    "Grants to enhance community infrastructure and promote local economic development.",
    "Funding for projects focused on environmental conservation and sustainability.",
    "Support for AI and robotics projects that offer innovative solutions to real-world problems.",
    "Grants for companies undergoing digital transformation to enhance operational efficiency.",
    "Funding for innovative energy solutions aimed at reducing carbon footprints.",
    "Social welfare grants for programs that support marginalized and vulnerable populations.",
    "Global education fund to promote access to education in developing countries."
]

eligibility_criteria = [
    "Applicants must have a project focused on health innovation and be registered in the medical field.",
    "Eligible projects must be in the engineering sector with a focus on sustainability.",
    "Applicants should have a proven track record in educational outreach and impact.",
    "Eligibility is limited to non-profit organizations working on financial literacy.",
    "Open to marketing professionals with at least five years of experience.",
    "Applicants must be early-stage startups in the technology sector.",
    "Eligible projects must involve significant research and have a potential for high impact.",
    "Applicants should be artists or organizations working on new artistic projects.",
    "Eligibility is limited to community development organizations.",
    "Open to environmental organizations with a focus on conservation projects.",
    "Eligible projects must be in AI or robotics with a clear application.",
    "Applicants must be companies actively pursuing digital transformation.",
    "Open to companies or organizations developing energy-efficient technologies.",
    "Eligible programs must focus on social welfare for marginalized communities.",
    "Open to NGOs and educational institutions working on global education initiatives."
]
#Seed Funding
def seed_fundings(categories):
    fundings = []
    for i in range(15):
        funding = Funding(
        category_id=random.choice(categories).id,
        grant_name=grant_names[i],
        amount=random.randint(5000, 100000),  # Random grant amount
        description=descriptions[i],
        eligibility_criteria=eligibility_criteria[i],
        grant_type=random.choice([GrantType.SOCIAL_AID, GrantType.BUSINESS])  # Randomly assign a grant type
        )
    fundings.append(funding)
    db.session.add_all(fundings)
    db.session.commit()
    return fundings

# Seed Funding Applications
def seed_funding_applications(users, fundings, n=100):
    funding_applications = []
    for _ in range(n):
        application_type = random.choice(list(ApplicationType))
        funding_application = FundingApplication(
            user_id=random.choice(users).id,
            funding_id=random.choice(fundings).id,
            status=random.choice(list(ApplicationStatus)),
            application_type=application_type,
            supporting_documents=fake.file_name(extension='pdf')
        )

        # Add Social Aid or Business-specific fields
        if application_type == ApplicationType.SOCIAL_AID:
            funding_application.household_income = random.randint(20000, 80000)
            funding_application.number_of_dependents = random.randint(1, 5)
            funding_application.reason_for_aid = fake.text()
        elif application_type == ApplicationType.BUSINESS:
            funding_application.concept_note = fake.text()
            funding_application.business_profile = fake.text()

        funding_applications.append(funding_application)
    db.session.add_all(funding_applications)
    db.session.commit()
    return funding_applications

# Seed all data
def seed_all():
    users = seed_users()
    categories = seed_categories(users)
    employments = seed_employments(users, categories)
    applications = seed_applications(users, employments)
    social_integrations = seed_social_integrations(users, categories)
    fundings = seed_fundings(categories)
    seed_funding_applications(users, fundings)

if __name__ == '__main__':
    seed_all()
