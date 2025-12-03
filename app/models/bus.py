"""
Bus model for the BusFlow application.

This module defines the Bus class that represents buses in the fleet,
including their routes, capacity, and operational status.

:module: app.models.bus
"""

from app.config import (
    BUS_STATUS_ACTIVE,
    DEFAULT_TOTAL_SEATS,
    DEFAULT_TICKET_PRICE
)


class Bus:
    """
    Represents a bus in the BusFlow fleet.
    
    Each bus has a defined route (sequence of stops), seat capacity,
    optional driver assignment, ticket price, and operational status.
    
    :param bus_id: Unique identifier for the bus (UUID)
    :type bus_id: str
    :param name: Display name of the bus (e.g., "Dhaka Chaka 01")
    :type name: str
    :param route: Ordered list of bus stops defining the route
    :type route: list
    :param total_seats: Total number of seats available
    :type total_seats: int
    :param driver_id: UUID of assigned driver or None
    :type driver_id: str or None
    :param price: Ticket price in BDT
    :type price: int
    :param status: Operational status (ACTIVE, MAINTENANCE, DECOMMISSIONED)
    :type status: str
    
    Example::
    
        bus = Bus(
            bus_id='uuid-456',
            name='Red Express 01',
            route=['Uttara', 'Banani', 'Farmgate'],
            total_seats=40,
            driver_id=None,
            price=50,
            status='ACTIVE'
        )
    """
    
    def __init__(self, bus_id, name, route, total_seats=DEFAULT_TOTAL_SEATS,
                 driver_id=None, price=DEFAULT_TICKET_PRICE,
                 status=BUS_STATUS_ACTIVE):
        """
        Initialize a new Bus instance.
        
        :param bus_id: Unique identifier for the bus
        :type bus_id: str
        :param name: Display name of the bus
        :type name: str
        :param route: List of stops in order
        :type route: list
        :param total_seats: Seat capacity
        :type total_seats: int
        :param driver_id: Assigned driver's ID
        :type driver_id: str or None
        :param price: Ticket price in BDT
        :type price: int
        :param status: Bus operational status
        :type status: str
        """
        self.id = bus_id
        self.name = name
        self.route = route if route else []
        self.total_seats = total_seats
        self.driver_id = driver_id
        self.price = price
        self.status = status
    
    @property
    def isActive(self):
        """
        Check if the bus is currently active for service.
        
        :returns: True if bus status is ACTIVE
        :rtype: bool
        """
        return self.status == BUS_STATUS_ACTIVE
    
    @property
    def start_stop(self):
        """
        Get the first stop in the route.
        
        :returns: Name of the starting stop
        :rtype: str
        """
        return self.route[0] if self.route else ''
    
    @property
    def end_stop(self):
        """
        Get the last stop in the route.
        
        :returns: Name of the ending stop
        :rtype: str
        """
        return self.route[-1] if self.route else ''
    
    @property
    def route_display(self):
        """
        Get a formatted string of the full route.
        
        :returns: Route stops joined with arrows
        :rtype: str
        """
        return ' → '.join(self.route)
    
    @property
    def hasDriver(self):
        """
        Check if the bus has an assigned driver.
        
        :returns: True if driver is assigned
        :rtype: bool
        """
        return self.driver_id is not None
    
    def get_stop_count(self):
        """
        Get the number of stops in the route.
        
        :returns: Number of stops
        :rtype: int
        """
        return len(self.route)
    
    def is_valid_trip(self, source, destination):
        """
        Check if a trip from source to destination is valid on this route.
        
        A trip is valid if both source and destination exist on the route
        and source comes before destination.
        
        :param source: Name of the boarding stop
        :type source: str
        :param destination: Name of the destination stop
        :type destination: str
        :returns: True if the trip is valid
        :rtype: bool
        """
        if source not in self.route or destination not in self.route:
            return False
        source_index = self.route.index(source)
        destination_index = self.route.index(destination)
        return source_index < destination_index
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Bus instance from a dictionary.
        
        Handles conversion from Supabase snake_case to Python attributes.
        
        :param data: Dictionary containing bus data
        :type data: dict
        :returns: New Bus instance
        :rtype: Bus
        """
        return cls(
            bus_id=data.get('id'),
            name=data.get('name'),
            route=data.get('route', []),
            total_seats=data.get('total_seats', DEFAULT_TOTAL_SEATS),
            driver_id=data.get('driver_id'),
            price=data.get('price', DEFAULT_TICKET_PRICE),
            status=data.get('status', BUS_STATUS_ACTIVE)
        )
    
    def to_dict(self):
        """
        Convert Bus instance to a dictionary.
        
        :returns: Dictionary representation of the bus
        :rtype: dict
        """
        return {
            'id': self.id,
            'name': self.name,
            'route': self.route,
            'total_seats': self.total_seats,
            'driver_id': self.driver_id,
            'price': self.price,
            'status': self.status
        }
    
    def to_db_dict(self):
        """
        Convert Bus instance to database format (snake_case).
        
        :returns: Dictionary formatted for Supabase
        :rtype: dict
        """
        return {
            'name': self.name,
            'route': self.route,
            'total_seats': self.total_seats,
            'driver_id': self.driver_id,
            'price': self.price,
            'status': self.status
        }
    
    def __repr__(self):
        """
        Return string representation of the Bus.
        
        :returns: String representation
        :rtype: str
        """
        return f'<Bus {self.name} ({self.status})>'

