"""
Landing page view for the BusFlow application.

This module defines the routes for the public landing page
that introduces the BusFlow platform to visitors.

:module: app.views.landing
"""

from flask import Blueprint, render_template

landing_bp = Blueprint('landing', __name__)


@landing_bp.route('/')
def index():
    """
    Render the landing page.
    
    Displays the main marketing page with information about
    the BusFlow platform and links to the different portals.
    
    :returns: Rendered landing page template
    :rtype: str
    """
    return render_template('landing.html')

