"""
Authentication views for the BusFlow application.

This module defines the routes for user authentication including
login, registration, and logout functionality.

:module: app.views.auth
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/<portal_type>', methods=['GET', 'POST'])
def login(portal_type):
    """
    Handle user login for a specific portal.
    
    GET: Display the login form
    POST: Process login credentials
    
    :param portal_type: Type of portal (user, driver, admin)
    :type portal_type: str
    :returns: Rendered template or redirect
    :rtype: str or Response
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return _redirect_to_portal(current_user.role)
    
    # Validate portal type
    if portal_type not in ['user', 'driver', 'admin']:
        flash('Invalid portal type.', 'error')
        return redirect(url_for('landing.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        controller = AuthController()
        user, error = controller.login(email, password, portal_type)
        
        if error:
            flash(error, 'error')
            return render_template('auth/login.html', portal_type=portal_type)
        
        if user:
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return _redirect_to_portal(user.role)
    
    return render_template('auth/login.html', portal_type=portal_type)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration (passengers only).
    
    GET: Display the registration form
    POST: Process registration details
    
    :returns: Rendered template or redirect
    :rtype: str or Response
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return _redirect_to_portal(current_user.role)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        controller = AuthController()
        user, error = controller.register(name, email, password)
        
        if error:
            flash(error, 'error')
            return render_template('auth/register.html')
        
        if user:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login', portal_type='user'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """
    Log out the current user and redirect to landing page.
    
    :returns: Redirect to landing page
    :rtype: Response
    """
    controller = AuthController()
    controller.logout()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing.index'))


def _redirect_to_portal(role):
    """
    Redirect user to their appropriate portal based on role.
    
    :param role: User's role (USER, DRIVER, ADMIN)
    :type role: str
    :returns: Redirect response
    :rtype: Response
    """
    if role == 'ADMIN':
        return redirect(url_for('admin_portal.dashboard'))
    elif role == 'DRIVER':
        return redirect(url_for('driver_portal.dashboard'))
    else:
        return redirect(url_for('user_portal.dashboard'))

