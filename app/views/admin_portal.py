"""
Admin portal views for the BusFlow application.

This module defines the routes for the administrator portal including
fleet management, driver assignment, and driver creation.

:module: app.views.admin_portal
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.controllers.bus_controller import BusController
from app.controllers.user_controller import UserController
from app.config import ALL_BUS_STOPS

admin_portal_bp = Blueprint('admin_portal', __name__)


def _check_admin_role():
    """
    Verify the current user has ADMIN role.
    
    :returns: Redirect if unauthorized, None if authorized
    :rtype: Response or None
    """
    if not current_user.isAdmin:
        flash('Access denied. This portal is for administrators only.', 'error')
        return redirect(url_for('landing.index'))
    return None


@admin_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Render the admin dashboard with fleet and user management.
    
    :returns: Rendered dashboard template
    :rtype: str
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return redirect_response
    
    bus_controller = BusController()
    user_controller = UserController()
    
    buses = bus_controller.get_all_buses()
    drivers = user_controller.get_all_drivers()
    
    # Create driver map for easy lookup
    driver_map = {d.id: d for d in drivers}
    
    # Add driver info to buses
    buses_with_drivers = []
    for bus in buses:
        bus_data = {
            'bus': bus,
            'driver': driver_map.get(bus.driver_id) if bus.driver_id else None
        }
        buses_with_drivers.append(bus_data)
    
    unassigned_buses = [b for b in buses if not b.hasDriver]
    
    return render_template(
        'admin/dashboard.html',
        user=current_user,
        buses=buses_with_drivers,
        drivers=drivers,
        unassigned_buses=unassigned_buses,
        bus_stops=ALL_BUS_STOPS,
        bus_count=len(buses),
        driver_count=len(drivers)
    )


@admin_portal_bp.route('/buses')
@login_required
def get_all_buses():
    """
    Get all buses in the fleet.
    
    :returns: JSON response with all buses
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bus_controller = BusController()
    user_controller = UserController()
    
    buses = bus_controller.get_all_buses()
    drivers = {d.id: d for d in user_controller.get_all_drivers()}
    
    bus_list = []
    for bus in buses:
        driver = drivers.get(bus.driver_id) if bus.driver_id else None
        bus_list.append({
            'id': bus.id,
            'name': bus.name,
            'route': bus.route,
            'route_display': bus.route_display,
            'total_seats': bus.total_seats,
            'price': bus.price,
            'status': bus.status,
            'driver_id': bus.driver_id,
            'driver_name': driver.name if driver else None
        })
    
    return jsonify({'buses': bus_list, 'count': len(bus_list)})


@admin_portal_bp.route('/bus/create', methods=['POST'])
@login_required
def create_bus():
    """
    Create a new bus in the fleet.
    
    :returns: JSON response with creation result
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    name = data.get('name', '').strip()
    route = data.get('route', [])
    price = data.get('price', 50)
    driver_id = data.get('driver_id')
    status = data.get('status', 'ACTIVE')
    
    bus_controller = BusController()
    bus, error = bus_controller.create_bus(
        name=name,
        route=route,
        price=price,
        driver_id=driver_id if driver_id else None,
        status=status
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Bus created successfully.',
        'bus': bus.to_dict()
    })


@admin_portal_bp.route('/bus/<bus_id>/update', methods=['POST'])
@login_required
def update_bus(bus_id):
    """
    Update an existing bus.
    
    :param bus_id: UUID of the bus to update
    :type bus_id: str
    :returns: JSON response with update result
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    name = data.get('name', '').strip()
    route = data.get('route', [])
    price = data.get('price', 50)
    driver_id = data.get('driver_id')
    status = data.get('status', 'ACTIVE')
    
    bus_controller = BusController()
    bus, error = bus_controller.update_bus(
        bus_id=bus_id,
        name=name,
        route=route,
        price=price,
        driver_id=driver_id if driver_id else None,
        status=status
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Bus updated successfully.',
        'bus': bus.to_dict()
    })


@admin_portal_bp.route('/bus/<bus_id>/assign', methods=['POST'])
@login_required
def assign_driver(bus_id):
    """
    Assign a driver to a bus.
    
    :param bus_id: UUID of the bus
    :type bus_id: str
    :returns: JSON response with assignment result
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    driver_id = data.get('driver_id')
    
    if not driver_id:
        return jsonify({'error': 'Driver ID is required.'}), 400
    
    bus_controller = BusController()
    success, error = bus_controller.assign_driver(bus_id, driver_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Driver assigned successfully.'
        })
    
    return jsonify({'error': error or 'Failed to assign driver.'}), 400


@admin_portal_bp.route('/drivers')
@login_required
def get_all_drivers():
    """
    Get all drivers in the system.
    
    :returns: JSON response with all drivers
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user_controller = UserController()
    bus_controller = BusController()
    
    drivers = user_controller.get_all_drivers()
    buses = bus_controller.get_all_buses()
    
    # Create map of driver_id to assigned bus
    driver_bus_map = {}
    for bus in buses:
        if bus.driver_id:
            driver_bus_map[bus.driver_id] = bus.name
    
    driver_list = []
    for driver in drivers:
        driver_list.append({
            'id': driver.id,
            'name': driver.name,
            'email': driver.email,
            'assigned_bus': driver_bus_map.get(driver.id)
        })
    
    return jsonify({'drivers': driver_list, 'count': len(driver_list)})


@admin_portal_bp.route('/driver/create', methods=['POST'])
@login_required
def create_driver():
    """
    Create a new driver account.
    
    :returns: JSON response with creation result
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    user_controller = UserController()
    driver, error = user_controller.create_driver(name, email, password)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Driver account created successfully.',
        'driver': driver.to_dict()
    })


@admin_portal_bp.route('/unassigned-buses')
@login_required
def get_unassigned_buses():
    """
    Get all buses without assigned drivers.
    
    :returns: JSON response with unassigned buses
    :rtype: Response
    """
    redirect_response = _check_admin_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bus_controller = BusController()
    buses = bus_controller.get_unassigned_buses()
    
    bus_list = []
    for bus in buses:
        bus_list.append({
            'id': bus.id,
            'name': bus.name,
            'route_display': bus.route_display,
            'status': bus.status
        })
    
    return jsonify({'buses': bus_list, 'count': len(bus_list)})

