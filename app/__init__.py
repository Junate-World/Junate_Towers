from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
from app.storage import storage

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    # Use a writable instance path (Vercel is read-only except /tmp)
    instance_path = os.environ.get('INSTANCE_PATH', '/tmp')
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    storage.init_app(app)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
