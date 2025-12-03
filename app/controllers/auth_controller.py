"""
Authentication controller for the BusFlow application.

This module provides the AuthController class that handles all
authentication-related business logic including login, registration,
and session management.

:module: app.controllers.auth_controller
"""

from app.models.user import User
from app.services.supabase_service import (
    SupabaseService,
    AuthenticationError,
    RegistrationError
)
from app.config import USER_ROLE, DRIVER_ROLE, ADMIN_ROLE


class AuthController:
    """
    Controller for handling authentication operations.
    
    This controller manages user login, registration, and role validation.
    It acts as an intermediary between the auth views and the Supabase service.
    
    Example::
    
        controller = AuthController()
        user, error = controller.login('user@example.com', 'password', 'user')
    """
    
    def __init__(self):
        """
        Initialize the AuthController with a Supabase service instance.
        """
        self._supabase_service = SupabaseService()
    
    def login(self, email, password, portal_type):
        """
        Authenticate a user and validate their role matches the portal.
        
        :param email: User's email address
        :type email: str
        :param password: User's password
        :type password: str
        :param portal_type: Type of portal (user, driver, admin)
        :type portal_type: str
        :returns: Tuple of (User object or None, error message or None)
        :rtype: tuple
        
        Example::
        
            user, error = controller.login('user@test.com', 'pass123', 'user')
            if error:
                print(f"Login failed: {error}")
            else:
                print(f"Welcome, {user.name}")
        """
        try:
            user_data = self._supabase_service.login(email, password)
            
            if not user_data:
                return None, "Invalid email or password."
            
            user = User.from_dict(user_data)
            
            # Validate role matches portal
            expected_role = self._get_expected_role(portal_type)
            if expected_role and user.role != expected_role:
                return None, f"Access denied. This portal is for {portal_type}s only."
            
            return user, None
            
        except AuthenticationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Login failed: {str(e)}"
    
    def register(self, name, email, password):
        """
        Register a new user account (passengers only).
        
        Only regular users can self-register. Drivers must be created by admins.
        
        :param name: User's full name
        :type name: str
        :param email: User's email address
        :type email: str
        :param password: User's chosen password
        :type password: str
        :returns: Tuple of (User object or None, error message or None)
        :rtype: tuple
        
        Example::
        
            user, error = controller.register('John Doe', 'john@test.com', 'pass123')
        """
        # Validate inputs
        validation_error = self._validate_registration_input(name, email, password)
        if validation_error:
            return None, validation_error
        
        try:
            user_data = self._supabase_service.register(name, email, password)
            
            if not user_data:
                return None, "Registration failed. Please try again."
            
            user = User.from_dict(user_data)
            return user, None
            
        except RegistrationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Registration failed: {str(e)}"
    
    def logout(self):
        """
        Log out the current user.
        """
        self._supabase_service.logout()
    
    def get_user_by_id(self, user_id):
        """
        Fetch a user by their ID.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: User object or None
        :rtype: User or None
        """
        user_data = self._supabase_service.get_user_by_id(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def _get_expected_role(self, portal_type):
        """
        Get the expected role for a portal type.
        
        :param portal_type: Type of portal (user, driver, admin)
        :type portal_type: str
        :returns: Expected role string or None
        :rtype: str or None
        """
        role_mapping = {
            'user': USER_ROLE,
            'driver': DRIVER_ROLE,
            'admin': ADMIN_ROLE
        }
        return role_mapping.get(portal_type.lower())
    
    def _validate_registration_input(self, name, email, password):
        """
        Validate registration input fields.
        
        :param name: User's full name
        :type name: str
        :param email: User's email address
        :type email: str
        :param password: User's chosen password
        :type password: str
        :returns: Error message or None if valid
        :rtype: str or None
        """
        if not name or len(name.strip()) < 2:
            return "Name must be at least 2 characters long."
        
        if not email or '@' not in email:
            return "Please enter a valid email address."
        
        if not password or len(password) < 6:
            return "Password must be at least 6 characters long."
        
        return None

