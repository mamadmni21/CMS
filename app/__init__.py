from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app():
    # Get root directory of the project
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Paths
    template_dir = os.path.join(root_dir, 'app', 'templates')
    static_dir = os.path.join(root_dir, 'static')

    print("Template Dir:", template_dir)
    print("Static Dir:", static_dir)

    # Create Flask app
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    db.init_app(app)

    # Import and register blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
