"""
User controller for the BusFlow application.

This module provides the UserController class that handles
user management operations performed by administrators.

:module: app.controllers.user_controller
"""

from app.models.user import User
from app.services.supabase_service import SupabaseService, RegistrationError
from app.config import USER_ROLE, DRIVER_ROLE, ADMIN_ROLE


class UserController:
    """
    Controller for handling user management operations.
    
    This controller is primarily used by administrators to manage
    users and create driver accounts.
    
    Example::
    
        controller = UserController()
        drivers = controller.get_all_drivers()
    """
    
    def __init__(self):
        """
        Initialize the UserController with a Supabase service instance.
        """
        self._supabase_service = SupabaseService()
    
    def get_all_users(self):
        """
        Fetch all users in the system.
        
        :returns: List of User objects
        :rtype: list
        """
        user_data_list = self._supabase_service.get_all_users()
        return [User.from_dict(data) for data in user_data_list]
    
    def get_all_drivers(self):
        """
        Fetch all users with driver role.
        
        :returns: List of User objects with driver role
        :rtype: list
        """
        driver_data_list = self._supabase_service.get_users_by_role(DRIVER_ROLE)
        return [User.from_dict(data) for data in driver_data_list]
    
    def get_all_passengers(self):
        """
        Fetch all users with regular user role.
        
        :returns: List of User objects with user role
        :rtype: list
        """
        user_data_list = self._supabase_service.get_users_by_role(USER_ROLE)
        return [User.from_dict(data) for data in user_data_list]
    
    def get_user_by_id(self, user_id):
        """
        Fetch a specific user by their ID.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: User object or None
        :rtype: User or None
        """
        user_data = self._supabase_service.get_user_by_id(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def create_driver(self, name, email, password):
        """
        Create a new driver account.
        
        :param name: Driver's full name
        :type name: str
        :param email: Driver's email address
        :type email: str
        :param password: Initial password
        :type password: str
        :returns: Tuple of (User object or None, error message or None)
        :rtype: tuple
        
        Example::
        
            driver, error = controller.create_driver('John Driver', 'john@test.com', 'pass123')
        """
        # Validate inputs
        validation_error = self._validate_driver_input(name, email, password)
        if validation_error:
            return None, validation_error
        
        try:
            driver_data = self._supabase_service.create_driver(name, email, password)
            if driver_data:
                return User.from_dict(driver_data), None
            return None, "Failed to create driver account."
        except RegistrationError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Failed to create driver: {str(e)}"
    
    def get_users_by_role(self, role):
        """
        Fetch all users with a specific role.
        
        :param role: Role to filter by (USER, DRIVER, ADMIN)
        :type role: str
        :returns: List of User objects
        :rtype: list
        """
        user_data_list = self._supabase_service.get_users_by_role(role)
        return [User.from_dict(data) for data in user_data_list]
    
    def get_user_statistics(self):
        """
        Get statistics about users in the system.
        
        :returns: Dictionary with user count statistics
        :rtype: dict
        """
        all_users = self.get_all_users()
        
        user_count = sum(1 for u in all_users if u.role == USER_ROLE)
        driver_count = sum(1 for u in all_users if u.role == DRIVER_ROLE)
        admin_count = sum(1 for u in all_users if u.role == ADMIN_ROLE)
        
        return {
            'total_users': len(all_users),
            'passengers': user_count,
            'drivers': driver_count,
            'admins': admin_count
        }
    
    def _validate_driver_input(self, name, email, password):
        """
        Validate driver creation input fields.
        
        :param name: Driver's full name
        :type name: str
        :param email: Driver's email address
        :type email: str
        :param password: Initial password
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

