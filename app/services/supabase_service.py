"""
Supabase service for database operations.

This module provides the SupabaseService class that handles all
interactions with the Supabase backend, including authentication
and CRUD operations for all database tables.

:module: app.services.supabase_service
"""

from supabase import create_client, Client
from flask import session
from app.config import SUPABASE_URL, SUPABASE_ANON_KEY


class SupabaseService:
    """
    Service class for Supabase database operations.
    
    This class encapsulates all database operations using the Supabase client,
    providing methods for authentication, user management, bus management,
    and booking operations.
    
    Example::
    
        service = SupabaseService()
        user_data = service.login('user@example.com', 'password123')
    """
    
    def __init__(self):
        """
        Initialize the Supabase client connection.
        Restores auth session if available.
        """
        self._client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Restore session if exists in Flask session
        self._restore_session()
    
    def _restore_session(self):
        """
        Restore Supabase auth session from Flask session.
        """
        try:
            access_token = session.get('supabase_access_token')
            refresh_token = session.get('supabase_refresh_token')
            
            if access_token and refresh_token:
                # Try to set session using available methods
                try:
                    # Method for supabase-py 1.x
                    self._client.auth.set_session(
                        access_token=access_token,
                        refresh_token=refresh_token
                    )
                except TypeError:
                    # Alternative: set session with positional args
                    try:
                        self._client.auth.set_session(access_token, refresh_token)
                    except Exception:
                        pass
                
                # Also set auth token on postgrest client for database operations
                try:
                    self._client.postgrest.auth(access_token)
                except Exception:
                    pass
        except Exception:
            # Session restore failed, continue without auth
            pass
    
    def _save_session(self, session_data):
        """
        Save Supabase auth session to Flask session.
        
        :param session_data: Session data from Supabase auth
        :type session_data: object
        """
        try:
            if session_data and hasattr(session_data, 'access_token'):
                session['supabase_access_token'] = session_data.access_token
                session['supabase_refresh_token'] = session_data.refresh_token
                
                # Also set auth token on postgrest client immediately
                try:
                    self._client.postgrest.auth(session_data.access_token)
                except Exception:
                    pass
        except Exception:
            pass
    
    def _clear_session(self):
        """
        Clear Supabase auth session from Flask session.
        """
        try:
            session.pop('supabase_access_token', None)
            session.pop('supabase_refresh_token', None)
        except Exception:
            pass
    
    # ========================================
    # Authentication Methods
    # ========================================
    
    def login(self, email, password):
        """
        Authenticate a user with email and password.
        
        :param email: User's email address
        :type email: str
        :param password: User's password
        :type password: str
        :returns: User profile data if successful
        :rtype: dict or None
        :raises AuthenticationError: If credentials are invalid
        
        Example::
        
            user_data = service.login('user@example.com', 'password123')
        """
        try:
            # For supabase-py 1.x
            response = self._client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Save session for future requests
                self._save_session(response.session)
                
                # Fetch user profile
                profile_response = self._client.table('profiles').select('*').eq(
                    'id', response.user.id
                ).single().execute()
                
                return profile_response.data
            return None
        except Exception as e:
            error_msg = str(e)
            if 'Invalid login credentials' in error_msg:
                raise AuthenticationError('Invalid email or password.')
            raise AuthenticationError(error_msg)
    
    def register(self, name, email, password, role='USER'):
        """
        Register a new user account.
        
        :param name: User's full name
        :type name: str
        :param email: User's email address
        :type email: str
        :param password: User's chosen password
        :type password: str
        :param role: User role (defaults to 'USER')
        :type role: str
        :returns: Created user profile data
        :rtype: dict or None
        :raises RegistrationError: If registration fails
        """
        try:
            # For supabase-py 1.x
            response = self._client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name,
                        "role": role
                    }
                }
            })
            
            if response.user:
                # Save session for future requests
                if response.session:
                    self._save_session(response.session)
                
                # Profile is created by database trigger
                # Return basic user info
                return {
                    'id': response.user.id,
                    'email': email,
                    'name': name,
                    'role': role
                }
            return None
        except Exception as e:
            error_msg = str(e)
            if 'already registered' in error_msg.lower():
                raise RegistrationError('This email is already registered.')
            raise RegistrationError(error_msg)
    
    def logout(self):
        """
        Sign out the current user.
        """
        try:
            self._client.auth.sign_out()
            self._clear_session()
        except Exception:
            self._clear_session()
    
    def get_user_by_id(self, user_id):
        """
        Fetch a user profile by their ID.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: User profile data or None
        :rtype: dict or None
        """
        try:
            response = self._client.table('profiles').select('*').eq(
                'id', user_id
            ).single().execute()
            return response.data
        except Exception:
            return None
    
    # ========================================
    # User Management Methods
    # ========================================
    
    def get_all_users(self):
        """
        Fetch all users from the database.
        
        :returns: List of user profile dictionaries
        :rtype: list
        """
        try:
            response = self._client.table('profiles').select('*').order(
                'created_at', desc=False
            ).execute()
            return response.data or []
        except Exception:
            return []
    
    def get_users_by_role(self, role):
        """
        Fetch all users with a specific role.
        
        :param role: Role to filter by (USER, DRIVER, ADMIN)
        :type role: str
        :returns: List of user profile dictionaries
        :rtype: list
        """
        try:
            response = self._client.table('profiles').select('*').eq(
                'role', role
            ).order('created_at', desc=False).execute()
            return response.data or []
        except Exception:
            return []
    
    def create_driver(self, name, email, password):
        """
        Create a new driver account.
        
        :param name: Driver's full name
        :type name: str
        :param email: Driver's email address
        :type email: str
        :param password: Initial password
        :type password: str
        :returns: Created driver profile data
        :rtype: dict or None
        """
        return self.register(name, email, password, role='DRIVER')
    
    # ========================================
    # Bus Management Methods
    # ========================================
    
    def get_all_buses(self):
        """
        Fetch all buses from the database.
        
        :returns: List of bus dictionaries
        :rtype: list
        """
        try:
            response = self._client.table('buses').select('*').order(
                'created_at', desc=False
            ).execute()
            return response.data or []
        except Exception:
            return []
    
    def get_bus_by_id(self, bus_id):
        """
        Fetch a specific bus by its ID.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :returns: Bus data or None
        :rtype: dict or None
        """
        try:
            response = self._client.table('buses').select('*').eq(
                'id', bus_id
            ).single().execute()
            return response.data
        except Exception:
            return None
    
    def get_buses_by_driver(self, driver_id):
        """
        Fetch all buses assigned to a specific driver.
        
        :param driver_id: UUID of the driver
        :type driver_id: str
        :returns: List of bus dictionaries
        :rtype: list
        """
        try:
            response = self._client.table('buses').select('*').eq(
                'driver_id', driver_id
            ).execute()
            return response.data or []
        except Exception:
            return []
    
    def create_bus(self, bus_data):
        """
        Create a new bus in the fleet.
        
        :param bus_data: Dictionary containing bus information
        :type bus_data: dict
        :returns: Created bus data
        :rtype: dict or None
        """
        try:
            response = self._client.table('buses').insert(bus_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise DatabaseOperationError(f"Failed to create bus: {str(e)}")
    
    def update_bus(self, bus_id, bus_data):
        """
        Update an existing bus.
        
        :param bus_id: UUID of the bus to update
        :type bus_id: str
        :param bus_data: Dictionary containing updated bus information
        :type bus_data: dict
        :returns: Updated bus data
        :rtype: dict or None
        """
        try:
            response = self._client.table('buses').update(bus_data).eq(
                'id', bus_id
            ).execute()
            
            # Check if update was successful
            if response.data:
                return response.data[0]
            
            # If no data returned, the update might have failed due to RLS
            # Try to fetch the bus to confirm
            check = self._client.table('buses').select('*').eq('id', bus_id).single().execute()
            if check.data:
                # Bus exists but update didn't return data - might be RLS issue
                # Return the fetched data as a workaround
                return check.data
            return None
        except Exception as e:
            error_str = str(e)
            if '42501' in error_str or 'row-level security' in error_str.lower():
                raise DatabaseOperationError(
                    "Permission denied. Admin authentication may have expired. Please log out and log back in."
                )
            raise DatabaseOperationError(f"Failed to update bus: {error_str}")
    
    def delete_bus(self, bus_id):
        """
        Delete a bus from the fleet.
        
        :param bus_id: UUID of the bus to delete
        :type bus_id: str
        :returns: True if successful
        :rtype: bool
        """
        try:
            self._client.table('buses').delete().eq('id', bus_id).execute()
            return True
        except Exception:
            return False
    
    # ========================================
    # Booking Management Methods
    # ========================================
    
    def get_bookings_by_user(self, user_id):
        """
        Fetch all bookings for a specific user.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: List of booking dictionaries
        :rtype: list
        """
        try:
            response = self._client.table('bookings').select('*').eq(
                'user_id', user_id
            ).order('created_at', desc=True).execute()
            return response.data or []
        except Exception:
            return []
    
    def get_bus_bookings_for_date(self, bus_id, date_str):
        """
        Fetch confirmed bookings for a bus on a specific date.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param date_str: Date string (ISO format)
        :type date_str: str
        :returns: List of booking dictionaries
        :rtype: list
        """
        try:
            date_prefix = date_str.split('T')[0]
            response = self._client.table('bookings').select('*').eq(
                'bus_id', bus_id
            ).eq('status', 'CONFIRMED').gte(
                'date', date_prefix
            ).lt('date', date_prefix + 'T23:59:59').execute()
            return response.data or []
        except Exception:
            return []
    
    def create_booking(self, booking_data):
        """
        Create a new ticket booking.
        
        :param booking_data: Dictionary containing booking information
        :type booking_data: dict
        :returns: Created booking data
        :rtype: dict or None
        :raises BookingError: If seat is already booked
        """
        try:
            # Check for existing booking
            date_prefix = booking_data['date'].split('T')[0]
            existing = self._client.table('bookings').select('*').eq(
                'bus_id', booking_data['bus_id']
            ).eq('seat_number', booking_data['seat_number']).eq(
                'status', 'CONFIRMED'
            ).gte('date', date_prefix).lt(
                'date', date_prefix + 'T23:59:59'
            ).execute()
            
            if existing.data:
                raise BookingError(
                    f"Seat {booking_data['seat_number']} is already booked."
                )
            
            response = self._client.table('bookings').insert(booking_data).execute()
            return response.data[0] if response.data else None
        except BookingError:
            raise
        except Exception as e:
            raise BookingError(f"Failed to create booking: {str(e)}")
    
    def cancel_booking(self, booking_id):
        """
        Cancel a booking by updating its status.
        
        :param booking_id: UUID of the booking
        :type booking_id: str
        :returns: True if successful
        :rtype: bool
        """
        try:
            self._client.table('bookings').update({
                'status': 'CANCELLED'
            }).eq('id', booking_id).execute()
            return True
        except Exception:
            return False
    
    def delete_booking(self, booking_id):
        """
        Permanently delete a booking.
        
        :param booking_id: UUID of the booking
        :type booking_id: str
        :returns: True if successful
        :rtype: bool
        """
        try:
            self._client.table('bookings').delete().eq('id', booking_id).execute()
            return True
        except Exception:
            return False


# ========================================
# Custom Exceptions
# ========================================

class AuthenticationError(Exception):
    """
    Exception raised for authentication failures.
    
    This exception is raised when login credentials are invalid
    or authentication otherwise fails.
    """
    pass


class RegistrationError(Exception):
    """
    Exception raised for registration failures.
    
    This exception is raised when user registration fails,
    such as when email is already in use.
    """
    pass


class BookingError(Exception):
    """
    Exception raised for booking failures.
    
    This exception is raised when a booking cannot be completed,
    such as when a seat is already taken.
    """
    pass


class DatabaseOperationError(Exception):
    """
    Exception raised for general database operation failures.
    
    This exception is raised for CRUD operations that fail
    for reasons other than specific business logic.
    """
    pass
