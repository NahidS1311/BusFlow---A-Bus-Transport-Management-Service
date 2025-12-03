"""
BusFlow Flask Application Factory.

This module contains the Flask application factory that creates and configures
the Flask application instance with all necessary extensions and blueprints.

:module: app
"""

from flask import Flask
from flask_login import LoginManager

from app.config import SECRET_KEY
from app.services.supabase_service import SupabaseService

# Initialize Flask-Login
login_manager = LoginManager()


def create_app():
    """
    Create and configure the Flask application.
    
    This factory function creates a Flask application instance,
    configures it with the necessary settings, and registers all blueprints.
    
    :returns: Configured Flask application instance
    :rtype: Flask
    
    Example::
    
        app = create_app()
        app.run(debug=True)
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID for Flask-Login session management.
        
        :param user_id: The unique identifier of the user
        :type user_id: str
        :returns: User object or None if not found
        :rtype: User or None
        """
        from app.models.user import User
        supabase_service = SupabaseService()
        user_data = supabase_service.get_user_by_id(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.landing import landing_bp
    from app.views.user_portal import user_portal_bp
    from app.views.driver_portal import driver_portal_bp
    from app.views.admin_portal import admin_portal_bp
    
    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_portal_bp, url_prefix='/user')
    app.register_blueprint(driver_portal_bp, url_prefix='/driver')
    app.register_blueprint(admin_portal_bp, url_prefix='/admin')
    
    return app

