"""
Driver portal views for the BusFlow application.

This module defines the routes for the driver portal including
viewing assigned buses and route information.

:module: app.views.driver_portal
"""

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.controllers.bus_controller import BusController

driver_portal_bp = Blueprint('driver_portal', __name__)


def _check_driver_role():
    """
    Verify the current user has DRIVER role.
    
    :returns: Redirect if unauthorized, None if authorized
    :rtype: Response or None
    """
    if not current_user.isDriver:
        flash('Access denied. This portal is for drivers only.', 'error')
        return redirect(url_for('landing.index'))
    return None


@driver_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Render the driver dashboard with assigned buses.
    
    :returns: Rendered dashboard template
    :rtype: str
    """
    redirect_response = _check_driver_role()
    if redirect_response:
        return redirect_response
    
    bus_controller = BusController()
    assigned_buses = bus_controller.get_buses_for_driver(current_user.id)
    
    return render_template(
        'driver/dashboard.html',
        user=current_user,
        assigned_buses=assigned_buses,
        bus_count=len(assigned_buses)
    )


@driver_portal_bp.route('/buses')
@login_required
def get_assigned_buses():
    """
    Get all buses assigned to the current driver.
    
    :returns: JSON response with assigned buses
    :rtype: Response
    """
    redirect_response = _check_driver_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bus_controller = BusController()
    buses = bus_controller.get_buses_for_driver(current_user.id)
    
    bus_list = []
    for bus in buses:
        bus_list.append({
            'id': bus.id,
            'name': bus.name,
            'route': bus.route,
            'route_display': bus.route_display,
            'start_stop': bus.start_stop,
            'end_stop': bus.end_stop,
            'total_seats': bus.total_seats,
            'stop_count': bus.get_stop_count(),
            'status': bus.status
        })
    
    return jsonify({
        'buses': bus_list,
        'count': len(bus_list)
    })


@driver_portal_bp.route('/bus/<bus_id>')
@login_required
def get_bus_detail(bus_id):
    """
    Get details of a specific assigned bus.
    
    :param bus_id: UUID of the bus
    :type bus_id: str
    :returns: JSON response with bus details
    :rtype: Response
    """
    redirect_response = _check_driver_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bus_controller = BusController()
    bus = bus_controller.get_bus_by_id(bus_id)
    
    if not bus:
        return jsonify({'error': 'Bus not found.'}), 404
    
    # Verify this bus is assigned to the driver
    if bus.driver_id != current_user.id:
        return jsonify({'error': 'This bus is not assigned to you.'}), 403
    
    return jsonify({
        'id': bus.id,
        'name': bus.name,
        'route': bus.route,
        'route_display': bus.route_display,
        'start_stop': bus.start_stop,
        'end_stop': bus.end_stop,
        'total_seats': bus.total_seats,
        'stop_count': bus.get_stop_count(),
        'price': bus.price,
        'status': bus.status
    })

