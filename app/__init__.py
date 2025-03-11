from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os
import logging

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()  # Will be initialized after app creation
mail = Mail()

load_dotenv()
print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logger = logging.getLogger(__name__)  # Get a logger instance for this module


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Application configuration
    secret_key = "mysecretkey"
    print(f"SECRET_KEY: {secret_key}")  # Debugging output
    app.config["SECRET_KEY"] = secret_key
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False  # Disable SSL when using TLS
    app.config["MAIL_USERNAME"] = "selvaqueen333@gmail.com"  # Add your email
    app.config["MAIL_PASSWORD"] = "secret password"  # Add your email password or app-specific password
    app.config["MAIL_DEFAULT_SENDER"] = "selvaqueen333@gmail.com"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")  # Directory to store images
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Max file size (16 MB)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    # Define the user_loader function
    from .models import User  # Import after db.init_app(app) to avoid circular imports

    @login_manager.user_loader
    def load_user(user_id):
        # return User.query.get(int(user_id))  # Fetch the user by ID
        return db.session.get(User, int(user_id))

    # Register blueprints
    from .views import main
    from .auth import auth
    from .password import password
    from .admin import admin
    from .category import category
    from .visualization import visualization
    from .rating import rating
    from .delivery_person import delivery_person

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin)
    app.register_blueprint(password, url_prefix="/password")
    app.register_blueprint(visualization,url_prefix="/visualization")
    app.register_blueprint(category)
    app.register_blueprint(rating)
    app.register_blueprint(delivery_person)

    # Database creation and admin user setup
    with app.app_context():
        db.create_all()
        # Creates database tables
        from .admin import create_admin_user  # Assuming this function exists in admin.py
        from .customer import create_customer_user
        from .delivery_person import create_delivery_person_user

        create_admin_user()
        create_customer_user()
        create_delivery_person_user()
    # print(app.url_map)

    return app
