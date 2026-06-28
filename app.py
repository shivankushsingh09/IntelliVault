"""
Flask Application Factory
Main entry point for the IntelliVault application
"""
from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager
from flask_cors import CORS
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException
import logging
from logging.handlers import RotatingFileHandler
import os

from config import config
from database.models import db, User
from database.db import init_db


def create_app(config_name='development'):
    """Create and configure Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Security headers
    csp = {
        'default-src': '\'self\'',
        'style-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com',
            '\'unsafe-inline\''
        ],
        'script-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            '\'unsafe-inline\''
        ],
        'font-src': [
            '\'self\'',
            'https://cdnjs.cloudflare.com',
            'https://fonts.gstatic.com'
        ],
        'img-src': [
            '\'self\'',
            'data:'
        ]
    }
    Talisman(app, content_security_policy=csp, force_https=False)
    
    # Create database
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Context processors
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return {'current_user': current_user}
    
    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
        }
    
    return app


def register_blueprints(app):
    """Register all route blueprints"""
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.notes import notes_bp
    from routes.pdf import pdf_bp
    from routes.ai import ai_bp
    from routes.quiz import quiz_bp
    from routes.profile import profile_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(profile_bp)


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('403.html'), 403
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': str(e)}), e.code
        return render_template('error.html', error=e), e.code


def setup_logging(app):
    """Setup logging configuration"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/intellivault.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(app.config['LOG_LEVEL'])
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config['LOG_LEVEL'])
        app.logger.info('IntelliVault startup')
