"""
Bus controller for the BusFlow application.

This module provides the BusController class that handles all
bus-related business logic including fetching, creating, updating,
and managing bus assignments.

:module: app.controllers.bus_controller
"""

from app.models.bus import Bus
from app.models.user import User
from app.services.supabase_service import (
    SupabaseService,
    DatabaseOperationError
)
from app.config import BUS_STATUS_ACTIVE


class BusController:
    """
    Controller for handling bus operations.
    
    This controller manages all bus-related functionality including
    fleet management, route searching, and driver assignments.
    
    Example::
    
        controller = BusController()
        buses = controller.get_all_buses()
    """
    
    def __init__(self):
        """
        Initialize the BusController with a Supabase service instance.
        """
        self._supabase_service = SupabaseService()
    
    def get_all_buses(self):
        """
        Fetch all buses in the fleet.
        
        :returns: List of Bus objects
        :rtype: list
        """
        bus_data_list = self._supabase_service.get_all_buses()
        return [Bus.from_dict(data) for data in bus_data_list]
    
    def get_bus_by_id(self, bus_id):
        """
        Fetch a specific bus by its ID.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :returns: Bus object or None
        :rtype: Bus or None
        """
        bus_data = self._supabase_service.get_bus_by_id(bus_id)
        if bus_data:
            return Bus.from_dict(bus_data)
        return None
    
    def get_buses_for_driver(self, driver_id):
        """
        Fetch all buses assigned to a specific driver.
        
        :param driver_id: UUID of the driver
        :type driver_id: str
        :returns: List of Bus objects
        :rtype: list
        """
        bus_data_list = self._supabase_service.get_buses_by_driver(driver_id)
        return [Bus.from_dict(data) for data in bus_data_list]
    
    def get_active_buses(self):
        """
        Fetch all active buses available for booking.
        
        :returns: List of active Bus objects
        :rtype: list
        """
        all_buses = self.get_all_buses()
        return [bus for bus in all_buses if bus.isActive]
    
    def search_buses(self, source, destination):
        """
        Search for buses that travel from source to destination.
        
        Returns only active buses where the source stop comes
        before the destination stop in the route.
        
        :param source: Name of the boarding stop
        :type source: str
        :param destination: Name of the destination stop
        :type destination: str
        :returns: List of matching Bus objects
        :rtype: list
        
        Example::
        
            buses = controller.search_buses('Uttara', 'Motijheel')
        """
        all_buses = self.get_active_buses()
        matching_buses = []
        
        for bus in all_buses:
            if bus.is_valid_trip(source, destination):
                matching_buses.append(bus)
        
        return matching_buses
    
    def create_bus(self, name, route, price, driver_id=None, status=BUS_STATUS_ACTIVE):
        """
        Create a new bus in the fleet.
        
        :param name: Display name of the bus
        :type name: str
        :param route: List of stops in order
        :type route: list
        :param price: Ticket price in BDT
        :type price: int
        :param driver_id: UUID of assigned driver (optional)
        :type driver_id: str or None
        :param status: Operational status
        :type status: str
        :returns: Tuple of (Bus object or None, error message or None)
        :rtype: tuple
        """
        # Validate inputs
        validation_error = self._validate_bus_input(name, route, price)
        if validation_error:
            return None, validation_error
        
        bus_data = {
            'name': name,
            'route': route,
            'total_seats': 40,
            'driver_id': driver_id if driver_id else None,
            'price': int(price),
            'status': status
        }
        
        try:
            created_data = self._supabase_service.create_bus(bus_data)
            if created_data:
                return Bus.from_dict(created_data), None
            return None, "Failed to create bus."
        except DatabaseOperationError as e:
            return None, str(e)
    
    def update_bus(self, bus_id, name, route, price, driver_id=None, status=BUS_STATUS_ACTIVE):
        """
        Update an existing bus.
        
        :param bus_id: UUID of the bus to update
        :type bus_id: str
        :param name: New display name
        :type name: str
        :param route: New route list
        :type route: list
        :param price: New ticket price
        :type price: int
        :param driver_id: New driver assignment
        :type driver_id: str or None
        :param status: New operational status
        :type status: str
        :returns: Tuple of (Bus object or None, error message or None)
        :rtype: tuple
        """
        # Validate inputs
        validation_error = self._validate_bus_input(name, route, price)
        if validation_error:
            return None, validation_error
        
        bus_data = {
            'name': name,
            'route': route,
            'driver_id': driver_id if driver_id else None,
            'price': int(price),
            'status': status
        }
        
        try:
            updated_data = self._supabase_service.update_bus(bus_id, bus_data)
            if updated_data:
                return Bus.from_dict(updated_data), None
            return None, "Failed to update bus."
        except DatabaseOperationError as e:
            return None, str(e)
    
    def assign_driver(self, bus_id, driver_id):
        """
        Assign a driver to a bus.
        
        :param bus_id: UUID of the bus
        :type bus_id: str
        :param driver_id: UUID of the driver
        :type driver_id: str
        :returns: Tuple of (success boolean, error message or None)
        :rtype: tuple
        """
        try:
            result = self._supabase_service.update_bus(bus_id, {'driver_id': driver_id})
            if result:
                return True, None
            return False, "Failed to assign driver. Update returned no result."
        except DatabaseOperationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Failed to assign driver: {str(e)}"
    
    def get_unassigned_buses(self):
        """
        Fetch all buses without assigned drivers.
        
        :returns: List of Bus objects without drivers
        :rtype: list
        """
        all_buses = self.get_all_buses()
        return [bus for bus in all_buses if not bus.hasDriver]
    
    def get_bus_with_driver_info(self):
        """
        Fetch all buses with their driver information.
        
        :returns: List of dictionaries with bus and driver data
        :rtype: list
        """
        buses = self.get_all_buses()
        drivers = self._get_all_drivers()
        driver_map = {d.id: d for d in drivers}
        
        result = []
        for bus in buses:
            bus_info = {
                'bus': bus,
                'driver': driver_map.get(bus.driver_id) if bus.driver_id else None
            }
            result.append(bus_info)
        
        return result
    
    def _get_all_drivers(self):
        """
        Fetch all users with driver role.
        
        :returns: List of User objects with driver role
        :rtype: list
        """
        driver_data_list = self._supabase_service.get_users_by_role('DRIVER')
        return [User.from_dict(data) for data in driver_data_list]
    
    def _validate_bus_input(self, name, route, price):
        """
        Validate bus input fields.
        
        :param name: Bus display name
        :type name: str
        :param route: Route stop list
        :type route: list
        :param price: Ticket price
        :type price: int or str
        :returns: Error message or None if valid
        :rtype: str or None
        """
        if not name or len(name.strip()) < 2:
            return "Bus name must be at least 2 characters."
        
        if not route or len(route) < 2:
            return "Route must have at least 2 stops."
        
        try:
            price_int = int(price)
            if price_int <= 0:
                return "Price must be greater than 0."
        except (ValueError, TypeError):
            return "Price must be a valid number."
        
        return None

