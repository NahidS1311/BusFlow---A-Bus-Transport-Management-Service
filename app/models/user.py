"""
User model for the BusFlow application.

This module defines the User class that represents all types of users
in the system: passengers (USER), drivers (DRIVER), and administrators (ADMIN).

:module: app.models.user
"""

from flask_login import UserMixin
from app.config import USER_ROLE, DRIVER_ROLE, ADMIN_ROLE


class User(UserMixin):
    """
    Represents a user in the BusFlow system.
    
    Users can have one of three roles:
    - USER: Regular passengers who book tickets
    - DRIVER: Bus drivers who view their assignments
    - ADMIN: Administrators who manage the fleet
    
    :param user_id: Unique identifier for the user (UUID from Supabase)
    :type user_id: str
    :param email: User's email address for authentication
    :type email: str
    :param name: User's display name
    :type name: str
    :param role: User's role (USER, DRIVER, or ADMIN)
    :type role: str
    
    Example::
    
        user = User(
            user_id='uuid-123',
            email='user@example.com',
            name='John Doe',
            role='USER'
        )
    """
    
    def __init__(self, user_id, email, name, role):
        """
        Initialize a new User instance.
        
        :param user_id: Unique identifier for the user
        :type user_id: str
        :param email: User's email address
        :type email: str
        :param name: User's display name
        :type name: str
        :param role: User's role in the system
        :type role: str
        """
        self.id = user_id
        self.email = email
        self.name = name
        self.role = role
    
    def get_id(self):
        """
        Return the unique identifier for Flask-Login.
        
        :returns: User's unique identifier
        :rtype: str
        """
        return str(self.id)
    
    @property
    def isAdmin(self):
        """
        Check if the user is an administrator.
        
        :returns: True if user has admin role, False otherwise
        :rtype: bool
        """
        return self.role == ADMIN_ROLE
    
    @property
    def isDriver(self):
        """
        Check if the user is a driver.
        
        :returns: True if user has driver role, False otherwise
        :rtype: bool
        """
        return self.role == DRIVER_ROLE
    
    @property
    def isUser(self):
        """
        Check if the user is a regular passenger.
        
        :returns: True if user has user role, False otherwise
        :rtype: bool
        """
        return self.role == USER_ROLE
    
    @property
    def first_name(self):
        """
        Get the user's first name from their full name.
        
        :returns: First name of the user
        :rtype: str
        """
        return self.name.split(' ')[0] if self.name else ''
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a User instance from a dictionary.
        
        :param data: Dictionary containing user data
        :type data: dict
        :returns: New User instance
        :rtype: User
        
        Example::
        
            data = {'id': 'uuid-123', 'email': 'test@test.com', 'name': 'Test', 'role': 'USER'}
            user = User.from_dict(data)
        """
        return cls(
            user_id=data.get('id'),
            email=data.get('email'),
            name=data.get('name'),
            role=data.get('role', USER_ROLE)
        )
    
    def to_dict(self):
        """
        Convert User instance to a dictionary.
        
        :returns: Dictionary representation of the user
        :rtype: dict
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role
        }
    
    def __repr__(self):
        """
        Return string representation of the User.
        
        :returns: String representation
        :rtype: str
        """
        return f'<User {self.email} ({self.role})>'

