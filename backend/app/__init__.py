from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from app.config import Config

# Global database connection
mongo_client = None
db = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    
    # Initialize MongoDB
    global mongo_client, db
    mongo_client = MongoClient(Config.MONGO_URI)
    db = mongo_client[Config.DATABASE_NAME]
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.files import files_bp
    from app.routes.access import access_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(files_bp, url_prefix='/api/files')
    app.register_blueprint(access_bp, url_prefix='/api/access')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'secure-file-sharing-backend'}, 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return {
            'message': 'Secure File Sharing API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'files': '/api/files',
                'access': '/api/access'
            }
        }, 200
    
    return app

def get_db():
    """Helper function to get database instance"""
    return db