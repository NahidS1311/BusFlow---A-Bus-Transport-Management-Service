"""
User portal views for the BusFlow application.

This module defines the routes for the passenger portal including
bus search, seat selection, booking management, and ticket cancellation.

:module: app.views.user_portal
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.controllers.bus_controller import BusController
from app.controllers.booking_controller import BookingController
from app.config import ALL_BUS_STOPS

user_portal_bp = Blueprint('user_portal', __name__)


def _check_user_role():
    """
    Verify the current user has USER role.
    
    :returns: Redirect if unauthorized, None if authorized
    :rtype: Response or None
    """
    if not current_user.isUser:
        flash('Access denied. This portal is for passengers only.', 'error')
        return redirect(url_for('landing.index'))
    return None


@user_portal_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Render the user dashboard with search and booking tabs.
    
    :returns: Rendered dashboard template
    :rtype: str
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return redirect_response
    
    booking_controller = BookingController()
    bookings = booking_controller.get_user_bookings(current_user.id)
    
    return render_template(
        'user/dashboard.html',
        user=current_user,
        bookings=bookings,
        bus_stops=ALL_BUS_STOPS
    )


@user_portal_bp.route('/search', methods=['POST'])
@login_required
def search_buses():
    """
    Search for buses matching the route criteria.
    
    :returns: JSON response with matching buses
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    source = request.form.get('source', '').strip()
    destination = request.form.get('destination', '').strip()
    
    if not source or not destination:
        return jsonify({'error': 'Please select both source and destination.'}), 400
    
    if source == destination:
        return jsonify({'error': 'Source and destination cannot be the same.'}), 400
    
    bus_controller = BusController()
    buses = bus_controller.search_buses(source, destination)
    
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
            'price': bus.price,
            'status': bus.status
        })
    
    return jsonify({
        'buses': bus_list,
        'count': len(bus_list),
        'source': source,
        'destination': destination
    })


@user_portal_bp.route('/seats/<bus_id>')
@login_required
def get_seats(bus_id):
    """
    Get seat availability for a specific bus.
    
    :param bus_id: UUID of the bus
    :type bus_id: str
    :returns: JSON response with seat layout
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking_controller = BookingController()
    bus_controller = BusController()
    
    bus = bus_controller.get_bus_by_id(bus_id)
    if not bus:
        return jsonify({'error': 'Bus not found.'}), 404
    
    seat_layout = booking_controller.get_seat_layout(bus_id)
    
    return jsonify({
        'bus': {
            'id': bus.id,
            'name': bus.name,
            'price': bus.price
        },
        'seats': seat_layout
    })


@user_portal_bp.route('/book', methods=['POST'])
@login_required
def create_booking():
    """
    Create a new booking for selected seats.
    
    :returns: JSON response with booking result
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    bus_id = data.get('bus_id')
    seat_numbers = data.get('seats', [])
    source = data.get('source')
    destination = data.get('destination')
    price_per_seat = data.get('price')
    
    if not all([bus_id, seat_numbers, source, destination, price_per_seat]):
        return jsonify({'error': 'Missing required booking information.'}), 400
    
    booking_controller = BookingController()
    successful_bookings, errors = booking_controller.create_multiple_bookings(
        user_id=current_user.id,
        bus_id=bus_id,
        seat_numbers=seat_numbers,
        source=source,
        destination=destination,
        price_per_seat=price_per_seat
    )
    
    if errors and not successful_bookings:
        return jsonify({'error': errors[0]}), 400
    
    response_data = {
        'success': True,
        'message': f'Successfully booked {len(successful_bookings)} seat(s).',
        'bookings': [b.to_dict() for b in successful_bookings],
        'total_price': sum(b.price for b in successful_bookings)
    }
    
    if errors:
        response_data['partial_errors'] = errors
    
    return jsonify(response_data)


@user_portal_bp.route('/bookings')
@login_required
def get_bookings():
    """
    Get all bookings for the current user.
    
    :returns: JSON response with user's bookings
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking_controller = BookingController()
    bus_controller = BusController()
    
    bookings = booking_controller.get_user_bookings(current_user.id)
    buses = {b.id: b for b in bus_controller.get_all_buses()}
    
    booking_list = []
    for booking in bookings:
        bus = buses.get(booking.bus_id)
        booking_data = booking.to_dict()
        booking_data['bus_name'] = bus.name if bus else 'Unknown Bus'
        booking_data['formatted_date'] = booking.formatted_date
        booking_data['formatted_time'] = booking.formatted_time
        booking_data['route_display'] = booking.route_display
        booking_list.append(booking_data)
    
    return jsonify({'bookings': booking_list})


@user_portal_bp.route('/booking/<booking_id>')
@login_required
def get_booking_detail(booking_id):
    """
    Get details of a specific booking.
    
    :param booking_id: UUID of the booking
    :type booking_id: str
    :returns: JSON response with booking details
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking_controller = BookingController()
    bus_controller = BusController()
    
    bookings = booking_controller.get_user_bookings(current_user.id)
    booking = next((b for b in bookings if b.id == booking_id), None)
    
    if not booking:
        return jsonify({'error': 'Booking not found.'}), 404
    
    bus = bus_controller.get_bus_by_id(booking.bus_id)
    
    return jsonify({
        'booking': booking.to_dict(),
        'bus_name': bus.name if bus else 'Unknown Bus',
        'formatted_date': booking.formatted_date,
        'formatted_time': booking.formatted_time,
        'route_display': booking.route_display
    })


@user_portal_bp.route('/cancel/<booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """
    Cancel a specific booking.
    
    :param booking_id: UUID of the booking to cancel
    :type booking_id: str
    :returns: JSON response with cancellation result
    :rtype: Response
    """
    redirect_response = _check_user_role()
    if redirect_response:
        return jsonify({'error': 'Unauthorized'}), 403
    
    booking_controller = BookingController()
    success, error = booking_controller.delete_booking(booking_id, current_user.id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Ticket cancelled successfully.'
        })
    
    return jsonify({'error': error or 'Failed to cancel booking.'}), 400

