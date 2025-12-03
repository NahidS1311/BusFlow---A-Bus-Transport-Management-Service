"""
Views package for BusFlow application.

This package contains Flask blueprints that define the routes and
view functions for the application. Views handle HTTP requests,
interact with controllers, and render templates.

:module: app.views
"""

from app.views.landing import landing_bp
from app.views.auth import auth_bp
from app.views.user_portal import user_portal_bp
from app.views.driver_portal import driver_portal_bp
from app.views.admin_portal import admin_portal_bp

__all__ = [
    'landing_bp',
    'auth_bp',
    'user_portal_bp',
    'driver_portal_bp',
    'admin_portal_bp'
]

