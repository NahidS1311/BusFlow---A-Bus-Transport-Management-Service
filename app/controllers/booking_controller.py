"""
Booking controller for the BusFlow application.

This module provides the BookingController class that handles all
booking-related business logic including creating bookings, fetching
user tickets, seat availability, and cancellations.

:module: app.controllers.booking_controller
"""

from datetime import datetime
from app.models.booking import Booking
from app.models.bus import Bus
from app.services.supabase_service import SupabaseService, BookingError
from app.config import (
    MAX_SEATS_PER_BOOKING,
    SEAT_ROWS,
    LAST_ROW,
    SEATS_PER_ROW,
    LAST_ROW_SEATS,
    BOOKING_STATUS_CONFIRMED
)


class BookingController:
    """
    Controller for handling booking operations.
    
    This controller manages all ticket booking functionality including
    creating bookings, cancelling tickets, and checking seat availability.
    
    Example::
    
        controller = BookingController()
        bookings = controller.get_user_bookings(user_id)
    """
    
    def __init__(self):
        """
        Initialize the BookingController with a Supabase service instance.
        """
        self._supabase_service = SupabaseService()
    
    def get_user_bookings(self, user_id):
        """
        Fetch all bookings for a specific user.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: List of Booking objects
        :rtype: list
        """
        booking_data_list = self._supabase_service.get_bookings_by_user(user_id)
        return [Booking.from_dict(data) for data in booking_data_list]
    
    def get_confirmed_bookings(self, user_id):
        """
        Fetch only confirmed bookings for a user.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: List of confirmed Booking objects
        :rtype: list
        """
        all_bookings = self.get_user_bookings(user_id)
        return [b for b in all_bookings if b.isConfirmed]
    
    def get_occupied_seats(self, bus_id, date_str=None):
        """
        Get list of occupied seat numbers for a bus on a date.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param date_str: Date string (defaults to today)
        :type date_str: str or None
        :returns: List of occupied seat numbers
        :rtype: list
        """
        if not date_str:
            date_str = datetime.now().isoformat()
        
        bookings = self._supabase_service.get_bus_bookings_for_date(bus_id, date_str)
        return [b['seat_number'] for b in bookings]
    
    def get_seat_layout(self, bus_id, date_str=None):
        """
        Get the seat layout with availability status.
        
        Returns a list of seat objects with seat number and availability.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param date_str: Date string (defaults to today)
        :type date_str: str or None
        :returns: List of seat dictionaries
        :rtype: list
        
        Example::
        
            seats = controller.get_seat_layout(bus_id)
            for seat in seats:
                print(f"{seat['number']}: {'Occupied' if seat['isOccupied'] else 'Available'}")
        """
        occupied_seats = self.get_occupied_seats(bus_id, date_str)
        seat_layout = []
        
        # Regular rows A-J (4 seats each: 1, 2, 3, 4)
        for row in SEAT_ROWS:
            for seat_num in range(1, SEATS_PER_ROW + 1):
                seat_label = f"{row}{seat_num}"
                seat_layout.append({
                    'number': seat_label,
                    'row': row,
                    'position': seat_num,
                    'isOccupied': seat_label in occupied_seats,
                    'isLastRow': False
                })
        
        # Last row K (5 seats)
        for seat_num in range(1, LAST_ROW_SEATS + 1):
            seat_label = f"{LAST_ROW}{seat_num}"
            seat_layout.append({
                'number': seat_label,
                'row': LAST_ROW,
                'position': seat_num,
                'isOccupied': seat_label in occupied_seats,
                'isLastRow': True
            })
        
        return seat_layout
    
    def create_booking(self, user_id, bus_id, seat_number, source, destination, price):
        """
        Create a single seat booking.
        
        :param user_id: UUID of the user making the booking
        :type user_id: str
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param seat_number: Seat label to book
        :type seat_number: str
        :param source: Boarding stop name
        :type source: str
        :param destination: Destination stop name
        :type destination: str
        :param price: Ticket price
        :type price: int
        :returns: Tuple of (Booking object or None, error message or None)
        :rtype: tuple
        """
        booking_data = {
            'user_id': user_id,
            'bus_id': bus_id,
            'seat_number': seat_number,
            'source': source,
            'destination': destination,
            'date': datetime.now().isoformat(),
            'price': int(price),
            'status': BOOKING_STATUS_CONFIRMED
        }
        
        try:
            created_data = self._supabase_service.create_booking(booking_data)
            if created_data:
                return Booking.from_dict(created_data), None
            return None, "Failed to create booking."
        except BookingError as e:
            return None, str(e)
    
    def create_multiple_bookings(self, user_id, bus_id, seat_numbers, source, 
                                  destination, price_per_seat):
        """
        Create bookings for multiple seats.
        
        :param user_id: UUID of the user
        :type user_id: str
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param seat_numbers: List of seat labels to book
        :type seat_numbers: list
        :param source: Boarding stop name
        :type source: str
        :param destination: Destination stop name
        :type destination: str
        :param price_per_seat: Price per ticket
        :type price_per_seat: int
        :returns: Tuple of (list of Booking objects, list of error messages)
        :rtype: tuple
        """
        # Validate number of seats
        if len(seat_numbers) > MAX_SEATS_PER_BOOKING:
            return [], [f"Cannot book more than {MAX_SEATS_PER_BOOKING} seats at once."]
        
        successful_bookings = []
        errors = []
        
        for seat_number in seat_numbers:
            booking, error = self.create_booking(
                user_id=user_id,
                bus_id=bus_id,
                seat_number=seat_number,
                source=source,
                destination=destination,
                price=price_per_seat
            )
            
            if booking:
                successful_bookings.append(booking)
            else:
                errors.append(f"Seat {seat_number}: {error}")
        
        return successful_bookings, errors
    
    def cancel_booking(self, booking_id, user_id):
        """
        Cancel a booking (soft delete).
        
        :param booking_id: UUID of the booking
        :type booking_id: str
        :param user_id: UUID of the user (for verification)
        :type user_id: str
        :returns: Tuple of (success boolean, error message or None)
        :rtype: tuple
        """
        # Verify the booking belongs to the user
        user_bookings = self.get_user_bookings(user_id)
        booking_ids = [b.id for b in user_bookings]
        
        if booking_id not in booking_ids:
            return False, "Booking not found or access denied."
        
        success = self._supabase_service.cancel_booking(booking_id)
        if success:
            return True, None
        return False, "Failed to cancel booking."
    
    def delete_booking(self, booking_id, user_id):
        """
        Permanently delete a booking.
        
        :param booking_id: UUID of the booking
        :type booking_id: str
        :param user_id: UUID of the user (for verification)
        :type user_id: str
        :returns: Tuple of (success boolean, error message or None)
        :rtype: tuple
        """
        # Verify the booking belongs to the user
        user_bookings = self.get_user_bookings(user_id)
        booking_ids = [b.id for b in user_bookings]
        
        if booking_id not in booking_ids:
            return False, "Booking not found or access denied."
        
        success = self._supabase_service.delete_booking(booking_id)
        if success:
            return True, None
        return False, "Failed to delete booking."
    
    def get_booking_with_bus(self, user_id):
        """
        Fetch user bookings with associated bus information.
        
        :param user_id: UUID of the user
        :type user_id: str
        :returns: List of dictionaries with booking and bus data
        :rtype: list
        """
        bookings = self.get_user_bookings(user_id)
        buses = self._supabase_service.get_all_buses()
        bus_map = {b['id']: Bus.from_dict(b) for b in buses}
        
        result = []
        for booking in bookings:
            booking_info = {
                'booking': booking,
                'bus': bus_map.get(booking.bus_id)
            }
            result.append(booking_info)
        
        return result

