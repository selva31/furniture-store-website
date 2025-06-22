from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os
import logging
import mimetypes

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()

# Load environment variables from .env
load_dotenv()

# Register .glb MIME type for 3D models
mimetypes.add_type('model/gltf-binary', '.glb')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Basic Config
    app.config["SECRET_KEY"] = "mysecretkey"
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

    # Mail Configuration
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = "selvaqueen333@gmail.com"
    app.config["MAIL_PASSWORD"] = "neme rovd accl zxge"
    app.config["MAIL_DEFAULT_SENDER"] = "selvaqueen333@gmail.com"

    # Upload paths
    app.config["IMAGE_UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MODEL_UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "model")

    # Max upload size (100MB)
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

    # Ensure upload folders exist
    os.makedirs(app.config["IMAGE_UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MODEL_UPLOAD_FOLDER"], exist_ok=True)


    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)


    # Login manager settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    # User loader
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
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
    app.register_blueprint(visualization, url_prefix="/visualization")
    app.register_blueprint(category)
    app.register_blueprint(rating)
    app.register_blueprint(delivery_person)

    # Create database and default users
    with app.app_context():
        db.create_all()
        from .admin import create_admin_user
        from .customer import create_customer_user
        from .delivery_person import create_delivery_person_user

        create_admin_user()
        create_customer_user()
        create_delivery_person_user()

    return app
