"""
Booking model for the BusFlow application.

This module defines the Booking class that represents ticket bookings
made by passengers for specific bus journeys.

:module: app.models.booking
"""

from datetime import datetime
from app.config import BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_CANCELLED


class Booking:
    """
    Represents a ticket booking in the BusFlow system.
    
    A booking captures all details about a passenger's reserved seat
    on a specific bus for a particular journey.
    
    :param booking_id: Unique identifier for the booking (UUID)
    :type booking_id: str
    :param user_id: ID of the user who made the booking
    :type user_id: str
    :param bus_id: ID of the booked bus
    :type bus_id: str
    :param seat_number: Seat label (e.g., "A1", "B3")
    :type seat_number: str
    :param source: Name of the boarding stop
    :type source: str
    :param destination: Name of the destination stop
    :type destination: str
    :param booking_date: Date of the journey
    :type booking_date: str
    :param price: Price paid for the ticket in BDT
    :type price: int
    :param status: Booking status (CONFIRMED or CANCELLED)
    :type status: str
    :param created_at: Timestamp when booking was created
    :type created_at: str
    
    Example::
    
        booking = Booking(
            booking_id='uuid-789',
            user_id='user-123',
            bus_id='bus-456',
            seat_number='A1',
            source='Uttara',
            destination='Motijheel',
            booking_date='2024-12-15',
            price=50,
            status='CONFIRMED'
        )
    """
    
    def __init__(self, booking_id, user_id, bus_id, seat_number, source,
                 destination, booking_date, price, 
                 status=BOOKING_STATUS_CONFIRMED, created_at=None):
        """
        Initialize a new Booking instance.
        
        :param booking_id: Unique identifier for the booking
        :type booking_id: str
        :param user_id: ID of the booking user
        :type user_id: str
        :param bus_id: ID of the booked bus
        :type bus_id: str
        :param seat_number: Reserved seat label
        :type seat_number: str
        :param source: Boarding stop name
        :type source: str
        :param destination: Destination stop name
        :type destination: str
        :param booking_date: Journey date
        :type booking_date: str
        :param price: Ticket price
        :type price: int
        :param status: Booking status
        :type status: str
        :param created_at: Creation timestamp
        :type created_at: str
        """
        self.id = booking_id
        self.user_id = user_id
        self.bus_id = bus_id
        self.seat_number = seat_number
        self.source = source
        self.destination = destination
        self.booking_date = booking_date
        self.price = price
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
    
    @property
    def isConfirmed(self):
        """
        Check if the booking is confirmed.
        
        :returns: True if booking status is CONFIRMED
        :rtype: bool
        """
        return self.status == BOOKING_STATUS_CONFIRMED
    
    @property
    def isCancelled(self):
        """
        Check if the booking has been cancelled.
        
        :returns: True if booking status is CANCELLED
        :rtype: bool
        """
        return self.status == BOOKING_STATUS_CANCELLED
    
    @property
    def route_display(self):
        """
        Get a formatted string of the journey route.
        
        :returns: Source and destination joined with arrow
        :rtype: str
        """
        return f'{self.source} → {self.destination}'
    
    @property
    def formatted_date(self):
        """
        Get a formatted date string for display.
        
        :returns: Formatted date string
        :rtype: str
        """
        try:
            date_obj = datetime.fromisoformat(self.booking_date.replace('Z', '+00:00'))
            return date_obj.strftime('%B %d, %Y')
        except (ValueError, AttributeError):
            return self.booking_date
    
    @property
    def formatted_time(self):
        """
        Get a formatted time string for display.
        
        :returns: Formatted time string
        :rtype: str
        """
        try:
            date_obj = datetime.fromisoformat(self.booking_date.replace('Z', '+00:00'))
            return date_obj.strftime('%I:%M %p')
        except (ValueError, AttributeError):
            return ''
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Booking instance from a dictionary.
        
        Handles conversion from Supabase snake_case to Python attributes.
        
        :param data: Dictionary containing booking data
        :type data: dict
        :returns: New Booking instance
        :rtype: Booking
        """
        return cls(
            booking_id=data.get('id'),
            user_id=data.get('user_id'),
            bus_id=data.get('bus_id'),
            seat_number=data.get('seat_number'),
            source=data.get('source'),
            destination=data.get('destination'),
            booking_date=data.get('date'),
            price=data.get('price'),
            status=data.get('status', BOOKING_STATUS_CONFIRMED),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        """
        Convert Booking instance to a dictionary.
        
        :returns: Dictionary representation of the booking
        :rtype: dict
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bus_id': self.bus_id,
            'seat_number': self.seat_number,
            'source': self.source,
            'destination': self.destination,
            'date': self.booking_date,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at
        }
    
    def to_db_dict(self):
        """
        Convert Booking instance to database format for insertion.
        
        :returns: Dictionary formatted for Supabase insert
        :rtype: dict
        """
        return {
            'user_id': self.user_id,
            'bus_id': self.bus_id,
            'seat_number': self.seat_number,
            'source': self.source,
            'destination': self.destination,
            'date': self.booking_date,
            'price': self.price,
            'status': self.status
        }
    
    def __repr__(self):
        """
        Return string representation of the Booking.
        
        :returns: String representation
        :rtype: str
        """
        return f'<Booking {self.seat_number} on {self.booking_date} ({self.status})>'

