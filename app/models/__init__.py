"""
Models package for BusFlow application.

This package contains all data models used in the application:
- User: Represents system users (passengers, drivers, admins)
- Bus: Represents buses in the fleet
- Booking: Represents ticket bookings

:module: app.models
"""

from app.models.user import User
from app.models.bus import Bus
from app.models.booking import Booking

__all__ = ['User', 'Bus', 'Booking']

