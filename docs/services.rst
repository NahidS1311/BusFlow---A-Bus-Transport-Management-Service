Services
========

The services package contains classes that handle external integrations 
and database operations. Services abstract away the complexity of 
interacting with external systems like Supabase.

Supabase Service
----------------

.. automodule:: app.services.supabase_service
   :members:
   :undoc-members:
   :show-inheritance:

Custom Exceptions
-----------------

The following custom exceptions are defined for error handling:

* **AuthenticationError**: Raised when login credentials are invalid
* **RegistrationError**: Raised when user registration fails
* **BookingError**: Raised when a booking cannot be completed
* **DatabaseOperationError**: Raised for general database operation failures

